"""
Logging configuration for the pAIssive_income project.

This module provides a centralized configuration for logging across the application.
"""

import json
import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Define log file paths
current_date = datetime.now().strftime("%Y-%m-%d")
app_log_file = logs_dir / f"app_{current_date}.log"
error_log_file = logs_dir / f"error_{current_date}.log"
access_log_file = logs_dir / f"access_{current_date}.log"
security_log_file = logs_dir / f"security_{current_date}.log"

# Define logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        "json": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "json_default": str,
            "timestamp": True,
        },
        "access": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(remote_addr)s - %(url)s - %(method)s - %(status)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(app_log_file),
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 10,
            "encoding": "utf8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": str(error_log_file),
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 10,
            "encoding": "utf8",
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "access",
            "filename": str(access_log_file),
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 10,
            "encoding": "utf8",
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(security_log_file),
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 10,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "paissive_income": {  # Application logger
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "paissive_income.access": {  # Access logger
            "handlers": ["access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "paissive_income.security": {  # Security logger
            "handlers": ["security_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def configure_logging():
    """
    Configure logging for the application.
    """
    # Check if we need to use JSON logging (e.g., in production)
    use_json = os.environ.get("USE_JSON_LOGGING", "false").lower() == "true"

    if use_json:
        try:
            # Import the JSON logger
            from pythonjsonlogger import jsonlogger

            # Update the handlers to use JSON formatter
            for handler_name, handler_config in LOGGING_CONFIG["handlers"].items():
                if handler_name != "console":  # Keep console output readable
                    handler_config["formatter"] = "json"
        except ImportError:
            logging.warning(
                "python-json-logger not installed. Falling back to standard logging."
            )

    # Apply the configuration
    logging.config.dictConfig(LOGGING_CONFIG)

    # Log that logging has been configured
    logging.info("Logging configured")


def get_logger(name):
    """
    Get a logger with the given name.

    Args:
        name: Name of the logger

    Returns:
        Logger instance
    """
    return logging.getLogger(f"paissive_income.{name}")


# Access logger for HTTP requests
access_logger = get_logger("access")

# Security logger for authentication and authorization events
security_logger = get_logger("security")


def log_request(request, response):
    """
    Log an HTTP request and response.

    Args:
        request: Flask request object
        response: Flask response object
    """
    access_logger.info(
        "Request processed",
        extra={
            "remote_addr": request.remote_addr,
            "url": request.path,
            "method": request.method,
            "status": response.status_code,
        },
    )


def log_security_event(event_type, user_id=None, details=None):
    """
    Log a security event.

    Args:
        event_type: Type of security event (e.g., login, logout, access_denied)
        user_id: ID of the user involved (if applicable)
        details: Additional details about the event
    """
    security_logger.info(
        f"Security event: {event_type}",
        extra={"event_type": event_type, "user_id": user_id, "details": details or {}},
    )


# Configure logging when this module is imported
configure_logging()
