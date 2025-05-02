"""
API Key service for the pAIssive Income API.

This module provides a service for managing API keys.
"""

from typing import Any, Dict

from .base import BaseService


class APIKeyService(BaseService):
    """
    API Key service.
    """

    def create_api_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new API key.

        Args:
            data: API key creation data
                - name: Name of the API key
                - description: Description of the API key
                - expires_at: Optional expiration date (ISO format)
                - scopes: Optional list of permission scopes

        Returns:
            Created API key data (including the actual key, which is only returned once)
        """
        return self._post("api-keys", data)

    def get_api_keys(self) -> Dict[str, Any]:
        """
        Get all API keys for the current user.

        Returns:
            List of API keys
        """
        return self._get("api-keys")

    def get_api_key(self, api_key_id: str) -> Dict[str, Any]:
        """
        Get details for a specific API key.

        Args:
            api_key_id: API key ID

        Returns:
            API key details (excluding the actual key)
        """
        return self._get(f"api-keys/{api_key_id}")

    def update_api_key(self, api_key_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an API key.

        Args:
            api_key_id: API key ID
            data: Updated API key data
                - name: Name of the API key
                - description: Description of the API key
                - scopes: List of permission scopes

        Returns:
            Updated API key details
        """
        return self._put(f"api-keys/{api_key_id}", data)

    def delete_api_key(self, api_key_id: str) -> Dict[str, Any]:
        """
        Delete an API key.

        Args:
            api_key_id: API key ID

        Returns:
            Result of the deletion
        """
        return self._delete(f"api-keys/{api_key_id}")

    def revoke_api_key(self, api_key_id: str) -> Dict[str, Any]:
        """
        Revoke an API key.

        Args:
            api_key_id: API key ID

        Returns:
            Result of the revocation
        """
        return self._post(f"api-keys/{api_key_id}/revoke", {})

    def get_api_key_scopes(self) -> Dict[str, Any]:
        """
        Get all available API key scopes.

        Returns:
            List of available scopes
        """
        return self._get("api-keys/scopes")
