"""Provides log filtering utilities for the pAIssive Income project."""

# Standard library imports
import logging

# Third-party imports

# Local imports


def filter_debug_logs(logs, level=logging.INFO):
    """Filter log messages to only include messages at or above the specified level.

    Args:
        logs (list of tuples): List of (level, message) tuples.
        level (int): Logging level (e.g., logging.INFO).

    Returns:
        list: Filtered list of log messages.

    """
    return [msg for lvl, msg in logs if lvl >= level]


def main():
    """Demo usage of the debug log filtering utility."""
    sample_logs = [
        (logging.DEBUG, "Debug message"),
        (logging.INFO, "Info message"),
        (logging.WARNING, "Warning!"),
        (logging.ERROR, "Error occurred"),
    ]
    filtered = filter_debug_logs(sample_logs, level=logging.WARNING)
    for msg in filtered:
        print(msg)


if __name__ == "__main__":
    main()
