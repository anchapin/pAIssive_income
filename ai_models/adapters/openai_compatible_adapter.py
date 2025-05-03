"""
OpenAI-compatible API adapter for the AI Models module.

This module provides an adapter for connecting to OpenAI-compatible APIs,
including local API servers and cloud services.
"""

import json
import logging
from typing import Any, Dict, Generator, List, Optional, Union

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
    logger.warning("Requests not available. OpenAI-compatible adapter will not work.")
    REQUESTS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI Python client not available. Using requests instead.")
    OPENAI_AVAILABLE = False


class OpenAICompatibleAdapter:
    """
    Adapter for connecting to OpenAI-compatible APIs.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: Optional[str] = "sk-",
        organization: Optional[str] = None,
        timeout: int = 60,
        use_client_library: bool = True,
        **kwargs,
    ):
        """
        Initialize the OpenAI-compatible adapter.

        Args:
            base_url: Base URL of the API
            api_key: API key for authentication
            organization: Optional organization ID
            timeout: Timeout for API requests in seconds
            use_client_library: Whether to use the OpenAI client library if available
            **kwargs: Additional parameters for the adapter
        """
        self.base_url = base_url
        self.api_key = api_key
        self.organization = organization
        self.timeout = timeout
        self.use_client_library = use_client_library and OPENAI_AVAILABLE
        self.kwargs = kwargs

        if self.use_client_library:
            # Initialize OpenAI client
            self.client = openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                organization=self.organization,
                timeout=self.timeout,
            )
        else:
            if not REQUESTS_AVAILABLE:
                raise ImportError(
                    "Requests not available. Please install it with: pip install requests"
                )

            # Initialize requests session
            self.session = requests.Session()

            # Set up headers
            self.headers = {"Content-Type": "application/json"}

            if self.api_key:
                self.headers["Authorization"] = f"Bearer {self.api_key}"

            if self.organization:
                self.headers["OpenAI-Organization"] = self.organization

        # Check if the API is available
        self._check_api_status()

    def _check_api_status(self) -> None:
        """
        Check if the API is available.

        Raises:
            ConnectionError: If the API is not available
        """
        try:
            if self.use_client_library:
                # Try to list models
                self.client.models.list()
            else:
                # Try to list models
                response = self.session.get(
                    f"{self.base_url}/models", headers=self.headers, timeout=5
                )
                if response.status_code != 200:
                    logger.warning(f"API returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error connecting to API: {e}")
            raise ConnectionError(
                f"Could not connect to API at {self.base_url}. Make sure the API server is running."
            )

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.

        Returns:
            List of model information dictionaries
        """
        try:
            if self.use_client_library:
                models = self.client.models.list()
                return [model.model_dump() for model in models.data]
            else:
                response = self.session.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()
                return data.get("data", [])

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise
