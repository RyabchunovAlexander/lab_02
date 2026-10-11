from dataclasses import dataclass
from datetime import datetime

from streamstats.errors import IncorrectTimestampError, MalformedEventError

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass
class LogLine:
    timestamp: str
    level: str
    source: str
    message: str

    def __post_init__(self):

        if self.level not in ALLOWED_LEVELS:
            raise MalformedEventError(f"Неверный уровень лога: {self.level}")

        if not self.source:
            raise MalformedEventError("Источник не может быть пустым")

        try:
            clean_date = self.timestamp.replace("Z", "+00:00")
            datetime.fromisoformat(clean_date)
        except ValueError:
            raise IncorrectTimestampError(f"Неверный формат даты: {self.timestamp}")
