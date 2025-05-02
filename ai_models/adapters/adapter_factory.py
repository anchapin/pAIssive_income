"""Factory for creating model adapters."""

from typing import Type

# Import BaseModelAdapter directly to avoid circular imports
from .base_adapter import BaseModelAdapter


class AdapterFactory:
    """Factory for creating model adapters."""

    def __init__(self):
        """Initialize the adapter factory."""
        self._adapter_registry = {}

    def register_adapter(self, adapter_type: str, adapter_class: Type[BaseModelAdapter]) -> None:
        """Register an adapter class with the factory.

        Args:
            adapter_type: Type name for the adapter
            adapter_class: Adapter class to register
        """
        self._adapter_registry[adapter_type] = adapter_class

    def create_adapter(self, adapter_type: str, **kwargs) -> BaseModelAdapter:
        """Create a model adapter instance.

        Args:
            adapter_type: Type of adapter to create
            **kwargs: Additional arguments to pass to the adapter constructor

        Returns:
            Instance of the requested adapter type

        Raises:
            ValueError: If adapter_type is not supported
        """
        if adapter_type not in self._adapter_registry:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")

        adapter_class = self._adapter_registry[adapter_type]
        return adapter_class(**kwargs)


# Create a singleton instance of the adapter factory
adapter_factory = AdapterFactory()


def get_adapter_factory() -> AdapterFactory:
    """Get the singleton adapter factory instance.

    Returns:
        The adapter factory instance
    """
    return adapter_factory
