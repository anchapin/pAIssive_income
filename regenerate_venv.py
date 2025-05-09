#!/usr/bin/env python3
"""Regenerate the virtual environment.

This script removes the existing virtual environment and creates a new one,
then installs all the required dependencies from requirements.txt and
requirements-dev.txt.
"""

import os
import platform
import shutil
import subprocess
import sys


def run_command(command, cwd=None):
    """Run a command and return its output.

    Args:
        command: The command to run as a list of strings
        cwd: The working directory to run the command in

    Returns:
        The command output as a string

    """
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return None

    return result.stdout


def is_venv_active():
    """Check if a virtual environment is active."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def main():
    """Regenerate the virtual environment."""
    # Determine the Python executable to use
    python_exe = sys.executable

    # Check if we're in a virtual environment
    if is_venv_active():
        print("Warning: You are currently in a virtual environment.")
        print("This script will deactivate it and create a new one.")
        print("Please run this script from outside any virtual environment.")
        return 1

    # Determine the virtual environment directory
    venv_dir = os.path.join(os.getcwd(), ".venv")

    # Remove the existing virtual environment
    if os.path.exists(venv_dir):
        print(f"Removing existing virtual environment at {venv_dir}...")

        # On Windows, try using the rd command which can force-remove directories
        if platform.system() == "Windows":
            try:
                # First try to use shutil.rmtree
                shutil.rmtree(venv_dir, ignore_errors=True)

                # If the directory still exists, use the rd command
                if os.path.exists(venv_dir):
                    print("Using Windows rd command to force-remove directory...")
                    subprocess.run(["rd", "/s", "/q", venv_dir], check=False)
            except Exception as e:
                print(f"Error removing virtual environment with shutil: {e}")

                # If the directory still exists, try a different approach
                if os.path.exists(venv_dir):
                    print(
                        "Directory still exists. Creating a new virtual environment "
                        "with a different name..."
                    )
                    temp_venv_dir = os.path.join(os.getcwd(), ".venv_new")
                    venv_result = run_command([python_exe, "-m", "venv", temp_venv_dir])
                    if venv_result is None:
                        return 1

                    print(f"New virtual environment created at {temp_venv_dir}")
                    print(
                        "Please manually delete the old .venv directory and rename "
                        ".venv_new to .venv"
                    )
                    print(
                        "after closing all applications that might be using "
                        "the virtual environment."
                    )
                    return 0
        else:
            # On Unix-like systems, use shutil.rmtree
            try:
                shutil.rmtree(venv_dir)
                print("Virtual environment removed successfully.")
            except Exception as e:
                print(f"Error removing virtual environment: {e}")
                return 1

    # Create a new virtual environment
    print(f"Creating new virtual environment at {venv_dir}...")
    venv_result = run_command([python_exe, "-m", "venv", venv_dir])
    if venv_result is None:
        return 1

    # Determine the python executable in the virtual environment
    if platform.system() == "Windows":
        python_venv_exe = os.path.join(venv_dir, "Scripts", "python")
    else:
        python_venv_exe = os.path.join(venv_dir, "bin", "python")

    # Upgrade pip
    print("Upgrading pip...")
    pip_upgrade_result = run_command(
        [python_venv_exe, "-m", "pip", "install", "--upgrade", "pip"]
    )
    if pip_upgrade_result is None:
        return 1

    # Install requirements
    print("Installing requirements...")
    req_result = run_command(
        [python_venv_exe, "-m", "pip", "install", "-r", "requirements.txt"]
    )
    if req_result is None:
        return 1

    # Install dev requirements if they exist
    if os.path.exists("requirements-dev.txt"):
        print("Installing development requirements...")
        dev_req_result = run_command(
            [python_venv_exe, "-m", "pip", "install", "-r", "requirements-dev.txt"]
        )
        if dev_req_result is None:
            return 1

    print("\nVirtual environment regenerated successfully!")
    print("To activate the virtual environment, run:")
    if platform.system() == "Windows":
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")

    return 0


if __name__ == "__main__":
    sys.exit(main())
