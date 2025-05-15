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
import platform
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_mcp_tests() -> int:
    """Run MCP adapter tests without loading the main conftest.py.

    Returns:
        int: The return code from the test run (0 for success, non-zero for failure)
    """
    logger.info("Running MCP adapter tests...")
    logger.info(f"Platform: {platform.system()}")
    logger.info(f"Python version: {sys.version}")

    # Set environment variables to avoid loading the main conftest.py
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")

    # Add additional environment variables for Windows
    if platform.system() == "Windows":
        # Ensure we have a clean PYTHONPATH that doesn't include any conflicting paths
        env["PYTHONPATH"] = os.path.abspath(".")
        # Add a flag to indicate we're running in CI
        env["MCP_TESTS_CI"] = "1"
        # Log the environment for debugging
        logger.info(f"PYTHONPATH: {env['PYTHONPATH']}")

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

        # Log the command for debugging
        logger.info(f"Running command: {' '.join(cmd)}")

        # First, ensure the modelcontextprotocol module is importable
        try:
            import importlib.util
            if importlib.util.find_spec("modelcontextprotocol") is None:
                logger.warning("modelcontextprotocol module not found, creating mock implementation")
                create_mock_mcp_module()
        except ImportError as e:
            logger.warning(f"Error checking for modelcontextprotocol module: {e}")
            create_mock_mcp_module()

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

        # If tests failed, try to diagnose the issue
        if result.returncode != 0:
            logger.warning("Tests failed, attempting to diagnose the issue...")
            diagnose_mcp_import_issues()
    except Exception as e:
        # Include basic exception info for better diagnostics
        logger.exception(f"Error running tests: {type(e).__name__}: {e}")
        return 1
    else:
        # This will only execute if no exception is raised
        # Ensure we return an int, not Any
        return 0 if result.returncode == 0 else 1


def create_mock_mcp_module() -> None:
    """Create a mock modelcontextprotocol module for testing."""
    try:
        # Create a temporary module
        import sys
        from types import ModuleType

        # Create a mock module
        mock_module = ModuleType("modelcontextprotocol")

        # Add a Client class to the module
        class MockClient:
            def __init__(self, endpoint, **kwargs):
                self.endpoint = endpoint
                self.kwargs = kwargs

            def connect(self):
                pass

            def disconnect(self):
                pass

            def send_message(self, message):
                return f"Mock response to: {message}"

        # Add the Client class to the module
        mock_module.Client = MockClient

        # Add the module to sys.modules
        sys.modules["modelcontextprotocol"] = mock_module

        logger.info("Created mock modelcontextprotocol module")
    except Exception as e:
        logger.error(f"Failed to create mock modelcontextprotocol module: {e}")


def diagnose_mcp_import_issues() -> None:
    """Diagnose issues with importing the modelcontextprotocol module."""
    try:
        logger.info("Diagnosing MCP import issues...")

        # Check if the module is in sys.modules
        import sys
        if "modelcontextprotocol" in sys.modules:
            logger.info("modelcontextprotocol is in sys.modules")
        else:
            logger.info("modelcontextprotocol is NOT in sys.modules")

        # Check if the module can be imported
        try:
            import modelcontextprotocol
            logger.info(f"Successfully imported modelcontextprotocol: {modelcontextprotocol}")
        except ImportError as e:
            logger.info(f"Failed to import modelcontextprotocol: {e}")

        # Check Python path
        logger.info(f"sys.path: {sys.path}")

        # Check for the adapter file
        adapter_path = os.path.join(os.path.abspath("."), "ai_models", "adapters", "mcp_adapter.py")
        if os.path.exists(adapter_path):
            logger.info(f"MCP adapter file exists at {adapter_path}")
        else:
            logger.info(f"MCP adapter file does NOT exist at {adapter_path}")
    except Exception as e:
        logger.error(f"Error during diagnosis: {e}")


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
