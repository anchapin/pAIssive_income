"""
API key repository for the API server.

This module provides a repository for API key storage and retrieval.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models.api_key import APIKey

# Configure logger
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
        self._api_keys: Dict[str, APIKey] = {}

        # Load API keys from storage
        self._load_api_keys()

    def _load_api_keys(self) -> None:
        """
        Load API keys from storage.
        """
        # Check if storage file exists
        if not os.path.exists(self.storage_path):
            # Create empty storage file
            self._save_api_keys()
            return

        try:
            # Load API keys from storage file
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            # Convert datetime strings to datetime objects
            for key_data in data:
                if key_data.get("created_at"):
                    key_data["created_at"] = datetime.fromisoformat(
                        key_data["created_at"]
                    )
                if key_data.get("expires_at"):
                    key_data["expires_at"] = datetime.fromisoformat(
                        key_data["expires_at"]
                    )
                if key_data.get("last_used_at"):
                    key_data["last_used_at"] = datetime.fromisoformat(
                        key_data["last_used_at"]
                    )

                # Create API key instance
                api_key = APIKey.from_dict(key_data)

                # Add to in-memory storage
                self._api_keys[api_key.id] = api_key

            logger.info(f"Loaded {len(self._api_keys)} API keys from storage")

        except Exception as e:
            logger.error(f"Failed to load API keys from storage: {e}")
            # Create empty storage file
            self._save_api_keys()

    def _save_api_keys(self) -> None:
        """
        Save API keys to storage.
        """
        try:
            # Convert API keys to dictionaries
            data = [api_key.to_dict() for api_key in self._api_keys.values()]

            # Convert datetime objects to ISO format strings
            for key_data in data:
                if key_data.get("created_at"):
                    key_data["created_at"] = key_data["created_at"].isoformat()
                if key_data.get("expires_at"):
                    key_data["expires_at"] = key_data["expires_at"].isoformat()
                if key_data.get("last_used_at"):
                    key_data["last_used_at"] = key_data["last_used_at"].isoformat()

            # Save to storage file
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self._api_keys)} API keys to storage")

        except Exception as e:
            logger.error(f"Failed to save API keys to storage: {e}")

    def create(self, api_key: APIKey) -> APIKey:
        """
        Create a new API key.

        Args:
            api_key: API key to create

        Returns:
            Created API key
        """
        # Generate a new key
        api_key.create_key()

        # Add to in-memory storage
        self._api_keys[api_key.id] = api_key

        # Save to storage
        self._save_api_keys()

        return api_key

    def get_by_id(self, api_key_id: str) -> Optional[APIKey]:
        """
        Get an API key by ID.

        Args:
            api_key_id: API key ID

        Returns:
            API key if found, None otherwise
        """
        return self._api_keys.get(api_key_id)

    def get_by_key(self, key: str) -> Optional[APIKey]:
        """
        Get an API key by key.

        Args:
            key: API key

        Returns:
            API key if found, None otherwise
        """
        # Hash the key
        key_hash = APIKey.hash_key(key)

        # Find API key with matching hash
        for api_key in self._api_keys.values():
            if api_key.key_hash == key_hash:
                return api_key

        return None

    def get_by_prefix(self, prefix: str) -> List[APIKey]:
        """
        Get API keys by prefix.

        Args:
            prefix: API key prefix

        Returns:
            List of API keys with matching prefix
        """
        return [
            api_key for api_key in self._api_keys.values() if api_key.prefix == prefix
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
            api_key for api_key in self._api_keys.values() if api_key.user_id == user_id
        ]

    def get_all(self) -> List[APIKey]:
        """
        Get all API keys.

        Returns:
            List of all API keys
        """
        return list(self._api_keys.values())

    def update(self, api_key: APIKey) -> APIKey:
        """
        Update an API key.

        Args:
            api_key: API key to update

        Returns:
            Updated API key
        """
        # Update in-memory storage
        self._api_keys[api_key.id] = api_key

        # Save to storage
        self._save_api_keys()

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
        if api_key_id not in self._api_keys:
            return False

        # Remove from in-memory storage
        del self._api_keys[api_key_id]

        # Save to storage
        self._save_api_keys()

        return True

    def verify_key(self, key: str) -> Optional[APIKey]:
        """
        Verify an API key.

        Args:
            key: API key to verify

        Returns:
            API key if valid, None otherwise
        """
        # Get API key by key
        api_key = self.get_by_key(key)

        # Check if API key exists
        if not api_key:
            return None

        # Check if API key is valid
        if not api_key.is_valid():
            return None

        # Update last used timestamp
        api_key.update_last_used()

        # Save to storage
        self._save_api_keys()

        return api_key
