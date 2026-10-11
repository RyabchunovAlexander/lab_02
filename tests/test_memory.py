import os
import sys
import tracemalloc

from streamstats.__main__ import main


def test_streaming_memory(tmp_path):
    log_file = tmp_path / "huge.jsonl"
    report_file = tmp_path / "rep.json"

    line = b'{"timestamp": "2026-10-11T12:00:00Z", "level": "INFO", "source": "srv", "message": "A"}\n'

    with open(log_file, mode="wb") as f:
        f.writelines(line * 15000 for _ in range(510))

    file_size_mb = os.path.getsize(log_file) / (1024 * 1024)

    sys.argv = [
        "streamstats",
        "analyze",
        str(log_file),
        "--format",
        "jsonl",
        "--output",
        str(report_file),
    ]

    tracemalloc.start()
    main()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024 * 1024)
    print(f"\n[MEMORY TEST] File size: {file_size_mb:.2f} MB | Peak RAM: {peak_mb:.2f} MB")

    assert peak_mb < 50.0

