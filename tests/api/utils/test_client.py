"""
Test client utilities for API tests.

This module provides utilities for making requests to the API in tests.
"""

from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

class APITestClient:
    """
    Test client for API tests.

    This class provides methods for making requests to the API in tests.
    """

    def __init__(self, client: TestClient, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the API test client.

        Args:
            client: FastAPI test client
            headers: Default headers for requests
        """
        self.client = client
        self.headers = headers or {}
        self.base_url = " / api / v1"  # Default to v1

    def set_version(self, version: str) -> None:
        """
        Set the API version for requests.

        Args:
            version: API version (e.g., "v1", "v2")
        """
        self.base_url = f" / api/{version}"

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make a GET request to the API.

        Args:
            path: API path (without base URL)
            params: Query parameters
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.get(url, params=params, headers=request_headers)

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make a POST request to the API.

        Args:
            path: API path (without base URL)
            data: Request data (used if json is not provided)
            headers: Request headers (overrides default headers)
            json: JSON data to send (takes precedence over data)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}"
        request_headers = {**self.headers, **(headers or {})}
        if json is not None:
            return self.client.post(url, json=json, headers=request_headers)
        return self.client.post(url, json=data, headers=request_headers)

    def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make a PUT request to the API.

        Args:
            path: API path (without base URL)
            data: Request data
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.put(url, json=data, headers=request_headers)

    def patch(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make a PATCH request to the API.

        Args:
            path: API path (without base URL)
            data: Request data
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.patch(url, json=data, headers=request_headers)

    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make a DELETE request to the API.

        Args:
            path: API path (without base URL)
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.delete(url, headers=request_headers)

    def bulk_create(
        self, path: str, items: List[Dict[str, Any]], headers: Optional[Dict[str, 
            str]] = None
    ) -> Any:
        """
        Make a bulk create request to the API.

        Args:
            path: API path (without base URL)
            items: List of items to create
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}/bulk"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.post(url, json={"items": items}, headers=request_headers)

    def bulk_update(
        self, path: str, items: List[Dict[str, Any]], headers: Optional[Dict[str, 
            str]] = None
    ) -> Any:
        """
        Make a bulk update request to the API.

        Args:
            path: API path (without base URL)
            items: List of items to update
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}/bulk"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.put(url, json={"items": items}, headers=request_headers)

    def bulk_delete(
        self, path: str, ids: List[str], headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a bulk delete request to the API.

        Args:
            path: API path (without base URL)
            ids: List of IDs to delete
            headers: Request headers (overrides default headers)

        Returns:
            Response from the API
        """
        url = f"{self.base_url}/{path.lstrip(' / ')}/bulk"
        request_headers = {**self.headers, **(headers or {})}
        return self.client.delete(url, json={"ids": ids}, headers=request_headers)

@pytest.fixture
def api_test_client(api_client: TestClient, api_unauth_headers: Dict[str, 
    str]) -> APITestClient:
    """
    Create an unauthenticated API test client.

    Args:
        api_client: FastAPI test client
        api_unauth_headers: Default headers for unauthenticated requests

    Returns:
        Unauthenticated API test client
    """
    return APITestClient(api_client, api_unauth_headers)

@pytest.fixture
def auth_api_test_client(api_client: TestClient, api_auth_headers: Dict[str, 
    str]) -> APITestClient:
    """
    Create an authenticated API test client.

    Args:
        api_client: FastAPI test client
        api_auth_headers: Default headers for authenticated requests

    Returns:
        Authenticated API test client
    """
    return APITestClient(api_client, api_auth_headers)
