import csv
import json


def export_metrics_to_json(report_data: dict, output_path: str):
    """Сохранение собранной статистики в файл формата JSON."""
    with open(output_path, mode="w", encoding="utf-8") as file:
        # ensure_ascii=False нужен, чтобы кириллица не превращалась в коды
        json.dump(report_data, file, ensure_ascii=False, indent=4)


def export_metrics_to_csv(report_data: dict, output_path: str):
    """Выгрузка плоского отчета в формате CSV для дополнительного задания."""
    with open(output_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        # Записываем шапку таблицы
        writer.writerow(["Metric", "Key", "Value"])

        # Базовые общие метрики
        writer.writerow(["General", "total_count", report_data["total_count"]])
        writer.writerow(["General", "skipped_count", report_data["skipped_count"]])
        writer.writerow(["General", "first_timestamp", report_data["first_timestamp"]])
        writer.writerow(["General", "last_timestamp", report_data["last_timestamp"]])

        # Раскладываем словари по отдельным строкам CSV таблицы
        for level, count in report_data["level_counts"].items():
            writer.writerow(["LevelCount", level, count])

        for source, count in report_data["top_sources"].items():
            writer.writerow(["TopSourceError", source, count])