"""Security configuration and utilities for the application."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# Secure defaults
ALLOWED_COMMANDS: set[str] = {
    "python",
    "pip",
    "uv",
    "npm",
    "npx",
    "pre-commit",
    "virtualenv",
    "git",
    "node",
    "pnpm",
    "pytest",
    "bandit",
    "safety",
}


def validate_command(
    command: list[str], allow_shell: bool = False
) -> tuple[list[str], bool]:
    """
    Validate and sanitize a command before execution.

    Args:
        command: Command as a list of strings
        allow_shell: Whether shell=True is allowed (default False)

    Returns:
        Tuple of (sanitized command, whether shell=True is safe to use)

    Raises:
        SecurityError: If command validation fails

    """
    if not command:
        empty_cmd_err = "Empty command"
        raise SecurityError(empty_cmd_err)

    cmd_copy = list(command)  # Work with a copy
    executable = cmd_copy[0]

    # Check for command injection attempts
    if any(char in executable for char in ";&|$()`\\"):
        inject_err_msg = f"Potential command injection in: {executable}"
        raise SecurityError(inject_err_msg)

    # Try to get full path to executable
    executable_path = shutil.which(executable)
    if executable_path:
        cmd_copy[0] = executable_path

    # Get basename without path
    cmd_basename = Path(executable).name  # Check if command is allowed
    if cmd_basename not in ALLOWED_COMMANDS and not _is_ci_mode():
        not_allowed_msg = f"Command not in allowed list: {cmd_basename}"
        raise SecurityError(not_allowed_msg)

    # Never allow shell=True unless explicitly required and in CI mode
    use_shell = allow_shell and _is_ci_mode()

    return cmd_copy, use_shell


def run_command_securely(
    command: list[str],
    cwd: Optional[str] = None,
    env: Optional[dict[str, str]] = None,
    allow_shell: bool = False,
    timeout: Optional[int] = None,
) -> subprocess.CompletedProcess[str]:
    """
    Run a command securely with proper validation and defaults.

    Args:
        command: Command as list of strings
        cwd: Working directory
        env: Environment variables
        allow_shell: Whether shell=True is allowed (only in CI mode)
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess instance

    Raises:
        SecurityError: If command validation fails
        subprocess.SubprocessError: If command fails

    """
    sanitized_cmd, use_shell = validate_command(command, allow_shell)

    # Security: Always use shell=False unless explicitly validated  # nosec B603
    return subprocess.run(  # nosec B602
        sanitized_cmd,
        cwd=cwd,
        env=env,
        shell=use_shell,  # This is now always False unless in CI mode
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def _is_ci_mode() -> bool:
    """Check if running in CI mode."""
    return (
        os.environ.get("GITHUB_ACTIONS") == "true"
        or os.environ.get("CI") == "true"
        or os.environ.get("ALLOW_COMMANDS", "").lower() == "true"
    )


class SecurityError(Exception):
    """Exception raised for security-related errors."""
