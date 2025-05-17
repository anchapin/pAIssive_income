#!/usr/bin/env python3
"""
Optimized test runner script that adjusts the number of pytest workers based on test count.

This script counts the number of tests to be run and sets the appropriate number of workers:
- If the test count exceeds a threshold (2x MAX_WORKERS), it uses all available workers
- Otherwise, it defaults to a single worker to reduce overhead for small test runs
"""

import logging
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
from typing import Sequence

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Maximum number of workers
MAX_WORKERS = 12
# Threshold: if test count > threshold, use MAX_WORKERS, else use 1
THRESHOLD = 2 * MAX_WORKERS


def get_test_count(pytest_args: Sequence[str]) -> int:
    """
    Get the number of collected tests for the given pytest arguments.

    Args:
        pytest_args: Command line arguments to pass to pytest

    Returns:
        int: Number of tests that would be run

    """
    # Create a safe command with validated arguments
    cmd = ["pytest", "--collect-only", "-q", *pytest_args]

    try:
        # Capture output of pytest collection
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # ruff: noqa: S603
        output = subprocess.check_output(  # nosec B603
            cmd,
            stderr=subprocess.DEVNULL,
            text=True,  # Use text instead of universal_newlines for newer Python
            shell=False  # Explicitly set shell=False for security
        )
        # Each test is one line in the output
        # Filter out empty lines and lines starting with '<' (pytest's summary lines)
        test_lines = [line for line in output.splitlines() if line.strip() and not line.startswith("<")]
        return len(test_lines)
    except subprocess.CalledProcessError:
        logger.warning("Error collecting tests. Falling back to single worker.")
        return 1


def main() -> None:
    """Run pytest with optimized worker count based on test count."""
    # Forward all command-line arguments to pytest except the script name
    pytest_args = sys.argv[1:]

    # Get number of tests that would be run
    test_count = get_test_count(pytest_args)

    # Use ternary operator for cleaner code
    n_workers = MAX_WORKERS if test_count > THRESHOLD else 1

    logger.info("Collected %d tests. Using %d pytest worker(s).", test_count, n_workers)

    # Build pytest command with unpacking instead of concatenation
    pytest_cmd = ["pytest", f"-n={n_workers}", *pytest_args]

    try:
        # Run pytest with the chosen number of workers
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # ruff: noqa: S603
        result = subprocess.run(  # nosec B603
            pytest_cmd,
            check=False,
            shell=False  # Explicitly set shell=False for security
        ).returncode
        sys.exit(result)
    except subprocess.SubprocessError:
        logger.exception("Error running pytest")
        sys.exit(1)


if __name__ == "__main__":
    main()
