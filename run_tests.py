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
        result = subprocess.run(
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

    # Validate command line arguments
    validated_args = validate_args(sys.argv[1:])

    # Count the number of tests
    test_count = count_tests(validated_args)

    # Calculate the number of workers based on the number of tests
    # Use at most 4 workers to avoid overwhelming the system
    num_workers = min(4, max(1, test_count // 5))
    logger.info("Running with %d worker%s", num_workers, "s" if num_workers > 1 else "")

    # Run pytest with the calculated number of workers
    # nosec B603 - subprocess call is used with shell=False and validated arguments
    result = subprocess.run(
        [sys.executable, "-m", "pytest", f"-n={num_workers}"] + validated_args,
        check=False,
        shell=False,  # Explicitly set shell=False for security
        env=get_sanitized_env()
    )

    # Exit with the same exit code as pytest
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
