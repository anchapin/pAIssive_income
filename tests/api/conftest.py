"""
Fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Generator, Dict, Any, Optional, Union
import json

from api.app import app
from api.utils.auth import create_access_token


class APITestClient:
    """
    Test client for API tests with helper methods.
    """

    def __init__(self, client: TestClient, headers: Dict[str, str] = None):
        """
        Initialize the API test client.

        Args:
            client: FastAPI test client
            headers: Default headers to include in requests
        """
        self.client = client
        self.headers = headers or {}

    def get(self, url: str, **kwargs) -> Any:
        """
        Send a GET request.

        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
        """
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return self.client.get(url, headers=headers, **kwargs)

    def post(self, url: str, json_data: Optional[Union[Dict, list]] = None, **kwargs) -> Any:
        """
        Send a POST request.

        Args:
            url: URL to request
            json_data: JSON data to send in the request body
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
        """
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return self.client.post(url, json=json_data, headers=headers, **kwargs)

    def put(self, url: str, json_data: Optional[Union[Dict, list]] = None, **kwargs) -> Any:
        """
        Send a PUT request.

        Args:
            url: URL to request
            json_data: JSON data to send in the request body
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
        """
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return self.client.put(url, json=json_data, headers=headers, **kwargs)

    def delete(self, url: str, **kwargs) -> Any:
        """
        Send a DELETE request.

        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
        """
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return self.client.delete(url, headers=headers, **kwargs)

    def patch(self, url: str, json_data: Optional[Union[Dict, list]] = None, **kwargs) -> Any:
        """
        Send a PATCH request.

        Args:
            url: URL to request
            json_data: JSON data to send in the request body
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
        """
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return self.client.patch(url, json=json_data, headers=headers, **kwargs)
    
    def bulk_create(self, url: str, items: list, **kwargs) -> Any:
        """
        Send a bulk create request.

        Args:
            url: URL to request
            items: List of items to create
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
        """
        return self.post(url + "/bulk", json_data=items, **kwargs)


@pytest.fixture
def api_client() -> TestClient:
    """
    Create a FastAPI test client.

    Returns:
        FastAPI test client
    """
    return TestClient(app)


@pytest.fixture
def api_headers() -> Dict[str, str]:
    """
    Create default headers for API requests.

    Returns:
        Default headers
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


@pytest.fixture
def api_auth_headers() -> Dict[str, str]:
    """
    Create authenticated headers for API requests.

    Returns:
        Authenticated headers
    """
    # Create a test user and token
    user_data = {
        "id": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "role": "admin",
    }
    token = create_access_token(data=user_data)
    
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
def api_test_client(api_client: TestClient, api_headers: Dict[str, str]) -> APITestClient:
    """
    Create an API test client.

    Args:
        api_client: FastAPI test client
        api_headers: Default headers

    Returns:
        API test client
    """
    return APITestClient(api_client, api_headers)


@pytest.fixture
def auth_api_test_client(api_client: TestClient, api_auth_headers: Dict[str, str]) -> APITestClient:
    """
    Create an authenticated API test client.

    Args:
        api_client: FastAPI test client
        api_auth_headers: Authenticated headers

    Returns:
        Authenticated API test client
    """
    return APITestClient(api_client, api_auth_headers)


def generate_id() -> str:
    """
    Generate a random ID for testing.

    Returns:
        Random ID
    """
    import uuid
    return str(uuid.uuid4())
