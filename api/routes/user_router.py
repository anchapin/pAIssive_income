"""user_router - User API endpoints using FastAPI."""

from __future__ import annotations

import os

# Type checking imports
from typing import TYPE_CHECKING, Union, Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, Path, status

from users.schemas import UserResponse, UserCreate, UserUpdate

from common_utils.logging import get_logger

if TYPE_CHECKING:
    from flask.wrappers import Response
    from werkzeug.wrappers import Response as WerkzeugResponse
from users.services import AuthenticationError, UserExistsError, UserService

# Set up secure logger that masks sensitive info
logger = get_logger(__name__)

# Example: provide your secret through environment variable in production
TOKEN_SECRET = os.environ.get("USER_TOKEN_SECRET", "super-secret")

# Create router
router = APIRouter(prefix="/users", tags=["users"])

# API endpoints
@router.get("", response_model=List[UserResponse])
async def get_users_endpoint():
    """Get all users."""
    return get_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int = Path(..., ge=1)):
    """Get a user by ID."""
    user = get_user_by_id(user_id)
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
        return create_user(user.model_dump())
    except Exception:
        logger.exception("Error creating user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user: UserUpdate, user_id: int = Path(..., ge=1)):
    """Update a user."""
    updated_user = update_user(user_id, user.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return updated_user


@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int = Path(..., ge=1)):
    """Delete a user."""
    if not delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return {"message": f"User with ID {user_id} deleted successfully"}
