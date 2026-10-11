class StreamStatsError(Exception):
    """Базовое исключение для анализатора."""

    def __init__(self, message: str, filename: str | None = None, line_number: int | None = None):
        super().__init__(message)
        self.filename = filename
        self.line_number = line_number


class UnknownFormatError(StreamStatsError):
    """Формат входного файла не поддерживается."""


class MalformedEventError(StreamStatsError):
    """Строка имеет неверную структуру или пустые поля."""


class IncorrectTimestampError(StreamStatsError):
    """Временная метка не соответствует стандарту."""


class IncorrectCLIArgsError(StreamStatsError):
    """Переданы некорректные параметры командной строки."""
