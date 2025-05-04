"""
"""
Ollama adapter for the AI Models module.
Ollama adapter for the AI Models module.


This module provides an adapter for connecting to Ollama,
This module provides an adapter for connecting to Ollama,
a local API server for running large language models.
a local API server for running large language models.
"""
"""


import logging
import logging
from typing import Any, Dict, List
from typing import Any, Dict, List


from .base_adapter import BaseModelAdapter
from .base_adapter import BaseModelAdapter


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Try to import optional dependencies
# Try to import optional dependencies
try:
    try:
    import requests
    import requests


    REQUESTS_AVAILABLE = True
    REQUESTS_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("Requests not available. Ollama adapter will not work.")
    logger.warning("Requests not available. Ollama adapter will not work.")
    REQUESTS_AVAILABLE = False
    REQUESTS_AVAILABLE = False


    # Check for aiohttp availability for async operations
    # Check for aiohttp availability for async operations
    try:
    try:
    import aiohttp
    import aiohttp


    AIOHTTP_AVAILABLE = True
    AIOHTTP_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("aiohttp not available. Async operations will not work.")
    logger.warning("aiohttp not available. Async operations will not work.")
    AIOHTTP_AVAILABLE = False
    AIOHTTP_AVAILABLE = False




    class OllamaAdapter(BaseModelAdapter):
    class OllamaAdapter(BaseModelAdapter):
    """
    """
    Adapter for connecting to Ollama.
    Adapter for connecting to Ollama.
    """
    """


    def __init__(
    def __init__(
    self, base_url: str = "http://localhost:11434", timeout: int = 60, **kwargs
    self, base_url: str = "http://localhost:11434", timeout: int = 60, **kwargs
    ):
    ):
    """
    """
    Initialize the Ollama adapter.
    Initialize the Ollama adapter.


    Args:
    Args:
    base_url: Base URL of the Ollama API
    base_url: Base URL of the Ollama API
    timeout: Timeout for API requests in seconds
    timeout: Timeout for API requests in seconds
    **kwargs: Additional parameters for the adapter
    **kwargs: Additional parameters for the adapter
    """
    """
    super().__init__(
    super().__init__(
    name="Ollama",
    name="Ollama",
    description="Adapter for connecting to Ollama, a local API server for running large language models",
    description="Adapter for connecting to Ollama, a local API server for running large language models",
    )
    )


    if not REQUESTS_AVAILABLE:
    if not REQUESTS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Requests not available. Please install it with: pip install requests"
    "Requests not available. Please install it with: pip install requests"
    )
    )


    self.base_url = base_url
    self.base_url = base_url
    self.timeout = timeout
    self.timeout = timeout
    self.kwargs = kwargs
    self.kwargs = kwargs
    self.session = requests.Session()
    self.session = requests.Session()
    self._async_session = None
    self._async_session = None


    # Check if Ollama is running
    # Check if Ollama is running
    self._check_ollama_status()
    self._check_ollama_status()


    def _check_ollama_status(self) -> None:
    def _check_ollama_status(self) -> None:
    """
    """
    Check if Ollama is running.
    Check if Ollama is running.


    Raises:
    Raises:
    ConnectionError: If Ollama is not running
    ConnectionError: If Ollama is not running
    """
    """
    try:
    try:
    response = self.session.get(f"{self.base_url}", timeout=5)
    response = self.session.get(f"{self.base_url}", timeout=5)
    if response.status_code != 200:
    if response.status_code != 200:
    logger.warning(f"Ollama returned status code {response.status_code}")
    logger.warning(f"Ollama returned status code {response.status_code}")
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error connecting to Ollama: {e}")
    logger.error(f"Error connecting to Ollama: {e}")
    raise ConnectionError(
    raise ConnectionError(
    f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
    f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
    )
    )


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
    try:
    try:
    # Try to connect to the Ollama API
    # Try to connect to the Ollama API
    response = self.session.get(f"{self.base_url}", timeout=5)
    response = self.session.get(f"{self.base_url}", timeout=5)
    if response.status_code != 200:
    if response.status_code != 200:
    logger.warning(f"Ollama returned status code {response.status_code}")
    logger.warning(f"Ollama returned status code {response.status_code}")
    self._connected = False
    self._connected = False
    return False
    return False


    self._connected = True
    self._connected = True
    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Failed to connect to Ollama: {e}")
    logger.error(f"Failed to connect to Ollama: {e}")
    self._connected = False
    self._connected = False
    return False
    return False


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
    try:
    try:
    self.session.close()
    self.session.close()
    self._connected = False
    self._connected = False
    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Error disconnecting from Ollama: {e}")
    logger.error(f"Error disconnecting from Ollama: {e}")
    return False
    return False


    def list_models(self) -> List[Dict[str, Any]]:
    def list_models(self) -> List[Dict[str, Any]]:
    """
    """
    List available models in Ollama.
    List available models in Ollama.


    Returns:
    Returns:
    List of model information dictionaries
    List of model information dictionaries
    """
    """
    try:
    try:
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/api/tags", timeout=self.timeout
    f"{self.base_url}/api/tags", timeout=self.timeout
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    data = response.json()
    data = response.json()
    return data.get("models", [])
    return data.get("models", [])


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error listing models: {e}")
    logger.error(f"Error listing models: {e}")
    raise
    raise


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
    try:
    try:
    models = self.list_models()
    models = self.list_models()


    # Transform the model data to a standard format
    # Transform the model data to a standard format
    standardized_models = []
    standardized_models = []
    for model in models:
    for model in models:
    standardized_models.append(
    standardized_models.append(
    {
    {
    "id": model.get("name", ""),
    "id": model.get("name", ""),
    "name": model.get("name", "").split(":")[0],
    "name": model.get("name", "").split(":")[0],
    "description": f"Ollama model: {model.get('name', '')}",
    "description": f"Ollama model: {model.get('name', '')}",
    "type": "llm",
    "type": "llm",
    "size": model.get("size", 0),
    "size": model.get("size", 0),
    "modified_at": model.get("modified_at", ""),
    "modified_at": model.get("modified_at", ""),
    "adapter": "ollama",
    "adapter": "ollama",
    }
    }
    )
    )


    return standardized_models
    return standardized_models


except Exception as e:
except Exception as e:
    self._handle_error(
    self._handle_error(
    e, "Failed to get models from Ollama", operation="get_models"
    e, "Failed to get models from Ollama", operation="get_models"
    )
    )
    return []
    return []

