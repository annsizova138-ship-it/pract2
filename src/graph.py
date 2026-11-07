"""Граф зависимостей: обход в ширину (BFS) с рекурсией и поиск циклов."""
from errors import GraphError


class Graph:
    """Граф: корень, порядок обнаружения узлов и рёбра раскрытых узлов."""

    def __init__(self, root, nodes, edges):
        """Запоминает корень, узлы (в порядке обнаружения) и рёбра."""
        self.root = root
        self.nodes = nodes
        self.edges = edges

    def deps(self, name):
        """Возвращает зависимости узла (у нераскрытого узла их нет)."""
        return self.edges.get(name, [])

    def unexpanded(self):
        """Узлы, чьи зависимости не раскрывались (граница глубины)."""
        return [name for name in self.nodes if name not in self.edges]


class GraphBuilder:
    """Строит граф уровень за уровнем (BFS), рекурсивно."""

    def __init__(self, repo, max_depth, substring):
        """Запоминает репозиторий, глубину и подстроку для фильтра."""
        self.repo = repo
        self.max_depth = max_depth
        self.substring = substring
        self.edges = {}
        self.nodes = []
        self.seen = set()

    def excluded(self, name):
        """Истина, если имя содержит подстроку фильтра."""
        return bool(self.substring) and self.substring in name

    def build(self, root):
        """Строит граф для пакета root."""
        if root not in self.repo:
            raise GraphError(f"пакет '{root}' не найден в репозитории")
        if self.excluded(root):
            raise GraphError(
                f"пакет '{root}' исключён фильтром '{self.substring}'")
        self.nodes = [root]
        self.seen = {root}
        self.edges = {}
        self.expand_level([root], 0)
        return Graph(root, self.nodes, self.edges)

    def expand_level(self, level, depth):
        """Раскрывает один уровень и рекурсивно вызывает следующий."""
        if not level or depth >= self.max_depth:
            return
        next_level = []
        for name in level:
            deps = [dep for dep in self.repo.get(name, [])
                    if not self.excluded(dep)]
            self.edges[name] = deps
            for dep in deps:
                if dep not in self.seen:
                    self.seen.add(dep)
                    self.nodes.append(dep)
                    next_level.append(dep)
        self.expand_level(next_level, depth + 1)


def build_graph(repo, root, max_depth, substring):
    """Строит граф зависимостей пакета с учётом глубины и фильтра."""
    return GraphBuilder(repo, max_depth, substring).build(root)


def _walk(graph, name, path, done, cycles):
    """Обход в глубину; на возврат в пройденный путь фиксирует цикл."""
    if name in path:
        cycles.append(path[path.index(name):] + [name])
        return
    if name in done:
        return
    path.append(name)
    for dep in graph.deps(name):
        _walk(graph, dep, path, done, cycles)
    path.pop()
    done.add(name)


def find_cycles(graph):
    """Возвращает циклы графа в виде списков [A, B, A]."""
    cycles = []
    _walk(graph, graph.root, [], set(), cycles)
    return cycles
