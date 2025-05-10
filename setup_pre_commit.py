"""setup_pre_commit - Module for setting up pre-commit hooks.

This script installs pre-commit hooks for the repository to ensure code quality
and consistency. It checks if pre-commit is installed and installs it if needed,
then sets up the hooks according to the configuration in .pre-commit-config.yaml.
"""

# Standard library imports
import subprocess
import sys
from typing import List, Tuple


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
        ["uv", "pip", "install", "pre-commit"], check=False
    )
    print("  uv pip install pre-commit")
    return exit_code == 0
    """Install pre-commit if it's not already installed.

    Returns
    -------
        True if installation was successful, False otherwise.

    """
    print("Installing pre-commit...")
    exit_code, stdout, stderr = run_command(
        ["uv", "pip", "install", "pre-commit"], check=False
print("  uv pip install pre-commit")
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
