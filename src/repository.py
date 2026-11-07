"""Выбор источника данных: настоящий репозиторий или тестовый файл."""
from apt_repo import load_apt_repository
from config import MODE_TEST
from file_repo import load_test_repository


def load_repository(config):
    """Возвращает словарь {пакет: [прямые зависимости]}."""
    if config.repo_mode == MODE_TEST:
        return load_test_repository(config.repo)
    return load_apt_repository(config.repo)
