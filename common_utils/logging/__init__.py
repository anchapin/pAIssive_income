"""
Common utilities for secure logging and log management.
"""

import logging
from typing import cast, Dict, Union

import sys # Added sys import

# Configure logging
logger = logging.getLogger(__name__)


# Third-party imports
# Local imports
try:
    from .secure_logging import (
        SENSITIVE_FIELDS,
        SecureLogger,
        get_secure_logger,
        mask_sensitive_data,
    )
except ImportError:
    print("Error: .secure_logging module not found. Ensure it's in the PYTHONPATH and the current package.")
    sys.exit(1)


__all__ = [
    "SENSITIVE_FIELDS",
    "SecureLogger",
    "get_logger",
    "get_secure_logger",
    "mask_sensitive_data",
    "secure_logger",
    "_logger_cache",
]


# Logger cache to avoid creating duplicate loggers
_logger_cache: Dict[str, Union[SecureLogger, logging.Logger]] = {}

# Create a default secure logger instance
secure_logger = get_secure_logger("secure_logger")

def get_logger(name: str, secure: bool = True) -> Union[SecureLogger, logging.Logger]:
    """Get a logger instance.

    Args:
        name: Logger name
        secure: Whether to return a secure logger (default True)

    Returns:
        Logger instance (SecureLogger if secure=True)
    """
    if name in _logger_cache:
        return _logger_cache[name]

    if secure:
        try:
            logger_instance = SecureLogger(name) # Renamed to avoid conflict with module-level logger
        except Exception:
            # Fall back to standard logger if secure logger fails
            logger.exception("Failed to initialize SecureLogger, falling back to standard logger.") # Use logger.exception
            logger_instance = logging.getLogger(name)
            logger_instance.setLevel(logging.INFO)
    else:
        logger_instance = logging.getLogger(name)
        logger_instance.setLevel(logging.INFO)

    _logger_cache[name] = logger_instance
    return logger_instance

# Note: secure_logger can be created on-demand using get_logger("secure_logger")
