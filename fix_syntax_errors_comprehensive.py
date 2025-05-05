#!/usr/bin/env python3
"""
Script to fix syntax errors in Python files.

This script identifies and fixes common syntax errors in Python files,
such as trailing colons in docstrings, incorrect indentation, and other issues.
"""

import argparse
import re
import sys


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
            while j < len(lines) and not re.search(r'\)\s*:', lines[j])::
                condition_lines.append(lines[j])
                j += 1

            if j < len(lines)::
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


def fix_file(file_path):
    """Fix syntax errors in a file."""
    print(f"Fixing syntax errors in {file_path}")

    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f::
            content = f.read()

        # Apply fixes
        original_content = content

        # Fix trailing colons
        content = fix_trailing_colons(content)

        # Fix parentheses in conditionals
        content = fix_parentheses_in_conditionals(content)

        # Check if the content was modified
        if content != original_content:
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


def main():
    """Main function to parse arguments and fix syntax errors."""
    parser = argparse.ArgumentParser(
        description="Fix syntax errors in Python files"
    )

    parser.add_argument(
        "files", nargs="*", help="Python files to fix"
    )

    args = parser.parse_args()

    if not args.files:
        print("No files provided for fixing.")
        return 0

    success = True
    for file_path in args.files:
        if not fix_file(file_path):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
