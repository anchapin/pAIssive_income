"""
Ollama adapter for the AI Models module.

This module provides an adapter for connecting to Ollama,
a local API server for running large language models.
"""

import logging
from typing import Any, Dict, List

from .base_adapter import BaseModelAdapter

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("Requests not available. Ollama adapter will not work.")
    REQUESTS_AVAILABLE = False

    # Check for aiohttp availability for async operations
    try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    logger.warning("aiohttp not available. Async operations will not work.")
    AIOHTTP_AVAILABLE = False


    class OllamaAdapter(BaseModelAdapter):
    """
    Adapter for connecting to Ollama.
    """

    def __init__(
    self, base_url: str = "http://localhost:11434", timeout: int = 60, **kwargs
    ):
    """
    Initialize the Ollama adapter.

    Args:
    base_url: Base URL of the Ollama API
    timeout: Timeout for API requests in seconds
    **kwargs: Additional parameters for the adapter
    """
    super().__init__(
    name="Ollama",
    description="Adapter for connecting to Ollama, a local API server for running large language models",
    )

    if not REQUESTS_AVAILABLE:
    raise ImportError(
    "Requests not available. Please install it with: pip install requests"
    )

    self.base_url = base_url
    self.timeout = timeout
    self.kwargs = kwargs
    self.session = requests.Session()
    self._async_session = None

    # Check if Ollama is running
    self._check_ollama_status()

    def _check_ollama_status(self) -> None:
    """
    Check if Ollama is running.

    Raises:
    ConnectionError: If Ollama is not running
    """
    try:
    response = self.session.get(f"{self.base_url}", timeout=5)
    if response.status_code != 200:
    logger.warning(f"Ollama returned status code {response.status_code}")
except requests.exceptions.RequestException as e:
    logger.error(f"Error connecting to Ollama: {e}")
    raise ConnectionError(
    f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
    )

    def connect(self, **kwargs) -> bool:
    """
    Connect to the adapter.

    Args:
    **kwargs: Connection parameters

    Returns:
    True if successful, False otherwise
    """
    try:
    # Try to connect to the Ollama API
    response = self.session.get(f"{self.base_url}", timeout=5)
    if response.status_code != 200:
    logger.warning(f"Ollama returned status code {response.status_code}")
    self._connected = False
    return False

    self._connected = True
    return True
except Exception as e:
    logger.error(f"Failed to connect to Ollama: {e}")
    self._connected = False
    return False

    def disconnect(self) -> bool:
    """
    Disconnect from the adapter.

    Returns:
    True if successful, False otherwise
    """
    try:
    self.session.close()
    self._connected = False
    return True
except Exception as e:
    logger.error(f"Error disconnecting from Ollama: {e}")
    return False

    def list_models(self) -> List[Dict[str, Any]]:
    """
    List available models in Ollama.

    Returns:
    List of model information dictionaries
    """
    try:
    response = self.session.get(
    f"{self.base_url}/api/tags", timeout=self.timeout
    )
    response.raise_for_status()

    data = response.json()
    return data.get("models", [])

except requests.exceptions.RequestException as e:
    logger.error(f"Error listing models: {e}")
    raise

    def get_models(self) -> List[Dict[str, Any]]:
    """
    Get available models from the adapter.

    Returns:
    List of model dictionaries
    """
    try:
    models = self.list_models()

    # Transform the model data to a standard format
    standardized_models = []
    for model in models:
    standardized_models.append(
    {
    "id": model.get("name", ""),
    "name": model.get("name", "").split(":")[0],
    "description": f"Ollama model: {model.get('name', '')}",
    "type": "llm",
    "size": model.get("size", 0),
    "modified_at": model.get("modified_at", ""),
    "adapter": "ollama",
    }
    )

    return standardized_models

except Exception as e:
    self._handle_error(
    e, "Failed to get models from Ollama", operation="get_models"
    )
    return []
