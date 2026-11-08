"""Параметры командной строки и их проверка."""
import argparse
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from errors import ConfigError

MODE_URL = "url"
MODE_TEST = "test"
MODES = (MODE_URL, MODE_TEST)
DEFAULT_MODE = MODE_URL
DEFAULT_MAX_DEPTH = 3
MIN_DEPTH = 1
URL_SCHEMES = ("http", "https")
APT_NAME = re.compile(r"[a-z0-9][a-z0-9+.\-]*")
TEST_NAME = re.compile(r"[A-Z]+")
HELP_TITLES = {
    "usage:": "использование:",
    "optional arguments:": "параметры:",
    "options:": "параметры:",
}


@dataclass
class Config:
    """Все параметры, которые задаёт пользователь."""

    package: str
    repo: str
    repo_mode: str
    ascii_tree: bool
    max_depth: int
    filter_substring: str
    load_order: bool = False


def translate_error(message):
    """Переводит типичные сообщения argparse на русский язык."""
    prefix = "unrecognized arguments:"
    if message.startswith(prefix):
        return "неизвестные параметры:" + message[len(prefix):]
    match = re.fullmatch(r"argument (\S+): expected one argument", message)
    if match:
        return f"для параметра {match.group(1)} нужно указать значение"
    return message


class Parser(argparse.ArgumentParser):
    """Парсер, который сообщает об ошибках исключением ConfigError."""

    def error(self, message):
        """Бросает ConfigError вместо завершения программы."""
        raise ConfigError(translate_error(message))

    def format_help(self):
        """Возвращает справку с русскими заголовками разделов."""
        text = super().format_help()
        for english, russian in HELP_TITLES.items():
            text = text.replace(english, russian)
        return text


def build_parser():
    """Создаёт описание параметров командной строки."""
    parser = Parser(
        prog="dep-graph", allow_abbrev=False, add_help=False,
        description="Граф зависимостей пакетов Ubuntu (формат apt)")
    parser.add_argument(
        "-h", "--help", action="help",
        help="показать эту справку и выйти")
    parser.add_argument(
        "--package", metavar="ИМЯ", help="имя анализируемого пакета")
    parser.add_argument(
        "--repo", metavar="ПУТЬ",
        help="URL репозитория или путь к тестовому файлу")
    parser.add_argument(
        "--repo-mode", default=DEFAULT_MODE, metavar="РЕЖИМ",
        help="режим репозитория: url (настоящий) или test (файл)")
    parser.add_argument(
        "--ascii-tree", action="store_true",
        help="вывести зависимости в виде ASCII-дерева")
    parser.add_argument(
        "--max-depth", default=str(DEFAULT_MAX_DEPTH), metavar="N",
        help="максимальная глубина анализа (целое число >= 1)")
    parser.add_argument(
        "--filter", default="", metavar="ПОДСТРОКА",
        help="не учитывать пакеты, в имени которых есть эта подстрока")
    parser.add_argument(
        "--load-order", action="store_true",
        help="вывести порядок загрузки зависимостей пакета")
    return parser


def check_mode(mode):
    """Проверяет режим работы с репозиторием."""
    if mode not in MODES:
        raise ConfigError(
            f"неизвестный режим '{mode}', допустимо: url или test")
    return mode


def check_package(name, mode):
    """Проверяет имя пакета: в режиме test - большие латинские буквы."""
    if not name:
        raise ConfigError("не задано имя пакета (--package)")
    if mode == MODE_TEST:
        pattern, hint = TEST_NAME, "большие латинские буквы"
    else:
        pattern, hint = APT_NAME, "строчные латинские буквы, цифры, + . -"
    if not pattern.fullmatch(name):
        raise ConfigError(
            f"недопустимое имя пакета '{name}' (нужны: {hint})")


def check_repo(repo, mode):
    """Проверяет URL репозитория или путь к тестовому файлу."""
    if not repo:
        raise ConfigError("не задан репозиторий (--repo)")
    if mode == MODE_TEST:
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        return
    parts = urlparse(repo)
    if parts.scheme not in URL_SCHEMES or not parts.netloc:
        raise ConfigError(f"некорректный URL репозитория: {repo}")


def parse_depth(text):
    """Переводит глубину в число и проверяет, что она не меньше 1."""
    try:
        depth = int(text)
    except ValueError as err:
        raise ConfigError(
            f"глубина должна быть целым числом, получено '{text}'") from err
    if depth < MIN_DEPTH:
        raise ConfigError(f"глубина должна быть не меньше {MIN_DEPTH}")
    return depth


def check_filter(substring):
    """Подстрока не может содержать пробелов (их нет в именах пакетов)."""
    if any(char.isspace() for char in substring):
        raise ConfigError("подстрока фильтра не должна содержать пробелов")


def parse_args(argv=None):
    """Разбирает и проверяет параметры; ошибки - ConfigError."""
    args = build_parser().parse_args(argv)
    mode = check_mode(args.repo_mode)
    check_package(args.package, mode)
    check_repo(args.repo, mode)
    check_filter(args.filter)
    return Config(
        package=args.package, repo=args.repo, repo_mode=mode,
        ascii_tree=args.ascii_tree, max_depth=parse_depth(args.max_depth),
        filter_substring=args.filter, load_order=args.load_order)
