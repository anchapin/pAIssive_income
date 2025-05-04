"""
Service client utilities for inter-service communication.

This module provides utilities for services to communicate with each other
using service-to-service authentication.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

import httpx

from .jwt_auth import ServiceTokenError, create_service_token

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServiceClient:
    """
    Client for service-to-service communication.

    This client handles authentication and communication between microservices.
    """

    def __init__(
    self,
    service_name: str,
    api_gateway_url: Optional[str] = None,
    timeout: float = 30.0,
    ):
    """
    Initialize the service client.

    Args:
    service_name: Name of this service
    api_gateway_url: URL of the API Gateway (default: from environment variable)
    timeout: Request timeout in seconds
    """
    self.service_name = service_name
    self.timeout = timeout

    # Get API Gateway URL from environment variable if not provided
    if api_gateway_url is None:
    api_gateway_url = os.environ.get("API_GATEWAY_URL", "http://localhost:8000")

    self.api_gateway_url = api_gateway_url.rstrip("/")

    # Create HTTP client
    self.client = httpx.AsyncClient(timeout=timeout)

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
    Get a service token for authenticating with another service.

    Args:
    target_service: Name of the target service
    expiration: Token expiration time in seconds
    claims: Additional service-specific claims

    Returns:
    str: The JWT token

    Raises:
    ServiceTokenError: If token creation fails
    """
    try:
    # Try to create the token locally first
    return create_service_token(
    issuer=self.service_name,
    audience=target_service,
    expiration=expiration,
    claims=claims,
    )
except Exception as e:
    logger.warning(f"Failed to create service token locally: {str(e)}")

    # If local creation fails, request a token from the API Gateway
    url = f"{self.api_gateway_url}/api/auth/service-token"

    # Prepare request data
    data = {"service_name": self.service_name, "target_service": target_service}

    if expiration is not None:
    data["expiration"] = expiration

    if claims is not None:
    data["claims"] = claims

    # Send request to API Gateway
    try:
    response = await self.client.post(url, json=data)
    response.raise_for_status()

    # Parse response
    result = response.json()

    # Return the token
    return result["token"]
except Exception as e:
    logger.error(f"Failed to get service token from API Gateway: {str(e)}")
    raise ServiceTokenError(f"Failed to get service token: {str(e)}")

    async def request(
    self,
    method: str,
    service_name: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    ) -> httpx.Response:
    """
    Send a request to another service.

    Args:
    method: HTTP method (GET, POST, PUT, DELETE, etc.)
    service_name: Name of the target service
    path: Path to request
    params: Query parameters
    data: Request data
    json_data: JSON request data
    headers: Request headers
    timeout: Request timeout in seconds

    Returns:
    httpx.Response: The response

    Raises:
    httpx.RequestError: If the request fails
    """
    # Normalize path
    if not path.startswith("/"):
    path = f"/{path}"

    # Construct URL through the API Gateway
    url = f"{self.api_gateway_url}/api/{service_name}{path}"

    # Get service token
    token = await self.get_service_token(service_name)

    # Prepare headers
    request_headers = headers or {}
    request_headers["X-Service-Token"] = token

    # Send request
    return await self.client.request(
    method=method,
    url=url,
    params=params,
    data=data,
    json=json_data,
    headers=request_headers,
    timeout=timeout or self.timeout,
    )

    async def get(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    Send a GET request to another service.

    Args:
    service_name: Name of the target service
    path: Path to request
    **kwargs: Additional arguments for request()

    Returns:
    httpx.Response: The response
    """
    return await self.request("GET", service_name, path, **kwargs)

    async def post(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    Send a POST request to another service.

    Args:
    service_name: Name of the target service
    path: Path to request
    **kwargs: Additional arguments for request()

    Returns:
    httpx.Response: The response
    """
    return await self.request("POST", service_name, path, **kwargs)

    async def put(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    Send a PUT request to another service.

    Args:
    service_name: Name of the target service
    path: Path to request
    **kwargs: Additional arguments for request()

    Returns:
    httpx.Response: The response
    """
    return await self.request("PUT", service_name, path, **kwargs)

    async def delete(self, service_name: str, path: str, **kwargs) -> httpx.Response:
    """
    Send a DELETE request to another service.

    Args:
    service_name: Name of the target service
    path: Path to request
    **kwargs: Additional arguments for request()

    Returns:
    httpx.Response: The response
    """
    return await self.request("DELETE", service_name, path, **kwargs)