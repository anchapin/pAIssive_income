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

    This is a convenience function that returns a secure logger by default,
    which automatically masks sensitive information.

    Args:
    ----
        name: Name of the logger

    Returns:
    -------
        logging.Logger: The secure logger

    """
    try:
        # Return a SecureLogger that masks sensitive information
        logger = get_secure_logger(name)
        return logger  # type: ignore
    except Exception as e:
        # Fall back to standard logger if secure logger is not available
        logging.getLogger("logging_setup").warning(
            f"Failed to create secure logger, falling back to standard logger: {str(e)}"
        )
        return logging.getLogger(name)
