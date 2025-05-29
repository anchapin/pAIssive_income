"""
setup_pre_commit - Module for setting up pre-commit hooks.

This script installs pre-commit hooks for the repository to ensure code quality
and consistency. It checks if pre-commit is installed and installs it if needed,
then sets up the hooks according to the configuration in .pre-commit-config.yaml.
"""

from __future__ import annotations

# Standard library imports
import logging
import shutil
import subprocess
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


# Set up a dedicated logger for this module


def run_command(command: list[str], check: bool = True) -> tuple[int, str, str]:
    """
    Run a command and return the exit code, stdout, and stderr.

    Args:
    ----
        command: The command to run as a list of strings.
        check: Whether to raise an exception if the command fails.

    Returns:
    -------
        A tuple of (exit_code, stdout, stderr).

    """
    try:
        # Ensure the first item in command is a full path to the executable
        if command and not Path(command[0]).is_absolute():
            executable = shutil.which(command[0])
            if executable:
                command[0] = executable
            else:
                logger.error("Command not found: %s", command[0])
                return -1, "", f"Command not found: {command[0]}"

        # Always use shell=False for security
        # nosec comment below tells security scanners this is safe as we control the input
        result = subprocess.run(  # nosec B603
            command,
            capture_output=True,
            text=True,
            check=check,
            shell=False,
        )
        # Ensure types are consistent for return
        result_code = result.returncode
        result_stdout = result.stdout if result.stdout is not None else ""
        result_stderr = result.stderr if result.stderr is not None else ""

    except subprocess.CalledProcessError as e:
        # Ensure types are consistent for return in case of exception
        stdout_val = e.stdout if e.stdout is not None else ""
        stderr_val = e.stderr if e.stderr is not None else ""
        logger.exception(  # TRY401: Ensure exception object is not in message
            "Error running command %s", " ".join(command)
        )
        return e.returncode, stdout_val, stderr_val
    except FileNotFoundError:
        logger.exception(  # TRY401: Ensure exception object is not in message
            "Command not found: %s. Please ensure it is installed and in your PATH.",
            command[0],
        )
        return -1, "", "Command not found"  # Indicate error clearly
    else:  # TRY300: Moved return to else block
        return result_code, result_stdout, result_stderr


def check_pre_commit_installed() -> bool:
    """
    Check if pre-commit is installed.

    Returns
    -------
        True if pre-commit is installed, False otherwise.

    """
    exit_code, _, _ = run_command(["pre-commit", "--version"], check=False)
    return exit_code == 0


def install_pre_commit() -> bool:
    """
    Install pre-commit if it's not already installed using uv.

    Returns
    -------
        True if installation was successful, False otherwise.

    """
    logger.info("Installing pre-commit using uv...")
    # Use uv for installation
    exit_code, stdout, stderr = run_command(
        ["uv", "pip", "install", "pre-commit"], check=False
    )

    if exit_code != 0:
        logger.error("Failed to install pre-commit using uv: %s", stderr)
        # Provide alternative pip command as a fallback suggestion
        logger.error("You might need to install it manually: pip install pre-commit")
        return False

    logger.info("pre-commit installed successfully using uv.")
    return True


def setup_hooks() -> bool:
    """
    Set up pre-commit hooks.

    Returns
    -------
        True if installation was successful, False otherwise.

    """
    logger.info("Setting up pre-commit hooks...")

    # Install the hooks
    exit_code, stdout, stderr = run_command(["pre-commit", "install"], check=False)

    if exit_code != 0:
        logger.error("Failed to install pre-commit hooks: %s", stderr)
        return False

    logger.info("Pre-commit hooks installed successfully.")

    # Update the hooks to the latest versions
    logger.info("Updating pre-commit hooks...")
    exit_code, stdout, stderr = run_command(["pre-commit", "autoupdate"], check=False)

    if exit_code != 0:
        logger.error("Failed to update pre-commit hooks: %s", stderr)
        # Not a critical error, so continue
        logger.info("Continuing with existing hook versions...")
    else:
        logger.info("Pre-commit hooks updated successfully.")

    return True


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    """
    Set up pre-commit hooks.

    Returns
    -------
        0 if successful, 1 otherwise.

    """
    logger.info("Setting up pre-commit hooks for platform: %s", sys.platform)

    # Check if pre-commit is installed
    if not check_pre_commit_installed():
        logger.info("pre-commit is not installed.")
        if not install_pre_commit():  # This now uses uv
            # install_pre_commit already logs detailed error and suggestion
            return 1
    else:
        logger.info("pre-commit is already installed.")

    # Set up the hooks
    if not setup_hooks():
        logger.error("Failed to set up pre-commit hooks.")
        return 1

    logger.info("\nPre-commit hooks setup completed successfully!")
    logger.info("You can run pre-commit manually with:")
    logger.info("  pre-commit run --all-files")
    logger.info("  pre-commit run <hook-id> --all-files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
