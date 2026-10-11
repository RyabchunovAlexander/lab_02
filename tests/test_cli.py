import json
import sys

import pytest

from streamstats.__main__ import main


def test_cli_multi_files(tmp_path):
    f1 = tmp_path / "part1.jsonl"
    f2 = tmp_path / "part2.jsonl"
    report_path = tmp_path / "summary.json"

    f1.write_text(
        '{"timestamp": "2026-10-10T09:00:00Z", "level": "INFO", "source": "srv", "message": "A"}\n',
        encoding="utf-8",
    )
    f2.write_text(
        '{"timestamp": "2026-10-10T10:00:00Z", "level": "INFO", "source": "srv", "message": "B"}\n',
        encoding="utf-8",
    )

    sys.argv = ["streamstats", "analyze", str(f1), str(f2), "--format", "jsonl", "--output", str(report_path)]

    main()

    with open(report_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_count"] == 2
    assert data["level_counts"]["INFO"] == 2


def test_cli_skip_invalid(tmp_path):
    bad_file = tmp_path / "corrupted.jsonl"
    report_path = tmp_path / "skip_report.json"

    content = (
        '{"timestamp": "2026-10-10T12:00:00Z", "level": "INFO", "source": "web", "message": "Ок"}\n'
        '{"timestamp": "2026-10-10T12:01:00Z", "level": "ERROR", "source": "api", "message": БАГ}\n'
    )
    bad_file.write_text(content, encoding="utf-8")

    sys.argv = [
        "streamstats",
        "analyze",
        str(bad_file),
        "--format",
        "jsonl",
        "--output",
        str(report_path),
        "--skip-invalid",
    ]
    main()

    with open(report_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_count"] == 1
    assert data["skipped_count"] == 1


def test_cli_exit_code_two(tmp_path):
    bad_file = tmp_path / "fail.jsonl"
    report_path = tmp_path / "fail_report.json"

    bad_file.write_text(
        '{"timestamp": "2026-10-10T12:00:00Z", "level": "INFO", "source": "web", "message": БАГ}\n',
        encoding="utf-8",
    )

    sys.argv = ["streamstats", "analyze", str(bad_file), "--format", "jsonl", "--output", str(report_path)]

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2
