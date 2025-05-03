"""
User schemas for the API server.
"""


from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest

(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Request model for user registration."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")


class UserLoginRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Request model for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserLoginResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Response model for user login."""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")


class UserResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Response model for user data."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    created_at: str = Field(..., description="Timestamp when user was created")
    updated_at: Optional[str] = Field(
        None, description="Timestamp when user was last updated"
    )


class UserProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Request model for updating user profile."""
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Request model for changing password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")


class Project(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Model for a user project."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_at: str = Field(..., description="Timestamp when project was created")
    updated_at: Optional[str] = Field(
        None, description="Timestamp when project was last updated"
    )


class Team(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Model for a user team."""
    id: str = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    created_at: str = Field(..., description="Timestamp when team was created")
    updated_at: Optional[str] = Field(
        None, description="Timestamp when team was last updated"
    )


class Activity(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Model for a user activity."""
    id: str = Field(..., description="Activity ID")
    type: str = Field(..., description="Activity type")
    description: str = Field(..., description="Activity description")
    timestamp: str = Field(..., description="Timestamp when activity occurred")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional activity metadata"
    )


class UserSettings(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Model for user settings."""
    theme: str = Field("light", description="UI theme preference")
    notifications_enabled: bool = Field(
        True, description="Whether notifications are enabled"
    )
    email_notifications: bool = Field(
        True, description="Whether email notifications are enabled"
    )


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Response model for user settings."""
    settings: UserSettings = Field(..., description="User settings")


class UserSettingsUpdateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Request model for updating user settings."""
    settings: UserSettings = Field(..., description="New user settings")


class PaginatedList(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Base model for paginated lists."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class PaginatedProjectList(PaginatedList):
    """Response model for paginated project list."""

    items: List[Project] = Field(..., description="List of projects")


class PaginatedTeamList(PaginatedList):
    """Response model for paginated team list."""

    items: List[Team] = Field(..., description="List of teams")


class PaginatedActivityList(PaginatedList:
    """Response model for paginated activity list."""

    items: List[Activity] = Field(..., description="List of activities"