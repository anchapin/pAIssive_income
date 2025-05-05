#!/usr/bin/env python
"""
Script to recreate the virtual environment with proper dependencies.:
This script will:
1. Remove the current virtual environment
2. Create a new one
3. Install all dependencies
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys


def run_command(command, description=None, check=True):
    """Run a shell command and print its output."""
    if description:
        print(f"\n{description}...")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}"):
        sys.exit(result.returncode)

    return result.returncode == 0


def remove_venv(venv_path):
    """Remove the virtual environment."""
    print(f"\nRemoving virtual environment at {venv_path}...")

    if os.path.exists(venv_path):
        try:
            shutil.rmtree(venv_path)
            print(f"Successfully removed {venv_path}")
        except Exception as e:
            print(f"Error removing {venv_path}: {e}")
            return False
    else:
        print(f"Virtual environment {venv_path} does not exist")

    return True


def create_venv(venv_path):
    """Create a new virtual environment."""
    print(f"\nCreating new virtual environment at {venv_path}...")

    return run_command(f"python -m venv {venv_path}")


def install_dependencies(venv_path):
    """Install dependencies in the virtual environment."""
    # Determine the activate script based on the platform
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_path, "Scripts", "activate")
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
        pip_path = os.path.join(venv_path, "bin", "pip")

    # Upgrade pip
    print("\nUpgrading pip...")
    if platform.system() == "Windows":
        run_command(f"{pip_path} install --upgrade pip")
    else:
        run_command(f"source {activate_script} && pip install --upgrade pip")

    # Install build dependencies
    print("\nInstalling build dependencies...")
    if platform.system() == "Windows":
        run_command(f"{pip_path} install build setuptools wheel")
    else:
        run_command(f"source {activate_script} && pip install build setuptools wheel")

    # Install requirements
    print("\nInstalling requirements...")
    if os.path.exists("requirements.txt"):
        if platform.system() == "Windows":
            run_command(f"{pip_path} install -r requirements.txt")
        else:
            run_command(f"source {activate_script} && pip install -r requirements.txt")

    # Install development requirements
    print("\nInstalling development requirements...")
    if os.path.exists("requirements-dev.txt"):
        if platform.system() == "Windows":
            run_command(f"{pip_path} install -r requirements-dev.txt")
        else:
            run_command(f"source {activate_script} && pip install -r requirements-dev.txt")

    # Install the package in development mode
    print("\nInstalling package in development mode...")
    if platform.system() == "Windows":
        run_command(f"{pip_path} install -e .")
    else:
        run_command(f"source {activate_script} && pip install -e .")

    # Install pre-commit
    print("\nInstalling pre-commit...")
    if platform.system() == "Windows":
        run_command(f"{pip_path} install pre-commit")
        run_command(f"{os.path.join(venv_path, 'Scripts', 'pre-commit')} install")
    else:
        run_command(f"source {activate_script} && pip install pre-commit")
        run_command(f"source {activate_script} && pre-commit install")

    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Recreate the virtual environment."
    )
    parser.add_argument(
        "--venv-path", default=".venv", help="Path to the virtual environment"
    )
    parser.add_argument(
        "--skip-remove", action="store_true", help="Skip removing the existing virtual environment"
    )
    parser.add_argument(
        "--skip-create", action="store_true", help="Skip creating a new virtual environment"
    )
    parser.add_argument(
        "--skip-install", action="store_true", help="Skip installing dependencies"
    )

    args = parser.parse_args()

    venv_path = args.venv_path

    # Remove the virtual environment
    if not args.skip_remove:
        if not remove_venv(venv_path):
            print("Failed to remove the virtual environment")
            return 1

    # Create a new virtual environment
    if not args.skip_create:
        if not create_venv(venv_path):
            print("Failed to create a new virtual environment")
            return 1

    # Install dependencies
    if not args.skip_install:
        if not install_dependencies(venv_path):
            print("Failed to install dependencies")
            return 1

    print("\n✅ Virtual environment successfully recreated!")

    # Print instructions for activating the virtual environment:
    print("\nTo activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"    {venv_path}\\Scripts\\activate")
    else:
        print(f"    source {venv_path}/bin/activate")

    return 0


if __name__ == "__main__":
    sys.exit(main())
