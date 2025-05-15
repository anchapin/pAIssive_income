"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports
import logging
from typing import Dict, Any, Optional, Type

# Third-party imports

# Local imports
from .base_adapter import BaseModelAdapter
from .ollama_adapter import OllamaAdapter
from .lmstudio_adapter import LMStudioAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter

logger = logging.getLogger(__name__)

class AdapterFactory:
    """Factory class for creating model adapters."""

    # Registry of adapter types
    _adapter_registry = {
        "ollama": OllamaAdapter,
        "lmstudio": LMStudioAdapter,
        "openai": OpenAICompatibleAdapter,
    }

    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[BaseModelAdapter]) -> None:
        """Register a new adapter type.

        Args:
            name: The name of the adapter type
            adapter_class: The adapter class to register
        """
        cls._adapter_registry[name] = adapter_class
        logger.info(f"Registered adapter type: {name}")

    @classmethod
    def create_adapter(cls, adapter_type: str, **kwargs) -> Optional[BaseModelAdapter]:
        """Create an adapter of the specified type.

        Args:
            adapter_type: The type of adapter to create
            **kwargs: Additional parameters to pass to the adapter constructor

        Returns:
            An instance of the specified adapter type, or None if the type is not registered
        """
        adapter_class = cls._adapter_registry.get(adapter_type)
        if adapter_class is None:
            logger.error(f"Unknown adapter type: {adapter_type}")
            return None

        try:
            adapter = adapter_class(**kwargs)
            logger.info(f"Created adapter of type: {adapter_type}")
            return adapter
        except Exception as e:
            logger.exception(f"Error creating adapter of type {adapter_type}: {e}")
            return None

    @classmethod
    def get_available_adapter_types(cls) -> list[str]:
        """Get a list of available adapter types.

        Returns:
            A list of registered adapter type names
        """
        return list(cls._adapter_registry.keys())
