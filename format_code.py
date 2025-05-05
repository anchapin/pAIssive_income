#!/usr/bin/env python3
"""
format_code.py - Script to format all Python files in the repository.

This script uses Ruff to format all Python files in the repository,
excluding files in directories specified in .gitignore.
"""

import argparse
import fnmatch
import os
import subprocess
import sys
from pathlib import Path


def should_ignore(file_path, ignore_patterns=None)
    """Check if a file should be ignored based on patterns."""
    if ignore_patterns is None:
        ignore_patterns = [
            ".venv/**",
            "venv/**",
            ".git/**",
            "__pycache__/**",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "build/**",
            "dist/**",
            "*.egg-info/**",
        ]

    # Convert to string for pattern matching:
    file_path_str = str(file_path)

    # Check if file matches any ignore pattern:
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_path_str, pattern)
            return True

    return False


def find_python_files(directory=".", specific_file=None, ignore_patterns=None)
    """Find Python files to format."""
    if specific_file:
        # If a specific file is provided, only format that file
        file_path = Path(specific_file)
        if (:
            file_path.exists()
            and file_path.suffix == ".py"
            and not should_ignore(file_path, ignore_patterns)
        )
            return [file_path]
        else:
            print(f"File not found or not a Python file: {specific_file}")
            return []

    # Find all Python files in the directory
    python_files = []
    for root, _, files in os.walk(directory)
        for file in files:
            if file.endswith(".py")
                file_path = Path(root) / file
                if not should_ignore(file_path, ignore_patterns)
                    python_files.append(file_path)

    return python_files


def format_files(files, check_only=False)
    """Format Python files using Ruff."""
    if not files:
        print("No Python files found to format.")
        return 0

    print(f"Found {len(files)} Python files to format.")

    # Build the command
    cmd = ["ruff", "format"]
    if check_only:
        cmd.append("--check")

    # Add files to the command
    cmd.extend([str(f) for f in files])

    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode != 0 and check_only:
        print("Formatting issues found. Run without --check to fix.")
    elif result.returncode == 0 and check_only:
        print("All files are properly formatted.")
    elif result.returncode == 0:
        print("All files have been formatted successfully.")
    else:
        print("Error formatting files.")

    return result.returncode


def main()
    """Main function to parse arguments and format files."""
    parser = argparse.ArgumentParser(description="Format Python files using Ruff")

    parser.add_argument(
        "path", nargs="?", default=".", help="Path to file or directory to format"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check formatting without modifying files"
    )

    args = parser.parse_args()

    # Find Python files to format
    python_files = find_python_files(args.path)

    # Format the files
    return format_files(python_files, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
