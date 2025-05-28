"""logging_config - Global logging configuration for the project."""

import logging
import sys


def configure_logging(
    level=logging.INFO,
    format_str="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
):
    """
    Configure the root logger for the entire application.

    Args:
        level: Logging level (default: logging.INFO)
        format_str: Log message format

    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Remove all existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
    # Add a default StreamHandler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(format_str))
    root_logger.addHandler(handler)
