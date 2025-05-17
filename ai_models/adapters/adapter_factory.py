"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports
from __future__ import annotations

import logging
from typing import Any, cast

# Third-party imports


# Local imports
# Import placeholders for adapters
# These will be properly implemented in their respective files
class OllamaAdapter:
    """Adapter for Ollama servers."""

    def __init__(self, host: str, port: int, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the OllamaAdapter.

        Args:
            host: Server hostname or IP address
            port: Server port number
            kwargs: Additional keyword arguments for the adapter

        """
        self.host = host
        self.port = port
        self.kwargs = kwargs


class OpenAICompatibleAdapter:
    """Adapter for OpenAI compatible servers."""

    def __init__(self, host: str, port: int, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the OpenAICompatibleAdapter.

        Args:
            host: Server hostname or IP address
            port: Server port number
            kwargs: Additional keyword arguments for the adapter

        """
        self.host = host
        self.port = port
        self.kwargs = kwargs


class LMStudioAdapter:
    """Adapter for LMStudio servers."""

    def __init__(self, host: str, port: int, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the LMStudioAdapter.

        Args:
            host: Server hostname or IP address
            port: Server port number
            kwargs: Additional keyword arguments for the adapter

        """
        self.host = host
        self.port = port
        self.kwargs = kwargs


class TensorRTAdapter:
    """Adapter for TensorRT servers."""

    def __init__(self, host: str, port: int, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the TensorRTAdapter.

        Args:
            host: Server hostname or IP address
            port: Server port number
            kwargs: Additional keyword arguments for the adapter

        """
        self.host = host
        self.port = port
        self.kwargs = kwargs


# Configure logging
logger = logging.getLogger(__name__)


class AdapterError(Exception):
    """Base class for adapter-related errors."""


class MCPAdapterNotAvailableError(AdapterError):
    """Raised when MCP adapter is not available."""

    MESSAGE = "MCPAdapter missing. Install mcp-use and ensure the file exists."

    def __init__(self) -> None:
        """Initialize the MCPAdapterNotAvailableError with a standard message."""
        super().__init__(self.MESSAGE)


class UnsupportedServerTypeError(AdapterError):
    """Raised when an unsupported server type is provided."""

    MESSAGE_TEMPLATE = "Unsupported server type: {server_type}"

    def __init__(self, server_type: str) -> None:
        """
        Initialize the UnsupportedServerTypeError.

        Args:
            server_type: The unsupported server type

        """
        message = self.MESSAGE_TEMPLATE.format(server_type=server_type)
        super().__init__(message)


# Import MCP adapter if available
try:
    from .mcp_adapter import MCPAdapter
except ImportError:
    # Define a placeholder for MCPAdapter when not available
    MCPAdapter = cast("Any", None)


def get_adapter(
    server_type: str, host: str, port: int, **kwargs: dict[str, Any]
) -> object:
    """
    Get the adapter for a specified server type.

    # Registry of adapter types
    _adapter_registry = {}

    @classmethod
    def _initialize_registry(cls):
        """Initialize the adapter registry with available adapters."""
        registry = {}

    Raises:
        MCPAdapterNotAvailableError: If MCP adapter is requested but not available
        UnsupportedServerTypeError: If server type is not supported

    """
    server_type = server_type.lower()

    if server_type == "ollama":
        return OllamaAdapter(host, port, **kwargs)
    if server_type == "openai":
        return OpenAICompatibleAdapter(host, port, **kwargs)
    if server_type == "lmstudio":
        return LMStudioAdapter(host, port, **kwargs)
    if server_type == "tensorrt":
        return TensorRTAdapter(host, port, **kwargs)
    if server_type == "mcp":
        if MCPAdapter is None:
            raise MCPAdapterNotAvailableError

        # Initialize the MCP adapter with provided configuration
        return MCPAdapter(host, port, **kwargs)
    raise UnsupportedServerTypeError(server_type)
