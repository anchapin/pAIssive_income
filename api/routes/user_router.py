"""user_router - User API endpoints using FastAPI."""

from __future__ import annotations

import os

# Type checking imports
from typing import List

from fastapi import APIRouter, HTTPException, Path, status

from common_utils.logging import get_logger
from users.schemas import UserCreate, UserResponse, UserUpdate
from users.services import UserService

# Set up secure logger that masks sensitive info
logger = get_logger(__name__)

# Example: provide your secret through environment variable in production
TOKEN_SECRET = os.environ.get("USER_TOKEN_SECRET", "super-secret")

# Create router
router = APIRouter(prefix="/users", tags=["users"])

# Initialize user service with token secret
user_service = UserService(token_secret=TOKEN_SECRET)

# API endpoints
@router.get("", response_model=List[UserResponse])
async def get_users_endpoint():
    """Get all users."""
    return user_service.get_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int = Path(..., ge=1)):
    """Get a user by ID."""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate):
    """Create a new user."""
    try:
        user_data = user.model_dump()
        return user_service.create_user(
            username=user_data["username"],
            email=user_data["email"],
            auth_credential=user_data["password"]
        )
    except Exception:
        logger.exception("Error creating user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user: UserUpdate, user_id: int = Path(..., ge=1)):
    """Update a user."""
    updated_user = user_service.update_user(user_id, user.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return updated_user


@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int = Path(..., ge=1)):
    """Delete a user."""
    if not user_service.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return {"message": f"User with ID {user_id} deleted successfully"}
