#!/usr/bin/env python3
"""Test script to verify that syntax errors have been fixed."""

import logging
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


def check_syntax_errors(file_path: str) -> bool:
    """
    Check if a Python file has syntax errors.

    Args:
        file_path: Path to the Python file

    Returns:
        True if no syntax errors, False otherwise

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Try to compile the file
        compile(content, file_path, "exec")
        return True
    except SyntaxError as e:
        logger.exception(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        logger.exception(f"Error checking {file_path}: {e}")
        return False


def main() -> int:
    """Main function to test syntax fixes."""
    logging.basicConfig(level=logging.INFO)

    # Files that were fixed
    fixed_files = [
        "init_agent_db.py",
        "main.py",
        "app_flask/middleware/logging_middleware.py",
        "scripts/check_logging_in_modified_files.py",
        "scripts/fix/fix_security_issues.py",
        "logging_config.py"
    ]

    all_good = True

    for file_path in fixed_files:
        if Path(file_path).exists():
            if check_syntax_errors(file_path):
                logger.info(f"✓ {file_path} - No syntax errors")
            else:
                logger.error(f"✗ {file_path} - Has syntax errors")
                all_good = False
        else:
            logger.warning(f"? {file_path} - File not found")

    if all_good:
        logger.info("All checked files have no syntax errors!")
        return 0
    logger.error("Some files still have syntax errors")
    return 1


if __name__ == "__main__":
    sys.exit(main())
