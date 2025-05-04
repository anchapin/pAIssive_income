"""
"""
API Key service for the pAIssive Income API.
API Key service for the pAIssive Income API.


This module provides a service for managing API keys.
This module provides a service for managing API keys.
"""
"""




from typing import Any, Dict
from typing import Any, Dict


from .base import BaseService
from .base import BaseService




class APIKeyService:
    class APIKeyService:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    API Key service.
    API Key service.
    """
    """


    def create_api_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
    def create_api_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Create a new API key.
    Create a new API key.


    Args:
    Args:
    data: API key creation data
    data: API key creation data
    - name: Name of the API key
    - name: Name of the API key
    - description: Description of the API key
    - description: Description of the API key
    - expires_at: Optional expiration date (ISO format)
    - expires_at: Optional expiration date (ISO format)
    - scopes: Optional list of permission scopes
    - scopes: Optional list of permission scopes


    Returns:
    Returns:
    Created API key data (including the actual key, which is only returned once)
    Created API key data (including the actual key, which is only returned once)
    """
    """
    return self._post("api-keys", data)
    return self._post("api-keys", data)


    def get_api_keys(self) -> Dict[str, Any]:
    def get_api_keys(self) -> Dict[str, Any]:
    """
    """
    Get all API keys for the current user.
    Get all API keys for the current user.


    Returns:
    Returns:
    List of API keys
    List of API keys
    """
    """
    return self._get("api-keys")
    return self._get("api-keys")


    def get_api_key(self, api_key_id: str) -> Dict[str, Any]:
    def get_api_key(self, api_key_id: str) -> Dict[str, Any]:
    """
    """
    Get details for a specific API key.
    Get details for a specific API key.


    Args:
    Args:
    api_key_id: API key ID
    api_key_id: API key ID


    Returns:
    Returns:
    API key details (excluding the actual key)
    API key details (excluding the actual key)
    """
    """
    return self._get(f"api-keys/{api_key_id}")
    return self._get(f"api-keys/{api_key_id}")


    def update_api_key(self, api_key_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    def update_api_key(self, api_key_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Update an API key.
    Update an API key.


    Args:
    Args:
    api_key_id: API key ID
    api_key_id: API key ID
    data: Updated API key data
    data: Updated API key data
    - name: Name of the API key
    - name: Name of the API key
    - description: Description of the API key
    - description: Description of the API key
    - scopes: List of permission scopes
    - scopes: List of permission scopes


    Returns:
    Returns:
    Updated API key details
    Updated API key details
    """
    """
    return self._put(f"api-keys/{api_key_id}", data)
    return self._put(f"api-keys/{api_key_id}", data)


    def delete_api_key(self, api_key_id: str) -> Dict[str, Any]:
    def delete_api_key(self, api_key_id: str) -> Dict[str, Any]:
    """
    """
    Delete an API key.
    Delete an API key.


    Args:
    Args:
    api_key_id: API key ID
    api_key_id: API key ID


    Returns:
    Returns:
    Result of the deletion
    Result of the deletion
    """
    """
    return self._delete(f"api-keys/{api_key_id}")
    return self._delete(f"api-keys/{api_key_id}")


    def revoke_api_key(self, api_key_id: str) -> Dict[str, Any]:
    def revoke_api_key(self, api_key_id: str) -> Dict[str, Any]:
    """
    """
    Revoke an API key.
    Revoke an API key.


    Args:
    Args:
    api_key_id: API key ID
    api_key_id: API key ID


    Returns:
    Returns:
    Result of the revocation
    Result of the revocation
    """
    """
    return self._post(f"api-keys/{api_key_id}/revoke", {})
    return self._post(f"api-keys/{api_key_id}/revoke", {})


    def get_api_key_scopes(self) -> Dict[str, Any]:
    def get_api_key_scopes(self) -> Dict[str, Any]:
    """
    """
    Get all available API key scopes.
    Get all available API key scopes.


    Returns:
    Returns:
    List of available scopes
    List of available scopes
    """
    """
    return self._get("api-keys/scopes")
    return self._get("api-keys/scopes")