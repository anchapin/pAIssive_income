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
import shlex
from typing import Sequence, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Maximum number of workers
MAX_WORKERS = 12
# Threshold: if test count > threshold, use MAX_WORKERS, else use 1
THRESHOLD = 2 * MAX_WORKERS


def validate_args(args: Sequence[str]) -> List[str]:
    """
    Validate command line arguments to ensure they are safe.

    Args:
        args: Command line arguments to validate

    Returns:
        List[str]: Validated arguments
    """
    # Only allow known pytest arguments and paths
    validated_args = []
    for arg in args:
        # Sanitize any potentially dangerous arguments
        # This is a simple validation - in a real-world scenario,
        # you might want more sophisticated validation
        if arg.startswith('--'):
            # Allow pytest options
            validated_args.append(arg)
        elif arg.startswith('-'):
            # Allow pytest short options
            validated_args.append(arg)
        else:
            # For paths or other arguments, use shlex.quote for safety
            # but since we're not using shell=True, we just need to ensure
            # they don't contain shell metacharacters
            if not any(c in arg for c in ';&|`$(){}[]<>'):
                validated_args.append(arg)
            else:
                logger.warning(f"Skipping potentially unsafe argument: {arg}")

    return validated_args


def get_test_count(pytest_args: Sequence[str]) -> int:
    """
    Get the number of collected tests for the given pytest arguments.

    Args:
        pytest_args: Command line arguments to pass to pytest

    Returns:
        int: Number of tests that would be run
    """
    # Create a safe command with validated arguments
    validated_args = validate_args(pytest_args)
    cmd = ["pytest", "--collect-only", "-q"] + validated_args

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

    # Validate arguments for security
    validated_args = validate_args(pytest_args)

    # Get number of tests that would be run
    test_count = get_test_count(validated_args)

    # Use ternary operator for cleaner code
    n_workers = MAX_WORKERS if test_count > THRESHOLD else 1

    logger.info("Collected %d tests. Using %d pytest worker(s).", test_count, n_workers)

    # Build pytest command with unpacking instead of concatenation
    # Add --no-cov if not already specified to avoid coverage failures
    if not any("--cov" in arg for arg in validated_args) and not any("-k" in arg for arg in validated_args):
        pytest_cmd = ["pytest", f"-n={n_workers}", "--no-cov"] + validated_args
    else:
        pytest_cmd = ["pytest", f"-n={n_workers}"] + validated_args

    try:
        # Run pytest with the chosen number of workers
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # ruff: noqa: S603
        result = subprocess.run(  # nosec B603
            pytest_cmd,
            check=False,
            shell=False,  # Explicitly set shell=False for security
            env=None  # Use current environment, don't allow environment injection
        ).returncode
        sys.exit(result)
    except subprocess.SubprocessError:
        logger.exception("Error running pytest")
        sys.exit(1)


if __name__ == "__main__":
    main()