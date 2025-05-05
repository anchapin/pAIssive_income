#!/usr/bin/env python3
"""
Script to fix all syntax errors in Python files comprehensively.

This script identifies and fixes various syntax errors in Python files,
including invalid colons, parentheses issues, indentation problems, and more.
"""

import argparse
import os
import re
import sys
from pathlib import Path


def fix_trailing_colons(content):
    """Fix trailing colons in docstrings and other statements."""
    # Fix trailing colons in docstrings
    content = re.sub(r'(""".*?"""):(\s*)', r'\1\2', content, flags=re.DOTALL)
    content = re.sub(r"('''.*?'''):(\s*)", r'\1\2', content, flags=re.DOTALL)

    # Fix trailing colons in variable assignments
    content = re.sub(r'(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*.*?):(\s*$)', r'\1\2', content, flags=re.MULTILINE)

    # Fix trailing colons in function calls
    content = re.sub(r'(\s*[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)):(\s*$)', r'\1\2', content, flags=re.MULTILINE)

    # Fix trailing colons in list/dict comprehensions
    content = re.sub(r'(\s*\[[^\]]*\]):(\s*$)', r'\1\2', content, flags=re.MULTILINE)
    content = re.sub(r'(\s*\{[^}]*\}):(\s*$)', r'\1\2', content, flags=re.MULTILINE)

    return content


def fix_colons_in_comments(content):
    """Fix colons at the end of comments."""
    # Fix colons at the end of single-line comments
    content = re.sub(r'(#[^:\n]*):(\s*)$', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons at the end of multi-line comments (more specific pattern)
    content = re.sub(r'(#[^:\n]*):(\s*\n)', r'\1\2', content, flags=re.MULTILINE)

    return content


def fix_colons_after_keywords(content):
    """Fix colons after keywords where they shouldn't be."""
    # Fix colons after keywords in list comprehensions
    content = re.sub(r'(\s*for\s+[^:]+\s+in\s+[^:]+):(\s+)', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons after 'in' keyword
    content = re.sub(r'(\s+in\s+[^:]+):(\s+)', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons after opening brackets in lists
    content = re.sub(r'(\[\s*):(\s*)', r'\1\2', content, flags=re.MULTILINE)

    return content


def fix_parentheses_in_conditionals(content):
    """Fix issues with parentheses in conditional statements."""
    # Fix if ( ... ) pattern
    lines = content.split('\n')
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for if ( pattern
        if re.match(r'^\s*if\s*\(\s*$', line):
            # Collect the condition lines
            condition_lines = [line]
            j = i + 1

            # Find the closing parenthesis
            while j < len(lines) and not re.search(r'\)\s*:', lines[j]):
                condition_lines.append(lines[j])
                j += 1

            if j < len(lines):
                condition_lines.append(lines[j])

                # Join the condition lines and fix the format
                condition = ' '.join([l.strip() for l in condition_lines])
                condition = re.sub(r'if\s*\(\s*(.*?)\s*\)\s*:', r'if \1:', condition)

                fixed_lines.append(condition)
                i = j + 1
                continue

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)


def fix_file(file_path, dry_run=False):
    """Fix syntax errors in a file."""
    print(f"Fixing syntax errors in {file_path}")

    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply fixes
        original_content = content

        # Fix trailing colons
        content = fix_trailing_colons(content)

        # Fix colons in comments
        content = fix_colons_in_comments(content)

        # Fix colons after keywords
        content = fix_colons_after_keywords(content)

        # Fix parentheses in conditionals
        content = fix_parentheses_in_conditionals(content)

        # Check if the content was modified
        if content != original_content:
            if dry_run:
                print(f"Would fix syntax errors in: {file_path}")
                return True
            else:
                # Write the fixed content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Fixed: {file_path}")
                return True
        else:
            print(f"No issues found in: {file_path}")
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_python_files(path):
    """Find all Python files in the given path."""
    if os.path.isfile(path) and path.endswith('.py'):
        return [path]

    python_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    """Main function to parse arguments and fix syntax errors."""
    parser = argparse.ArgumentParser(
        description="Fix syntax errors in Python files"
    )

    parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to a Python file or directory containing Python files"
    )

    parser.add_argument(
        "--dry-run", action="store_true",
        help="Check for syntax errors without modifying files"
    )

    args = parser.parse_args()

    # Find Python files to check/fix
    python_files = find_python_files(args.path)

    if not python_files:
        print("No files provided for fixing.")
        return 0

    print(f"Checking {len(python_files)} Python files...")

    # Check/fix the files
    success = True
    for file_path in python_files:
        if not fix_file(file_path, dry_run=args.dry_run):
            success = False

    if args.dry_run:
        print("Dry run completed. No files were modified.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
