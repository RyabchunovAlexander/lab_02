from dataclasses import dataclass
from datetime import datetime

from streamstats.errors import IncorrectTimestampError, MalformedEventError

# Список валидных уровней логирования для проверки
ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass
class LogLine:
    """Модель для хранения одной валидированной строки лога."""
    timestamp: str
    level: str
    source: str
    message: str

    def __post_init__(self):
        # Проверяем корректность уровня лога
        if self.level not in ALLOWED_LEVELS:
            raise MalformedEventError(f"Неверный уровень лога: {self.level}")

        # Источник обязательно должен быть заполнен
        if not self.source:
            raise MalformedEventError("Источник не может быть пустым")

        try:
            # Заменяем Z на смещение, чтобы python корректно распарсил ISO дату
            clean_date = self.timestamp.replace("Z", "+00:00")
            datetime.fromisoformat(clean_date)
        except ValueError:
            raise IncorrectTimestampError(f"Неверный формат даты: {self.timestamp}")
