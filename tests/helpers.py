"""Общие помощники для тестов: локальный HTTP-сервер с индексом."""
import contextlib
import functools
import http.server
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


class _Handler(http.server.BaseHTTPRequestHandler):
    """Отдаёт заранее заданные байты или 404."""

    def __init__(self, body, *args, **kwargs):
        """Запоминает тело ответа."""
        self.body = body
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Отвечает на GET: /Packages - данные, остальное - 404."""
        if self.path.startswith("/Packages"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.body)
        else:
            self.send_error(404)

    def log_message(self, *_args):
        """Не печатает журнал запросов."""


@contextlib.contextmanager
def serve(body):
    """Запускает локальный сервер и отдаёт его базовый URL."""
    handler = functools.partial(_Handler, body)
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
