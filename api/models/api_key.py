"""
API key model for the API server.

This module provides the API key model for API key management.
"""


import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


class APIKey:
    """
    Model for API key.

    This class represents an API key with various attributes and methods
    for key generation, validation, and management.
    """

    # API key prefix length
    PREFIX_LENGTH = 8

    # API key format
    KEY_PREFIX = "pik_"

    # API key length (not including prefix)
    KEY_LENGTH = 32

    def __init__(
        self,
        id: Optional[str] = None,
        key: Optional[str] = None,
        name: str = "",
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        scopes: List[str] = None,
        is_active: bool = True,
        expires_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        last_used_at: Optional[datetime] = None,
    ):
        """
        Initialize an API key.

        Args:
            id: API key ID
            key: API key value
            name: API key name
            description: API key description
            user_id: ID of the user who owns the API key
            scopes: List of scopes the API key has access to
            is_active: Whether the API key is active
            expires_at: Expiration timestamp
            created_at: Creation timestamp
            last_used_at: Last usage timestamp
        """
        self.id = id or str(uuid4())
        self.key = key or self._generate_key()
        self.name = name
        self.description = description
        self.user_id = user_id
        self.scopes = scopes or ["read"]
        self.is_active = is_active
        self.expires_at = expires_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_used_at = last_used_at

        # Key-related fields for secure storage
        self.prefix = self.get_prefix(self.key) if self.key else None
        self.key_hash = self.hash_key(self.key) if self.key else None

    def _generate_key(self) -> str:
        """
        Generate a new API key.

        Returns:
            Generated API key
        """
        # Generate a 32-byte random token
                return f"{self.KEY_PREFIX}{secrets.token_urlsafe(self.KEY_LENGTH)}"

    @classmethod
    def get_prefix(cls, key: str) -> str:
        """
        Get the prefix of an API key.

        Args:
            key: API key

        Returns:
            API key prefix
        """
        # Remove the key prefix
        if key.startswith(cls.KEY_PREFIX):
            key_without_prefix = key[len(cls.KEY_PREFIX) :]
            # Return the first PREFIX_LENGTH characters
                    return f"{cls.KEY_PREFIX}{key_without_prefix[:cls.PREFIX_LENGTH]}"
                return key[: cls.PREFIX_LENGTH]

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
                return hashlib.sha256(key.encode()).hexdigest() if key else None

    def is_valid(self) -> bool:
        """
        Check if the API key is valid (not expired and active).

        Returns:
            True if the API key is valid, False otherwise
        """
        # Check if the API key is active
        if not self.is_active:
                    return False

        # Check if the API key has expired
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
                    return False

                return True

    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.last_used_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the API key to a dictionary.

        Returns:
            Dictionary representation of the API key
        """
                return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "scopes": self.scopes,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
            "prefix": self.prefix,
            "key_hash": self.key_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIKey":
        """
        Create an API key from a dictionary.

        Args:
            data: Dictionary representation of the API key

        Returns:
            API key instance
        """
        # Convert ISO format strings to datetime objects
        expires_at = (
            datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None
        )
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None
        )
        last_used_at = (
            datetime.fromisoformat(data["last_used_at"])
            if data.get("last_used_at")
            else None
        )

        api_key = cls(
            id=data.get("id"),
            key=data.get("key"),
            name=data.get("name", ""),
            description=data.get("description"),
            user_id=data.get("user_id"),
            scopes=data.get("scopes", ["read"]),
            is_active=data.get("is_active", True),
            expires_at=expires_at,
            created_at=created_at,
            last_used_at=last_used_at,
        )

        # Set key-related fields if they exist in the data
        if "prefix" in data:
            api_key.prefix = data["prefix"]
        if "key_hash" in data:
            api_key.key_hash = data["key_hash"]

                return api_key

    def has_scope(self, scope: str) -> bool:
        """
        Check if the API key has a specific scope.

        Args:
            scope: Scope to check

        Returns:
            True if the API key has the scope, False otherwise
        """
                return scope in self.scopes