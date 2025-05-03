#!/usr/bin/env python
"""
Script to run all linting fixes in sequence.

This script runs all the fix scripts in the appropriate order to address
the remaining linting issues in the project.

Usage:
    python run_all_fixes.py [directory]
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(message):
    """Print a formatted header message."""
    print(f"\n{'=' * 80}")
    print(f"= {message}")
    print(f"{'=' * 80}\n")


def run_script(script_name, directory="."):
    """Run a Python script with the given directory."""
    print_header(f"Running {script_name}")
    result = subprocess.run(
        [sys.executable, script_name, directory],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"Errors:\n{result.stderr}")
    return result.returncode == 0


def run_flake8(directory="."):
    """Run flake8 to check for remaining issues."""
    print_header("Running flake8 to check for remaining issues")
    
    # Use the virtual environment's flake8 if available
    flake8_cmd = ".venv/bin/flake8" if os.path.exists(".venv/bin/flake8") else "flake8"
    
    # Run flake8 with specific error codes
    try:
        result = subprocess.run(
            [flake8_cmd, directory, "--select=E226,E501,F401", "--count", "--statistics"],
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        print("flake8 not found. Please install it in your virtual environment.")
        print("Try: python -m venv .venv && source .venv/bin/activate && pip install flake8")
        return {}
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors:\n{result.stderr}")
    
    # Parse the results
    issues = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            parts = line.split(":")
            if len(parts) >= 3:
                error_code = parts[2].strip().split()[0]
                if error_code not in issues:
                    issues[error_code] = 0
                issues[error_code] += 1
    
    # Print summary
    if issues:
        print("\nRemaining issues:")
        for code, count in issues.items():
            print(f"  {code}: {count} issues")
    else:
        print("\nNo remaining issues found!")
    
    return issues


def main():
    """Main function to run all fix scripts."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Run initial flake8 check
    print_header("Initial check")
    initial_issues = run_flake8(directory)
    
    # Run fix scripts in sequence
    run_script("fix_unused_imports.py", directory)
    run_script("fix_whitespace.py", directory)
    run_script("fix_line_length.py", directory)
    
    # Run final flake8 check
    print_header("Final check")
    final_issues = run_flake8(directory)
    
    # Print summary of improvements
    print_header("Summary of improvements")
    
    if not initial_issues and not final_issues:
        print("No issues were found before or after running the fixes.")
        return
    
    for code in set(list(initial_issues.keys()) + list(final_issues.keys())):
        initial = initial_issues.get(code, 0)
        final = final_issues.get(code, 0)
        if initial > final:
            print(f"{code}: {initial} → {final} issues ({initial - final} fixed, {100 * (initial - final) / initial:.1f}% improvement)")
        elif initial == final:
            print(f"{code}: {initial} → {final} issues (no change)")
        else:
            print(f"{code}: {initial} → {final} issues ({final - initial} new issues)")
    
    # Print overall improvement
    initial_total = sum(initial_issues.values())
    final_total = sum(final_issues.values())
    if initial_total > 0:
        improvement = 100 * (initial_total - final_total) / initial_total
        print(f"\nOverall: {initial_total} → {final_total} issues ({initial_total - final_total} fixed, {improvement:.1f}% improvement)")
    

if __name__ == "__main__":
    main()
