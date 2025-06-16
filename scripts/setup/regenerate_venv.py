"""Regenerate venv using uv."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Set up a dedicated logger for this module
logger = logging.getLogger(__name__)


def run_command(
    command: list[str], cwd: Optional[str] = None, capture_output: bool = True
) -> Optional[str]:
    """Run a command and return its output."""
    logger.info("Running command: %s", " ".join(command))
    try:
        # Ensure the first item in command is a full path to the executable
        if command and not Path(command[0]).is_absolute():
            executable = shutil.which(command[0])
            if executable:
                command[0] = executable
            else:
                logger.error("Command not found: %s", command[0])
                return None

        # nosec comment below tells security scanners this is safe as we control the input
        process_result = subprocess.run(  # nosec S603
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False,  # We handle the error code manually
        )

        if process_result.returncode != 0:
            error_message = f"Command failed with exit code {process_result.returncode}"
            logger.error(error_message)
            if process_result.stdout:
                stdout_content = process_result.stdout.strip()
                logger.error("STDOUT: %s", stdout_content)
            if process_result.stderr:
                stderr_content = process_result.stderr.strip()
                logger.error("STDERR: %s", stderr_content)
            return None
        # Store result in a variable to avoid TRY300 error
        result = ""
        if capture_output and process_result.stdout is not None:
            result = process_result.stdout.strip()

    except FileNotFoundError:
        logger.exception(  # TRY401
            "Command not found: %s. Please ensure it is installed and in your PATH.",
            command[0],
        )
        return None
    except Exception:  # TRY401
        logger.exception(  # Removed str(e) from message
            "Error running command '%s'", " ".join(command)
        )
        return None
    else:
        return result


def is_venv_active() -> bool:
    """Check if a virtual environment is active."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def check_venv_status() -> bool:
    """
    Check if we're in a virtual environment.

    Returns:
        bool: True if it's safe to proceed, False otherwise

    """
    if is_venv_active():
        logger.warning("You are currently in a virtual environment.")
        logger.warning(
            "This script should be run from outside any virtual environment."
        )
    return True


def remove_venv_windows(
    venv_dir: str,
) -> tuple[bool, str]:  # ARG001: Removed unused python_exe
    """
    Remove virtual environment on Windows.

    Args:
        venv_dir: Path to the virtual environment

    Returns:
        tuple: (success, venv_dir_to_use)

    """
    try:
        shutil.rmtree(venv_dir, ignore_errors=True)
        if Path(venv_dir).exists():
            logger.info("Using Windows 'rd' command to force-remove directory...")
            # Use full path to rd.exe if possible, otherwise fall back to partial path
            rd_executable = shutil.which("rd") or "rd"
            subprocess.run(
                [rd_executable, "/s", "/q", venv_dir], check=False, capture_output=True
            )  # nosec B607

        if not Path(venv_dir).exists():
            logger.info("Virtual environment at %s removed successfully.", venv_dir)
            return True, venv_dir
    except (OSError, shutil.Error):
        logger.exception(
            "Error removing virtual environment at %s with shutil/rd", venv_dir
        )

    if Path(venv_dir).exists():
        logger.warning(
            "Failed to remove %s. It might be in use. "
            "Attempting to create a new virtual environment with a different name (.venv_new).",
            venv_dir,
        )
        venv_parent = Path(venv_dir).parent
        temp_venv_dir = str(venv_parent / ".venv_new")
        if Path(temp_venv_dir).exists():
            shutil.rmtree(temp_venv_dir, ignore_errors=True)
            if Path(temp_venv_dir).exists():
                # Use full path to rd.exe if possible, otherwise fall back to partial path
                rd_executable = shutil.which("rd") or "rd"
                subprocess.run(
                    [rd_executable, "/s", "/q", temp_venv_dir],
                    check=False,
                    capture_output=True,
                )  # nosec B607
        try:
            Path(temp_venv_dir).mkdir(parents=True, exist_ok=True)
            logger.info(
                "Using temporary directory %s for the new virtual environment.",
                temp_venv_dir,
            )
            logger.warning(
                "Please manually delete the old %s directory and rename "
                "%s to %s after closing all "
                "applications that might be using the old virtual environment.",
                venv_dir,
                temp_venv_dir,
                Path(venv_dir).name,
            )
        except OSError:
            logger.exception("Could not create temporary directory %s", temp_venv_dir)
            return False, venv_dir
        else:
            return True, temp_venv_dir
    return True, venv_dir


def remove_venv_unix(venv_dir: str) -> bool:
    """Remove virtual environment on Unix-like systems."""
    try:
        shutil.rmtree(venv_dir)
        logger.info("Virtual environment at %s removed successfully.", venv_dir)
    except (OSError, shutil.Error):
        logger.exception("Error removing virtual environment at %s", venv_dir)
        return False
    else:
        return True


def remove_existing_venv(
    venv_dir: str,
) -> tuple[bool, str]:  # ARG001: Removed python_exe
    """Remove the existing virtual environment."""
    if not Path(venv_dir).exists():
        logger.info("No existing virtual environment found at %s.", venv_dir)
        return True, venv_dir

    logger.info("Attempting to remove existing virtual environment at %s...", venv_dir)
    if platform.system() == "Windows":
        return remove_venv_windows(venv_dir)
    success = remove_venv_unix(venv_dir)
    return success, venv_dir


def get_venv_python(venv_dir: str) -> str:
    """Get the path to the Python executable in the virtual environment."""
    venv_path = Path(venv_dir)
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "python.exe")
    return str(venv_path / "bin" / "python")


def print_activation_instructions(venv_dir: str) -> None:
    """Print instructions for activating the virtual environment."""
    logger.info("To activate the virtual environment, run:")
    rel_venv_dir = os.path.relpath(venv_dir)
    if platform.system() == "Windows":
        logger.info("    %s\\Scripts\\activate", rel_venv_dir)
    else:
        logger.info("    source %s/bin/activate", rel_venv_dir)


def _determine_compile_sources() -> Optional[list[str]]:
    """
    Determine the source files for `uv pip compile`.

    Returns:
        A list of source files, or None if no suitable source is found.

    """
    compile_sources = []
    if Path("pyproject.toml").exists():
        logger.info("Using pyproject.toml for lockfile generation.")
        compile_sources.append("pyproject.toml")
    elif Path("requirements.txt").exists():
        logger.info("Using requirements.txt for lockfile generation.")
        compile_sources.append("requirements.txt")
        if Path("requirements-dev.txt").exists():
            logger.info("Including requirements-dev.txt for lockfile generation.")
            compile_sources.append("requirements-dev.txt")
    else:
        logger.error(
            "No pyproject.toml or requirements.txt found for lockfile generation."
        )
        return None
    return compile_sources


def _safe_subprocess_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:  # noqa: ANN003
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    if "cwd" in kwargs and isinstance(kwargs["cwd"], Path):
        kwargs["cwd"] = str(kwargs["cwd"])
    allowed_keys = {
        "cwd",
        "timeout",
        "check",
        "shell",
        "text",
        "capture_output",
        "input",
        "encoding",
        "errors",
        "env",
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
    return subprocess.run(cmd, check=False, **filtered_kwargs)


def _perform_venv_creation_steps(
    python_exe: str, venv_dir_path: str
) -> tuple[bool, str]:
    """
    Handle the core venv regeneration steps.

    Returns:
        A tuple (success_flag, path_to_active_venv).

    """
    operation_successful = True

    # Step 1: Remove existing venv
    op_success, venv_to_use_after_removal = remove_existing_venv(venv_dir_path)
    current_venv_path = venv_to_use_after_removal  # Update path, might be .venv_new
    if not op_success:
        logger.error("Failed to remove existing virtual environment. Aborting.")
        operation_successful = False

    # Step 2: Check for uv and create venv
    if operation_successful:
        logger.info(
            "Creating new virtual environment at %s using uv...", current_venv_path
        )
        if not shutil.which("uv"):
            logger.error(
                "uv command not found. Please install uv and ensure it's in your PATH."
            )
            operation_successful = False
        else:
            venv_creation_command = [
                "uv",
                "venv",
                current_venv_path,
                "--python",
                python_exe,
            ]
            if run_command(venv_creation_command) is None:
                logger.error(
                    "Failed to create virtual environment at %s with uv.",
                    current_venv_path,
                )
                operation_successful = False

    # Initialize variables that will be used across steps
    python_in_venv: str = ""
    lockfile: str = "requirements.lock"

    # Step 3: Compile requirements
    if operation_successful:
        python_in_venv = get_venv_python(current_venv_path)
        logger.info("Generating/updating %s using uv pip compile...", lockfile)
        compile_command_base = ["uv", "pip", "compile"]
        output_args = ["-o", lockfile]
        compile_sources = _determine_compile_sources()
        if compile_sources is None:  # Error already logged by helper
            operation_successful = False
        elif run_command(compile_command_base + compile_sources + output_args) is None:
            logger.error("Failed to generate %s.", lockfile)
            operation_successful = False

    # Step 4: Sync environment
    if operation_successful:
        # python_in_venv and lockfile are already defined above and in scope.
        logger.info("Syncing environment to %s with uv pip sync...", lockfile)
        sync_command = ["uv", "pip", "sync", lockfile, "--python", python_in_venv]
        if run_command(sync_command) is None:
            logger.error("Failed to sync environment to %s with uv.", lockfile)
            operation_successful = False

    return operation_successful, current_venv_path


def main() -> int:
    """Regenerate the virtual environment using uv."""
    if not check_venv_status():
        # This path is currently not taken as check_venv_status always returns True
        # If it could fail, this would be a return point.
        pass

    python_exe: str = sys.executable
    base_venv_dir_name = ".venv"
    venv_dir_path: str = str(Path.cwd() / base_venv_dir_name)

    success, venv_to_use = _perform_venv_creation_steps(python_exe, venv_dir_path)

    if not success:
        return 1  # Errors are logged within the helper

    logger.info("\nVirtual environment regenerated and fully synced with uv!")
    print_activation_instructions(venv_to_use)

    logger.info("\nTo update dependencies in the future:")
    logger.info(
        "  1. Edit pyproject.toml or requirements.txt/requirements-dev.txt as needed."
    )
    logger.info(
        "  2. Run this script again (python regenerate_venv.py) to re-lock and re-sync."
    )
    logger.info(
        "For deterministic installs, ensure requirements.lock is committed and use "
        "'uv pip sync requirements.lock'."
    )

    if venv_to_use != venv_dir_path:
        logger.warning(
            "\nIMPORTANT: The new environment is in %s. "
            "Remember to manually delete the old %s "
            "directory and rename %s "
            "to %s.",
            venv_to_use,
            Path(venv_dir_path).name,
            Path(venv_to_use).name,
            Path(venv_dir_path).name,
        )
    return 0


def _exit(code: int = 0) -> NoReturn:
    """Exit the program with the given code."""
    sys.exit(code)


if __name__ == "__main__":
    _exit(main())
