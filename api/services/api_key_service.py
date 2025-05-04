"""
"""
API key service for the API server.
API key service for the API server.


This module provides services for API key management.
This module provides services for API key management.
"""
"""




import logging
import logging
from typing import List, Optional
from typing import List, Optional


from ..models.api_key import APIKey
from ..models.api_key import APIKey
from ..repositories.api_key_repository import APIKeyRepository
from ..repositories.api_key_repository import APIKeyRepository
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate


# Configure logger
# Configure logger
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class APIKeyService:
    class APIKeyService:
    """
    """
    Service for API key management.
    Service for API key management.
    """
    """


    def __init__(self, repository: Optional[APIKeyRepository] = None):
    def __init__(self, repository: Optional[APIKeyRepository] = None):
    """
    """
    Initialize the API key service.
    Initialize the API key service.


    Args:
    Args:
    repository: API key repository
    repository: API key repository
    """
    """
    self.repository = repository or APIKeyRepository()
    self.repository = repository or APIKeyRepository()


    def create_api_key(
    def create_api_key(
    self, data: APIKeyCreate, user_id: Optional[str] = None
    self, data: APIKeyCreate, user_id: Optional[str] = None
    ) -> APIKey:
    ) -> APIKey:
    """
    """
    Create a new API key.
    Create a new API key.


    Args:
    Args:
    data: API key creation data
    data: API key creation data
    user_id: ID of the user who owns the API key
    user_id: ID of the user who owns the API key


    Returns:
    Returns:
    Created API key
    Created API key
    """
    """
    # Create API key instance
    # Create API key instance
    api_key = APIKey(
    api_key = APIKey(
    name=data.name,
    name=data.name,
    description=data.description,
    description=data.description,
    expires_at=data.expires_at,
    expires_at=data.expires_at,
    scopes=data.scopes,
    scopes=data.scopes,
    user_id=user_id,
    user_id=user_id,
    )
    )


    # Create API key in repository
    # Create API key in repository
    return self.repository.create(api_key)
    return self.repository.create(api_key)


    def get_api_key(self, api_key_id: str) -> Optional[APIKey]:
    def get_api_key(self, api_key_id: str) -> Optional[APIKey]:
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
    return self.repository.get_by_id(api_key_id)
    return self.repository.get_by_id(api_key_id)


    def get_api_keys_by_user(self, user_id: str) -> List[APIKey]:
    def get_api_keys_by_user(self, user_id: str) -> List[APIKey]:
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
    return self.repository.get_by_user_id(user_id)
    return self.repository.get_by_user_id(user_id)


    def get_all_api_keys(self) -> List[APIKey]:
    def get_all_api_keys(self) -> List[APIKey]:
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
    return self.repository.get_all()
    return self.repository.get_all()


    def update_api_key(self, api_key_id: str, data: APIKeyUpdate) -> Optional[APIKey]:
    def update_api_key(self, api_key_id: str, data: APIKeyUpdate) -> Optional[APIKey]:
    """
    """
    Update an API key.
    Update an API key.


    Args:
    Args:
    api_key_id: API key ID
    api_key_id: API key ID
    data: API key update data
    data: API key update data


    Returns:
    Returns:
    Updated API key if found, None otherwise
    Updated API key if found, None otherwise
    """
    """
    # Get API key
    # Get API key
    api_key = self.repository.get_by_id(api_key_id)
    api_key = self.repository.get_by_id(api_key_id)


    # Check if API key exists
    # Check if API key exists
    if not api_key:
    if not api_key:
    return None
    return None


    # Update API key fields
    # Update API key fields
    if data.name is not None:
    if data.name is not None:
    api_key.name = data.name
    api_key.name = data.name
    if data.description is not None:
    if data.description is not None:
    api_key.description = data.description
    api_key.description = data.description
    if data.expires_at is not None:
    if data.expires_at is not None:
    api_key.expires_at = data.expires_at
    api_key.expires_at = data.expires_at
    if data.scopes is not None:
    if data.scopes is not None:
    api_key.scopes = data.scopes
    api_key.scopes = data.scopes
    if data.is_active is not None:
    if data.is_active is not None:
    api_key.is_active = data.is_active
    api_key.is_active = data.is_active


    # Update API key in repository
    # Update API key in repository
    return self.repository.update(api_key)
    return self.repository.update(api_key)


    def delete_api_key(self, api_key_id: str) -> bool:
    def delete_api_key(self, api_key_id: str) -> bool:
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
    return self.repository.delete(api_key_id)
    return self.repository.delete(api_key_id)


    def verify_api_key(self, key: str) -> Optional[APIKey]:
    def verify_api_key(self, key: str) -> Optional[APIKey]:
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
    return self.repository.verify_key(key)
    return self.repository.verify_key(key)


    def revoke_api_key(self, api_key_id: str) -> Optional[APIKey]:
    def revoke_api_key(self, api_key_id: str) -> Optional[APIKey]:
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
    Revoked API key if found, None otherwise
    Revoked API key if found, None otherwise
    """
    """
    # Get API key
    # Get API key
    api_key = self.repository.get_by_id(api_key_id)
    api_key = self.repository.get_by_id(api_key_id)


    # Check if API key exists
    # Check if API key exists
    if not api_key:
    if not api_key:
    return None
    return None


    # Revoke API key
    # Revoke API key
    api_key.is_active = False
    api_key.is_active = False


    # Update API key in repository
    # Update API key in repository
    return self.repository.update(api_key)
    return self.repository.update(api_key)


    def check_api_key_permissions(
    def check_api_key_permissions(
    self, api_key: APIKey, required_scopes: List[str]
    self, api_key: APIKey, required_scopes: List[str]
    ) -> bool:
    ) -> bool:
    """
    """
    Check if an API key has the required permissions.
    Check if an API key has the required permissions.


    Args:
    Args:
    api_key: API key
    api_key: API key
    required_scopes: Required scopes
    required_scopes: Required scopes


    Returns:
    Returns:
    True if the API key has the required permissions, False otherwise
    True if the API key has the required permissions, False otherwise
    """
    """
    # Check if API key is valid
    # Check if API key is valid
    if not api_key.is_valid():
    if not api_key.is_valid():
    return False
    return False


    # Check if API key has all required scopes
    # Check if API key has all required scopes
    for scope in required_scopes:
    for scope in required_scopes:
    if scope not in api_key.scopes:
    if scope not in api_key.scopes:
    return False
    return False


    return True
    return True