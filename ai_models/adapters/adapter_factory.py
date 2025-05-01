"""Factory for creating model adapters."""

from typing import Type

from . import (
    BaseModelAdapter,
    LMStudioAdapter,
    OllamaAdapter,
    OpenAICompatibleAdapter,
    TensorRTAdapter,
)
from .base_adapter import BaseAdapter


class AdapterFactory:
    """Factory for creating model adapters."""

    _adapter_types = {
        "base": BaseModelAdapter,
        "lmstudio": LMStudioAdapter,
        "ollama": OllamaAdapter,
        "openai": OpenAICompatibleAdapter,
        "tensorrt": TensorRTAdapter,
    }

    @classmethod
    def create_adapter(cls, adapter_type: str) -> BaseAdapter:
        """Create a model adapter instance.

        Args:
            adapter_type: Type of adapter to create

        Returns:
            Instance of the requested adapter type

        Raises:
            ValueError: If adapter_type is not supported
        """
        if adapter_type not in cls._adapter_types:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")

        adapter_class = cls._adapter_types[adapter_type]
        return adapter_class()
