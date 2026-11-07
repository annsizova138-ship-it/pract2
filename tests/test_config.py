"""Тесты параметров командной строки."""
import contextlib
import io
import os
import unittest

from config import Config, build_parser, format_config, parse_args
from errors import ConfigError
from main import EXIT_OK, EXIT_USAGE, main

THIS_FILE = os.path.abspath(__file__)
URL = "http://archive.ubuntu.com/ubuntu/dists/noble/main/Packages.gz"


class ParseArgsTests(unittest.TestCase):
    """Проверки разбора и проверки параметров."""

    def test_defaults(self):
        """Обязательные параметры заданы, остальные - по умолчанию."""
        config = parse_args(["--package", "curl", "--repo", URL])
        self.assertEqual(config, Config(
            "curl", URL, "url", False, 3, ""))

    def test_all_params(self):
        """Все параметры читаются."""
        config = parse_args([
            "--package", "curl", "--repo", URL, "--repo-mode", "url",
            "--ascii-tree", "--max-depth", "5", "--filter", "lib"])
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 5)
        self.assertEqual(config.filter_substring, "lib")

    def test_test_mode(self):
        """В режиме test путь - существующий файл, имя - заглавные буквы."""
        config = parse_args([
            "--package", "A", "--repo", THIS_FILE, "--repo-mode", "test"])
        self.assertEqual(config.repo_mode, "test")

    def test_errors(self):
        """Каждый неверный параметр даёт ConfigError."""
        bad = {
            "нет пакета": ["--repo", URL],
            "пакет с заглавными": ["--package", "Curl", "--repo", URL],
            "пакет с пробелом": ["--package", "a b", "--repo", URL],
            "пакет в test строчными": [
                "--package", "a", "--repo", THIS_FILE,
                "--repo-mode", "test"],
            "нет репозитория": ["--package", "curl"],
            "не http": ["--package", "curl", "--repo", "ftp://x.org/p"],
            "не URL": ["--package", "curl", "--repo", "just text"],
            "нет файла": [
                "--package", "A", "--repo", "no_such_file.txt",
                "--repo-mode", "test"],
            "неизвестный режим": [
                "--package", "curl", "--repo", URL, "--repo-mode", "x"],
            "глубина не число": [
                "--package", "curl", "--repo", URL, "--max-depth", "abc"],
            "глубина ноль": [
                "--package", "curl", "--repo", URL, "--max-depth", "0"],
            "глубина отрицательная": [
                "--package", "curl", "--repo", URL, "--max-depth", "-2"],
            "фильтр с пробелом": [
                "--package", "curl", "--repo", URL, "--filter", "a b"],
            "неизвестная опция": [
                "--package", "curl", "--repo", URL, "--bogus"],
        }
        for title, argv in bad.items():
            with self.subTest(title):
                with self.assertRaises(ConfigError):
                    parse_args(argv)

    def test_format_config(self):
        """Параметры выводятся как 'ключ: значение'."""
        config = Config("curl", URL, "url", True, 4, "")
        self.assertEqual(format_config(config), [
            "package: curl", f"repo: {URL}", "repo-mode: url",
            "ascii-tree: true", "max-depth: 4", 'filter: ""'])


class RussianTextTests(unittest.TestCase):
    """Проверки русских сообщений argparse."""

    def test_help_in_russian(self):
        """Справка выводится по-русски."""
        text = build_parser().format_help()
        self.assertIn("использование:", text)
        self.assertIn("параметры:", text)
        self.assertNotIn("usage:", text)

    def test_unknown_option_message(self):
        """Сообщение о неизвестном параметре - по-русски."""
        with self.assertRaises(ConfigError) as caught:
            parse_args(["--package", "curl", "--repo", URL, "--bogus"])
        self.assertIn("неизвестные параметры", str(caught.exception))

    def test_missing_value_message(self):
        """Сообщение об отсутствующем значении - по-русски."""
        with self.assertRaises(ConfigError) as caught:
            parse_args(["--package"])
        self.assertIn("нужно указать значение", str(caught.exception))


class MainTests(unittest.TestCase):
    """Проверки точки входа."""

    def test_prints_params(self):
        """При запуске выводятся все параметры."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["--package", "curl", "--repo", URL])
        self.assertEqual(code, EXIT_OK)
        self.assertIn("package: curl", out.getvalue())
        self.assertIn("max-depth: 3", out.getvalue())

    def test_error_exit_code(self):
        """Ошибка параметров: сообщение в stderr и код 2."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["--package", "curl"])
        self.assertEqual(code, EXIT_USAGE)
        self.assertIn("--repo", err.getvalue())


if __name__ == "__main__":
    unittest.main()
