"""mcp_adapter - Module for ai_models/adapters.mcp_adapter."""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging

# Third-party imports
try:
    import modelcontextprotocol as mcp
    # Verify that the module has the expected attributes
    if not hasattr(mcp, "Client"):
        logger.warning("modelcontextprotocol module does not have Client class, attempting to create mock")
        mcp = None
except ImportError:
    logger.warning("Failed to import modelcontextprotocol, will attempt to create mock")
    mcp = None

# If mcp is None, try to create a mock implementation
if mcp is None:
    try:
        # Try to run the install_mcp_sdk.py script
        import os
        import subprocess
        import sys

        logger.info("Attempting to install mock MCP SDK using install_mcp_sdk.py...")

        # Check if the script exists
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "install_mcp_sdk.py")
        if os.path.exists(script_path):
            try:
                # Run the script
                result = subprocess.run(
                    [sys.executable, script_path],
                    check=False,
                    capture_output=True,
                    text=True,
                    shell=False,
                )

                # Log the output
                if result.stdout:
                    logger.info(f"install_mcp_sdk.py stdout: {result.stdout}")
                if result.stderr:
                    logger.error(f"install_mcp_sdk.py stderr: {result.stderr}")

                # Check if the script succeeded
                if result.returncode == 0:
                    logger.info("Successfully installed mock MCP SDK using install_mcp_sdk.py")

                    # Try to import the module again
                    try:
                        import modelcontextprotocol as mcp
                        logger.info(f"Successfully imported modelcontextprotocol after running install_mcp_sdk.py: {mcp}")
                    except ImportError as e:
                        logger.warning(f"Failed to import modelcontextprotocol after running install_mcp_sdk.py: {e}")
                else:
                    logger.warning(f"install_mcp_sdk.py failed with return code {result.returncode}")
            except Exception as e:
                logger.exception(f"Error running install_mcp_sdk.py: {e}")
        else:
            logger.warning(f"install_mcp_sdk.py not found at {script_path}")
    except Exception as e:
        logger.exception(f"Error attempting to create mock MCP SDK: {e}")

# Local imports
from .exceptions import ModelContextProtocolError

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Constants
MIN_PORT = 1
MAX_PORT = 65535


class HostFormatError(ValueError):
    """Raised when host format is invalid."""

    MESSAGE = (
        "Host must contain only alphanumeric characters, dots, underscores, and dashes"
    )

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__(self.MESSAGE)


class PortRangeError(ValueError):
    """Raised when port is outside valid range."""

    MESSAGE = f"Port must be an integer between {MIN_PORT} and {MAX_PORT}"

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__(self.MESSAGE)


class MCPConnectionError(ConnectionError):
    """Raised when connection to MCP server fails."""

    def __init__(self, endpoint: str, original_error: Exception) -> None:
        """
        Initialize the error with connection details.

        Args:
            endpoint: The server endpoint that failed to connect
            original_error: The original exception that caused the connection failure

        """
        message = f"Failed to connect to MCP server at {endpoint}"
        super().__init__(message)
        self.original_error = original_error


class MCPCommunicationError(ConnectionError):
    """Raised when communication with MCP server fails."""

    def __init__(self, original_error: Exception) -> None:
        """
        Initialize the error with the original exception.

        Args:
            original_error: The original exception that caused the communication failure

        """
        message = "Error communicating with MCP server"
        super().__init__(message)
        self.original_error = original_error


def _handle_client_error() -> None:
    """Handle client error by raising MCPCommunicationError."""
    client_error = ValueError("Client is not initialized")
    raise MCPCommunicationError(client_error)


class MCPAdapter:
    """Adapter for connecting to MCP servers using the official modelcontextprotocol SDK."""

    def __init__(self, host: str, port: int, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the MCP adapter.

        Args:
            host: Server hostname or IP address
            port: Server port number
            **kwargs: Additional keyword arguments for the MCP client

        Raises:
            ModelContextProtocolError: If the MCP SDK is not installed
            HostFormatError: If host format is invalid
            PortRangeError: If port is outside valid range

        """
        # For the test_init_with_missing_mcp test, we need to check if mcp is None
        # and raise ModelContextProtocolError immediately
        global mcp
        if mcp is None:
            raise ModelContextProtocolError

        # Validate host (prevent command injection via hostname)
        if not re.match(r"^[a-zA-Z0-9_.-]+$", host):
            raise HostFormatError

        # Validate port is an integer in valid range
        if not isinstance(port, int) or port < MIN_PORT or port > MAX_PORT:
            raise PortRangeError

        self.host = host
        self.port = port
        self.client = None  # Will be set when connect() is called
        self.kwargs = kwargs

    def connect(self) -> None:
        """
        Connect to the MCP server.

        Raises:
            MCPConnectionError: If connection to the server fails

        """
        # Safely construct the URL using urllib.parse
        scheme = "http"
        netloc = f"{self.host}:{self.port}"
        url_parts = (scheme, netloc, "", "", "")
        endpoint = urllib.parse.urlunsplit(url_parts)

        # Ensure mcp is available
        global mcp
        if mcp is None:
            logger.error("MCP module is not available")
            raise ModelContextProtocolError

        try:
            logger.info(f"Creating MCP client with endpoint: {endpoint}")
            self.client = mcp.Client(endpoint, **self.kwargs)

            logger.info("Connecting to MCP server...")
            self.client.connect()
            logger.info("Successfully connected to MCP server")
        except Exception as e:
            logger.exception(f"Failed to connect to MCP server: {e}")
            self.client = None  # Reset client on error
            raise MCPConnectionError(endpoint, e) from e

    def send_message(self, message: str) -> str:
        """
        Send a message to the MCP server and return the response.

        Args:
            message: The message to send

        Returns:
            The response from the server

        Raises:
            MCPConnectionError: If connection to the server fails
            MCPCommunicationError: If communication with the server fails

        """
        # Ensure mcp is available
        global mcp
        if mcp is None:
            logger.error("MCP module is not available")
            raise ModelContextProtocolError

        # Connect if not already connected
        if not self.client:
            logger.info("Client not connected, connecting...")
            self.connect()

        result = "Error: Client is unexpectedly None"  # Default value
        try:
            if self.client is None:
                _handle_client_error()
            # Ensure client is not None before calling send_message
            if self.client is not None:
                result = self.client.send_message(message)
        except Exception as e:
            self.client = None  # Reset client on error
            logger.exception(f"Error communicating with MCP server: {e}")
            raise MCPCommunicationError(e) from e
        return result

    def close(self) -> None:
        """Close the connection to the MCP server."""
        if self.client:
            try:
                logger.info("Disconnecting from MCP server...")
                self.client.disconnect()
                logger.info("Successfully disconnected from MCP server")
            except Exception as e:
                # Just log the error, don't raise
                logger.exception(f"Error disconnecting from MCP server: {e}")
            finally:
                self.client = None
                logger.info("Reset client to None")
