#!/usr/bin/env python3
"""
Simple script to fix common issues that prevent pytest from collecting tests.
"""

import argparse
import os
import re
import sys


def fix_file(file_path):
    """Fix common issues in a file that prevent test collection."""
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Apply fixes
        original_content = content

        # Fix missing colons after class definitions:
        content = re.sub(r"(class\s+\w+(?:\([^)]*\))?)(\s*\n)", r"\1:\2", content)

        # Fix missing colons after function definitions
        content = re.sub(r"(def\s+\w+\([^)]*\))(\s*\n)", r"\1:\2", content)

        # Check if the content was modified
        if content != original_content:
            # Write the fixed content back to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Fixed: {file_path}")
            return True

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to parse arguments and fix test collection warnings."""
    parser = argparse.ArgumentParser(
        description="Fix common issues that prevent pytest from collecting tests"
    )

    parser.add_argument(
        "path", nargs="?", default=".", help="Path to file or directory to check/fix"
    )

    args = parser.parse_args()

    # Find Python files to check/fix
    python_files = []
    if os.path.isfile(args.path) and args.path.endswith(".py"):
        python_files = [args.path]
    else:
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

    if not python_files:
        print("No Python files found to check.")
        return 0

    print(f"Checking {len(python_files)} Python files...")

    # Check/fix the files
    for file_path in python_files:
        fix_file(file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
