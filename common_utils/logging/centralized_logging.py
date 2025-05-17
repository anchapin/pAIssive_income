"""Centralized logging service for distributed applications.

This module provides a centralized logging service that can be used to collect logs
from multiple distributed applications and store them in a central location.

The service consists of two main components:
1. A server that receives logs from clients and stores them in files
2. A client that sends logs to the server

Usage:
    # Server side
    from common_utils.logging.centralized_logging import CentralizedLoggingService

    # Create and start the service
    service = CentralizedLoggingService(host="0.0.0.0", port=5000)
    service.start()

    # Client side
    from common_utils.logging.centralized_logging import configure_centralized_logging, get_centralized_logger

    # Configure centralized logging
    configure_centralized_logging(app_name="my_app", host="logging_server", port=5000)

    # Get a logger
    logger = get_centralized_logger(__name__)

    # Log messages
    logger.info("This is an info message")
    logger.error("This is an error message")
"""

import datetime
import json
import logging
import os
import socket
import threading
import time
from typing import Any, Dict, Optional, Union

from common_utils.logging.secure_logging import SecureLogger, get_secure_logger


class CentralizedLoggingService:
    """Centralized logging service for collecting logs from distributed applications."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        log_dir: str = "logs",
        buffer_size: int = 8192,
    ) -> None:
        """Initialize the centralized logging service.

        Args:
            host: Host to bind the service to
            port: Port to bind the service to
            log_dir: Directory to store log files
            buffer_size: Size of the receive buffer
        """
        self.host = host
        self.port = port
        self.log_dir = log_dir
        self.buffer_size = buffer_size
        self.running = False
        self.socket = None
        self.thread = None

        # Create the log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Set up logging for the service itself
        self.logger = get_secure_logger("centralized_logging_service")

    def start(self) -> None:
        """Start the centralized logging service."""
        if self.running:
            self.logger.warning("Service is already running")
            return

        try:
            # Create a UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))

            # Mark the service as running
            self.running = True

            # Start the processing thread
            self.thread = threading.Thread(target=self._process_logs)
            self.thread.daemon = True
            self.thread.start()

            self.logger.info(f"Centralized logging service started on {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to start centralized logging service: {e}")
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

        self.logger.info("Centralized logging service stopped")

    def receive_log(self) -> Dict[str, Any]:
        """Receive a log entry from a client.

        Returns:
            Dict[str, Any]: The received log entry
        """
        if not self.running or not self.socket:
            raise RuntimeError("Service is not running")

        # Receive data from the socket
        data, addr = self.socket.recvfrom(self.buffer_size)

        # Parse the JSON data
        try:
            log_entry = json.loads(data.decode("utf-8"))
            self.logger.debug(f"Received log entry from {addr}")

            # Ensure the app field is present
            if "app" not in log_entry:
                log_entry["app"] = "unknown"

            return log_entry
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse log entry from {addr}: {e}")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "level": "ERROR",
                "message": f"Failed to parse log entry: {e}",
                "logger": "centralized_logging_service",
                "app": "centralized_logging_service",
            }

    def process_log(self, log_entry: Dict[str, Any]) -> None:
        """Process a log entry.

        Args:
            log_entry: The log entry to process
        """
        # Get the app name from the log entry
        app_name = log_entry.get("app", "unknown")

        # Create a log file for the app
        log_file = os.path.join(self.log_dir, f"{app_name}.log")

        # Write the log entry to the file
        try:
            with open(log_file, "a") as f:
                # Format the log entry
                timestamp = log_entry.get("timestamp", datetime.datetime.now().isoformat())
                level = log_entry.get("level", "INFO")
                logger_name = log_entry.get("logger", "unknown")
                message = log_entry.get("message", "")

                # Ensure app_name is included in the log entry
                log_line = f"{timestamp} - {app_name} - {logger_name} - {level} - {message}\n"

                # Write the formatted log entry
                f.write(log_line)
        except Exception as e:
            self.logger.error(f"Failed to write log entry to {log_file}: {e}")

    def _process_logs(self) -> None:
        """Process logs in a loop."""
        while self.running:
            try:
                # Receive a log entry
                log_entry = self.receive_log()

                # Process the log entry
                self.process_log(log_entry)
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error processing log: {e}")
                    # Sleep briefly to avoid tight loop in case of persistent errors
                    time.sleep(0.1)


class LoggingClient:
    """Client for sending logs to the centralized logging service."""

    def __init__(
        self,
        app_name: str,
        host: str = "localhost",
        port: int = 5000,
    ) -> None:
        """Initialize the logging client.

        Args:
            app_name: Name of the application
            host: Host of the centralized logging service
            port: Port of the centralized logging service
        """
        self.app_name = app_name
        self.host = host
        self.port = port

        # Set up logging for the client itself
        self.logger = get_secure_logger("centralized_logging_client")

    def send_log(self, log_entry: Dict[str, Any]) -> None:
        """Send a log entry to the centralized logging service.

        Args:
            log_entry: The log entry to send
        """
        try:
            # Add the app name to the log entry if not already present
            if "app" not in log_entry:
                log_entry["app"] = self.app_name

            # Convert the log entry to JSON
            data = json.dumps(log_entry).encode("utf-8")

            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Send the data
            sock.sendto(data, (self.host, self.port))

            # Close the socket
            sock.close()
        except Exception as e:
            # Log the error locally
            self.logger.error(f"Failed to send log entry: {e}")


class RemoteHandler(logging.Handler):
    """Logging handler that sends logs to the centralized logging service."""

    def __init__(
        self,
        client: LoggingClient,
        level: int = logging.NOTSET,
    ) -> None:
        """Initialize the remote handler.

        Args:
            client: The logging client to use
            level: The logging level
        """
        super().__init__(level)
        self.client = client

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

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
) -> None:
    """Configure centralized logging.

    Args:
        app_name: Name of the application
        host: Host of the centralized logging service
        port: Port of the centralized logging service
        level: The logging level
    """
    global _client

    # Create a client
    _client = LoggingClient(app_name=app_name, host=host, port=port)

    # Create a handler
    handler = RemoteHandler(client=_client, level=level)

    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)

    # Set the logging level
    logging.getLogger().setLevel(level)


def get_centralized_logger(name: str) -> Union[logging.Logger, SecureLogger]:
    """Get a logger that sends logs to the centralized logging service.

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
    logger = logging.getLogger(name)

    # Return the logger
    return logger
