"""Script to format all Python files in the scripts directory."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging
logger = logging.getLogger(__name__)


# Use built-in types for type annotations

# Set up a dedicated logger for this module


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr."""
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
        # Use a separate variable to avoid TRY300 issue
        result_code = result.returncode
        result_stdout = result.stdout
        result_stderr = result.stderr
    except Exception as e:
        logger.exception("Error running command %s", " ".join(command))
        return 1, "", str(e)
    else:
        # Return the results
        return result_code, result_stdout, result_stderr


def format_file(file_path: str) -> bool:
    """Format a Python file using Ruff."""
    logger.info("Formatting %s...", file_path)

    # Run Ruff format
    ruff_format_cmd = ["ruff", "format", file_path]
    ruff_format_code, ruff_format_stdout, ruff_format_stderr = run_command(
        ruff_format_cmd
    )
    if ruff_format_code != 0:
        logger.error("Ruff format failed on %s: %s", file_path, ruff_format_stderr)
    else:
        logger.info("Ruff format succeeded on %s", file_path)

    # Run Ruff check with fixes
    ruff_check_cmd = ["ruff", "check", "--fix", file_path]
    ruff_check_code, ruff_check_stdout, ruff_check_stderr = run_command(ruff_check_cmd)
    if ruff_check_code != 0:
        logger.error("Ruff check failed on %s: %s", file_path, ruff_check_stderr)
    else:
        logger.info("Ruff check succeeded on %s", file_path)

    return ruff_format_code == 0 and ruff_check_code == 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    """Format all Python files in the scripts directory."""
    script_files = [
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

    success_count = 0
    failed_files = []

    for file_path in script_files:
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
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
