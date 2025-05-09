#!/usr/bin/env python
"""Script to fix docstring issues in Python files."""

import os
import re
import sys

from pathlib import Path
from typing import List
from typing import Optional


def find_python_files(ignore_patterns: Optional[List[str]] = None) -> List[str]:
    """Find all Python files in the current directory and subdirectories."""
    if ignore_patterns is None:
        # Default patterns to ignore - include both slash types for cross-platform
        # compatibility
        ignore_patterns = [
            r"\.git[/\\]",
            r"\.venv[/\\]",
            r"venv[/\\]",
            r"__pycache__[/\\]",
            r"\.pytest_cache[/\\]",
            r"\.mypy_cache[/\\]",
            r"\.ruff_cache[/\\]",
            r"\.eggs[/\\]",
            r"\.tox[/\\]",
            r"build[/\\]",
            r"dist[/\\]",
            r".*\.egg-info[/\\]",
        ]

    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip directories that match ignore patterns
        # Convert paths to use forward slashes for consistency in pattern matching
        dirs[:] = [
            d
            for d in dirs
            if not any(
                re.search(pattern, os.path.join(root, d).replace("\\", "/"))
                for pattern in ignore_patterns
            )
        ]

        # Also explicitly remove .venv directory if it exists
        if ".venv" in dirs:
            dirs.remove(".venv")
        if "venv" in dirs:
            dirs.remove("venv")

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Check if the file path matches any ignore pattern
                if not any(
                    re.search(pattern, file_path.replace("\\", "/"))
                    for pattern in ignore_patterns
                ):
                    python_files.append(file_path)

    return python_files


def fix_docstring_issues(file_path: str, verbose: bool = False) -> bool:
    """Fix docstring issues in a Python file."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    original_content = content

    # Fix module-level docstrings
    if re.match(r'^""".*"""', content, re.DOTALL):
        # If the docstring doesn't end with a period, add one
        content = re.sub(
            r'^"""(.*?)([^.!?])"""', r'"""\1\2."""', content, flags=re.DOTALL
        )
    else:
        # If there's no module-level docstring, add one
        module_name = os.path.basename(file_path).replace(".py", "")
        module_path = (
            os.path.dirname(file_path)
            .replace("\\", "/")
            .replace("./", "")
            .replace(".", "")
        )
        if module_path:
            module_path = f"{module_path}."

        new_docstring = (
            f'"""\n{module_name} - Module for {module_path}{module_name}.\n"""\n\n'
        )
        content = new_docstring + content

    # Check if any changes were made
    if content == original_content:
        if verbose:
            print(f"No docstring issues fixed in {file_path}")
        return True

    # Write the fixed content back to the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

    if verbose:
        print(f"Fixed docstring issues in {file_path}")

    return True


def main() -> int:
    """Run the main script functionality."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix docstring issues in Python files."
    )
    parser.add_argument(
        "file_paths",
        nargs="*",
        help=(
            "Paths to Python files to fix. "
            "If not provided, all Python files will be processed."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information about fixes.",
    )
    args = parser.parse_args()

    # Get the list of Python files to process
    if args.file_paths:
        python_files = [str(Path(path).resolve()) for path in args.file_paths]
    else:
        python_files = find_python_files()

    success = True
    fixed_files = 0
    total_files = len(python_files)

    print(f"Processing {total_files} Python files...")

    for file_path in python_files:
        if args.verbose:
            print(f"Processing {file_path}...")

        if fix_docstring_issues(file_path, args.verbose):
            fixed_files += 1
        else:
            print(f"Failed to fix docstring issues in {file_path}")
            success = False

    print(f"Fixed {fixed_files} out of {total_files} files.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
