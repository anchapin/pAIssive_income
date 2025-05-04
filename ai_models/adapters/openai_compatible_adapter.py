"""
"""
OpenAI-compatible API adapter for the AI Models module.
OpenAI-compatible API adapter for the AI Models module.


This module provides an adapter for connecting to OpenAI-compatible APIs,
This module provides an adapter for connecting to OpenAI-compatible APIs,
including local API servers and cloud services.
including local API servers and cloud services.
"""
"""


import logging
import logging
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


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
    logger.warning("Requests not available. OpenAI-compatible adapter will not work.")
    logger.warning("Requests not available. OpenAI-compatible adapter will not work.")
    REQUESTS_AVAILABLE = False
    REQUESTS_AVAILABLE = False


    try:
    try:
    import openai
    import openai


    OPENAI_AVAILABLE = True
    OPENAI_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("OpenAI Python client not available. Using requests instead.")
    logger.warning("OpenAI Python client not available. Using requests instead.")
    OPENAI_AVAILABLE = False
    OPENAI_AVAILABLE = False




    class OpenAICompatibleAdapter:
    class OpenAICompatibleAdapter:
    """
    """
    Adapter for connecting to OpenAI-compatible APIs.
    Adapter for connecting to OpenAI-compatible APIs.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    base_url: str = "http://localhost:8000/v1",
    base_url: str = "http://localhost:8000/v1",
    api_key: Optional[str] = "sk-",
    api_key: Optional[str] = "sk-",
    organization: Optional[str] = None,
    organization: Optional[str] = None,
    timeout: int = 60,
    timeout: int = 60,
    use_client_library: bool = True,
    use_client_library: bool = True,
    **kwargs,
    **kwargs,
    ):
    ):
    """
    """
    Initialize the OpenAI-compatible adapter.
    Initialize the OpenAI-compatible adapter.


    Args:
    Args:
    base_url: Base URL of the API
    base_url: Base URL of the API
    api_key: API key for authentication
    api_key: API key for authentication
    organization: Optional organization ID
    organization: Optional organization ID
    timeout: Timeout for API requests in seconds
    timeout: Timeout for API requests in seconds
    use_client_library: Whether to use the OpenAI client library if available
    use_client_library: Whether to use the OpenAI client library if available
    **kwargs: Additional parameters for the adapter
    **kwargs: Additional parameters for the adapter
    """
    """
    self.base_url = base_url
    self.base_url = base_url
    self.api_key = api_key
    self.api_key = api_key
    self.organization = organization
    self.organization = organization
    self.timeout = timeout
    self.timeout = timeout
    self.use_client_library = use_client_library and OPENAI_AVAILABLE
    self.use_client_library = use_client_library and OPENAI_AVAILABLE
    self.kwargs = kwargs
    self.kwargs = kwargs


    if self.use_client_library:
    if self.use_client_library:
    # Initialize OpenAI client
    # Initialize OpenAI client
    self.client = openai.OpenAI(
    self.client = openai.OpenAI(
    base_url=self.base_url,
    base_url=self.base_url,
    api_key=self.api_key,
    api_key=self.api_key,
    organization=self.organization,
    organization=self.organization,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    else:
    else:
    if not REQUESTS_AVAILABLE:
    if not REQUESTS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Requests not available. Please install it with: pip install requests"
    "Requests not available. Please install it with: pip install requests"
    )
    )


    # Initialize requests session
    # Initialize requests session
    self.session = requests.Session()
    self.session = requests.Session()


    # Set up headers
    # Set up headers
    self.headers = {"Content-Type": "application/json"}
    self.headers = {"Content-Type": "application/json"}


    if self.api_key:
    if self.api_key:
    self.headers["Authorization"] = f"Bearer {self.api_key}"
    self.headers["Authorization"] = f"Bearer {self.api_key}"


    if self.organization:
    if self.organization:
    self.headers["OpenAI-Organization"] = self.organization
    self.headers["OpenAI-Organization"] = self.organization


    # Check if the API is available
    # Check if the API is available
    self._check_api_status()
    self._check_api_status()


    def _check_api_status(self) -> None:
    def _check_api_status(self) -> None:
    """
    """
    Check if the API is available.
    Check if the API is available.


    Raises:
    Raises:
    ConnectionError: If the API is not available
    ConnectionError: If the API is not available
    """
    """
    try:
    try:
    if self.use_client_library:
    if self.use_client_library:
    # Try to list models
    # Try to list models
    self.client.models.list()
    self.client.models.list()
    else:
    else:
    # Try to list models
    # Try to list models
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/models", headers=self.headers, timeout=5
    f"{self.base_url}/models", headers=self.headers, timeout=5
    )
    )
    if response.status_code != 200:
    if response.status_code != 200:
    logger.warning(f"API returned status code {response.status_code}")
    logger.warning(f"API returned status code {response.status_code}")
except Exception as e:
except Exception as e:
    logger.error(f"Error connecting to API: {e}")
    logger.error(f"Error connecting to API: {e}")
    raise ConnectionError(
    raise ConnectionError(
    f"Could not connect to API at {self.base_url}. Make sure the API server is running."
    f"Could not connect to API at {self.base_url}. Make sure the API server is running."
    )
    )


    def list_models(self) -> List[Dict[str, Any]]:
    def list_models(self) -> List[Dict[str, Any]]:
    """
    """
    List available models.
    List available models.


    Returns:
    Returns:
    List of model information dictionaries
    List of model information dictionaries
    """
    """
    try:
    try:
    if self.use_client_library:
    if self.use_client_library:
    models = self.client.models.list()
    models = self.client.models.list()
    return [model.model_dump() for model in models.data]
    return [model.model_dump() for model in models.data]
    else:
    else:
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/models",
    f"{self.base_url}/models",
    headers=self.headers,
    headers=self.headers,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    data = response.json()
    data = response.json()
    return data.get("data", [])
    return data.get("data", [])


except Exception as e:
except Exception as e:
    logger.error(f"Error listing models: {e}")
    logger.error(f"Error listing models: {e}")
    raise
    raise

