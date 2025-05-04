"""
"""
Client for the pAIssive Income API.
Client for the pAIssive Income API.


This module provides a client for making requests to the pAIssive Income API.
This module provides a client for making requests to the pAIssive Income API.
"""
"""




import json
import json
import logging
import logging
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


import requests
import requests


from .auth import Auth, NoAuth
from .auth import Auth, NoAuth


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class Client:
    class Client:
    """
    """
    Client for the pAIssive Income API.
    Client for the pAIssive Income API.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    base_url: str = "http://localhost:8000/api",
    base_url: str = "http://localhost:8000/api",
    auth: Optional[Auth] = None,
    auth: Optional[Auth] = None,
    version: str = "v1",
    version: str = "v1",
    timeout: int = 60,
    timeout: int = 60,
    ):
    ):
    """
    """
    Initialize the client.
    Initialize the client.


    Args:
    Args:
    base_url: Base URL for the API
    base_url: Base URL for the API
    auth: Authentication method
    auth: Authentication method
    version: API version to use
    version: API version to use
    timeout: Request timeout in seconds
    timeout: Request timeout in seconds
    """
    """
    self.base_url = base_url.rstrip("/")
    self.base_url = base_url.rstrip("/")
    self.auth = auth or NoAuth()
    self.auth = auth or NoAuth()
    self.version = version
    self.version = version
    self.timeout = timeout
    self.timeout = timeout


    # Initialize services
    # Initialize services
    from .services import (AgentTeamService, AIModelsService,
    from .services import (AgentTeamService, AIModelsService,
    APIKeyService, DashboardService,
    APIKeyService, DashboardService,
    MarketingService, MonetizationService,
    MarketingService, MonetizationService,
    NicheAnalysisService, UserService)
    NicheAnalysisService, UserService)


    self.niche_analysis = NicheAnalysisService(self)
    self.niche_analysis = NicheAnalysisService(self)
    self.monetization = MonetizationService(self)
    self.monetization = MonetizationService(self)
    self.marketing = MarketingService(self)
    self.marketing = MarketingService(self)
    self.ai_models = AIModelsService(self)
    self.ai_models = AIModelsService(self)
    self.agent_team = AgentTeamService(self)
    self.agent_team = AgentTeamService(self)
    self.user = UserService(self)
    self.user = UserService(self)
    self.dashboard = DashboardService(self)
    self.dashboard = DashboardService(self)
    self.api_keys = APIKeyService(self)
    self.api_keys = APIKeyService(self)


    def request(
    def request(
    self,
    self,
    method: str,
    method: str,
    endpoint: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    files: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Make a request to the API.
    Make a request to the API.


    Args:
    Args:
    method: HTTP method to use
    method: HTTP method to use
    endpoint: API endpoint
    endpoint: API endpoint
    params: Query parameters
    params: Query parameters
    data: Request body
    data: Request body
    headers: Additional headers
    headers: Additional headers
    files: Files to upload
    files: Files to upload


    Returns:
    Returns:
    Response data
    Response data


    Raises:
    Raises:
    requests.exceptions.RequestException: If the request fails
    requests.exceptions.RequestException: If the request fails
    """
    """
    url = f"{self.base_url}/{self.version}/{endpoint.lstrip('/')}"
    url = f"{self.base_url}/{self.version}/{endpoint.lstrip('/')}"


    # Prepare headers
    # Prepare headers
    request_headers = {
    request_headers = {
    "Content-Type": "application/json",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept": "application/json",
    }
    }


    # Add authentication headers
    # Add authentication headers
    request_headers.update(self.auth.get_headers())
    request_headers.update(self.auth.get_headers())


    # Add additional headers
    # Add additional headers
    if headers:
    if headers:
    request_headers.update(headers)
    request_headers.update(headers)


    # Log request
    # Log request
    logger.debug(f"Making {method} request to {url}")
    logger.debug(f"Making {method} request to {url}")


    # Make request
    # Make request
    response = requests.request(
    response = requests.request(
    method=method,
    method=method,
    url=url,
    url=url,
    headers=request_headers,
    headers=request_headers,
    params=params,
    params=params,
    data=json.dumps(data) if data else None,
    data=json.dumps(data) if data else None,
    files=files,
    files=files,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )


    # Check for errors
    # Check for errors
    try:
    try:
    response.raise_for_status()
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    logger.error(f"HTTP error: {e}")
    try:
    try:
    error_data = response.json()
    error_data = response.json()
    logger.error(f"Error details: {error_data}")
    logger.error(f"Error details: {error_data}")
except ValueError:
except ValueError:
    logger.error(f"Error response: {response.text}")
    logger.error(f"Error response: {response.text}")
    raise
    raise


    # Parse response
    # Parse response
    if response.headers.get("Content-Type", "").startswith("application/json"):
    if response.headers.get("Content-Type", "").startswith("application/json"):
    return response.json()
    return response.json()
    else:
    else:
    return {"data": response.text}
    return {"data": response.text}


    def get(
    def get(
    self, endpoint: str, params: Optional[Dict[str, Any]] = None
    self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Make a GET request.
    Make a GET request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint
    params: Query parameters
    params: Query parameters


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.request("GET", endpoint, params=params)
    return self.request("GET", endpoint, params=params)


    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Make a POST request.
    Make a POST request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint
    data: Request body
    data: Request body


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.request("POST", endpoint, data=data)
    return self.request("POST", endpoint, data=data)


    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Make a PUT request.
    Make a PUT request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint
    data: Request body
    data: Request body


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.request("PUT", endpoint, data=data)
    return self.request("PUT", endpoint, data=data)


    def delete(self, endpoint: str) -> Dict[str, Any]:
    def delete(self, endpoint: str) -> Dict[str, Any]:
    """
    """
    Make a DELETE request.
    Make a DELETE request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.request("DELETE", endpoint)
    return self.request("DELETE", endpoint)