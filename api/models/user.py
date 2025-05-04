"""
"""
User model for the API server.
User model for the API server.


This module provides the User model for user management.
This module provides the User model for user management.
"""
"""




from datetime import datetime
from datetime import datetime
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional
from uuid import uuid4
from uuid import uuid4




class User:
    class User:


    pass  # Added missing block
    pass  # Added missing block
    """User model."""

    def __init__(
    self,
    id: Optional[str] = None,
    username: str = "",
    email: str = "",
    full_name: Optional[str] = None,
    hashed_password: Optional[str] = None,
    is_active: bool = True,
    is_admin: bool = False,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    last_login: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    """
    """
    Initialize a user.
    Initialize a user.


    Args:
    Args:
    id: User ID
    id: User ID
    username: Username
    username: Username
    email: Email address
    email: Email address
    full_name: Full name
    full_name: Full name
    hashed_password: Hashed password
    hashed_password: Hashed password
    is_active: Whether the user is active
    is_active: Whether the user is active
    is_admin: Whether the user is an admin
    is_admin: Whether the user is an admin
    created_at: Creation timestamp
    created_at: Creation timestamp
    updated_at: Last update timestamp
    updated_at: Last update timestamp
    last_login: Last login timestamp
    last_login: Last login timestamp
    metadata: Additional metadata
    metadata: Additional metadata
    """
    """
    self.id = id or str(uuid4())
    self.id = id or str(uuid4())
    self.username = username
    self.username = username
    self.email = email
    self.email = email
    self.full_name = full_name
    self.full_name = full_name
    self.hashed_password = hashed_password
    self.hashed_password = hashed_password
    self.is_active = is_active
    self.is_active = is_active
    self.is_admin = is_admin
    self.is_admin = is_admin
    self.created_at = created_at or datetime.utcnow()
    self.created_at = created_at or datetime.utcnow()
    self.updated_at = updated_at or self.created_at
    self.updated_at = updated_at or self.created_at
    self.last_login = last_login
    self.last_login = last_login
    self.metadata = metadata or {}
    self.metadata = metadata or {}


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the user to a dictionary.
    Convert the user to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the user
    Dictionary representation of the user
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "username": self.username,
    "username": self.username,
    "email": self.email,
    "email": self.email,
    "full_name": self.full_name,
    "full_name": self.full_name,
    "is_active": self.is_active,
    "is_active": self.is_active,
    "is_admin": self.is_admin,
    "is_admin": self.is_admin,
    "created_at": self.created_at.isoformat() if self.created_at else None,
    "created_at": self.created_at.isoformat() if self.created_at else None,
    "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    "last_login": self.last_login.isoformat() if self.last_login else None,
    "last_login": self.last_login.isoformat() if self.last_login else None,
    "metadata": self.metadata,
    "metadata": self.metadata,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
    def from_dict(cls, data: Dict[str, Any]) -> "User":
    """
    """
    Create a user from a dictionary.
    Create a user from a dictionary.


    Args:
    Args:
    data: Dictionary representation of the user
    data: Dictionary representation of the user


    Returns:
    Returns:
    User instance
    User instance
    """
    """
    # Convert ISO format strings to datetime objects
    # Convert ISO format strings to datetime objects
    created_at = (
    created_at = (
    datetime.fromisoformat(data["created_at"])
    datetime.fromisoformat(data["created_at"])
    if data.get("created_at")
    if data.get("created_at")
    else None
    else None
    )
    )
    updated_at = (
    updated_at = (
    datetime.fromisoformat(data["updated_at"])
    datetime.fromisoformat(data["updated_at"])
    if data.get("updated_at")
    if data.get("updated_at")
    else None
    else None
    )
    )
    last_login = (
    last_login = (
    datetime.fromisoformat(data["last_login"])
    datetime.fromisoformat(data["last_login"])
    if data.get("last_login")
    if data.get("last_login")
    else None
    else None
    )
    )


    return cls(
    return cls(
    id=data.get("id"),
    id=data.get("id"),
    username=data.get("username", ""),
    username=data.get("username", ""),
    email=data.get("email", ""),
    email=data.get("email", ""),
    full_name=data.get("full_name"),
    full_name=data.get("full_name"),
    hashed_password=data.get("hashed_password"),
    hashed_password=data.get("hashed_password"),
    is_active=data.get("is_active", True),
    is_active=data.get("is_active", True),
    is_admin=data.get("is_admin", False),
    is_admin=data.get("is_admin", False),
    created_at=created_at,
    created_at=created_at,
    updated_at=updated_at,
    updated_at=updated_at,
    last_login=last_login,
    last_login=last_login,
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    def update_login(self) -> None:
    def update_login(self) -> None:
    """Update the last login timestamp."""
    self.last_login = datetime.utcnow()

    def update(self) -> None:
    """Update the last update timestamp."""
    self.updated_at = datetime.utcnow()

    def has_permission(self, permission: str) -> bool:
    """
    """
    Check if the user has a specific permission.
    Check if the user has a specific permission.


    Args:
    Args:
    permission: Permission to check
    permission: Permission to check


    Returns:
    Returns:
    True if the user has the permission, False otherwise
    True if the user has the permission, False otherwise
    """
    """
    # Admin users have all permissions
    # Admin users have all permissions
    if self.is_admin:
    if self.is_admin:
    return True
    return True


    # Check user-specific permissions (could be stored in metadata)
    # Check user-specific permissions (could be stored in metadata)
    permissions = self.metadata.get("permissions", [])
    permissions = self.metadata.get("permissions", [])
    return permission in permissions
    return permission in permissions