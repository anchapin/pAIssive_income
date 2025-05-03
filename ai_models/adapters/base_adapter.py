"""
Base adapter for AI model frameworks.

This module provides a base class for adapters that connect to various AI model frameworks.
"""

import logging
import os
import sys
from abc import abstractmethod
from typing import Any, Dict, List

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import after path modification
from errors import ModelError
from interfaces.model_interfaces import IModelAdapter

# Set up logging
logger = logging.getLogger(__name__)


class BaseModelAdapter(IModelAdapter):
    """
    Base class for model adapters.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base model adapter.

        Args:
            name: Name of the adapter
            description: Description of the adapter
        """
        self._name = name
        self._description = description
        self._connected = False

    @property
    def name(self) -> str:
        """Get the adapter name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the adapter description."""
        return self._description

    def is_available(self) -> bool:
        """
        Check if the adapter is available.

        Returns:
            True if available, False otherwise
        """
        try:
            # Default implementation just checks if the adapter can connect
            result = self.connect()
            if result:
                self.disconnect()
            return result
        except Exception as e:
            logger.debug(f"Adapter {self.name} is not available: {e}")
            return False

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to the adapter.

        Args:
            **kwargs: Connection parameters

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the adapter.

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from the adapter.

        Returns:
            List of model dictionaries
        """

    def _handle_error(self, error: Exception, error_message: str, **kwargs) -> None:
        """
        Handle an error from the adapter.

        Args:
            error: The exception that occurred
            error_message: Human - readable error message
            **kwargs: Additional error details

        Raises:
            ModelError: The handled error
        """
        # Create a ModelError with the appropriate message and details
        model_error = ModelError(
            message=error_message,
            details={"adapter": self.name, **kwargs},
            original_exception=error,
        )

        # Log and raise the error
        model_error.log()
        raise model_error
