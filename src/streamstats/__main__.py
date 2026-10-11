import argparse
import sys

from streamstats.analysis import LogMetrics
from streamstats.errors import (
    IncorrectCLIArgsError,
    StreamStatsError,
)
from streamstats.models import LogLine
from streamstats.parsers import stream_csv_rows, stream_jsonl_lines
from streamstats.report import export_metrics_to_json


def main():
    parser = argparse.ArgumentParser(description="Потоковый анализатор логов.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze", help="Анализ файлов логов")

    analyze_parser.add_argument("input_files", nargs="+", help="Путь к входным файлам логов")
    analyze_parser.add_argument(
        "--format", required=True, choices=["csv", "jsonl"], help="Формат входных файлов"
    )
    analyze_parser.add_argument(
        "--output", required=True, help="Путь для сохранения JSON-отчета"
    )
    analyze_parser.add_argument(
        "--skip-invalid", action="store_true", help="Пропускать поврежденные строки"
    )

    def cli_error(message):
        raise IncorrectCLIArgsError(message)

    parser.error = cli_error

    try:
        args = parser.parse_args()
    except IncorrectCLIArgsError as error:
        print(f"Ошибка параметров CLI: {error}", file=sys.stderr)
        sys.exit(2)

    metrics = LogMetrics()
    skipped_lines = 0

    for file_path in args.input_files:
        try:
            if args.format == "jsonl":
                log_stream = stream_jsonl_lines(file_path)
            elif args.format == "csv":
                log_stream = stream_csv_rows(file_path)

            for item in log_stream:
                if isinstance(item, StreamStatsError):
                    if args.skip_invalid:
                        print(
                            f"WARNING: Пропущена строка. Причина: {item}",
                            file=sys.stderr,
                        )
                        skipped_lines += 1
                    else:
                        log_context = f" в файле {item.filename} на строке {item.line_number}" if getattr(item, "filename", None) and getattr(item, "line_number", None) else ""
                        print(f"Критическая ошибка{log_context}: {item}", file=sys.stderr)
                        sys.exit(2)
                elif isinstance(item, LogLine):
                    metrics.update(item)


        except StreamStatsError as error:
            log_context = f" в файле {error.filename} на строке {error.line_number}" if getattr(error, "filename", None) and getattr(error, "line_number", None) else ""
            print(f"Критическая ошибка{log_context}: {error}", file=sys.stderr)
            sys.exit(2)
        except Exception as unexpected_error: # noqa: BLE001
            print(f"Системный сбой: {unexpected_error}", file=sys.stderr)
            sys.exit(2)

    final_data = metrics.get_report_data()
    final_data["skipped_count"] = skipped_lines

    if args.output.endswith(".csv"):
        from streamstats.report import export_metrics_to_csv
        export_metrics_to_csv(final_data, args.output)
    else:
        export_metrics_to_json(final_data, args.output)


if __name__ == "__main__":
    main()
