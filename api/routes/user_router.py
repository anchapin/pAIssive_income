"""user_router - User API endpoints using FastAPI."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, EmailStr, Field

# Set up logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["users"])


# Pydantic models for request/response
class UserCreate(BaseModel):
    """Schema for user creation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user update."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    email: str
    is_active: bool


# Mock database functions
def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID from the database.

    Args:
        user_id: The user ID

    Returns:
        User data or None if not found
    """
    # This is a mock implementation
    if user_id == 999:
        return None
    return {
        "id": user_id,
        "username": f"user{user_id}",
        "email": f"user{user_id}@example.com",
        "is_active": True
    }


def get_users() -> List[Dict[str, Any]]:
    """Get all users from the database.

    Returns:
        List of user data
    """
    # This is a mock implementation
    return [
        {
            "id": 1,
            "username": "user1",
            "email": "user1@example.com",
            "is_active": True
        },
        {
            "id": 2,
            "username": "user2",
            "email": "user2@example.com",
            "is_active": False
        }
    ]


def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user in the database.

    Args:
        user_data: User data

    Returns:
        Created user data
    """
    # This is a mock implementation
    return {
        "id": 1,
        "username": user_data["username"],
        "email": user_data["email"],
        "is_active": True
    }


def update_user(user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a user in the database.

    Args:
        user_id: The user ID
        user_data: User data to update

    Returns:
        Updated user data or None if not found
    """
    # This is a mock implementation
    if user_id == 999:
        return None
    return {
        "id": user_id,
        "username": user_data.get("username", f"user{user_id}"),
        "email": user_data.get("email", f"user{user_id}@example.com"),
        "is_active": True
    }


def delete_user(user_id: int) -> bool:
    """Delete a user from the database.

    Args:
        user_id: The user ID

    Returns:
        True if deleted, False if not found
    """
    # This is a mock implementation
    return user_id != 999


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
