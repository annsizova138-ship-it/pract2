"""Порядок загрузки: зависимости раньше тех, кто от них зависит."""


def _visit(graph, name, visited, order):
    """Обход в глубину: пакет записывается после своих зависимостей."""
    if name in visited:
        return
    visited.add(name)
    for dep in graph.deps(name):
        _visit(graph, dep, visited, order)
    order.append(name)


def load_order(graph):
    """Возвращает список пакетов в порядке загрузки (корень - последний).

    Связи, замыкающие цикл, пропускаются: для цикла нет верного порядка.
    """
    order = []
    _visit(graph, graph.root, set(), order)
    return order
