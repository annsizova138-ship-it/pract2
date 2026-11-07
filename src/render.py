"""Текстовое представление графа зависимостей."""

NO_DEPS = "(нет зависимостей)"


def format_cycles(cycles):
    """Возвращает строки с описанием циклических зависимостей."""
    if not cycles:
        return ["Циклические зависимости: нет"]
    lines = ["Циклические зависимости:"]
    lines.extend("  " + " -> ".join(cycle) for cycle in cycles)
    return lines


def format_graph(graph, cycles):
    """Возвращает строки: рёбра графа, граница глубины, циклы."""
    lines = [f"Граф зависимостей пакета {graph.root}:"]
    for name, deps in graph.edges.items():
        lines.append(f"  {name} -> {', '.join(deps) or NO_DEPS}")
    boundary = graph.unexpanded()
    if boundary:
        lines.append("Зависимости не раскрыты (глубина): "
                     + ", ".join(boundary))
    lines.extend(format_cycles(cycles))
    return lines
