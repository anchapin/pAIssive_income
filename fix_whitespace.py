#!/usr/bin/env python
"""
Script to fix whitespace issues (E226) in Python files.

This script scans Python files in the project and fixes missing whitespace
around arithmetic operators (E226).

Usage:
    python fix_whitespace.py [directory]
"""

import os
import re
import sys
from pathlib import Path


def find_python_files(directory):
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).rglob("*.py"))


def fix_whitespace_in_file(file_path):
    """Fix whitespace issues in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix missing whitespace around arithmetic operators (E226)
    # Match patterns like: x+y, x-y, x*y, x/y, x%y, x**y, x//y, x@y
    patterns = [
        (r'([a-zA-Z0-9_\)\]\'"])\+([a-zA-Z0-9_\(\[\'\"])', r'\1 + \2'),
        (r'([a-zA-Z0-9_\)\]\'"])-([a-zA-Z0-9_\(\[\'\"])', r'\1 - \2'),
        (r'([a-zA-Z0-9_\)\]\'"]\*\*)([a-zA-Z0-9_\(\[\'\"])', r'\1 \2'),  # Handle ** before *
        (r'([a-zA-Z0-9_\)\]\'"])\*([a-zA-Z0-9_\(\[\'\"])', r'\1 * \2'),
        (r'([a-zA-Z0-9_\)\]\'"])/([a-zA-Z0-9_\(\[\'\"])', r'\1 / \2'),
        (r'([a-zA-Z0-9_\)\]\'"])%([a-zA-Z0-9_\(\[\'\"])', r'\1 % \2'),
        (r'([a-zA-Z0-9_\)\]\'"])//([a-zA-Z0-9_\(\[\'\"])', r'\1 // \2'),
        (r'([a-zA-Z0-9_\)\]\'"])@([a-zA-Z0-9_\(\[\'\"])', r'\1 @ \2'),
    ]

    modified_content = content
    for pattern, replacement in patterns:
        modified_content = re.sub(pattern, replacement, modified_content)

    # Check if we need to write changes
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True

    return False


def fix_whitespace(directory):
    """Fix whitespace issues in all Python files in the directory."""
    python_files = find_python_files(directory)
    fixed_files = []
    
    for file_path in python_files:
        try:
            if fix_whitespace_in_file(file_path):
                fixed_files.append(str(file_path))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return fixed_files


def main():
    """Main function to run the script."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    fixed_files = fix_whitespace(directory)
    
    if fixed_files:
        print(f"Fixed whitespace issues in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No whitespace issues found or fixed.")


if __name__ == "__main__":
    main()
