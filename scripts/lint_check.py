#!/usr/bin/env python
"""
Script to run linting checks locally before pushing changes.
This script runs the same checks that are used in the CI workflow.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description=None):
    """Run a shell command and print its output."""
    if description:
        print(f"\n{description}...")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def check_syntax_errors(file_path=None):
    """Check for syntax errors in Python files."""
    print("\nChecking for syntax errors...")
    
    if file_path:
        command = f"python fix_test_collection_warnings.py --check {file_path}"
    else:
        command = "python fix_test_collection_warnings.py --check ."
    
    return run_command(command)


def check_with_ruff(file_path=None):
    """Check code with Ruff."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    success = run_command(
        f"ruff check {target}", 
        "Checking code with Ruff"
    )
    
    format_success = run_command(
        f"ruff format --check {target}", 
        "Checking formatting with Ruff"
    )
    
    return success and format_success


def check_with_flake8(file_path=None):
    """Check code with Flake8."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    # Check for syntax errors and undefined names
    success1 = run_command(
        f"flake8 {target} --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Checking for syntax errors with Flake8"
    )
    
    # Check for other issues (treated as warnings)
    success2 = run_command(
        f"flake8 {target} --count --exit-zero --max-complexity=10 --max-line-length=88 --extend-ignore=E203 --statistics",
        "Checking for other issues with Flake8"
    )
    
    return success1 and success2


def check_with_black(file_path=None):
    """Check formatting with Black."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    return run_command(
        f"black --check --diff {target}",
        "Checking formatting with Black"
    )


def check_with_isort(file_path=None):
    """Check import order with isort."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    return run_command(
        f"isort --check-only --diff --profile black {target}",
        "Checking import order with isort"
    )


def check_with_mypy(file_path=None):
    """Check types with mypy."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    return run_command(
        f"mypy {target} --ignore-missing-imports --install-types --non-interactive --explicit-package-bases",
        "Checking types with mypy"
    )


def check_with_pyright(file_path=None):
    """Check types with pyright."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    return run_command(
        f"pyright {target}",
        "Checking types with pyright"
    )


def check_unused_imports(file_path=None):
    """Check for unused imports."""
    if file_path:
        target = file_path
    else:
        target = "."
    
    return run_command(
        f"ruff check {target} --select F401",
        "Checking for unused imports"
    )


def main():
    """Run all linting checks."""
    parser = argparse.ArgumentParser(description="Run linting checks locally.")
    parser.add_argument("--file", "-f", help="Path to a specific file to check")
    parser.add_argument("--all", "-a", action="store_true", help="Run all checks")
    parser.add_argument("--syntax", "-s", action="store_true", help="Check for syntax errors")
    parser.add_argument("--ruff", "-r", action="store_true", help="Check with Ruff")
    parser.add_argument("--flake8", action="store_true", help="Check with Flake8")
    parser.add_argument("--black", "-b", action="store_true", help="Check with Black")
    parser.add_argument("--isort", "-i", action="store_true", help="Check with isort")
    parser.add_argument("--mypy", "-m", action="store_true", help="Check with mypy")
    parser.add_argument("--pyright", "-p", action="store_true", help="Check with pyright")
    parser.add_argument("--unused", "-u", action="store_true", help="Check for unused imports")
    
    args = parser.parse_args()
    
    # If no specific checks are specified, run all checks
    run_all = args.all or not any([
        args.syntax, args.ruff, args.flake8, args.black, 
        args.isort, args.mypy, args.pyright, args.unused
    ])
    
    file_path = args.file
    
    # Create a list to track which checks passed
    results = []
    
    # Run the selected checks
    if run_all or args.syntax:
        results.append(("Syntax errors", check_syntax_errors(file_path)))
    
    if run_all or args.ruff:
        results.append(("Ruff", check_with_ruff(file_path)))
    
    if run_all or args.flake8:
        results.append(("Flake8", check_with_flake8(file_path)))
    
    if run_all or args.black:
        results.append(("Black", check_with_black(file_path)))
    
    if run_all or args.isort:
        results.append(("isort", check_with_isort(file_path)))
    
    if run_all or args.mypy:
        results.append(("mypy", check_with_mypy(file_path)))
    
    if run_all or args.pyright:
        results.append(("pyright", check_with_pyright(file_path)))
    
    if run_all or args.unused:
        results.append(("Unused imports", check_unused_imports(file_path)))
    
    # Print a summary of the results
    print("\n=== Linting Check Results ===")
    all_passed = True
    for check, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check}: {status}")
        all_passed = all_passed and passed
    
    # Return a non-zero exit code if any check failed
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
