"""lmstudio_adapter - Module for ai_models/adapters.lmstudio_adapter."""

# Standard library imports
import logging
import asyncio
import sys # Added sys import
logger = logging.getLogger(__name__)
from typing import Dict, List, Any

try:
    import aiohttp
except ImportError:
    logger.exception("aiohttp library not found. Please install it using 'pip install aiohttp'")
    sys.exit(1)


# Third-party imports

# Local imports
from .base_adapter import BaseModelAdapter


class LMStudioAdapter(BaseModelAdapter):
    """Adapter for connecting to LM Studio, a local API server for running large language models."""

    def __init__(self, host_or_base_url: str = "http://localhost:1234/v1", port: int = None, api_key: str = "", timeout: int = 60):
        """Initialize the LM Studio adapter.

        Args:
            host_or_base_url: Either a full base URL or just the host (for backward compatibility)
            port: Port number (only used if host_or_base_url is just a host)
            api_key: API key (usually not required for local LM Studio)
            timeout: Request timeout in seconds
        """
        # Support both old interface (host, port) and new interface (base_url)
        if port is not None:
            # Old interface: separate host and port
            self.host = host_or_base_url
            self.port = port
            self.base_url = f"http://{self.host}:{self.port}/v1"
        else:
            # New interface: full base_url
            self.base_url = host_or_base_url
            # Extract host and port for backward compatibility
            if "://" in self.base_url:
                url_parts = self.base_url.split("://")[1].split("/")[0]
                if ":" in url_parts:
                    self.host, port_str = url_parts.split(":")
                    self.port = int(port_str)
                else:
                    self.host = url_parts
                    self.port = 80 if self.base_url.startswith("http://") else 443
            else:
                self.host = "localhost"
                self.port = 1234
        
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized LMStudioAdapter with base_url={self.base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=headers
            )
        return self._session

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from LM Studio.

        Returns:
            List of model information dictionaries
        """
        session = await self._get_session()
        try:
            async with session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
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
