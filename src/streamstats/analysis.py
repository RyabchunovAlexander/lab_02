from collections import Counter

class LogMetrics:
    def __init__(self):
        self.total_count = 0
        self.level_counts = Counter()
        self.top_sources = Counter()

    def update(self, log_line):
        self.total_count += 1
        self.level_counts[log_line.level] += 1

        if log_line.level in ("ERROR", "CRITICAL"):
            self.top_sources[log_line.source] += 1

    def get_report_data(self):

        level_report = dict(self.level_counts)

        top_five = dict(self.top_sources.most_common(5))

        return {
            "total_count": self.total_count,
            "level_counts": level_report,
            "top_sources": top_five,
        }