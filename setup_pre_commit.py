"""setup_pre_commit - Module for setting up pre-commit hooks.

This script installs pre-commit hooks for the repository to ensure code quality
and consistency. It checks if pre-commit is installed and installs it if needed,
then sets up the hooks according to the configuration in .pre-commit-config.yaml.
"""

# Standard library imports
import subprocess
import sys

from typing import List
from typing import Tuple


def run_command(command: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
    ----
        command: The command to run as a list of strings.
        check: Whether to raise an exception if the command fails.

    Returns:
    -------
        A tuple of (exit_code, stdout, stderr).

    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check,
            shell=sys.platform == "win32",
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return e.returncode, e.stdout, e.stderr


def check_pre_commit_installed() -> bool:
    """Check if pre-commit is installed.

    Returns
    -------
        True if pre-commit is installed, False otherwise.

    """
    try:
        exit_code, _, _ = run_command(["pre-commit", "--version"], check=False)
        return exit_code == 0
    except Exception:
        return False


def install_pre_commit() -> bool:
    """Install pre-commit if it's not already installed.

    Returns
    -------
        True if installation was successful, False otherwise.

    """
    print("Installing pre-commit...")
    exit_code, stdout, stderr = run_command(
        ["pip", "install", "pre-commit"], check=False
    )

    if exit_code != 0:
        print(f"Failed to install pre-commit: {stderr}")
        return False

    print("pre-commit installed successfully.")
    return True


def setup_hooks() -> bool:
    """Set up pre-commit hooks.

    Returns
    -------
        True if setup was successful, False otherwise.

    """
    print("Setting up pre-commit hooks...")

    # Install the hooks
    exit_code, stdout, stderr = run_command(["pre-commit", "install"], check=False)

    if exit_code != 0:
        print(f"Failed to install pre-commit hooks: {stderr}")
        return False

    print("Pre-commit hooks installed successfully.")

    # Update the hooks to the latest versions
    print("Updating pre-commit hooks...")
    exit_code, stdout, stderr = run_command(["pre-commit", "autoupdate"], check=False)

    if exit_code != 0:
        print(f"Failed to update pre-commit hooks: {stderr}")
        # Not a critical error, so continue
        print("Continuing with existing hook versions...")
    else:
        print("Pre-commit hooks updated successfully.")

    return True


def main() -> int:
    """Set up pre-commit hooks.

    Returns
    -------
        0 if successful, 1 otherwise.

    """
    print(f"Setting up pre-commit hooks for platform: {sys.platform}")

    # Check if pre-commit is installed
    if not check_pre_commit_installed():
        print("pre-commit is not installed.")
        if not install_pre_commit():
            print("Failed to install pre-commit. Please install it manually:")
            print("  pip install pre-commit")
            return 1

    # Set up the hooks
    if not setup_hooks():
        print("Failed to set up pre-commit hooks.")
        return 1

    print("\nPre-commit hooks setup completed successfully!")
    print("\nYou can run pre-commit manually with:")
    print("  pre-commit run --all-files")
    print("  pre-commit run <hook-id> --all-files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
