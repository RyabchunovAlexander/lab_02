import csv
import json

from streamstats.errors import MalformedEventError, StreamStatsError
from streamstats.models import LogLine


def stream_jsonl_lines(file_path: str):
    """Построчное чтение и валидация файлов формата JSONL."""
    with open(file_path, mode="r", encoding="utf-8") as file:
        for line_number, text_line in enumerate(file, start=1):
            clean_line = text_line.strip()
            if not clean_line:
                continue

            try:
                data = json.loads(clean_line)

                # Проверяем, что в словаре есть все нужные ключи
                for field in ("timestamp", "level", "source", "message"):
                    if field not in data:
                        raise MalformedEventError(f"Отсутствует обязательное поле: {field}")

                yield LogLine(
                    timestamp=data["timestamp"],
                    level=data["level"],
                    source=data["source"],
                    message=data["message"],
                )
            except json.JSONDecodeError:
                yield MalformedEventError(
                    message=f"Неверный JSON в строке {line_number}",
                    filename=file_path,
                    line_number=line_number,
                )
            except (MalformedEventError, Exception) as error:
                # Ловим ошибки валидации полей из LogLine и оборачиваем контекстом
                if isinstance(error, StreamStatsError):
                    error.line_number = line_number
                    error.filename = file_path
                    yield error
                else:
                    raise


def stream_csv_rows(file_path: str):
    """Построчное чтение и валидация файлов формата CSV."""
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            # Считываем первую строчку как заголовки
            headers = next(reader)
        except StopIteration:
            return

        expected_count = len(headers)

        for line_number, row in enumerate(reader, start=2):
            # Пропускаем пустые строки
            if not row or all(not cell.strip() for cell in row):
                continue

            try:
                # Проверяем длину текущей строки лога
                if len(row) != expected_count:
                    raise MalformedEventError(
                        message=f"Неверное количество колонок в строке {line_number}",
                        filename=file_path,
                        line_number=line_number,
                    )

                data = dict(zip(headers, row))

                # Проверяем наличие обязательных колонок
                for field in ("timestamp", "level", "source", "message"):
                    if field not in data:
                        raise MalformedEventError(f"В CSV отсутствует обязательный столбец: {field}")

                yield LogLine(
                    timestamp=data["timestamp"],
                    level=data["level"],
                    source=data["source"],
                    message=data["message"],
                )
            except (MalformedEventError, Exception) as error:
                if isinstance(error, StreamStatsError):
                    error.line_number = line_number
                    error.filename = file_path
                    yield error
                else:
                    raise