#!/usr/bin/env python3
"""
Optimized test runner script that adjusts the number of pytest workers based on test count.

This script counts the number of tests to be run and sets the appropriate number of workers:
- If the test count exceeds a threshold (2x MAX_WORKERS), it uses all available workers
- Otherwise, it defaults to a single worker to reduce overhead for small test runs
"""

from __future__ import annotations

import logging
import os
import os.path  # Used for os.path.normpath and os.sep
import platform
import shutil
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
    for var in [
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "DYLD_INSERT_LIBRARIES",
        "DYLD_LIBRARY_PATH",
    ]:
        env.pop(var, None)

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
        if arg.startswith(("--exec", "--shell")):
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
    # Default to 1 test if we can't determine the count
    default_test_count = 1

    # Check if we have any test files specified
    has_test_files = any(arg.endswith(".py") for arg in validated_args)

    try:
        logger.info("Collecting tests...")

        # Run pytest with --collect-only to get the list of tests
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # nosec B607 - subprocess call is used with a fixed executable path
        result = subprocess.run(  # nosec B603 # nosec B607
            [sys.executable, "-m", "pytest", "--collect-only", *validated_args],
            check=False,
            capture_output=True,
            text=True,
            shell=False,  # Explicitly set shell=False for security
            env=get_sanitized_env(),
            timeout=300,  # Set a timeout of 5 minutes
        )

        # Check if pytest collection was successful
        if result.returncode != 0:
            logger.warning(
                "Test collection failed with return code %d", result.returncode
            )
            if result.stderr:
                logger.debug("Collection error: %s", result.stderr)
            return default_test_count if has_test_files else 0

        # Get the output
        output = result.stdout
        if not output:
            logger.warning("No output from test collection")
            return default_test_count if has_test_files else 0

        # Count the number of collected tests by looking for lines that contain
        # a path followed by "::" which indicates a test
        test_count = 0
        for line in output.splitlines():
            if (
                "::" in line
                and not line.strip().startswith("<")
                and "PASSED" not in line
                and "FAILED" not in line
            ):
                test_count += 1

        # Look for the summary line that says "collected X items"
        for line in output.splitlines():
            if "collected " in line and " item" in line:
                try:
                    # Extract the number from "collected X items"
                    parts = line.split("collected ")[1].split(" item")[0]
                    collected_count = int(parts.strip())
                    if collected_count > 0:
                        # If we found a valid count in the summary, use it
                        test_count = collected_count
                        break
                except (ValueError, IndexError):
                    # If parsing fails, continue with our manual count
                    pass

        # If we somehow didn't find any tests but pytest is going to run tests,        # default to at least 1 test
        if test_count == 0 and has_test_files:
            logger.warning(
                "No tests found in collection output, "
                "but test files specified. Using default count."
            )
            test_count = default_test_count

        logger.info("Collected %d tests", test_count)
        return test_count

    except subprocess.TimeoutExpired as e:
        logger.warning(
            "Test collection timed out after 5 minutes: %s. Falling back to single worker.",
            e,
        )
        return default_test_count if has_test_files else 0

    except subprocess.CalledProcessError as e:
        logger.warning("Error collecting tests: %s. Falling back to single worker.", e)
        return default_test_count if has_test_files else 0

    except Exception as e:
        logger.warning(
            "Unexpected error collecting tests: %s. Falling back to single worker.", e
        )
        return default_test_count if has_test_files else 0


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    This is needed for bandit and other security tools to write their reports.
    Returns silently if the directory already exists or was created successfully.
    Logs a warning if the directory could not be created but continues execution.
    """
    reports_dir = Path("security-reports")

    # Check if directory already exists
    if reports_dir.exists() and reports_dir.is_dir():
        logger.debug("security-reports directory already exists")
        return

    # Try to create the directory
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created security-reports directory")
        return
    except (PermissionError, OSError) as e:
        logger.warning("Failed to create security-reports directory: %s", e)

    # First fallback: Try to create in current directory with different name
    try:
        alt_reports_dir = Path("security_reports")  # Use underscore instead of hyphen
        if not alt_reports_dir.exists():
            alt_reports_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created alternative security_reports directory")

            # Create a symlink to the alternative directory
            try:
                if platform.system() == "Windows":
                    # Use directory junction on Windows
                    cmd_path = shutil.which("cmd.exe")
                    if cmd_path:
                        # nosec B603 - subprocess call is used with shell=False and validated arguments
                        # nosec B607 - subprocess call is used with a fixed executable path
                        subprocess.run(  # nosec B603 # nosec B607
                            [
                                cmd_path,
                                "/c",
                                "mklink",
                                "/J",
                                "security-reports",
                                str(alt_reports_dir),
                            ],
                            check=False,
                            shell=False,
                            capture_output=True,
                        )
                else:
                    # Use symlink on Unix
                    os.symlink(alt_reports_dir, "security-reports")
                return
            except Exception as symlink_error:
                logger.warning(
                    "Failed to create symlink to alternative directory: %s",
                    symlink_error,
                )
    except Exception as alt_dir_error:
        logger.warning(
            "Failed to create alternative security_reports directory: %s", alt_dir_error
        )

    # Second fallback: Try to create in temp directory
    try:
        import tempfile

        temp_dir = Path(tempfile.gettempdir()) / "security-reports"
        temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created security-reports directory in temp location: %s", temp_dir)

        # Try to create a symlink or junction to the temp directory
        try:
            if platform.system() == "Windows":
                # Use directory junction on Windows
                cmd_path = shutil.which("cmd.exe")
                if cmd_path:
                    # nosec B603 - subprocess call is used with shell=False and validated arguments
                    # nosec B607 - subprocess call is used with a fixed executable path
                    subprocess.run(  # nosec B603 # nosec B607
                        [
                            cmd_path,
                            "/c",
                            "mklink",
                            "/J",
                            "security-reports",
                            str(temp_dir),
                        ],
                        check=False,
                        shell=False,
                        capture_output=True,
                    )
            else:
                # Use symlink on Unix
                os.symlink(temp_dir, "security-reports")
        except Exception as symlink_error:
            logger.warning(
                "Failed to create symlink to temp directory: %s", symlink_error
            )
    except Exception as temp_dir_error:
        logger.warning(
            "Failed to create security-reports directory in temp location: %s",
            temp_dir_error,
        )

    # Final fallback: Just continue without the directory
    # The security tools should handle this gracefully or we'll catch their exceptions


def check_venv_exists() -> bool:
    """
    Check if we're running in a virtual environment.

    Returns:
        bool: True if running in a virtual environment, False otherwise

    """
    try:
        # Method 1: Check for sys.real_prefix (set by virtualenv)
        if hasattr(sys, "real_prefix"):
            return True

        # Method 2: Check for sys.base_prefix != sys.prefix (set by venv)
        if hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix:
            return True

        # Method 3: Check for VIRTUAL_ENV environment variable
        if os.environ.get("VIRTUAL_ENV"):
            return True

        # Method 4: Check for common virtual environment directories
        for venv_dir in [".venv", "venv", "env", ".env"]:
            if os.path.isdir(venv_dir) and os.path.isfile(
                os.path.join(venv_dir, "pyvenv.cfg")
            ):
                return True

        # Not in a virtual environment
        return False
    except Exception as e:
        # If any error occurs, log it but assume we're not in a virtual environment
        logger.warning("Error checking for virtual environment: %s", e)
        return False


def main() -> None:
    """
    Run the test suite with optimized worker count.

    Validates command line arguments, counts tests, and runs pytest with the
    appropriate number of workers.
    """
    # Check if we should skip the virtual environment check
    if os.environ.get("SKIP_VENV_CHECK") == "1":
        logger.info("Skipping virtual environment check")
    else:
        # Check if we're running in a virtual environment
        in_venv = check_venv_exists()
        if not in_venv:
            logger.warning(
                "Not running in a virtual environment. This may cause issues with pytest."
            )
            logger.info(
                "Continuing anyway, but consider running in a virtual environment."
            )

            # Create a temporary virtual environment if needed for CI environments
            if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
                logger.info(
                    "CI environment detected. Will proceed without virtual environment."
                )
                # In CI, we can continue without a virtual environment as dependencies are installed globally

    # Ensure pytest-xdist is installed
    try:
        # First check if pytest-xdist is already installed
        try:
            # nosec B603 - subprocess call is used with shell=False and validated arguments
            # nosec B607 - subprocess call is used with a fixed executable path
            check_result = subprocess.run(  # nosec B603 # nosec B607
                [sys.executable, "-c", "import pytest_xdist"],
                check=False,
                capture_output=True,
                shell=False,  # Explicitly set shell=False for security
                env=get_sanitized_env(),
                timeout=30,  # Short timeout for import check
            )

            if check_result.returncode == 0:
                logger.info("pytest-xdist is already installed")
            else:
                # Try to install pytest-xdist
                logger.info("Installing pytest-xdist...")

                # Determine which package installer to use (pip or uv)
                use_uv = False
                try:
                    # Check if uv is available
                    # Get full path to uv executable to avoid B607 warning
                    uv_path = shutil.which("uv") or "uv"
                    # nosec B603 - subprocess call is used with shell=False and validated arguments
                    # nosec B607 - We're using shutil.which to get the full path
                    uv_check = subprocess.run(  # nosec B603 # nosec B607
                        [uv_path, "--version"],
                        check=False,
                        capture_output=True,
                        shell=False,
                        env=get_sanitized_env(),
                        timeout=30,
                    )
                    use_uv = uv_check.returncode == 0
                except (subprocess.SubprocessError, FileNotFoundError):
                    use_uv = False

                # Install using the appropriate tool
                if use_uv:
                    logger.info("Using uv to install pytest-xdist")
                    install_cmd = ["uv", "pip", "install", "pytest-xdist"]
                else:
                    logger.info("Using pip to install pytest-xdist")
                    install_cmd = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "pytest-xdist",
                    ]

                # nosec B603 - subprocess call is used with shell=False and validated arguments
                # nosec B607 - subprocess call is used with a fixed executable path
                install_result = subprocess.run(  # nosec B603 # nosec B607
                    install_cmd,
                    check=False,
                    capture_output=True,
                    shell=False,  # Explicitly set shell=False for security
                    env=get_sanitized_env(),
                    timeout=300,  # Set a timeout of 5 minutes
                )

                if install_result.returncode == 0:
                    logger.info("Successfully installed pytest-xdist")
                else:
                    logger.warning(
                        "Failed to install pytest-xdist. Will run tests without parallelization."
                    )
                    if install_result.stderr:
                        logger.debug(
                            "Installation error: %s",
                            install_result.stderr.decode("utf-8", errors="replace"),
                        )
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            logger.warning(
                "Error checking for pytest-xdist: %s. Will run tests without parallelization.",
                e,
            )
    except Exception as e:
        logger.warning(
            "Unexpected error installing pytest-xdist: %s. Will run tests without parallelization.",
            e,
        )

    # Ensure security-reports directory exists
    ensure_security_reports_dir()

    # Validate command line arguments
    validated_args = validate_args(sys.argv[1:])

    # Count the number of tests
    test_count = count_tests(validated_args)

    # Calculate the number of workers based on the number of tests
    # If test count exceeds threshold (2x MAX_WORKERS), use all available workers; otherwise use 1
    num_workers = MAX_WORKERS if test_count > THRESHOLD else 1
    logger.info(
        "Collected %d tests. Using %d worker%s",
        test_count,
        num_workers,
        "s" if num_workers > 1 else "",
    )

    # Run pytest with the calculated number of workers
    try:
        # Check if pytest-xdist is available
        xdist_available = False
        try:
            # nosec B603 - subprocess call is used with shell=False and validated arguments
            # nosec B607 - subprocess call is used with a fixed executable path
            xdist_check = subprocess.run(  # nosec B603 # nosec B607
                [sys.executable, "-c", "import pytest_xdist"],
                check=False,
                capture_output=True,
                shell=False,  # Explicitly set shell=False for security                env=get_sanitized_env(),
                timeout=30,  # Short timeout for import check
            )
            xdist_available = xdist_check.returncode == 0
            if xdist_available:
                logger.info("pytest-xdist is available, parallel testing is enabled")
            else:
                logger.warning(
                    "pytest-xdist import check failed, "
                    "will run tests without parallelization"
                )
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            logger.warning(
                "Failed to check for pytest-xdist: %s. Will run tests without parallelization.",
                e,
            )
        except Exception as e:
            logger.warning(
                "Unexpected error checking for pytest-xdist: %s. Will run tests without parallelization.",
                e,
            )

        # Determine pytest command based on available modules and arguments
        pytest_cmd = [sys.executable, "-m", "pytest"]

        # Add parallel workers if xdist is available and we have enough tests
        if xdist_available and num_workers > 1:
            pytest_cmd.append(f"-n={num_workers}")
            logger.info("Using %d parallel workers", num_workers)
        else:
            logger.info("Running tests sequentially")

        # Add --no-cov if not already specified to avoid coverage failures with xdist
        has_coverage = any("--cov" in arg for arg in validated_args)
        has_keyword = any("-k" in arg for arg in validated_args)

        if not has_coverage and not has_keyword:
            pytest_cmd.append("--no-cov")

        # Add validated arguments
        pytest_cmd.extend(validated_args)

        # Log the final command
        logger.info("Running pytest with command: %s", " ".join(pytest_cmd))

        # Run pytest with the calculated command
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        # nosec B607 - subprocess call is used with a fixed executable path
        result = subprocess.run(  # nosec B603 # nosec B607
            pytest_cmd,
            check=False,
            shell=False,  # Explicitly set shell=False for security
            env=get_sanitized_env(),
            timeout=3600,  # Set a timeout of 1 hour to prevent hanging
        )

        # Check for common pytest errors
        if result.returncode not in [0, 1, 2, 3, 4, 5]:  # 0=success, 1-5=test failures
            logger.warning(
                "Pytest exited with unexpected return code: %d", result.returncode
            )
            if result.stdout:
                logger.info("Pytest stdout: %s", result.stdout)
            if result.stderr:
                logger.error("Pytest stderr: %s", result.stderr)
    except subprocess.TimeoutExpired as timeout_error:
        logger.exception("Pytest execution timed out after 1 hour: %s", timeout_error)
        sys.exit(2)
    except subprocess.SubprocessError as subprocess_error:
        logger.exception("Error running pytest: %s", subprocess_error)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error running pytest: %s", e)
        sys.exit(1)

    # Exit with the same exit code as pytest
    sys.exit(result.returncode)


if __name__ == "__main__":
    # Set CI environment variable if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS"):
        os.environ["CI"] = "1"
        logger.info("GitHub Actions environment detected")

    # Skip virtual environment check by setting a flag
    os.environ["SKIP_VENV_CHECK"] = "1"

    main()
