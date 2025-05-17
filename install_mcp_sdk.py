#!/usr/bin/env python
"""
Wrapper script to install the MCP SDK.

This script is a wrapper around scripts/setup/install_mcp_sdk.py to maintain backward compatibility
with existing workflows that expect install_mcp_sdk.py to be in the root directory.
"""

import sys
from pathlib import Path


def verify_mock_installation() -> bool:
    """Verify that the mock MCP SDK is properly installed.

    Returns:
        True if the mock is properly installed, False otherwise
    """
    try:
        # Try to import the module
        import modelcontextprotocol as mcp

        # Verify that it has the expected attributes
        if not hasattr(mcp, 'Client'):
            logger.error("Mock MCP SDK is missing Client class")
            return False

        # Create a client and test basic functionality
        client = mcp.Client("http://localhost:9000")
        client.connect()
        response = client.send_message("Test message")
        client.disconnect()

        # Check that the response is as expected
        if not isinstance(response, str) or "Test message" not in response:
            logger.error(f"Mock MCP SDK returned unexpected response: {response}")
            return False

        logger.info("Mock MCP SDK is properly installed and working")
        return True
    except Exception as e:
        logger.exception(f"Error verifying mock MCP SDK: {e}")
        return False


def main() -> int:
    """
    Install the MCP SDK by calling the script in its new location.

    Returns:
        int: The return code from the installation (0 for success, non-zero for failure)

    """
    # Get the path to the actual script
    script_path = Path(__file__).parent / "scripts" / "setup" / "install_mcp_sdk.py"

    # Check if the script exists
    if not script_path.exists():
        import logging

        # Create a named logger instead of using the root logger
        logger = logging.getLogger("install_mcp_sdk")

        # Use string formatting instead of f-string
        logger.error("Script not found at %s", script_path)
        return 1

    # Execute the script with the same arguments
    # We use subprocess.run instead of os.execv for better security
    # This still ensures that the return code is properly propagated
    import subprocess

    # Validate script_path to ensure it's not from untrusted input
    # Convert to absolute path and ensure it's within the expected directory
    abs_script_path = script_path.resolve()
    expected_dir = (Path(__file__).parent / "scripts" / "setup").resolve()

    if not abs_script_path.startswith(expected_dir):
        import logging

        logger = logging.getLogger("install_mcp_sdk")
        logger.error("Invalid script path: not in expected directory")
        return 1

    # Use a list of arguments to avoid shell injection
    cmd = [sys.executable, str(script_path)] + sys.argv[1:]

    # We've validated script_path is within our expected directory
    # and we're using a list of arguments to avoid shell injection
    # ruff: noqa: S603
    result = subprocess.run(  # nosec B603
        cmd,
        check=False,
        shell=False,  # Explicitly set shell=False for security
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
