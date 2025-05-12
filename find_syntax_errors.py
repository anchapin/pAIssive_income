"""find_syntax_errors.py - Script to identify syntax errors in Python files.

This script scans Python files for syntax errors and provides detailed information
about the errors found, including line numbers and error messages.
"""

import ast
import logging
import os
import sys
import traceback

from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def find_python_files(specific_files: Optional[list[str]] = None) -> list[str]:
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


def check_syntax(file_path: str) -> tuple[bool, Optional[str], Optional[int]]:
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

    except SyntaxError as e:
        return True, str(e), e.lineno
    except Exception as e:
        return True, str(e), None
    else:
        # Try to parse the file with ast
        ast.parse(source, filename=file_path)
        return False, None, None


def check_files(files: list[str]) -> dict[str, tuple[str, Optional[int]]]:
    """Check multiple Python files for syntax errors.

    Args:
    ----
        files: List of Python file paths.

    Returns:
    -------
        Dictionary mapping file paths to (error_message, line_number) tuples.

    """
    errors: dict[str, tuple[str, Optional[int]]] = {}
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
        logging.warning(f"Cannot show context for {file_path} (line number unknown)")
        return

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)

        logging.info(f"\nContext for error in {file_path}:")
        logging.info("-" * 60)

        for i in range(start_line, end_line):
            line_marker = ">" if i == line_number - 1 else " "
            logging.info(f"{line_marker} {i + 1:4d}: {lines[i].rstrip()}")

        logging.info("-" * 60)
    except Exception:
        logging.exception("Error showing context:")


def main() -> int:
    """Run the main program to find syntax errors."""
    try:
        logging.info(f"Running find_syntax_errors.py on platform: {sys.platform}")
        logging.info(f"Python version: {sys.version}")

        # Get files to check
        specific_files = sys.argv[1:] if len(sys.argv) > 1 else None
        python_files = find_python_files(specific_files)

        if not python_files:
            logging.info("No Python files found to check.")
            return 0

        logging.info(f"Checking {len(python_files)} Python files for syntax errors...")

        # Check files for syntax errors
        errors = check_files(python_files)

        # Print results
        if not errors:
            logging.info("\nNo syntax errors found!")
            return 0

        logging.info(f"\nFound syntax errors in {len(errors)} files:")

        for file_path, (error_message, line_number) in errors.items():
            line_info = f" (line {line_number})" if line_number else ""
            logging.error(f"\n{file_path}{line_info}: {error_message}")
            show_error_context(file_path, line_number)

    except Exception:
        logging.exception("Error in main function:")
        traceback.print_exc()
        return 1
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
