#!/usr/bin/env python3

"""
Install pre-commit hooks for the project.

This script installs pre-commit hooks for the project, ensuring that code quality
checks are run before each commit.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import cast

# Create a dedicated logger for this module
logger = logging.getLogger(__name__)
# Configure the logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(command: list[str], check: bool = True) -> int:
    """
    Run a command and return the exit code.

    Args:
        command: The command to run as a list of strings.
        check: Whether to raise an exception if the command fails.

    Returns:
        int: The exit code of the command. 0 for success, non-zero for failure.

    """
    cmd_str = " ".join(command)
    logger.debug("Running command: %s", cmd_str)

    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        return cast("int", result.returncode)
    except subprocess.CalledProcessError as e:
        logger.exception("Command failed: %s", cmd_str)
        if e.stdout:
            logger.info(e.stdout)
        if e.stderr:
            logger.exception(e.stderr)
        return cast("int", e.returncode)
    except (OSError, FileNotFoundError):
        logger.exception("Error running command %s", cmd_str)
        return 1


def check_pre_commit_installed() -> bool:
    """
    Check if pre-commit is installed.

    Returns:
        bool: True if pre-commit is installed, False otherwise.

    """
    try:
        # Use a safer approach with full path if possible
        import shutil

        pre_commit_path = shutil.which("pre-commit")
        if pre_commit_path:
            cmd = [pre_commit_path, "--version"]
        else:
            cmd = ["pre-commit", "--version"]

        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        # More specific exception handling
        return False


def install_pre_commit() -> bool:
    """
    Install pre-commit if it's not already installed.

    Returns:
        True if pre-commit is installed successfully, False otherwise.

    """
    if check_pre_commit_installed():
        logger.info("pre-commit is already installed.")
        return True

    logger.info("Installing pre-commit...")
    return run_command(["pip", "install", "pre-commit"], check=False) == 0


def install_hooks() -> bool:
    """
    Install pre-commit hooks.

    Returns:
        True if hooks are installed successfully, False otherwise.

    """
    logger.info("Installing pre-commit hooks...")
    return run_command(["pre-commit", "install"], check=False) == 0


def main() -> int:
    """
    Run the main script functionality.

    Returns:
        int: 0 for success, 1 for failure

    """
    try:
        # Get the root directory of the project
        root_dir = Path(__file__).parent

        # Change to the root directory
        os.chdir(root_dir)

        # Install pre-commit
        if not install_pre_commit():
            logger.error("Failed to install pre-commit.")
            return 1

        # Install hooks
        if not install_hooks():
            logger.error("Failed to install pre-commit hooks.")
            return 1

        logger.info("\nPre-commit hooks installed successfully!")
        logger.info("\nYou can now run pre-commit checks manually with:")
        logger.info("  pre-commit run --all-files")
        logger.info("\nOr use the unified script:")
        logger.info("  python scripts/manage_quality.py pre-commit")
        logger.info(
            "\nPre-commit hooks will also run automatically before each commit."
        )

        return 0

    except Exception:
        logger.exception("Unexpected error during pre-commit setup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
