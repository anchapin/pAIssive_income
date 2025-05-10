#!/usr/bin/env python3
"""Regenerate the virtual environment.

This script removes the existing virtual environment and creates a new one,
then installs all the required dependencies from requirements.txt and
requirements-dev.txt.
"""

import logging
import os
import platform
import shutil
import subprocess
import sys

from subprocess import CompletedProcess
from typing import NoReturn
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(
    command: list[str], cwd: Optional[str] = None, capture_output: bool = True
) -> Optional[str]:
    """Run a command and return its output.

    Args:
        command: The command to run as a list of strings
        cwd: The working directory to run the command in
        capture_output: Whether to capture the command output

    Returns:
        The command output as a string if successful, None otherwise
    """
    logging.info(f"Running command: {' '.join(command)}")
    try:
        result: CompletedProcess[str] = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            logging.error(f"Command failed with exit code {result.returncode}")
            logging.error(f"STDOUT: {result.stdout}")
            logging.error(f"STDERR: {result.stderr}")
            return None
    except Exception:
        logging.exception("Error running command")
        return None
    else:
        # Explicitly cast to Optional[str] to satisfy mypy
        return result.stdout if result.stdout is not None else None


def is_venv_active() -> bool:
    """Check if a virtual environment is active."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def check_venv_status() -> bool:
    """Check if we're in a virtual environment.

    Returns:
        bool: True if it's safe to proceed, False otherwise
    """
    if is_venv_active():
        logging.warning("You are currently in a virtual environment.")
        logging.warning("This script will deactivate it and create a new one.")
        logging.warning("Please run this script from outside any virtual environment.")
        return False
    return True


def remove_venv_windows(venv_dir: str, python_exe: str) -> tuple[bool, str]:
    """Remove virtual environment on Windows.

    Args:
        venv_dir: Path to the virtual environment
        python_exe: Python executable path

    Returns:
        tuple: (success, venv_dir) - success flag and the venv directory to use
    """
    try:
        # First try to use shutil.rmtree
        shutil.rmtree(venv_dir, ignore_errors=True)

        # If the directory still exists, use the rd command
        if os.path.exists(venv_dir):
            logging.info("Using Windows rd command to force-remove directory...")
            subprocess.run(["rd", "/s", "/q", venv_dir], check=False)

        # If directory was successfully removed
        if not os.path.exists(venv_dir):
            logging.info("Virtual environment removed successfully.")
            return True, venv_dir
    except (OSError, shutil.Error):
        logging.exception("Error removing virtual environment with shutil")

    # If the directory still exists, try a different approach
    if os.path.exists(venv_dir):
        logging.warning(
            "Directory still exists. Creating a new virtual environment with a different name..."
        )
        temp_venv_dir: str = os.path.join(os.getcwd(), ".venv_new")
        venv_result = run_command([python_exe, "-m", "venv", temp_venv_dir])
        if venv_result is None:
            return False, venv_dir

        logging.info(f"New virtual environment created at {temp_venv_dir}")
        logging.warning(
            "Please manually delete the old .venv directory and rename .venv_new to .venv"
        )
        logging.warning(
            "after closing all applications that might be using the virtual environment."
        )
        return True, temp_venv_dir

    return True, venv_dir


def remove_venv_unix(venv_dir: str) -> bool:
    """Remove virtual environment on Unix-like systems.

    Args:
        venv_dir: Path to the virtual environment

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        shutil.rmtree(venv_dir)
        logging.info("Virtual environment removed successfully.")
    except (OSError, shutil.Error):
        logging.exception("Error removing virtual environment")
        return False
    else:
        return True


def remove_existing_venv(venv_dir: str, python_exe: str) -> tuple[bool, str]:
    """Remove the existing virtual environment.

    Args:
        venv_dir: Path to the virtual environment
        python_exe: Python executable path

    Returns:
        tuple: (success, venv_dir) - success flag and the venv directory to use
    """
    if not os.path.exists(venv_dir):
        return True, venv_dir

    logging.info(f"Removing existing virtual environment at {venv_dir}...")

    # Platform-specific removal
    if platform.system() == "Windows":
        return remove_venv_windows(venv_dir, python_exe)
    else:
        success = remove_venv_unix(venv_dir)
        return success, venv_dir


def create_venv(venv_dir: str, python_exe: str) -> bool:
    """Create a new virtual environment.

    Args:
        venv_dir: Path to create the virtual environment
        python_exe: Python executable path

    Returns:
        bool: True if successful, False otherwise
    """
    logging.info(f"Creating new virtual environment at {venv_dir}...")
    venv_result = run_command([python_exe, "-m", "venv", venv_dir])
    return venv_result is not None


def get_venv_python(venv_dir: str) -> str:
    """Get the path to the Python executable in the virtual environment.

    Args:
        venv_dir: Path to the virtual environment

    Returns:
        str: Path to the Python executable
    """
    if platform.system() == "Windows":
        # Explicitly cast to str to satisfy mypy
        return str(os.path.join(venv_dir, "Scripts", "python"))
    else:
        # Explicitly cast to str to satisfy mypy
        return str(os.path.join(venv_dir, "bin", "python"))


def install_packages(python_venv_exe: str) -> bool:
    """Install packages in the virtual environment.

    Args:
        python_venv_exe: Path to the Python executable in the virtual environment

    Returns:
        bool: True if successful, False otherwise
    """
    # Upgrade pip
    logging.info("Upgrading pip...")
    pip_upgrade_result = run_command(
        [
            python_venv_exe,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ]
    )
    if pip_upgrade_result is None:
        return False

    # Install requirements
    logging.info("Installing requirements...")
    req_result = run_command(
        [
            python_venv_exe,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
        ]
    )
    if req_result is None:
        return False

    # Install dev requirements if they exist
    if os.path.exists("requirements-dev.txt"):
        logging.info("Installing development requirements...")
        dev_req_result = run_command(
            [
                python_venv_exe,
                "-m",
                "pip",
                "install",
                "-r",
                "requirements-dev.txt",
            ]
        )
        if dev_req_result is None:
            return False

    return True


def print_activation_instructions(venv_dir: str) -> None:
    """Print instructions for activating the virtual environment.

    Args:
        venv_dir: Path to the virtual environment
    """
    logging.info("Virtual environment regenerated successfully!")
    logging.info("To activate the virtual environment, run:")

    # Get the relative path to make the instructions more user-friendly
    rel_venv_dir = os.path.relpath(venv_dir)

    if platform.system() == "Windows":
        logging.info(f"    {rel_venv_dir}\\Scripts\\activate")
    else:
        logging.info(f"    source {rel_venv_dir}/bin/activate")


def main() -> int:
    """Regenerate the virtual environment.

    Returns:
        int: 0 on success, 1 on failure
    """
    # Check if we're in a virtual environment
    if not check_venv_status():
        return 1

    # Determine the Python executable to use
    python_exe = sys.executable

    # Determine the virtual environment directory
    venv_dir: str = os.path.join(os.getcwd(), ".venv")

    # Remove the existing virtual environment
    success, venv_dir = remove_existing_venv(venv_dir, python_exe)
    if not success:
        return 1

    # If we're using a temporary directory that's already created, skip creation
    # Create a new virtual environment if needed
    if not os.path.exists(venv_dir) and not create_venv(venv_dir, python_exe):
        return 1

    # Get the Python executable in the virtual environment
    python_venv_exe = get_venv_python(venv_dir)

    # Install packages
    if not install_packages(python_venv_exe):
        return 1

    # Print activation instructions
    print_activation_instructions(venv_dir)

    return 0


def _exit(code: int = 0) -> NoReturn:
    """Exit the program with the given code."""
    sys.exit(code)


if __name__ == "__main__":
    _exit(main())
