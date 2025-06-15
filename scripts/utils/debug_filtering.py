"""Provides log filtering utilities for the pAIssive Income project."""

from __future__ import annotations

# Standard library imports
import logging
from typing import Final, Sequence

# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger: Final = get_logger(__name__)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def filter_debug_logs(
    logs: Sequence[tuple[int, str]], level: int = logging.INFO
) -> list[str]:
    """
    Filter log messages to only include messages at or above the specified level.

    Args:
        logs: List of (level, message) tuples
        level: Minimum logging level to include (e.g., logging.INFO)

    Returns:
        list[str]: Filtered list of log messages above the specified level

    """
    return [msg for lvl, msg in logs if lvl >= level]


def main() -> None:
    """
    Demo usage of the debug log filtering utility.

    This function demonstrates how to use the log filtering functionality
    by creating sample logs at different levels and filtering them.
    """
    # Create sample logs at different levels
    sample_logs: list[tuple[int, str]] = [
        (logging.DEBUG, "Debug message"),
        (logging.INFO, "Info message"),
        (logging.WARNING, "Warning!"),
        (logging.ERROR, "Error occurred"),
    ]

    # Filter logs at WARNING level and above
    filtered_logs: list[str] = filter_debug_logs(sample_logs, logging.WARNING)
    for log in filtered_logs:
        logger.info("Filtered log: %s", log)


if __name__ == "__main__":
    main()
