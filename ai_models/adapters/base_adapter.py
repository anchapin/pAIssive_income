"""base_adapter - Module for ai_models/adapters.base_adapter."""

# Standard library imports
import abc
from typing import Any, Dict, List

# Third-party imports

# Local imports

class BaseModelAdapter(abc.ABC):
    """
    Base class for model adapters.

    This abstract class defines the interface that all model adapters must implement.
    """

    @abc.abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.

        Returns:
            List of model information dictionaries

        """

    @abc.abstractmethod
    async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using the specified model.

        Args:
            model: The name of the model to use
            prompt: The input prompt
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated text

        """

    @abc.abstractmethod
    async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generate chat completions using the specified model.

        Args:
            model: The name of the model to use
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated chat completion

        """

    @abc.abstractmethod
    async def close(self):
        """Close any open connections or resources."""
