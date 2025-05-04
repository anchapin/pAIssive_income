"""
"""
Test client utilities for API tests.
Test client utilities for API tests.


This module provides utilities for making requests to the API in tests.
This module provides utilities for making requests to the API in tests.
"""
"""




from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


import pytest
import pytest
from fastapi.testclient import TestClient
from fastapi.testclient import TestClient




class APITestClient:
    class APITestClient:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Test client for API tests.
    Test client for API tests.


    This class provides methods for making requests to the API in tests.
    This class provides methods for making requests to the API in tests.
    """
    """


    def __init__(self, client: TestClient, headers: Optional[Dict[str, str]] = None):
    def __init__(self, client: TestClient, headers: Optional[Dict[str, str]] = None):
    """
    """
    Initialize the API test client.
    Initialize the API test client.


    Args:
    Args:
    client: FastAPI test client
    client: FastAPI test client
    headers: Default headers for requests
    headers: Default headers for requests
    """
    """
    self.client = client
    self.client = client
    self.headers = headers or {}
    self.headers = headers or {}
    self.base_url = "/api/v1"  # Default to v1
    self.base_url = "/api/v1"  # Default to v1


    def set_version(self, version: str) -> None:
    def set_version(self, version: str) -> None:
    """
    """
    Set the API version for requests.
    Set the API version for requests.


    Args:
    Args:
    version: API version (e.g., "v1", "v2")
    version: API version (e.g., "v1", "v2")
    """
    """
    self.base_url = f"/api/{version}"
    self.base_url = f"/api/{version}"


    def get(
    def get(
    self,
    self,
    path: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a GET request to the API.
    Make a GET request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    params: Query parameters
    params: Query parameters
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}"
    url = f"{self.base_url}/{path.lstrip('/')}"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.get(url, params=params, headers=request_headers)
    return self.client.get(url, params=params, headers=request_headers)


    def post(
    def post(
    self,
    self,
    path: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a POST request to the API.
    Make a POST request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    data: Request data (used if json is not provided)
    data: Request data (used if json is not provided)
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)
    json: JSON data to send (takes precedence over data)
    json: JSON data to send (takes precedence over data)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}"
    url = f"{self.base_url}/{path.lstrip('/')}"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    if json is not None:
    if json is not None:
    return self.client.post(url, json=json, headers=request_headers)
    return self.client.post(url, json=json, headers=request_headers)
    return self.client.post(url, json=data, headers=request_headers)
    return self.client.post(url, json=data, headers=request_headers)


    def put(
    def put(
    self,
    self,
    path: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a PUT request to the API.
    Make a PUT request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    data: Request data
    data: Request data
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}"
    url = f"{self.base_url}/{path.lstrip('/')}"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.put(url, json=data, headers=request_headers)
    return self.client.put(url, json=data, headers=request_headers)


    def patch(
    def patch(
    self,
    self,
    path: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a PATCH request to the API.
    Make a PATCH request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    data: Request data
    data: Request data
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}"
    url = f"{self.base_url}/{path.lstrip('/')}"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.patch(url, json=data, headers=request_headers)
    return self.client.patch(url, json=data, headers=request_headers)


    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Any:
    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Any:
    """
    """
    Make a DELETE request to the API.
    Make a DELETE request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}"
    url = f"{self.base_url}/{path.lstrip('/')}"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.delete(url, headers=request_headers)
    return self.client.delete(url, headers=request_headers)


    def bulk_create(
    def bulk_create(
    self,
    self,
    path: str,
    path: str,
    items: List[Dict[str, Any]],
    items: List[Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a bulk create request to the API.
    Make a bulk create request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    items: List of items to create
    items: List of items to create
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}/bulk"
    url = f"{self.base_url}/{path.lstrip('/')}/bulk"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.post(url, json={"items": items}, headers=request_headers)
    return self.client.post(url, json={"items": items}, headers=request_headers)


    def bulk_update(
    def bulk_update(
    self,
    self,
    path: str,
    path: str,
    items: List[Dict[str, Any]],
    items: List[Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a bulk update request to the API.
    Make a bulk update request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    items: List of items to update
    items: List of items to update
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}/bulk"
    url = f"{self.base_url}/{path.lstrip('/')}/bulk"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.put(url, json={"items": items}, headers=request_headers)
    return self.client.put(url, json={"items": items}, headers=request_headers)


    def bulk_delete(
    def bulk_delete(
    self, path: str, ids: List[str], headers: Optional[Dict[str, str]] = None
    self, path: str, ids: List[str], headers: Optional[Dict[str, str]] = None
    ) -> Any:
    ) -> Any:
    """
    """
    Make a bulk delete request to the API.
    Make a bulk delete request to the API.


    Args:
    Args:
    path: API path (without base URL)
    path: API path (without base URL)
    ids: List of IDs to delete
    ids: List of IDs to delete
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the API
    Response from the API
    """
    """
    url = f"{self.base_url}/{path.lstrip('/')}/bulk"
    url = f"{self.base_url}/{path.lstrip('/')}/bulk"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    return self.client.delete(url, json={"ids": ids}, headers=request_headers)
    return self.client.delete(url, json={"ids": ids}, headers=request_headers)


    def graphql_query(
    def graphql_query(
    self,
    self,
    query: str,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    variables: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a GraphQL query request.
    Make a GraphQL query request.


    Args:
    Args:
    query: GraphQL query string
    query: GraphQL query string
    variables: GraphQL variables
    variables: GraphQL variables
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the GraphQL API
    Response from the GraphQL API
    """
    """
    url = f"{self.base_url}/graphql"
    url = f"{self.base_url}/graphql"
    request_headers = {**self.headers, **(headers or {})}
    request_headers = {**self.headers, **(headers or {})}
    request_data = {"query": query}
    request_data = {"query": query}
    if variables:
    if variables:
    request_data["variables"] = variables
    request_data["variables"] = variables
    return self.client.post(url, json=request_data, headers=request_headers)
    return self.client.post(url, json=request_data, headers=request_headers)


    def graphql_mutation(
    def graphql_mutation(
    self,
    self,
    mutation: str,
    mutation: str,
    variables: Optional[Dict[str, Any]] = None,
    variables: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    ) -> Any:
    ) -> Any:
    """
    """
    Make a GraphQL mutation request.
    Make a GraphQL mutation request.


    Args:
    Args:
    mutation: GraphQL mutation string
    mutation: GraphQL mutation string
    variables: GraphQL variables
    variables: GraphQL variables
    headers: Request headers (overrides default headers)
    headers: Request headers (overrides default headers)


    Returns:
    Returns:
    Response from the GraphQL API
    Response from the GraphQL API
    """
    """
    # GraphQL mutations use the same endpoint as queries
    # GraphQL mutations use the same endpoint as queries
    return self.graphql_query(mutation, variables, headers)
    return self.graphql_query(mutation, variables, headers)




    @pytest.fixture
    @pytest.fixture
    def api_test_client(
    def api_test_client(
    api_client: TestClient, api_unauth_headers: Dict[str, str]
    api_client: TestClient, api_unauth_headers: Dict[str, str]
    ) -> APITestClient:
    ) -> APITestClient:
    """
    """
    Create an unauthenticated API test client.
    Create an unauthenticated API test client.


    Args:
    Args:
    api_client: FastAPI test client
    api_client: FastAPI test client
    api_unauth_headers: Default headers for unauthenticated requests
    api_unauth_headers: Default headers for unauthenticated requests


    Returns:
    Returns:
    Unauthenticated API test client
    Unauthenticated API test client
    """
    """
    return APITestClient(api_client, api_unauth_headers)
    return APITestClient(api_client, api_unauth_headers)




    @pytest.fixture
    @pytest.fixture
    def auth_api_test_client(
    def auth_api_test_client(
    api_client: TestClient, api_auth_headers: Dict[str, str]
    api_client: TestClient, api_auth_headers: Dict[str, str]
    ) -> APITestClient:
    ) -> APITestClient:
    """
    """
    Create an authenticated API test client.
    Create an authenticated API test client.


    Args:
    Args:
    api_client: FastAPI test client
    api_client: FastAPI test client
    api_auth_headers: Default headers for authenticated requests
    api_auth_headers: Default headers for authenticated requests


    Returns:
    Returns:
    Authenticated API test client
    Authenticated API test client
    """
    """
    return APITestClient(api_client, api_auth_headers)
    return APITestClient(api_client, api_auth_headers)