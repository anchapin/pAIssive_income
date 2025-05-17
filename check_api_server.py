"""Script to check the API server code for syntax errors.

This script checks Python files for syntax errors using the ast module.
It can be used as a standalone script or imported as a module.
"""

import ast
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
MIN_ARGS = 2
DEFAULT_ENCODING = "utf-8"


def check_syntax(file_path: str) -> bool:
    """
    Check the syntax of a Python file.

    Args:
        file_path: Path to the Python file to check.

    Returns:
        True if the file has valid syntax, False otherwise.

    """
    if not os.path.exists(file_path):
        logger.error("❌ File not found: %s", file_path)
        return False

    if not os.path.isfile(file_path):
        logger.error("❌ Not a file: %s", file_path)
        return False

    try:
        # Use a context manager to ensure the file is properly closed
        with Path(file_path).open(encoding="utf-8") as file:
            source = file.read()

        # Parse the source code
        ast.parse(source, filename=file_path)
    except SyntaxError as error:
        # Format the syntax error message
        error_msg = format_syntax_error(file_path, error)
        # ruff: noqa: TRY400
        logger.error(error_msg)
        return False
    except Exception as e:
        logger.exception("❌ Error checking %s: %s", file_path, str(e))
        return False
    else:
        logger.info("✅ %s has valid syntax.", file_path)
        return True


def format_syntax_error(file_path: str, error: SyntaxError) -> str:
    """Format a syntax error message.

    Args:
        file_path: Path to the file with the syntax error.
        error: The SyntaxError exception.

    Returns:
        A formatted error message.
    """
    # Handle potential None values safely
    lineno = error.lineno if hasattr(error, 'lineno') and error.lineno is not None else 0

    # Keep the original offset value for the message
    offset_display = "None" if not hasattr(error, 'offset') or error.offset is None else error.offset

    # For calculations, use 0 if offset is None
    offset = 0 if not hasattr(error, 'offset') or error.offset is None else error.offset

    # Handle empty or None text
    if not hasattr(error, 'text') or error.text is None or error.text.strip() == "":
        text = "<unknown>"
    else:
        text = error.text.strip()

    # Handle None message
    msg = error.msg if hasattr(error, 'msg') and error.msg is not None else "Unknown syntax error"

    # Create the error message
    error_msg = (
        f"❌ Syntax error in {file_path} at line {lineno}, column {offset_display}:\n"
        f"   {text}\n"
    )

    # Add the pointer only if we have valid text and offset
    if text != "<unknown>" and offset > 0:
        error_msg += f"   {' ' * (offset - 1)}^\n"

    # Add the error message
    error_msg += f"   {msg}"

    return error_msg


def check_multiple_files(file_paths: List[str]) -> Tuple[List[str], List[str]]:
    """Check multiple Python files for syntax errors.

    Args:
        file_paths: List of paths to Python files to check.

    Returns:
        A tuple containing two lists:
        - List of files with valid syntax
        - List of files with syntax errors
    """
    valid_files = []
    invalid_files = []

    for file_path in file_paths:
        if check_syntax(file_path):
            valid_files.append(file_path)
        else:
            invalid_files.append(file_path)

    return valid_files, invalid_files


def main() -> int:
    """Main entry point for the script.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < MIN_ARGS:
        logger.error("Usage: python check_api_server.py <file_path> [<file_path> ...]")
        return 1

    file_paths = sys.argv[1:]
    valid_files, invalid_files = check_multiple_files(file_paths)

    # Print summary
    if invalid_files:
        logger.error("❌ %d file(s) have syntax errors:", len(invalid_files))
        for file_path in invalid_files:
            logger.error("  - %s", file_path)
        return 1
    else:
        logger.info("✅ All %d file(s) have valid syntax.", len(valid_files))
        return 0


if __name__ == "__main__":
    sys.exit(main())
