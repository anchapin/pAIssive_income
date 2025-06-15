#!/usr/bin/env python3
"""
Setup Development Environment Script.

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

from __future__ import annotations

import argparse
import json
import platform
import shutil  # Added for shutil.which
import sys
from pathlib import Path
from typing import Optional

from common_utils.security import SecurityError, run_command_securely


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
    """
    Run a command securely.

    Args:
        cmd: Command to run as list
        cwd: Working directory
        env: Environment variables

    Returns:
        Tuple of (exit code, stdout, stderr)

    """
    try:
        result = run_command_securely(cmd, cwd=cwd, env=env, timeout=600)
        return result.returncode, result.stdout, result.stderr
    except SecurityError as e:
        return 1, "", str(e)
    except Exception as e:
        return 1, "", f"Error executing command: {e!s}"


def is_venv_activated() -> bool:
    """Check if a virtual environment is activated."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def check_uv_available() -> bool:
    """Check if uv is installed and available."""
    if shutil.which("uv"):
        print("uv found.")
        return True
    print("Error: uv is not installed or not in PATH.")
    print(
        "Please install uv by following the instructions at https://github.com/astral-sh/uv"
    )
    print(
        "For example: 'pip install uv' or 'curl -LsSf https://astral.sh/uv/install.sh | sh'"
    )
    return False


def create_virtual_environment() -> bool:
    """
    Create a virtual environment using uv.

    Returns:
        True if successful, False otherwise

    """
    print("Creating virtual environment using uv...")
    venv_path = Path(".venv")

    if venv_path.exists():
        print(f"Virtual environment already exists at {venv_path}")
        # We can optionally verify it's a uv-compatible venv or just proceed
        return True

    # Use the Python interpreter that's running this script for the venv
    python_executable = sys.executable
    exit_code, stdout, stderr = run_command(
        [
            "uv",
            "venv",
            str(venv_path),
            "--python",
            python_executable,
        ]
    )
    if exit_code != 0:
        print(f"Error creating virtual environment with uv: {stderr}")
        print(f"Stdout: {stdout}")
        return False

    print(f"Created virtual environment at {venv_path} using uv.")
    print(stdout)
    return True


def get_venv_python_path() -> str:
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return str(Path(".venv") / "Scripts" / "python.exe")
    return str(Path(".venv") / "bin" / "python")


def install_dependencies() -> bool:
    """
    Install dependencies using uv.

    Returns:
        True if successful, False otherwise

    """
    print("Installing dependencies using uv...")
    venv_python_path = get_venv_python_path()

    # Install requirements
    requirements_files = ["requirements.txt", "requirements-dev.txt"]
    for req_file in requirements_files:
        if not Path(req_file).exists():
            print(f"Warning: {req_file} not found, skipping")
            continue

        print(f"Installing dependencies from {req_file} using uv...")
        # uv pip install will use the activated venv if available,
        # or we can specify the python interpreter of the target venv.
        cmd = ["uv", "pip", "install", "--python", venv_python_path, "-r", req_file]
        exit_code, stdout, stderr = run_command(cmd)
        if exit_code != 0:
            print(f"Error installing dependencies from {req_file} using uv: {stderr}")
            print(f"Stdout: {stdout}")
            return False
        print(stdout)

    # Install the package in development mode
    print("Installing package in development mode using uv...")
    cmd = ["uv", "pip", "install", "--python", venv_python_path, "-e", "."]
    exit_code, stdout, stderr = run_command(cmd)
    if exit_code != 0:
        print(f"Error installing package in development mode using uv: {stderr}")
        print(f"Stdout: {stdout}")
        return False
    print(stdout)

    return True


def setup_pre_commit() -> bool:
    """
    Set up pre-commit hooks using uv.

    Returns:
        True if successful, False otherwise

    """
    print("Setting up pre-commit hooks using uv...")
    venv_python_path = get_venv_python_path()

    # Install pre-commit using uv
    print("Installing pre-commit using uv...")
    cmd_install_precommit = [
        "uv",
        "pip",
        "install",
        "--python",
        venv_python_path,
        "pre-commit",
    ]
    exit_code, stdout, stderr = run_command(cmd_install_precommit)
    if exit_code != 0:
        print(f"Error installing pre-commit using uv: {stderr}")
        print(f"Stdout: {stdout}")
        return False
    print(stdout)

    # Install pre-commit hooks using the venv's python
    print("Installing pre-commit hooks...")
    # pre_commit module is now available in the venv
    cmd_setup_hooks = [venv_python_path, "-m", "pre_commit", "install"]
    exit_code, stdout, stderr = run_command(cmd_setup_hooks)
    if exit_code != 0:
        print(f"Error installing pre-commit hooks: {stderr}")
        print(f"Stdout: {stdout}")
        return False
    print(stdout)

    return True


def configure_vscode() -> bool:
    """
    Configure VS Code.

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
        with Path(settings_path).open("w") as f:
            json.dump(settings, f, indent=4)
    except OSError as e:
        print(f"Error creating VS Code settings (I/O error): {e}")
        return False
    except (TypeError, ValueError) as e:
        print(f"Error creating VS Code settings (data error): {e}")
        return False
    else:
        print(f"Created VS Code settings at {settings_path}")
        return True


def configure_pycharm() -> bool:
    """
    Configure PyCharm.

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
        with Path(ruff_xml_path).open("w") as f:
            f.write(ruff_xml_content)
    except OSError as e:
        print(f"Error creating PyCharm Ruff configuration (I/O error): {e}")
        return False
    except (TypeError, ValueError) as e:
        print(f"Error creating PyCharm Ruff configuration (data error): {e}")
        return False
    else:
        print(f"Created PyCharm Ruff configuration at {ruff_xml_path}")
        return True


def create_editorconfig() -> bool:
    """
    Create .editorconfig file.

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
        with Path(editorconfig_path).open("w") as f:
            f.write(editorconfig_content)
    except OSError as e:
        print(f"Error creating .editorconfig (I/O error): {e}")
        return False
    except (TypeError, ValueError) as e:
        print(f"Error creating .editorconfig (data error): {e}")
        return False
    else:
        print(f"Created .editorconfig at {editorconfig_path}")
        return True


def configure_ides(ide: str) -> bool:
    """
    Configure IDEs.

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
    print("Ensure 'uv' is installed and in your PATH.")
    print("You can install it via pip: 'pip install uv' or from https://astral.sh/uv")
    print("\n1. Activate the virtual environment (created with uv):")
    if platform.system() == "Windows":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")

    print("\n2. If you skipped dependency installation, install them with uv:")
    print(f"   uv pip install -r requirements.txt --python {get_venv_python_path()}")
    print(
        f"   uv pip install -r requirements-dev.txt --python {get_venv_python_path()}"
    )
    print(f"   uv pip install -e . --python {get_venv_python_path()}")

    print("\n3. Install IDE extensions:")
    print("   VS Code:")
    print(
        "   - Ruff: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff"
    )
    print(
        "   - Python: https://marketplace.visualstudio.com/items?itemName=ms-python.python"
    )
    print("\n   PyCharm:")
    print("   - Ruff: https://plugins.jetbrains.com/plugin/20574-ruff")

    print("\n4. Run pre-commit hooks on all files (after activating venv):")
    print("   pre-commit run --all-files")

    print("\n5. Run tests to verify the setup (after activating venv):")
    print("   pytest")

    print("\nFor more information, see the documentation:")
    print("- README.md")
    print("- docs/contributing.md")
    print("- docs/ide_setup.md")


def main() -> int:
    """
    Run the setup process.

    Returns:
        Exit code (0 for success, 1 for failure)

    """
    args = parse_args()
    success = True

    # Check if uv is available
    if not check_uv_available():
        return 1  # uv is required, exit if not found

    # Check if running in a virtual environment
    if is_venv_activated():
        print("Warning: Running in an activated virtual environment.")
        print("This script is designed to be run outside of a virtual environment.")
        print("It will create/use a '.venv' directory in the current location.")
        print("Continuing anyway...")

    # Create virtual environment
    if not args.no_venv and not create_virtual_environment():
        print("Error: Failed to create virtual environment using uv.")
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
