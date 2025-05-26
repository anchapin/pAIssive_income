"""config.py - Configuration for Flask app and SQLAlchemy."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path
from typing import ClassVar


class Config:
    """Configuration settings for the application."""

    # Base paths
    APP_DIR = Path(__file__).parent.resolve()
    LOG_DIR = APP_DIR / "logs"

    # Server settings
    # In container environments, bind to all interfaces (0.0.0.0)
    # In non-container environments, bind only to localhost (127.0.0.1)
    # This can be overridden by setting the FLASK_HOST environment variable    # Only bind to all interfaces if explicitly configured and in container mode
    HOST = os.environ.get(
        "FLASK_HOST",
        "127.0.0.1",  # Default to localhost for security
    )
    PORT = int(os.environ.get("FLASK_PORT", "5000"))
    DEBUG = (
        os.environ.get("FLASK_ENV", "production") == "development"
        and os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    )

    # Disable reloader in container or production environments
    USE_RELOADER = DEBUG and (
        os.environ.get("FLASK_ENV") == "development"
        and not bool(os.environ.get("CONTAINER"))
    )

    # Force disable debug mode in container environments
    if os.environ.get("CONTAINER") == "true":
        DEBUG = False
        USE_RELOADER = False

    # Database settings    # Get the database URI based on environment
    if os.environ.get("FLASK_ENV") == "development":
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            "sqlite:///:memory:",  # Safe default for development
        )
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
        if SQLALCHEMY_DATABASE_URI is None:
            db_env_error = "DATABASE_URL environment variable must be set in production"
            raise ValueError(db_env_error)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict[str, object]] = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,  # Recycle connections every 5 minutes
    }

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
