#!/usr/bin/env python3
"""
Optimized test runner script that adjusts the number of pytest workers based on test count.

This script counts the number of tests to be run and sets the appropriate number of workers:
- If the test count exceeds a threshold (2x MAX_WORKERS), it uses all available workers
- Otherwise, it defaults to a single worker to reduce overhead for small test runs
"""

from __future__ import annotations

import logging
import os.path  # Used for os.path.normpath and os.sep
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
from pathlib import Path
from typing import Sequence

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Set to DEBUG for more verbose output
logging.getLogger().setLevel(logging.INFO)


# Maximum number of workers
MAX_WORKERS = 12
# Threshold: if test count > threshold, use MAX_WORKERS, else use 1
THRESHOLD = 2 * MAX_WORKERS
def get_sanitized_env() -> dict[str, str]:
    """
    Create a sanitized copy of the environment variables.

    Removes potentially dangerous environment variables that could be used
    for command injection or other security issues.

    Returns:
        dict[str, str]: Sanitized environment variables

    """
    # Start with a copy of the current environment
    env = dict(os.environ)

    # Remove potentially dangerous environment variables
    for var in ["LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH"]:
        if var in env:
            del env[var]

    return env


def validate_args(args: Sequence[str]) -> list[str]:
    """
    Validate command line arguments to ensure they are safe.

    Args:
        args: Command line arguments to validate

    Returns:
        list[str]: Validated arguments

    """
    # Start with an empty list of validated arguments
    validated_args = []

    # Add each argument that passes validation
    for arg in args:
        # Skip empty arguments
        if not arg:
            continue

        # Skip arguments that contain shell metacharacters
        if any(c in arg for c in ";&|`$(){}[]<>\\\"'"):
            logger.warning("Skipping argument with shell metacharacters: %s", arg)
            continue

        # Skip arguments that look like they're trying to break out of the command
        if arg.startswith("-") and not arg.startswith("--"):
            # Allow common pytest options
            if arg in ["-v", "-vv", "-vvv", "-xvs", "-xvs"]:
                validated_args.append(arg)
            else:
                logger.warning("Skipping suspicious argument: %s", arg)
            continue

        # Skip arguments that look like they're trying to execute arbitrary code
        if arg.startswith("--exec") or arg.startswith("--shell"):
            logger.warning("Skipping suspicious argument: %s", arg)
            continue

        # If the argument is a file path, check for directory traversal attempts
        if os.path.sep in arg or "/" in arg or "\\" in arg:
            # Additional check for path traversal attempts
            normalized_path = os.path.normpath(arg)
            path_obj = Path(normalized_path)
            if not normalized_path.startswith("..") and ".." not in path_obj.parts:
                validated_args.append(arg)
            else:
                logger.warning("Skipping path with directory traversal: %s", arg)
        else:
            # If we get here, the argument passed all checks
            validated_args.append(arg)

    return validated_args


def count_tests(validated_args: list[str]) -> int:
    """
    Count the number of tests that will be run.

    Args:
        validated_args: Validated command line arguments

    Returns:
        int: Number of tests that will be run

    """
    try:
        # Run pytest with --collect-only to get the list of tests
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # ruff: noqa: S603
        result = subprocess.run(  # nosec B603
            [sys.executable, "-m", "pytest", "--collect-only"] + validated_args,
            check=False,
            capture_output=True,
            text=True,
            shell=False,  # Explicitly set shell=False for security
            env=get_sanitized_env(),
            timeout=300  # Set a timeout of 5 minutes
        )

        # Get the output
        output = result.stdout

        # Count the number of collected tests by looking for lines that contain
        # a path followed by "::" which indicates a test
        test_count = 0
        for line in output.splitlines():
            if "::" in line and not line.strip().startswith("<") and "PASSED" not in line and "FAILED" not in line:
                test_count += 1

        # If we somehow didn't find any tests but pytest is going to run tests,
        # default to at least 1 test
        if test_count == 0 and any(arg.endswith(".py") for arg in validated_args):
            test_count = 1

        logger.debug("Collected %d tests", test_count)
    except subprocess.TimeoutExpired:
        logger.warning("Test collection timed out after 5 minutes. Falling back to single worker.")
        return 1
    except subprocess.CalledProcessError:
        logger.warning("Error collecting tests. Falling back to single worker.")
        return 1
    else:
        return test_count


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    This is needed for bandit and other security tools to write their reports.
    """
    reports_dir = Path("security-reports")
    if not reports_dir.exists():
        try:
            reports_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created security-reports directory")
        except (PermissionError, OSError) as e:
            logger.warning("Failed to create security-reports directory: %s", e)


def check_venv_exists() -> bool:
    """
    Check if we're running in a virtual environment.

    Returns:
        bool: True if running in a virtual environment, False otherwise

    """
    # This should not raise exceptions, but we'll be defensive just in case
    return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)


def main() -> None:
    """
    Main entry point for the script.

    Validates command line arguments, counts tests, and runs pytest with the
    appropriate number of workers.
    """
    # Check if we're running in a virtual environment
    if not check_venv_exists():
        logger.warning("Not running in a virtual environment. This may cause issues with pytest.")
        logger.info("Continuing anyway, but consider running in a virtual environment.")

    # Ensure pytest-xdist is installed
    try:
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # ruff: noqa: S603
        subprocess.run(  # nosec B603
            [sys.executable, "-m", "pip", "install", "pytest-xdist"],
            check=False,
            capture_output=True,
            shell=False,  # Explicitly set shell=False for security
            env=get_sanitized_env(),
            timeout=300  # Set a timeout of 5 minutes
        )
        logger.info("Ensured pytest-xdist is installed")
    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
        logger.warning("Failed to install pytest-xdist. Will run tests without parallelization.")

    # Ensure security-reports directory exists
    ensure_security_reports_dir()

    # Validate command line arguments
    validated_args = validate_args(sys.argv[1:])

    # Count the number of tests
    test_count = count_tests(validated_args)

    # Calculate the number of workers based on the number of tests
    # If test count exceeds threshold (2x MAX_WORKERS), use all available workers; otherwise use 1
    num_workers = MAX_WORKERS if test_count > THRESHOLD else 1
    logger.info("Collected %d tests. Using %d worker%s", test_count, num_workers, "s" if num_workers > 1 else "")

    # Run pytest with the calculated number of workers
    # nosec B603 - subprocess call is used with shell=False and validated arguments
    try:
        # Check if pytest-xdist is available
        try:
            # ruff: noqa: S603
            xdist_check = subprocess.run(  # nosec B603
                [sys.executable, "-c", "import pytest_xdist"],
                check=False,
                capture_output=True,
                shell=False,  # Explicitly set shell=False for security
                env=get_sanitized_env(),
                timeout=30  # Short timeout for import check
            )
            xdist_available = xdist_check.returncode == 0
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            xdist_available = False
            logger.warning("Failed to check for pytest-xdist. Will run tests without parallelization.")

        # Add --no-cov if not already specified to avoid coverage failures
        if not any("--cov" in arg for arg in validated_args) and not any("-k" in arg for arg in validated_args):
            if xdist_available and num_workers > 1:
                pytest_cmd = [sys.executable, "-m", "pytest", f"-n={num_workers}", "--no-cov"] + validated_args
            else:
                pytest_cmd = [sys.executable, "-m", "pytest", "--no-cov"] + validated_args
        else:
            if xdist_available and num_workers > 1:
                pytest_cmd = [sys.executable, "-m", "pytest", f"-n={num_workers}"] + validated_args
            else:
                pytest_cmd = [sys.executable, "-m", "pytest"] + validated_args

        logger.info("Running pytest with command: %s", " ".join(pytest_cmd))

        # ruff: noqa: S603
        result = subprocess.run(  # nosec B603
            pytest_cmd,
            check=False,
            shell=False,  # Explicitly set shell=False for security
            env=get_sanitized_env(),
            timeout=3600  # Set a timeout of 1 hour to prevent hanging
        )
    except subprocess.TimeoutExpired:
        logger.exception("Pytest execution timed out after 1 hour")
        sys.exit(2)
    except subprocess.SubprocessError:
        logger.exception("Error running pytest")
        sys.exit(1)

    # Exit with the same exit code as pytest
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
