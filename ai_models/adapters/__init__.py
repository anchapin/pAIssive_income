"""
Adapters for different AI model frameworks.

This package provides adapters for connecting to various AI model frameworks,
including Ollama, LM Studio, OpenAI-compatible APIs, and GPU acceleration libraries.
"""

from .ollama_adapter import OllamaAdapter
from .lmstudio_adapter import LMStudioAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter

# Import TensorRT adapter if available
try:
    from .tensorrt_adapter import TensorRTAdapter
    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False

__all__ = [
    'OllamaAdapter',
    'LMStudioAdapter',
    'OpenAICompatibleAdapter',
]

# Add TensorRT adapter if available
if TENSORRT_AVAILABLE:
    __all__.append('TensorRTAdapter')
