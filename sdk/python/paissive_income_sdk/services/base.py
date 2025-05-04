"""
Base service class for the pAIssive Income API.

This module provides a base service class that all other service classes inherit from.
"""

from typing import Any, Dict, Optional

class BaseService:
    """
    Base service class.
    """

    def __init__(self, client):
        """
        Initialize the service.

        Args:
            client: API client
        """
        self.client = client

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, 
        Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        return self.client.get(endpoint, params=params)

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint
            data: Request body

        Returns:
            Response data
        """
        return self.client.post(endpoint, data=data)

    def _put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint
            data: Request body

        Returns:
            Response data
        """
        return self.client.put(endpoint, data=data)

    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request.

        Args:
            endpoint: API endpoint

        Returns:
            Response data
        """
        return self.client.delete(endpoint)
