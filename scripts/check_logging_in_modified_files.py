#!/usr/bin/env python
"""
Script to check for proper logger usage in modified files.

This script is designed to be used as a pre-commit hook to check only the
modified files for proper logger usage. It uses the logger initialization
checker but focuses only on the files that have been modified in the current
Git commit.

Usage:
    python scripts/check_logging_in_modified_files.py [--fix] [--verbose]

Arguments:
    --fix       Attempt to fix issues automatically
    --verbose   Show detailed output

"""

import argparse
import logging
import os
import subprocess
import sys
from typing import List, Set, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Import the logger initialization checker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.check_logger_initialization import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_FILES,
    DEFAULT_EXCLUDE_PATTERNS,
    LoggerIssue,
    check_file,
    fix_file,
)

# Configure logging
# logging.basicConfig will be moved to the main() function


def get_modified_files() -> List[str]:
    """
    Get the list of modified Python files in the current Git commit.

    Returns:
        List of modified Python file paths

    """
    try:
        # Get staged files
        staged_cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
        staged_output = subprocess.check_output(staged_cmd, universal_newlines=True)
        staged_files = staged_output.splitlines()

        # Get unstaged files
        unstaged_cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR"]
        unstaged_output = subprocess.check_output(unstaged_cmd, universal_newlines=True)
        unstaged_files = unstaged_output.splitlines()

        # Get untracked files
        untracked_cmd = ["git", "ls-files", "--others", "--exclude-standard"]
        untracked_output = subprocess.check_output(untracked_cmd, universal_newlines=True)
        untracked_files = untracked_output.splitlines()

        # Combine all files
        all_files = set(staged_files + unstaged_files + untracked_files)

        # Filter for Python files
        python_files = [f for f in all_files if f.endswith(".py")]

        return python_files
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error getting modified files: {e}")
        return []


def should_check_file(file_path: str, exclude_dirs: Set[str], exclude_files: Set[str], exclude_patterns: List[str]) -> bool:
    """
    Check if a file should be checked.

    Args:
        file_path: Path to the file
        exclude_dirs: Set of directory names to exclude
        exclude_files: Set of file names to exclude
        exclude_patterns: List of file name patterns to exclude

    Returns:
        True if the file should be checked, False otherwise

    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        return False

    # Check if the file is in an excluded directory
    for exclude_dir in exclude_dirs:
        if exclude_dir in file_path.split(os.path.sep):
            return False

    # Check if the file is excluded
    if os.path.basename(file_path) in exclude_files:
        return False

    # Check if the file matches an excluded pattern
    import re
    for pattern in exclude_patterns:
        if re.match(pattern, os.path.basename(file_path)):
            return False

    return True


def check_modified_files(fix: bool = False, verbose: bool = False) -> Tuple[List[LoggerIssue], int]:
    """
    Check modified files for logger initialization issues.

    Args:
        fix: Whether to fix issues automatically
        verbose: Whether to show detailed output

    Returns:
        Tuple of (list of issues found, number of files fixed)

    """
    modified_files = get_modified_files()
    if verbose:
        logger.info(f"Found {len(modified_files)} modified Python files")

    exclude_dirs = DEFAULT_EXCLUDE_DIRS
    exclude_files = DEFAULT_EXCLUDE_FILES
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    all_issues = []
    fixed_count = 0

    for file_path in modified_files:
        if should_check_file(file_path, exclude_dirs, exclude_files, exclude_patterns):
            if verbose:
                logger.info(f"Checking {file_path}")

            file_issues = check_file(file_path)
            all_issues.extend(file_issues)

            if fix and any(issue.fixable for issue in file_issues):
                if fix_file(file_path, file_issues):
                    fixed_count += 1
                    if verbose:
                        logger.info(f"Fixed {file_path}")

    return all_issues, fixed_count


def main() -> int:
    """
    Main function.

    Returns:
        Exit code (0 for success, non-zero for failure)

    """
    # Configure logging early in main
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    parser = argparse.ArgumentParser(description="Check for proper logger usage in modified files")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues automatically")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    all_issues, fixed_count = check_modified_files(args.fix, args.verbose)

    # Group issues by file
    from collections import defaultdict

# Configure logging


# Configure logging


# Configure logging


# Configure logging



# Configure logging
    issues_by_file = defaultdict(list)

    for issue in all_issues:
        issues_by_file[issue.file_path].append(issue)

    # Print issues
    for file_path, file_issues in issues_by_file.items():
        print(f"\n{file_path}:")
        for issue in file_issues:
            print(f"  Line {issue.line_number}: {issue.issue_type}: {issue.message}")

    # Print summary
    print(f"\nFound {len(all_issues)} issues in {len(issues_by_file)} files")
    if args.fix:
        print(f"Fixed {fixed_count} files")

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
