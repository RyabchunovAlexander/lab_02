class StreamStatsError(Exception):
    """Базовое исключение для анализатора."""

    def __init__(self, message: str, filename: str = None, line_number: int = None):
        super().__init__(message)
        self.filename = filename
        self.line_number = line_number


class UnknownFormatError(StreamStatsError):
    """Формат входного файла не поддерживается."""

    pass


class MalformedEventError(StreamStatsError):
    """Строка имеет неверную структуру или пустые поля."""

    pass


class IncorrectTimestampError(StreamStatsError):
    """Временная метка не соответствует стандарту."""

    pass


class IncorrectCLIArgsError(StreamStatsError):
    """Переданы некорректные параметры командной строки."""

    pass