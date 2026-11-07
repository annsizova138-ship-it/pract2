"""Тесты построения графа: глубина, фильтр, циклы."""
import contextlib
import io
import os
import unittest

from errors import GraphError
from file_repo import load_test_repository
from graph import build_graph, find_cycles
from main import EXIT_ERROR, EXIT_OK, main

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
NO_LIMIT = 100


def example(name):
    """Загружает пример тестового репозитория."""
    return load_test_repository(os.path.join(EXAMPLES, name))


class GraphTests(unittest.TestCase):
    """Проверки BFS с рекурсией."""

    def test_chain_full(self):
        """Цепочка раскрывается до конца."""
        graph = build_graph(example("chain.txt"), "A", NO_LIMIT, "")
        self.assertEqual(graph.nodes, ["A", "B", "C", "D"])
        self.assertEqual(
            graph.edges, {"A": ["B"], "B": ["C"], "C": ["D"], "D": []})

    def test_depth_limit(self):
        """Глубина 2: у узла C зависимости не раскрыты."""
        graph = build_graph(example("chain.txt"), "A", 2, "")
        self.assertEqual(graph.nodes, ["A", "B", "C"])
        self.assertEqual(graph.edges, {"A": ["B"], "B": ["C"]})
        self.assertEqual(graph.unexpanded(), ["C"])

    def test_depth_one(self):
        """Глубина 1: только прямые зависимости."""
        graph = build_graph(example("diamond.txt"), "A", 1, "")
        self.assertEqual(graph.edges, {"A": ["B", "C"]})

    def test_diamond_shared_node_once(self):
        """Общий пакет D попадает в граф один раз."""
        graph = build_graph(example("diamond.txt"), "A", NO_LIMIT, "")
        self.assertEqual(graph.nodes, ["A", "B", "C", "D"])
        self.assertEqual(graph.edges["B"], ["D"])
        self.assertEqual(graph.edges["C"], ["D"])

    def test_filter(self):
        """Пакеты с подстрокой в имени не учитываются."""
        graph = build_graph(example("diamond.txt"), "A", NO_LIMIT, "D")
        self.assertEqual(graph.nodes, ["A", "B", "C"])
        self.assertEqual(graph.edges, {"A": ["B", "C"], "B": [], "C": []})

    def test_filter_root_error(self):
        """Корневой пакет не может быть исключён фильтром."""
        with self.assertRaises(GraphError):
            build_graph(example("diamond.txt"), "A", NO_LIMIT, "A")

    def test_unknown_root(self):
        """Неизвестный пакет - GraphError."""
        with self.assertRaises(GraphError):
            build_graph(example("diamond.txt"), "Z", NO_LIMIT, "")

    def test_cycle_terminates_and_found(self):
        """Цикл не вешает программу и обнаруживается."""
        graph = build_graph(example("cycle.txt"), "A", NO_LIMIT, "")
        self.assertEqual(graph.nodes, ["A", "B", "C", "D"])
        self.assertEqual(find_cycles(graph), [["A", "B", "C", "A"]])

    def test_self_cycle(self):
        """Зависимость пакета от самого себя - цикл из одного узла."""
        graph = build_graph(example("self.txt"), "A", NO_LIMIT, "")
        self.assertEqual(find_cycles(graph), [["A", "A"]])

    def test_no_cycles(self):
        """В ромбе циклов нет."""
        graph = build_graph(example("diamond.txt"), "A", NO_LIMIT, "")
        self.assertEqual(find_cycles(graph), [])


class MainTests(unittest.TestCase):
    """Проверки main в тестовом режиме."""

    def run_main(self, name, package, *extra):
        """Запускает main и возвращает (код, stdout)."""
        argv = ["--package", package, "--repo-mode", "test",
                "--repo", os.path.join(EXAMPLES, name), *extra]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = main(argv)
        return code, out.getvalue()

    def test_diamond(self):
        """Вывод графа-ромба."""
        code, text = self.run_main("diamond.txt", "A")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  A -> B, C\n", text)
        self.assertIn("  D -> (нет зависимостей)\n", text)
        self.assertIn("Циклические зависимости: нет", text)

    def test_cycle_reported(self):
        """Цикл попадает в вывод."""
        code, text = self.run_main("cycle.txt", "A")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  A -> B -> C -> A", text)

    def test_unknown_package(self):
        """Неизвестный пакет: код ошибки 1."""
        code, _ = self.run_main("diamond.txt", "Z")
        self.assertEqual(code, EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
