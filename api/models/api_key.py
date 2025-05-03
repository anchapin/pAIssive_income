"""
API key model for the API server.

This module provides the API key model for API key management.
"""

import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


class APIKey:
    """API key model."""

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

    def _generate_key(self) -> str:
        """
        Generate a new API key.

        Returns:
            Generated API key
        """
        # Generate a 32 - byte random token
        return f"pik_{secrets.token_urlsafe(32)}"

    def is_valid(self) -> bool:
        """
        Check if the API key is valid.

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
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
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
        expires_at = datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        last_used_at = (
            datetime.fromisoformat(data["last_used_at"]) if data.get("last_used_at") else None
        )

        return cls(
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

    def has_scope(self, scope: str) -> bool:
        """
        Check if the API key has a specific scope.

        Args:
            scope: Scope to check

        Returns:
            True if the API key has the scope, False otherwise
        """
        return scope in self.scopes
