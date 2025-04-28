"""
API key models for the API server.

This module provides models for API key storage and management.
"""

import uuid
import secrets
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Set

# Configure logger
logger = logging.getLogger(__name__)


class APIKey:
    """
    Model for API key.
    """
    
    # API key prefix length
    PREFIX_LENGTH = 8
    
    # API key format
    KEY_PREFIX = "sk_"
    
    # API key length (not including prefix)
    KEY_LENGTH = 32
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        scopes: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_used_at: Optional[datetime] = None,
        is_active: bool = True
    ):
        """
        Initialize an API key.
        
        Args:
            name: Name of the API key
            description: Description of the API key
            expires_at: Expiration date of the API key
            scopes: Scopes (permissions) for the API key
            user_id: ID of the user who owns the API key
            id: Unique identifier for the API key
            created_at: Creation timestamp
            last_used_at: Last usage timestamp
            is_active: Whether the API key is active
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.expires_at = expires_at
        self.scopes = scopes or []
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.last_used_at = last_used_at
        self.is_active = is_active
        
        # Key-related fields (set when generating a key)
        self.key = None
        self.prefix = None
        self.key_hash = None
    
    @classmethod
    def generate_key(cls) -> str:
        """
        Generate a new API key.
        
        Returns:
            API key string
        """
        # Generate random key
        key = secrets.token_hex(cls.KEY_LENGTH)
        
        # Add prefix
        return f"{cls.KEY_PREFIX}{key}"
    
    @classmethod
    def get_prefix(cls, key: str) -> str:
        """
        Get the prefix of an API key.
        
        Args:
            key: API key
            
        Returns:
            API key prefix
        """
        # Remove the key prefix (e.g., "sk_")
        key_without_prefix = key[len(cls.KEY_PREFIX):]
        
        # Return the first PREFIX_LENGTH characters
        return f"{cls.KEY_PREFIX}{key_without_prefix[:cls.PREFIX_LENGTH]}"
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            key: API key
            
        Returns:
            Hashed API key
        """
        # Use SHA-256 for hashing
        return hashlib.sha256(key.encode()).hexdigest()
    
    def create_key(self) -> str:
        """
        Create a new API key for this instance.
        
        Returns:
            API key string
        """
        # Generate key
        self.key = self.generate_key()
        
        # Set prefix
        self.prefix = self.get_prefix(self.key)
        
        # Hash key for storage
        self.key_hash = self.hash_key(self.key)
        
        return self.key
    
    def verify_key(self, key: str) -> bool:
        """
        Verify if a key matches this API key.
        
        Args:
            key: API key to verify
            
        Returns:
            True if the key matches, False otherwise
        """
        # Hash the provided key
        key_hash = self.hash_key(key)
        
        # Compare with stored hash
        return key_hash == self.key_hash
    
    def is_valid(self) -> bool:
        """
        Check if the API key is valid (not expired and active).
        
        Returns:
            True if the API key is valid, False otherwise
        """
        # Check if the key is active
        if not self.is_active:
            return False
        
        # Check if the key has expired
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def update_last_used(self) -> None:
        """
        Update the last used timestamp.
        """
        self.last_used_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the API key to a dictionary.
        
        Returns:
            Dictionary representation of the API key
        """
        return {
            "id": self.id,
            "prefix": self.prefix,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used_at": self.last_used_at,
            "scopes": self.scopes,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "key_hash": self.key_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIKey':
        """
        Create an API key from a dictionary.
        
        Args:
            data: Dictionary representation of the API key
            
        Returns:
            API key instance
        """
        api_key = cls(
            name=data["name"],
            description=data.get("description"),
            expires_at=data.get("expires_at"),
            scopes=data.get("scopes", []),
            user_id=data.get("user_id"),
            id=data["id"],
            created_at=data["created_at"],
            last_used_at=data.get("last_used_at"),
            is_active=data.get("is_active", True)
        )
        
        # Set key-related fields
        api_key.prefix = data.get("prefix")
        api_key.key_hash = data.get("key_hash")
        
        return api_key
