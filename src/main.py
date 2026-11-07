"""Точка входа: граф зависимостей пакетов (формат apt)."""
import sys

from config import parse_args
from errors import ConfigError, DepGraphError
from graph import build_graph, find_cycles
from render import format_graph
from repository import load_repository

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def run(config):
    """Выполняет работу этапа 3: строит и выводит граф зависимостей."""
    print(f"Источник: {config.repo}", file=sys.stderr)
    repo = load_repository(config)
    graph = build_graph(
        repo, config.package, config.max_depth, config.filter_substring)
    for line in format_graph(graph, find_cycles(graph)):
        print(line)


def main(argv=None):
    """Читает параметры и запускает работу; возвращает код выхода."""
    try:
        run(parse_args(argv))
    except ConfigError as err:
        print(f"Ошибка параметров: {err}", file=sys.stderr)
        print("Подсказка: python src/main.py --help", file=sys.stderr)
        return EXIT_USAGE
    except DepGraphError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
