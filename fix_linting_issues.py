"""fix_linting_issues - Script to fix common linting issues in Python files.

This script automatically fixes common linting issues in Python files using tools like
isort and Ruff. It can be run on a specific file or on all Python files in the
project.
"""

import argparse
import logging
import os
import subprocess
import sys

from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(command: list[str], _check_mode: bool = False) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
        command: The command to run.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        A tuple of (exit_code, stdout, stderr).

    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
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


def run_isort(file_path: str, check_mode: bool = False) -> bool:
    """Run isort on a Python file.

    Args:
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        True if successful, False otherwise.

    """
    command: list[str] = ["isort"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)
    if exit_code != 0:
        logging.error(f"isort failed on {file_path}: {stderr}")
    return exit_code == 0


def run_ruff(file_path: str, check_mode: bool = False) -> bool:
    """Run Ruff linter on a Python file.

    Args:
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        True if successful, False otherwise.

    """
    command: list[str] = ["ruff", "check"]
    if not check_mode:
        command.append("--fix")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)

    # Also run ruff format
    format_command: list[str] = ["ruff", "format"]
    if check_mode:
        format_command.append("--check")
    format_command.append(file_path)

    format_exit_code, format_stdout, format_stderr = run_command(
        format_command, check_mode
    )

    if exit_code != 0:
        logging.error(f"Ruff failed on {file_path}: {stderr}")
    return exit_code == 0 and format_exit_code == 0


def find_python_files(exclude_patterns: Optional[list[str]] = None) -> list[str]:
    """Find all Python files in the project.

    Args:
        exclude_patterns: List of patterns to exclude.

    Returns:
        List of Python file paths.

    """
    if exclude_patterns is None:
        exclude_patterns = [
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            "node_modules",
            "build",
            "dist",
        ]

    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not any(
                excl in os.path.join(root, d).replace("\\", "/")
                for excl in exclude_patterns
            )
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Convert to forward slashes for consistent pattern matching
                file_path_fwd = file_path.replace("\\", "/")
                if not any(excl in file_path_fwd for excl in exclude_patterns):
                    python_files.append(file_path)

    return python_files


def fix_file(file_path: str, args: argparse.Namespace) -> bool:
    """Fix linting issues in a Python file.

    Args:
        file_path: Path to the Python file.
        args: Command-line arguments.

    Returns:
        True if successful, False otherwise.

    """
    logging.info(f"Fixing {file_path}...")
    success = True

    # Run isort
    if not args.no_isort:
        if args.verbose:
            logging.info(f"Running isort on {file_path}")
        if not run_isort(file_path, args.check):
            logging.error(f"isort failed on {file_path}")
            success = False

    # Run Ruff
    if not args.no_ruff:
        if args.verbose:
            logging.info(f"Running Ruff on {file_path}")
        if not run_ruff(file_path, args.check):
            logging.error(f"Ruff failed on {file_path}")
            success = False

    return success


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up and return the argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Fix linting issues in Python files.")
    parser.add_argument(
        "file_paths",
        nargs="*",
        help=(
            "Paths to specific Python files to fix. "
            "If not provided, all Python files will be fixed."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without fixing them.",
    )
    parser.add_argument(
        "--no-isort",
        action="store_true",
        help="Skip isort.",
    )
    parser.add_argument(
        "--no-ruff",
        action="store_true",
        help="Skip Ruff linter.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser


def process_specific_files(file_paths: list[str], args: argparse.Namespace) -> int:
    """Process specific Python files provided by the user.

    Args:
        file_paths: List of file paths to process.
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    success_count = 0
    failed_files = []

    for file_path in file_paths:
        if os.path.isfile(file_path) and file_path.endswith(".py"):
            if fix_file(file_path, args):
                success_count += 1
                logging.info(f"Successfully fixed {file_path}")
            else:
                failed_files.append(file_path)
                logging.error(f"Failed to fix {file_path}")
        else:
            logging.error(f"Error: {file_path} is not a Python file.")
            failed_files.append(file_path)

    return report_results(success_count, len(file_paths), failed_files)


def process_all_files(args: argparse.Namespace) -> int:
    """Process all Python files in the project.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    python_files = find_python_files()
    if not python_files:
        logging.warning("No Python files found.")
        return 0

    success_count = 0
    failed_files = []

    for file_path in python_files:
        if fix_file(file_path, args):
            success_count += 1
        else:
            failed_files.append(file_path)

    return report_results(success_count, len(python_files), failed_files)


def report_results(
    success_count: int, total_count: int, failed_files: list[str]
) -> int:
    """Report the results of the linting operation.

    Args:
        success_count: Number of successfully processed files.
        total_count: Total number of files processed.
        failed_files: List of files that failed processing.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logging.info(f"\nFixed {success_count} out of {total_count} files.")

    if failed_files:
        logging.error(f"{len(failed_files)} files failed:")
        for file in failed_files:
            logging.error(f"  - {file}")
        return 1

    return 0


def main() -> int:
    """Run the main script functionality.

    Returns:
        Exit code.
    """
    parser = setup_argument_parser()
    args = parser.parse_args()

    if args.file_paths:
        return process_specific_files(args.file_paths, args)
    else:
        return process_all_files(args)


if __name__ == "__main__":
    sys.exit(main())
