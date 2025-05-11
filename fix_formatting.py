#!/usr/bin/env python3
"""Fix formatting issues in the codebase.

This script runs Ruff formatter on the files that were identified as needing reformatting
in the GitHub Actions workflow.

Note: This project uses Ruff as the primary formatter, not Black. Running Black directly
may cause formatting conflicts with Ruff. Always use Ruff for formatting to ensure
consistency with the pre-commit hooks.
"""

import argparse
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

# Files that need reformatting according to the GitHub Actions workflow
FILES_TO_FIX = [
    "test_security_fixes.py",
    "regenerate_venv.py",
    "fix_potential_secrets.py",
    "common_utils/secrets/secrets_manager.py",
    "fix_security_issues.py",
]


def run_command(cmd: list[str], cwd: Optional[str] = None) -> bool:
    """Run a command and return whether it succeeded.

    Args:
        cmd: The command to run
        cwd: The directory to run the command in

    Returns:
        bool: True if the command succeeded, False otherwise
    """
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.exception(f"Command failed with exit code {e.returncode}")
        logger.info(f"Stdout: {e.stdout}")
        logger.info(f"Stderr: {e.stderr}")
        return False
    return True


def fix_formatting_with_ruff(files: list[str]) -> bool:
    """Fix formatting issues with Ruff.

    Args:
        files: List of files to fix

    Returns:
        bool: True if all files were fixed successfully, False otherwise
    """
    # Normalize paths
    normalized_files = [str(Path(file).resolve()) for file in files]

    # Run Ruff formatter
    cmd = ["ruff", "format", *normalized_files]
    return run_command(cmd)


def fix_formatting_with_black(files: list[str]) -> bool:
    """Fix formatting issues with Black.

    Args:
        files: List of files to fix

    Returns:
        bool: True if all files were fixed successfully, False otherwise
    """
    # Normalize paths
    normalized_files = [str(Path(file).resolve()) for file in files]

    # Run Black formatter
    cmd = ["black", *normalized_files]
    return run_command(cmd)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fix formatting issues in the codebase"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Files to fix (defaults to the files identified in the GitHub Actions workflow)",
    )
    parser.add_argument(
        "--use-black",
        action="store_true",
        help="Use Black instead of Ruff for formatting",
    )
    return parser.parse_args()


def main() -> int:
    """Fix formatting issues in the codebase.

    Returns:
        int: 0 on success, 1 on failure
    """
    args = parse_args()

    # Use the files from the command line if provided, otherwise use the default list
    files_to_fix = args.files if args.files else FILES_TO_FIX

    # Check if the files exist
    for file in files_to_fix:
        if not os.path.exists(file):
            logger.error(f"File not found: {file}")
            return 1

    # Fix formatting issues
    if args.use_black:
        success = fix_formatting_with_black(files_to_fix)
    else:
        success = fix_formatting_with_ruff(files_to_fix)

    if success:
        logger.info("Formatting issues fixed successfully")
        return 0
    else:
        logger.error("Failed to fix formatting issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
