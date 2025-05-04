"""
run_tests.py - Script to run tests for the pAIssive Income project.

This script provides a convenient way to run tests with various options,
including running specific test files, test directories, or test methods.
It also includes options for formatting code and checking for linting issues.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_python_files(directory=".", ignore_patterns=None):
    """Find Python files to format or lint."""
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

    # Find all Python files in the directory
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                file_path_str = str(file_path)

                # Check if file should be ignored
                ignore_file = False
                for pattern in ignore_patterns:
                    if pattern.endswith("/**"):
                        # Directory pattern
                        dir_pattern = pattern[:-3]
                        if file_path_str.startswith(dir_pattern):
                            ignore_file = True
                            break
                    elif "*" in pattern:
                        # Wildcard pattern
                        import fnmatch

                        if fnmatch.fnmatch(file_path_str, pattern):
                            ignore_file = True
                            break

                if not ignore_file:
                    python_files.append(file_path)

    return python_files


def format_code(check_only=True):
    """Format Python files using Ruff."""
    python_files = find_python_files()

    if not python_files:
        print("No Python files found to format.")
        return 0

    print(f"Found {len(python_files)} Python files to format.")

    # Build the command
    cmd = ["ruff", "format"]
    if check_only:
        cmd.append("--check")
    cmd.append(".")

    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode != 0 and check_only:
        print("Formatting issues found. Run with --format to fix.")
    elif result.returncode == 0 and check_only:
        print("All files are properly formatted.")
    elif result.returncode == 0:
        print("All files have been formatted successfully.")
    else:
        print("Error formatting files.")

    return result.returncode


def lint_code():
    """Lint Python files using Ruff."""
    # Build the command
    cmd = ["ruff", "check", "."]

    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("Linting issues found.")
    else:
        print("All files pass linting checks.")

    return result.returncode


def run_tests(
    test_path=None,
    verbose=False,
    coverage=False,
    junit_xml=False,
    xvs=False,
    specific_test=None,
):
    """Run tests with pytest."""
    # Build the command
    cmd = ["pytest"]

    # Add test path if specified
    if test_path:
        cmd.append(test_path)

    # Add specific test if specified
    if specific_test:
        cmd.append(f"-k {specific_test}")

    # Add verbose flag if specified
    if verbose:
        cmd.append("-v")

    # Add coverage flag if specified
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])

    # Add JUnit XML flag if specified
    if junit_xml:
        cmd.append("--junitxml=test-results.xml")

    # Add xvs flag if specified
    if xvs:
        cmd.append("-xvs")

    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run tests for the pAIssive Income project"
    )

    parser.add_argument(
        "test_path", nargs="?", default=None, help="Path to test file or directory"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "--junit-xml", action="store_true", help="Generate JUnit XML report"
    )
    parser.add_argument(
        "--xvs",
        action="store_true",
        help="Exit on first failure, verbose output, show locals",
    )
    parser.add_argument(
        "-k",
        "--specific-test",
        help="Only run tests matching the given substring expression",
    )
    parser.add_argument(
        "--check-format",
        action="store_true",
        help="Check code formatting without modifying files",
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code using Ruff",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Lint code using Ruff",
    )

    args = parser.parse_args()

    # Handle formatting and linting options
    if args.check_format:
        return format_code(check_only=True)

    if args.format:
        return format_code(check_only=False)

    if args.lint:
        return lint_code()

    # Run tests
    return run_tests(
        test_path=args.test_path,
        verbose=args.verbose,
        coverage=args.coverage,
        junit_xml=args.junit_xml,
        xvs=args.xvs,
        specific_test=args.specific_test,
    )


if __name__ == "__main__":
    sys.exit(main())
