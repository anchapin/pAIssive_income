"""logger - Module for common_utils/logging.logger."""

# Standard library imports
import logging
import sys
from typing import Dict, List, Optional

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging
logger = logging.getLogger(__name__)


# Configure logging



# Third-party imports
try:
    # Place third-party imports here
    import some_third_party_module
except ImportError as e:
    logger.exception("Failed to import some_third_party_module", exc_info=e)

# Local imports

# Cache for loggers to avoid creating multiple instances
_loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.

    If a logger with the given name already exists, returns the existing instance.
    Otherwise, creates a new logger.

    Args:
        name: The name of the logger

    Returns:
        A Logger instance

    """
    if name in _loggers:
        return _loggers[name]

    new_logger = logging.getLogger(name)
    _loggers[name] = new_logger
    return new_logger


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers: Optional[List[logging.Handler]] = None,
    propagate: bool = True,
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.

    Args:
        name: The name of the logger
        level: The logging level (default: INFO)
        format_str: The log format string
        handlers: Optional list of handlers to add to the logger
        propagate: Whether the logger should propagate to parent loggers

    Returns:
        The configured Logger instance

    """
    target_logger = get_logger(name)
    target_logger.setLevel(level)
    target_logger.propagate = propagate

    # Remove existing handlers to avoid duplicates
    for handler in list(target_logger.handlers):
        target_logger.removeHandler(handler)

    # Add default console handler if no handlers provided
    if not handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(format_str))
        handlers = [console_handler]

    # Add all handlers to the logger and set formatter
    formatter = logging.Formatter(format_str)
    for handler in handlers:
        # Always set the formatter on the handler to ensure consistency
        handler.setFormatter(formatter)
        target_logger.addHandler(handler)

    return target_logger
