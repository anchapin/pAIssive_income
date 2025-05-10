#!/usr/bin/env python3
"""Regenerate the virtual environment using uv for full reproducibility.

This script removes the existing virtual environment and creates a new one using uv,
then generates a requirements.lock with uv (from pyproject.toml if present),
and finally syncs all dependencies using uv pip sync for an exact, reproducible environment.
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

    # Create a new virtual environment with uv
    print(f"Creating new virtual environment at {venv_dir} using uv...")
    venv_result = run_command(["uv", "venv", ".venv"])
    if venv_result is None:
        print("Failed to create virtual environment with uv.")
        return 1

    # Determine the python executable in the virtual environment
    if platform.system() == "Windows":
        python_venv_exe = os.path.join(venv_dir, "Scripts", "python")
    else:
        python_venv_exe = os.path.join(venv_dir, "bin", "python")

    # Activate venv for subsequent uv commands (subprocess uses full path anyway)

    # Generate or update requirements.lock using uv pip compile
    lockfile = "requirements.lock"
    # Prefer pyproject.toml if present, otherwise combine requirements.txt and requirements-dev.txt
    if os.path.exists("pyproject.toml"):
        print("Generating/updating lockfile (requirements.lock) from pyproject.toml via uv...")
        compile_result = run_command([
            python_venv_exe, "-m", "uv", "pip", "compile", "pyproject.toml", "-o", lockfile
        ])
        if compile_result is None:
            print("Failed to generate requirements.lock from pyproject.toml.")
            return 1
    elif os.path.exists("requirements.txt") and os.path.exists("requirements-dev.txt"):
        # Merge requirements.txt and requirements-dev.txt for complete reproducibility
        print("Combining requirements.txt and requirements-dev.txt into requirements-full.txt for locking...")
        with open("requirements.txt", "r") as req, open("requirements-dev.txt", "r") as dev, open("requirements-full.txt", "w") as full:
            full.write(req.read())
            full.write("\n")
            full.write(dev.read())
        print("Generating/updating lockfile (requirements.lock) from requirements-full.txt via uv...")
        compile_result = run_command([
            python_venv_exe, "-m", "uv", "pip", "compile", "requirements-full.txt", "-o", lockfile
        ])
        os.remove("requirements-full.txt")
        if compile_result is None:
            print("Failed to generate requirements.lock from requirements-full.txt.")
            return 1
    elif os.path.exists("requirements.txt"):
        print("Generating/updating lockfile (requirements.lock) from requirements.txt via uv...")
        compile_result = run_command([
            python_venv_exe, "-m", "uv", "pip", "compile", "requirements.txt", "-o", lockfile
        ])
        if compile_result is None:
            print("Failed to generate requirements.lock from requirements.txt.")
            return 1
    else:
        print("No pyproject.toml or requirements.txt found for locking.")
        return 1

    # Sync environment to the lockfile
    print("Syncing environment to requirements.lock with uv pip sync (fully reproducible)...")
    sync_result = run_command([
        python_venv_exe, "-m", "uv", "pip", "sync", lockfile
    ])
    if sync_result is None:
        print("Failed to sync environment to requirements.lock with uv.")
        return 1

    print("\nVirtual environment regenerated and fully synced with uv!")
    print("To activate the virtual environment, run:")
    if platform.system() == "Windows":
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")

    print("\nTo update dependencies in the future:")
    print("  1. Edit pyproject.toml or requirements.txt/requirements-dev.txt as needed.")
    print("  2. Run this script to re-lock and re-sync your environment: python regenerate_venv.py")
    print("For deterministic installs, always use uv pip sync requirements.lock.")
    print("NOTE: Both production and development dependencies are included in the lockfile for full reproducibility.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
