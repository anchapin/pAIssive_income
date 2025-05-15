"""logger - Module for common_utils/logging.logger."""

# Standard library imports
import logging
import os
import sys
from typing import Dict, List, Optional, Union

# Third-party imports

# Local imports

# Cache for loggers to avoid creating multiple instances
_loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name.

    If a logger with the given name already exists, returns the existing instance.
    Otherwise, creates a new logger.

    Args:
        name: The name of the logger

    Returns:
        A Logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers: Optional[List[logging.Handler]] = None,
    propagate: bool = True,
) -> logging.Logger:
    """Set up a logger with the specified configuration.

    Args:
        name: The name of the logger
        level: The logging level (default: INFO)
        format_str: The log format string
        handlers: Optional list of handlers to add to the logger
        propagate: Whether the logger should propagate to parent loggers

    Returns:
        The configured Logger instance
    """
    logger = get_logger(name)
    logger.setLevel(level)
    logger.propagate = propagate

    # Remove existing handlers to avoid duplicates
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Add default console handler if no handlers provided
    if not handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(format_str))
        handlers = [console_handler]

    # Add all handlers to the logger
    for handler in handlers:
        logger.addHandler(handler)

    return logger
