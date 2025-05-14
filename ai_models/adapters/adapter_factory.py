"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports

# Third-party imports

# Local imports
from .ollama_adapter import OllamaAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter
from .lmstudio_adapter import LMStudioAdapter
from .tensorrt_adapter import TensorRTAdapter

class AdapterError(Exception):
    """Base class for adapter-related errors."""

class MCPAdapterNotAvailableError(AdapterError):
    """Raised when MCP adapter is not available."""

class UnsupportedServerTypeError(AdapterError):
    """Raised when an unsupported server type is provided."""

try:
    from .mcp_adapter import MCPAdapter
except ImportError:
    MCPAdapter = None

def get_adapter(server_type: str, host: str, port: int, **kwargs):
    """
    Factory method to obtain the adapter for a specified server type.
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
            raise MCPAdapterNotAvailableError("MCPAdapter missing. Install mcp-use and ensure the file exists.")
        return MCPAdapter(host, port, **kwargs)
    else:
        raise UnsupportedServerTypeError(f"Unsupported server type: {server_type}")
