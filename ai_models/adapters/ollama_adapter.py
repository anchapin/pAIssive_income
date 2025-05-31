"""ollama_adapter - Module for ai_models/adapters.ollama_adapter."""

# Standard library imports
import asyncio
import logging
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging

# Third-party imports
try:
    import aiohttp
except ImportError:
    # If aiohttp is not available, try to use our mock implementation
    try:
        from ai_models import mock_aiohttp as aiohttp
        logger.info("Using mock aiohttp in ollama_adapter")
    except ImportError as e:
        logger.exception(f"Failed to import mock_aiohttp: {e}")
        # Create a minimal mock to prevent import errors
        class aiohttp:
            class ClientSession:
                def __init__(self, *args, **kwargs) -> None:
                    pass
            class ClientTimeout:
                def __init__(self, *args, **kwargs) -> None:
                    pass

# Local imports
from .base_adapter import BaseModelAdapter

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging



class OllamaAdapter(BaseModelAdapter):
    """Adapter for connecting to Ollama, a local API server for running large language models."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60) -> None:
        """
        Initialize the Ollama adapter.

        Args:
            base_url: The base URL of the Ollama API server
            timeout: Request timeout in seconds

        """
        self.base_url = base_url
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized OllamaAdapter with base_url={base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session

    async def list_models(self) -> list[dict[str, Any]]:
        """
        List available models from Ollama.

        Returns:
            List of model information dictionaries

        """
        session = await self._get_session()
        try:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                error_text = await response.text()
                msg = f"Failed to list models (status {response.status}): {error_text}"
                raise Exception(msg)
        except aiohttp.ClientConnectionError as e:
            msg = f"Failed to connect to Ollama server: {e}"
            raise Exception(msg)
        except asyncio.TimeoutError:
            msg = "Request to Ollama server timed out"
            raise Exception(msg)
        except Exception as e:
            msg = f"Error listing models: {e}"
            raise Exception(msg)

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
            **kwargs
        }

        try:
            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                msg = f"Failed to generate text (status {response.status}): {error_text}"
                raise Exception(msg)
        except aiohttp.ClientConnectionError as e:
            msg = f"Failed to connect to Ollama server: {e}"
            raise Exception(msg)
        except asyncio.TimeoutError:
            msg = "Request to Ollama server timed out"
            raise Exception(msg)
        except Exception as e:
            msg = f"Error generating text: {e}"
            raise Exception(msg)

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
            **kwargs
        }

        try:
            async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                msg = f"Failed to generate chat completion (status {response.status}): {error_text}"
                raise Exception(msg)
        except aiohttp.ClientConnectionError as e:
            msg = f"Failed to connect to Ollama server: {e}"
            raise Exception(msg)
        except asyncio.TimeoutError:
            msg = "Request to Ollama server timed out"
            raise Exception(msg)
        except Exception as e:
            msg = f"Error generating chat completion: {e}"
            raise Exception(msg)

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    def __del__(self) -> None:
        """Ensure the session is closed when the adapter is garbage collected."""
        if self._session and not self._session.closed:
            asyncio.create_task(self._session.close())
