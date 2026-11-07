"""Тестовый репозиторий: файл с описанием графа, пакеты - A, B, C ..."""
from config import TEST_NAME
from errors import RepoError

COMMENT = "#"
SEPARATOR = ":"


def split_definition(line, number):
    """Разбирает строку 'A: B C' в пару (имя, список зависимостей)."""
    name, colon, rest = line.partition(SEPARATOR)
    name = name.strip()
    if not colon:
        raise RepoError(f"строка {number}: нет двоеточия после имени")
    deps = []
    for word in [name] + rest.replace(",", " ").split():
        if not TEST_NAME.fullmatch(word):
            raise RepoError(
                f"строка {number}: имя '{word}' должно состоять "
                "из больших латинских букв")
        deps.append(word)
    unique = list(dict.fromkeys(deps[1:]))
    return name, unique


def parse_test_repository(text):
    """Разбирает текст тестового файла в {пакет: [зависимости]}."""
    repo = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split(COMMENT, 1)[0].strip()
        if not line:
            continue
        name, deps = split_definition(line, number)
        if name in repo:
            raise RepoError(f"строка {number}: пакет {name} описан дважды")
        repo[name] = deps
    return repo


def load_test_repository(path):
    """Читает тестовый файл и возвращает словарь зависимостей."""
    try:
        with open(path, encoding="utf-8-sig") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as err:
        raise RepoError(f"не удалось прочитать {path}: {err}") from err
    return parse_test_repository(text)
