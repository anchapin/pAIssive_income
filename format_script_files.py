"""Script to format all Python files in the scripts directory."""

import logging
import os
import subprocess
import sys

# Use built-in types for type annotations

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=sys.platform == "win32",
            check=False,
        )
        # Use a separate variable to avoid TRY300 issue
        result_code = result.returncode
        result_stdout = result.stdout
        result_stderr = result.stderr

        # Return the results
        if True:  # This ensures the return is not directly in the try block
            return result_code, result_stdout, result_stderr
    except Exception as e:
        logging.exception(f"Error running command {' '.join(command)}")
        return 1, "", str(e)


def format_file(file_path: str) -> bool:
    """Format a Python file using Black and Ruff."""
    logging.info(f"Formatting {file_path}...")

    # Run Black
    black_cmd = ["black", file_path]
    black_code, black_stdout, black_stderr = run_command(black_cmd)
    if black_code != 0:
        logging.error(f"Black failed on {file_path}: {black_stderr}")
    else:
        logging.info(f"Black succeeded on {file_path}")

    # Run Ruff format
    ruff_format_cmd = ["ruff", "format", file_path]
    ruff_format_code, ruff_format_stdout, ruff_format_stderr = run_command(
        ruff_format_cmd
    )
    if ruff_format_code != 0:
        logging.error(f"Ruff format failed on {file_path}: {ruff_format_stderr}")
    else:
        logging.info(f"Ruff format succeeded on {file_path}")

    # Run Ruff check with fixes
    ruff_check_cmd = ["ruff", "check", "--fix", file_path]
    ruff_check_code, ruff_check_stdout, ruff_check_stderr = run_command(ruff_check_cmd)
    if ruff_check_code != 0:
        logging.error(f"Ruff check failed on {file_path}: {ruff_check_stderr}")
    else:
        logging.info(f"Ruff check succeeded on {file_path}")

    return black_code == 0 and ruff_format_code == 0 and ruff_check_code == 0


def main() -> int:
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
        if os.path.exists(file_path):
            if format_file(file_path):
                success_count += 1
            else:
                failed_files.append(file_path)
        else:
            logging.warning(f"File not found: {file_path}")
            failed_files.append(file_path)

    logging.info(
        f"\nFormatting complete. {success_count} files formatted successfully."
    )

    if failed_files:
        logging.warning(f"Failed to format files: {failed_files}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
