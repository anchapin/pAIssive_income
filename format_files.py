#!/usr/bin/env python3

"""Script to format Python files according to a simplified version of Black's style.

This script applies basic formatting rules to make Python code more consistent.
"""

import argparse
import os
import re
import sys


def format_file(file_path):
    """Format a Python file according to Black's style."""
    print(f"Formatting {file_path}")

    try:
        # Check if file exists:
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            return False

        # Read the file content
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Apply some basic formatting rules

        # 1. Fix trailing whitespace
        content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

        # 2. Ensure consistent line endings
        content = content.replace("\r\n", "\n")

        # 3. Fix function calls with multiple arguments:
        # This is a simplified version of what Black does
        content = re.sub(
            r"(\s+)([a-zA-Z0-9_]+)\(\s*\n\s*([^,\n]+),\s*\n\s*([^,\n]+),\s*\n\s*\)",
            r"\1\2(\n\1    \3, \4\n\1)",
            content,
        )

        # 4. Fix function calls with two arguments on separate lines:
        content = re.sub(
            r"(\s+)([a-zA-Z0-9_]+)\(\s*\n\s*([^,\n]+),\s*\n\s*([^,\n]+)\s*\n\s*\)",
            r"\1\2(\n\1    \3, \4\n\1)",
            content,
        )

        # 5. Fix function calls with a single argument on a separate line:
        content = re.sub(
            r"(\s+)([a-zA-Z0-9_]+)\(\s*\n\s*([^,\n]+)\s*\n\s*\)",
            r"\1\2(\1    \3\1)",
            content,
        )

        # Write the formatted content back to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Formatted {file_path}")
        return True
    except Exception as e:
        print(f"Error formatting {file_path}: {e}")
        return False


def main():
    """Initialize module to parse arguments and format files."""
    parser = argparse.ArgumentParser(
        description="""Format Python files according to a simplified version of
        Black's style"""
    )

    parser.add_argument("files", nargs="*", help="Python files to format")

    args = parser.parse_args()

    if not args.files:
        print("No files provided for formatting.")
        return 0  # Exit successfully when no files are provided

    success = True
    for file_path in args.files:
        if not format_file(file_path):
            success = False

    return 0 if success else 1


# This function wraps the main() call and sys.exit() to make it testable
def run_main():
    """Run the main function and exit with its return code."""
    result = main()
    return result


if __name__ == "__main__":
    exit_code = run_main()
    sys.exit(exit_code)
