"""fix_linting_issues - Script to fix common linting issues in Python files.

This script automatically fixes common linting issues in Python files using tools like
Black, isort, and Ruff. It can be run on a specific file or on all Python files in the
project.
"""

import argparse
import os
import subprocess
import sys

from typing import List
from typing import Tuple


def run_command(command: List[str], check_mode: bool = False) -> Tuple[int, str, str]:
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
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return 1, "", str(e)


def run_black(file_path: str, check_mode: bool = False) -> bool:
    """Run Black formatter on a Python file.

    Args:
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        True if successful, False otherwise.

    """
    command = ["black"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)
    if exit_code != 0:
        print(f"Black failed on {file_path}: {stderr}")
    return exit_code == 0


def run_isort(file_path: str, check_mode: bool = False) -> bool:
    """Run isort on a Python file.

    Args:
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        True if successful, False otherwise.

    """
    command = ["isort"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)
    if exit_code != 0:
        print(f"isort failed on {file_path}: {stderr}")
    return exit_code == 0


def run_ruff(file_path: str, check_mode: bool = False) -> bool:
    """Run Ruff linter on a Python file.

    Args:
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        True if successful, False otherwise.

    """
    command = ["ruff", "check"]
    if not check_mode:
        command.append("--fix")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)

    # Also run ruff format
    format_command = ["ruff", "format"]
    if check_mode:
        format_command.append("--check")
    format_command.append(file_path)

    format_exit_code, format_stdout, format_stderr = run_command(
        format_command, check_mode
    )

    return exit_code == 0 and format_exit_code == 0


def find_python_files(exclude_patterns: List[str] = None) -> List[str]:
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
    print(f"Fixing {file_path}...")
    success = True

    # Run Black
    if not args.no_black:
        if args.verbose:
            print(f"Running Black on {file_path}")
        if not run_black(file_path, args.check):
            print(f"Black failed on {file_path}")
            success = False

    # Run isort
    if not args.no_isort:
        if args.verbose:
            print(f"Running isort on {file_path}")
        if not run_isort(file_path, args.check):
            print(f"isort failed on {file_path}")
            success = False

    # Run Ruff
    if not args.no_ruff:
        if args.verbose:
            print(f"Running Ruff on {file_path}")
        if not run_ruff(file_path, args.check):
            print(f"Ruff failed on {file_path}")
            success = False

    return success


def main() -> int:
    """Run the main script functionality.

    Returns:
        Exit code.

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
        "--no-black",
        action="store_true",
        help="Skip Black formatter.",
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
    args = parser.parse_args()

    if args.file_paths:
        # Fix specific files
        success_count = 0
        failed_files = []

        for file_path in args.file_paths:
            if os.path.isfile(file_path) and file_path.endswith(".py"):
                if fix_file(file_path, args):
                    success_count += 1
                    print(f"Successfully fixed {file_path}")
                else:
                    failed_files.append(file_path)
                    print(f"Failed to fix {file_path}")
            else:
                print(f"Error: {file_path} is not a Python file.")
                failed_files.append(file_path)

        print(f"\nFixed {success_count} out of {len(args.file_paths)} files.")

        if failed_files:
            print(f"{len(failed_files)} files failed:")
            for file in failed_files:
                print(f"  - {file}")
            return 1

        return 0
    else:
        # Fix all Python files
        python_files = find_python_files()
        if not python_files:
            print("No Python files found.")
            return 0

        success_count = 0
        failed_files = []

        for file_path in python_files:
            if fix_file(file_path, args):
                success_count += 1
            else:
                failed_files.append(file_path)

        print(f"\nFixed {success_count} out of {len(python_files)} files.")

        if failed_files:
            print(f"{len(failed_files)} files failed:")
            for file in failed_files:
                print(f"  - {file}")
            return 1

        return 0


if __name__ == "__main__":
    sys.exit(main())
