"""mcp_adapter - Module for ai_models/adapters.mcp_adapter."""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any, Optional

# Third-party imports
try:
    import modelcontextprotocol as mcp
except ImportError:
    mcp = None

# Local imports
from .exceptions import ModelContextProtocolError

# Constants
MIN_PORT = 1
MAX_PORT = 65535

# Configure logging
logger = logging.getLogger(__name__)


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
        self.client: Optional[mcp.Client] = None
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

        try:
            self.client = mcp.Client(endpoint, **self.kwargs)
            self.client.connect()
        except Exception as e:
            logger.exception("Failed to connect to MCP server")
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
        if not self.client:
            self.connect()

        # Define a function outside the try block to handle client errors
        def _handle_client_error() -> None:
            # Create an exception to pass to MCPCommunicationError
            client_error = ValueError("Client is not initialized")
            raise MCPCommunicationError(client_error)

        result = "Error: Client is unexpectedly None"  # Default value
        try:
            if self.client is None:
                _handle_client_error()
            # Ensure client is not None before calling send_message
            if self.client is not None:
                result = self.client.send_message(message)
        except Exception as e:
            self.client = None  # Reset client on error
            logger.exception("Error communicating with MCP server")
            raise MCPCommunicationError(e) from e
        return result

    def close(self) -> None:
        """Close the connection to the MCP server."""
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                # Just log the error, don't raise
                logger.exception("Error disconnecting from MCP server")
            finally:
                self.client = None
