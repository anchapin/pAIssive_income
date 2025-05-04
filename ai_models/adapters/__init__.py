"""
"""
Adapters for different AI model frameworks.
Adapters for different AI model frameworks.


This package provides adapters for connecting to various AI model frameworks,
This package provides adapters for connecting to various AI model frameworks,
including Ollama, LM Studio, OpenAI-compatible APIs, and GPU acceleration libraries.
including Ollama, LM Studio, OpenAI-compatible APIs, and GPU acceleration libraries.
"""
"""


from .adapter_factory import (AdapterFactory, adapter_factory,
from .adapter_factory import (AdapterFactory, adapter_factory,
get_adapter_factory)
get_adapter_factory)
from .base_adapter import BaseModelAdapter
from .base_adapter import BaseModelAdapter
from .lmstudio_adapter import LMStudioAdapter
from .lmstudio_adapter import LMStudioAdapter
from .ollama_adapter import OllamaAdapter
from .ollama_adapter import OllamaAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter


# Import TensorRT adapter if available
# Import TensorRT adapter if available
try:
    try:
    from .tensorrt_adapter import TensorRTAdapter
    from .tensorrt_adapter import TensorRTAdapter


    TENSORRT_AVAILABLE = True
    TENSORRT_AVAILABLE = True
except ImportError:
except ImportError:
    TENSORRT_AVAILABLE = False
    TENSORRT_AVAILABLE = False


    # Register adapters with the factory
    # Register adapters with the factory
    adapter_factory.register_adapter("ollama", OllamaAdapter)
    adapter_factory.register_adapter("ollama", OllamaAdapter)
    adapter_factory.register_adapter("lmstudio", LMStudioAdapter)
    adapter_factory.register_adapter("lmstudio", LMStudioAdapter)
    adapter_factory.register_adapter("openai", OpenAICompatibleAdapter)
    adapter_factory.register_adapter("openai", OpenAICompatibleAdapter)


    # Register TensorRT adapter if available
    # Register TensorRT adapter if available
    if TENSORRT_AVAILABLE:
    if TENSORRT_AVAILABLE:
    adapter_factory.register_adapter("tensorrt", TensorRTAdapter)
    adapter_factory.register_adapter("tensorrt", TensorRTAdapter)


    __all__ = [
    __all__ = [
    "BaseModelAdapter",
    "BaseModelAdapter",
    "OllamaAdapter",
    "OllamaAdapter",
    "LMStudioAdapter",
    "LMStudioAdapter",
    "OpenAICompatibleAdapter",
    "OpenAICompatibleAdapter",
    "AdapterFactory",
    "AdapterFactory",
    "adapter_factory",
    "adapter_factory",
    "get_adapter_factory",
    "get_adapter_factory",
    ]
    ]


    # Add TensorRT adapter if available
    # Add TensorRT adapter if available
    if TENSORRT_AVAILABLE:
    if TENSORRT_AVAILABLE:
    __all__.append("TensorRTAdapter")
    __all__.append("TensorRTAdapter")

