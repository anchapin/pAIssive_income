"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports
from __future__ import annotations

import logging
from typing import Any, cast

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging

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

# logger is now initialized globally, no need to redefine here

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

    # If we get here, the server type is not supported
    raise UnsupportedServerTypeError(server_type)


class AdapterFactory:
    """Factory class for creating model adapters."""

    # Registry of adapter types
    _adapter_registry = {}

    @classmethod
    def _initialize_registry(cls):
        """Initialize the adapter registry with available adapters."""
        registry = {
            "ollama": OllamaAdapter,
            "openai": OpenAICompatibleAdapter,
            "lmstudio": LMStudioAdapter,
            "tensorrt": TensorRTAdapter,
        }

        # Add MCP adapter if available
        if MCPAdapter is not None:
            registry["mcp"] = MCPAdapter

        cls._adapter_registry = registry
        return registry

    @classmethod
    def get_available_adapter_types(cls):
        """Get a list of available adapter types.

        Returns:
            List of available adapter type names
        """
        if not cls._adapter_registry:
            cls._initialize_registry()

        logger.info("Getting available adapter types")
        adapter_types = list(cls._adapter_registry.keys())
        logger.info(f"Found {len(adapter_types)} available adapter types")
        return adapter_types

    @classmethod
    def register_adapter(cls, name: str, adapter_class):
        """Register a new adapter type.

        Args:
            name: The name of the adapter type
            adapter_class: The adapter class to register
        """
        # Initialize registry if not already done
        if not cls._adapter_registry:
            cls._initialize_registry()

        cls._adapter_registry[name] = adapter_class
        logger.info(f"Registered adapter type: {name}")

    @classmethod
    def create_adapter(cls, adapter_type: str, host: str, port: int, **kwargs):
        """Create an adapter of the specified type.

        Args:
            adapter_type: The type of adapter to create
            host: Server hostname or IP address
            port: Server port number
            **kwargs: Additional parameters to pass to the adapter constructor

        Returns:
            An instance of the specified adapter type

        Raises:
            UnsupportedServerTypeError: If the adapter type is not supported
            MCPAdapterNotAvailableError: If MCP adapter is requested but not available
        """
        # Initialize registry if not already done
        if not cls._adapter_registry:
            cls._initialize_registry()

        # Convert adapter_type to lowercase for case-insensitive matching
        adapter_type = adapter_type.lower()

        # Check if adapter type is supported
        if adapter_type not in cls._adapter_registry:
            logger.error(f"Unsupported adapter type requested: {adapter_type}")
            raise UnsupportedServerTypeError(adapter_type)

        # Special case for MCP adapter
        if adapter_type == "mcp" and MCPAdapter is None:
            logger.error("MCP adapter requested but not available.")
            raise MCPAdapterNotAvailableError()

        # Create and return the adapter
        adapter_class = cls._adapter_registry[adapter_type]
        try:
            adapter = adapter_class(host=host, port=port, **kwargs)
            logger.info(f"Successfully created adapter of type: {adapter_type}")
            return adapter
        except Exception as e:
            logger.exception(f"Error creating adapter of type {adapter_type} for {host}:{port}")
            # Optionally, re-raise a more specific error or return None/default
            raise AdapterError(f"Failed to create adapter {adapter_type}: {e}") from e
