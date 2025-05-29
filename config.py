"""config.py - Configuration for Flask app and SQLAlchemy."""

import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Configuration settings for the application."""

    # Base paths
    APP_DIR = Path(__file__).parent.resolve()
    LOG_DIR = APP_DIR / "logs"

    # Database settings
    def __init__(self):
        """Initialize configuration with environment variables."""
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging settings
    LOG_FILE = LOG_DIR / "flask.log"
    LOG_ERROR_FILE = LOG_DIR / "error.log"  # Separate error log
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT_JSON = True  # Use JSON formatting for file logs
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 10
    LOG_ROTATION_INTERVAL = timedelta(days=1)  # Rotate logs daily
    LOG_COMPRESS = True  # Compress rotated logs
    LOG_COMPRESSION_DELAY = 60  # Wait 60 seconds before compressing
    LOG_QUEUE_SIZE = 1000  # Size of async logging queue
    LOG_REQUEST_ID_HEADER = "X-Request-ID"  # Header to extract request ID from
    LOG_CORRELATION_ID_HEADER = "X-Correlation-ID"  # For distributed tracing

    # Performance logging thresholds (in milliseconds)
    LOG_SLOW_REQUEST_THRESHOLD = 1000  # Log requests taking more than 1 second
    LOG_VERY_SLOW_REQUEST_THRESHOLD = (
        3000  # Log detailed info for requests over 3 seconds
    )

    # Audit logging settings
    LOG_AUDIT_EVENTS = True  # Enable audit logging
    LOG_AUDIT_FILE = LOG_DIR / "audit.log"  # Separate file for audit logs

    # Set more detailed logging in development
    if os.environ.get("FLASK_ENV") == "development":
        LOG_LEVEL = "DEBUG"
        LOG_FORMAT_JSON = False  # Human readable logs in development
        LOG_SLOW_REQUEST_THRESHOLD = 500  # More aggressive in development

    # Error reporting settings
    LOG_INCLUDE_TRACE = True  # Include stack traces in error logs
    LOG_MAX_TRACEBACK_DEPTH = 20  # Maximum depth of stack traces
    LOG_SANITIZE_ERRORS = True  # Remove sensitive data from error logs
