"""setup_pre_commit - Module for setting up pre-commit hooks.

This script installs pre-commit hooks for the repository to ensure code quality
and consistency. It checks if pre-commit is installed and installs it if needed,
then sets up the hooks according to the configuration in .pre-commit-config.yaml.
"""

# Standard library imports
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(command: list[str], check: bool = True) -> tuple[int, str, str]:
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
        # Always use shell=False for security
        result = subprocess.run(
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
        logging.exception(  # TRY401: Ensure exception object is not in message
            "Error running command {}".format(" ".join(command))
        )
        return e.returncode, stdout_val, stderr_val
    except FileNotFoundError:
        logging.exception(  # TRY401: Ensure exception object is not in message
            f"Command not found: {command[0]}. "  # Replaced f-string
            "Please ensure it is installed and in your PATH."
        )
        return -1, "", "Command not found"  # Indicate error clearly
    else:  # TRY300: Moved return to else block
        return result_code, result_stdout, result_stderr


def check_pre_commit_installed() -> bool:
    """Check if pre-commit is installed.

    Returns
    -------
        True if pre-commit is installed, False otherwise.

    """
    exit_code, _, _ = run_command(["pre-commit", "--version"], check=False)
    return exit_code == 0


def install_pre_commit() -> bool:
    """Install pre-commit if it's not already installed using uv.

    Returns
    -------
        True if installation was successful, False otherwise.

    """
    logging.info("Installing pre-commit using uv...")
    # Use uv for installation
    exit_code, stdout, stderr = run_command(
        ["uv", "pip", "install", "pre-commit"], check=False
    )

    if exit_code != 0:
        logging.error(
            f"Failed to install pre-commit using uv: {stderr}"
        )  # Replaced f-string
        # Provide alternative pip command as a fallback suggestion
        logging.error("You might need to install it manually: pip install pre-commit")
        return False

    logging.info("pre-commit installed successfully using uv.")
    return True


def setup_hooks() -> bool:
    """Set up pre-commit hooks.

    Returns
    -------
        True if installation was successful, False otherwise.

    """
    logging.info("Setting up pre-commit hooks...")

    # Install the hooks
    exit_code, stdout, stderr = run_command(["pre-commit", "install"], check=False)

    if exit_code != 0:
        logging.error(
            f"Failed to install pre-commit hooks: {stderr}"
        )  # Replaced f-string
        return False

    logging.info("Pre-commit hooks installed successfully.")

    # Update the hooks to the latest versions
    logging.info("Updating pre-commit hooks...")
    exit_code, stdout, stderr = run_command(["pre-commit", "autoupdate"], check=False)

    if exit_code != 0:
        logging.error(
            f"Failed to update pre-commit hooks: {stderr}"
        )  # Replaced f-string
        # Not a critical error, so continue
        logging.info("Continuing with existing hook versions...")
    else:
        logging.info("Pre-commit hooks updated successfully.")

    return True


def main() -> int:
    """Set up pre-commit hooks.

    Returns
    -------
        0 if successful, 1 otherwise.

    """
    logging.info(
        f"Setting up pre-commit hooks for platform: {sys.platform}"
    )  # Replaced f-string

    # Check if pre-commit is installed
    if not check_pre_commit_installed():
        logging.info("pre-commit is not installed.")
        if not install_pre_commit():  # This now uses uv
            # install_pre_commit already logs detailed error and suggestion
            return 1
    else:
        logging.info("pre-commit is already installed.")

    # Set up the hooks
    if not setup_hooks():
        logging.error("Failed to set up pre-commit hooks.")
        return 1

    logging.info("\nPre-commit hooks setup completed successfully!")
    logging.info("You can run pre-commit manually with:")
    logging.info("  pre-commit run --all-files")
    logging.info("  pre-commit run <hook-id> --all-files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
