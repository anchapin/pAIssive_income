"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports

# Third-party imports

# Local imports
from .ollama_adapter import OllamaAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter
from .lmstudio_adapter import LMStudioAdapter
from .tensorrt_adapter import TensorRTAdapter

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
            raise ImportError("MCPAdapter not available. Ensure ai_models/adapters/mcp_adapter.py exists and mcp-use is installed.")
        return MCPAdapter(host, port, **kwargs)
    else:
        raise ValueError(f"Unsupported server type: {server_type}")
