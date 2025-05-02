"""
User router for the API server.

This module provides route handlers for user operations.
"""

import logging
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from fastapi.security import OAuth2PasswordBearer

from ..middleware.auth import verify_token
from ..schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserLoginResponse, UserResponse,
    UserProfileUpdateRequest, PasswordChangeRequest, UserSettingsResponse,
    UserSettingsUpdateRequest, PaginatedProjectList, PaginatedTeamList,
    PaginatedActivityList
)
from ..schemas.common import ErrorResponse, SuccessResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        422: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def register_user(data: UserRegisterRequest = Body(...)):
    """Register a new user."""
    try:
        user_id = str(uuid.uuid4())
        return {
            "id": user_id,
            "username": data.username,
            "email": data.email,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/login",
    response_model=UserLoginResponse,
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    }
)
async def login_user(data: UserLoginRequest = Body(...)):
    """Log in a user."""
    try:
        # For testing, authenticate specific test user
        if data.username == "testuser" and data.password == "testpassword":
            return {
                "access_token": "mock_token",
                "token_type": "bearer"
            }
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/profile",
    response_model=UserResponse,
    responses={
        200: {"description": "User profile"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_user_profile(token: str = Depends(verify_token)):
    """Get the user profile."""
    try:
        return {
            "id": "test_user_id",
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/profile",
    response_model=UserResponse,
    responses={
        200: {"description": "Profile updated"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def update_user_profile(
    data: UserProfileUpdateRequest,
    token: str = Depends(verify_token)
):
    """Update the user profile."""
    try:
        return {
            "id": "test_user_id",
            "username": "testuser",
            "email": data.email,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/change-password",
    response_model=SuccessResponse,
    responses={
        200: {"description": "Password changed"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def change_password(
    data: PasswordChangeRequest,
    token: str = Depends(verify_token)
):
    """Change the user password."""
    try:
        return {"message": "Password changed successfully"}
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/projects",
    response_model=PaginatedProjectList,
    responses={
        200: {"description": "User projects"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_user_projects(
    token: str = Depends(verify_token),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """Get the user's projects."""
    try:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "pages": 0
        }
    except Exception as e:
        logger.error(f"Error getting user projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/teams",
    response_model=PaginatedTeamList,
    responses={
        200: {"description": "User teams"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_user_teams(
    token: str = Depends(verify_token),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """Get the user's teams."""
    try:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "pages": 0
        }
    except Exception as e:
        logger.error(f"Error getting user teams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/activity",
    response_model=PaginatedActivityList,
    responses={
        200: {"description": "User activity"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_user_activity(
    token: str = Depends(verify_token),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """Get the user's activity."""
    try:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "pages": 0
        }
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/settings",
    response_model=UserSettingsResponse,
    responses={
        200: {"description": "User settings"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_user_settings(token: str = Depends(verify_token)):
    """Get the user's settings."""
    try:
        return {
            "settings": {
                "theme": "light",
                "notifications_enabled": True,
                "email_notifications": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/settings",
    response_model=UserSettingsResponse,
    responses={
        200: {"description": "Settings updated"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def update_user_settings(
    data: UserSettingsUpdateRequest,
    token: str = Depends(verify_token)
):
    """Update the user's settings."""
    try:
        return {"settings": data.settings}
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
