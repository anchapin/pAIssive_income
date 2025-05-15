"""ollama_adapter - Module for ai_models/adapters.ollama_adapter."""

# Standard library imports
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any

# Third-party imports

# Local imports
from .base_adapter import BaseModelAdapter

logger = logging.getLogger(__name__)

class OllamaAdapter(BaseModelAdapter):
    """Adapter for connecting to Ollama, a local API server for running large language models."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60):
        """Initialize the Ollama adapter.

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

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama.

        Returns:
            List of model information dictionaries
        """
        session = await self._get_session()
        try:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to list models: {error_text}")
                    return []
        except Exception as e:
            logger.exception(f"Error listing models: {e}")
            return []

    async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the specified model.

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
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to generate text: {error_text}")
                    return {"error": error_text}
        except Exception as e:
            logger.exception(f"Error generating text: {e}")
            return {"error": str(e)}

    async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completions using the specified model.

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
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to generate chat completion: {error_text}")
                    return {"error": error_text}
        except Exception as e:
            logger.exception(f"Error generating chat completion: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def __del__(self):
        """Ensure the session is closed when the adapter is garbage collected."""
        if self._session and not self._session.closed:
            asyncio.create_task(self._session.close())
