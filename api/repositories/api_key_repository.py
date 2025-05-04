"""
"""
API key repository for the API server.
API key repository for the API server.


This module provides a repository for API key storage and retrieval.
This module provides a repository for API key storage and retrieval.
"""
"""




import json
import json
import logging
import logging
import os
import os
from typing import Dict, List, Optional
from typing import Dict, List, Optional


from ..models.api_key import APIKey
from ..models.api_key import APIKey


# Configure logger
# Configure logger
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class APIKeyRepository:
    class APIKeyRepository:
    """
    """
    Repository for API key storage and retrieval.
    Repository for API key storage and retrieval.


    This implementation uses a JSON file for storage.
    This implementation uses a JSON file for storage.
    In a production environment, this would use a database.
    In a production environment, this would use a database.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the API key repository.
    Initialize the API key repository.


    Args:
    Args:
    storage_path: Path to the storage file
    storage_path: Path to the storage file
    """
    """
    # Set default storage path if not provided
    # Set default storage path if not provided
    if storage_path is None:
    if storage_path is None:
    # Use ~/.pAIssive_income/api_keys.json as default
    # Use ~/.pAIssive_income/api_keys.json as default
    home_dir = os.path.expanduser("~")
    home_dir = os.path.expanduser("~")
    storage_dir = os.path.join(home_dir, ".pAIssive_income")
    storage_dir = os.path.join(home_dir, ".pAIssive_income")


    # Create directory if it doesn't exist
    # Create directory if it doesn't exist
    os.makedirs(storage_dir, exist_ok=True)
    os.makedirs(storage_dir, exist_ok=True)


    storage_path = os.path.join(storage_dir, "api_keys.json")
    storage_path = os.path.join(storage_dir, "api_keys.json")


    self.storage_path = storage_path
    self.storage_path = storage_path
    self.api_keys: Dict[str, APIKey] = {}
    self.api_keys: Dict[str, APIKey] = {}
    self.key_to_id: Dict[str, str] = {}
    self.key_to_id: Dict[str, str] = {}


    # Create directory if it doesn't exist
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)


    # Load API keys from storage
    # Load API keys from storage
    self._load()
    self._load()


    def _load(self) -> None:
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
    """
    Create a new API key.
    Create a new API key.


    Args:
    Args:
    api_key: API key to create
    api_key: API key to create


    Returns:
    Returns:
    Created API key
    Created API key
    """
    """
    # Store API key
    # Store API key
    self.api_keys[api_key.id] = api_key
    self.api_keys[api_key.id] = api_key
    if api_key.key:
    if api_key.key:
    self.key_to_id[api_key.key] = api_key.id
    self.key_to_id[api_key.key] = api_key.id


    # Save to storage
    # Save to storage
    self._save()
    self._save()


    return api_key
    return api_key


    def get_by_id(self, api_key_id: str) -> Optional[APIKey]:
    def get_by_id(self, api_key_id: str) -> Optional[APIKey]:
    """
    """
    Get an API key by ID.
    Get an API key by ID.


    Args:
    Args:
    api_key_id: API key ID
    api_key_id: API key ID


    Returns:
    Returns:
    API key if found, None otherwise
    API key if found, None otherwise
    """
    """
    return self.api_keys.get(api_key_id)
    return self.api_keys.get(api_key_id)


    def get_by_key(self, key: str) -> Optional[APIKey]:
    def get_by_key(self, key: str) -> Optional[APIKey]:
    """
    """
    Get an API key by key value.
    Get an API key by key value.


    Args:
    Args:
    key: API key value
    key: API key value


    Returns:
    Returns:
    API key if found, None otherwise
    API key if found, None otherwise
    """
    """
    api_key_id = self.key_to_id.get(key)
    api_key_id = self.key_to_id.get(key)


    if not api_key_id:
    if not api_key_id:
    # Try to find by key hash if not found in key_to_id mapping
    # Try to find by key hash if not found in key_to_id mapping
    key_hash = APIKey.hash_key(key)
    key_hash = APIKey.hash_key(key)
    for api_key in self.api_keys.values():
    for api_key in self.api_keys.values():
    if api_key.key_hash == key_hash:
    if api_key.key_hash == key_hash:
    return api_key
    return api_key
    return None
    return None


    return self.api_keys.get(api_key_id)
    return self.api_keys.get(api_key_id)


    def get_by_prefix(self, prefix: str) -> List[APIKey]:
    def get_by_prefix(self, prefix: str) -> List[APIKey]:
    """
    """
    Get API keys by prefix.
    Get API keys by prefix.


    Args:
    Args:
    prefix: API key prefix
    prefix: API key prefix


    Returns:
    Returns:
    List of API keys with matching prefix
    List of API keys with matching prefix
    """
    """
    return [
    return [
    api_key for api_key in self.api_keys.values() if api_key.prefix == prefix
    api_key for api_key in self.api_keys.values() if api_key.prefix == prefix
    ]
    ]


    def get_by_user_id(self, user_id: str) -> List[APIKey]:
    def get_by_user_id(self, user_id: str) -> List[APIKey]:
    """
    """
    Get API keys by user ID.
    Get API keys by user ID.


    Args:
    Args:
    user_id: User ID
    user_id: User ID


    Returns:
    Returns:
    List of API keys for the user
    List of API keys for the user
    """
    """
    return [
    return [
    api_key for api_key in self.api_keys.values() if api_key.user_id == user_id
    api_key for api_key in self.api_keys.values() if api_key.user_id == user_id
    ]
    ]


    def get_all(self) -> List[APIKey]:
    def get_all(self) -> List[APIKey]:
    """
    """
    Get all API keys.
    Get all API keys.


    Returns:
    Returns:
    List of all API keys
    List of all API keys
    """
    """
    return list(self.api_keys.values())
    return list(self.api_keys.values())


    def update(self, api_key: APIKey) -> APIKey:
    def update(self, api_key: APIKey) -> APIKey:
    """
    """
    Update an API key.
    Update an API key.


    Args:
    Args:
    api_key: API key to update
    api_key: API key to update


    Returns:
    Returns:
    Updated API key
    Updated API key
    """
    """
    # Store API key
    # Store API key
    self.api_keys[api_key.id] = api_key
    self.api_keys[api_key.id] = api_key
    if api_key.key:
    if api_key.key:
    self.key_to_id[api_key.key] = api_key.id
    self.key_to_id[api_key.key] = api_key.id


    # Save to storage
    # Save to storage
    self._save()
    self._save()


    return api_key
    return api_key


    def delete(self, api_key_id: str) -> bool:
    def delete(self, api_key_id: str) -> bool:
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
    True if the API key was deleted, False otherwise
    True if the API key was deleted, False otherwise
    """
    """
    # Check if API key exists
    # Check if API key exists
    if api_key_id not in self.api_keys:
    if api_key_id not in self.api_keys:
    return False
    return False


    # Get API key
    # Get API key
    api_key = self.api_keys[api_key_id]
    api_key = self.api_keys[api_key_id]


    # Remove API key
    # Remove API key
    del self.api_keys[api_key_id]
    del self.api_keys[api_key_id]
    if api_key.key and api_key.key in self.key_to_id:
    if api_key.key and api_key.key in self.key_to_id:
    del self.key_to_id[api_key.key]
    del self.key_to_id[api_key.key]


    # Save to storage
    # Save to storage
    self._save()
    self._save()


    return True
    return True


    def verify_key(self, key: str) -> Optional[APIKey]:
    def verify_key(self, key: str) -> Optional[APIKey]:
    """
    """
    Verify an API key.
    Verify an API key.


    Args:
    Args:
    key: API key to verify
    key: API key to verify


    Returns:
    Returns:
    API key if valid, None otherwise
    API key if valid, None otherwise
    """
    """
    # Get API key
    # Get API key
    api_key = self.get_by_key(key)
    api_key = self.get_by_key(key)


    if not api_key:
    if not api_key:
    return None
    return None


    # Check if API key is valid
    # Check if API key is valid
    if not api_key.is_valid():
    if not api_key.is_valid():
    return None
    return None


    # Update last used timestamp
    # Update last used timestamp
    api_key.update_last_used()
    api_key.update_last_used()
    self.update(api_key)
    self.update(api_key)


    return api_key
    return api_key