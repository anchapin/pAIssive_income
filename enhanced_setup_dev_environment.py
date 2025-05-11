#!/usr/bin/env python3
"""
Enhanced Setup Development Environment Script

This script automates the setup of a development environment for the pAIssive Income project.
It performs the following tasks:
1. Checks for and installs system dependencies (Node.js, Git, etc.)
2. Creates a virtual environment
3. Installs Python dependencies
4. Sets up pre-commit hooks
5. Creates IDE configuration files
6. Provides instructions for manual steps

Usage:
    python enhanced_setup_dev_environment.py [options]

Options:
    # System dependencies
    --no-system-deps      Skip system dependency checks
    --node-version=<ver>  Specify Node.js version to install (e.g., 18.x, 20.x)
    --force-install-deps  Force installation of missing dependencies

    # Environment setup
    --no-venv             Skip virtual environment creation
    --no-deps             Skip dependency installation
    --no-pre-commit       Skip pre-commit hook setup
    --no-ide-config       Skip IDE configuration
    --ide=<name>          Configure specific IDE (vscode, pycharm, all)

    # Setup profiles
    --ui-only             Set up only UI-related dependencies
    --backend-only        Set up only backend-related dependencies
    --minimal             Minimal setup with essential dependencies only
    --full                Full setup with all dependencies (default)

    # Configuration
    --config-file=<path>  Specify a configuration file for setup options
    --help                Show this help message
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("setup")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Setup development environment for pAIssive Income project"
    )

    # System dependency options
    system_group = parser.add_argument_group("System Dependencies")
    system_group.add_argument(
        "--no-system-deps", action="store_true", help="Skip system dependency checks"
    )
    system_group.add_argument(
        "--node-version",
        default="18.x",
        help="Node.js version to install (e.g., 18.x, 20.x)",
    )
    system_group.add_argument(
        "--force-install-deps",
        action="store_true",
        help="Force installation of missing dependencies",
    )

    # Environment setup options
    env_group = parser.add_argument_group("Environment Setup")
    env_group.add_argument(
        "--no-venv", action="store_true", help="Skip virtual environment creation"
    )
    env_group.add_argument(
        "--no-deps", action="store_true", help="Skip dependency installation"
    )
    env_group.add_argument(
        "--no-pre-commit", action="store_true", help="Skip pre-commit hook setup"
    )
    env_group.add_argument(
        "--no-ide-config", action="store_true", help="Skip IDE configuration"
    )
    env_group.add_argument(
        "--ide",
        choices=["vscode", "pycharm", "all"],
        default="all",
        help="Configure specific IDE",
    )

    # Setup profile options
    profile_group = parser.add_argument_group("Setup Profiles")
    profile_group.add_argument(
        "--ui-only", action="store_true", help="Set up only UI-related dependencies"
    )
    profile_group.add_argument(
        "--backend-only",
        action="store_true",
        help="Set up only backend-related dependencies",
    )
    profile_group.add_argument(
        "--minimal",
        action="store_true",
        help="Minimal setup with essential dependencies only",
    )
    profile_group.add_argument(
        "--full", action="store_true", help="Full setup with all dependencies (default)"
    )

    # Configuration options
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--config-file", help="Specify a configuration file for setup options"
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
    executable_path_str = cmd[0]  # Keep original for error messages if needed

    # Resolve command using shutil.which if it's a bare command name.
    # This helps find .cmd, .bat files on Windows correctly from PATH.
    if not os.path.isabs(executable_path_str) and not os.path.dirname(
        executable_path_str
    ):
        resolved_executable = shutil.which(executable_path_str)
        if resolved_executable:
            cmd_to_run = [resolved_executable] + cmd[1:]
        else:
            # If shutil.which doesn't find it, it's unlikely to be found by subprocess.run directly.
            logger.debug(
                f"shutil.which could not find '{executable_path_str}' in PATH: {os.environ.get('PATH')}"
            )
            return 1, "", f"Command '{executable_path_str}' not found in PATH."
    else:
        cmd_to_run = list(cmd)  # Ensure it's a mutable list copy

    try:
        process = subprocess.run(
            cmd_to_run,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,  # Original script uses check=False
        )
    except FileNotFoundError as e:
        # This catch is a fallback, should be less likely if shutil.which is effective.
        logger.debug(
            f"FileNotFoundError for '{cmd_to_run[0]}' with PATH: {os.environ.get('PATH')}"
        )
        return 1, "", f"Execution failed for '{cmd_to_run[0]}': {e}"
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
    logger.info("Creating virtual environment...")
    venv_path = Path(".venv")

    if venv_path.exists():
        logger.info(f"Virtual environment already exists at {venv_path}")
        return True

    try:
        venv.create(venv_path, with_pip=True)
    except Exception:
        logger.exception("Error creating virtual environment")
        return False
    else:
        logger.info(f"Created virtual environment at {venv_path}")
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


def check_system_dependency(dependency: str) -> bool:
    """Check if a system dependency is installed.

    Args:
        dependency: Name of the dependency to check

    Returns:
        True if installed, False otherwise
    """
    if platform.system() == "Windows":
        cmd = ["where", dependency]
    else:
        cmd = ["which", dependency]

    exit_code, _, _ = run_command(cmd)
    return exit_code == 0


def get_node_version() -> Optional[str]:
    """Get the installed Node.js version.

    Returns:
        Node.js version string or None if not installed
    """
    exit_code, stdout, _ = run_command(["node", "--version"])
    if exit_code == 0:
        return stdout.strip()
    return None


def get_pnpm_version() -> Optional[str]:
    """Get the installed pnpm version.

    Returns:
        pnpm version string or None if not installed
    """
    # Try with npx to bypass PATH issues for pnpm itself
    exit_code, stdout, _ = run_command(["npx", "pnpm", "--version"])
    if exit_code == 0:
        return stdout.strip()
    return None


def get_git_version() -> Optional[str]:
    """Get the installed Git version.

    Returns:
        Git version string or None if not installed
    """
    exit_code, stdout, _ = run_command(["git", "--version"])
    if exit_code == 0:
        return stdout.strip()
    return None


def install_nodejs_windows(version: str = "18.x") -> bool:
    """Install Node.js on Windows.

    Args:
        version: Node.js version to install

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Installing Node.js {version} on Windows...")

    # Check if chocolatey is installed
    exit_code, _, _ = run_command(["choco", "--version"])
    if exit_code != 0:
        logger.error("Chocolatey is not installed. Please install it first:")
        logger.error("https://chocolatey.org/install")
        return False

    # Install Node.js using chocolatey
    exit_code, stdout, stderr = run_command([
        "choco",
        "install",
        "nodejs",
        f"--version={version}",
        "-y",
    ])
    if exit_code != 0:
        logger.error(f"Error installing Node.js: {stderr}")
        return False

    logger.debug(stdout)
    logger.info(
        "Node.js installed successfully. You may need to restart your terminal."
    )
    return True


def install_nodejs_unix(version: str = "18.x") -> bool:
    """Install Node.js on Unix-like systems.

    Args:
        version: Node.js version to install

    Returns:
        True if successful, False otherwise
    """
    system = platform.system()
    logger.info(f"Installing Node.js {version} on {system}...")

    if system == "Darwin":  # macOS
        # Check if brew is installed
        exit_code, _, _ = run_command(["brew", "--version"])
        if exit_code != 0:
            logger.error("Homebrew is not installed. Please install it first:")
            logger.error("https://brew.sh/")
            return False

        # Install Node.js using homebrew
        exit_code, stdout, stderr = run_command([
            "brew",
            "install",
            "node@" + version.split(".")[0],
        ])
        if exit_code != 0:
            logger.error(f"Error installing Node.js: {stderr}")
            return False

        logger.debug(stdout)
    else:  # Linux
        # Use NVM to install Node.js
        nvm_dir = os.path.expanduser("~/.nvm")
        if not os.path.exists(nvm_dir):
            logger.info("Installing NVM (Node Version Manager)...")
            exit_code, stdout, stderr = run_command([
                "curl",
                "-o-",
                "https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh",
                "|",
                "bash",
            ])
            if exit_code != 0:
                logger.error(f"Error installing NVM: {stderr}")
                return False

            logger.debug(stdout)

        # Source NVM and install Node.js
        nvm_script = os.path.join(nvm_dir, "nvm.sh")
        exit_code, stdout, stderr = run_command([
            "bash",
            "-c",
            f"source {nvm_script} && nvm install {version}",
        ])
        if exit_code != 0:
            logger.error(f"Error installing Node.js: {stderr}")
            return False

        logger.debug(stdout)

    logger.info(
        "Node.js installed successfully. You may need to restart your terminal."
    )
    return True


def install_nodejs(version: str = "18.x") -> bool:
    """Install Node.js on the current platform.

    Args:
        version: Node.js version to install

    Returns:
        True if successful, False otherwise
    """
    if platform.system() == "Windows":
        return install_nodejs_windows(version)
    else:
        return install_nodejs_unix(version)


def install_git() -> bool:
    """Install Git on the current platform.

    Returns:
        True if successful, False otherwise
    """
    system = platform.system()
    logger.info(f"Installing Git on {system}...")

    if system == "Windows":
        logger.info("Please download and install Git for Windows:")
        logger.info("https://git-scm.com/download/win")
        return False
    elif system == "Darwin":  # macOS
        # Check if brew is installed
        exit_code, _, _ = run_command(["brew", "--version"])
        if exit_code != 0:
            logger.error("Homebrew is not installed. Please install it first:")
            logger.error("https://brew.sh/")
            return False

        # Install Git using homebrew
        exit_code, stdout, stderr = run_command(["brew", "install", "git"])
        if exit_code != 0:
            logger.error(f"Error installing Git: {stderr}")
            return False

        logger.debug(stdout)
    else:  # Linux
        # Try to detect the package manager
        if shutil.which("apt-get"):
            cmd = [
                "sudo",
                "apt-get",
                "update",
                "&&",
                "sudo",
                "apt-get",
                "install",
                "-y",
                "git",
            ]
        elif shutil.which("dnf"):
            cmd = ["sudo", "dnf", "install", "-y", "git"]
        elif shutil.which("yum"):
            cmd = ["sudo", "yum", "install", "-y", "git"]
        elif shutil.which("pacman"):
            cmd = ["sudo", "pacman", "-S", "--noconfirm", "git"]
        else:
            logger.error(
                "Could not detect package manager. Please install Git manually."
            )
            return False

        exit_code, stdout, stderr = run_command(cmd)
        if exit_code != 0:
            logger.error(f"Error installing Git: {stderr}")
            return False

        logger.debug(stdout)

    logger.info("Git installed successfully.")
    return True


def check_dependency(
    name: str,
    get_version_func: Callable[[], Optional[str]],
    install_func: Optional[Callable[..., bool]] = None,
    version_arg: Optional[str] = None,
    args: Optional[argparse.Namespace] = None,
) -> bool:
    """Check for a specific dependency and install if missing.

    Args:
        name: Name of the dependency
        get_version_func: Function to get the version
        install_func: Function to install the dependency
        version_arg: Version argument for install function
        args: Command-line arguments

    Returns:
        True if dependency is installed, False otherwise
    """
    version = get_version_func()
    if version:
        logger.info(f"{name} is installed: {version}")
        return True

    logger.warning(f"{name} is not installed.")

    if args and args.force_install_deps and install_func:
        if version_arg:
            result = install_func(version_arg)
            return bool(result)
        result = install_func()
        return bool(result)

    if args:
        logger.warning(f"Please install {name} or run with --force-install-deps")
    return False


def check_system_dependencies(args: argparse.Namespace) -> bool:
    """Check for required system dependencies and install if missing.

    Args:
        args: Command-line arguments

    Returns:
        True if all dependencies are installed, False otherwise
    """
    if args.no_system_deps:
        logger.info("Skipping system dependency checks...")
        return True

    logger.info("Checking system dependencies...")

    # Check Node.js
    node_installed = check_dependency(
        "Node.js", get_node_version, install_nodejs, args.node_version, args
    )

    # Check pnpm (it needs to be installed separately)
    pnpm_installed = check_dependency(
        "pnpm", get_pnpm_version, install_func=install_pnpm_globally, args=args
    )
    if not pnpm_installed and args.force_install_deps:
        logger.warning(
            "pnpm was not installed. Please check your installation or logs."
        )

    # Check Git
    git_installed = check_dependency("Git", get_git_version, install_git, args=args)

    # All dependencies must be installed
    return node_installed and pnpm_installed and git_installed


def load_config_file(config_file: str) -> dict[str, Any]:
    """Load configuration from a YAML or JSON file.

    Args:
        config_file: Path to the configuration file

    Returns:
        Dictionary containing configuration options
    """
    if not os.path.exists(config_file):
        logger.error(f"Error: Configuration file {config_file} not found.")
        return {}

    try:
        with open(config_file) as f:
            if config_file.endswith(".json"):
                config = json.load(f)
            elif config_file.endswith((".yaml", ".yml")):
                config = yaml.safe_load(f)
            else:
                logger.error(
                    f"Error: Unsupported configuration file format: {config_file}"
                )
                return {}
    except Exception:
        logger.exception("Error loading configuration file")
        return {}

    logger.info(f"Loaded configuration from {config_file}")
    # Ensure we return a dict[str, Any] to satisfy mypy
    if not isinstance(config, dict):
        logger.error(
            f"Error: Configuration file {config_file} did not contain a dictionary"
        )
        return {}
    return config


def create_sample_config_file() -> bool:
    """Create a sample configuration file.

    Returns:
        True if successful, False otherwise
    """
    config_file = "setup_config.yaml"
    if os.path.exists(config_file):
        logger.info(f"Configuration file {config_file} already exists.")
        return True

    sample_config = {
        "system_dependencies": {
            "check_system_deps": True,
            "node_version": "18.x",
            "force_install_deps": False,
        },
        "environment_setup": {
            "create_venv": True,
            "install_deps": True,
            "setup_pre_commit": True,
            "configure_ide": True,
            "ide": "all",
        },
        "setup_profile": {
            "profile": "full",  # Options: minimal, backend_only, ui_only, full
        },
        "dependencies": {
            "backend": ["requirements.txt", "requirements-dev.txt"],
            "ui": ["ui/react_frontend/package.json"],
            "minimal": ["requirements.txt"],
        },
    }

    try:
        with open(config_file, "w") as f:
            yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    except Exception:
        logger.exception("Error creating sample configuration file")
        return False

    logger.info(f"Created sample configuration file at {config_file}")
    return True


def apply_setup_profile(args: argparse.Namespace) -> argparse.Namespace:
    """Apply setup profile to arguments.

    Args:
        args: Command-line arguments

    Returns:
        Updated arguments with profile settings applied
    """
    # Default to full setup if no profile specified
    if not any([args.minimal, args.ui_only, args.backend_only, args.full]):
        args.full = True

    if args.minimal:
        logger.info("Applying minimal setup profile...")
        # Skip non-essential dependencies
        args.no_pre_commit = True
        args.no_ide_config = True

    if args.ui_only:
        logger.info("Applying UI-only setup profile...")
        # Focus on UI dependencies
        args.no_venv = True  # Node.js doesn't need Python venv

    if args.backend_only:
        logger.info("Applying backend-only setup profile...")
        # Skip UI dependencies

    if args.full:
        logger.info("Applying full setup profile...")
        # Full setup with all dependencies
        args.force_install_deps = (
            True  # Ensure dependencies are forcibly installed with full profile
        )

    return args


def install_dependencies() -> bool:
    """Install Python dependencies.

    Returns:
        True if successful, False otherwise
    """
    logger.info("Installing Python dependencies...")

    pip_path = get_venv_pip_path()

    # Check for requirements.txt in root directory
    if os.path.exists("requirements.txt"):
        logger.info("Found requirements.txt in root directory")
        exit_code, stdout, stderr = run_command([
            pip_path,
            "install",
            "-r",
            "requirements.txt",
        ])
        if exit_code != 0:
            logger.error(f"Error installing Python dependencies: {stderr}")
            return False
        logger.debug(stdout)

    # Check for requirements-dev.txt in root directory
    if os.path.exists("requirements-dev.txt"):
        logger.info("Found requirements-dev.txt in root directory")
        exit_code, stdout, stderr = run_command([
            pip_path,
            "install",
            "-r",
            "requirements-dev.txt",
        ])
        if exit_code != 0:
            logger.error(f"Error installing development dependencies: {stderr}")
            return False
        logger.debug(stdout)

    # Install pre-commit package
    exit_code, stdout, stderr = run_command([pip_path, "install", "pre-commit"])
    if exit_code != 0:
        logger.error(f"Error installing pre-commit: {stderr}")
        return False
    logger.debug(stdout)

    # Run Ruff to fix linting issues
    logger.info("Running Ruff to fix linting issues...")
    ruff_exit_code, ruff_stdout, ruff_stderr = run_command([
        "ruff",
        "check",
        "--fix",
        ".",
    ])
    if ruff_exit_code != 0:
        error_message = "Ruff command failed."
        if ruff_stderr:
            error_message += f" Stderr:\n{ruff_stderr.strip()}"
        else:
            error_message += " No stderr output."
        if ruff_stdout:
            error_message += f"\nStdout:\n{ruff_stdout.strip()}"
        else:
            error_message += "\nNo stdout output."
        logger.error(error_message)
        return False

    logger.info("Ruff check and fix completed successfully.")
    return True


def setup_pre_commit() -> bool:
    """Set up pre-commit hooks.

    Returns:
        True if successful, False otherwise
    """
    logger.info("Setting up pre-commit hooks...")

    # Check if .pre-commit-config.yaml exists
    if not os.path.exists(".pre-commit-config.yaml"):
        logger.error("Error: .pre-commit-config.yaml not found.")
        return False

    # Install pre-commit hooks
    exit_code, stdout, stderr = run_command(["pre-commit", "install"])
    if exit_code != 0:
        logger.error(f"Error installing pre-commit hooks: {stderr}")
        return False
    logger.debug(stdout)

    return True


def configure_ides(ide_choice: str) -> bool:
    """Configure IDE settings.

    Args:
        ide_choice: Which IDE to configure (vscode, pycharm, all)

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Configuring IDE settings for {ide_choice}...")

    success = True

    if ide_choice in ["vscode", "all"]:
        success = configure_vscode() and success

    if ide_choice in ["pycharm", "all"]:
        success = configure_pycharm() and success

    return success


def configure_vscode() -> bool:
    """Configure VS Code settings.

    Returns:
        True if successful, False otherwise
    """
    logger.info("Configuring VS Code settings...")

    vscode_dir = os.path.join(".vscode")
    os.makedirs(vscode_dir, exist_ok=True)

    # Create settings.json
    settings = {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
        "python.formatting.provider": "none",
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.fixAll": True,
            "source.organizeImports": True,
        },
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll": True,
                "source.organizeImports": True,
            },
        },
        "ruff.format.args": [],
        "ruff.lint.run": "onSave",
    }

    try:
        with open(os.path.join(vscode_dir, "settings.json"), "w") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        logger.exception("Error creating VS Code settings")
        return False

    # Create launch.json for debugging
    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
            {
                "name": "Python: API Server",
                "type": "python",
                "request": "launch",
                "module": "uvicorn",
                "args": ["api.main:app", "--reload"],
                "jinja": True,
                "justMyCode": True,
            },
        ],
    }

    try:
        with open(os.path.join(vscode_dir, "launch.json"), "w") as f:
            json.dump(launch, f, indent=4)
    except Exception:
        logger.exception("Error creating VS Code launch configuration")
        return False

    logger.info("VS Code configuration complete.")
    return True


def configure_pycharm() -> bool:
    """Configure PyCharm settings.

    Returns:
        True if successful, False otherwise
    """
    logger.info("Configuring PyCharm settings...")

    # PyCharm settings are stored in .idea directory, but it's complex to modify them directly
    # Instead, create a README file with instructions

    pycharm_readme = """# PyCharm Configuration

To configure PyCharm for this project:

1. Open the project in PyCharm
2. Go to File > Settings > Project > Python Interpreter
3. Click the gear icon and select "Add"
4. Choose "Existing Environment" and select the interpreter at:
   - Windows: `.venv\\Scripts\\python.exe`
   - macOS/Linux: `.venv/bin/python`

5. Install the Ruff plugin:
   - Go to File > Settings > Plugins
   - Search for "Ruff" and install the plugin

6. Configure Ruff as the formatter:
   - Go to File > Settings > Tools > Ruff
   - Enable "Format files on save"
   - Enable "Fix errors on save"

7. Configure Node.js (if working on UI components):
   - Go to File > Settings > Languages & Frameworks > Node.js
   - Set the Node.js interpreter path
"""

    try:
        os.makedirs(".idea", exist_ok=True)
        with open(os.path.join(".idea", "PYCHARM_SETUP.md"), "w") as f:
            f.write(pycharm_readme)
    except Exception:
        logger.exception("Error creating PyCharm setup instructions")
        return False

    logger.info("PyCharm configuration instructions created.")
    return True


def install_pnpm_globally() -> bool:  # noqa: C901, PLR0912
    """Install pnpm globally using corepack or npm."""
    logger.info("Attempting to install pnpm globally...")

    corepack_exe = shutil.which("corepack")
    if not corepack_exe:
        logger.warning(
            "corepack command not found in PATH. Cannot use corepack to enable pnpm."
        )
    else:
        logger.info(
            f"Found corepack at: {corepack_exe}. Attempting 'corepack enable'..."
        )
        exit_code, stdout, stderr = run_command([corepack_exe, "enable"])
        if exit_code == 0:
            # Allow stdout to be multiline by removing strip()
            logger.info(f"corepack enable succeeded. Output:\n{stdout}")
            if stderr:
                logger.debug(f"corepack enable stderr:\n{stderr}")

            # Verify pnpm installation after enabling corepack
            logger.info("Verifying pnpm after 'corepack enable'...")
            pnpm_version = get_pnpm_version()
            if pnpm_version:
                logger.info(f"pnpm is now available via corepack: {pnpm_version}")
                return True
            else:
                logger.error(
                    "pnpm is still not available after successful 'corepack enable'. This is unexpected. Will try npm install."
                )
                # Proceed to try npm install as a fallback
        else:
            logger.warning(
                f"Failed to enable corepack (exit code {exit_code}). stderr:\n{stderr}\nstdout:\n{stdout}"
            )

    # Fallback to npm if corepack path failed or corepack enable didn't make pnpm available
    logger.info(
        "Attempting to install pnpm globally using npm as a fallback/alternative..."
    )
    npm_exe = shutil.which("npm")
    if not npm_exe:
        logger.error(
            "npm command not found in PATH. Cannot install pnpm globally using npm."
        )
        return False

    logger.info(f"Found npm at: {npm_exe}. Attempting 'npm install -g pnpm'...")
    exit_code_npm, stdout_npm, stderr_npm = run_command([
        npm_exe,
        "install",
        "-g",
        "pnpm",
    ])
    if exit_code_npm != 0:
        # Check if the error is EEXIST (file already exists)
        if "EEXIST" in stderr_npm and "file already exists" in stderr_npm.lower():
            logger.warning(
                f"npm install -g pnpm reported EEXIST (file already exists). This is likely okay if pnpm (e.g. corepack shim) is already in place. stderr:\n{stderr_npm}"
            )
            # Proceed to verification, as pnpm might already be correctly installed/shimmed
        else:
            logger.error(
                f"Error installing pnpm globally via npm (exit code {exit_code_npm}). stderr:\n{stderr_npm}"
            )
            if stdout_npm:  # Only log stdout if it's not empty
                logger.debug(f"npm install stdout:\n{stdout_npm}")
            return False
    else:
        logger.info("pnpm install via npm reported success.")
    if stdout_npm:  # Only log stdout if it's not empty
        logger.debug(f"npm install stdout:\n{stdout_npm}")
    if (
        stderr_npm
    ):  # Also log stderr for npm install on success, as it might contain warnings
        logger.debug(f"npm install stderr (on success):\n{stderr_npm}")

    # Verify pnpm installation after npm install
    logger.info("Verifying pnpm after 'npm install -g pnpm'...")
    pnpm_version_after_npm = get_pnpm_version()
    if pnpm_version_after_npm:
        logger.info(f"pnpm is now available via npm install: {pnpm_version_after_npm}")
        return True
    else:
        logger.error(
            "pnpm is still not available after 'npm install -g pnpm' reported success. This may indicate a PATH issue not reflected in the current script environment."
        )
        return False


def install_node_dependencies() -> bool:
    """Install Node.js dependencies using pnpm.

    Returns:
        True if successful, False otherwise
    """
    logger.info("Installing Node.js dependencies using pnpm...")

    # Check for package.json in root directory
    if os.path.exists("package.json"):
        logger.info("Found package.json in root directory")
        exit_code, stdout, stderr = run_command(["npx", "pnpm", "install"])
        if exit_code != 0:
            logger.error(
                f"Error installing Node.js dependencies with npx pnpm: {stderr}"
            )
            return False
        logger.debug(stdout)

    # Check for package.json in ui/react_frontend directory
    ui_dir = "ui/react_frontend"
    if os.path.exists(os.path.join(ui_dir, "package.json")):
        logger.info(f"Found package.json in {ui_dir} directory")
        exit_code, stdout, stderr = run_command(["npx", "pnpm", "install"], cwd=ui_dir)
        if exit_code != 0:
            logger.error(
                f"Error installing Node.js dependencies with npx pnpm in {ui_dir}: {stderr}"
            )
            return False
        logger.debug(stdout)

    # Check for package.json in sdk/javascript directory
    sdk_dir = "sdk/javascript"
    if os.path.exists(os.path.join(sdk_dir, "package.json")):
        logger.info(f"Found package.json in {sdk_dir} directory")
        exit_code, stdout, stderr = run_command(["npx", "pnpm", "install"], cwd=sdk_dir)
        if exit_code != 0:
            logger.error(
                f"Error installing Node.js dependencies with npx pnpm in {sdk_dir}: {stderr}"
            )
            return False
        logger.debug(stdout)

    return True


def print_enhanced_next_steps() -> None:
    """Print enhanced next steps for the user."""
    next_steps = ["\n=== Next Steps ===", "1. Activate the virtual environment:"]

    if platform.system() == "Windows":
        next_steps.append("   .venv\\Scripts\\activate")
    else:
        next_steps.append("   source .venv/bin/activate")

    next_steps.extend([
        "\n2. Install IDE extensions:",
        "   VS Code:",
        "   - Ruff: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff",
        "   - Python: https://marketplace.visualstudio.com/items?itemName=ms-python.python",
        "   - ESLint: https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint",
        "   - Prettier: https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode",
        "\n   PyCharm:",
        "   - Ruff: https://plugins.jetbrains.com/plugin/20574-ruff",
        "   - Node.js: https://plugins.jetbrains.com/plugin/6098-node-js",
        "\n3. Run pre-commit hooks on all files:",
        "   pre-commit run --all-files",
        "\n4. Run tests to verify the setup:",
        "   pytest",
        "   pnpm test (for UI components)",
        "\n5. Start the development server:",
        "   For backend: python -m uvicorn api.main:app --reload",
        "   For frontend: cd ui/react_frontend && pnpm start",
        "\nFor more information, see the documentation:",
        "- README.md",
        "- docs/contributing.md",
        "- docs/ide_setup.md",
        "- docs/getting-started.md",
    ])

    # Use a single logger.info call with joined strings to avoid T201 warnings
    logger.info("\n".join(next_steps))


def apply_config_to_args(args: argparse.Namespace, config: dict) -> argparse.Namespace:
    """Apply configuration from file to command-line arguments.

    Args:
        args: Command-line arguments
        config: Configuration dictionary

    Returns:
        Updated arguments
    """
    # Apply system dependencies configuration
    if "system_dependencies" in config:
        sys_deps = config["system_dependencies"]
        args.no_system_deps = not sys_deps.get("check_system_deps", True)
        args.node_version = sys_deps.get("node_version", args.node_version)
        args.force_install_deps = sys_deps.get(
            "force_install_deps", args.force_install_deps
        )

    # Apply environment setup configuration
    if "environment_setup" in config:
        env_setup = config["environment_setup"]
        args.no_venv = not env_setup.get("create_venv", True)
        args.no_deps = not env_setup.get("install_deps", True)
        args.no_pre_commit = not env_setup.get("setup_pre_commit", True)
        args.no_ide_config = not env_setup.get("configure_ide", True)
        args.ide = env_setup.get("ide", args.ide)

    # Apply setup profile configuration
    if "setup_profile" in config:
        profile = config["setup_profile"].get("profile", "full")
        args.minimal = profile == "minimal"
        args.ui_only = profile == "ui_only"
        args.backend_only = profile == "backend_only"
        args.full = profile == "full"

    return args


def setup_environment(args: argparse.Namespace) -> bool:
    """Set up the development environment based on arguments.

    Args:
        args: Command-line arguments

    Returns:
        True if successful, False if there were non-critical errors
    """
    success = True

    # Check if running in a virtual environment
    if is_venv_activated():
        logger.warning("Running in an activated virtual environment.")
        logger.warning(
            "This script is designed to be run outside of a virtual environment."
        )
        logger.warning("Continuing anyway...")

    # Check system dependencies
    if not check_system_dependencies(args):
        logger.warning("Some system dependencies are missing.")
        logger.warning("You may encounter issues during setup.")
        success = False

    # Create virtual environment (skip for UI-only setup)
    if not args.no_venv and not args.ui_only and not create_virtual_environment():
        logger.error("Failed to create virtual environment.")
        return False  # Critical error

    # Install Python dependencies (skip for UI-only setup)
    if not args.no_deps and not args.ui_only and not install_dependencies():
        logger.error("Failed to install Python dependencies.")
        success = False

    # Install Node.js dependencies (skip for backend-only setup)
    if not args.no_deps and not args.backend_only and not install_node_dependencies():
        logger.error("Failed to install Node.js dependencies.")
        success = False

    # Set up pre-commit hooks (skip for UI-only setup)
    if not args.no_pre_commit and not args.ui_only and not setup_pre_commit():
        logger.error("Failed to set up pre-commit hooks.")
        success = False

    # Configure IDEs
    if not args.no_ide_config and not configure_ides(args.ide):
        logger.error("Failed to configure IDEs.")
        success = False

    return success


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args()

    # Load configuration from file if specified
    if args.config_file:
        config = load_config_file(args.config_file)
        if config:
            args = apply_config_to_args(args, config)

    # Apply setup profile
    args = apply_setup_profile(args)

    # Set up the environment
    success = setup_environment(args)

    # Create sample configuration file
    if not args.config_file:
        create_sample_config_file()

    # Print next steps
    print_enhanced_next_steps()

    if not success:
        logger.warning("\nSome steps failed. See the output above for details.")
        return 1

    logger.info("\nDevelopment environment setup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
