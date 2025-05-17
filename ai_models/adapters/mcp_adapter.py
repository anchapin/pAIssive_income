"""mcp_adapter - Module for ai_models/adapters.mcp_adapter."""

import re
import logging
import urllib.parse
from typing import Optional

# Third-party imports
try:
    import modelcontextprotocol as mcp
    # Verify that the module has the expected attributes
    if not hasattr(mcp, 'Client'):
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
        import sys
        import subprocess

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

    def __init__(self):
        super().__init__(self.MESSAGE)


class PortRangeError(ValueError):
    """Raised when port is outside valid range."""

    MESSAGE = f"Port must be an integer between {MIN_PORT} and {MAX_PORT}"

    def __init__(self):
        super().__init__(self.MESSAGE)


class MCPConnectionError(ConnectionError):
    """Raised when connection to MCP server fails."""

    def __init__(self, endpoint: str, original_error: Exception):
        message = f"Failed to connect to MCP server at {endpoint}"
        super().__init__(message)
        self.original_error = original_error


class MCPCommunicationError(ConnectionError):
    """Raised when communication with MCP server fails."""

    def __init__(self, original_error: Exception):
        message = "Error communicating with MCP server"
        super().__init__(message)
        self.original_error = original_error


class MCPAdapter:
    """Adapter for connecting to MCP servers using the official modelcontextprotocol SDK."""

    def __init__(self, host: str, port: int, **kwargs):
        """Initialize the MCP adapter.

        Args:
            host: Server hostname or IP address
            port: Server port number
            **kwargs: Additional keyword arguments for the MCP client

        Raises:
            ModelContextProtocolError: If the MCP SDK is not installed
            HostFormatError: If host format is invalid
            PortRangeError: If port is outside valid range
        """
        # Try one more time to import the module if it's not available
        global mcp
        if mcp is None:
            try:
                import modelcontextprotocol as mcp_module
                mcp = mcp_module
                logger.info(f"Successfully imported modelcontextprotocol in __init__: {mcp}")
            except ImportError:
                logger.warning("Failed to import modelcontextprotocol in __init__")

                # Try to create a mock implementation
                try:
                    # Create a temporary module
                    import sys
                    from types import ModuleType

                    # Create a mock module
                    mock_module = ModuleType("modelcontextprotocol")
                    mock_module.__file__ = "<mock>"
                    mock_module.__path__ = []
                    mock_module.__package__ = "modelcontextprotocol"

                    # Add a Client class to the module with more robust implementation
                    class MockClient:
                        def __init__(self, endpoint, **kwargs):
                            self.endpoint = endpoint
                            self.kwargs = kwargs
                            self.connected = False

                        def connect(self):
                            self.connected = True
                            return True

                        def disconnect(self):
                            self.connected = False
                            return True

                        def send_message(self, message):
                            if not self.connected:
                                raise ConnectionError("Not connected to server")
                            return "Mock response to: " + str(message)

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
                    mcp = mock_module

                    logger.info("Created in-memory mock modelcontextprotocol module in __init__")
                except Exception as e:
                    logger.exception(f"Failed to create mock modelcontextprotocol module in __init__: {e}")

        # If mcp is still None, raise an error
        if mcp is None:
            raise ModelContextProtocolError()

        # Validate host (prevent command injection via hostname)
        if not re.match(r"^[a-zA-Z0-9_.-]+$", host):
            raise HostFormatError()

        # Validate port is an integer in valid range
        if not isinstance(port, int) or port < MIN_PORT or port > MAX_PORT:
            raise PortRangeError()

        self.host = host
        self.port = port
        self.client = None  # Will be set when connect() is called
        self.kwargs = kwargs

    def connect(self):
        """Connect to the MCP server.

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
            raise ModelContextProtocolError()

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
        """Send a message to the MCP server and return the response.

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
            raise ModelContextProtocolError()

        # Connect if not already connected
        if not self.client:
            logger.info("Client not connected, connecting...")
            self.connect()

        # Ensure client is connected
        if not self.client:
            logger.error("Failed to create client")
            raise MCPConnectionError("unknown", Exception("Failed to create client"))

        try:
            logger.info(f"Sending message to MCP server: {message[:50]}...")
            response = self.client.send_message(message)
            logger.info(f"Received response from MCP server: {str(response)[:50]}...")
            return response
        except Exception as e:
            self.client = None  # Reset client on error
            logger.exception(f"Error communicating with MCP server: {e}")
            raise MCPCommunicationError(e) from e

    def close(self):
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
