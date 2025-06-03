#!/usr/bin/env python3
"""
Cross-platform utilities for GitHub Actions workflows.

This module provides utilities to handle cross-platform differences
in GitHub Actions workflows, particularly for Windows PowerShell vs Unix bash.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


def get_platform_info() -> dict[str, str]:
    """Get platform information for debugging."""
    return {
        "system": platform.system(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "is_windows": platform.system().lower() == "windows",
        "is_macos": platform.system().lower() == "darwin",
        "is_linux": platform.system().lower() == "linux",
    }


def normalize_path(path: Union[str, Path]) -> str:
    """Normalize path for current platform."""
    path_obj = Path(path)
    return str(path_obj.resolve())


def get_timeout_for_platform(base_timeout: int, platform_multipliers: Optional[dict[str, float]] = None) -> int:
    """
    Get platform-specific timeout values.
    
    Args:
        base_timeout: Base timeout in minutes
        platform_multipliers: Optional multipliers for different platforms
    
    Returns:
        Adjusted timeout in minutes

    """
    if platform_multipliers is None:
        platform_multipliers = {
            "windows": 1.5,  # Windows typically needs 50% more time
            "darwin": 1.2,   # macOS sometimes needs 20% more time
            "linux": 1.0,    # Linux is the baseline
        }

    system = platform.system().lower()
    multiplier = platform_multipliers.get(system, 1.0)
    return int(base_timeout * multiplier)


def run_command_with_timeout(
    command: list[str],
    timeout_seconds: int = 300,
    cwd: Optional[str] = None,
    env: Optional[dict[str, str]] = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a command with platform-appropriate timeout handling.
    
    Args:
        command: Command and arguments to run
        timeout_seconds: Timeout in seconds
        cwd: Working directory
        env: Environment variables
        capture_output: Whether to capture stdout/stderr
    
    Returns:
        CompletedProcess instance

    """
    # Adjust timeout for platform
    platform_info = get_platform_info()
    if platform_info["is_windows"]:
        timeout_seconds = int(timeout_seconds * 1.5)
    elif platform_info["is_macos"]:
        timeout_seconds = int(timeout_seconds * 1.2)

    try:
        result = subprocess.run(
            command,
            timeout=timeout_seconds,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=True,
            check=False,
        )
        return result
    except subprocess.TimeoutExpired as e:
        print(f"Command timed out after {timeout_seconds} seconds: {' '.join(command)}")
        raise e


def get_shell_command(script_content: str) -> list[str]:
    """Get appropriate shell command for current platform."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return ["powershell", "-Command", script_content]
    return ["bash", "-c", script_content]


def create_cross_platform_script(
    bash_script: str,
    powershell_script: str,
    output_dir: str = "scripts/temp",
) -> str:
    """
    Create a cross-platform script that runs appropriate version based on OS.
    
    Args:
        bash_script: Bash script content
        powershell_script: PowerShell script content
        output_dir: Directory to save scripts
    
    Returns:
        Path to the main script

    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write bash script
    bash_file = output_path / "script.sh"
    with open(bash_file, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write(bash_script)
    bash_file.chmod(0o755)

    # Write PowerShell script
    ps_file = output_path / "script.ps1"
    with open(ps_file, "w", encoding="utf-8") as f:
        f.write(powershell_script)

    # Write main script
    main_script = output_path / "run_script.py"
    main_content = '''#!/usr/bin/env python3
"""Auto-generated cross-platform script runner."""

import platform
import subprocess
import sys
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    
    if platform.system().lower() == "windows":
        script_file = script_dir / "script.ps1"
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_file)]
    else:
        script_file = script_dir / "script.sh"
        cmd = ["bash", str(script_file)]
    
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    with open(main_script, "w", encoding="utf-8") as f:
        f.write(main_content)
    main_script.chmod(0o755)

    return str(main_script)


def get_recommended_timeouts() -> dict[str, dict[str, int]]:
    """Get recommended timeout values for different workflow steps."""
    base_timeouts = {
        "node_install": 20,
        "python_deps": 25,
        "essential_deps": 15,
        "security_tools": 15,
        "security_scans": 20,
        "tests": 30,
        "docker_build": 30,
    }

    platform_info = get_platform_info()

    timeouts = {}
    for step, base_timeout in base_timeouts.items():
        timeouts[step] = {
            "linux": base_timeout,
            "macos": int(base_timeout * 1.2),
            "windows": int(base_timeout * 1.5),
        }

    return timeouts


def print_platform_debug_info():
    """Print platform information for debugging."""
    info = get_platform_info()
    print("=== Platform Debug Information ===")
    for key, value in info.items():
        print(f"{key}: {value}")

    print("\n=== Recommended Timeouts ===")
    timeouts = get_recommended_timeouts()
    for step, step_timeouts in timeouts.items():
        print(f"{step}:")
        for platform_name, timeout in step_timeouts.items():
            print(f"  {platform_name}: {timeout} minutes")


if __name__ == "__main__":
    print_platform_debug_info()
