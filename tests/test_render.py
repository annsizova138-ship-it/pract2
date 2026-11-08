"""Тесты ASCII-дерева, DOT и изображения."""
import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from errors import RenderError
from file_repo import load_test_repository
from graph import build_graph, find_cycles
from main import EXIT_ERROR, EXIT_OK, main
from render import ascii_tree, open_image, render_image, to_dot

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
NO_LIMIT = 100
HAS_DOT = shutil.which("dot") is not None


def graph_of(name, package, depth=NO_LIMIT):
    """Строит граф примера из examples."""
    repo = load_test_repository(os.path.join(EXAMPLES, name))
    return build_graph(repo, package, depth, "")


class AsciiTreeTests(unittest.TestCase):
    """Проверки ASCII-дерева."""

    def test_diamond(self):
        """Общий лист D показывается в обеих ветках."""
        self.assertEqual(
            ascii_tree(graph_of("diamond.txt", "A")),
            ["A", "|-- B", "|   `-- D", "`-- C", "    `-- D"])

    def test_repeated_subtree(self):
        """Повторно встреченный пакет с зависимостями помечается."""
        lines = ascii_tree(graph_of("big.txt", "A"))
        self.assertIn("    |-- E (повтор)", lines)

    def test_cycle_marked(self):
        """Возврат к пакету выше по ветке помечается (цикл)."""
        self.assertEqual(
            ascii_tree(graph_of("cycle.txt", "A")),
            ["A", "`-- B", "    `-- C", "        |-- A (цикл)",
             "        `-- D"])

    def test_single_node(self):
        """Пакет без зависимостей - одна строка."""
        self.assertEqual(ascii_tree(graph_of("chain.txt", "D")), ["D"])


class DotTests(unittest.TestCase):
    """Проверки текста Graphviz."""

    def test_diamond(self):
        """Заголовок, корень и рёбра."""
        graph = graph_of("diamond.txt", "A")
        text = to_dot(graph, find_cycles(graph))
        self.assertTrue(text.startswith('digraph "A" {'))
        self.assertTrue(text.endswith("}"))
        self.assertIn('"A" [style=filled, fillcolor=lightblue];', text)
        self.assertIn('"B" -> "D";', text)

    def test_cycle_edges_red(self):
        """Рёбра цикла красные, остальные обычные."""
        graph = graph_of("cycle.txt", "A")
        text = to_dot(graph, find_cycles(graph))
        self.assertIn('"C" -> "A" [color=red];', text)
        self.assertIn('"C" -> "D";', text)

    def test_boundary_dashed(self):
        """Узлы на границе глубины рисуются пунктиром."""
        graph = graph_of("chain.txt", "A", depth=2)
        text = to_dot(graph, [])
        self.assertIn('"C" [style=dashed];', text)


class ImageTests(unittest.TestCase):
    """Проверки получения и показа изображения."""

    @unittest.skipUnless(HAS_DOT, "Graphviz (dot) не установлен")
    def test_render_png_and_svg(self):
        """dot создаёт PNG и SVG."""
        graph = graph_of("diamond.txt", "A")
        dot_text = to_dot(graph, [])
        with tempfile.TemporaryDirectory() as folder:
            png = os.path.join(folder, "g.png")
            svg = os.path.join(folder, "g.svg")
            render_image(dot_text, png)
            render_image(dot_text, svg)
            with open(png, "rb") as handle:
                self.assertEqual(handle.read(4), b"\x89PNG")
            with open(svg, encoding="utf-8") as handle:
                self.assertIn("<svg", handle.read())

    def test_dot_missing(self):
        """Нет программы dot - RenderError."""
        with mock.patch("subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaises(RenderError):
                render_image("digraph {}", "g.png")

    def test_dot_failure(self):
        """Ошибка dot - RenderError с текстом ошибки."""
        failure = subprocess.CalledProcessError(1, "dot", stderr=b"bad")
        with mock.patch("subprocess.run", side_effect=failure):
            with self.assertRaises(RenderError):
                render_image("digraph {", "g.png")

    def test_open_failure(self):
        """Не удалось открыть изображение - RenderError."""
        failure = OSError("нет просмотрщика")
        with mock.patch("subprocess.run", side_effect=failure), \
                mock.patch("sys.platform", "linux"):
            with self.assertRaises(RenderError):
                open_image("g.png")


class MainTests(unittest.TestCase):
    """Проверки main: дерево, DOT, изображение."""

    def run_main(self, *extra):
        """Запускает main на ромбе; возвращает (код, stdout)."""
        argv = ["--package", "A", "--repo-mode", "test",
                "--repo", os.path.join(EXAMPLES, "diamond.txt"), *extra]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = main(argv)
        return code, out.getvalue()

    @unittest.skipUnless(HAS_DOT, "Graphviz (dot) не установлен")
    def test_ascii_tree_and_image(self):
        """Дерево и DOT выводятся, изображение сохраняется."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "g.png")
            code, text = self.run_main(
                "--ascii-tree", "--no-show", "--image", path)
            self.assertTrue(os.path.getsize(path) > 0)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("|-- B\n|   `-- D\n`-- C\n    `-- D\n", text)
        self.assertIn('digraph "A" {', text)

    def test_missing_dot_is_error(self):
        """Без Graphviz main возвращает код ошибки 1."""
        with mock.patch("subprocess.run", side_effect=FileNotFoundError):
            code, text = self.run_main("--no-show")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn('digraph "A" {', text)


if __name__ == "__main__":
    unittest.main()
