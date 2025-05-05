"""Script to create or recreate the virtual environment."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command):
    """Run a command and return its output."""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    """Create or recreate the virtual environment."""
    venv_path = "venv"

    # Delete existing venv if it exists:
    if os.path.exists(venv_path):
        print(f"Removing existing virtual environment at {venv_path}...")
        try:
            if platform.system() == "Windows":
                # On Windows, some files might be read-only or locked
                subprocess.run(["rmdir", "/S", "/Q", venv_path], check=False)
            else:
                shutil.rmtree(venv_path)
        except Exception as e:
            print(f"Warning: Could not fully remove old environment: {e}")

    # Create new virtual environment
    print("Creating new virtual environment...")
    run_command([sys.executable, "-m", "venv", venv_path])

    pip_cmd = (
        str(Path(venv_path) / "Scripts" / "pip.exe")
        if platform.system() == "Windows"
        else str(Path(venv_path) / "bin" / "pip")
    )

    # Upgrade pip
    print("Upgrading pip...")
    run_command([pip_cmd, "install", "--upgrade", "pip"])

    # Install development requirements
    print("Installing development requirements...")
    run_command([pip_cmd, "install", "-r", "requirements-dev.txt"])

    print("\nVirtual environment has been created and requirements installed!")
    print("Activate it with:")
    if platform.system() == "Windows":
        print("    .\\venv\\Scripts\\activate")
    else:
        print("    source venv/bin/activate")


if __name__ == "__main__":
    main()
