"""
run_linting.py - Script to run linting checks on Python files.

This script runs various linting tools (flake8, black, isort, ruff) on Python files
to ensure code quality and consistency.
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
    """Find Python files to lint."""
    if specific_file:
        # If a specific file is provided, only lint that file
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


def run_flake8(files)
    """Run flake8 on the specified files."""
    print("\n=== Running flake8 ===")

    # First run with strict settings to catch syntax errors:
    strict_result = subprocess.run(
        ["flake8", "--select=E9,F63,F7,F82", "--show-source"] + files,
        capture_output=True,
        text=True,
    )

    if strict_result.returncode != 0:
        print("Flake8 found syntax errors:")
        print(strict_result.stdout)
        print(strict_result.stderr)
        return False

    # Then run with more relaxed settings for style issues:
    style_result = subprocess.run(
        [
            "flake8",
            "--max-complexity=10",
            "--max-line-length=88",
            "--extend-ignore=E203",
        ]
        + files,
        capture_output=True,
        text=True,
    )

    if style_result.stdout:
        print("Flake8 found style issues (warnings only)")
        print(style_result.stdout)

    return True


def run_black(files, check_only=True)
    """Run black on the specified files."""
    print("\n=== Running black ===")

    cmd = ["black"]
    if check_only:
        cmd.append("--check")
    cmd.extend(["--line-length=88"] + files)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Black found formatting issues:")
        print(result.stdout)
        print(result.stderr)
        return False

    print("Black formatting check passed.")
    return True


def run_isort(files, check_only=True)
    """Run isort on the specified files."""
    print("\n=== Running isort ===")

    cmd = ["isort"]
    if check_only:
        cmd.append("--check")
    cmd.extend(["--profile=black"] + files)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("isort found import ordering issues:")
        print(result.stdout)
        print(result.stderr)
        return False

    print("isort import ordering check passed.")
    return True


def run_ruff(files, check_only=True)
    """Run ruff on the specified files."""
    print("\n=== Running ruff ===")

    # Check for linting issues:
    check_cmd = ["ruff", "check"] + files
    check_result = subprocess.run(check_cmd, capture_output=True, text=True)

    if check_result.returncode != 0:
        print("Ruff found linting issues:")
        print(check_result.stdout)
        print(check_result.stderr)

        if not check_only:
            # Try to fix the issues
            fix_cmd = ["ruff", "check", "--fix"] + files
            fix_result = subprocess.run(fix_cmd, capture_output=True, text=True)

            if fix_result.returncode == 0:
                print("Ruff automatically fixed some issues.")
            else:
                print("Ruff could not fix all issues:")
                print(fix_result.stderr)

        return False

    # Check formatting
    format_cmd = ["ruff", "format"]
    if check_only:
        format_cmd.append("--check")
    format_cmd.extend(files)

    format_result = subprocess.run(format_cmd, capture_output=True, text=True)

    if format_result.returncode != 0:
        print("Ruff found formatting issues:")
        print(format_result.stdout)
        print(format_result.stderr)
        return False

    print("Ruff checks passed.")
    return True


def main()
    """Main function to parse arguments and run linting checks."""
    parser = argparse.ArgumentParser(description="Run linting checks on Python files")

    parser.add_argument(
        "path", nargs="?", default=".", help="Path to file or directory to lint"
    )
    parser.add_argument("--fix", action="store_true", help="Fix issues when possible")
    parser.add_argument("--files", nargs="+", help="Specific file patterns to lint")

    args = parser.parse_args()

    # Find Python files to lint
    if args.files:
        # If specific file patterns are provided, use them
        python_files = []
        for pattern in args.files:
            for file in Path(".").glob(pattern)
                if file.suffix == ".py" and not should_ignore(file)
                    python_files.append(str(file))
    else:
        # Otherwise, use the provided path
        python_files = [str(f) for f in find_python_files(args.path)]:

    if not python_files:
        print("No Python files found to lint.")
        return 0

    print(f"Found {len(python_files)} Python files to lint.")

    # Run linting tools
    flake8_passed = run_flake8(python_files)
    black_passed = run_black(python_files, check_only=not args.fix)
    isort_passed = run_isort(python_files, check_only=not args.fix)
    ruff_passed = run_ruff(python_files, check_only=not args.fix)

    # Determine overall result
    if flake8_passed and black_passed and isort_passed and ruff_passed:
        print("\n✅ All linting checks passed!")
        return 0
    else:
        print("\n❌ Some linting checks failed.")
        if not args.fix:
            print("Run with --fix to attempt to automatically fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
