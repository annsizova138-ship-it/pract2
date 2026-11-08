"""Тесты порядка загрузки зависимостей."""
import contextlib
import io
import os
import unittest

from file_repo import load_test_repository
from graph import build_graph, find_cycles
from main import EXIT_OK, main
from order import load_order

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
NO_LIMIT = 100


def order_of(name, package, depth=NO_LIMIT, substring=""):
    """Строит граф примера и возвращает порядок загрузки."""
    repo = load_test_repository(os.path.join(EXAMPLES, name))
    return load_order(build_graph(repo, package, depth, substring))


class OrderTests(unittest.TestCase):
    """Проверки load_order."""

    def test_chain(self):
        """В цепочке сначала самый глубокий пакет."""
        self.assertEqual(order_of("chain.txt", "A"), ["D", "C", "B", "A"])

    def test_diamond(self):
        """В ромбе общий пакет D идёт раньше B и C, корень последний."""
        self.assertEqual(order_of("diamond.txt", "A"), ["D", "B", "C", "A"])

    def test_depth_limit(self):
        """Порядок учитывает ограничение глубины."""
        self.assertEqual(order_of("chain.txt", "A", depth=2), ["C", "B", "A"])

    def test_filter(self):
        """Исключённые фильтром пакеты в порядок не попадают."""
        self.assertEqual(
            order_of("diamond.txt", "A", substring="D"), ["B", "C", "A"])

    def test_cycle(self):
        """С циклом порядок строится, каждый пакет один раз."""
        order = order_of("cycle.txt", "A")
        self.assertEqual(sorted(order), ["A", "B", "C", "D"])
        self.assertEqual(order[-1], "A")

    def test_dependencies_come_first(self):
        """Для графа без циклов зависимости идут раньше зависимых."""
        repo = load_test_repository(os.path.join(EXAMPLES, "big.txt"))
        graph = build_graph(repo, "A", NO_LIMIT, "")
        self.assertEqual(find_cycles(graph), [])
        order = load_order(graph)
        position = {name: index for index, name in enumerate(order)}
        for name in order:
            for dep in graph.deps(name):
                self.assertLess(position[dep], position[name])


class MainTests(unittest.TestCase):
    """Проверка режима --load-order в main."""

    def test_load_order_mode(self):
        """Режим выводит нумерованный порядок загрузки."""
        argv = ["--package", "A", "--repo-mode", "test", "--load-order",
                "--repo", os.path.join(EXAMPLES, "diamond.txt")]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = main(argv)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  1. D\n  2. B\n  3. C\n  4. A\n", out.getvalue())


if __name__ == "__main__":
    unittest.main()
