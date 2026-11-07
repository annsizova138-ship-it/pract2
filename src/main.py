"""Точка входа: граф зависимостей пакетов (формат apt)."""
import sys

from config import format_config, parse_args
from errors import ConfigError, DepGraphError

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def run(config):
    """Выполняет работу этапа 1: выводит все параметры."""
    for line in format_config(config):
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
