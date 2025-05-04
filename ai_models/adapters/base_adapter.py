"""
"""
Base adapter for AI model frameworks.
Base adapter for AI model frameworks.


This module provides a base class for adapters that connect to various AI model frameworks.
This module provides a base class for adapters that connect to various AI model frameworks.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
from abc import abstractmethod
from abc import abstractmethod
from typing import Any, Dict, List
from typing import Any, Dict, List


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




class BaseModelAdapter(IModelAdapter):
    class BaseModelAdapter(IModelAdapter):
    """
    """
    Base class for model adapters.
    Base class for model adapters.
    """
    """


    def __init__(self, name: str, description: str = ""):
    def __init__(self, name: str, description: str = ""):
    """
    """
    Initialize the base model adapter.
    Initialize the base model adapter.


    Args:
    Args:
    name: Name of the adapter
    name: Name of the adapter
    description: Description of the adapter
    description: Description of the adapter
    """
    """
    self._name = name
    self._name = name
    self._description = description
    self._description = description
    self._connected = False
    self._connected = False


    @property
    @property
    def name(self) -> str:
    def name(self) -> str:
    """Get the adapter name."""
    return self._name

    @property
    def description(self) -> str:
    """Get the adapter description."""
    return self._description

    def is_available(self) -> bool:
    """
    """
    Check if the adapter is available.
    Check if the adapter is available.


    Returns:
    Returns:
    True if available, False otherwise
    True if available, False otherwise
    """
    """
    try:
    try:
    # Default implementation just checks if the adapter can connect
    # Default implementation just checks if the adapter can connect
    result = self.connect()
    result = self.connect()
    if result:
    if result:
    self.disconnect()
    self.disconnect()
    return result
    return result
except Exception as e:
except Exception as e:
    logger.debug(f"Adapter {self.name} is not available: {e}")
    logger.debug(f"Adapter {self.name} is not available: {e}")
    return False
    return False


    @abstractmethod
    @abstractmethod
    def connect(self, **kwargs) -> bool:
    def connect(self, **kwargs) -> bool:
    """
    """
    Connect to the adapter.
    Connect to the adapter.


    Args:
    Args:
    **kwargs: Connection parameters
    **kwargs: Connection parameters


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def disconnect(self) -> bool:
    def disconnect(self) -> bool:
    """
    """
    Disconnect from the adapter.
    Disconnect from the adapter.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
    def get_models(self) -> List[Dict[str, Any]]:
    """
    """
    Get available models from the adapter.
    Get available models from the adapter.


    Returns:
    Returns:
    List of model dictionaries
    List of model dictionaries
    """
    """
    pass
    pass


    def _handle_error(self, error: Exception, error_message: str, **kwargs) -> None:
    def _handle_error(self, error: Exception, error_message: str, **kwargs) -> None:
    """
    """
    Handle an error from the adapter.
    Handle an error from the adapter.


    Args:
    Args:
    error: The exception that occurred
    error: The exception that occurred
    error_message: Human-readable error message
    error_message: Human-readable error message
    **kwargs: Additional error details
    **kwargs: Additional error details


    Raises:
    Raises:
    ModelError: The handled error
    ModelError: The handled error
    """
    """
    # Create a ModelError with the appropriate message and details
    # Create a ModelError with the appropriate message and details
    model_error = ModelError(
    model_error = ModelError(
    message=error_message,
    message=error_message,
    details={"adapter": self.name, **kwargs},
    details={"adapter": self.name, **kwargs},
    original_exception=error,
    original_exception=error,
    )
    )


    # Log and raise the error
    # Log and raise the error
    model_error.log()
    model_error.log()
    raise model_error
    raise model_error

