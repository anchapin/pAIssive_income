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
from typing import Any, Sequence

# Type alias for subprocess kwargs (for documentation purposes)
SubprocessKwargs = dict[str, Any]

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


def _parse_test_collection_output(output: str, has_test_files: bool) -> int:
    """Parse pytest --collect-only output to count tests."""
    default_test_count = 1
    test_count = 0
    if not output:
        logger.warning("No output from test collection")
        return default_test_count if has_test_files else 0
    for line in output.splitlines():
        if (
            "::" in line
            and not line.strip().startswith("<")
            and "PASSED" not in line
            and "FAILED" not in line
        ):
            test_count += 1
    for line in output.splitlines():
        if "collected " in line and " item" in line:
            try:
                parts = line.split("collected ")[1].split(" item")[0]
                collected_count = int(parts.strip())
                if collected_count > 0:
                    test_count = collected_count
                    break
            except (ValueError, IndexError):
                # Ignore parsing errors and continue to next line
                pass
    if test_count == 0 and has_test_files:
        logger.warning(
            "No tests found in collection output, but test files specified. Using default count."
        )
        test_count = default_test_count
    return test_count


def count_tests(validated_args: list[str]) -> int:
    """
    Count the number of tests that will be run.

    Args:
        validated_args: Validated command line arguments

    Returns:
        int: Number of tests that will be run

    """
    default_test_count = 1
    has_test_files = any(arg.endswith(".py") for arg in validated_args)
    test_count = 0
    try:
        logger.info("Collecting tests...")
        result = _safe_subprocess_run(
            [sys.executable, "-m", "pytest", "--collect-only", *validated_args],
            check=False,
            capture_output=True,
            text=True,
            shell=False,
            env=get_sanitized_env(),
            timeout=300,
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        logger.warning(
            "Test collection failed or timed out: %s. Falling back to single worker.",
            e,
        )
    else:
        if result.returncode != 0:
            logger.warning(
                "Test collection failed with return code %d", result.returncode
            )
            if result.stderr:
                logger.debug("Collection error: %s", result.stderr)
            test_count = default_test_count if has_test_files else 0
        else:
            test_count = _parse_test_collection_output(result.stdout, has_test_files)
        logger.info("Collected %d tests", test_count)
        return test_count
    return default_test_count if has_test_files else 0


def _get_xdist_available() -> bool:
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    else:
        return True


def _get_pytest_args(validated_args: list[str], num_workers: int) -> list[str]:
    args = validated_args.copy()
    if num_workers > 1:
        args.extend(["-n", str(num_workers)])
    return args


def run_pytest_with_workers(validated_args: list[str], num_workers: int) -> int:
    """Run pytest with the calculated number of workers."""
    xdist_available = _get_xdist_available()
    args = _get_pytest_args(validated_args, num_workers if xdist_available else 1)
    pytest_cmd = [sys.executable, "-m", "pytest"]
    pytest_cmd.extend(args)
    logger.info("Running pytest with command: %s", " ".join(pytest_cmd))
    try:
        result = _safe_subprocess_run(
            pytest_cmd,
            shell=False,
            env=get_sanitized_env(),
            timeout=3600,
            capture_output=True,
            check=False,  # Explicitly set check
        )
        if result.returncode not in [0, 1, 2, 3, 4, 5]:
            logger.warning(
                "Pytest exited with unexpected return code: %d", result.returncode
            )
            if result.stdout:
                logger.info("Pytest stdout: %s", result.stdout)
            if result.stderr:
                logger.error("Pytest stderr: %s", result.stderr)
    except subprocess.TimeoutExpired:
        logger.exception("Pytest execution timed out after 1 hour")
        return 2
    except subprocess.SubprocessError:
        logger.exception("Error running pytest")
        return 1
    except (OSError, FileNotFoundError):
        logger.exception("Unexpected error running pytest")
        return 1
    else:
        return result.returncode


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    This is needed for bandit and other security tools to write their reports.
    Returns silently if the directory already exists or was created successfully.
    Logs a warning if the directory could not be created but continues execution.
    """
    reports_dir = Path("security-reports")
    if _ensure_dir_exists(reports_dir, "security-reports"):
        return
    alt_reports_dir = Path("security_reports")
    if _ensure_dir_exists(alt_reports_dir, "alternative security_reports"):
        _try_create_symlink(alt_reports_dir, "security-reports")
        return
    import tempfile

    temp_dir = Path(tempfile.gettempdir()) / "security-reports"
    if _ensure_dir_exists(temp_dir, f"security-reports in temp location: {temp_dir}"):
        _try_create_symlink(temp_dir, "security-reports")
        return
    logger.warning(
        "Could not create any security-reports directory; continuing without it."
    )


def _ensure_dir_exists(path: Path, description: str) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.warning("Failed to create %s directory: %s", description, e)
        return False
    else:
        logger.info("Created %s directory", description)
        return True


def _try_create_symlink(target: Path, link_name: str) -> None:
    try:
        if platform.system() == "Windows":
            cmd_path = shutil.which("cmd.exe")
            if cmd_path:
                _safe_subprocess_run(
                    [
                        cmd_path,
                        "/c",
                        "mklink",
                        "/J",
                        link_name,
                        str(target),
                    ],
                    capture_output=True,
                    shell=False,
                    check=False,  # Explicitly set check
                )
        else:
            os.symlink(target, link_name)
    except OSError as symlink_error:
        logger.warning("Failed to create symlink to %s: %s", target, symlink_error)


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
            venv_path = Path(venv_dir)
            if venv_path.is_dir() and (venv_path / "pyvenv.cfg").is_file():
                return True
    except (OSError, AttributeError) as e:
        # If any error occurs, log it but assume we're not in a virtual environment
        logger.warning("Error checking for virtual environment: %s", e)
    else:
        # Not in a virtual environment
        return False
    return False


def _safe_subprocess_run(
    cmd: list[str],
    **kwargs: Any,  # noqa: ANN401
) -> subprocess.CompletedProcess[str]:
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    if "cwd" in kwargs and isinstance(kwargs["cwd"], Path):
        kwargs["cwd"] = str(kwargs["cwd"])
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return subprocess.run(cmd, check=False, **filtered_kwargs)  # type: ignore[return-value]  # noqa: S603


def ensure_pytest_xdist_installed() -> None:
    """Ensure pytest-xdist is installed, install if missing."""
    try:
        check_result = _safe_subprocess_run(
            [sys.executable, "-c", "import pytest_xdist"],
            capture_output=True,
            shell=False,
        )
        if check_result.returncode == 0:
            logger.info("pytest-xdist is already installed")
            return
        logger.info("Installing pytest-xdist...")
        use_uv = False
        try:
            uv_path = shutil.which("uv") or "uv"
            uv_check = _safe_subprocess_run(
                [uv_path, "--version"],
                capture_output=True,
                shell=False,
            )
            use_uv = uv_check.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            use_uv = False
        if use_uv:
            logger.info("Using uv to install pytest-xdist")
            install_cmd = ["uv", "pip", "install", "pytest-xdist"]
        else:
            logger.info("Using pip to install pytest-xdist")
            install_cmd = [sys.executable, "-m", "pip", "install", "pytest-xdist"]
        install_result = _safe_subprocess_run(
            install_cmd,
            capture_output=True,
            shell=False,
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
                    install_result.stderr,
                )
    except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
        logger.warning(
            "Error checking for pytest-xdist: %s. Will run tests without parallelization.",
            e,
        )
    except (OSError, FileNotFoundError) as e:
        logger.warning(
            "Unexpected error installing pytest-xdist: %s. Will run tests without parallelization.",
            e,
        )


def main() -> None:
    """
    Run the test suite with optimized worker count.

    Validates command line arguments, counts tests, and runs pytest with the
    appropriate number of workers.
    """
    if os.environ.get("SKIP_VENV_CHECK") == "1":
        logger.info("Skipping virtual environment check")
    else:
        in_venv = check_venv_exists()
        if not in_venv:
            logger.warning(
                "Not running in a virtual environment. This may cause issues with pytest."
            )
            logger.info(
                "Continuing anyway, but consider running in a virtual environment."
            )
            if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
                logger.info(
                    "CI environment detected. Will proceed without virtual environment."
                )
    ensure_pytest_xdist_installed()
    ensure_security_reports_dir()
    validated_args = validate_args(sys.argv[1:])
    test_count = count_tests(validated_args)
    num_workers = MAX_WORKERS if test_count > THRESHOLD else 1
    logger.info(
        "Collected %d tests. Using %d worker%s",
        test_count,
        num_workers,
        "s" if num_workers > 1 else "",
    )
    exit_code = run_pytest_with_workers(validated_args, num_workers)
    sys.exit(exit_code)


if __name__ == "__main__":
    # Set CI environment variable if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS"):
        os.environ["CI"] = "1"
        logger.info("GitHub Actions environment detected")

    # Skip virtual environment check by setting a flag
    os.environ["SKIP_VENV_CHECK"] = "1"

    main()
