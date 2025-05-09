"""Script to format all Python files in the scripts directory."""

import os
import subprocess
import sys


def run_command(command):
    """Run a command and return the exit code, stdout, and stderr."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=sys.platform == "win32",
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return 1, "", str(e)


def format_file(file_path):
    """Format a Python file using Black and Ruff."""
    print(f"Formatting {file_path}...")

    # Run Black
    black_cmd = ["black", file_path]
    black_code, black_stdout, black_stderr = run_command(black_cmd)
    if black_code != 0:
        print(f"Black failed on {file_path}: {black_stderr}")
    else:
        print(f"Black succeeded on {file_path}")

    # Run Ruff format
    ruff_format_cmd = ["ruff", "format", file_path]
    ruff_format_code, ruff_format_stdout, ruff_format_stderr = run_command(
        ruff_format_cmd
    )
    if ruff_format_code != 0:
        print(f"Ruff format failed on {file_path}: {ruff_format_stderr}")
    else:
        print(f"Ruff format succeeded on {file_path}")

    # Run Ruff check with fixes
    ruff_check_cmd = ["ruff", "check", "--fix", file_path]
    ruff_check_code, ruff_check_stdout, ruff_check_stderr = run_command(ruff_check_cmd)
    if ruff_check_code != 0:
        print(f"Ruff check failed on {file_path}: {ruff_check_stderr}")
    else:
        print(f"Ruff check succeeded on {file_path}")

    return black_code == 0 and ruff_format_code == 0 and ruff_check_code == 0


def main():
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
            print(f"File not found: {file_path}")
            failed_files.append(file_path)

    print(f"\nFormatting complete. {success_count} files formatted successfully.")

    if failed_files:
        print(f"{len(failed_files)} files failed formatting:")
        for file in failed_files:
            print(f"  - {file}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
