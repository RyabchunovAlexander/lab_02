from streamstats.errors import MalformedEventError
from streamstats.parsers import stream_csv_rows, stream_jsonl_lines


def test_jsonl_ok(tmp_path):
    """Обычное чтение правильного лога с кириллицей."""
    path = tmp_path / "system.jsonl"
    line = (
        '{"timestamp": "2026-10-10T08:30:15Z", "level": "DEBUG", '
        '"source": "network", "message": "Связь установлена"}\n'
    )
    path.write_text(line, encoding="utf-8")

    res = list(stream_jsonl_lines(str(path)))
    assert len(res) == 1
    assert res[0].level == "DEBUG"
    assert res[0].message == "Связь установлена"


def test_jsonl_empty(tmp_path):
    """Тест пустого файла."""
    path = tmp_path / "null_data.jsonl"
    path.write_text("", encoding="utf-8")

    assert len(list(stream_jsonl_lines(str(path)))) == 0


def test_jsonl_bad(tmp_path):
    """Тест поврежденной JSONL строки."""
    path = tmp_path / "corrupted.jsonl"
    text = (
        '{"timestamp": "2026-10-10T14:15:00Z", "level": "INFO", '
        '"source": "web", "message": "OK"}\n'
        '{"timestamp": "2026-10-10T14:16:00Z", "level": "CRITICAL", '
        '"source": "billing", "message": ТЕКСТ_БЕЗ_КАВЫЧЕК}\n'
    )
    path.write_text(text, encoding="utf-8")

    res = list(stream_jsonl_lines(str(path)))
    assert len(res) == 2
    assert isinstance(res[1], MalformedEventError)
    assert res[1].line_number == 2


def test_csv_ok(tmp_path):
    """Обычное чтение правильного CSV с шапкой."""
    path = tmp_path / "metrics.csv"
    text = (
        "timestamp,level,source,message\n"
        "2026-10-10T17:45:00Z,WARNING,database,Диск почти заполнен\n"
    )
    path.write_text(text, encoding="utf-8")

    res = list(stream_csv_rows(str(path)))
    assert len(res) == 1
    assert res[0].level == "WARNING"
    assert res[0].message == "Диск почти заполнен"


def test_csv_empty(tmp_path):
    """Тест пустого CSV файла."""
    path = tmp_path / "blank.csv"
    path.write_text("", encoding="utf-8")

    assert len(list(stream_csv_rows(str(path)))) == 0


def test_csv_bad(tmp_path):
    """Тест строки CSV с неверным количеством колонок."""
    path = tmp_path / "broken_fields.csv"
    text = (
        "timestamp,level,source,message\n2026-10-10T21:10:00Z,ERROR,security_service\n"
    )
    path.write_text(text, encoding="utf-8")

    res = list(stream_csv_rows(str(path)))
    assert len(res) == 1
    assert isinstance(res[0], MalformedEventError)
    assert res[0].line_number == 2
