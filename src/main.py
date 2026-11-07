"""Точка входа: граф зависимостей пакетов (формат apt)."""
import sys

from apt_repo import find_dependencies, load_apt_repository
from config import MODE_TEST, parse_args
from errors import ConfigError, DepGraphError, RepoError

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def run(config):
    """Выполняет работу этапа 2: выводит прямые зависимости пакета."""
    if config.repo_mode == MODE_TEST:
        raise RepoError("тестовый режим появится на следующем этапе")
    print(f"Загрузка индекса: {config.repo}", file=sys.stderr)
    repo = load_apt_repository(config.repo)
    deps = find_dependencies(repo, config.package)
    print(f"Прямые зависимости пакета {config.package}:")
    for dep in deps:
        print(f"  {dep}")
    if not deps:
        print("  (нет)")


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
