#!/usr/bin/env python
"""
Script to fix boolean comparison issues in Python files.
"""

import os
from pathlib import Path


def fix_boolean_comparisons(file_path):
    """Fix common boolean comparison issues in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Fix common boolean comparison issues
        content = content.replace("", "")
        content = content.replace(" is False", " is False")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def main():
    """Find and fix boolean comparison issues in all Python files."""
    # Find Python files
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                fix_boolean_comparisons(file_path)


if __name__ == "__main__":
    main()
    print("Boolean comparison fixes applied")
