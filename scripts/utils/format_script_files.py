"""Script to format all Python files in the scripts directory."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Final, Literal, NoReturn, Sequence, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Type aliases and constants
ExitCode = Literal[0, 1]
CommandOutput = Tuple[ExitCode, str, str]  # (exit_code, stdout, stderr)

RUFF_FORMAT_CMD: Final[str] = "ruff"
RUFF_FORMAT_ACTION: Final[str] = "format"
RUFF_CHECK_ACTION: Final[str] = "check"
RUFF_FIX_FLAG: Final[str] = "--fix"

SUCCESS_CODE: Final[ExitCode] = 0
ERROR_CODE: Final[ExitCode] = 1


def run_command(command: Sequence[str]) -> CommandOutput:
    """
    Run a command and return the exit code, stdout, and stderr.

    Args:
        command: The command to run as a sequence of strings

    Returns:
        A tuple containing (exit_code, stdout, stderr)

    """
    try:
        # Always use shell=False for security
        # nosec comment below tells security scanners this is safe as we control the input
        result = subprocess.run(  # nosec B603 S603
            command,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        # Use separate variables to avoid TRY300 issue
        result_code: ExitCode = SUCCESS_CODE if result.returncode == 0 else ERROR_CODE
        result_stdout: str = result.stdout if result.stdout is not None else ""
        result_stderr: str = result.stderr if result.stderr is not None else ""
    except Exception as e:
        logger.exception("Error running command %s", " ".join(command))
        return ERROR_CODE, "", str(e)
    else:
        # Return the results
        return result_code, result_stdout, result_stderr


def format_file(file_path: str | Path) -> bool:
    """
    Format a Python file using Ruff.

    Args:
        file_path: Path to the Python file to format

    Returns:
        True if both format and check operations succeeded, False otherwise

    """
    logger.info("Formatting %s...", file_path)

    # Convert path to string if it's a Path object
    path_str = str(file_path)

    # Run Ruff format
    ruff_format_cmd = [RUFF_FORMAT_CMD, RUFF_FORMAT_ACTION, path_str]
    ruff_format_code, ruff_format_stdout, ruff_format_stderr = run_command(
        ruff_format_cmd
    )
    if ruff_format_code != SUCCESS_CODE:
        logger.error("Ruff format failed on %s: %s", path_str, ruff_format_stderr)
    else:
        logger.info("Ruff format succeeded on %s", path_str)

    # Run Ruff check with fixes
    ruff_check_cmd = [RUFF_FORMAT_CMD, RUFF_CHECK_ACTION, RUFF_FIX_FLAG, path_str]
    ruff_check_code, ruff_check_stdout, ruff_check_stderr = run_command(ruff_check_cmd)
    if ruff_check_code != SUCCESS_CODE:
        logger.error("Ruff check failed on %s: %s", path_str, ruff_check_stderr)
    else:
        logger.info("Ruff check succeeded on %s", path_str)

    return ruff_format_code == SUCCESS_CODE and ruff_check_code == SUCCESS_CODE


def main() -> ExitCode:
    """
    Format all Python files in the scripts directory.

    Returns:
        0 if all files were formatted successfully, 1 if any failed

    """
    # Define script files to format as constant
    SCRIPT_FILES: Final[list[str]] = [
        "scripts/debug_filtering.py",
        "scripts/run_webhook_tests.py",
        "scripts/missing_schemas.py",
        "scripts/service_initialization.py",
        "scripts/run_basic_integration_tests.py",
        "scripts/setup_pre_commit.py",
        "scripts/run_dashboard.py",
        "scripts/run_data_consistency_tests.py",
        "scripts/run_github_actions_locally.py",
        "scripts/run_integration_tests.py",
        "scripts/run_integration_tests_standalone.py",
        "scripts/run_linting.py",
        "scripts/run_local_tests.py",
        "scripts/run_microservices.py",
        "scripts/run_security_tests.py",
        "scripts/dependency_container.py",
        "scripts/run_security_tests_advanced.py",
        "scripts/fix_test_collection_warnings.py",
        "scripts/run_security_tests_standalone.py",
        "scripts/format_code.py",
        "scripts/run_webhook_performance_tests.py",
        "scripts/format_files.py",
        "scripts/sues.py",
    ]

    success_count: int = 0
    failed_files: list[str] = []

    for file_path in SCRIPT_FILES:
        if Path(file_path).exists():
            if format_file(file_path):
                success_count += 1
            else:
                failed_files.append(file_path)
        else:
            logger.warning("File not found: %s", file_path)
            failed_files.append(file_path)

    logger.info(
        "\nFormatting complete. %d files formatted successfully.", success_count
    )

    if failed_files:
        logger.warning("Failed to format files: %s", failed_files)
        return ERROR_CODE

    return SUCCESS_CODE


def _raise_sys_exit(code: ExitCode) -> NoReturn:
    """
    Raise SystemExit with the given code.

    Args:
        code: Exit code to raise

    Raises:
        SystemExit: Always

    """
    raise SystemExit(code)


if __name__ == "__main__":
    _raise_sys_exit(main())
