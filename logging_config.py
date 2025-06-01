"""logging_config - Global logging configuration for the project."""

import logging
import sys

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports can be added here as needed
# Example:
# try:
#     import some_third_party_module
# except ImportError as e:
#     logger.exception("Failed to import some_third_party_module", exc_info=e)

def configure_logging(
    level=logging.INFO,
    format_str="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
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
