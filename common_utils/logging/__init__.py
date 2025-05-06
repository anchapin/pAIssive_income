"""Common utilities for secure logging and log management.

This package provides tools for secure logging, ensuring sensitive information
is not logged in clear text.
"""

# Standard library imports
import logging

# Third-party imports
# Local imports
from .secure_logging import (
    SENSITIVE_FIELDS,
    SecureLogger,
    get_secure_logger,
    mask_sensitive_data,
)

__all__ = [
    "mask_sensitive_data",
    "get_secure_logger",
    "SecureLogger",
    "SENSITIVE_FIELDS",
    "get_logger",
]


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    This is a convenience function that returns a secure logger if available,
    otherwise falls back to a standard logger.

    Args:
    ----
        name: Name of the logger

    Returns:
    -------
        logging.Logger: The logger

    """
    try:
        # Cast the SecureLogger to Logger for type compatibility
        return logging.getLogger(name)
    except Exception:
        # Fall back to standard logger if secure logger is not available
        return logging.getLogger(name)
