import logging

logger = logging.getLogger(__name__)

"""Log aggregation module for collecting and processing logs from multiple sources.

This module provides functionality for aggregating logs from multiple sources,
such as files, databases, and remote services, and sending them to various
destinations, such as Elasticsearch, Logstash, or files.

Usage:
    from common_utils.logging.log_aggregation import (
        LogAggregator,
        ElasticsearchHandler,
        LogstashHandler,
        FileRotatingHandler,
        aggregate_logs,
        configure_log_aggregation,
    )

    # Create a log aggregator
    aggregator = LogAggregator(app_name="my_app")

    # Add handlers
    aggregator.add_handler(ElasticsearchHandler(es_client=es_client, index_name="logs"))
    aggregator.add_handler(LogstashHandler(host="logstash", port=5000))
    aggregator.add_handler(FileRotatingHandler(filename="aggregated.log"))

    # Aggregate logs from a file
    aggregator.aggregate_log_file("app.log")

    # Aggregate logs from a directory
    aggregator.aggregate_log_directory("logs")

    # Or use the convenience function
    aggregate_logs(
        app_name="my_app",
        log_dir="logs",
        es_host="elasticsearch",
        es_port=9200,
        logstash_host="logstash",
        logstash_port=5000,
    )
"""

import datetime
import glob
import json
import logging
import os
import re
import socket
import threading
import time
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional

# Import the secure logging utilities

# Use the existing logger from line 3

# Log entry pattern (same as in log_dashboard.py)
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?) - "
    r"(?P<name>[^-]+) - "
    r"(?P<level>[A-Z]+) - "
    r"(?P<message>.*)"
)


def parse_log_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a log file into a list of log entries.

    Args:
        file_path: Path to the log file

    Returns:
        List of dictionaries containing log entries

    """
    log_entries = []

    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                match = LOG_PATTERN.match(line.strip())
                if match:
                    entry = match.groupdict()
                    entry["timestamp"] = datetime.datetime.strptime(
                        entry["timestamp"].split(".")[0],
                        "%Y-%m-%d %H:%M:%S"
                    ).isoformat()
                    log_entries.append(entry)
                # Handle multi-line entries (e.g., tracebacks)
                elif log_entries:
                    log_entries[-1]["message"] += "\n" + line.strip()
    except Exception as e:
        logger.error(f"Error parsing log file {file_path}: {e}")

    return log_entries


def get_log_files(log_dir: str) -> List[str]:
    """
    Get all log files in a directory.

    Args:
        log_dir: Directory containing log files

    Returns:
        List of paths to log files

    """
    import glob
    return glob.glob(os.path.join(log_dir, "*.log"))


def get_log_statistics(log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics for a list of log entries.

    Args:
        log_entries: List of log entries

    Returns:
        Dictionary containing statistics

    """
    if not log_entries:
        return {
            "total": 0,
            "by_level": {},
            "by_module": {},
            "by_hour": {},
            "by_date": {},
        }

    # Count by level
    from collections import Counter
    level_counts = Counter(entry["level"] for entry in log_entries)

    # Count by module
    module_counts = Counter(entry["name"] for entry in log_entries)

    # Count by hour
    hour_counts = {}
    for entry in log_entries:
        if isinstance(entry["timestamp"], str):
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        else:
            timestamp = entry["timestamp"]
        hour = timestamp.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1

    # Count by date
    date_counts = {}
    for entry in log_entries:
        if isinstance(entry["timestamp"], str):
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        else:
            timestamp = entry["timestamp"]
        date = timestamp.date()
        date_str = date.isoformat()
        date_counts[date_str] = date_counts.get(date_str, 0) + 1

    return {
        "total": len(log_entries),
        "by_level": dict(level_counts),
        "by_module": dict(module_counts),
        "by_hour": hour_counts,
        "by_date": date_counts,
    }


class LogAggregator:
    """Aggregator for collecting logs from multiple sources."""

    def __init__(
        self,
        app_name: str,
        log_dir: str = "logs",
    ) -> None:
        """
        Initialize the log aggregator.

        Args:
            app_name: Name of the application
            log_dir: Directory containing log files

        """
        self.app_name = app_name
        self.log_dir = log_dir
        self.handlers: List[Any] = []

        # Create the log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

    def add_handler(self, handler: Any) -> None:
        """
        Add a handler for processing log entries.

        Args:
            handler: Handler for processing log entries

        """
        self.handlers.append(handler)

    def remove_handler(self, handler: Any) -> None:
        """
        Remove a handler.

        Args:
            handler: Handler to remove

        """
        if handler in self.handlers:
            self.handlers.remove(handler)

    def aggregate_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """
        Aggregate a single log entry.

        Args:
            log_entry: Log entry to aggregate

        """
        # Add the app name to the log entry if not already present
        if "app" not in log_entry:
            log_entry["app"] = self.app_name

        # Process the log entry with each handler
        for handler in self.handlers:
            try:
                handler.handle(log_entry)
            except Exception as e:
                logger.error(f"Error handling log entry with {handler.__class__.__name__}: {e}")

    def aggregate_log_file(self, file_path: str) -> None:
        """
        Aggregate logs from a file.

        Args:
            file_path: Path to the log file

        """
        # Parse the log file
        log_entries = parse_log_file(file_path)

        # Aggregate each log entry
        for log_entry in log_entries:
            self.aggregate_log_entry(log_entry)

        logger.info(f"Aggregated {len(log_entries)} log entries from {file_path}")

    def aggregate_log_directory(self, directory: str) -> None:
        """
        Aggregate logs from all files in a directory.

        Args:
            directory: Directory containing log files

        """
        # Get all log files in the directory
        log_files = glob.glob(os.path.join(directory, "*.log"))

        # Aggregate each log file
        for log_file in log_files:
            self.aggregate_log_file(log_file)

        logger.info(f"Aggregated logs from {len(log_files)} files in {directory}")


class ElasticsearchHandler:
    """Handler for sending log entries to Elasticsearch."""

    def __init__(
        self,
        es_client: Any,
        index_name: str = "logs",
    ) -> None:
        """
        Initialize the Elasticsearch handler.

        Args:
            es_client: Elasticsearch client
            index_name: Name of the Elasticsearch index

        """
        self.es_client = es_client
        self.index_name = index_name

    def handle(self, log_entry: Dict[str, Any]) -> None:
        """
        Handle a log entry by sending it to Elasticsearch.

        Args:
            log_entry: Log entry to handle

        """
        try:
            # Index the log entry in Elasticsearch
            self.es_client.index(
                index=self.index_name,
                document=log_entry,
            )
        except Exception as e:
            logger.error(f"Error indexing log entry in Elasticsearch: {e}")


class LogstashHandler:
    """Handler for sending log entries to Logstash."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        socket: Optional[socket.socket] = None,
    ) -> None:
        """
        Initialize the Logstash handler.

        Args:
            host: Logstash host
            port: Logstash port
            socket: Optional socket to use (for testing)

        """
        self.host = host
        self.port = port
        self.socket = socket

    def handle(self, log_entry: Dict[str, Any]) -> None:
        """
        Handle a log entry by sending it to Logstash.

        Args:
            log_entry: Log entry to handle

        """
        try:
            # Convert the log entry to JSON
            data = json.dumps(log_entry).encode("utf-8")

            # Create a socket if one wasn't provided
            if self.socket is None:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                sock = self.socket

            # Send the data
            sock.sendto(data, (self.host, self.port))

            # Close the socket if we created it
            if self.socket is None:
                sock.close()
        except Exception as e:
            logger.error(f"Error sending log entry to Logstash: {e}")


class FileRotatingHandler:
    """Handler for writing log entries to a rotating file."""

    def __init__(
        self,
        filename: str = "aggregated.log",
        max_bytes: int = 10485760,  # 10 MB
        backup_count: int = 5,
    ) -> None:
        """
        Initialize the file rotating handler.

        Args:
            filename: Name of the log file
            max_bytes: Maximum size of the log file before rotation
            backup_count: Number of backup files to keep

        """
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Create a rotating file handler
        self.handler = RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )

        # Set the formatter
        self.handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    def close(self) -> None:
        """Close the file handler."""
        if hasattr(self, "handler") and self.handler:
            self.handler.close()

    def handle(self, log_entry: Dict[str, Any]) -> None:
        """
        Handle a log entry by writing it to the log file.

        Args:
            log_entry: Log entry to handle

        """
        try:
            # Create a log record
            record = logging.LogRecord(
                name=log_entry.get("logger", "unknown"),
                level=getattr(logging, log_entry.get("level", "INFO"), logging.INFO),
                pathname=log_entry.get("pathname", ""),
                lineno=log_entry.get("lineno", 0),
                msg=log_entry.get("message", ""),
                args=(),
                exc_info=None,
            )

            # Emit the record
            self.handler.emit(record)
        except Exception as e:
            logger.error(f"Error writing log entry to file: {e}")


def aggregate_logs(
    app_name: str,
    log_dir: str = "logs",
    es_host: Optional[str] = None,
    es_port: int = 9200,
    es_index: str = "logs",
    logstash_host: Optional[str] = None,
    logstash_port: int = 5000,
    output_file: Optional[str] = None,
) -> None:
    """
    Aggregate logs from multiple sources.

    Args:
        app_name: Name of the application
        log_dir: Directory containing log files
        es_host: Elasticsearch host (if None, Elasticsearch is not used)
        es_port: Elasticsearch port
        es_index: Elasticsearch index name
        logstash_host: Logstash host (if None, Logstash is not used)
        logstash_port: Logstash port
        output_file: Output file for aggregated logs (if None, no file output)

    """
    # Create a log aggregator
    aggregator = LogAggregator(app_name=app_name, log_dir=log_dir)

    # Add Elasticsearch handler if host is provided
    if es_host:
        try:
            # Import elasticsearch module
            from elasticsearch import Elasticsearch

            # Create Elasticsearch client
            es_client = Elasticsearch([f"http://{es_host}:{es_port}"])

            # Add Elasticsearch handler
            aggregator.add_handler(
                ElasticsearchHandler(es_client=es_client, index_name=es_index)
            )

            logger.info(f"Added Elasticsearch handler for {es_host}:{es_port}")
        except ImportError:
            logger.error("Elasticsearch module not found. Install with: pip install elasticsearch")
        except Exception as e:
            logger.error(f"Error creating Elasticsearch client: {e}")

    # Add Logstash handler if host is provided
    if logstash_host:
        aggregator.add_handler(
            LogstashHandler(host=logstash_host, port=logstash_port)
        )
        logger.info(f"Added Logstash handler for {logstash_host}:{logstash_port}")

    # Add file handler if output file is provided
    if output_file:
        aggregator.add_handler(
            FileRotatingHandler(filename=output_file)
        )
        logger.info(f"Added file handler for {output_file}")

    # Aggregate logs from the log directory
    aggregator.aggregate_log_directory(log_dir)


def configure_log_aggregation(
    app_name: str,
    log_dir: str = "logs",
    es_host: Optional[str] = None,
    es_port: int = 9200,
    es_index: str = "logs",
    logstash_host: Optional[str] = None,
    logstash_port: int = 5000,
    output_file: Optional[str] = None,
    test_mode: bool = False,
) -> threading.Thread:
    """
    Configure log aggregation for the application.

    This function sets up log aggregation and schedules it to run periodically.

    Args:
        app_name: Name of the application
        log_dir: Directory containing log files
        es_host: Elasticsearch host (if None, Elasticsearch is not used)
        es_port: Elasticsearch port
        es_index: Elasticsearch index name
        logstash_host: Logstash host (if None, Logstash is not used)
        logstash_port: Logstash port
        output_file: Output file for aggregated logs (if None, no file output)
        test_mode: If True, the thread will run only once (for testing)

    Returns:
        The created thread object

    """

    # Define the aggregation function
    def _aggregate():
        # In test mode, run only once
        if test_mode:
            try:
                # Aggregate logs
                aggregate_logs(
                    app_name=app_name,
                    log_dir=log_dir,
                    es_host=es_host,
                    es_port=es_port,
                    es_index=es_index,
                    logstash_host=logstash_host,
                    logstash_port=logstash_port,
                    output_file=output_file,
                )
            except Exception as e:
                logger.error(f"Error aggregating logs: {e}")
            return

        # In normal mode, run continuously
        while True:
            try:
                # Aggregate logs
                aggregate_logs(
                    app_name=app_name,
                    log_dir=log_dir,
                    es_host=es_host,
                    es_port=es_port,
                    es_index=es_index,
                    logstash_host=logstash_host,
                    logstash_port=logstash_port,
                    output_file=output_file,
                )
            except Exception as e:
                logger.error(f"Error aggregating logs: {e}")

            # Sleep for 5 minutes
            time.sleep(300)

    # Start the aggregation thread
    thread = threading.Thread(target=_aggregate, daemon=True)
    thread.start()

    logger.info("Log aggregation configured and started")

    return thread
