#!/usr/bin/env python3
"""Fix line endings in a file."""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
EXPECTED_ARG_COUNT = 2


def fix_line_endings(file_path: str) -> None:
    """Fix line endings in a file.

    Args:
        file_path: Path to the file to fix
    """
    with open(file_path, "rb") as f:
        content = f.read()

    # Replace all line endings with the platform-specific line ending
    if os.name == "nt":  # Windows
        content = content.replace(b"\n", b"\r\n")
    else:  # Unix/Linux/macOS
        content = content.replace(b"\r\n", b"\n")

    with open(file_path, "wb") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) != EXPECTED_ARG_COUNT:
        logger.error(f"Usage: {sys.argv[0]} <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        logger.error(f"Error: {file_path} is not a file")
        sys.exit(1)

    fix_line_endings(file_path)
    logger.info(f"Fixed line endings in {file_path}")
