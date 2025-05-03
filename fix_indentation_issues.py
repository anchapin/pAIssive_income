#!/usr/bin/env python
"""
Script to fix indentation issues in Python files.
This script helps fix common indentation errors that are causing GitHub Actions to fail.
"""

import os
import re
import sys
from pathlib import Path
from typing import Set, List


def fix_indentation_issues(file_path):
    """Fix indentation issues in a Python file."""
    print(f"Fixing indentation issues in {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix common indentation issues

    # 1. Fix missing indentation after function/class definitions
    content = re.sub(r'(def\s+\w+\([^)]*\):)\s*\n([^\s])', r'\1\n    \2', content)
    content = re.sub(r'(class\s+\w+(?:\([^)]*\))?:)\s*\n([^\s])', r'\1\n    \2', content)

    # 2. Fix inconsistent indentation levels
    lines = content.split('\n')
    fixed_lines = []
    current_indent = 0
    indent_stack = [0]

    for line in lines:
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue

        # Calculate the current line's indentation
        indent = len(line) - len(line.lstrip())
        content_line = line.strip()

        # Check for indentation decreases
        if indent < current_indent:
            while indent_stack and indent < indent_stack[-1]:
                indent_stack.pop()

            if indent_stack:
                # Align with the proper indentation level
                current_indent = indent_stack[-1]
                fixed_line = ' ' * current_indent + content_line
            else:
                # Reset to no indentation if we've popped everything
                current_indent = 0
                indent_stack = [0]
                fixed_line = content_line
        else:
            # For lines that increase indentation or stay at the same level
            fixed_line = line

        # Check for indentation increases (after colons)
        if content_line.endswith(':'):
            indent_stack.append(current_indent + 4)
            current_indent = indent_stack[-1]

        fixed_lines.append(fixed_line)

    # 3. Fix 'return' statements outside of functions
    fixed_content = '\n'.join(fixed_lines)
    fixed_content = re.sub(r'(\n\s*)return\s+', r'\1    return ', fixed_content)

    # 4. Fix unmatched parentheses
    open_count = fixed_content.count('(')
    close_count = fixed_content.count(')')

    if open_count > close_count:
        fixed_content += ')' * (open_count - close_count)
    elif close_count > open_count:
        # This is trickier to fix automatically, but we'll try
        last_close = fixed_content.rindex(')')
        fixed_content = fixed_content[:last_close] + fixed_content[last_close+1:]

    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

        return True


def get_gitignore_patterns() -> Set[str]:
    """Read .gitignore patterns and return them as a set."""
    patterns = set()
    try:
        with open(".gitignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)
    except FileNotFoundError:
        pass
        return patterns


def should_ignore(file_path: str, ignore_patterns: Set[str]) -> bool:
    """Check if a file should be ignored based on gitignore patterns."""
    # Convert Windows paths to forward slashes for consistency
    file_path = file_path.replace("\\", "/")

    for pattern in ignore_patterns:
        # Basic gitignore pattern matching
        if pattern.endswith("/"):
            # Directory pattern
            if pattern[:-1] in file_path.split("/"):
                return True
        elif pattern.startswith("**/"):
            # Match anywhere in path
            if file_path.endswith(pattern[3:]):
                return True
        elif pattern.startswith("/"):
            # Match from root
            if file_path.startswith(pattern[1:]):
                return True
        else:
            # Simple pattern
            if pattern in file_path:
                return True
    return False


def find_python_files(directory='.') -> List[Path]:
    """Find all Python files in the directory that aren't ignored by gitignore."""
    all_python_files = []

    # Explicitly exclude .venv directory and other common directories to ignore
    excluded_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', 'build', 'dist'}

    # Walk the directory tree manually to have more control
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from dirs to prevent os.walk from traversing them
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        # Skip any path that contains .venv
        if any(excluded_dir in root.split(os.sep) for excluded_dir in excluded_dirs):
            continue

        # Add Python files
        for file in files:
            if file.endswith('.py'):
                file_path = Path(os.path.join(root, file))
                all_python_files.append(file_path)

    # Also apply gitignore patterns
    ignore_patterns = get_gitignore_patterns()

    return [
        file_path for file_path in all_python_files
        if not should_ignore(str(file_path.relative_to(directory)), ignore_patterns)
    ]


def main():
    """Main function to run the script."""
    if len(sys.argv) > 1:
        # Fix a specific file
        file_path = sys.argv[1]
        if os.path.isfile(file_path) and file_path.endswith('.py'):
            fix_indentation_issues(file_path)
        else:
            print(f"Error: {file_path} is not a Python file.")
            return 1
    else:
        # Fix all Python files
        python_files = find_python_files()

        fixed_count = 0
        for file_path in python_files:
            try:
                if fix_indentation_issues(str(file_path)):
                    fixed_count += 1
            except Exception as e:
                print(f"Error fixing {file_path}: {e}")

        print(f"\nFixed {fixed_count} files.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
