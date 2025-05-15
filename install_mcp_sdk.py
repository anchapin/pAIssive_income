#!/usr/bin/env python
"""
Script to install the MCP SDK from GitHub.
This script is used by the CI/CD pipeline to install the MCP SDK.
"""

import logging
import subprocess
import sys
import tempfile
import shutil
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_command(command: str, cwd: Optional[str] = None) -> Optional[str]:
    """Run a shell command and return the output.

    Args:
        command: The command to run
        cwd: The working directory to run the command in

    Returns:
        The command output or None if the command failed
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error running command: {command}\nError: {e.stderr}")
        return None
    else:
        output: str = result.stdout.strip()
        return output


def install_mcp_sdk() -> bool:
    """Install the MCP SDK from GitHub.

    Returns:
        True if installation was successful, False otherwise
    """
    logger.info("Installing MCP SDK from GitHub...")

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Clone the repository
        logger.info(f"Cloning MCP SDK repository to {temp_dir}...")
        result = run_command(
            "git clone --depth 1 https://github.com/modelcontextprotocol/python-sdk.git .",
            cwd=temp_dir,
        )

        if result is None:
            logger.error("Failed to clone MCP SDK repository")
            return False

        # Install the package
        logger.info("Installing MCP SDK...")
        result = run_command(
            f"{sys.executable} -m pip install -e .",
            cwd=temp_dir,
        )

        if result is None:
            logger.error("Failed to install MCP SDK")
            return False

        logger.info("MCP SDK installed successfully")
        return True
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    success = install_mcp_sdk()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
