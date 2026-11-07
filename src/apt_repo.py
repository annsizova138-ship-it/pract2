"""Загрузка и разбор индекса пакетов Ubuntu (формат apt Packages)."""
import gzip
import lzma
import re
import urllib.error
import urllib.request

from errors import RepoError

TIMEOUT_SECONDS = 60
GZIP_MAGIC = b"\x1f\x8b"
XZ_MAGIC = b"\xfd7zXZ\x00"
CONTINUATION = " \t"
WANTED_FIELDS = ("Package", "Depends", "Pre-Depends")
DEPENDENCY_FIELDS = ("Pre-Depends", "Depends")
NAME_AT_START = re.compile(r"[a-z0-9][a-z0-9+.\-]*")


def download(url):
    """Скачивает файл по URL и возвращает его байты."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as reply:
            return reply.read()
    except urllib.error.HTTPError as err:
        raise RepoError(
            f"сервер ответил {err.code} {err.reason}: {url}") from err
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise RepoError(f"не удалось скачать {url}: {err}") from err


def decompress(data):
    """Распаковывает gzip или xz (по сигнатуре) и возвращает текст."""
    try:
        if data.startswith(GZIP_MAGIC):
            data = gzip.decompress(data)
        elif data.startswith(XZ_MAGIC):
            data = lzma.decompress(data)
    except (OSError, EOFError, lzma.LZMAError) as err:
        raise RepoError(f"не удалось распаковать индекс: {err}") from err
    return data.decode("utf-8", errors="replace")


def iter_stanzas(text):
    """Делит текст индекса на записи: словари {поле: значение}."""
    fields = {}
    last = None
    for line in text.splitlines():
        if not line.strip():
            if fields:
                yield fields
            fields, last = {}, None
        elif line[0] in CONTINUATION:
            if last is not None:
                fields[last] += " " + line.strip()
        else:
            name, _, value = line.partition(":")
            last = name if name in WANTED_FIELDS else None
            if last is not None:
                fields[last] = value.strip()
    if fields:
        yield fields


def parse_dependencies(value):
    """Достаёт имена пакетов из значения поля Depends.

    Версии и архитектуры отбрасываются, из альтернатив 'a | b'
    берётся первая.
    """
    names = []
    for group in value.split(","):
        first = group.split("|")[0].strip()
        match = NAME_AT_START.match(first)
        if match and match.group() not in names:
            names.append(match.group())
    return names


def parse_packages(text):
    """Разбирает индекс в словарь {пакет: [прямые зависимости]}."""
    repo = {}
    for fields in iter_stanzas(text):
        name = fields.get("Package")
        if name is None or name in repo:
            continue
        deps = []
        for field in DEPENDENCY_FIELDS:
            for dep in parse_dependencies(fields.get(field, "")):
                if dep not in deps:
                    deps.append(dep)
        repo[name] = deps
    return repo


def load_apt_repository(url):
    """Скачивает индекс по URL и возвращает словарь зависимостей."""
    return parse_packages(decompress(download(url)))


def find_dependencies(repo, name):
    """Возвращает прямые зависимости пакета или бросает RepoError."""
    if name not in repo:
        raise RepoError(f"пакет '{name}' не найден в репозитории")
    return repo[name]
