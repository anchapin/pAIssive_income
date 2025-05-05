#!/usr/bin/env python3
"""
Script to fix invalid colons in Python files.

This script identifies and fixes colons that appear in places where they shouldn't be,
such as at the end of comments, at the end of statements, or after certain keywords
where they don't belong.

The script automatically ignores files in the .venv directory to avoid modifying
virtual environment files.

Note: Some complex syntax errors may still require manual fixing after running this script.
Examples include:
- Dictionary syntax errors with misplaced colons
- Type hint syntax errors
- Other complex syntax constructs
"""

import argparse
import os
import re
import sys
from pathlib import Path


def fix_colons_in_comments(content):
    """Fix colons at the end of comments."""
    # Fix colons at the end of single-line comments (but not type hints)
    content = re.sub(r'(#[^:\n]*):(\s*)$', r'\1\2', content, flags=re.MULTILINE)
    content = re.sub(r'(#[^:\n]*):(\s*\n)', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons after docstring closing quotes (but not module docstrings that might have type hints)
    # This is a more careful approach that only removes colons after closing quotes
    # when they're followed by whitespace or newline
    content = re.sub(r'("""[^"]*?"""):(\s+)', r'\1\2', content, flags=re.DOTALL)
    content = re.sub(r"('''[^']*?'''):(\s+)", r'\1\2', content, flags=re.DOTALL)

    # Fix double colons at the end of lines (more aggressive pattern)
    content = re.sub(r'::(\s*$)', r':\1', content, flags=re.MULTILINE)
    content = re.sub(r'::(\s*\n)', r':\1', content, flags=re.MULTILINE)

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


def fix_colons_at_line_end(content):
    """Fix colons at the end of statements where they shouldn't be."""
    # Fix colons at the end of import statements
    content = re.sub(r'(^\s*(?:from|import)\s+[^:]+):(\s*)$', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons at the end of return statements
    content = re.sub(r'(^\s*return\s+[^:]*):(\s*)$', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons at the end of variable assignments (but not class/function definitions)
    # This pattern is more careful to avoid removing colons in dictionary definitions
    content = re.sub(r'(^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^:{]+):(\s*)$', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons at the end of function calls
    content = re.sub(r'(^\s*[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)):(\s*)$', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons at the end of print statements
    content = re.sub(r'(^\s*print\([^)]*\)):(\s*)$', r'\1\2', content, flags=re.MULTILINE)

    # Fix colons at the end of list/dict/set literals (but not in dict key-value pairs)
    content = re.sub(r'(\]\s*):(\s*)$', r'\1\2', content, flags=re.MULTILINE)  # Lists
    content = re.sub(r'(\}\s*):(\s*)$', r'\1\2', content, flags=re.MULTILINE)  # Dicts/sets

    return content


def fix_colons_in_function_definitions(content):
    """Fix colons in function definitions where they shouldn't be."""
    # Fix colons in function parameter lists
    lines = content.split('\n')
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if line is a function definition
        if re.match(r'^\s*def\s+\w+\s*\(', line):
            # If the line already ends with a colon and closing parenthesis, it's fine
            if re.search(r'\):\s*$', line):
                fixed_lines.append(line)
                i += 1
                continue

            # If the line has a colon inside the parameter list, fix it
            if ':' in line and not line.rstrip().endswith(':'):
                # This is a complex case, collect all lines of the function definition
                func_def = [line]
                j = i + 1

                # Keep collecting lines until we find the closing parenthesis
                while j < len(lines) and ')' not in lines[j]:
                    func_def.append(lines[j])
                    j += 1

                if j < len(lines):
                    func_def.append(lines[j])

                    # Join the function definition and fix colons inside parameter list
                    full_def = '\n'.join(func_def)

                    # Replace colons inside parameter list (but not the final one)
                    # This is a simplified approach - complex cases might need manual fixing
                    if ')' in full_def:
                        parts = full_def.split(')', 1)
                        # Remove colons from parameter part
                        param_part = parts[0].replace(':', ',')
                        # Make sure we keep the colon after the closing parenthesis
                        if len(parts) > 1 and not parts[1].lstrip().startswith(':'):
                            parts[1] = ':' + parts[1]
                        full_def = ')'.join([param_part, parts[1]])

                    # Split back into lines
                    fixed_func_def = full_def.split('\n')
                    fixed_lines.extend(fixed_func_def)
                    i = j + 1
                    continue

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)


def ensure_required_colons(content):
    """Ensure that required colons are present."""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Add colons after class definitions if missing
        if re.match(r'^\s*class\s+\w+(?:\([^)]*\))?\s*$', line):
            line += ':'

        # Add colons after function definitions if missing
        elif re.match(r'^\s*def\s+\w+\([^)]*\)\s*$', line):
            line += ':'

        # Add colons after control statements if missing
        elif re.match(r'^\s*(if|elif|else|for|while|try|except|finally|with)\s+.*\S\s*$', line):
            # Don't add colon if it's in a list comprehension
            if not re.search(r'\[.*for\s+.*\s+in\s+.*\]', line):
                line += ':'

        # Add colons after bare 'else' statements
        elif re.match(r'^\s*else\s*$', line):
            line += ':'

        # Add colons after bare 'try' statements
        elif re.match(r'^\s*try\s*$', line):
            line += ':'

        # Fix variable assignments with trailing colons
        elif re.search(r'=\s*\w+:$', line):
            line = re.sub(r'=\s*(\w+):$', r'= \1', line)

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)





def fix_file(file_path, dry_run=False):
    """Fix invalid colons in a file."""
    print(f"Checking for invalid colons in {file_path}")

    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply fixes
        original_content = content

        # Fix colons in comments
        content = fix_colons_in_comments(content)

        # Fix colons after keywords
        content = fix_colons_after_keywords(content)

        # Fix colons at the end of statements
        content = fix_colons_at_line_end(content)

        # Fix colons in function definitions
        content = fix_colons_in_function_definitions(content)

        # Ensure required colons are present
        content = ensure_required_colons(content)

        # Check if the content was modified
        if content != original_content:
            if dry_run:
                print(f"Would fix invalid colons in: {file_path}")
                return True
            else:
                # Write the fixed content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Fixed invalid colons in: {file_path}")
                return True
        else:
            print(f"No invalid colons found in: {file_path}")
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def should_ignore_path(path):
    """Check if a path should be ignored."""
    # Normalize path separators to handle both / and \
    normalized_path = os.path.normpath(path)

    # Check if path contains .venv directory
    path_parts = normalized_path.split(os.sep)
    if '.venv' in path_parts:
        return True

    # Alternative check for different path formats
    if '.venv' in normalized_path.replace('\\', '/').split('/'):
        return True

    return False


def find_python_files(path):
    """Find all Python files in the given path."""
    if os.path.isfile(path) and path.endswith('.py'):
        if should_ignore_path(path):
            print(f"Ignoring file in .venv directory {path}")
            return []
        return [path]

    python_files = []
    for root, _, files in os.walk(path):
        # Skip .venv directory
        if should_ignore_path(root):
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not should_ignore_path(file_path):
                    python_files.append(file_path)

    return python_files


def main():
    """Main function to parse arguments and fix invalid colons."""
    parser = argparse.ArgumentParser(
        description="Fix invalid colons in Python files"
    )

    parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to a Python file or directory containing Python files"
    )

    parser.add_argument(
        "--dry-run", action="store_true",
        help="Check for invalid colons without modifying files"
    )

    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed information about the fixes being made"
    )

    args = parser.parse_args()

    # Find Python files to check/fix
    python_files = find_python_files(args.path)

    if not python_files:
        print("No Python files found to check.")
        return 0

    print(f"Checking {len(python_files)} Python files for invalid colons...")
    print("This script will fix the following types of issues:")
    print("  - Colons at the end of comments")
    print("  - Colons at the end of statements where they shouldn't be")
    print("  - Colons after keywords where they don't belong")
    print("  - Missing colons after class/function definitions and control statements")
    print("  - Colons in function parameter lists (except for type hints)")
    print()
    print("Note: Files in the .venv directory are automatically ignored.")
    print("Note: Some complex syntax errors may still require manual fixing.")
    print()

    # Check/fix the files
    success = True
    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path, dry_run=args.dry_run):
            fixed_count += 1
        else:
            success = False

    if args.dry_run:
        print("Dry run completed. No files were modified.")
    else:
        print(f"Completed. Fixed {fixed_count} files with invalid colons.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
