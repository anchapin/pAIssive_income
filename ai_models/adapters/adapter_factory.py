"""
"""
Factory for creating model adapters.
Factory for creating model adapters.


This module provides a factory for creating model adapters based on adapter type.
This module provides a factory for creating model adapters based on adapter type.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
from typing import Dict, List, Type
from typing import Dict, List, Type


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from errors import ModelError
from errors import ModelError
from interfaces.model_interfaces import IModelAdapter
from interfaces.model_interfaces import IModelAdapter


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class AdapterFactory:
    class AdapterFactory:
    """
    """
    Factory for creating model adapters.
    Factory for creating model adapters.
    """
    """


    def __init__(self):
    def __init__(self):
    """Initialize the adapter factory."""
    self._adapters: Dict[str, Type[IModelAdapter]] = {}

    def register_adapter(
    self, adapter_type: str, adapter_class: Type[IModelAdapter]
    ) -> None:
    """
    """
    Register an adapter class.
    Register an adapter class.


    Args:
    Args:
    adapter_type: Type of adapter
    adapter_type: Type of adapter
    adapter_class: Adapter class
    adapter_class: Adapter class
    """
    """
    self._adapters[adapter_type] = adapter_class
    self._adapters[adapter_type] = adapter_class
    logger.debug(f"Registered adapter: {adapter_type}")
    logger.debug(f"Registered adapter: {adapter_type}")


    def create_adapter(self, adapter_type: str, **kwargs) -> IModelAdapter:
    def create_adapter(self, adapter_type: str, **kwargs) -> IModelAdapter:
    """
    """
    Create an adapter instance.
    Create an adapter instance.


    Args:
    Args:
    adapter_type: Type of adapter
    adapter_type: Type of adapter
    **kwargs: Additional parameters for the adapter
    **kwargs: Additional parameters for the adapter


    Returns:
    Returns:
    Adapter instance
    Adapter instance


    Raises:
    Raises:
    ModelError: If the adapter type is not registered
    ModelError: If the adapter type is not registered
    """
    """
    try:
    try:
    if adapter_type not in self._adapters:
    if adapter_type not in self._adapters:
    raise ValueError(f"Adapter type not registered: {adapter_type}")
    raise ValueError(f"Adapter type not registered: {adapter_type}")


    adapter_class = self._adapters[adapter_type]
    adapter_class = self._adapters[adapter_type]
    adapter = adapter_class(**kwargs)
    adapter = adapter_class(**kwargs)


    logger.debug(f"Created adapter: {adapter_type}")
    logger.debug(f"Created adapter: {adapter_type}")
    return adapter
    return adapter


except Exception as e:
except Exception as e:
    # Create a ModelError with the appropriate message and details
    # Create a ModelError with the appropriate message and details
    error = ModelError(
    error = ModelError(
    message=f"Failed to create adapter: {adapter_type}",
    message=f"Failed to create adapter: {adapter_type}",
    details={
    details={
    "adapter_type": adapter_type,
    "adapter_type": adapter_type,
    "available_adapters": list(self._adapters.keys()),
    "available_adapters": list(self._adapters.keys()),
    },
    },
    original_exception=e,
    original_exception=e,
    )
    )


    # Log and raise the error
    # Log and raise the error
    error.log()
    error.log()
    raise error
    raise error
    # This line won't be reached due to reraise=True
    # This line won't be reached due to reraise=True
    return None
    return None


    def get_available_adapters(self) -> List[str]:
    def get_available_adapters(self) -> List[str]:
    """
    """
    Get a list of available adapter types.
    Get a list of available adapter types.


    Returns:
    Returns:
    List of adapter types
    List of adapter types
    """
    """
    return list(self._adapters.keys())
    return list(self._adapters.keys())




    # Create a global adapter factory
    # Create a global adapter factory
    adapter_factory = AdapterFactory()
    adapter_factory = AdapterFactory()




    def get_adapter_factory() -> AdapterFactory:
    def get_adapter_factory() -> AdapterFactory:
    """
    """
    Get the global adapter factory.
    Get the global adapter factory.


    Returns:
    Returns:
    Global adapter factory
    Global adapter factory
    """
    """
    return adapter_factory
    return adapter_factory

