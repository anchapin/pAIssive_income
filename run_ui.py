#!/usr/bin/env python3
"""run_ui.py - Entry point for the Flask web application."""

from __future__ import annotations

import contextlib
import gzip
import logging
import logging.handlers
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from queue import Queue
from typing import Any, TypeVar

from werkzeug.local import LocalProxy

from app_flask import create_app
from app_flask.middleware.logging_middleware import setup_request_logging
from config import Config
from flask.globals import current_app

# Type variable for generic typing
T = TypeVar("T")

# Type hint for Flask app logger
FlaskLogger = logging.Logger

logger = LocalProxy(lambda: current_app.logger)


class CompressedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """Extended handler that compresses rotated logs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize with compression delay."""
        self.compress_delay = int(kwargs.pop("compress_delay", 60))
        super().__init__(*args, **kwargs)

    def rotation_filename(self, default_name: str) -> str:
        """Generate compressed filename."""
        return f"{default_name}.gz"

    def rotate(self, source: str, dest: str) -> None:
        """Rotate and compress the log file."""

        def delayed_compress() -> None:
            """Compress file after delay to avoid race conditions."""
            time.sleep(float(self.compress_delay))
            source_path = Path(source)
            with source_path.open("rb") as f_in, gzip.open(f"{dest}.gz", "wb") as f_out:
                f_out.writelines(f_in)
            with contextlib.suppress(OSError):
                source_path.unlink()

        threading.Thread(target=delayed_compress, daemon=True).start()


class ContextFilter(logging.Filter):
    """Add contextual information to log records."""

    def __init__(self) -> None:
        """Initialize system information."""
        super().__init__()
        import time

        self.process_start_time = time.time()
        self.process_id = os.getpid()
        import psutil

        self.process = psutil.Process(self.process_id)

    def get_memory_usage(self) -> dict[str, float]:
        """Get current memory usage."""
        try:
            mem_info = self.process.memory_info()
            return {
                "memory_rss_mb": mem_info.rss / 1024 / 1024,
                "memory_vms_mb": mem_info.vms / 1024 / 1024,
                "memory_percent": self.process.memory_percent(),
            }
        except (AttributeError, OSError):
            return {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add extra fields to log record."""
        # Add process and memory information to logs
        import time

        record.process_id = self.process_id
        record.uptime = time.time() - self.process_start_time
        record.memory_usage = self.get_memory_usage()
        return True


def create_compressed_handler(
    filename: str, compress_delay: int = 60
) -> logging.Handler:
    """
    Create a rotating file handler with compression.

    Args:
        filename: Path to the log file
        compress_delay: Delay before compressing rotated logs in seconds

    Returns:
        CompressedRotatingFileHandler instance

    """
    return CompressedRotatingFileHandler(
        filename,
        when="midnight",
        interval=1,
        backupCount=Config.LOG_BACKUP_COUNT,
        delay=True,
        compress_delay=compress_delay,
        encoding="utf-8",
    )


def verify_log_files(*log_files: str) -> None:
    """
    Verify log files can be written to.

    Args:
        log_files: One or more log file paths

    """
    for log_file in log_files:
        log_path = Path(log_file)
        if log_path.exists():
            with log_path.open("a"):
                pass


def create_console_handler(level: str = Config.LOG_LEVEL) -> logging.Handler:
    """
    Create console handler with basic formatting.

    Args:
        level: Log level

    Returns:
        Handler for console output

    """
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    console_handler.setLevel(getattr(logging, level))
    return console_handler


def setup_file_formatter(use_json: bool = Config.LOG_FORMAT_JSON) -> logging.Formatter:
    """
    Set up formatter for file handlers.

    Args:
        use_json: Whether to use JSON formatting

    Returns:
        Formatter for file log handlers

    """
    if use_json:
        return logging.Formatter("%(message)s")
    return logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )


def setup_handlers() -> tuple[list[logging.Handler], Queue]:
    """
    Set up and configure all log handlers.

    Returns:
        Tuple of (list of handlers, logging queue)

    """
    # Create logging queue
    log_queue: Queue = Queue(maxsize=Config.LOG_QUEUE_SIZE)

    # Create main and error log handlers
    file_handler = create_compressed_handler(str(Config.LOG_FILE))
    error_handler = create_compressed_handler(str(Config.LOG_ERROR_FILE))
    error_handler.setLevel(logging.ERROR)

    # Create console handler
    console_handler = logging.StreamHandler()

    # Configure formatters
    file_formatter = setup_file_formatter(Config.LOG_FORMAT_JSON)
    console_formatter = logging.Formatter(
        "%(levelname)s [%(asctime)s] %(name)s: %(message)s"
    )

    # Apply formatters and filters
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(ContextFilter())
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))

    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))

    return [file_handler, error_handler, console_handler], log_queue


def setup_root_logger(level: str) -> logging.Logger:
    """
    Configure the root logger.

    Args:
        level: Logging level

    Returns:
        The configured root logger

    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    return root_logger


def setup_logging() -> None:
    """Set up application logging with rotation and formatting."""
    try:
        Path(Config.LOG_DIR).mkdir(parents=True, exist_ok=True)
        verify_log_files(str(Config.LOG_FILE), str(Config.LOG_ERROR_FILE))

        # Set up handlers and queue
        handlers, log_queue = setup_handlers()
        queue_handler = logging.handlers.QueueHandler(log_queue)
        queue_listener = logging.handlers.QueueListener(
            log_queue, *handlers, respect_handler_level=True
        )

        # Configure root logger
        root_logger = setup_root_logger(Config.LOG_LEVEL)
        root_logger.addHandler(queue_handler)
        root_logger.addFilter(ContextFilter())

        # Start queue listener
        queue_listener.start()
        import atexit

        atexit.register(queue_listener.stop)

        # Log initialization success
        root_logger.info(
            "Logging system initialized",
            extra={
                "log_file": Config.LOG_FILE,
                "error_log": Config.LOG_ERROR_FILE,
                "log_level": Config.LOG_LEVEL,
                "format": "JSON" if Config.LOG_FORMAT_JSON else "text",
                "compression": "enabled" if Config.LOG_COMPRESS else "disabled",
                "async_queue_size": Config.LOG_QUEUE_SIZE,
            },
        )

    except Exception:
        # Fall back to console logging
        console_handler = create_console_handler("INFO")
        root_logger = setup_root_logger("INFO")
        root_logger.addHandler(console_handler)
        root_logger.exception("Failed to initialize file logging")


# Initialize logging first
setup_logging()

# Create Flask application
app = create_app()

# Set up request logging middleware
setup_request_logging(app)

# Configure Flask's built-in logger to use our settings
if hasattr(app, "logger"):
    app.logger.handlers = []
    app.logger.propagate = True


@app.route("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        dict[str, str]: Health status information

    """
    return {
        "status": "healthy",
        "service": "paissive-income-ui",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    # Use 127.0.0.1 as default for security (localhost only)
    # Only use 0.0.0.0 in containerized environments where needed
    is_container = os.environ.get("CONTAINER", "false").lower() in ("true", "1", "yes")

    # Default to localhost for security, only bind to all interfaces in container
    if is_container:
        default_host = "0.0.0.0"  # noqa: S104 - Intentional for container environments
        if hasattr(app, "logger"):
            app.logger.warning(
                "Binding to all network interfaces (0.0.0.0). "
                "This is expected in container environments but may pose a security risk otherwise."
            )
    else:
        default_host = "127.0.0.1"

    host = os.environ.get("FLASK_HOST", default_host)
    port = int(os.environ.get("FLASK_PORT", "5000"))

    # Log startup information with extra context
    if hasattr(app, "logger"):
        app.logger.info(
            "Starting Flask application",
            extra={
                "host": host,
                "port": port,
                "environment": os.environ.get("FLASK_ENV", "development"),
                "python_version": sys.version,
                "debug_mode": app.debug if hasattr(app, "debug") else False,
            },
        )

    # Run the application
    app.run(host=host, port=port)
