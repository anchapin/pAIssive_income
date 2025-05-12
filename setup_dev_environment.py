#!/usr/bin/env python3
"""
Setup Development Environment Script

This script automates the setup of a development environment for the pAIssive Income project.
It performs the following tasks:
1. Creates a virtual environment
2. Installs dependencies
3. Sets up pre-commit hooks
4. Creates IDE configuration files
5. Provides instructions for manual steps

Usage:
    python setup_dev_environment.py [options]

Options:
    --no-venv          Skip virtual environment creation
    --no-deps          Skip dependency installation
    --no-pre-commit    Skip pre-commit hook setup
    --no-ide-config    Skip IDE configuration
    --ide=<name>       Configure specific IDE (vscode, pycharm, all)
    --help             Show this help message
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import venv

from pathlib import Path
from typing import Optional


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Setup development environment for pAIssive Income project"
    )
    parser.add_argument(
        "--no-venv", action="store_true", help="Skip virtual environment creation"
    )
    parser.add_argument(
        "--no-deps", action="store_true", help="Skip dependency installation"
    )
    parser.add_argument(
        "--no-pre-commit", action="store_true", help="Skip pre-commit hook setup"
    )
    parser.add_argument(
        "--no-ide-config", action="store_true", help="Skip IDE configuration"
    )
    parser.add_argument(
        "--ide",
        choices=["vscode", "pycharm", "all"],
        default="all",
        help="Configure specific IDE",
    )
    return parser.parse_args()


def run_command(
    cmd: list[str], cwd: Optional[str] = None, env: Optional[dict[str, str]] = None
) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory
        env: Environment variables

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        process = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        return 1, "", str(e)
    else:
        return process.returncode, process.stdout, process.stderr


def is_venv_activated() -> bool:
    """Check if a virtual environment is activated."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def create_virtual_environment() -> bool:
    """Create a virtual environment.

    Returns:
        True if successful, False otherwise
    """
    print("Creating virtual environment...")
    venv_path = Path(".venv")

    if venv_path.exists():
        print(f"Virtual environment already exists at {venv_path}")
        return True

    try:
        venv.create(venv_path, with_pip=True)
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False
    else:
        print(f"Created virtual environment at {venv_path}")
        return True


def get_venv_python_path() -> str:
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return str(os.path.join(".venv", "Scripts", "python.exe"))
    return str(os.path.join(".venv", "bin", "python"))


def get_venv_pip_path() -> str:
    """Get the path to the pip executable in the virtual environment."""
    if platform.system() == "Windows":
        return str(os.path.join(".venv", "Scripts", "pip.exe"))
    return str(os.path.join(".venv", "bin", "pip"))


def install_dependencies() -> bool:
    """Install dependencies.

    Returns:
        True if successful, False otherwise
    """
    print("Installing dependencies...")
    pip_path = get_venv_pip_path()

    # Install requirements
    requirements_files = ["requirements.txt", "requirements-dev.txt"]
    for req_file in requirements_files:
        if not os.path.exists(req_file):
            print(f"Warning: {req_file} not found, skipping")
            continue

        print(f"Installing dependencies from {req_file}...")
        exit_code, stdout, stderr = run_command([pip_path, "install", "-r", req_file])
        if exit_code != 0:
            print(f"Error installing dependencies from {req_file}: {stderr}")
            return False
        print(stdout)

    # Install the package in development mode
    print("Installing package in development mode...")
    exit_code, stdout, stderr = run_command([pip_path, "install", "-e", "."])
    if exit_code != 0:
        print(f"Error installing package in development mode: {stderr}")
        return False
    print(stdout)

    return True


def setup_pre_commit() -> bool:
    """Set up pre-commit hooks.

    Returns:
        True if successful, False otherwise
    """
    print("Setting up pre-commit hooks...")
    pip_path = get_venv_pip_path()
    python_path = get_venv_python_path()

    # Install pre-commit
    exit_code, stdout, stderr = run_command([pip_path, "install", "pre-commit"])
    if exit_code != 0:
        print(f"Error installing pre-commit: {stderr}")
        return False
    print(stdout)

    # Install pre-commit hooks
    exit_code, stdout, stderr = run_command([
        python_path,
        "-m",
        "pre_commit",
        "install",
    ])
    if exit_code != 0:
        print(f"Error installing pre-commit hooks: {stderr}")
        return False
    print(stdout)

    return True


def configure_vscode() -> bool:
    """Configure VS Code.

    Returns:
        True if successful, False otherwise
    """
    print("Configuring VS Code...")
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    settings_path = vscode_dir / "settings.json"
    settings = {
        "python.testing.pytestArgs": ["tests"],
        "python.testing.unittestEnabled": False,
        "python.testing.pytestEnabled": True,
        # Linting and formatting settings
        "python.linting.enabled": True,
        "python.linting.flake8Enabled": True,
        "python.linting.mypyEnabled": True,
        # Disable Black formatter
        "python.formatting.blackEnabled": False,
        # Enable Ruff as the primary formatter and linter
        "python.formatting.provider": "none",
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll.ruff": True,
                "source.organizeImports.ruff": True,
            },
        },
        # Ruff extension settings
        "ruff.format.args": [],
        "ruff.lint.run": "onSave",
        # Editor settings for consistent formatting
        "editor.rulers": [88],
        "editor.renderWhitespace": "all",
        "editor.insertSpaces": True,
        "editor.tabSize": 4,
        "files.trimTrailingWhitespace": True,
        "files.insertFinalNewline": True,
    }

    try:
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error creating VS Code settings: {e}")
        return False
    else:
        print(f"Created VS Code settings at {settings_path}")
        return True


def configure_pycharm() -> bool:
    """Configure PyCharm.

    Returns:
        True if successful, False otherwise
    """
    print("Configuring PyCharm...")
    idea_dir = Path(".idea")
    idea_dir.mkdir(exist_ok=True)

    ruff_xml_path = idea_dir / "ruff.xml"
    ruff_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="RuffConfigService">
    <option name="projectRuffExecutablePath" value="$PROJECT_DIR$/.venv/bin/ruff" />
    <option name="useRuffFormat" value="true" />
    <option name="runRuffOnSave" value="true" />
    <option name="runRuffOnReformatCode" value="true" />
  </component>
</project>"""

    try:
        with open(ruff_xml_path, "w") as f:
            f.write(ruff_xml_content)
    except Exception as e:
        print(f"Error creating PyCharm Ruff configuration: {e}")
        return False
    else:
        print(f"Created PyCharm Ruff configuration at {ruff_xml_path}")
        return True


def create_editorconfig() -> bool:
    """Create .editorconfig file.

    Returns:
        True if successful, False otherwise
    """
    print("Creating .editorconfig file...")
    editorconfig_path = Path(".editorconfig")
    editorconfig_content = """\
# EditorConfig helps maintain consistent coding styles across different editors
# https://editorconfig.org/

root = true

[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8

[*.{py,pyi}]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{json,yml,yaml,toml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
"""

    try:
        with open(editorconfig_path, "w") as f:
            f.write(editorconfig_content)
    except Exception as e:
        print(f"Error creating .editorconfig: {e}")
        return False
    else:
        print(f"Created .editorconfig at {editorconfig_path}")
        return True


def configure_ides(ide: str) -> bool:
    """Configure IDEs.

    Args:
        ide: IDE to configure (vscode, pycharm, all)

    Returns:
        True if successful, False otherwise
    """
    success = True

    # Create .editorconfig for all editors
    if not create_editorconfig():
        success = False

    # Configure specific IDEs
    if ide in ["vscode", "all"] and not configure_vscode():
        success = False

    if ide in ["pycharm", "all"] and not configure_pycharm():
        success = False

    return success


def print_next_steps() -> None:
    """Print next steps for the user."""
    print("\n=== Next Steps ===")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")

    print("\n2. Install IDE extensions:")
    print("   VS Code:")
    print(
        "   - Ruff: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff"
    )
    print(
        "   - Python: https://marketplace.visualstudio.com/items?itemName=ms-python.python"
    )
    print("\n   PyCharm:")
    print("   - Ruff: https://plugins.jetbrains.com/plugin/20574-ruff")

    print("\n3. Run pre-commit hooks on all files:")
    print("   pre-commit run --all-files")

    print("\n4. Run tests to verify the setup:")
    print("   pytest")

    print("\nFor more information, see the documentation:")
    print("- README.md")
    print("- docs/contributing.md")
    print("- docs/ide_setup.md")


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args()
    success = True

    # Check if running in a virtual environment
    if is_venv_activated():
        print("Warning: Running in an activated virtual environment.")
        print("This script is designed to be run outside of a virtual environment.")
        print("Continuing anyway...")

    # Create virtual environment
    if not args.no_venv and not create_virtual_environment():
        print("Error: Failed to create virtual environment.")
        return 1

    # Install dependencies
    if not args.no_deps and not install_dependencies():
        print("Error: Failed to install dependencies.")
        success = False

    # Set up pre-commit hooks
    if not args.no_pre_commit and not setup_pre_commit():
        print("Error: Failed to set up pre-commit hooks.")
        success = False

    # Configure IDEs
    if not args.no_ide_config and not configure_ides(args.ide):
        print("Error: Failed to configure IDEs.")
        success = False

    # Print next steps
    print_next_steps()

    if not success:
        print("\nWarning: Some steps failed. See the output above for details.")
        return 1

    print("\nDevelopment environment setup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
