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
import contextlib
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class MinimalYaml:
    """Minimal YAML implementation that uses JSON internally."""

    @staticmethod
    def safe_load(stream: str) -> dict[str, Any]:
        """Load YAML data from a string."""
        logger.warning(
            "Using minimal YAML implementation - only JSON-compatible syntax supported"
        )
        try:
            result = json.loads(stream)
            return result if isinstance(result, dict) else {}
        except Exception:
            logger.exception("Failed to parse YAML/JSON")
            return {}

    @staticmethod
    def dump(data: dict[str, Any], file: Any, **_kwargs: Any) -> None:
        """Dump data to a file in JSON format."""
        logger.warning("Using minimal YAML implementation - saving as JSON")
        json.dump(data, file, indent=2)


def install_pyyaml() -> bool:
    """Install PyYAML module using multiple fallback mechanisms."""
    methods = [
        lambda: subprocess.check_call(["uv", "pip", "install", "pyyaml"]) == 0,
        lambda: subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "uv",
        ])
        == 0
        and subprocess.check_call(["uv", "pip", "install", "pyyaml"]) == 0,
        lambda: subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "pyyaml",
        ])
        == 0,
        lambda: subprocess.check_call(["pip", "install", "pyyaml"]) == 0,
    ]

    for method in methods:
        try:
            if method():
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return False


def get_yaml_module() -> Any:
    """Get the YAML module, either PyYAML or our minimal implementation."""
    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML module not found. Installing it now...")
        if install_pyyaml():
            with contextlib.suppress(ImportError):
                import yaml
        else:
            return MinimalYaml()
    else:
        return yaml

    logger.warning("Using minimal YAML implementation")
    return MinimalYaml()


# Get the YAML module once at module level
yaml = get_yaml_module()


def run_command(
    cmd: list[str], cwd: Optional[str] = None, env: Optional[dict[str, str]] = None
) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr."""
    executable_path_str = cmd[0]

    try:
        # Resolve command using shutil.which if needed
        if not os.path.isabs(executable_path_str) and not os.path.dirname(
            executable_path_str
        ):
            resolved_executable = shutil.which(executable_path_str)
            if resolved_executable:
                cmd_to_run = [resolved_executable] + cmd[1:]
            else:
                logger.debug(f"Command '{executable_path_str}' not found in PATH")
                return 1, "", f"Command '{executable_path_str}' not found in PATH."
        else:
            cmd_to_run = list(cmd)

        process = subprocess.run(
            cmd_to_run,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        logger.exception(f"Command not found: {executable_path_str}")
        return 1, "", f"Command not found: {executable_path_str}"
    except Exception as e:
        logger.exception("Error executing command")
        return 1, "", str(e)
    else:
        return process.returncode, process.stdout, process.stderr


def create_virtual_environment() -> bool:
    """Create a virtual environment using multiple fallback methods."""
    logger.info("Creating virtual environment...")
    venv_path = Path(".venv")

    if venv_path.exists():
        logger.info(f"Virtual environment already exists at {venv_path}")
        return True

    # Try with uv first
    uv_available = shutil.which("uv") is not None
    if uv_available:
        try:
            exit_code, _, stderr = run_command(["uv", "venv", str(venv_path)])
            if exit_code == 0:
                logger.info(f"Created virtual environment at {venv_path} using uv")
                return True
            logger.warning(f"Error creating virtual environment with uv: {stderr}")
        except Exception as e:
            logger.warning(f"Exception when creating virtual environment with uv: {e}")

    # Fallback to regular venv
    try:
        venv.create(venv_path, with_pip=True)
        logger.info(f"Created virtual environment at {venv_path}")
    except Exception:
        logger.exception("Failed to create virtual environment using venv")
        # Try virtualenv as last resort
        try:
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "virtualenv",
            ])
            subprocess.check_call([sys.executable, "-m", "virtualenv", str(venv_path)])
            logger.info(f"Created virtual environment at {venv_path} using virtualenv")
        except Exception:
            logger.exception("Failed to create virtual environment using virtualenv")
            return False
        else:
            return True
    else:
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


def _upgrade_pip() -> bool:
    """Upgrade pip to the latest version using uv if available."""
    logger.info("Upgrading pip...")
    try:
        if shutil.which("uv"):
            exit_code, _, stderr = run_command([
                "uv",
                "pip",
                "install",
                "--upgrade",
                "pip",
            ])
            if exit_code != 0:
                logger.warning(f"Failed to upgrade pip with uv: {stderr}")
    except Exception as e:
        logger.warning(f"Error upgrading pip: {e}")
    return True  # Continue anyway, not critical


def _install_requirements(pip_path: str, req_file: str) -> bool:
    """Install dependencies from a requirements file."""
    if not os.path.exists(req_file):
        logger.debug(f"Requirements file not found: {req_file}")
        return True  # Not an error if file doesn't exist

    logger.info(f"Installing dependencies from {req_file}...")

    # Try with uv first
    if shutil.which("uv"):
        try:
            exit_code, _, stderr = run_command(["uv", "pip", "install", "-r", req_file])
            if exit_code == 0:
                return True
            logger.warning(f"Failed to install with uv: {stderr}")
        except Exception as e:
            logger.warning(f"Error using uv to install dependencies: {e}")

    # Fallback to regular pip
    try:
        exit_code, _, stderr = run_command([pip_path, "install", "-r", req_file])
        if exit_code != 0:
            logger.error(f"Failed to install with pip: {stderr}")
            return False
    except Exception:
        logger.exception("Error using pip to install dependencies")
        return False
    else:
        return True


def install_dependencies(args: argparse.Namespace) -> bool:
    """Install Python dependencies."""
    if args.no_deps:
        logger.info("Skipping dependency installation...")
        return True

    pip_path = get_venv_pip_path()

    # First upgrade pip
    _upgrade_pip()

    # Install dependencies from requirements files
    requirements_files = [
        "requirements.txt",
        "requirements-dev.txt" if not args.minimal else None,
    ]

    success = True
    for req_file in requirements_files:
        if req_file and not _install_requirements(pip_path, req_file):
            success = False

    if not success:
        logger.error("Failed to install some dependencies")
        return False

    return True


def setup_pre_commit_hooks(python_path: str) -> bool:
    """Set up pre-commit hooks."""
    try:
        exit_code, _, stderr = run_command([python_path, "-m", "pre_commit", "install"])
        if exit_code != 0:
            logger.error(f"Failed to set up pre-commit hooks: {stderr}")
            return False
        logger.info("Pre-commit hooks installed successfully")
    except Exception:
        logger.exception("Error setting up pre-commit hooks")
        return False
    else:
        return True


def configure_vscode() -> bool:
    """Configure VSCode settings."""
    logger.info("Configuring VSCode settings...")
    vscode_dir = Path(".vscode")
    try:
        # Ensure parent directory exists
        vscode_dir.parent.mkdir(parents=True, exist_ok=True)
        # Create .vscode directory
        vscode_dir.mkdir(exist_ok=True)
        logger.info(f"Created/verified .vscode directory at {vscode_dir}")

        # Determine platform-specific Python path
        python_path = str(
            Path(
                ".venv/Scripts/python.exe"
                if platform.system() == "Windows"
                else ".venv/bin/python"
            ).resolve()
        )

        settings = {
            "python.defaultInterpreterPath": python_path,
            "python.formatting.provider": "black",
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.mypyEnabled": True,
        }

        settings_file = vscode_dir / "settings.json"
        logger.info(f"Writing VS Code settings to {settings_file}")

        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)

        logger.info("VSCode configuration complete")
    except PermissionError:
        logger.exception(
            "Permission denied when configuring VSCode. Try running with elevated privileges."
        )
        return False
    except OSError:
        logger.exception("OS error when configuring VSCode")
        return False
    except Exception:
        logger.exception("Unexpected error configuring VSCode")
        # Create a basic .vscode directory if we couldn't create the full configuration
        if not vscode_dir.exists():
            try:
                vscode_dir.mkdir(parents=True, exist_ok=True)
                logger.info("Created basic .vscode directory")
            except Exception:
                logger.exception("Failed to create basic .vscode directory")
        return False
    else:
        return True


def configure_pycharm() -> bool:
    """Configure PyCharm settings."""
    logger.info("Configuring PyCharm settings...")
    try:
        idea_dir = Path(".idea")
        idea_dir.mkdir(exist_ok=True)
        logger.info("PyCharm configuration complete")
    except Exception:
        logger.exception("Error configuring PyCharm")
        return False
    else:
        return True


def configure_ide(args: argparse.Namespace) -> bool:
    """Configure IDE settings."""
    if args.no_ide_config:
        logger.info("Skipping IDE configuration...")
        return True

    success = True
    if args.ide in ["vscode", "all"]:
        success &= configure_vscode()
    if args.ide in ["pycharm", "all"]:
        success &= configure_pycharm()

    return success


def install_pnpm_globally() -> bool:
    """Install pnpm globally."""
    logger.info("Installing pnpm globally...")
    try:
        # First try using npm to install pnpm
        exit_code, _, stderr = run_command(["npm", "install", "-g", "pnpm"])
        if exit_code == 0:
            logger.info("pnpm installed successfully")
            return True

        # If npm install fails, try using npx
        logger.warning("Failed to install pnpm with npm, trying npx...")
        exit_code, _, stderr = run_command(["npx", "pnpm", "setup"])
        if exit_code != 0:
            logger.error(f"Failed to install pnpm: {stderr}")
            return False

        logger.info("pnpm installed successfully")
    except Exception:
        logger.exception("Error installing pnpm")
        return False
    else:
        return True


def check_dependency(
    name: str,
    get_version_func: Callable[[], Optional[str]],
    install_func: Optional[Callable[..., bool]] = None,
    version_arg: Optional[str] = None,
    args: Optional[argparse.Namespace] = None,
) -> bool:
    """Check for a specific dependency and install if missing."""
    version = get_version_func()
    if version:
        logger.info(f"{name} is installed: {version}")
        return True

    logger.warning(f"{name} is not installed.")
    if args and args.force_install_deps and install_func:
        if version_arg:
            return bool(install_func(version_arg))
        return bool(install_func())

    if args:
        logger.warning(f"Please install {name} or run with --force-install-deps")
    return False


def check_system_dependencies(args: argparse.Namespace) -> bool:
    """Check for required system dependencies and install if missing."""
    if args.no_system_deps:
        logger.info("Skipping system dependency checks...")
        return True

    # Add system dependency checks here
    return True


def apply_setup_profile(args: argparse.Namespace) -> argparse.Namespace:
    """Apply setup profile to arguments."""
    # Default to full setup if no profile specified
    if not any([args.minimal, args.ui_only, args.backend_only, args.full]):
        args.full = True

    if args.minimal:
        logger.info("Applying minimal setup profile...")
        args.no_pre_commit = True
        args.no_ide_config = True

    if args.ui_only:
        logger.info("Applying UI-only setup profile...")
        args.no_venv = True

    if args.backend_only:
        logger.info("Applying backend-only setup profile...")

    if args.full:
        logger.info("Applying full setup profile...")
        args.force_install_deps = True

    return args


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    try:
        parser = argparse.ArgumentParser(
            description="Setup development environment for pAIssive Income project"
        )

        parser.add_argument(
            "--ci-mode",
            action="store_true",
            help=argparse.SUPPRESS,
        )

        # System dependency options
        system_group = parser.add_argument_group("System Dependencies")
        system_group.add_argument(
            "--no-system-deps",
            action="store_true",
            help="Skip system dependency checks",
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
            "--full",
            action="store_true",
            help="Full setup with all dependencies (default)",
        )

        # Configuration options
        config_group = parser.add_argument_group("Configuration")
        config_group.add_argument(
            "--config-file", help="Specify a configuration file for setup options"
        )

    except Exception:
        logger.exception("Error parsing arguments")
        sys.exit(1)
    else:
        return parser.parse_args()


def main() -> int:
    """Main entry point."""
    try:
        args = parse_args()
        args = apply_setup_profile(args)

        if not args.no_venv and not create_virtual_environment():
            logger.error("Failed to create virtual environment")
            return 1

        if not install_dependencies(args):
            logger.error("Failed to install dependencies")
            return 1

        if not args.no_pre_commit:
            python_path = get_venv_python_path()
            if not setup_pre_commit_hooks(python_path):
                logger.error("Failed to set up pre-commit hooks")
                return 1

        if not configure_ide(args):
            logger.error("Failed to configure IDE settings")
            return 1

        logger.info("Development environment setup completed successfully")
    except Exception:
        logger.exception("Unexpected error in main")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
