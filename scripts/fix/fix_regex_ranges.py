#!/usr/bin/env python3
"""Script to find and fix overly permissive regular expression ranges.

This script scans Python files for regular expressions with overly permissive
character ranges like [A-Za-z] and replaces them with safer alternatives like [A-Za-z].
"""

import logging
import os
import re
import sys

# Import typing annotations

# Constants
MIN_ARGS = 2  # Program name + directory

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Patterns to search for
PROBLEMATIC_PATTERNS = [
    (r"\[A-z\]", r"[A-Za-z]"),  # [A-Za-z] -> [A-Za-z]
    (r"\[a-Z\]", r"[a-zA-Z]"),  # [a-zA-Z] -> [a-zA-Z]
    (r"\[0-z\]", r"[0-9A-Za-z]"),  # [0-9A-Za-z] -> [0-9A-Za-z]
    (r"\[0-Z\]", r"[0-9A-Z]"),  # [0-9A-Z] -> [0-9A-Z]
    (r"\[A-9\]", r"[0-9A-Z]"),  # [0-9A-Z] -> [0-9A-Z]
    (r"\[a-9\]", r"[0-9a-z]"),  # [0-9a-z] -> [0-9a-z]
]

# Directories to exclude
EXCLUDE_DIRS = [".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist"]


def find_python_files(directory: str) -> list[str]:
    """Find all Python files in the given directory and its subdirectories.

    Args:
    ----
        directory: The directory to search in

    Returns:
    -------
        A list of paths to Python files

    """
    python_files = []

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def check_file(file_path: str) -> list[tuple[int, str, str, str]]:
    """Check a file for problematic regex patterns.

    Args:
    ----
        file_path: Path to the file to check

    Returns:
    -------
        A list of tuples (line_number, line, problematic_pattern, replacement)

    """
    issues = []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        for pattern, replacement in PROBLEMATIC_PATTERNS:
            if re.search(pattern, line):
                issues.append((i + 1, line, pattern, replacement))

    return issues


def fix_file(file_path: str, dry_run: bool = False) -> list[tuple[int, str, str]]:
    """Fix problematic regex patterns in a file.

    Args:
    ----
        file_path: Path to the file to fix
        dry_run: If True, don't actually modify the file

    Returns:
    -------
        A list of tuples (line_number, old_line, new_line) describing the changes made

    """
    changes = []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    for i, line in enumerate(lines):
        new_line = line
        for pattern, replacement in PROBLEMATIC_PATTERNS:
            if re.search(pattern, new_line):
                new_line = re.sub(pattern, replacement, new_line)
                modified = True

        if new_line != line:
            changes.append((i + 1, line.rstrip(), new_line.rstrip()))
            lines[i] = new_line

    if modified and not dry_run:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return changes


def main() -> None:
    """Run the main script functionality."""
    if len(sys.argv) < MIN_ARGS:
        logging.error(f"Usage: {sys.argv[0]} <directory> [--dry-run]")
        sys.exit(1)

    directory = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.isdir(directory):
        logging.error(f"Error: {directory} is not a directory")
        sys.exit(1)

    python_files = find_python_files(directory)
    logging.info(f"Found {len(python_files)} Python files")

    total_issues = 0
    total_files_with_issues = 0

    for file_path in python_files:
        issues = check_file(file_path)

        if issues:
            total_issues += len(issues)
            total_files_with_issues += 1

            logging.info(f"\nIssues in {file_path}:")
            for line_number, line, pattern, replacement in issues:
                logging.info(f"  Line {line_number}: {pattern} -> {replacement}")
                logging.info(f"    {line.strip()}")

            changes = fix_file(file_path, dry_run)

            if changes:
                logging.info("\n  Changes:")
                for line_number, old_line, new_line in changes:
                    logging.info(f"    Line {line_number}:")
                    logging.info(f"      - {old_line}")
                    logging.info(f"      + {new_line}")

    logging.info(f"\nFound {total_issues} issues in {total_files_with_issues} files")
    if dry_run:
        logging.info("Dry run - no files were modified")
    else:
        logging.info(f"Fixed {total_issues} issues in {total_files_with_issues} files")


if __name__ == "__main__":
    main()
