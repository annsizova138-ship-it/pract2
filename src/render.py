"""Представление графа: ASCII-дерево, Graphviz (DOT) и изображение."""
import os
import subprocess
import sys

from errors import RenderError

BRANCH = "|-- "
LAST_BRANCH = "`-- "
PIPE = "|   "
SPACE = "    "
ROOT_STYLE = 'style=filled, fillcolor=lightblue'
CYCLE_STYLE = "color=red"
BOUNDARY_STYLE = "style=dashed"


def format_cycles(cycles):
    """Возвращает строки с описанием циклических зависимостей."""
    if not cycles:
        return ["Циклические зависимости: нет"]
    lines = ["Циклические зависимости:"]
    lines.extend("  " + " -> ".join(cycle) for cycle in cycles)
    return lines


def format_order(graph, order, cycles):
    """Возвращает строки: порядок загрузки, граница глубины, циклы."""
    lines = [f"Порядок загрузки пакета {graph.root} "
             "(зависимости раньше зависимых):"]
    for number, name in enumerate(order, start=1):
        lines.append(f"  {number}. {name}")
    boundary = graph.unexpanded()
    if boundary:
        lines.append("Зависимости не раскрыты (глубина): "
                     + ", ".join(boundary))
    lines.extend(format_cycles(cycles))
    return lines


def _tree_lines(graph, name, prefix, state):
    """Добавляет строки поддерева узла name.

    state - тройка (путь от корня, уже раскрытые узлы, список строк).
    """
    path, shown, lines = state
    deps = graph.deps(name)
    for index, dep in enumerate(deps):
        last = index == len(deps) - 1
        note = ""
        if dep in path:
            note = " (цикл)"
        elif dep in shown and graph.deps(dep):
            note = " (повтор)"
        lines.append(prefix + (LAST_BRANCH if last else BRANCH) + dep + note)
        if note:
            continue
        shown.add(dep)
        path.append(dep)
        _tree_lines(graph, dep, prefix + (SPACE if last else PIPE), state)
        path.pop()


def ascii_tree(graph):
    """Возвращает строки ASCII-дерева зависимостей.

    Узел, который уже есть выше по ветке, помечается (цикл); узел,
    раскрытый в другой ветке, - (повтор), его зависимости не повторяются.
    """
    lines = [graph.root]
    state = ([graph.root], {graph.root}, lines)
    _tree_lines(graph, graph.root, "", state)
    return lines


def quote(name):
    """Оборачивает имя в кавычки языка DOT."""
    return '"' + name.replace('"', '\\"') + '"'


def to_dot(graph, cycles):
    """Возвращает описание графа на языке Graphviz (DOT).

    Корень закрашен, рёбра циклов красные, узлы на границе глубины
    нарисованы пунктиром.
    """
    cyclic = {pair for cycle in cycles for pair in zip(cycle, cycle[1:])}
    lines = [f"digraph {quote(graph.root)} {{", "  rankdir=LR;",
             "  node [shape=box];",
             f"  {quote(graph.root)} [{ROOT_STYLE}];"]
    for name in graph.unexpanded():
        lines.append(f"  {quote(name)} [{BOUNDARY_STYLE}];")
    for name in graph.nodes:
        for dep in graph.deps(name):
            style = f" [{CYCLE_STYLE}]" if (name, dep) in cyclic else ""
            lines.append(f"  {quote(name)} -> {quote(dep)}{style};")
    lines.append("}")
    return "\n".join(lines)


def render_image(dot_text, path):
    """Строит изображение программой Graphviz (dot) и сохраняет в path."""
    fmt = os.path.splitext(path)[1].lstrip(".").lower()
    try:
        subprocess.run(
            ["dot", f"-T{fmt}", "-o", path], input=dot_text.encode("utf-8"),
            check=True, capture_output=True)
    except FileNotFoundError as err:
        raise RenderError(
            "Graphviz не найден: установите его и добавьте dot в PATH"
        ) from err
    except subprocess.CalledProcessError as err:
        message = err.stderr.decode("utf-8", errors="replace").strip()
        raise RenderError(f"dot завершился с ошибкой: {message}") from err


def open_image(path):
    """Открывает изображение в программе просмотра по умолчанию."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.run([opener, path], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as err:
        raise RenderError(f"не удалось открыть изображение: {err}") from err
