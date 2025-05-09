#!/usr/bin/env python3

"""Install pre-commit hooks for the project.

This script installs pre-commit hooks for the project, ensuring that code quality
checks are run before each commit.
"""

import os
import subprocess
import sys

from pathlib import Path


def run_command(command, check=True):
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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return e.returncode
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return 1


def check_pre_commit_installed():
    """Check if pre-commit is installed.

    Returns:
        True if pre-commit is installed, False otherwise.

    """
    try:
        result = subprocess.run(
            ["pre-commit", "--version"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def install_pre_commit():
    """Install pre-commit if it's not already installed.

    Returns:
        True if pre-commit is installed successfully, False otherwise.

    """
    if check_pre_commit_installed():
        print("pre-commit is already installed.")
        return True

    print("Installing pre-commit...")
    return run_command(["pip", "install", "pre-commit"], check=False) == 0


def install_hooks():
    """Install pre-commit hooks.

    Returns:
        True if hooks are installed successfully, False otherwise.

    """
    print("Installing pre-commit hooks...")
    return run_command(["pre-commit", "install"], check=False) == 0


def main():
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
        print("Failed to install pre-commit.")
        return 1

    # Install hooks
    if not install_hooks():
        print("Failed to install pre-commit hooks.")
        return 1

    print("\nPre-commit hooks installed successfully!")
    print("\nYou can now run pre-commit checks manually with:")
    print("  pre-commit run --all-files")
    print("\nOr use the unified script:")
    print("  python scripts/manage_quality.py pre-commit")
    print("\nPre-commit hooks will also run automatically before each commit.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
