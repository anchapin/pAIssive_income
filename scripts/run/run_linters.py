#!/usr/bin/env python3
"""
Run linters on all Python files except those in node_modules.

This script runs ruff (format and lint) on all Python files in the project,
excluding files in node_modules and other directories specified in
.gitignore.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Directories to exclude
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def run_command(
    command: list[str], cwd: Optional[str] = None, capture_output: bool = True
) -> tuple[int, Optional[str], Optional[str]]:
    """
    Run a command and return its output.

    Args:
        command: The command to run as a list of strings
        cwd: The working directory to run the command in
        capture_output: Whether to capture the command output

    Returns:
        Tuple of (exit_code, stdout, stderr)

    """
    logger.info("Running command: %s", " ".join(command))
    try:
        # nosec comment below tells security scanners this is safe as we control the input
        result = subprocess.run(  # nosec S603
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False,
        )
    except Exception as e:
        logger.exception("Error running command")
        return 1, None, str(e)
    else:
        return (
            result.returncode,
            result.stdout if result.stdout else None,
            result.stderr if result.stderr else None,
        )


def find_python_files() -> list[str]:
    """
    Find all Python files in the project, excluding node_modules.

    Returns:
        List of Python file paths

    """
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith(".py"):
                file_path = str(Path(root) / file)
                python_files.append(file_path)

    return python_files


def run_ruff_format(files: list[str], check_only: bool = False) -> bool:
    """
    Run ruff format on the specified files.

    Args:
        files: List of files to run ruff format on
        check_only: Whether to run in check mode (don't modify files)

    Returns:
        True if successful, False otherwise

    """
    if not files:
        logger.info("No Python files found to format with ruff")
        return True

    command = ["ruff", "format"]
    if check_only:
        command.append("--check")
    command.extend(files)

    exit_code, stdout, stderr = run_command(command)
    if exit_code != 0:
        logger.error("Ruff format failed: %s", stderr if stderr else stdout)
        return False

    logger.info("Ruff format succeeded")
    return True


def run_ruff(files: list[str], fix: bool = False) -> bool:
    """
    Run ruff on the specified files.

    Args:
        files: List of files to run ruff on
        fix: Whether to fix issues automatically

    Returns:
        True if successful, False otherwise

    """
    if not files:
        logger.info("No Python files found to check with ruff")
        return True

    command = ["ruff", "check"]
    if fix:
        command.append("--fix")
    command.extend(files)

    exit_code, stdout, stderr = run_command(command)
    if exit_code != 0:
        logger.error("Ruff failed: %s", stdout)
        return False

    logger.info("Ruff succeeded")
    return True


def main() -> int:
    """
    Run linters on all Python files.

    Returns:
        0 on success, 1 on failure

    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Run ruff on all Python files except those in node_modules"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run in check mode (don't modify files)",
    )
    parser.add_argument(
        "--ruff-format-only",
        action="store_true",
        help="Run only ruff format",
    )
    parser.add_argument(
        "--ruff-only",
        action="store_true",
        help="Run only ruff",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix issues automatically",
    )
    args = parser.parse_args()

    # Find all Python files
    python_files = find_python_files()
    logger.info("Found %d Python files", len(python_files))

    success = True

    # Run ruff format
    if not args.ruff_only and not run_ruff_format(
        python_files, check_only=args.check_only and not args.fix
    ):
        success = False

    # Run ruff lint
    if (
        not args.ruff_format_only
        and not run_ruff(
            python_files, fix=args.fix
        )  # Assuming ruff (lint) might also fix
    ):
        success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
