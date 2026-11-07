"""Тесты загрузки и разбора индекса apt."""
import contextlib
import gzip
import io
import lzma
import unittest

from apt_repo import (decompress, download, find_dependencies,
                      parse_dependencies, parse_packages)
from errors import RepoError
from helpers import SAMPLE_INDEX, serve
from main import EXIT_ERROR, EXIT_OK, main


class ParseTests(unittest.TestCase):
    """Проверки разбора текста индекса."""

    def test_versions_and_arch_removed(self):
        """Версии и архитектуры отбрасываются."""
        self.assertEqual(
            parse_dependencies("libc6 (>= 2.34), python3:any (>= 3)"),
            ["libc6", "python3"])

    def test_first_alternative(self):
        """Из альтернатив берётся первая."""
        self.assertEqual(parse_dependencies("a | b, c"), ["a", "c"])

    def test_duplicates_removed(self):
        """Повторы убираются."""
        self.assertEqual(parse_dependencies("a, a (>= 1), b"), ["a", "b"])

    def test_empty(self):
        """Пустое значение - пустой список."""
        self.assertEqual(parse_dependencies(""), [])

    def test_parse_packages(self):
        """Pre-Depends и Depends объединяются, строки склеиваются."""
        repo = parse_packages(SAMPLE_INDEX)
        self.assertEqual(
            repo["curl"], ["libc6", "libcurl4", "zlib1g"])
        self.assertEqual(
            repo["libcurl4"],
            ["libc6", "libssl3", "ca-certificates", "zlib1g"])
        self.assertEqual(repo["libc6"], [])
        self.assertEqual(repo["tool"], ["libc6", "libfoo"])

    def test_find_dependencies(self):
        """Прямые зависимости ищутся; неизвестный пакет - ошибка."""
        repo = parse_packages(SAMPLE_INDEX)
        self.assertEqual(find_dependencies(repo, "zlib1g"), ["libc6"])
        with self.assertRaises(RepoError):
            find_dependencies(repo, "nothing")


class DecompressTests(unittest.TestCase):
    """Проверки распаковки."""

    def test_formats(self):
        """gzip, xz и обычный текст распознаются по сигнатуре."""
        raw = SAMPLE_INDEX.encode("utf-8")
        for data in (raw, gzip.compress(raw), lzma.compress(raw)):
            self.assertEqual(decompress(data), SAMPLE_INDEX)

    def test_broken_archive(self):
        """Повреждённый архив даёт RepoError."""
        with self.assertRaises(RepoError):
            decompress(b"\x1f\x8b broken")


class NetworkTests(unittest.TestCase):
    """Проверки скачивания через локальный сервер."""

    def test_download_ok(self):
        """Данные скачиваются."""
        with serve(b"hello") as base:
            self.assertEqual(download(base + "/Packages"), b"hello")

    def test_download_404(self):
        """Ответ 404 даёт RepoError."""
        with serve(b"x") as base:
            with self.assertRaises(RepoError):
                download(base + "/missing")

    def test_download_unreachable(self):
        """Недоступный сервер даёт RepoError."""
        with self.assertRaises(RepoError):
            download("http://127.0.0.1:9/Packages")

    def test_main_url_mode(self):
        """main читает индекс по URL и строит граф."""
        body = gzip.compress(SAMPLE_INDEX.encode("utf-8"))
        with serve(body) as base:
            out = io.StringIO()
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(io.StringIO()):
                code = main(["--package", "curl", "--max-depth", "1",
                             "--repo", base + "/Packages.gz"])
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  curl -> libc6, libcurl4, zlib1g\n", out.getvalue())

    def test_main_unknown_package(self):
        """Неизвестный пакет: код ошибки 1."""
        with serve(SAMPLE_INDEX.encode("utf-8")) as base:
            with contextlib.redirect_stderr(io.StringIO()):
                code = main(["--package", "nothing",
                             "--repo", base + "/Packages"])
        self.assertEqual(code, EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
