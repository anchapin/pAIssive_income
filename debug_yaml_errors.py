#!/usr/bin/env python3
"""Script to debug specific YAML syntax errors."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def debug_yaml_errors() -> None:
    """Debug specific YAML syntax errors in workflow files."""
    # Files with errors and their line numbers
    error_files = [
        (".github/workflows/codeql-macos.yml", 317, 319),
        (".github/workflows/codeql-windows.yml", 184, 185),
        (".github/workflows/codeql.yml", 310, 313),
    ]

    for filepath, error_line, _ in error_files:
        logger.info("=== %s ===", filepath)
        logger.info("Error around line %d:", error_line)

        try:
            with Path(filepath).open(encoding="utf-8") as f:
                lines = f.readlines()

            # Show context around the error
            start = max(0, error_line - 5)
            end = min(len(lines), error_line + 5)

            for i in range(start, end):
                line_num = i + 1
                marker = ">>> " if line_num == error_line else "    "
                logger.info("%s%3d: %r", marker, line_num, lines[i])

        except OSError:
            logger.exception("Error reading %s", filepath)


if __name__ == "__main__":
    debug_yaml_errors()
