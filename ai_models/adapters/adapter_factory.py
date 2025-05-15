"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports
import logging

# Third-party imports

# Local imports
# Import placeholders for adapters
# These will be properly implemented in their respective files
class OllamaAdapter:
    """Adapter for Ollama servers."""
    def __init__(self, host: str, port: int, **kwargs):
        self.host = host
        self.port = port
        self.kwargs = kwargs

class OpenAICompatibleAdapter:
    """Adapter for OpenAI compatible servers."""
    def __init__(self, host: str, port: int, **kwargs):
        self.host = host
        self.port = port
        self.kwargs = kwargs

class LMStudioAdapter:
    """Adapter for LMStudio servers."""
    def __init__(self, host: str, port: int, **kwargs):
        self.host = host
        self.port = port
        self.kwargs = kwargs

class TensorRTAdapter:
    """Adapter for TensorRT servers."""
    def __init__(self, host: str, port: int, **kwargs):
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

    def __init__(self):
        super().__init__(self.MESSAGE)


class UnsupportedServerTypeError(AdapterError):
    """Raised when an unsupported server type is provided."""

    MESSAGE_TEMPLATE = "Unsupported server type: {server_type}"

    def __init__(self, server_type: str):
        message = self.MESSAGE_TEMPLATE.format(server_type=server_type)
        super().__init__(message)


try:
    from .mcp_adapter import MCPAdapter
except ImportError:
    MCPAdapter = None


def get_adapter(server_type: str, host: str, port: int, **kwargs):
    """
    Factory method to obtain the adapter for a specified server type.

    Args:
        server_type: Type of server to connect to ('ollama', 'openai', etc.)
        host: Server hostname or IP address
        port: Server port number
        **kwargs: Additional keyword arguments for the adapter

    Returns:
        An instance of the appropriate adapter class

    Raises:
        MCPAdapterNotAvailableError: If MCP adapter is requested but not available
        UnsupportedServerTypeError: If server type is not supported
    """
    server_type = server_type.lower()

    if server_type == "ollama":
        return OllamaAdapter(host, port, **kwargs)
    elif server_type == "openai":
        return OpenAICompatibleAdapter(host, port, **kwargs)
    elif server_type == "lmstudio":
        return LMStudioAdapter(host, port, **kwargs)
    elif server_type == "tensorrt":
        return TensorRTAdapter(host, port, **kwargs)
    elif server_type == "mcp":
        if MCPAdapter is None:
            raise MCPAdapterNotAvailableError()

        # Initialize the MCP adapter with provided configuration
        adapter = MCPAdapter(host, port, **kwargs)
        return adapter
    else:
        raise UnsupportedServerTypeError(server_type)
