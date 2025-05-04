#!/usr/bin/env python
"""
Script to fix module docstrings in Python files.
This script specifically targets invalid module docstrings at the beginning of files.
"""

import os
import sys


def fix_file(file_path):
    """Fix module docstrings in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if the file starts with a docstring that has syntax errors
        lines = content.split("\n")
        modified = False

        # Find the first non-empty line
        first_line_idx = 0
        for i, line in enumerate(lines):
            if line.strip():
                first_line_idx = i
                break

        # Check if the first non-empty line is a docstring with invalid syntax
        if first_line_idx < len(lines):
            first_line = lines[first_line_idx].strip()

            # Case 1: Line starts with a docstring but has invalid syntax
            if first_line.startswith('"""') and not first_line.endswith('"""'):
                # Find the end of the docstring or add one if not found
                docstring_end_idx = -1
                for i in range(
                    first_line_idx + 1, min(first_line_idx + 20, len(lines))
                ):
                    if '"""' in lines[i]:
                        docstring_end_idx = i
                        break

                if docstring_end_idx == -1:
                    # No end found, add one
                    lines.insert(first_line_idx + 1, '"""')
                    modified = True

            # Case 2: Line is a docstring content without the opening quotes
            elif (
                not first_line.startswith('"""')
                and not first_line.startswith("#")
                and not first_line.startswith("from")
                and not first_line.startswith("import")
            ):
                # Check if this might be a docstring content without the opening quotes
                if first_line_idx > 0 and not lines[first_line_idx - 1].strip():
                    # Add opening and closing quotes
                    lines[first_line_idx] = f'"""{first_line}"""'
                    modified = True

        # Fix unterminated triple-quoted strings
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line:
                # Count the number of triple quotes in this line
                count = line.count('"""')
                if count % 2 == 1:
                    in_docstring = not in_docstring

        # If we're still in a docstring at the end of the file, close it
        if in_docstring:
            lines.append('"""')
            modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_python_files(directory, exclude_dirs=None):
    """Find all Python files in a directory and its subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = [".venv", ".git", "__pycache__"]

    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    """Main function."""
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]

    python_files = find_python_files(directory)
    fixed_count = 0

    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1

    print(f"Fixed {fixed_count} files out of {len(python_files)} Python files.")


if __name__ == "__main__":
    main()
