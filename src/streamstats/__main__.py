import argparse
import sys
from typing import final

from streamstats.analysis import LogMetrics
from streamstats.errors import StreamStatsError, UnknownFormatError
from streamstats.parsers import stream_csv_rows, stream_jsonl_lines
from streamstats.report import export_metrics_to_json

def main():
    parser = argparse.ArgumentParser(description='Потоковый анализатор.')
    parser.add_argument('input_files', nargs='+', help='Путь к входному файлу (CSV или JSONL)')
    parser.add_argument('--output', required=True, help='Путь для сохранения JSON-отчёта')
    parser.add_argument('--skip-invalid', action='store_true', help='Пропускать повреждённые строки')

    args = parser.parse_args()

    metrics = LogMetrics()
    skipped_lines = 0

    for file_path in args.input_files:
        try:
            if file_path.endswith('.jsonl'):
                log_stream = stream_jsonl_lines(file_path)
            elif file_path.endswith('.csv'):
                log_stream = stream_csv_rows(file_path)
            else:
                raise UnknownFormatError(f'Неподдерживаемый формат файла: {file_path}')

            for record in log_stream:
                try:
                    metrics.update(record)
                except StreamStatsError as error:
                    if args.skip_invalid:
                        print(f'WARNING: Пропущена строка. Причина: {error}', file=sys.stderr)
                        skipped_lines += 1
                    else:
                        raise error

        except StreamStatsError as error:
            print(f'Критическая ошибка: {error}', file=sys.stderr)
            sys.exit(2)

        except Exception as unexpected_error:
            print(f'Cистемный сбой: {unexpected_error}', file=sys.stderr)
            sys.exit(2)

final_data = metrics.get_report_data()

final_data['skipped_count'] = skipped_lines

export_metrics_to_json(final_data, args.output)

if __name__ == '__main__':
    main()