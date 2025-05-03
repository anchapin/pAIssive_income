#!/usr / bin / env python
"""
Script to update the GitHub Actions progress file with the latest status.

This script runs the linting checks and updates the progress file with
the current status of the linting issues.

Usage:
    python update_github_actions_progress.py
"""

import os
import re
import subprocess
import sys
from datetime import datetime


def run_flake8():
    """Run flake8 to check for remaining issues."""
    # Check if flake8 is installed
    try:
        subprocess.run(["flake8", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("flake8 is not installed. Installing...")
        subprocess.run([sys.executable, " - m", "pip", "install", "flake8"], check=True)
    
    # Run flake8 with specific error codes
    result = subprocess.run(
        ["flake8", ".", "--select=E226,E501,F401", "--count", "--statistics"],
        capture_output=True,
        text=True
    )
    
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
    
    return issues


def update_progress_file(issues):
    """Update the GitHub Actions progress file with the latest status."""
    progress_file = "github_actions_progress.md"
    
    if not os.path.exists(progress_file):
        print(f"Error: {progress_file} not found.")
        return False
    
    with open(progress_file, "r") as f:
        content = f.read()
    
    # Get current date
    today = datetime.now().strftime(" % B %d, %Y")
    
    # Update the "Recent Progress" section
    recent_progress_pattern = r"## Recent Progress \(.*?\)"
    updated_recent_progress = f"## Recent Progress ({today})"
    content = re.sub(recent_progress_pattern, updated_recent_progress, content)
    
    # Update the issue counts
    patterns = {
        "F401": r"Unused imports \(F401\): (\d+) out of (\d+) issues",
        "E501": r"Line length issues \(E501\): (\d+) out of (\d+) issues",
        "E226": r"Missing whitespace around operators \(
            E226\): (\d+) out of (\d+) issues"
    }
    
    for code, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            current_fixed = int(match.group(1))
            total = int(match.group(2))
            remaining = issues.get(code, 0)
            fixed = total - remaining
            
            # Update the pattern
            replacement = f"{code.split(':')[0]}: Fixed {fixed} out of {total} issues"
            content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(progress_file, "w") as f:
        f.write(content)
    
    print(f"Updated {progress_file} with the latest status.")
    return True


def main():
    """Main function to update the GitHub Actions progress file."""
    issues = run_flake8()
    
    print("Current linting issues:")
    for code, count in issues.items():
        print(f"  {code}: {count} issues")
    
    update_progress_file(issues)


if __name__ == "__main__":
    main()
