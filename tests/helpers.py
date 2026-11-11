"""Общие помощники для тестов: локальный HTTP-сервер с индексом."""
import contextlib
import functools
import http.server
import os
import tempfile
import threading

SAMPLE_INDEX = """Package: curl
Version: 8.5.0
Depends: libc6 (>= 2.34), libcurl4 (= 8.5.0), zlib1g (>= 1:1.1.4)
Description: утилита командной строки
 для передачи данных по URL

Package: libcurl4
Pre-Depends: libc6 (>= 2.34)
Depends: libssl3 | libssl-dev, ca-certificates:any,
 zlib1g (>= 1:1.1.4)
Description: библиотека для передачи данных по URL

Package: zlib1g
Depends: libc6 (>= 2.14)

Package: libc6
Description: стандартная библиотека языка C

Package: tool
Depends: libc6, libc6 (>= 2), libfoo [amd64] | libbar
"""


INDEX_FILES = ("Packages", "Packages.gz")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Отдаёт файлы из заданной папки и не печатает журнал запросов."""

    def log_message(self, *_args):
        """Не печатает журнал запросов."""


@contextlib.contextmanager
def serve(body):
    """Запускает локальный сервер и отдаёт его базовый URL.

    Файлы Packages и Packages.gz содержат body, любой другой адрес
    сервер не найдёт и ответит 404.
    """
    with tempfile.TemporaryDirectory() as folder:
        for name in INDEX_FILES:
            with open(os.path.join(folder, name), "wb") as handle:
                handle.write(body)
        handler = functools.partial(QuietHandler, directory=folder)
        server = http.server.HTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
