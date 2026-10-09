import csv
import json

from streamstats.errors import MalformedEventError, UnknownFormatError
from streamstats.models import LogLine

def stream_jsonl_lines(file_path: str):
    """Потоковое чтение и валидация строк из файла формата JSONL."""
    with open(file_path, mode="r", encoding="utf-8") as file:
        for line_number, text_line in enumerate(file, start=1):
            clean_line = text_line.strip()

            if not clean_line:
                continue

            try:
                data = json.loads(clean_line)
            except json.JSONDecodeError:
                raise MalformedEventError(
                    message = f"Неверный JSON в строке {line_number}",
                    filename = file_path,
                    line_number = line_number
                )

            for field in ("timestamp", "level", "source", "message"):
                if field not in data:
                    raise MalformedEventError(
                        message = f"Отсутствует обязательное поле {field}",
                        filename = file_path,
                        line_number = line_number
                    )

            try:
                log_line = LogLine(
                    timestamp = data["timestamp"],
                    level = data["level"],
                    source = data["source"],
                    message = data["message"]
                )
                yield log_line
            except MalformedEventError as e:
                e.filename = file_path
                e.line_number = line_number
                raise e


def stream_csv_rows(file_path: str):
    """Читаем файл CSV построчно и проверяем события"""
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        try:
            header = next(reader)
        except StopIteration:
            return

        for field in ('timestamp', 'level', 'source', 'message'):
            if field not in header:
                raise MalformedEventError(
                    message = f'В CSV отсутствует обязательный столбец: {field}',
                    filename = file_path,
                    line_number = 1
                )

        for line_number, row in enumerate(reader, start = 2):
            if len(row) != len(header):
                raise MalformedEventError(
                    message = f'Неверное количество колонок в строке {line_number}',
                    filename = file_path,
                    line_number = line_number
                )

            data = dict(zip(header, row))

            try:
                log_line = LogLine(
                    timestamp = data["timestamp"],
                    level = data["level"],
                    source = data["source"],
                    message = data["message"]
                )
                yield log_line
            except MalformedEventError as e:
                e.filename = file_path
                e.line_number = line_number
                raise e