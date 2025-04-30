"""
API key service for the API server.

This module provides services for API key management.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models.api_key import APIKey
from ..repositories.api_key_repository import APIKeyRepository
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate

# Configure logger
logger = logging.getLogger(__name__)


class APIKeyService:
    """
    Service for API key management.
    """

    def __init__(self, repository: Optional[APIKeyRepository] = None):
        """
        Initialize the API key service.

        Args:
            repository: API key repository
        """
        self.repository = repository or APIKeyRepository()

    def create_api_key(
        self, data: APIKeyCreate, user_id: Optional[str] = None
    ) -> APIKey:
        """
        Create a new API key.

        Args:
            data: API key creation data
            user_id: ID of the user who owns the API key

        Returns:
            Created API key
        """
        # Create API key instance
        api_key = APIKey(
            name=data.name,
            description=data.description,
            expires_at=data.expires_at,
            scopes=data.scopes,
            user_id=user_id,
        )

        # Create API key in repository
        return self.repository.create(api_key)

    def get_api_key(self, api_key_id: str) -> Optional[APIKey]:
        """
        Get an API key by ID.

        Args:
            api_key_id: API key ID

        Returns:
            API key if found, None otherwise
        """
        return self.repository.get_by_id(api_key_id)

    def get_api_keys_by_user(self, user_id: str) -> List[APIKey]:
        """
        Get API keys by user ID.

        Args:
            user_id: User ID

        Returns:
            List of API keys for the user
        """
        return self.repository.get_by_user_id(user_id)

    def get_all_api_keys(self) -> List[APIKey]:
        """
        Get all API keys.

        Returns:
            List of all API keys
        """
        return self.repository.get_all()

    def update_api_key(self, api_key_id: str, data: APIKeyUpdate) -> Optional[APIKey]:
        """
        Update an API key.

        Args:
            api_key_id: API key ID
            data: API key update data

        Returns:
            Updated API key if found, None otherwise
        """
        # Get API key
        api_key = self.repository.get_by_id(api_key_id)

        # Check if API key exists
        if not api_key:
            return None

        # Update API key fields
        if data.name is not None:
            api_key.name = data.name
        if data.description is not None:
            api_key.description = data.description
        if data.expires_at is not None:
            api_key.expires_at = data.expires_at
        if data.scopes is not None:
            api_key.scopes = data.scopes
        if data.is_active is not None:
            api_key.is_active = data.is_active

        # Update API key in repository
        return self.repository.update(api_key)

    def delete_api_key(self, api_key_id: str) -> bool:
        """
        Delete an API key.

        Args:
            api_key_id: API key ID

        Returns:
            True if the API key was deleted, False otherwise
        """
        return self.repository.delete(api_key_id)

    def verify_api_key(self, key: str) -> Optional[APIKey]:
        """
        Verify an API key.

        Args:
            key: API key to verify

        Returns:
            API key if valid, None otherwise
        """
        return self.repository.verify_key(key)

    def revoke_api_key(self, api_key_id: str) -> Optional[APIKey]:
        """
        Revoke an API key.

        Args:
            api_key_id: API key ID

        Returns:
            Revoked API key if found, None otherwise
        """
        # Get API key
        api_key = self.repository.get_by_id(api_key_id)

        # Check if API key exists
        if not api_key:
            return None

        # Revoke API key
        api_key.is_active = False

        # Update API key in repository
        return self.repository.update(api_key)

    def check_api_key_permissions(
        self, api_key: APIKey, required_scopes: List[str]
    ) -> bool:
        """
        Check if an API key has the required permissions.

        Args:
            api_key: API key
            required_scopes: Required scopes

        Returns:
            True if the API key has the required permissions, False otherwise
        """
        # Check if API key is valid
        if not api_key.is_valid():
            return False

        # Check if API key has all required scopes
        for scope in required_scopes:
            if scope not in api_key.scopes:
                return False

        return True
