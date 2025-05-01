"""
Adapters for different AI model frameworks.

This package provides adapters for connecting to various AI model frameworks,
including Ollama, LM Studio, OpenAI-compatible APIs, and GPU acceleration libraries.
"""

from .base_adapter import BaseModelAdapter
from .lmstudio_adapter import LMStudioAdapter
from .ollama_adapter import OllamaAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter

# Import TensorRT adapter if available
try:
    from .tensorrt_adapter import TensorRTAdapter

    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False
    TensorRTAdapter = None

# Import factory after other adapters to avoid circular imports
from .adapter_factory import AdapterFactory, adapter_factory, get_adapter_factory

# Register adapters with the factory
adapter_factory.register_adapter("ollama", OllamaAdapter)
adapter_factory.register_adapter("lmstudio", LMStudioAdapter)
adapter_factory.register_adapter("openai", OpenAICompatibleAdapter)

# Register TensorRT adapter if available
if TENSORRT_AVAILABLE:
    adapter_factory.register_adapter("tensorrt", TensorRTAdapter)

__all__ = [
    "BaseModelAdapter",
    "OllamaAdapter",
    "LMStudioAdapter",
    "OpenAICompatibleAdapter",
    "AdapterFactory",
    "adapter_factory",
    "get_adapter_factory",
]

# Add TensorRT adapter if available
if TENSORRT_AVAILABLE:
    __all__.append("TensorRTAdapter")
