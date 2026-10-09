from dataclasses import dataclass
from datetime import datetime
from streamstats.errors import MalformedEventError


ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass
class LogLine:
    timestamp: str
    level: str
    source: str
    message: str

    def __post_init__(self):

        if self.level not in ALLOWED_LEVELS:
            raise MalformedEventError("Неверный уровень")

        if not self.source:
            raise MalformedEventError("Источник не может быть пустым")

        try:
            datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError:
            raise MalformedEventError("Неверный формат даты")