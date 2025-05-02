#!/usr/bin/env python
"""
Script to run linting checks on Python files.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, file_path):
    """Run a command and return the result."""
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ {' '.join(command)} passed for {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {' '.join(command)} failed for {file_path}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False


def lint_file(file_path):
    """Run linting checks on a file."""
    print(f"\nLinting {file_path}...")

    # Check for syntax errors and undefined names
    flake8_result = run_command(
        [
            "flake8",
            file_path,
            "--count",
            "--select=E9,F63,F7,F82",
            "--show-source",
            "--statistics",
        ],
        file_path,
    )

    # Check formatting with Black
    black_result = run_command(
        ["black", "--check", file_path],
        file_path,
    )

    # Check import sorting with isort
    isort_result = run_command(
        ["isort", "--check-only", "--profile", "black", file_path],
        file_path,
    )

    # Check with Ruff
    ruff_result = run_command(
        ["ruff", "check", file_path],
        file_path,
    )

    return all([flake8_result, black_result, isort_result, ruff_result])


def process_directory(directory, file_patterns=None):
    """Process all Python files in a directory and its subdirectories."""
    all_passed = True

    if file_patterns:
        # Process specific files/patterns
        for pattern in file_patterns:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file() and file_path.suffix == ".py":
                    if not lint_file(str(file_path)):
                        all_passed = False
    else:
        # Process all Python files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if not lint_file(file_path):
                        all_passed = False

    return all_passed


def main():
    """Main function to parse args and run the script."""
    parser = argparse.ArgumentParser(description="Run linting checks on Python files.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a file or directory to lint (default: current directory)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific file patterns to lint (e.g., '*.py' 'src/*.py')",
    )

    args = parser.parse_args()

    if os.path.isfile(args.path):
        # Lint a single file
        success = lint_file(args.path)
    else:
        # Lint a directory
        success = process_directory(args.path, args.files)

    if success:
        print("\n✅ All linting checks passed!")
        return 0
    else:
        print("\n❌ Some linting checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
