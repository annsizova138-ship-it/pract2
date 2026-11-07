"""Исключения приложения."""


class DepGraphError(Exception):
    """Базовая ошибка: её текст показывается пользователю."""


class ConfigError(DepGraphError):
    """Неверное значение параметра командной строки."""


class RepoError(DepGraphError):
    """Репозиторий недоступен или его данные нельзя разобрать."""


class GraphError(DepGraphError):
    """Граф зависимостей построить нельзя."""
