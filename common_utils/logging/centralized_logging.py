"""
Advanced centralized logging service for distributed applications.

This module provides a comprehensive centralized logging service that can be used to collect,
process, and store logs from multiple distributed applications in a central location.
It supports various output formats, log rotation, filtering, and integration with
external logging systems like ELK stack.

The service consists of several main components:
1. A server that receives logs from clients and processes them
2. A client that sends logs to the server
3. Multiple output handlers for different storage backends
4. Filtering and processing capabilities
5. Integration with external logging systems

Usage:
    # Server side
    from common_utils.logging.centralized_logging import CentralizedLoggingService

    # Create and start the service with multiple outputs
    service = CentralizedLoggingService(
        host="0.0.0.0",
        port=5000,
        outputs=[
            FileOutput(directory="logs", rotation="daily"),
            ElasticsearchOutput(hosts=["elasticsearch:9200"], index_prefix="logs"),
            LogstashOutput(host="logstash", port=5000),
        ],
        filters=[
            SensitiveDataFilter(),
            LevelFilter(min_level="INFO"),
        ]
    )
    service.start()

    # Client side
    from common_utils.logging.centralized_logging import configure_centralized_logging, get_centralized_logger

    # Configure centralized logging with buffering and retry
    configure_centralized_logging(
        app_name="my_app",
        host="logging_server",
        port=5000,
        buffer_size=100,
        retry_interval=5,
        secure=True
    )

    # Get a logger
    logger = get_centralized_logger(__name__)

    # Log messages with structured data
    logger.info("User logged in", extra={"user_id": "12345", "ip": "192.168.1.1"})
    logger.error("Database connection failed", extra={"db": "users", "error_code": 500})
"""

import datetime
import gzip
import json
import logging
import os
import queue
import shutil
import socket
import ssl
import threading
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from common_utils.logging.secure_logging import (
    SecureLogger,
    get_secure_logger,
    mask_sensitive_data,
)

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging


# Configure logging


# Try to import optional dependencies
try:
    from elasticsearch import Elasticsearch

    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    logger.warning(
        "Elasticsearch library not found. ElasticsearchOutput will not be available.",
        exc_info=True,
    )
    ELASTICSEARCH_AVAILABLE = False

try:
    import logstash

    LOGSTASH_AVAILABLE = True
except ImportError:
    logger.warning(
        "python-logstash library not found. LogstashOutput will not be available.",
        exc_info=True,
    )
    LOGSTASH_AVAILABLE = False


class LogLevel(Enum):
    """Log levels enum for easier filtering."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogFilter(ABC):
    """Base class for log filters."""

    @abstractmethod
    def filter(self, log_entry: Dict[str, Any]) -> bool:
        """
        Filter a log entry.

        Args:
            log_entry: The log entry to filter

        Returns:
            bool: True if the log entry should be kept, False if it should be filtered out

        """


class LevelFilter(LogFilter):
    """Filter logs based on level."""

    def __init__(self, min_level: Union[str, int, LogLevel] = LogLevel.INFO):
        """
        Initialize the level filter.

        Args:
            min_level: Minimum log level to keep

        """
        if isinstance(min_level, str):
            self.min_level = getattr(LogLevel, min_level.upper(), LogLevel.INFO).value
        elif isinstance(min_level, int):
            self.min_level = min_level
        else:
            self.min_level = min_level.value

    def filter(self, log_entry: Dict[str, Any]) -> bool:
        """
        Filter a log entry based on level.

        Args:
            log_entry: The log entry to filter

        Returns:
            bool: True if the log entry should be kept, False if it should be filtered out

        """
        level_name = log_entry.get("level", "INFO").upper()
        level = getattr(LogLevel, level_name, LogLevel.INFO).value
        return level >= self.min_level


class SensitiveDataFilter(LogFilter):
    """Filter sensitive data from logs."""

    def __init__(self, fields: Optional[List[str]] = None):
        """
        Initialize the sensitive data filter.

        Args:
            fields: List of field names to mask

        """
        self.fields = fields or []

    def filter(self, log_entry: Dict[str, Any]) -> bool:
        """
        Mask sensitive data in a log entry.

        Args:
            log_entry: The log entry to filter

        Returns:
            bool: Always True, as this filter only modifies the log entry

        """
        # Mask sensitive data in the message
        if "message" in log_entry:
            log_entry["message"] = mask_sensitive_data(log_entry["message"])

        # Mask sensitive data in extra fields
        for field in self.fields:
            if field in log_entry:
                log_entry[field] = mask_sensitive_data(log_entry[field])

        return True


class LogOutput(ABC):
    """Base class for log outputs."""

    @abstractmethod
    def output(self, log_entry: Dict[str, Any]) -> None:
        """
        Output a log entry.

        Args:
            log_entry: The log entry to output

        """

    @abstractmethod
    def close(self) -> None:
        """Close the output."""


class FileOutput(LogOutput):
    """Output logs to files."""

    def __init__(
        self,
        directory: str = "logs",
        rotation: str = "none",
        max_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        compress: bool = True,
    ) -> None:
        """
        Initialize the file output.

        Args:
            directory: Directory to store log files
            rotation: Rotation strategy ('none', 'size', 'daily', 'hourly')
            max_size: Maximum file size for size-based rotation
            backup_count: Number of backup files to keep
            compress: Whether to compress rotated files

        """
        self.directory = directory
        self.rotation = rotation
        self.max_size = max_size
        self.backup_count = backup_count
        self.compress = compress
        self.files = {}

        # Create the log directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

    def output(self, log_entry: Dict[str, Any]) -> None:
        """
        Output a log entry to a file.

        Args:
            log_entry: The log entry to output

        """
        # Get the app name from the log entry
        app_name = log_entry.get("app", "unknown")

        # Get the current log file path
        log_file = self._get_log_file_path(app_name)

        # Check if rotation is needed
        if self._should_rotate(log_file):
            self._rotate_log_file(app_name, log_file)
            log_file = self._get_log_file_path(app_name)

        # Write the log entry to the file
        try:
            with open(log_file, "a") as f:
                # Format the log entry
                timestamp = log_entry.get(
                    "timestamp", datetime.datetime.now().isoformat()
                )
                level = log_entry.get("level", "INFO")
                logger_name = log_entry.get("logger", "unknown")
                message = log_entry.get("message", "")

                # Ensure app_name is included in the log entry
                log_line = (
                    f"{timestamp} - {app_name} - {logger_name} - {level} - {message}\n"
                )

                # Write the formatted log entry
                f.write(log_line)
        except Exception:
            # Log the error locally
            logger = get_secure_logger("file_output")
            logger.exception(f"Failed to write log entry to {log_file}")

    def close(self) -> None:
        """Close the file output."""

    def _get_log_file_path(self, app_name: str) -> str:
        """
        Get the log file path for an app.

        Args:
            app_name: Name of the application

        Returns:
            str: Path to the log file

        """
        if self.rotation == "daily":
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            return os.path.join(self.directory, f"{app_name}_{date_str}.log")
        if self.rotation == "hourly":
            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H")
            return os.path.join(self.directory, f"{app_name}_{date_str}.log")
        return os.path.join(self.directory, f"{app_name}.log")

    def _should_rotate(self, log_file: str) -> bool:
        """
        Check if a log file should be rotated.

        Args:
            log_file: Path to the log file

        Returns:
            bool: True if the log file should be rotated, False otherwise

        """
        if not os.path.exists(log_file):
            return False

        if self.rotation == "size":
            return os.path.getsize(log_file) >= self.max_size

        return False

    def _rotate_log_file(self, app_name: str, log_file: str) -> None:
        """
        Rotate a log file.

        Args:
            app_name: Name of the application
            log_file: Path to the log file

        """
        if not os.path.exists(log_file):
            return

        # Rotate the log files
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{log_file}.{i}"
            dst = f"{log_file}.{i + 1}"

            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.move(src, dst)

        # Move the current log file
        if os.path.exists(log_file):
            shutil.move(log_file, f"{log_file}.1")

        # Compress the rotated log file if needed
        if self.compress and os.path.exists(f"{log_file}.1"):
            with open(f"{log_file}.1", "rb") as f_in:
                with gzip.open(f"{log_file}.1.gz", "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(f"{log_file}.1")


class ElasticsearchOutput(LogOutput):
    """Output logs to Elasticsearch."""

    def __init__(
        self,
        hosts: List[str] = ["localhost:9200"],
        index_prefix: str = "logs",
        batch_size: int = 100,
        flush_interval: int = 5,
    ) -> None:
        """
        Initialize the Elasticsearch output.

        Args:
            hosts: List of Elasticsearch hosts
            index_prefix: Prefix for Elasticsearch indices
            batch_size: Number of logs to batch before sending
            flush_interval: Interval in seconds to flush the batch

        """
        if not ELASTICSEARCH_AVAILABLE:
            raise ImportError("Elasticsearch package is not installed")

        self.hosts = hosts
        self.index_prefix = index_prefix
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()

        # Create Elasticsearch client
        self.es = Elasticsearch(hosts)

        # Start the flush thread
        self.running = True
        self.thread = threading.Thread(target=self._flush_thread)
        self.thread.daemon = True
        self.thread.start()

    def output(self, log_entry: Dict[str, Any]) -> None:
        """
        Output a log entry to Elasticsearch.

        Args:
            log_entry: The log entry to output

        """
        # Add the log entry to the batch
        self.batch.append(log_entry)

        # Flush the batch if it's full
        if len(self.batch) >= self.batch_size:
            self._flush()

    def close(self) -> None:
        """Close the Elasticsearch output."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=self.flush_interval + 1)
        self._flush()

    def _flush(self) -> None:
        """Flush the batch to Elasticsearch."""
        if not self.batch:
            return

        try:
            # Create the index name with date suffix
            date_str = datetime.datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{date_str}"

            # Prepare the bulk request
            bulk_data = []
            for log_entry in self.batch:
                # Add the index action
                bulk_data.append({"index": {"_index": index_name}})

                # Add the log entry
                bulk_data.append(log_entry)

            # Send the bulk request
            if bulk_data:
                self.es.bulk(body=bulk_data)

            # Clear the batch
            self.batch = []
            self.last_flush = time.time()
        except Exception:
            # Log the error locally
            logger = get_secure_logger("elasticsearch_output")
            logger.exception("Failed to flush logs to Elasticsearch")

    def _flush_thread(self) -> None:
        """Flush thread that periodically flushes the batch."""
        while self.running:
            # Sleep for a bit
            time.sleep(0.1)

            # Check if it's time to flush
            if time.time() - self.last_flush >= self.flush_interval:
                self._flush()


class LogstashOutput(LogOutput):
    """Output logs to Logstash."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        protocol: str = "udp",
    ) -> None:
        """
        Initialize the Logstash output.

        Args:
            host: Logstash host
            port: Logstash port
            protocol: Protocol to use ('udp' or 'tcp')

        """
        if not LOGSTASH_AVAILABLE:
            raise ImportError("Logstash package is not installed")

        self.host = host
        self.port = port
        self.protocol = protocol

        # Create the Logstash handler
        if protocol == "udp":
            self.handler = logstash.UDPLogstashHandler(host, port)
        else:
            self.handler = logstash.TCPLogstashHandler(host, port)

    def output(self, log_entry: Dict[str, Any]) -> None:
        """
        Output a log entry to Logstash.

        Args:
            log_entry: The log entry to output

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

            # Add extra fields
            for key, value in log_entry.items():
                if key not in ("logger", "level", "pathname", "lineno", "message"):
                    setattr(record, key, value)

            # Emit the record
            self.handler.emit(record)
        except Exception:
            # Log the error locally
            logger = get_secure_logger("logstash_output")
            logger.exception("Failed to send log entry to Logstash")

    def close(self) -> None:
        """Close the Logstash output."""
        self.handler.close()


class CentralizedLoggingService:
    """Advanced centralized logging service for collecting logs from distributed applications."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        buffer_size: int = 8192,
        outputs: Optional[List[LogOutput]] = None,
        filters: Optional[List[LogFilter]] = None,
        use_ssl: bool = False,
        ssl_cert: Optional[str] = None,
        ssl_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the centralized logging service.

        Args:
            host: Host to bind the service to
            port: Port to bind the service to
            buffer_size: Size of the receive buffer
            outputs: List of outputs to send logs to
            filters: List of filters to apply to logs
            use_ssl: Whether to use SSL for secure communication
            ssl_cert: Path to SSL certificate file
            ssl_key: Path to SSL key file

        Raises:
            ValueError: If use_ssl is True but ssl_cert or ssl_key is missing.

        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.outputs = outputs or [FileOutput()]
        self.filters = filters or []
        self.use_ssl = use_ssl
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.running = False
        self.socket = None
        self.thread = None
        self.stats = {
            "received": 0,
            "filtered": 0,
            "errors": 0,
            "start_time": None,
        }

        # Set up logging for the service itself
        self.logger = get_secure_logger("centralized_logging_service")

        if use_ssl and (not ssl_cert or not ssl_key):
            raise ValueError("SSL is enabled but ssl_cert or ssl_key is missing.")

    def start(self) -> None:
        """Start the centralized logging service."""
        if self.running:
            self.logger.warning("Service is already running")
            return

        try:
            # Create a socket
            if self.use_ssl:
                # Create a TCP socket for SSL
                base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Create SSL context
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)

                # Wrap the socket with SSL
                self.socket = context.wrap_socket(base_socket, server_side=True)
            else:
                # Create a UDP socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind the socket
            self.socket.bind((self.host, self.port))

            # For TCP, start listening
            if self.use_ssl:
                self.socket.listen(5)

            # Mark the service as running
            self.running = True
            self.stats["start_time"] = datetime.datetime.now()

            # Start the processing thread
            self.thread = threading.Thread(target=self._process_logs)
            self.thread.daemon = True
            self.thread.start()

            self.logger.info(
                f"Centralized logging service started on {self.host}:{self.port} (SSL: {self.use_ssl})"
            )
        except Exception:
            self.logger.exception("Failed to start centralized logging service")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.running = False
            raise

    def stop(self) -> None:
        """Stop the centralized logging service."""
        if not self.running:
            self.logger.warning("Service is not running")
            return

        # Mark the service as not running
        self.running = False

        # Close the socket
        if self.socket:
            self.socket.close()
            self.socket = None

        # Wait for the processing thread to finish
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None

        # Close all outputs
        for output in self.outputs:
            try:
                output.close()
            except Exception:
                self.logger.exception(
                    f"Error closing output {output.__class__.__name__}"
                )

        # Log statistics
        uptime = (
            datetime.datetime.now() - self.stats["start_time"]
            if self.stats["start_time"]
            else datetime.timedelta(0)
        )
        self.logger.info(
            f"Centralized logging service stopped. "
            f"Stats: received={self.stats['received']}, "
            f"filtered={self.stats['filtered']}, "
            f"errors={self.stats['errors']}, "
            f"uptime={uptime}"
        )

    def receive_log(self) -> Dict[str, Any]:
        """
        Receive a log entry from a client.

        Returns:
            Dict[str, Any]: The received log entry

        """
        if not self.running or not self.socket:
            raise RuntimeError("Service is not running")

        try:
            if self.use_ssl:
                # For SSL/TCP, accept a connection
                client_socket, addr = self.socket.accept()

                try:
                    # Receive data
                    data = b""
                    while True:
                        chunk = client_socket.recv(self.buffer_size)
                        if not chunk:
                            break
                        data += chunk

                        # Check if we have a complete JSON object
                        try:
                            json.loads(data.decode("utf-8"))
                            break
                        except json.JSONDecodeError:
                            # Not a complete JSON object yet, continue receiving
                            pass
                finally:
                    # Close the client socket
                    client_socket.close()
            else:
                # For UDP, receive a datagram
                data, addr = self.socket.recvfrom(self.buffer_size)

            # Update statistics
            self.stats["received"] += 1

            # Parse the JSON data
            try:
                log_entry = json.loads(data.decode("utf-8"))
                self.logger.debug(f"Received log entry from {addr}")

                # Ensure the app field is present
                if "app" not in log_entry:
                    log_entry["app"] = "unknown"

                # Ensure timestamp is present
                if "timestamp" not in log_entry:
                    log_entry["timestamp"] = datetime.datetime.now().isoformat()

                return log_entry
            except json.JSONDecodeError as e:
                self.logger.exception(f"Failed to parse log entry from {addr}")
                self.stats["errors"] += 1
                return {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Failed to parse log entry: {e}",
                    "logger": "centralized_logging_service",
                    "app": "centralized_logging_service",
                }
        except Exception:
            self.logger.exception("Error receiving log entry")
            self.stats["errors"] += 1
            raise

    def process_log(self, log_entry: Dict[str, Any]) -> None:
        """
        Process a log entry.

        Args:
            log_entry: The log entry to process

        """
        try:
            # Apply filters
            for log_filter in self.filters:
                if not log_filter.filter(log_entry):
                    self.stats["filtered"] += 1
                    return

            # Send to all outputs
            for output in self.outputs:
                try:
                    output.output(log_entry)
                except Exception:
                    self.logger.exception(
                        f"Error sending log entry to {output.__class__.__name__}"
                    )
                    self.stats["errors"] += 1
        except Exception:
            self.logger.exception("Error processing log entry")
            self.stats["errors"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the logging service.

        Returns:
            Dict[str, Any]: Statistics about the logging service

        """
        stats = self.stats.copy()

        # Calculate uptime
        if stats["start_time"]:
            stats["uptime"] = str(datetime.datetime.now() - stats["start_time"])
        else:
            stats["uptime"] = "0:00:00"

        # Add status
        stats["status"] = "running" if self.running else "stopped"

        return stats

    def _process_logs(self) -> None:
        """Process logs in a loop."""
        while self.running:
            try:
                # Receive a log entry
                log_entry = self.receive_log()

                # Process the log entry
                self.process_log(log_entry)
            except Exception:
                if self.running:
                    self.logger.exception("Error processing log")
                    self.stats["errors"] += 1
                    # Sleep briefly to avoid tight loop in case of persistent errors
                    time.sleep(0.1)


class LoggingClient:
    """Client for sending logs to the centralized logging service."""

    def __init__(
        self,
        app_name: str,
        host: str = "localhost",
        port: int = 5000,
        buffer_size: int = 100,
        retry_interval: int = 5,
        secure: bool = False,
    ) -> None:
        """
        Initialize the logging client.

        Args:
            app_name: Name of the application
            host: Host of the centralized logging service
            port: Port of the centralized logging service
            buffer_size: Size of the log buffer (0 to disable buffering)
            retry_interval: Interval in seconds to retry sending logs
            secure: Whether to use SSL for secure communication

        """
        self.app_name = app_name
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.retry_interval = retry_interval
        self.secure = secure
        self.buffer = queue.Queue(maxsize=max(0, buffer_size))
        self.running = True
        self.stats = {
            "sent": 0,
            "failed": 0,
            "retried": 0,
            "dropped": 0,
        }

        # Set up logging for the client itself
        self.logger = get_secure_logger("centralized_logging_client")

        # Start the buffer processing thread if buffering is enabled
        if buffer_size > 0:
            self.thread = threading.Thread(target=self._process_buffer)
            self.thread.daemon = True
            self.thread.start()
        else:
            self.thread = None

    def send_log(self, log_entry: Dict[str, Any]) -> None:
        """
        Send a log entry to the centralized logging service.

        Args:
            log_entry: The log entry to send

        """
        # Add the app name to the log entry if not already present
        if "app" not in log_entry:
            log_entry["app"] = self.app_name

        # Add timestamp if not present
        if "timestamp" not in log_entry:
            log_entry["timestamp"] = datetime.datetime.now().isoformat()

        # If buffering is enabled, add to buffer
        if self.buffer_size > 0:
            try:
                self.buffer.put_nowait(log_entry)
            except queue.Full:
                # Buffer is full, drop the log entry
                self.stats["dropped"] += 1
                self.logger.warning("Log buffer is full, dropping log entry")
        else:
            # Send immediately
            self._send_log_entry(log_entry)

    def _send_log_entry(self, log_entry: Dict[str, Any]) -> bool:
        """
        Send a log entry to the centralized logging service.

        Args:
            log_entry: The log entry to send

        Returns:
            bool: True if the log entry was sent successfully, False otherwise

        """
        try:
            # Convert the log entry to JSON
            data = json.dumps(log_entry).encode("utf-8")

            if self.secure:
                # Create a TCP socket for SSL
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Create SSL context
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                # Wrap the socket with SSL
                ssl_sock = context.wrap_socket(sock)

                # Connect to the server
                ssl_sock.connect((self.host, self.port))

                # Send the data
                ssl_sock.sendall(data)

                # Close the socket
                ssl_sock.close()
            else:
                # Create a UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                # Send the data
                sock.sendto(data, (self.host, self.port))

                # Close the socket
                sock.close()

            # Update statistics
            self.stats["sent"] += 1
            return True
        except Exception:
            # Log the error locally
            self.logger.exception("Failed to send log entry")

            # Update statistics
            self.stats["failed"] += 1
            return False

    def _process_buffer(self) -> None:
        """Process the log buffer in a loop."""
        while self.running:
            try:
                # Get a log entry from the buffer
                try:
                    log_entry = self.buffer.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Try to send the log entry
                if not self._send_log_entry(log_entry):
                    # Failed to send, retry later
                    self.stats["retried"] += 1

                    # Sleep for the retry interval
                    time.sleep(self.retry_interval)

                    # Try again
                    if not self._send_log_entry(log_entry):
                        # Failed again, drop the log entry
                        self.stats["dropped"] += 1
                        self.logger.warning(
                            "Failed to send log entry after retry, dropping"
                        )

                # Mark the task as done
                self.buffer.task_done()
            except Exception:
                self.logger.exception("Error processing log buffer")
                time.sleep(0.1)

    def stop(self) -> None:
        """Stop the logging client."""
        self.running = False

        # Wait for the buffer to be processed
        if self.thread:
            self.thread.join(timeout=5.0)

        # Log statistics
        self.logger.info(
            f"Logging client stopped. "
            f"Stats: sent={self.stats['sent']}, "
            f"failed={self.stats['failed']}, "
            f"retried={self.stats['retried']}, "
            f"dropped={self.stats['dropped']}"
        )


class RemoteHandler(logging.Handler):
    """Logging handler that sends logs to the centralized logging service."""

    def __init__(
        self,
        client: LoggingClient,
        level: int = logging.NOTSET,
    ) -> None:
        """
        Initialize the remote handler.

        Args:
            client: The logging client to use
            level: The logging level

        """
        super().__init__(level)
        self.client = client

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Args:
            record: The log record to emit

        """
        try:
            # Format the log record
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "level": record.levelname,
                "message": self.format(record),
                "logger": record.name,
                "pathname": record.pathname,
                "lineno": record.lineno,
                "funcName": record.funcName,
            }

            # Send the log entry
            self.client.send_log(log_entry)
        except Exception:
            self.handleError(record)


# Global client instance
_client: Optional[LoggingClient] = None


def configure_centralized_logging(
    app_name: str,
    host: str = "localhost",
    port: int = 5000,
    level: int = logging.INFO,
    buffer_size: int = 100,
    retry_interval: int = 5,
    secure: bool = False,
    formatter: Optional[logging.Formatter] = None,
) -> None:
    """
    Configure centralized logging.

    Args:
        app_name: Name of the application
        host: Host of the centralized logging service
        port: Port of the centralized logging service
        level: The logging level
        buffer_size: Size of the log buffer (0 to disable buffering)
        retry_interval: Interval in seconds to retry sending logs
        secure: Whether to use SSL for secure communication
        formatter: Custom formatter for log messages

    Raises:
        TypeError: If formatter is not a logging.Formatter instance or None.

    """
    global _client

    # Create a client
    _client = LoggingClient(
        app_name=app_name,
        host=host,
        port=port,
        buffer_size=buffer_size,
        retry_interval=retry_interval,
        secure=secure,
    )

    # Create a handler
    handler = RemoteHandler(client=_client, level=level)

    # Set formatter if provided
    if formatter is not None and not isinstance(formatter, logging.Formatter):
        raise TypeError("formatter must be a logging.Formatter instance or None")
    if formatter:
        handler.setFormatter(formatter)
    else:
        # Use a default formatter that includes more information
        default_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(default_formatter)

    # Add the handler to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    # Set the logging level
    root_logger.setLevel(level)

    # Log a message to confirm configuration
    root_logger.info(
        f"Centralized logging configured for {app_name} "
        f"(host={host}, port={port}, secure={secure})"
    )


def get_centralized_logger(name: str) -> Union[logging.Logger, SecureLogger]:
    """
    Get a logger that sends logs to the centralized logging service.

    Args:
        name: Name of the logger

    Returns:
        Union[logging.Logger, SecureLogger]: The logger

    """
    # Check if centralized logging is configured
    if _client is None:
        # Fall back to secure logger
        return get_secure_logger(name)

    # Get a logger
    target_logger = logging.getLogger(name)

    # Add a method to log with extra fields
    def log_with_extra(
        self,
        level: int,
        msg: str,
        *args: Any,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log a message with extra fields.

        Args:
            level: Log level
            msg: Log message
            args: Arguments for message formatting
            extra: Extra fields to include in the log entry
            kwargs: Additional keyword arguments

        """
        if extra is None:
            extra = {}
        self.log(level, msg, *args, extra=extra, **kwargs)

    # Add the method to the logger
    target_logger.log_with_extra = lambda level, msg, *args, **kwargs: log_with_extra(
        target_logger, level, msg, *args, **kwargs
    )

    # Add convenience methods
    target_logger.debug_with_extra = lambda msg, *args, **kwargs: log_with_extra(
        target_logger, logging.DEBUG, msg, *args, **kwargs
    )
    target_logger.info_with_extra = lambda msg, *args, **kwargs: log_with_extra(
        target_logger, logging.INFO, msg, *args, **kwargs
    )
    target_logger.warning_with_extra = lambda msg, *args, **kwargs: log_with_extra(
        target_logger, logging.WARNING, msg, *args, **kwargs
    )
    target_logger.error_with_extra = lambda msg, *args, **kwargs: log_with_extra(
        target_logger, logging.ERROR, msg, *args, **kwargs
    )
    target_logger.critical_with_extra = lambda msg, *args, **kwargs: log_with_extra(
        target_logger, logging.CRITICAL, msg, *args, **kwargs
    )

    return target_logger


def stop_centralized_logging() -> None:
    """Stop centralized logging."""
    global _client

    if _client is not None:
        # Stop the client
        _client.stop()

        # Remove the handler from the root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RemoteHandler):
                root_logger.removeHandler(handler)

        # Clear the client
        _client = None
