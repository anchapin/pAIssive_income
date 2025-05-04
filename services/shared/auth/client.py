"""
"""
Service client utilities for inter-service communication.
Service client utilities for inter-service communication.


This module provides utilities for services to communicate with each other
This module provides utilities for services to communicate with each other
using service-to-service authentication.
using service-to-service authentication.
"""
"""


import logging
import logging
import os
import os
import time
import time
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


import httpx
import httpx


from .jwt_auth import ServiceTokenError, create_service_token
from .jwt_auth import ServiceTokenError, create_service_token


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




class ServiceClient:
    class ServiceClient:
    """
    """
    Client for service-to-service communication.
    Client for service-to-service communication.


    This client handles authentication and communication between microservices.
    This client handles authentication and communication between microservices.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    service_name: str,
    service_name: str,
    api_gateway_url: Optional[str] = None,
    api_gateway_url: Optional[str] = None,
    timeout: float = 30.0,
    timeout: float = 30.0,
    ):
    ):
    """
    """
    Initialize the service client.
    Initialize the service client.


    Args:
    Args:
    service_name: Name of this service
    service_name: Name of this service
    api_gateway_url: URL of the API Gateway (default: from environment variable)
    api_gateway_url: URL of the API Gateway (default: from environment variable)
    timeout: Request timeout in seconds
    timeout: Request timeout in seconds
    """
    """
    self.service_name = service_name
    self.service_name = service_name
    self.timeout = timeout
    self.timeout = timeout


    # Get API Gateway URL from environment variable if not provided
    # Get API Gateway URL from environment variable if not provided
    if api_gateway_url is None:
    if api_gateway_url is None:
    api_gateway_url = os.environ.get("API_GATEWAY_URL", "http://localhost:8000")
    api_gateway_url = os.environ.get("API_GATEWAY_URL", "http://localhost:8000")


    self.api_gateway_url = api_gateway_url.rstrip("/")
    self.api_gateway_url = api_gateway_url.rstrip("/")


    # Create HTTP client
    # Create HTTP client
    self.client = httpx.AsyncClient(timeout=timeout)
    self.client = httpx.AsyncClient(timeout=timeout)


    async def close(self):
    async def close(self):
    """Close the HTTP client."""
    await self.client.aclose()

    async def __aenter__(self):
    """Enter async context manager."""
    return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Exit async context manager."""
    await self.close()

    async def get_service_token(
    self,
    target_service: str,
    expiration: Optional[int] = None,
    claims: Optional[Dict[str, Any]] = None,
    ) -> str:
    """
    """
    Get a service token for authenticating with another service.
    Get a service token for authenticating with another service.


    Args:
    Args:
    target_service: Name of the target service
    target_service: Name of the target service
    expiration: Token expiration time in seconds
    expiration: Token expiration time in seconds
    claims: Additional service-specific claims
    claims: Additional service-specific claims


    Returns:
    Returns:
    str: The JWT token
    str: The JWT token


    Raises:
    Raises:
    ServiceTokenError: If token creation fails
    ServiceTokenError: If token creation fails
    """
    """
    try:
    try:
    # Try to create the token locally first
    # Try to create the token locally first
    return create_service_token(
    return create_service_token(
    issuer=self.service_name,
    issuer=self.service_name,
    audience=target_service,
    audience=target_service,
    expiration=expiration,
    expiration=expiration,
    claims=claims,
    claims=claims,
    )
    )
except Exception as e:
except Exception as e:
    logger.warning(f"Failed to create service token locally: {str(e)}")
    logger.warning(f"Failed to create service token locally: {str(e)}")


    # If local creation fails, request a token from the API Gateway
    # If local creation fails, request a token from the API Gateway
    url = f"{self.api_gateway_url}/api/auth/service-token"
    url = f"{self.api_gateway_url}/api/auth/service-token"


    # Prepare request data
    # Prepare request data
    data = {"service_name": self.service_name, "target_service": target_service}
    data = {"service_name": self.service_name, "target_service": target_service}


    if expiration is not None:
    if expiration is not None:
    data["expiration"] = expiration
    data["expiration"] = expiration


    if claims is not None:
    if claims is not None:
    data["claims"] = claims
    data["claims"] = claims


    # Send request to API Gateway
    # Send request to API Gateway
    try:
    try:
    response = await self.client.post(url, json=data)
    response = await self.client.post(url, json=data)
    response.raise_for_status()
    response.raise_for_status()


    # Parse response
    # Parse response
    result = response.json()
    result = response.json()


    # Return the token
    # Return the token
    return result["token"]
    return result["token"]
except Exception as e:
except Exception as e:
    logger.error(f"Failed to get service token from API Gateway: {str(e)}")
    logger.error(f"Failed to get service token from API Gateway: {str(e)}")
    raise ServiceTokenError(f"Failed to get service token: {str(e)}")
    raise ServiceTokenError(f"Failed to get service token: {str(e)}")


    async def request(
    async def request(
    self,
    self,
    method: str,
    method: str,
    service_name: str,
    service_name: str,
    path: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    data: Optional[Any] = None,
    json_data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    timeout: Optional[float] = None,
    ) -> httpx.Response:
    ) -> httpx.Response:
    """
    """
    Send a request to another service.
    Send a request to another service.


    Args:
    Args:
    method: HTTP method (GET, POST, PUT, DELETE, etc.)
    method: HTTP method (GET, POST, PUT, DELETE, etc.)
    service_name: Name of the target service
    service_name: Name of the target service
    path: Path to request
    path: Path to request
    params: Query parameters
    params: Query parameters
    data: Request data
    data: Request data
    json_data: JSON request data
    json_data: JSON request data
    headers: Request headers
    headers: Request headers
    timeout: Request timeout in seconds
    timeout: Request timeout in seconds


    Returns:
    Returns:
    httpx.Response: The response
    httpx.Response: The response


    Raises:
    Raises:
    httpx.RequestError: If the request fails
    httpx.RequestError: If the request fails
    """
    """
    # Normalize path
    # Normalize path
    if not path.startswith("/"):
    if not path.startswith("/"):
    path = f"/{path}"
    path = f"/{path}"


    # Construct URL through the API Gateway
    # Construct URL through the API Gateway
    url = f"{self.api_gateway_url}/api/{service_name}{path}"
    url = f"{self.api_gateway_url}/api/{service_name}{path}"


    # Get service token
    # Get service token
    token = await self.get_service_token(service_name)
    token = await self.get_service_token(service_name)


    # Prepare headers
    # Prepare headers
    request_headers = headers or {}
    request_headers = headers or {}
    request_headers["X-Service-Token"] = token
    request_headers["X-Service-Token"] = token


    # Send request
    # Send request
    return await self.client.request(
    return await self.client.request(
    method=method,
    method=method,
    url=url,
    url=url,
    params=params,
    params=params,
    data=data,
    data=data,
    json=json_data,
    json=json_data,
    headers=request_headers,
    headers=request_headers,
    timeout=timeout or self.timeout,
    timeout=timeout or self.timeout,
    )
    )


    async def get(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    async def get(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    """
    Send a GET request to another service.
    Send a GET request to another service.


    Args:
    Args:
    service_name: Name of the target service
    service_name: Name of the target service
    path: Path to request
    path: Path to request
    **kwargs: Additional arguments for request()
    **kwargs: Additional arguments for request()


    Returns:
    Returns:
    httpx.Response: The response
    httpx.Response: The response
    """
    """
    return await self.request("GET", service_name, path, **kwargs)
    return await self.request("GET", service_name, path, **kwargs)


    async def post(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    async def post(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    """
    Send a POST request to another service.
    Send a POST request to another service.


    Args:
    Args:
    service_name: Name of the target service
    service_name: Name of the target service
    path: Path to request
    path: Path to request
    **kwargs: Additional arguments for request()
    **kwargs: Additional arguments for request()


    Returns:
    Returns:
    httpx.Response: The response
    httpx.Response: The response
    """
    """
    return await self.request("POST", service_name, path, **kwargs)
    return await self.request("POST", service_name, path, **kwargs)


    async def put(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    async def put(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    """
    Send a PUT request to another service.
    Send a PUT request to another service.


    Args:
    Args:
    service_name: Name of the target service
    service_name: Name of the target service
    path: Path to request
    path: Path to request
    **kwargs: Additional arguments for request()
    **kwargs: Additional arguments for request()


    Returns:
    Returns:
    httpx.Response: The response
    httpx.Response: The response
    """
    """
    return await self.request("PUT", service_name, path, **kwargs)
    return await self.request("PUT", service_name, path, **kwargs)


    async def delete(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    async def delete(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    """
    Send a DELETE request to another service.
    Send a DELETE request to another service.


    Args:
    Args:
    service_name: Name of the target service
    service_name: Name of the target service
    path: Path to request
    path: Path to request
    **kwargs: Additional arguments for request()
    **kwargs: Additional arguments for request()


    Returns:
    Returns:
    httpx.Response: The response
    httpx.Response: The response
    """
    """
    return await self.request("DELETE", service_name, path, **kwargs)
    return await self.request("DELETE", service_name, path, **kwargs)