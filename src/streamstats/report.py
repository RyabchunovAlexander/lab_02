import json

def export_metrics_to_json(report_data: dict, output_path: str):
    with open(output_path, mode='w', encoding='utf-8') as file:
        json.dump(report_data, file, ensure_ascii=False, indent=4)