#!/usr/bin/env python
"""
Script to run MCP adapter tests without loading the main conftest.py.
This script is used by the CI/CD pipeline to run the MCP adapter tests.
"""

import os
import sys
import subprocess  # nosec B404 - subprocess is used with proper security controls
import logging
import shutil
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_mcp_tests() -> int:
    """Run MCP adapter tests without loading the main conftest.py.

    Returns:
        int: The return code from the test run (0 for success, non-zero for failure)
    """
    logger.info("Running MCP adapter tests...")

    # Set environment variables to avoid loading the main conftest.py
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")

    # Define the test command with fixed arguments
    # These are hardcoded and not user-provided, so they're safe
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--no-header",
        "--no-summary",
        "tests/ai_models/adapters/test_mcp_adapter.py",
        "tests/test_mcp_import.py",
        "tests/test_mcp_top_level_import.py",
        "-k",
        "not test_mcp_server",
        "--confcutdir=tests/ai_models/adapters",
        "--noconftest",
        "--no-cov",  # Disable coverage to avoid issues with the coverage report
    ]

    # Validate the command to ensure it's safe to execute
    if not _validate_command(cmd):
        logger.error("Invalid command detected")
        return 1

    try:
        # Use absolute path for the executable when possible
        if shutil.which(sys.executable):
            cmd[0] = shutil.which(sys.executable)

        # nosec comment below tells Bandit to ignore this line since we've added proper validation
        result = subprocess.run(  # nosec B603
            cmd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            shell=False,  # Explicitly set shell=False for security
        )

        # Log the output instead of using print
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
    except Exception:
        # No need to include the exception object in the logging.exception call
        logger.exception("Error running tests")
        return 1
    else:
        # This will only execute if no exception is raised
        # Ensure we return an int, not Any
        return 0 if result.returncode == 0 else 1


def _validate_command(command: List[str]) -> bool:
    """Validate that the command is safe to execute.

    Args:
        command: The command to validate as a list of strings

    Returns:
        True if the command is valid, False otherwise
    """
    # Ensure command is a list of strings
    if not isinstance(command, list) or not all(isinstance(arg, str) for arg in command):
        return False

    # Check for shell metacharacters in any argument
    for arg in command:
        if any(char in arg for char in [';', '&', '|', '>', '<', '$', '`']):
            return False

    return True


if __name__ == "__main__":
    sys.exit(run_mcp_tests())
