"""
User-related models for the pAIssive_income project.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class Permission(BaseModel):
    """
    Permission model representing actions a user can perform.
    """

    id: str
    name: str
    description: Optional[str] = None


class Role(BaseModel):
    """
    Role model representing a set of permissions assigned to users.
    """

    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []  # List of permission IDs


class User(BaseModel):
    """
    User model with authentication and authorization information.
    """

    id: str
    username: str
    email: EmailStr
    name: str
    password_hash: str
    roles: List[str] = []  # List of role IDs
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    preferences: Dict[str, Any] = {}

    @validator("username")
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be less than 50 characters")
        if not v.isalnum() and "_" not in v and "-" not in v:
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v

    class Config:
        """Configuration for the User model."""

        # Don't include password_hash in JSON output
        schema_extra = {
            "example": {
                "id": "user123",
                "username": "johndoe",
                "email": "john@example.com",
                "name": "John Doe",
                "roles": ["user"],
                "is_active": True,
            }
        }


# Define a model for user input without sensitive fields
class UserPublic(BaseModel):
    """
    Public user model for API responses without sensitive data.
    """

    id: str
    username: str
    email: EmailStr
    name: str
    roles: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


# Models for user creation and updates
class UserCreate(BaseModel):
    """
    Model for user registration input.
    """

    username: str
    email: EmailStr
    name: str
    password: str

    @validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 100:
            raise ValueError("Password must be less than 100 characters")
        # Check if password has at least one number
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserUpdate(BaseModel):
    """
    Model for user profile updates.
    """

    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None


class LoginCredentials(BaseModel):
    """
    Model for login credentials.
    """

    username: str
    password: str
