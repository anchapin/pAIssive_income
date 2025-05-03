"""OpenAI - compatible model adapter implementation."""

import logging
from typing import Any, Dict, List, Optional, Union

from .base_adapter import BaseModelAdapter

logger = logging.getLogger(__name__)


class OpenAICompatibleAdapter(BaseModelAdapter):
    """Adapter for OpenAI - compatible API endpoints."""

    def __init__(self, model_id: str, config: Dict[str, Any]):
        """Initialize OpenAI adapter."""
        super().__init__(model_id, config)
        self.api_base = config.get("api_base", "https://api.openai.com / v1")
        self.api_key = config.get("api_key")

    def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
    ) -> str:
        """
        Generate text using the model.

        Args:
            prompt: Text prompt to generate from
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0 - 1)
            stop: Stop sequence(s) to end generation

        Returns:
            Generated text

        Raises:
            ModelError: If generation fails
        """
        try:
            response = self._make_request(
                "completions",
                {
                    "model": self.model_id,
                    "prompt": prompt,
                    "max_tokens": max_tokens or 100,
                    "temperature": temperature or self.config.get("temperature", 0.7),
                    "stop": stop,
                },
            )
            return response["choices"][0]["text"]
        except Exception as e:
            self._handle_error(e, "Text generation failed")
            return ""

    def embed_text(self, text: str) -> List[float]:
        """
        Generate text embeddings.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            ModelError: If embedding fails
        """
        try:
            response = self._make_request(
                "embeddings",
                {
                    "model": self.model_id,
                    "input": text,
                },
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            self._handle_error(e, "Text embedding failed")
            return []

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request."""
        import requests

        headers = {
            "Content - Type": "application / json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Use a default timeout of 30 seconds if not specified in config
        timeout = self.config.get("timeout", 30)

        response = requests.post(
            f"{self.api_base}/{endpoint}",
            headers=headers,
            json=payload,
            timeout=timeout,
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")

        return response.json()
