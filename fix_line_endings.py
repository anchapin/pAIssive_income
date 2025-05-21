#!/usr/bin/env python3
"""Fix line endings in a file."""

import logging
import os
import sys

try:
    from pathlib import Path
except ImportError:
    print("Error: pathlib module not found. Please install it.")
    sys.exit(1)

logger = logging.getLogger(__name__)

# Constants
EXPECTED_ARG_COUNT = 2


def fix_line_endings(file_path: str) -> None:
    """
    Fix line endings in a file.

    Args:
        file_path: Path to the file to fix

    """
    path = Path(file_path)
    with path.open("rb") as f:
        content = f.read()

    # Replace all line endings with the platform-specific line ending
    if os.name == "nt":  # Windows
        content = content.replace(b"\n", b"\r\n")
    else:  # Unix/Linux/macOS
        content = content.replace(b"\r\n", b"\n")

    with path.open("wb") as f:
        f.write(content)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    if len(sys.argv) != EXPECTED_ARG_COUNT:
        logger.error("Usage: %s <file_path>", sys.argv[0])
        sys.exit(1)

    file_path = sys.argv[1]
    path = Path(file_path)
    if not path.is_file():
        logger.error("Error: %s is not a file", file_path)
        sys.exit(1)

    fix_line_endings(file_path)
    logger.info("Fixed line endings in %s", file_path)
