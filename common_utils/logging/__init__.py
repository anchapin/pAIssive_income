"""
Common utilities for secure logging and log management.

This package provides tools for secure logging, ensuring sensitive information
is not logged in clear text.
"""

from __future__ import annotations

# Standard library imports
import logging
from typing import cast

# Third-party imports
# Local imports
from .secure_logging import (
    SENSITIVE_FIELDS,
    SecureLogger,
    get_secure_logger,
    mask_sensitive_data,
    is_sensitive_key,
)

__all__ = [
    "SENSITIVE_FIELDS",
    "SecureLogger",
    "get_logger",
    "get_secure_logger",
    "mask_sensitive_data",
    "is_sensitive_key",
]


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    This is a convenience function that returns a secure logger by default,
    which automatically masks sensitive information.

    Args:
    ----
        name: Name of the logger

    Returns:
    -------
        logging.Logger: The secure logger or a standard logger as fallback

    """
    try:
        # Return a SecureLogger that masks sensitive information
        logger = get_secure_logger(name)
        # Cast to logging.Logger to satisfy type checking
        return cast("logging.Logger", logger)
    except (ImportError, AttributeError) as e:
        # Fall back to standard logger if secure logger is not available
        setup_logger = logging.getLogger("logging_setup")
        setup_logger.warning(
            "Failed to create secure logger, falling back to standard logger: %s",
            str(e),
        )
        return logging.getLogger(name)
