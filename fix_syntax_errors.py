#!/usr/bin/env python
"""
Script to fix common syntax errors in Python files.
This script helps fix syntax errors that are causing GitHub Actions to fail.
"""

import os
import re
import sys
from pathlib import Path


def fix_missing_colons(file_path):
    """Fix missing colons after class and function definitions."""
    with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

    # Fix missing colons after class definitions
    content = re.sub(r'(class\s+\w+\([^)]*\))\s*\n', r'\1:\n', content)

    # Fix missing colons after function definitions
    content = re.sub(r'(def\s+\w+\([^)]*\))\s*\n', r'\1:\n', content)

    # Fix missing parentheses after function definitions
    content = re.sub(r'(def\s+\w+)\s*\n', r'\1():\n', content)

    with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)


    def fix_indentation_errors(file_path):
    """Fix unexpected indentation errors."""
    with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

    fixed_lines = []
    prev_line_empty = False

    for i, line in enumerate(lines):
    # Skip empty lines
    if line.strip() == '':
    fixed_lines.append(line)
    prev_line_empty = True
    continue

    # Check for unexpected indentation at the beginning of a block
    if prev_line_empty and line.startswith('    '):
    fixed_lines.append(line.lstrip())
    else:
    fixed_lines.append(line)

    prev_line_empty = False

    with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)


    def fix_unmatched_parentheses(file_path):
    """Fix unmatched parentheses."""
    with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

    # Count opening and closing parentheses
    open_count = content.count('(')
    close_count = content.count(')')

    # If there are more opening than closing parentheses, add closing ones
    if open_count > close_count:
    content += ')' * (open_count - close_count)

    # If there are more closing than opening parentheses, remove extra closing ones
    elif close_count > open_count:
    for _ in range(close_count - open_count):
    last_close = content.rindex(')')
    content = content[:last_close] + content[last_close+1:]

    with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)


    def fix_invalid_syntax(file_path):
    """Fix various invalid syntax issues."""
    with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

    # Fix assignment in class/function definition
    content = re.sub(r'(class|def)\s+\w+\s*=', r'\1 ', content)

    # Fix missing try/except blocks
    if 'try:' in content and 'except' not in content and 'finally' not in content:
    content += '\nexcept Exception as e:\n    pass\n'

    with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)


    def fix_file(file_path):
    """Apply all fixes to a file."""
    print(f"Fixing {file_path}...")

    try:
    fix_missing_colons(file_path)
    fix_indentation_errors(file_path)
    fix_unmatched_parentheses(file_path)
    fix_invalid_syntax(file_path)
    return True
except Exception as e:
    print(f"Error fixing {file_path}: {e}")
    return False


    def find_python_files(directory='.'):
    """Find all Python files in the directory."""
    return list(Path(directory).glob('**/*.py'))


    def main():
    """Main function to run the script."""
    python_files = find_python_files()

    fixed_count = 0
    error_count = 0

    for file_path in python_files:
    if fix_file(file_path):
    fixed_count += 1
    else:
    error_count += 1

    print(f"\nFixed {fixed_count} files."
    print(f"Failed to fix {error_count} files."

    return 0 if error_count == 0 else 1


    if __name__ == "__main__":
    sys.exit(main(