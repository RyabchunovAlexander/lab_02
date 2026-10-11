class StreamStatsError(Exception):
    """Базовый класс ошибок для всего проекта."""

    def __init__(self, message: str, filename: str | None = None, line_number: int | None = None):
        super().__init__(message)
        self.filename = filename
        self.line_number = line_number


class UnknownFormatError(StreamStatsError):
    """Ошибка, если передан неподдерживаемый формат файла."""


class MalformedEventError(StreamStatsError):
    """Ошибка валидации: битая структура или пустые поля."""


class IncorrectTimestampError(StreamStatsError):
    """Ошибка, дата не в формате ISO 8601."""


class IncorrectCLIArgsError(StreamStatsError):
    """Ошибка при передаче неверных аргументов в консоли."""
