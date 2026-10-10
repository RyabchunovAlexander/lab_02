from collections import Counter

class LogMetrics:
    def __init__(self):
        self.total_count = 0
        self.level_counts = Counter()
        self.top_sources = Counter()
        self.first_timestamp = None
        self.last_timestamp = None

    def update(self, log_line):
        self.total_count += 1
        self.level_counts[log_line.level] += 1

        if log_line.level in ("ERROR", "CRITICAL"):
            self.top_sources[log_line.source] += 1

        if self.first_timestamp is None:
            self.first_timestamp = log_line.timestamp

        self.last_timestamp = log_line.timestamp

    def get_report_data(self):

        level_report = dict(self.level_counts)

        top_five = dict(self.top_sources.most_common(5))

        return {
            "total_count": self.total_count,
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "level_counts": level_report,
            "top_sources": top_five,
        }