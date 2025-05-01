"""
API key repository for the API server.

This module provides a repository for API key storage and retrieval.
"""

import logging
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.api_key import APIKey

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeyRepository:
    """
    Repository for API key storage and retrieval.

    This implementation uses a JSON file for storage.
    In a production environment, this would use a database.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the API key repository.

        Args:
            storage_path: Path to the storage file
        """
        # Set default storage path if not provided
        if storage_path is None:
            # Use ~/.pAIssive_income/api_keys.json as default
            home_dir = os.path.expanduser("~")
            storage_dir = os.path.join(home_dir, ".pAIssive_income")

            # Create directory if it doesn't exist
            os.makedirs(storage_dir, exist_ok=True)

            storage_path = os.path.join(storage_dir, "api_keys.json")

        self.storage_path = storage_path
        self.api_keys: Dict[str, APIKey] = {}
        self.key_to_id: Dict[str, str] = {}

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # Load API keys from storage
        self._load()

    def _load(self) -> None:
        """Load API keys from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    data = json.load(f)

                for api_key_data in data:
                    api_key = APIKey.from_dict(api_key_data)
                    self.api_keys[api_key.id] = api_key
                    if api_key.key:
                        self.key_to_id[api_key.key] = api_key.id

                logger.info(f"Loaded {len(self.api_keys)} API keys from storage")
        except Exception as e:
            logger.error(f"Error loading API keys: {str(e)}")
            # Create empty storage file
            self._save()

    def _save(self) -> None:
        """Save API keys to storage."""
        try:
            data = [api_key.to_dict() for api_key in self.api_keys.values()]

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.api_keys)} API keys to storage")
        except Exception as e:
            logger.error(f"Error saving API keys: {str(e)}")

    def create(self, api_key: APIKey) -> APIKey:
        """
        Create a new API key.

        Args:
            api_key: API key to create

        Returns:
            Created API key
        """
        # Store API key
        self.api_keys[api_key.id] = api_key
        if api_key.key:
            self.key_to_id[api_key.key] = api_key.id

        # Save to storage
        self._save()

        return api_key

    def get_by_id(self, api_key_id: str) -> Optional[APIKey]:
        """
        Get an API key by ID.

        Args:
            api_key_id: API key ID

        Returns:
            API key if found, None otherwise
        """
        return self.api_keys.get(api_key_id)

    def get_by_key(self, key: str) -> Optional[APIKey]:
        """
        Get an API key by key value.

        Args:
            key: API key value

        Returns:
            API key if found, None otherwise
        """
        api_key_id = self.key_to_id.get(key)

        if not api_key_id:
            # Try to find by key hash if not found in key_to_id mapping
            key_hash = APIKey.hash_key(key)
            for api_key in self.api_keys.values():
                if api_key.key_hash == key_hash:
                    return api_key
            return None

        return self.api_keys.get(api_key_id)

    def get_by_prefix(self, prefix: str) -> List[APIKey]:
        """
        Get API keys by prefix.

        Args:
            prefix: API key prefix

        Returns:
            List of API keys with matching prefix
        """
        return [
            api_key for api_key in self.api_keys.values() if api_key.prefix == prefix
        ]

    def get_by_user_id(self, user_id: str) -> List[APIKey]:
        """
        Get API keys by user ID.

        Args:
            user_id: User ID

        Returns:
            List of API keys for the user
        """
        return [
            api_key for api_key in self.api_keys.values()
            if api_key.user_id == user_id
        ]

    def get_all(self) -> List[APIKey]:
        """
        Get all API keys.

        Returns:
            List of all API keys
        """
        return list(self.api_keys.values())

    def update(self, api_key: APIKey) -> APIKey:
        """
        Update an API key.

        Args:
            api_key: API key to update

        Returns:
            Updated API key
        """
        # Store API key
        self.api_keys[api_key.id] = api_key
        if api_key.key:
            self.key_to_id[api_key.key] = api_key.id

        # Save to storage
        self._save()

        return api_key

    def delete(self, api_key_id: str) -> bool:
        """
        Delete an API key.

        Args:
            api_key_id: API key ID

        Returns:
            True if the API key was deleted, False otherwise
        """
        # Check if API key exists
        if api_key_id not in self.api_keys:
            return False

        # Get API key
        api_key = self.api_keys[api_key_id]

        # Remove API key
        del self.api_keys[api_key_id]
        if api_key.key and api_key.key in self.key_to_id:
            del self.key_to_id[api_key.key]

        # Save to storage
        self._save()

        return True

    def verify_key(self, key: str) -> Optional[APIKey]:
        """
        Verify an API key.

        Args:
            key: API key to verify

        Returns:
            API key if valid, None otherwise
        """
        # Get API key
        api_key = self.get_by_key(key)

        if not api_key:
            return None

        # Check if API key is valid
        if not api_key.is_valid():
            return None

        # Update last used timestamp
        api_key.update_last_used()
        self.update(api_key)

        return api_key
