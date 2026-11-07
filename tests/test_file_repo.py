"""Тесты разбора тестового репозитория."""
import os
import unittest

from errors import RepoError
from file_repo import load_test_repository, parse_test_repository

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


class FileRepoTests(unittest.TestCase):
    """Проверки формата 'A: B C'."""

    def test_parse(self):
        """Зависимости читаются; комментарии и пустые строки пропускаются."""
        text = "# комментарий\nA: B, C  # хвост\n\nB:\nC: B B\n"
        self.assertEqual(
            parse_test_repository(text),
            {"A": ["B", "C"], "B": [], "C": ["B"]})

    def test_errors(self):
        """Неверные строки дают RepoError."""
        bad = ["A B", "a: B", "A: b", "A: B\nA: C", "1: A"]
        for text in bad:
            with self.subTest(text):
                with self.assertRaises(RepoError):
                    parse_test_repository(text)

    def test_load_example(self):
        """Пример из examples читается."""
        repo = load_test_repository(os.path.join(EXAMPLES, "diamond.txt"))
        self.assertEqual(repo["A"], ["B", "C"])

    def test_missing_file(self):
        """Нет файла - RepoError."""
        with self.assertRaises(RepoError):
            load_test_repository("no_such_repo.txt")


if __name__ == "__main__":
    unittest.main()
