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
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _setup_environment() -> dict:
    """Set up the environment for running MCP tests.

    Returns:
        dict: The environment variables for the test run
    """
    # Set environment variables to avoid loading the main conftest.py
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")

    # Add additional environment variables for Windows
    if platform.system() == "Windows":
        # Add a flag to indicate we're running in CI
        env["MCP_TESTS_CI"] = "1"
        # Log the environment for debugging
        logger.info(f"PYTHONPATH: {env['PYTHONPATH']}")

    return env


def _prepare_test_command() -> List[str]:
    """Prepare the test command for running MCP tests.

    Returns:
        List[str]: The test command as a list of strings
    """
    # Define the test command with fixed arguments
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
        # Use the custom pytest.ini file we created
        "-c",
        "tests/ai_models/adapters/pytest.ini",
    ]

    # Use absolute path for the executable when possible
    if shutil.which(sys.executable):
        cmd[0] = shutil.which(sys.executable)

    return cmd


def _ensure_mcp_module() -> None:
    """Ensure the modelcontextprotocol module is importable."""
    try:
        import importlib.util
        if importlib.util.find_spec("modelcontextprotocol") is None:
            logger.warning("modelcontextprotocol module not found, creating mock implementation")
            create_mock_mcp_module()
        else:
            logger.info("modelcontextprotocol module found")
    except ImportError as e:
        logger.warning(f"Error checking for modelcontextprotocol module: {e}")
        create_mock_mcp_module()

    # Double-check that the module is now importable
    try:
        import modelcontextprotocol
        logger.info(f"Successfully imported modelcontextprotocol: {modelcontextprotocol}")
    except ImportError as e:
        logger.warning(f"Still unable to import modelcontextprotocol after ensuring module: {e}")
        # Try one more time to create the mock module
        create_mock_mcp_module()


def run_mcp_tests() -> int:
    """Run MCP adapter tests without loading the main conftest.py.

    Returns:
        int: The return code from the test run (0 for success, non-zero for failure)
    """
    logger.info("Running MCP adapter tests...")
    logger.info(f"Platform: {platform.system()}")
    logger.info(f"Python version: {sys.version}")

    # Set up the environment
    env = _setup_environment()

    # Prepare the test command
    cmd = _prepare_test_command()

    # Validate the command to ensure it's safe to execute
    if not _validate_command(cmd):
        logger.error("Invalid command detected")
        return 1

    try:
        # Log the command for debugging
        logger.info(f"Running command: {' '.join(cmd)}")

        # Ensure the modelcontextprotocol module is importable
        _ensure_mcp_module()

        # Run the tests
        result = subprocess.run(
            cmd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            shell=False,
        )

        # Log the output
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)

        # If tests failed, try to diagnose the issue
        if result.returncode != 0:
            logger.warning("Tests failed, attempting to diagnose the issue...")
            diagnose_mcp_import_issues()
    except Exception:
        # Log the exception
        logger.exception("Error running tests")
        return 1
    else:
        # This will only execute if no exception is raised
        return 0 if result.returncode == 0 else 1


def create_mock_mcp_module() -> None:
    """Create a mock modelcontextprotocol module for testing."""
    try:
        # Create a temporary module
        import sys
        from types import ModuleType

        # Create a mock module
        mock_module = ModuleType("modelcontextprotocol")
        mock_module.__file__ = "<mock>"
        mock_module.__path__ = []
        mock_module.__package__ = "modelcontextprotocol"

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

        # Add version information
        mock_module.__version__ = "0.1.0"

        # Add error classes that might be expected
        class MCPError(Exception):
            """Base class for MCP errors."""
            pass

        class ConnectionError(MCPError):
            """Error raised when connection fails."""
            pass

        class MessageError(MCPError):
            """Error raised when message sending fails."""
            pass

        # Add error classes to the module
        mock_module.MCPError = MCPError
        mock_module.ConnectionError = ConnectionError
        mock_module.MessageError = MessageError

        # Add the module to sys.modules
        sys.modules["modelcontextprotocol"] = mock_module

        logger.info("Created mock modelcontextprotocol module")

        # Verify the module is importable
        import modelcontextprotocol
        logger.info(f"Verified mock module is importable: {modelcontextprotocol}")
    except Exception as e:
        logger.exception(f"Failed to create mock modelcontextprotocol module: {e}")


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
    except Exception:
        logger.exception("Error during diagnosis")


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
