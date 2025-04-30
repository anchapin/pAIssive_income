"""
User router for the API server.

This module provides API endpoints for user operations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import APIRouter, HTTPException, Query, Depends, Response, status, Header, Body
    from fastapi.responses import JSONResponse
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from pydantic import BaseModel, Field, EmailStr
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for API routes")
    FASTAPI_AVAILABLE = False

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter()
else:
    router = None

# Define schemas if FastAPI is available
if FASTAPI_AVAILABLE:
    class UserBase(BaseModel):
        """Base user schema."""
        username: str = Field(..., description="Username")
        email: EmailStr = Field(..., description="Email address")

    class UserCreate(UserBase):
        """User creation schema."""
        password: str = Field(..., description="Password")
        first_name: str = Field(..., description="First name")
        last_name: str = Field(..., description="Last name")

    class UserUpdate(BaseModel):
        """User update schema."""
        first_name: Optional[str] = Field(None, description="First name")
        last_name: Optional[str] = Field(None, description="Last name")
        email: Optional[EmailStr] = Field(None, description="Email address")

    class UserResponse(UserBase):
        """User response schema."""
        id: str = Field(..., description="User ID")
        first_name: str = Field(..., description="First name")
        last_name: str = Field(..., description="Last name")
        created_at: str = Field(..., description="Creation timestamp")
        updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class UserProfileResponse(BaseModel):
        """User profile response schema."""
        id: str = Field(..., description="User ID")
        username: str = Field(..., description="Username")
        email: EmailStr = Field(..., description="Email address")
        first_name: str = Field(..., description="First name")
        last_name: str = Field(..., description="Last name")
        created_at: str = Field(..., description="Creation timestamp")
        updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class UserLoginRequest(BaseModel):
        """User login request schema."""
        username: str = Field(..., description="Username")
        password: str = Field(..., description="Password")

    class UserLoginResponse(BaseModel):
        """User login response schema."""
        access_token: str = Field(..., description="Access token")
        token_type: str = Field(..., description="Token type")
        expires_in: int = Field(..., description="Token expiration in seconds")
        user_id: str = Field(..., description="User ID")

    class ChangePasswordRequest(BaseModel):
        """Change password request schema."""
        current_password: str = Field(..., description="Current password")
        new_password: str = Field(..., description="New password")

    class UserSettingsResponse(BaseModel):
        """User settings response schema."""
        id: str = Field(..., description="Settings ID")
        user_id: str = Field(..., description="User ID")
        theme: str = Field(..., description="UI theme")
        notifications_enabled: bool = Field(..., description="Notifications enabled")
        email_notifications: bool = Field(..., description="Email notifications enabled")
        language: str = Field(..., description="Language preference")

    class UserSettingsUpdate(BaseModel):
        """User settings update schema."""
        theme: Optional[str] = Field(None, description="UI theme")
        notifications_enabled: Optional[bool] = Field(None, description="Notifications enabled")
        email_notifications: Optional[bool] = Field(None, description="Email notifications enabled")
        language: Optional[str] = Field(None, description="Language preference")

    class UserActivityResponse(BaseModel):
        """User activity response schema."""
        id: str = Field(..., description="Activity ID")
        user_id: str = Field(..., description="User ID")
        action: str = Field(..., description="Action performed")
        resource_type: str = Field(..., description="Resource type")
        resource_id: str = Field(..., description="Resource ID")
        timestamp: str = Field(..., description="Timestamp")
        details: Optional[Dict[str, Any]] = Field(None, description="Additional details")

    class UserProjectResponse(BaseModel):
        """User project response schema."""
        id: str = Field(..., description="Project ID")
        name: str = Field(..., description="Project name")
        description: str = Field(..., description="Project description")
        status: str = Field(..., description="Project status")
        created_at: str = Field(..., description="Creation timestamp")
        updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class UserTeamResponse(BaseModel):
        """User team response schema."""
        id: str = Field(..., description="Team ID")
        name: str = Field(..., description="Team name")
        description: str = Field(..., description="Team description")
        role: str = Field(..., description="User's role in the team")
        created_at: str = Field(..., description="Creation timestamp")

# Define route handlers
if FASTAPI_AVAILABLE:
    # OAuth2 password bearer for token authentication
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    # Dependency to get the current user
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        """
        Get the current authenticated user.

        Args:
            token: JWT token

        Returns:
            Current user
        """
        # This is a mock implementation
        # In a real implementation, you would validate the token and get the user
        return {
            "id": "test-user-id",
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "created_at": "2025-04-29T21:30:00Z",
            "updated_at": None
        }

    @router.get("/")
    async def get_user_info():
        """
        Get user information.

        Returns:
            User information
        """
        return {
            "message": "User API is available",
            "status": "active",
            "endpoints": [
                "/register",
                "/login",
                "/profile",
                "/settings",
                "/activity",
                "/projects",
                "/teams"
            ]
        }

    @router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Register a new user",
        description="Register a new user with the system"
    )
    async def register_user(user: UserCreate):
        """
        Register a new user.

        Args:
            user: User creation data

        Returns:
            Created user
        """
        try:
            # Validate required fields
            if not user.username or not user.email or not user.password:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Username, email, and password are required"
                )

            # Mock user creation
            new_user = {
                "id": "user-" + user.username,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }

            return new_user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register user: {str(e)}"
            )

    @router.post(
        "/login",
        response_model=UserLoginResponse,
        summary="Login user",
        description="Login user and get access token"
    )
    async def login_user(user: UserLoginRequest):
        """
        Login user.

        Args:
            user: User login data

        Returns:
            Access token
        """
        try:
            # Validate credentials
            if user.username != "testuser" or user.password != "password":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )

            # Generate token
            token = "mock-jwt-token"

            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": "test-user-id"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to login user: {str(e)}"
            )

    @router.get(
        "/profile",
        response_model=UserProfileResponse,
        summary="Get user profile",
        description="Get the profile of the current authenticated user"
    )
    async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
        """
        Get user profile.

        Args:
            current_user: Current authenticated user

        Returns:
            User profile
        """
        try:
            # Return user profile
            return {
                "id": current_user["id"],
                "username": current_user["username"],
                "email": current_user["email"],
                "first_name": current_user["first_name"],
                "last_name": current_user["last_name"],
                "created_at": current_user["created_at"],
                "updated_at": current_user["updated_at"]
            }
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user profile: {str(e)}"
            )

    @router.put(
        "/profile",
        response_model=UserProfileResponse,
        summary="Update user profile",
        description="Update the profile of the current authenticated user"
    )
    async def update_user_profile(
        user: UserUpdate,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        """
        Update user profile.

        Args:
            user: User update data
            current_user: Current authenticated user

        Returns:
            Updated user profile
        """
        try:
            # Update user profile
            updated_user = dict(current_user)

            if user.first_name:
                updated_user["first_name"] = user.first_name

            if user.last_name:
                updated_user["last_name"] = user.last_name

            if user.email:
                updated_user["email"] = user.email

            updated_user["updated_at"] = datetime.now().isoformat()

            return updated_user
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user profile: {str(e)}"
            )

    @router.post(
        "/change-password",
        summary="Change user password",
        description="Change the password of the current authenticated user"
    )
    async def change_password(
        password: ChangePasswordRequest,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        """
        Change user password.

        Args:
            password: Password change data
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            # Validate current password
            if password.current_password != "password":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid current password"
                )

            # Change password
            return {"message": "Password changed successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to change password: {str(e)}"
            )

    @router.get(
        "/projects",
        response_model=List[UserProjectResponse],
        summary="Get user projects",
        description="Get the projects of the current authenticated user"
    )
    async def get_user_projects(
        current_user: Dict[str, Any] = Depends(get_current_user),
        status: Optional[str] = Query(None, description="Filter by project status")
    ):
        """
        Get user projects.

        Args:
            current_user: Current authenticated user
            status: Filter by project status

        Returns:
            List of user projects
        """
        try:
            # Mock projects
            projects = [
                {
                    "id": "project-1",
                    "name": "AI Writing Assistant",
                    "description": "An AI-powered writing assistant",
                    "status": "active",
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": "2025-04-20T15:30:00Z"
                },
                {
                    "id": "project-2",
                    "name": "Code Helper",
                    "description": "AI code assistant for developers",
                    "status": "in_development",
                    "created_at": "2025-03-10T14:20:00Z",
                    "updated_at": None
                }
            ]

            # Filter by status if provided
            if status:
                projects = [p for p in projects if p["status"] == status]

            return projects
        except Exception as e:
            logger.error(f"Error getting user projects: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user projects: {str(e)}"
            )

    @router.get(
        "/teams",
        response_model=List[UserTeamResponse],
        summary="Get user teams",
        description="Get the teams of the current authenticated user"
    )
    async def get_user_teams(current_user: Dict[str, Any] = Depends(get_current_user)):
        """
        Get user teams.

        Args:
            current_user: Current authenticated user

        Returns:
            List of user teams
        """
        try:
            # Mock teams
            teams = [
                {
                    "id": "team-1",
                    "name": "Development Team",
                    "description": "Main development team",
                    "role": "admin",
                    "created_at": "2025-01-10T09:00:00Z"
                },
                {
                    "id": "team-2",
                    "name": "Marketing Team",
                    "description": "Marketing and promotion team",
                    "role": "member",
                    "created_at": "2025-02-15T11:30:00Z"
                }
            ]

            return teams
        except Exception as e:
            logger.error(f"Error getting user teams: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user teams: {str(e)}"
            )

    @router.get(
        "/activity",
        response_model=List[UserActivityResponse],
        summary="Get user activity",
        description="Get the activity history of the current authenticated user"
    )
    async def get_user_activity(
        current_user: Dict[str, Any] = Depends(get_current_user),
        limit: int = Query(10, description="Maximum number of activities to return")
    ):
        """
        Get user activity.

        Args:
            current_user: Current authenticated user
            limit: Maximum number of activities to return

        Returns:
            List of user activities
        """
        try:
            # Mock activities
            activities = [
                {
                    "id": "activity-1",
                    "user_id": current_user["id"],
                    "action": "create",
                    "resource_type": "project",
                    "resource_id": "project-1",
                    "timestamp": "2025-04-28T14:30:00Z",
                    "details": {"name": "AI Writing Assistant"}
                },
                {
                    "id": "activity-2",
                    "user_id": current_user["id"],
                    "action": "update",
                    "resource_type": "project",
                    "resource_id": "project-1",
                    "timestamp": "2025-04-29T10:15:00Z",
                    "details": {"status": "active"}
                }
            ]

            return activities[:limit]
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user activity: {str(e)}"
            )

    @router.get(
        "/settings",
        response_model=UserSettingsResponse,
        summary="Get user settings",
        description="Get the settings of the current authenticated user"
    )
    async def get_user_settings(current_user: Dict[str, Any] = Depends(get_current_user)):
        """
        Get user settings.

        Args:
            current_user: Current authenticated user

        Returns:
            User settings
        """
        try:
            # Mock settings
            settings = {
                "id": "settings-1",
                "user_id": current_user["id"],
                "theme": "light",
                "notifications_enabled": True,
                "email_notifications": True,
                "language": "en"
            }

            return settings
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user settings: {str(e)}"
            )

    @router.put(
        "/settings",
        response_model=UserSettingsResponse,
        summary="Update user settings",
        description="Update the settings of the current authenticated user"
    )
    async def update_user_settings(
        settings: UserSettingsUpdate,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        """
        Update user settings.

        Args:
            settings: Settings update data
            current_user: Current authenticated user

        Returns:
            Updated user settings
        """
        try:
            # Mock current settings
            current_settings = {
                "id": "settings-1",
                "user_id": current_user["id"],
                "theme": "light",
                "notifications_enabled": True,
                "email_notifications": True,
                "language": "en"
            }

            # Update settings
            if settings.theme is not None:
                current_settings["theme"] = settings.theme

            if settings.notifications_enabled is not None:
                current_settings["notifications_enabled"] = settings.notifications_enabled

            if settings.email_notifications is not None:
                current_settings["email_notifications"] = settings.email_notifications

            if settings.language is not None:
                current_settings["language"] = settings.language

            return current_settings
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user settings: {str(e)}"
            )
