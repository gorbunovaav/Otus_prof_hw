import os
import re
import gzip
import json
import statistics
import structlog
from datetime import datetime
from typing import List, Dict, Optional

logger = structlog.get_logger()

LOG_DIR = "./logs"
REPORT_DIR = "./reports"
REPORT_TEMPLATE = "./templates/report.html"

def find_latest_log(log_dir: str) -> Optional[str]:
    log_files = [f for f in os.listdir(log_dir) if re.match(r'nginx-access-ui\.log-\d{8}(\.gz)?', f)]
    if not log_files:
        return None
    return max(log_files, key=lambda x: re.search(r'\d{8}', x).group())


def read_log(file_path: str) -> List[str]:
    open_func = gzip.open if file_path.endswith(".gz") else open
    with open_func(file_path, mode='rt', encoding='utf-8') as f:
        return f.readlines()


def parse_log(lines: List[str]) -> List[Dict]:
    log_pattern = re.compile(r'"[A-Z]+ (?P<url>.+?) HTTP.*" (?P<request_time>[0-9\.]+)$')
    parsed_data = []
    
    for line in lines:
        match = log_pattern.search(line)
        if match:
            parsed_data.append({
                "url": match.group("url"),
                "request_time": float(match.group("request_time"))
            })
    return parsed_data


def compute_statistics(parsed_data: List[Dict]) -> List[Dict]:
    stats = {}
    
    for entry in parsed_data:
        url, req_time = entry["url"], entry["request_time"]
        if url not in stats:
            stats[url] = []
        stats[url].append(req_time)
    
    report = []
    for url, times in stats.items():
        report.append({
            "url": url,
            "count": len(times),
            "count_perc": len(times) / len(parsed_data) * 100,
            "time_sum": sum(times),
            "time_perc": sum(times) / sum(e["request_time"] for e in parsed_data) * 100,
            "time_avg": sum(times) / len(times),
            "time_max": max(times),
            "time_med": statistics.median(times)
        })
    
    return sorted(report, key=lambda x: x["time_sum"], reverse=True)[:100]


def generate_report(report_data: List[Dict], output_file: str):
    with open(REPORT_TEMPLATE, encoding='utf-8') as template_file:
        template = template_file.read()
    
    table_json = json.dumps(report_data, indent=2)
    report_content = template.replace('$table_json', table_json)
    
    with open(output_file, 'w', encoding='utf-8') as report_file:
        report_file.write(report_content)
    
    logger.info("Report generated", file=output_file)


def main():
    log_path = os.path.join(LOG_DIR, latest_log)
    logger.info("Processing log file", file=log_path)
    
    log_lines = read_log(log_path)
    parsed_data = parse_log(log_lines)
    report_data = compute_statistics(parsed_data)
    
    report_date = re.search(r'\d{8}', latest_log).group()
    report_filename = f"report-{datetime.strptime(report_date, '%Y%m%d').strftime('%Y.%m.%d')}.html"
    report_path = os.path.join(REPORT_DIR, report_filename)
    
    generate_report(report_data, report_path)
    logger.info("Log analysis complete.")


if __name__ == "__main__":
    main()
