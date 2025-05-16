#!/usr/bin/env python
"""
Script to run MCP adapter tests without loading the main conftest.py.

This script is used by the CI/CD pipeline to run the MCP adapter tests.
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _setup_environment() -> dict[str, str]:
    """
    Set up the environment for running MCP tests.

    Returns:
        dict[str, str]: Environment variables dictionary

    """
    # Set environment variables to avoid loading the main conftest.py
    env = os.environ.copy()
    # Convert environment to dict[str, str] for type safety
    env_str: dict[str, str] = {k: str(v) for k, v in env.items()}
    env_str["PYTHONPATH"] = str(Path.cwd().resolve())

    # Add additional environment variables for Windows
    if platform.system() == "Windows":
        # Ensure we have a clean PYTHONPATH that doesn't include any conflicting paths
        env_str["PYTHONPATH"] = str(Path.cwd().resolve())
        # Add a flag to indicate we're running in CI
        env_str["MCP_TESTS_CI"] = "1"
        # Log the environment for debugging
        logger.info("PYTHONPATH: %s", env_str["PYTHONPATH"])

    return env_str


def _prepare_test_command() -> list[str]:
    """
    Prepare the pytest command for running MCP tests.

    Returns:
        list[str]: Command to run as a list of strings

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
        "--confcutdir=tests/ai_models/adapters",
        "--noconftest",
        "--no-cov",  # Disable coverage to avoid issues with the coverage report
    ]

    # Use absolute path for the executable when possible
    if shutil.which(sys.executable):
        cmd[0] = shutil.which(sys.executable)

    return cmd


def _ensure_mcp_module_exists() -> None:
    """Ensure the modelcontextprotocol module is available."""
    try:
        import importlib.util

        if importlib.util.find_spec("modelcontextprotocol") is None:
            logger.warning(
                "modelcontextprotocol module not found, creating mock implementation"
            )
            create_mock_mcp_module()
    except ImportError as e:
        logger.warning("Error checking for modelcontextprotocol module: %s", e)
        create_mock_mcp_module()


def run_mcp_tests() -> int:
    """
    Run MCP adapter tests without loading the main conftest.py.

    Returns:
        int: The return code from the test run (0 for success, non-zero for failure)

    """
    logger.info("Running MCP adapter tests...")
    logger.info("Platform: %s", platform.system())
    logger.info("Python version: %s", sys.version)

    # Set up environment
    env = _setup_environment()

    # Prepare test command
    cmd = _prepare_test_command()

    # Validate the command to ensure it's safe to execute
    if not _validate_command(cmd):
        logger.error("Invalid command detected")
        return 1

    try:
        # Log the command for debugging
        logger.info("Running command: %s", " ".join(cmd))

        # Ensure the modelcontextprotocol module is importable
        _ensure_mcp_module_exists()

        # nosec comment below tells Bandit to ignore this line since we've added proper validation
        # We've validated the command above with _validate_command to ensure it's safe to execute
        # ruff: noqa: S603
        result = subprocess.run(  # nosec B603 S603
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
        # Include basic exception info for better diagnostics
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

        # Add a Client class to the module
        class MockClient:
            def __init__(self, endpoint: str, **kwargs: dict) -> None:
                self.endpoint = endpoint
                self.kwargs = kwargs

            def connect(self) -> None:
                pass

            def disconnect(self) -> None:
                pass

            def send_message(self, message: str) -> str:
                return f"Mock response to: {message}"

        # Add the Client class to the module
        # mypy: disable-error-code=attr-defined
        mock_module.Client = MockClient  # type: ignore[attr-defined]

        # Add the module to sys.modules
        sys.modules["modelcontextprotocol"] = mock_module

        logger.info("Created mock modelcontextprotocol module")
    except Exception:
        logger.exception("Failed to create mock modelcontextprotocol module")


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

            logger.info(
                "Successfully imported modelcontextprotocol: %s", modelcontextprotocol
            )
        except ImportError as e:
            logger.info("Failed to import modelcontextprotocol: %s", e)

        # Check Python path
        logger.info("sys.path: %s", sys.path)

        # Check for the adapter file
        adapter_path = (
            Path.cwd().resolve() / "ai_models" / "adapters" / "mcp_adapter.py"
        )
        if adapter_path.exists():
            logger.info("MCP adapter file exists at %s", adapter_path)
        else:
            logger.info("MCP adapter file does NOT exist at %s", adapter_path)
    except Exception:
        logger.exception("Error during diagnosis")


def _validate_command(command: list[str]) -> bool:
    """
    Validate that the command is safe to execute.

    Args:
        command: The command to validate as a list of strings

    Returns:
        True if the command is valid, False otherwise

    """
    # Ensure command is a list of strings
    if not isinstance(command, list) or not all(
        isinstance(arg, str) for arg in command
    ):
        return False

    # Check for shell metacharacters in any argument
    for arg in command:
        if any(char in arg for char in [";", "&", "|", ">", "<", "$", "`"]):
            return False

    return True


if __name__ == "__main__":
    sys.exit(run_mcp_tests())
