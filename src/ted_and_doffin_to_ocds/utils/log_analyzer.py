import multiprocessing as mp
import os
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from itertools import islice
from pathlib import Path
from typing import Any


def chunk_reader(file_path: Path, chunk_size: int = 10000) -> list[str]:
    """Read file in chunks."""
    with file_path.open() as f:
        while True:
            lines = list(islice(f, chunk_size))
            if not lines:
                break
            yield lines


def process_chunk(chunk: list[str], patterns: dict) -> dict:
    """Process a chunk of log lines in parallel."""
    results = {
        "warnings": Counter(),
        "errors": Counter(),
        "error_timestamps": {},
        "module_stats": {},  # Changed from defaultdict to regular dict
        "processing_times": {},
        "error_details": {},  # Add storage for actual error messages
    }

    current_file = ""
    start_time = None
    error_lines = []
    in_error = False

    for _idx, line in enumerate(chunk):
        match = patterns["log"].match(line)
        if match:
            # If we were collecting error lines, store them with the previous error
            if error_lines and in_error:
                last_error = list(results["error_timestamps"].values())[-1]
                last_error["details"] = "\n".join(error_lines)
                error_lines = []
                in_error = False

            entry = match.groupdict()
            timestamp = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")

            # Process the entry similar to the main parse_logs method
            if start_match := patterns["start"].search(entry["message"]):
                current_file = start_match.group(1)
                start_time = timestamp
            elif patterns["end"].search(entry["message"]):
                if start_time and current_file:
                    results["processing_times"][current_file] = (
                        timestamp - start_time
                    ).total_seconds()

            level = entry["level"]
            message = entry["message"]
            module = entry["module"]

            # Initialize module stats if needed
            if module not in results["module_stats"]:
                results["module_stats"][module] = {}
            if level not in results["module_stats"][module]:
                results["module_stats"][module][level] = 0

            if level == "WARNING":
                results["warnings"][message] += 1
            elif level == "ERROR":
                in_error = True
                error_lines = [message]
                results["error_timestamps"][message] = {
                    "first": timestamp,
                    "last": timestamp,
                    "details": message,
                }
                results["errors"][message] += 1

            results["module_stats"][module][level] += 1
        elif in_error:
            # Collect non-log lines that are part of error details
            error_lines.append(line.strip())

    # Handle any remaining error lines
    if error_lines and in_error:
        last_error = list(results["error_timestamps"].values())[-1]
        last_error["details"] = "\n".join(error_lines)

    return results


def categorize_error(error_msg: str) -> str:
    """Categorize error messages into types."""
    if "Invalid date/time format" in error_msg:
        return "Date Format Error"
    if "list index out of range" in error_msg:
        return "Index Error"
    if "'relatedLot'" in error_msg:
        return "Related Lot Error"
    if "Undefined namespace prefix" in error_msg:
        return "XML Namespace Error"
    if "could not convert string to float" in error_msg:
        return "Number Format Error"
    return "Other Error"


class LogAnalyzer:
    """Analyzes application log files to extract metrics and patterns."""

    LOG_PATTERN = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - "
        r"(?P<module>[\w\.]+) - "
        r"(?P<level>\w+) - "
        r"(?P<message>.*)"
    )
    PROCESSING_START_PATTERN = re.compile(r"Processing file: (.+)")
    PROCESSING_END_PATTERN = re.compile(r"Successfully processed file: (.+)")

    def __init__(self, log_file: Path) -> None:
        """Initialize log analyzer with log file path.

        Args:
            log_file: Path to log file to analyze
        """
        self.log_file = log_file
        self.entries: list[dict[str, Any]] = []
        self.warnings = Counter()
        self.errors = Counter()
        self.processing_times: dict[str, float] = {}
        self.module_stats = defaultdict(lambda: defaultdict(int))
        self.error_timestamps: dict[str, dict[str, datetime]] = {}
        self.processed_files: set[str] = set()
        self.file_errors: dict[str, list[dict[str, Any]]] = {}

    def parse_logs(self) -> None:
        """Parse log file and collect statistics using multiple processes."""
        chunk_size = 10000  # Lines per chunk
        patterns = {
            "log": self.LOG_PATTERN,
            "start": self.PROCESSING_START_PATTERN,
            "end": self.PROCESSING_END_PATTERN,
        }

        # Initialize multiprocessing pool with number of CPU cores
        num_processes = os.cpu_count() or 1
        with mp.Pool(processes=num_processes) as pool:
            # Process chunks in parallel
            chunks = chunk_reader(self.log_file, chunk_size)
            results = pool.starmap(
                process_chunk, ((chunk, patterns) for chunk in chunks)
            )

        # Merge results from all processes
        for result in results:
            self.warnings.update(result["warnings"])
            self.errors.update(result["errors"])
            self.processing_times.update(result["processing_times"])

            # Merge error timestamps
            for msg, stamps in result["error_timestamps"].items():
                if msg not in self.error_timestamps:
                    self.error_timestamps[msg] = stamps
                else:
                    self.error_timestamps[msg]["first"] = min(
                        stamps["first"], self.error_timestamps[msg]["first"]
                    )
                    self.error_timestamps[msg]["last"] = max(
                        stamps["last"], self.error_timestamps[msg]["last"]
                    )

            # Merge module statistics using regular dict operations
            for module, stats in result["module_stats"].items():
                if module not in self.module_stats:
                    self.module_stats[module] = defaultdict(int)
                for level, count in stats.items():
                    self.module_stats[module][level] += count

        # After merging other results, process file errors
        for entry in self.entries:
            if entry["level"] == "ERROR":
                # Try to find filename in error message
                msg = entry["message"]
                if "file:" in msg:
                    filename = msg.split("file:")[-1].strip()
                    if filename not in self.file_errors:
                        self.file_errors[filename] = []
                    self.file_errors[filename].append(
                        {
                            "timestamp": entry["timestamp"],
                            "error": msg,
                            "module": entry["module"],
                        }
                    )

    def get_most_common_warnings(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most frequent warning messages.

        Args:
            limit: Number of top warnings to return

        Returns:
            List of (warning message, count) tuples
        """
        return self.warnings.most_common(limit)

    def get_most_common_errors(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most frequent error messages.

        Args:
            limit: Number of top errors to return

        Returns:
            List of (error message, count) tuples
        """
        return self.errors.most_common(limit)

    def get_slow_files(self, threshold: float = 5.0) -> list[tuple[str, float]]:
        """Get files that took longer than threshold to process.

        Args:
            threshold: Time threshold in seconds

        Returns:
            List of (filename, duration) tuples
        """
        return [(f, t) for f, t in self.processing_times.items() if t > threshold]

    def get_module_statistics(self) -> dict[str, dict[str, int]]:
        """Get message statistics per module.

        Returns:
            Dict mapping module names to their message counts by level
        """
        return dict(self.module_stats)

    def get_error_details(self) -> list[dict[str, Any]]:
        """Get detailed information about each error type.

        Returns:
            List of dicts containing error details including first/last occurrence
        """
        return [
            {
                "message": message,
                "count": count,
                "first_occurrence": self.error_timestamps[message]["first"],
                "last_occurrence": self.error_timestamps[message]["last"],
                "details": self.error_timestamps[message].get("details", message),
            }
            for message, count in self.errors.most_common()
        ]

    def get_error_summary(self) -> dict[str, list[dict[str, Any]]]:
        """Get errors grouped by category with counts and examples.

        Returns:
            Dict mapping error categories to lists of error details
        """
        error_categories: dict[str, list[dict[str, Any]]] = {}

        for message, count in self.errors.most_common():
            category = categorize_error(message)
            if category not in error_categories:
                error_categories[category] = []

            error_categories[category].append(
                {
                    "message": message,
                    "count": count,
                    "first_seen": self.error_timestamps[message]["first"],
                    "last_seen": self.error_timestamps[message]["last"],
                    "example": message.split("\n")[0],  # First line of error
                }
            )

        return error_categories

    def generate_categorized_report(self) -> str:
        """Generate error report grouped by categories.

        Returns:
            Formatted report string with categorized errors
        """
        report = [
            "Error Analysis Report by Category",
            "==============================\n",
        ]

        error_summary = self.get_error_summary()
        for category, errors in sorted(error_summary.items()):
            total_count = sum(e["count"] for e in errors)
            report.extend(
                [
                    f"{category}:",
                    f"Total occurrences: {total_count}",
                    "------------------------",
                ]
            )

            for error in sorted(errors, key=lambda x: x["count"], reverse=True):
                report.extend(
                    [
                        f"\nCount: {error['count']}",
                        f"Example: {error['example']}",
                        f"First seen: {error['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}",
                        f"Last seen: {error['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}\n",
                    ]
                )

        return "\n".join(report)

    def generate_report(self) -> str:
        """Generate analysis report.

        Returns:
            Formatted report string
        """
        report = ["Log Analysis Report", "===================\n"]

        # Processing statistics
        total_files = len(self.processing_times)
        avg_time = (
            sum(self.processing_times.values()) / total_files if total_files else 0
        )
        report.extend(
            [
                f"Total files processed: {total_files}",
                f"Average processing time: {avg_time:.2f}s",
                f"Total warnings: {sum(self.warnings.values())}",
                f"Total errors: {sum(self.errors.values())}\n",
            ]
        )

        # Top warnings
        report.extend(["Top 5 Most Common Warnings:", "-------------------------"])
        for msg, count in self.get_most_common_warnings(5):
            report.append(f"[{count}x] {msg}")
        report.append("")

        # Problematic files
        report.extend(["Slow Processing Files (>5s):", "---------------------------"])
        for filename, duration in self.get_slow_files():
            report.append(f"{filename}: {duration:.2f}s")
        report.append("")

        # Detailed error analysis
        report.extend(["\nDetailed Error Analysis:", "----------------------"])
        for error in self.get_error_details():
            details = error["details"].split("\n")
            error_msg = details[0]
            error_trace = (
                "\n".join(details[1:])
                if len(details) > 1
                else "No stack trace available"
            )

            report.extend(
                [
                    f"\nError: {error_msg}",
                    f"Count: {error['count']}",
                    "Stack trace:",
                    error_trace,
                    f"First occurred: {error['first_occurrence'].strftime('%Y-%m-%d %H:%M:%S')}",
                    f"Last occurred: {error['last_occurrence'].strftime('%Y-%m-%d %H:%M:%S')}",
                    "-" * 40,
                ]
            )
        report.append("")

        # Module statistics
        report.extend(["Module Statistics:", "-----------------"])
        for module, stats in self.get_module_statistics().items():
            report.append(f"{module}:")
            for level, count in stats.items():
                report.append(f"  {level}: {count}")

        return "\n".join(report)

    def get_file_errors(self) -> dict[str, list[dict[str, Any]]]:
        """Get errors grouped by filename.

        Returns:
            Dict mapping filenames to lists of error details
        """
        return dict(sorted(self.file_errors.items()))

    def generate_file_error_report(self) -> str:
        """Generate report of errors by file.

        Returns:
            Formatted report string
        """
        report = ["File Error Report", "=================\n"]

        for filename, errors in self.get_file_errors().items():
            report.extend(
                [f"File: {filename}", f"Total errors: {len(errors)}", "Errors:"]
            )
            for error in errors:
                report.extend(
                    [
                        f"  Timestamp: {error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                        f"  Module: {error['module']}",
                        f"  Error: {error['error']}",
                        "",
                    ]
                )
            report.append("-" * 40 + "\n")

        return "\n".join(report)


def analyze_logs(log_file: Path) -> None:
    """Analyze log file and write reports to files.

    Args:
        log_file: Path to log file
    """
    analyzer = LogAnalyzer(log_file)
    analyzer.parse_logs()

    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    # Generate timestamp for unique filenames with timezone
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")

    # Write file error report
    with (reports_dir / f"file_errors_{timestamp}.txt").open("w") as f:
        f.write(analyzer.generate_file_error_report())

    # Write categorized error report
    with (reports_dir / f"error_categories_{timestamp}.txt").open("w") as f:
        f.write(analyzer.generate_categorized_report())

    # Write detailed statistics
    with (reports_dir / f"detailed_statistics_{timestamp}.txt").open("w") as f:
        f.write(analyzer.generate_report())

    print(  # noqa: T201
        f"Reports have been written to the 'reports' directory with timestamp {timestamp}"
    )


if __name__ == "__main__":
    analyze_logs(Path("app.log"))
