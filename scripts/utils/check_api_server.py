"""Script to check the API server code for syntax errors."""

import ast
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
MIN_ARGS = 2


def check_syntax(file_path: str) -> bool:
    """Check the syntax of a Python file.

    Args:
        file_path: Path to the Python file to check.

    Returns:
        True if the file has valid syntax, False otherwise.
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            source = file.read()

        # Parse the source code
        ast.parse(source)
    except SyntaxError as e:
        # Custom formatting for syntax errors
        error_msg = (
            f"❌ Syntax error in {file_path} at line {e.lineno}, column {e.offset}:\n"
            f"   {e.text.strip()}\n"
            f"   {' ' * (e.offset - 1)}^\n"
            f"   {e.msg}"
        )
        # ruff: noqa: TRY400
        logger.error(error_msg)
        return False
    except Exception:
        logger.exception("❌ Error checking %s:", file_path)
        return False
    else:
        logger.info("✅ %s has valid syntax.", file_path)
        return True


if __name__ == "__main__":
    if len(sys.argv) < MIN_ARGS:
        logger.error("Usage: python check_api_server.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not check_syntax(file_path):
        sys.exit(1)
