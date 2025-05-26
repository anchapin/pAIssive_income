#!/usr/bin/env python3

# Configure logging
logger = logging.getLogger(__name__)


"""Script to run pre-commit on all Python files in the repository, excluding the .venv directory."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path



def find_python_files() -> list[str]:
    """Find all Python files in the repository, excluding the .venv directory."""
    exclude_patterns = [
        ".venv",
        "venv",
        "env",
        ".git",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
    ]

    python_files: list[str] = []

    for root, _, files in os.walk("."):
        # Skip directories matching exclude patterns
        if any(pattern in root for pattern in exclude_patterns):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = str(Path(root) / file)
                python_files.append(file_path)

    return python_files


def run_pre_commit(files: list[str]) -> int:
    """
    Run pre-commit on the specified files.

    Args:
        files: List of files to run pre-commit on

    Returns:
        Exit code from pre-commit

    """
    if not files:
        logger.info("No Python files found to check.")
        return 0

    logger.info("Running pre-commit on %d files...", len(files))

    # Run pre-commit on the files
    cmd = ["pre-commit", "run", "--files", *files]

    # Use check=False to avoid raising an exception on non-zero exit code
    # nosec B603 S603 - We're only running pre-commit with Python files from the repo
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )  # nosec B603 S603

    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)

    return int(result.returncode)


def main() -> None:
    """Execute the main script functionality."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # Find Python files
    python_files = find_python_files()

    # Run pre-commit in batches to avoid command line length limits
    batch_size = 50
    exit_code = 0

    for i in range(0, len(python_files), batch_size):
        batch = python_files[i : i + batch_size]
        logger.info(
            "Processing batch %d of %d...",
            i // batch_size + 1,
            (len(python_files) + batch_size - 1) // batch_size,
        )
        batch_exit_code = run_pre_commit(batch)
        if batch_exit_code != 0:
            exit_code = batch_exit_code

    if exit_code != 0:
        logger.error("Pre-commit checks failed. Please fix the issues and try again.")
    else:
        logger.info("Pre-commit checks passed successfully.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
