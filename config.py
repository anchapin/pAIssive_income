"""config.py - Configuration for Flask app and SQLAlchemy."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Configuration settings for the application."""

    # Base paths
    APP_DIR = Path(__file__).parent.resolve()
    LOG_DIR = APP_DIR / "logs"

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging settings
    LOG_FILE = LOG_DIR / "flask.log"
    LOG_ERROR_FILE = LOG_DIR / "error.log"  # Separate error log
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT_JSON: bool = True  # Use JSON formatting for file logs
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 10
    LOG_ROTATION_INTERVAL = timedelta(days=1)  # Rotate logs daily
    LOG_COMPRESS = True  # Compress rotated logs
    LOG_COMPRESSION_DELAY = 60  # Wait 60 seconds before compressing
    LOG_QUEUE_SIZE = 1000  # Size of async logging queue
    LOG_REQUEST_ID_HEADER = "X-Request-ID"  # Header to extract request ID from
    LOG_CORRELATION_ID_HEADER = "X-Correlation-ID"  # For distributed tracing

    # Performance logging thresholds (in milliseconds)
    LOG_SLOW_REQUEST_THRESHOLD: int = 1000  # Log requests taking more than 1 second
    LOG_VERY_SLOW_REQUEST_THRESHOLD = (
        3000  # Log detailed info for requests over 3 seconds
    )

    # Audit logging settings
    LOG_AUDIT_EVENTS = True  # Enable audit logging
    LOG_AUDIT_FILE = LOG_DIR / "audit.log"  # Separate file for audit logs

    # Error reporting settings
    LOG_INCLUDE_TRACE = True  # Include stack traces in error logs
    LOG_MAX_TRACEBACK_DEPTH = 20  # Maximum depth of stack traces
    LOG_SANITIZE_ERRORS = True  # Remove sensitive data from error logs

    SECRET_KEY: str | None = None


# Apply development overrides after class definition
if os.environ.get("FLASK_ENV") == "development":
    Config.LOG_LEVEL = "DEBUG"
    Config.LOG_FORMAT_JSON = False  # Human readable logs in development
    Config.LOG_SLOW_REQUEST_THRESHOLD = 500  # More aggressive in development

# Environment-based overrides (use local variables, do not reassign constants in class)
if os.environ.get("ENV") == "development":
    _dev_db_url = os.environ.get("DEV_DATABASE_URL")
    if _dev_db_url:
        Config.SQLALCHEMY_DATABASE_URI = _dev_db_url
    _dev_secret = os.environ.get("DEV_SECRET_KEY")
    if _dev_secret:
        Config.SECRET_KEY = _dev_secret
