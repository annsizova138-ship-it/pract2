"""Точка входа: граф зависимостей пакетов (формат apt)."""
import os
import sys
import tempfile

from config import parse_args
from errors import ConfigError, DepGraphError
from graph import build_graph, find_cycles
from order import load_order
from render import (ascii_tree, format_cycles, format_order, open_image,
                    render_image, to_dot)
from repository import load_repository

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def image_path(config):
    """Путь к изображению: заданный пользователем или во временной папке."""
    if config.image:
        return config.image
    name = f"dep-graph-{config.package}.png"
    return os.path.join(tempfile.gettempdir(), name)


def show_image(dot_text, config):
    """Строит изображение графа и (если не запрещено) открывает его."""
    path = image_path(config)
    render_image(dot_text, path)
    print(f"Изображение сохранено: {path}", file=sys.stderr)
    if not config.no_show:
        open_image(path)


def run(config):
    """Строит граф и выводит порядок загрузки, дерево, DOT и картинку."""
    print(f"Источник: {config.repo}", file=sys.stderr)
    repo = load_repository(config)
    graph = build_graph(
        repo, config.package, config.max_depth, config.filter_substring)
    cycles = find_cycles(graph)
    if config.load_order:
        print("\n".join(format_order(graph, load_order(graph), cycles)))
        return
    if config.ascii_tree:
        print("\n".join(ascii_tree(graph)))
    if cycles:
        print("\n".join(format_cycles(cycles)), file=sys.stderr)
    dot_text = to_dot(graph, cycles)
    print(dot_text)
    show_image(dot_text, config)


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
