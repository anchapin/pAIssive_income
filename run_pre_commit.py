#!/usr/bin/env python3

"""
Script to run pre-commit with proper exclusions for .venv directory.

This script finds all Python files in the repository, excluding those in the .venv directory,
and runs pre-commit on them.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_python_files(exclude_patterns: Optional[list[str]] = None) -> list[str]:
    """
    Find all Python files in the repository, excluding those matching exclude patterns.

    Args:
        exclude_patterns: List of patterns to exclude

    Returns:
        List of Python files

    """
    if exclude_patterns is None:
        exclude_patterns = [
            ".venv",
            "venv",
            ".git",
            "__pycache__",
            "node_modules",
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


def _safe_subprocess_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:  # noqa: ANN003
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    if "cwd" in kwargs and isinstance(kwargs["cwd"], Path):
        kwargs["cwd"] = str(kwargs["cwd"])
    allowed_keys = {
        "cwd",
        "timeout",
        "check",
        "shell",
        "text",
        "capture_output",
        "input",
        "encoding",
        "errors",
        "env",
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
    return subprocess.run(cmd, check=False, **filtered_kwargs)


def run_pre_commit(files: list[str]) -> int:
    """
    Run pre-commit on the specified files.

    Args:
        files: List of files to run pre-commit on

    Returns:
        Exit code from pre-commit

    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    if not files:
        logger.info("No Python files found to check.")
        return 0

    logger.info("Running pre-commit on %d files...", len(files))

    # Run pre-commit on the files
    cmd = ["pre-commit", "run", "--files", *files]
    result = _safe_subprocess_run(cmd)

    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)

    return int(result.returncode)


def main() -> None:
    """Execute the main script functionality."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    # Find Python files
    python_files = find_python_files()

    # Run pre-commit
    exit_code = run_pre_commit(python_files)

    if exit_code != 0:
        logger.error("Pre-commit checks failed. Please fix the issues and try again.")
    else:
        logger.info("Pre-commit checks passed successfully.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
