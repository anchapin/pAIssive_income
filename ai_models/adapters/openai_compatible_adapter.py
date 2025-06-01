"""openai_compatible_adapter - Module for ai_models/adapters.openai_compatible_adapter."""

# Standard library imports
import asyncio
import logging

logger = logging.getLogger(__name__)
from typing import Any, Union

try:
    import aiohttp
except ImportError:
    logger.warning("aiohttp library not found. OpenAICompatibleAdapter will not be available.")
    aiohttp = None


# Third-party imports

# Local imports
from .base_adapter import BaseModelAdapter

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging



class OpenAICompatibleAdapter(BaseModelAdapter):
    """Adapter for connecting to OpenAI-compatible APIs, including local servers that implement the OpenAI API."""

    def __init__(self, base_url: str = "https://api.openai.com/v1", api_key: str = "sk-", timeout: int = 60) -> None:
        """
        Initialize the OpenAI-compatible adapter.

        Args:
            base_url: The base URL of the OpenAI-compatible API server
            api_key: API key for authentication
            timeout: Request timeout in seconds

        Raises:
            ImportError: If aiohttp is not available

        """
        if aiohttp is None:
            raise ImportError("aiohttp library is required for OpenAICompatibleAdapter. Please install it using 'pip install aiohttp'")

        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized OpenAICompatibleAdapter with base_url={base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=headers
            )
        return self._session

    async def list_models(self) -> list[dict[str, Any]]:
        """
        List available models from the OpenAI-compatible API.

        Returns:
            List of model information dictionaries

        """
        session = await self._get_session()
        try:
            async with session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                error_text = await response.text()
                logger.error(f"Failed to list models: {error_text}")
                return []
        except Exception as e:
            logger.exception(f"Error listing models: {e}")
            return []

    async def generate_text(self, model: str, prompt: str, **kwargs) -> dict[str, Any]:
        """
        Generate text using the specified model.

        Args:
            model: The name of the model to use
            prompt: The input prompt
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated text

        """
        session = await self._get_session()
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "n": kwargs.get("n", 1),
            "stream": kwargs.get("stream", False),
            "stop": kwargs.get("stop"),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
        }

        try:
            async with session.post(f"{self.base_url}/completions", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                logger.error(f"Failed to generate text: {error_text}")
                return {"error": error_text}
        except Exception as e:
            logger.exception(f"Error generating text: {e}")
            return {"error": str(e)}

    async def generate_chat_completions(self, model: str, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]:
        """
        Generate chat completions using the specified model.

        Args:
            model: The name of the model to use
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated chat completion

        """
        session = await self._get_session()
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "n": kwargs.get("n", 1),
            "stream": kwargs.get("stream", False),
            "stop": kwargs.get("stop"),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
        }

        try:
            async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                logger.error(f"Failed to generate chat completion: {error_text}")
                return {"error": error_text}
        except Exception as e:
            logger.exception(f"Error generating chat completion: {e}")
            return {"error": str(e)}

    async def create_embedding(self, model: str, input_text: Union[str, list[str]], **kwargs) -> dict[str, Any]:
        """
        Create embeddings for the given input text.

        Args:
            model: The name of the model to use
            input_text: The input text or list of texts to embed
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the embeddings

        """
        session = await self._get_session()
        payload = {
            "model": model,
            "input": input_text,
            **kwargs
        }

        try:
            async with session.post(f"{self.base_url}/embeddings", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                logger.error(f"Failed to create embeddings: {error_text}")
                return {"error": error_text}
        except Exception as e:
            logger.exception(f"Error creating embeddings: {e}")
            return {"error": str(e)}

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    def __del__(self) -> None:
        """Ensure the session is closed when the adapter is garbage collected."""
        if self._session and not self._session.closed:
            asyncio.create_task(self._session.close())
