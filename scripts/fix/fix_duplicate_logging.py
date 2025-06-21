#!/usr/bin/env python3
"""
Fix duplicate logging messages and improve logging practices.

This script analyzes Python files for duplicate and redundant logging messages,
especially those that might leak sensitive information.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Patterns for problematic logging
PROBLEMATIC_PATTERNS = [
    # Duplicate log messages with similar content
    (r"logger\.\w+\([^)]*\)\s+logger\.\w+\([^)]*\)", "Duplicate log messages"),
    # Passing sensitive data directly to log messages
    (
        r'logger\.\w+\(f?["\'].*\b(password|token|secret|key|credential)\b.*?["\']',
        "Sensitive data in log message",
    ),
    # Logging exceptions with parameters
    (r"logger\.exception\(.*?,\s*\w+\)", "Exception with parameters"),
]

# Safe logging replacements
SAFE_REPLACEMENTS = {
    # Replace direct string logging with extra dict
    r'logger\.(\w+)\(f?"([^"]*){([^}]+)}"(.*)\)': r'logger.\1("\2", extra={"\3": \3}\4)',
    r"logger\.(\w+)\(f'([^']*){([^}]+)}'(.*)\)": r"logger.\1('\2', extra={'\3': \3}\4)",
    # Replace duplicate log patterns
    r"(logger\.\w+\([^)]*\))\s+logger\.\w+\([^)]*similar[^)]*\)": r"\1",
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fix duplicate logging messages and improve logging practices"
    )

    parser.add_argument(
        "--file", "-f", type=str, help="Path to a specific Python file to fix"
    )

    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=".",
        help="Directory to scan for Python files (default: current directory)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--check",
        "-c",
        action="store_true",
        help="Check mode - don't modify files, just report issues",
    )

    return parser.parse_args()


def find_python_files(directory: str) -> list[str]:
    """Find all Python files in a directory recursively."""
    python_files = []
    directory_path = Path(directory)

    for python_file in directory_path.rglob("*.py"):
        # Skip virtual environments and other common excludes
        if any(
            excluded in str(python_file)
            for excluded in [".venv", "venv", "__pycache__", "node_modules"]
        ):
            continue
        python_files.append(str(python_file))

    return python_files


def fix_duplicate_logs(
    file_path: str,
    check_only: bool = False,
) -> tuple[int, int]:
    """
    Fix duplicate and problematic logging in the file.

    Args:
        file_path: Path to the Python file
        check_only: Whether to check without modifying

    Returns:
        Tuple of (fixed_issues, total_issues)

    """
    try:
        # Read the file content
        file_path_obj = Path(file_path)
        with file_path_obj.open(encoding="utf-8") as f:
            content = f.read()

        # Find problematic patterns
        issues_found = []
        for pattern, issue_type in PROBLEMATIC_PATTERNS:
            issues_found.extend(
                (match.start(), match.end(), issue_type)
                for match in re.finditer(pattern, content)
            )

        if not issues_found:
            return 0, 0

        # Apply fixes if not in check mode
        if check_only:
            return 0, len(issues_found)

        # Make replacements
        updated_content = content
        for pattern, replacement in SAFE_REPLACEMENTS.items():
            updated_content = re.sub(pattern, replacement, updated_content)

        # Write the modified content back to file if changes were made
        if updated_content != content:
            with file_path_obj.open("w", encoding="utf-8") as f:
                f.write(updated_content)
            return len(issues_found), len(issues_found)

        return 0, len(issues_found)

    except Exception:
        logger.exception("Error processing %s", file_path)
        return 0, 0


def main() -> int:
    """Run the main function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    fixed_count = 0
    issue_count = 0

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error("File does not exist: %s", args.file)
            return 1

        if not args.file.endswith(".py"):
            logger.error("Not a Python file")
            return 1

        fixed, issues = fix_duplicate_logs(args.file, args.check)
        fixed_count += fixed
        issue_count += issues

        logger.info("Fixed %d/%d logging issues in %s", fixed, issues, args.file)
    else:
        directory_path = Path(args.directory)
        if not directory_path.exists():
            logger.error("Directory does not exist: %s", args.directory)
            return 1

        python_files = find_python_files(args.directory)
        logger.info("Found %d Python files to check", len(python_files))

        for file_path in python_files:
            fixed, issues = fix_duplicate_logs(file_path, args.check)
            fixed_count += fixed
            issue_count += issues

            if issues > 0:
                logger.info(
                    "Fixed %d/%d logging issues in %s", fixed, issues, file_path
                )

    if args.check:
        logger.info(
            "Found %d logging issues in total (check mode, no fixes applied)",
            issue_count,
        )
    else:
        logger.info("Fixed %d/%d logging issues in total", fixed_count, issue_count)

    return 0


if __name__ == "__main__":
    sys.exit(main())
