"""
Common utilities for secure logging and log management.
"""

import logging
from typing import cast, Dict, Union

# Third-party imports
# Local imports
from .secure_logging import (
    SENSITIVE_FIELDS,
    SecureLogger,
    get_secure_logger,
    mask_sensitive_data,
)

__all__ = [
    "SENSITIVE_FIELDS",
    "SecureLogger",
    "get_logger",
    "get_secure_logger",
    "mask_sensitive_data",
]


# Logger cache to avoid creating duplicate loggers
_logger_cache: Dict[str, Union[SecureLogger, logging.Logger]] = {}

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
            logger = SecureLogger(name)
        except Exception:
            # Fall back to standard logger if secure logger fails
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

    _logger_cache[name] = logger
    return logger

# Create global secure logger instance
secure_logger = get_logger("secure_logger")
