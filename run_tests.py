#!/usr/bin/env python3
"""
Optimized test runner script that adjusts the number of pytest workers based on test count.

This script counts the number of tests to be run and sets the appropriate number of workers:
- If the test count exceeds a threshold (2x MAX_WORKERS), it uses all available workers
- Otherwise, it defaults to a single worker to reduce overhead for small test runs
"""

import logging
import os
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
import shlex
from typing import List, Sequence, Dict, Optional
import pathlib

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Set to DEBUG for more verbose output
# logging.getLogger().setLevel(logging.DEBUG)

# Maximum number of workers
MAX_WORKERS = 12
# Threshold: if test count > threshold, use MAX_WORKERS, else use 1
THRESHOLD = 2 * MAX_WORKERS


def get_sanitized_env() -> Dict[str, str]:
    """
    Create a sanitized copy of the environment variables.

    Removes potentially dangerous environment variables that could be used
    for command injection or other security issues.

    Returns:
        Dict[str, str]: Sanitized environment variables
    """
    # Create a copy of the current environment
    safe_env = os.environ.copy()

    # Remove potentially dangerous environment variables
    dangerous_prefixes = ['PYTEST_', 'PYTHON_', 'PATH_', 'LD_', 'DYLD_']
    for key in list(safe_env.keys()):
        if any(key.startswith(prefix) for prefix in dangerous_prefixes):
            safe_env.pop(key, None)

    return safe_env


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
        if arg.startswith('--'):
            # Allow pytest options, but validate they don't contain shell metacharacters
            if not any(c in arg.split('=')[1] if '=' in arg else '' for c in ';&|`$(){}[]<>'):
                validated_args.append(arg)
            else:
                logger.warning(f"Skipping potentially unsafe argument: {arg}")
        elif arg.startswith('-'):
            # Allow pytest short options
            validated_args.append(arg)
        else:
            # For paths or other arguments, use shlex.quote for safety
            # but since we're not using shell=True, we just need to ensure
            # they don't contain shell metacharacters
            if not any(c in arg for c in ';&|`$(){}[]<>'):
                # Additional check for path traversal attempts
                normalized_path = os.path.normpath(arg)
                if not normalized_path.startswith('..') and '..' not in normalized_path.split(os.sep):
                    validated_args.append(arg)
                else:
                    logger.warning(f"Skipping path with directory traversal: {arg}")
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
    cmd = ["pytest", "--collect-only", "-v"] + validated_args

    try:
        # Capture output of pytest collection
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # ruff: noqa: S603
        # Get a sanitized environment
        safe_env = get_sanitized_env()

        output = subprocess.check_output(  # nosec B603
            cmd,
            stderr=subprocess.DEVNULL,
            text=True,  # Use text instead of universal_newlines for newer Python
            shell=False,  # Explicitly set shell=False for security
            cwd=os.getcwd(),  # Explicitly set working directory
            timeout=300,  # Set a timeout of 5 minutes for test collection
            env=safe_env  # Use sanitized environment
        )
        # Count the number of collected tests by looking for lines that contain
        # a path followed by "::" which indicates a test
        test_count = 0
        for line in output.splitlines():
            if "::" in line and not line.strip().startswith("<") and "PASSED" not in line and "FAILED" not in line:
                test_count += 1

        # If we somehow didn't find any tests but pytest is going to run tests,
        # default to at least 1 test
        if test_count == 0 and any(arg.endswith('.py') for arg in validated_args):
            test_count = 1

        logger.debug(f"Collected {test_count} tests")
        return test_count
    except subprocess.TimeoutExpired:
        logger.warning("Test collection timed out after 5 minutes. Falling back to single worker.")
        return 1
    except subprocess.CalledProcessError:
        logger.warning("Error collecting tests. Falling back to single worker.")
        return 1


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    This is needed for bandit and other security tools to write their reports.
    """
    reports_dir = pathlib.Path("security-reports")
    if not reports_dir.exists():
        try:
            reports_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created security-reports directory")
        except Exception as e:
            logger.warning(f"Failed to create security-reports directory: {e}")


def main() -> None:
    """Run pytest with optimized worker count based on test count."""
    # Forward all command-line arguments to pytest except the script name
    pytest_args = sys.argv[1:]

    # Validate arguments for security
    validated_args = validate_args(pytest_args)

    # Ensure security-reports directory exists
    ensure_security_reports_dir()

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

        # Get a sanitized environment
        safe_env = get_sanitized_env()

        result = subprocess.run(  # nosec B603
            pytest_cmd,
            check=False,
            shell=False,  # Explicitly set shell=False for security
            env=safe_env,  # Use sanitized environment
            cwd=os.getcwd(),  # Explicitly set working directory
            timeout=3600,  # Set a timeout of 1 hour to prevent hanging
            text=True  # Use text mode for better error handling
        ).returncode
        sys.exit(result)
    except subprocess.TimeoutExpired:
        logger.error("Pytest execution timed out after 1 hour")
        sys.exit(2)
    except subprocess.SubprocessError:
        logger.exception("Error running pytest")
        sys.exit(1)


if __name__ == "__main__":
    main()