"""find_syntax_errors.py - Script to identify syntax errors in Python files.

This script scans Python files for syntax errors and provides detailed information
about the errors found, including line numbers and error messages.
"""

import ast
import os
import sys
import traceback

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


def find_python_files(specific_files: Optional[List[str]] = None) -> List[str]:
    """Find Python files to process.

    Args:
    ----
        specific_files: List of specific files to process. If None,
        all Python files will be found.

    Returns:
    -------
        List of Python file paths.

    """
    if specific_files:
        # Normalize paths for cross-platform compatibility
        normalized_files = []
        for f in specific_files:
            if f.endswith(".py") and os.path.isfile(f):
                normalized_files.append(os.path.normpath(f))
        return normalized_files

    python_files = []
    # Directories to ignore
    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }

    # Create normalized patterns for both forward and backslash paths
    ignore_patterns = []
    for pattern in [
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    ]:
        # Add cross-platform path patterns
        # Forward slash pattern
        fwd = os.path.normpath(f"./{pattern}")
        ignore_patterns.append(fwd)
        # Backslash pattern
        bck = os.path.normpath(f".\\{pattern}")
        ignore_patterns.append(bck)

    for root, dirs, files in os.walk("."):
        # Skip ignored directories
        norm_root = os.path.normpath(root)

        # Check if this directory should be ignored
        if any(norm_root.startswith(pattern) for pattern in ignore_patterns):
            continue

        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.normpath(os.path.join(root, file))
                python_files.append(file_path)

    return python_files


def check_syntax(file_path: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """Check a Python file for syntax errors.

    Args:
    ----
        file_path: Path to the Python file.

    Returns:
    -------
        Tuple of (has_error, error_message, line_number).

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Try to parse the file with ast
        ast.parse(source, filename=file_path)
        return False, None, None
    except SyntaxError as e:
        return True, str(e), e.lineno
    except Exception as e:
        return True, str(e), None


def check_files(files: List[str]) -> Dict[str, Tuple[str, Optional[int]]]:
    """Check multiple Python files for syntax errors.

    Args:
    ----
        files: List of Python file paths.

    Returns:
    -------
        Dictionary mapping file paths to (error_message, line_number) tuples.

    """
    errors: Dict[str, Tuple[str, Optional[int]]] = {}
    for file_path in files:
        has_error, error_message, line_number = check_syntax(file_path)
        if has_error and error_message is not None:
            errors[file_path] = (error_message, line_number)

    return errors


def show_error_context(
    file_path: str, line_number: Optional[int], context_lines: int = 3
) -> None:
    """Show the context around an error in a file.

    Args:
    ----
        file_path: Path to the file.
        line_number: Line number of the error.
        context_lines: Number of lines of context to show before and after the error.

    """
    if line_number is None:
        print(f"Cannot show context for {file_path} (line number unknown)")
        return

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)

        print(f"\nContext for error in {file_path}:")
        print("-" * 60)

        for i in range(start_line, end_line):
            line_marker = ">" if i == line_number - 1 else " "
            print(f"{line_marker} {i + 1:4d}: {lines[i].rstrip()}")

        print("-" * 60)
    except Exception as e:
        print(f"Error showing context: {e}")


def main() -> int:
    """Run the main program to find syntax errors."""
    try:
        print(f"Running find_syntax_errors.py on platform: {sys.platform}")
        print(f"Python version: {sys.version}")

        # Get files to check
        specific_files = sys.argv[1:] if len(sys.argv) > 1 else None
        python_files = find_python_files(specific_files)

        if not python_files:
            print("No Python files found to check.")
            return 0

        print(f"Checking {len(python_files)} Python files for syntax errors...")

        # Check files for syntax errors
        errors = check_files(python_files)

        # Print results
        if not errors:
            print("\nNo syntax errors found!")
            return 0

        print(f"\nFound syntax errors in {len(errors)} files:")

        for file_path, (error_message, line_number) in errors.items():
            line_info = f" (line {line_number})" if line_number else ""
            print(f"\n{file_path}{line_info}: {error_message}")
            show_error_context(file_path, line_number)

        return 1
    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
