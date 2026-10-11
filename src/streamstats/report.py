import csv
import json


def export_metrics_to_json(report_data: dict, output_path: str):
    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(report_data, file, ensure_ascii=False, indent=4)


def export_metrics_to_csv(report_data: dict, output_path: str):
    with open(output_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Key", "Value"])

        writer.writerow(["General", "total_count", report_data["total_count"]])
        writer.writerow(["General", "skipped_count", report_data["skipped_count"]])
        writer.writerow(["General", "first_timestamp", report_data["first_timestamp"]])
        writer.writerow(["General", "last_timestamp", report_data["last_timestamp"]])

        for level, count in report_data["level_counts"].items():
            writer.writerow(["LevelCount", level, count])

        for source, count in report_data["top_sources"].items():
            writer.writerow(["TopSourceError", source, count])