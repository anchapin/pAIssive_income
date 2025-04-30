"""
Factory for creating model adapters.

This module provides a factory for creating model adapters based on adapter type.
"""

import logging
from typing import Dict, List, Any, Optional, Type, Union

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from interfaces.model_interfaces import IModelAdapter
from errors import ModelError, handle_exception

# Set up logging
logger = logging.getLogger(__name__)


class AdapterFactory:
    """
    Factory for creating model adapters.
    """

    def __init__(self):
        """Initialize the adapter factory."""
        self._adapters: Dict[str, Type[IModelAdapter]] = {}

    def register_adapter(
        self, adapter_type: str, adapter_class: Type[IModelAdapter]
    ) -> None:
        """
        Register an adapter class.

        Args:
            adapter_type: Type of adapter
            adapter_class: Adapter class
        """
        self._adapters[adapter_type] = adapter_class
        logger.debug(f"Registered adapter: {adapter_type}")

    def create_adapter(self, adapter_type: str, **kwargs) -> IModelAdapter:
        """
        Create an adapter instance.

        Args:
            adapter_type: Type of adapter
            **kwargs: Additional parameters for the adapter

        Returns:
            Adapter instance

        Raises:
            ModelError: If the adapter type is not registered
        """
        try:
            if adapter_type not in self._adapters:
                raise ValueError(f"Adapter type not registered: {adapter_type}")

            adapter_class = self._adapters[adapter_type]
            adapter = adapter_class(**kwargs)

            logger.debug(f"Created adapter: {adapter_type}")
            return adapter

        except Exception as e:
            # Create a ModelError with the appropriate message and details
            error = ModelError(
                message=f"Failed to create adapter: {adapter_type}",
                details={
                    "adapter_type": adapter_type,
                    "available_adapters": list(self._adapters.keys()),
                },
                original_exception=e,
            )

            # Log and raise the error
            error.log()
            raise error
            # This line won't be reached due to reraise=True
            return None

    def get_available_adapters(self) -> List[str]:
        """
        Get a list of available adapter types.

        Returns:
            List of adapter types
        """
        return list(self._adapters.keys())


# Create a global adapter factory
adapter_factory = AdapterFactory()


def get_adapter_factory() -> AdapterFactory:
    """
    Get the global adapter factory.

    Returns:
        Global adapter factory
    """
    return adapter_factory
