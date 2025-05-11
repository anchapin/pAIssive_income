"""Regenerate venv using uv."""

import logging
import os
import platform
import shutil
import subprocess
import sys

from typing import NoReturn
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(
    command: list[str], cwd: Optional[str] = None, capture_output: bool = True
) -> Optional[str]:
    """Run a command and return its output."""
    logging.info("Running command: {}".format(" ".join(command)))
    try:
        process_result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False,  # We handle the error code manually
        )

        if process_result.returncode != 0:
            error_message = f"Command failed with exit code {process_result.returncode}"
            logging.error(error_message)
            if process_result.stdout:
                stdout_content = process_result.stdout.strip()
                logging.error(f"STDOUT: {stdout_content}")
            if process_result.stderr:
                stderr_content = process_result.stderr.strip()
                logging.error(f"STDERR: {stderr_content}")
            return None
        elif capture_output:
            return (
                process_result.stdout.strip()
                if process_result.stdout is not None
                else ""
            )
        else:
            return ""

    except FileNotFoundError:
        logging.exception(  # TRY401
            f"Command not found: {command[0]}. Please ensure it is installed and in your PATH."
        )
        return None
    except Exception:  # TRY401
        logging.exception(  # Removed str(e) from message
            "Error running command '{}'".format(" ".join(command))
        )
        return None


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
        logging.warning(
            "This script should be run from outside any virtual environment."
        )
    return True


def remove_venv_windows(
    venv_dir: str,
) -> tuple[bool, str]:  # ARG001: Removed unused python_exe
    """Remove virtual environment on Windows.

    Args:
        venv_dir: Path to the virtual environment

    Returns:
        tuple: (success, venv_dir_to_use)
    """
    try:
        shutil.rmtree(venv_dir, ignore_errors=True)
        if os.path.exists(venv_dir):
            logging.info("Using Windows 'rd' command to force-remove directory...")
            subprocess.run(
                ["rd", "/s", "/q", venv_dir], check=False, capture_output=True
            )

        if not os.path.exists(venv_dir):
            logging.info(f"Virtual environment at {venv_dir} removed successfully.")
            return True, venv_dir
    except (OSError, shutil.Error):
        logging.exception(
            f"Error removing virtual environment at {venv_dir} with shutil/rd"
        )

    if os.path.exists(venv_dir):
        logging.warning(
            f"Failed to remove {venv_dir}. It might be in use. "
            + "Attempting to create a new virtual environment with a different name (.venv_new)."
        )
        temp_venv_dir: str = os.path.join(os.path.dirname(venv_dir), ".venv_new")
        if os.path.exists(temp_venv_dir):
            shutil.rmtree(temp_venv_dir, ignore_errors=True)
            if os.path.exists(temp_venv_dir):
                subprocess.run(
                    ["rd", "/s", "/q", temp_venv_dir], check=False, capture_output=True
                )
        try:
            os.makedirs(temp_venv_dir, exist_ok=True)
            logging.info(
                f"Using temporary directory {temp_venv_dir} for the new virtual environment."
            )
            logging.warning(
                f"Please manually delete the old {venv_dir} directory and rename "
                f"{temp_venv_dir} to {os.path.basename(venv_dir)} after closing all "
                "applications that might be using the old virtual environment."
            )
        except OSError:
            logging.exception(f"Could not create temporary directory {temp_venv_dir}")
            return False, venv_dir
        else:
            return True, temp_venv_dir
    return True, venv_dir


def remove_venv_unix(venv_dir: str) -> bool:
    """Remove virtual environment on Unix-like systems."""
    try:
        shutil.rmtree(venv_dir)
        logging.info(f"Virtual environment at {venv_dir} removed successfully.")
    except (OSError, shutil.Error):
        logging.exception(f"Error removing virtual environment at {venv_dir}")
        return False
    else:
        return True


def remove_existing_venv(
    venv_dir: str,
) -> tuple[bool, str]:  # ARG001: Removed python_exe
    """Remove the existing virtual environment."""
    if not os.path.exists(venv_dir):
        logging.info(f"No existing virtual environment found at {venv_dir}.")
        return True, venv_dir

    logging.info(f"Attempting to remove existing virtual environment at {venv_dir}...")
    if platform.system() == "Windows":
        return remove_venv_windows(venv_dir)
    else:
        success = remove_venv_unix(venv_dir)
        return success, venv_dir


def get_venv_python(venv_dir: str) -> str:
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return str(os.path.join(venv_dir, "Scripts", "python.exe"))
    else:
        return str(os.path.join(venv_dir, "bin", "python"))


def print_activation_instructions(venv_dir: str) -> None:
    """Print instructions for activating the virtual environment."""
    logging.info("To activate the virtual environment, run:")
    rel_venv_dir = os.path.relpath(venv_dir)
    if platform.system() == "Windows":
        logging.info(f"    {rel_venv_dir}\\Scripts\\activate")
    else:
        logging.info(f"    source {rel_venv_dir}/bin/activate")


def _determine_compile_sources() -> Optional[list[str]]:
    """Determines the source files for `uv pip compile`.

    Returns:
        A list of source files, or None if no suitable source is found.
    """
    compile_sources = []
    if os.path.exists("pyproject.toml"):
        logging.info("Using pyproject.toml for lockfile generation.")
        compile_sources.append("pyproject.toml")
    elif os.path.exists("requirements.txt"):
        logging.info("Using requirements.txt for lockfile generation.")
        compile_sources.append("requirements.txt")
        if os.path.exists("requirements-dev.txt"):
            logging.info("Including requirements-dev.txt for lockfile generation.")
            compile_sources.append("requirements-dev.txt")
    else:
        logging.error(
            "No pyproject.toml or requirements.txt found for lockfile generation."
        )
        return None
    return compile_sources


def _perform_venv_creation_steps(
    python_exe: str, venv_dir_path: str
) -> tuple[bool, str]:
    """Handles the core venv regeneration steps.

    Returns:
        A tuple (success_flag, path_to_active_venv).
    """
    operation_successful = True
    current_venv_path = venv_dir_path  # Start with original, update if temp is used

    # Step 1: Remove existing venv
    op_success, venv_to_use_after_removal = remove_existing_venv(venv_dir_path)
    current_venv_path = venv_to_use_after_removal  # Update path, might be .venv_new
    if not op_success:
        logging.error("Failed to remove existing virtual environment. Aborting.")
        operation_successful = False

    # Step 2: Check for uv and create venv
    if operation_successful:
        logging.info(
            f"Creating new virtual environment at {current_venv_path} using uv..."
        )
        if not shutil.which("uv"):
            logging.error(
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
                logging.error(
                    f"Failed to create virtual environment at {current_venv_path} with uv."
                )
                operation_successful = False

    # Step 3: Compile requirements
    if operation_successful:
        python_in_venv: str = get_venv_python(current_venv_path)
        lockfile: str = "requirements.lock"
        logging.info(f"Generating/updating {lockfile} using uv pip compile...")
        compile_command_base = ["uv", "pip", "compile"]
        output_args = ["-o", lockfile]
        compile_sources = _determine_compile_sources()
        if compile_sources is None:  # Error already logged by helper
            operation_successful = False
        elif run_command(compile_command_base + compile_sources + output_args) is None:
            logging.error(f"Failed to generate {lockfile}.")
            operation_successful = False

    # Step 4: Sync environment
    if operation_successful:
        # python_in_venv and lockfile are already defined in Step 3 and in scope.
        # Re-getting python_in_venv is fine if current_venv_path could change, but it doesn't between step 3 and 4.
        # For clarity, ensure they are used from the Step 3 definition.
        logging.info(f"Syncing environment to {lockfile} with uv pip sync...")
        sync_command = ["uv", "pip", "sync", lockfile, "--python", python_in_venv]
        if run_command(sync_command) is None:
            logging.error(f"Failed to sync environment to {lockfile} with uv.")
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
    venv_dir_path: str = os.path.join(os.getcwd(), base_venv_dir_name)

    success, venv_to_use = _perform_venv_creation_steps(python_exe, venv_dir_path)

    if not success:
        return 1  # Errors are logged within the helper

    logging.info("\nVirtual environment regenerated and fully synced with uv!")
    print_activation_instructions(venv_to_use)

    logging.info("\nTo update dependencies in the future:")
    logging.info(
        "  1. Edit pyproject.toml or requirements.txt/requirements-dev.txt as needed."
    )
    logging.info(
        "  2. Run this script again (python regenerate_venv.py) to re-lock and re-sync."
    )
    logging.info(
        "For deterministic installs, ensure requirements.lock is committed and use 'uv pip sync requirements.lock'."
    )

    if venv_to_use != venv_dir_path:
        logging.warning(
            f"\nIMPORTANT: The new environment is in {venv_to_use}. "
            f"Remember to manually delete the old {os.path.basename(venv_dir_path)} "
            f"directory and rename {os.path.basename(venv_to_use)} "
            f"to {os.path.basename(venv_dir_path)}."
        )
    return 0


def _exit(code: int = 0) -> NoReturn:
    """Exit the program with the given code."""
    sys.exit(code)


if __name__ == "__main__":
    _exit(main())
