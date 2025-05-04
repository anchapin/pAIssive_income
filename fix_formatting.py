#!/usr/bin/env python
"""
Script to automatically format Python files using Black and isort.
"""

import os
import subprocess
import sys


def format_file(file_path):
    """Format a file using Black and isort."""
    print(f"\nFormatting {file_path}...")

    # Format with Black
    try:
        subprocess.run(
            ["black", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ Black formatting successful for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Black formatting failed for {file_path}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False

    # Sort imports with isort
    try:
        subprocess.run(
            ["isort", "--profile", "black", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ isort sorting successful for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ isort sorting failed for {file_path}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False

    # Fix issues with ruff
    try:
        subprocess.run(
            ["ruff", "check", "--fix", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ ruff fixes successful for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ruff fixes failed for {file_path}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False

    return True


def process_directory(directory, exclude_dirs=None):
    """Process all Python files in a directory and its subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = [".venv", ".git", "__pycache__"]

    all_passed = True

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not format_file(file_path):
                    all_passed = False

    return all_passed


def main():
    """Main function to parse args and run the script."""
    directory = "."
    exclude_dirs = [".venv", ".git", "__pycache__"]

    success = process_directory(directory, exclude_dirs)

    if success:
        print("\n✅ All files formatted successfully!")
        return 0
    else:
        print("\n❌ Some files could not be formatted.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
