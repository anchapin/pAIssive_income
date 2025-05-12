#!/usr/bin/env python3

"""Install pre-commit hooks for the project.

This script installs pre-commit hooks for the project, ensuring that code quality
checks are run before each commit.
"""

import logging
import os
import subprocess
import sys

from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(command: list[str], check: bool = True) -> int:
    """Run a command and return the exit code.

    Args:
        command: The command to run as a list of strings.
        check: Whether to raise an exception if the command fails.

    Returns:
        The exit code of the command.

    """
    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
        )
        logging.info(result.stdout)
        if result.stderr:
            logging.error(result.stderr)
        return int(result.returncode)
    except subprocess.CalledProcessError as e:
        logging.exception(f"Command failed: {' '.join(command)}")
        logging.info(e.stdout)
        logging.exception(e.stderr)
        return int(e.returncode)
    except Exception:
        logging.exception(f"Error running command {' '.join(command)}")
        return 1


def check_pre_commit_installed() -> bool:
    """Check if pre-commit is installed.

    Returns:
        True if pre-commit is installed, False otherwise.

    """
    try:
        result = subprocess.run(
            ["pre-commit", "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        return bool(result.returncode == 0)
    except Exception:
        return False


def install_pre_commit() -> bool:
    """Install pre-commit if it's not already installed.

    Returns:
        True if pre-commit is installed successfully, False otherwise.

    """
    if check_pre_commit_installed():
        logging.info("pre-commit is already installed.")
        return True

    logging.info("Installing pre-commit...")
    return bool(run_command(["pip", "install", "pre-commit"], check=False) == 0)


def install_hooks() -> bool:
    """Install pre-commit hooks.

    Returns:
        True if hooks are installed successfully, False otherwise.

    """
    logging.info("Installing pre-commit hooks...")
    return bool(run_command(["pre-commit", "install"], check=False) == 0)


def main() -> int:
    """Run the main script functionality.

    Returns:
        Exit code.

    """
    # Get the root directory of the project
    root_dir = Path(__file__).parent

    # Change to the root directory
    os.chdir(root_dir)

    # Install pre-commit
    if not install_pre_commit():
        logging.error("Failed to install pre-commit.")
        return 1

    # Install hooks
    if not install_hooks():
        logging.error("Failed to install pre-commit hooks.")
        return 1

    logging.info("\nPre-commit hooks installed successfully!")
    logging.info("\nYou can now run pre-commit checks manually with:")
    logging.info("  pre-commit run --all-files")
    logging.info("\nOr use the unified script:")
    logging.info("  python scripts/manage_quality.py pre-commit")
    logging.info("\nPre-commit hooks will also run automatically before each commit.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
