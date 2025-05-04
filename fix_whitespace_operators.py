#!/usr/bin/env python
"""
Script to fix missing whitespace around arithmetic operators (E226) in Python files.

This script scans Python files in the project and adds missing whitespace
around arithmetic operators that are flagged by flake8 with the E226 error code.

Usage:
    python fix_whitespace_operators.py [directory]
"""

import os
import re
import sys
import subprocess

def run_flake8(directory):
    """Run flake8 to find missing whitespace around operators and parse the output."""
    try:
        result = subprocess.run(
            ["flake8", directory, "--select=E226"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error running flake8: {e}")
        return []

def parse_flake8_output(output_lines):
    """Parse flake8 output to extract file paths and line numbers."""
    issues = {}
    for line in output_lines:
        # Example line: path/to/file.py:1:1: E226 missing whitespace around arithmetic operator
        match = re.match(r'(.+?):(\d+):\d+: E226', line)
        if match:
            file_path, line_num = match.groups()
            file_path = file_path.strip()
            line_num = int(line_num)
            issues.setdefault(file_path, []).append(line_num)
    return issues

def fix_whitespace_in_line(line):
    """Add missing whitespace around arithmetic operators."""
    # Define patterns for operators that need spacing
    patterns = [
        (
         r'([^<>!=\s])([+\-*/%@]|==|!=|<=|>=|<|>)([^<>!=\s])',
         r'\1 \2 \3'
        ),  # Basic operators
        (
         r'([^<>!=\s])([+\-*/%@]|==|!=|<=|>=|<|>)(\s)',
         r'\1 \2\3'
        ),  # Operator followed by space
        (
         r'(\s)([+\-*/%@]|==|!=|<=|>=|<|>)([^<>!=\s])',
         r'\1\2 \3'
        ),  # Operator preceded by space
    ]
    
    modified_line = line
    for pattern, replacement in patterns:
        modified_line = re.sub(pattern, replacement, modified_line)
    
    return modified_line

def fix_file(file_path, line_numbers):
    """Fix whitespace issues in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    for line_num in line_numbers:
        if line_num <= len(lines):
            original_line = lines[line_num - 1]
            modified_line = fix_whitespace_in_line(original_line)
            if original_line != modified_line:
                lines[line_num - 1] = modified_line
                modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    return False

def main():
    """Main function to run the script."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."

    # Run flake8 to find whitespace issues
    flake8_output = run_flake8(directory)
    if not flake8_output:
        print("No missing whitespace around operators found.")
        return

    # Parse flake8 output
    issues = parse_flake8_output(flake8_output)
    
    # Fix each file
    fixed_files = []
    for file_path, line_numbers in issues.items():
        try:
            if fix_file(file_path, line_numbers):
                fixed_files.append(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if fixed_files:
        print(f"Fixed whitespace issues in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No files were modified.")

if __name__ == "__main__":
    main()
