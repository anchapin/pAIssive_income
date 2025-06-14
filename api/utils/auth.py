"""
auth - Module for api/utils.auth.

This module provides utility functions for authentication in the API.
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime, timezone

# Local imports
from typing import TYPE_CHECKING, Any

# Third-party imports
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from pydantic import BaseModel

from common_utils.logging import get_logger
from users.password_reset import UserRepositoryProtocol

if TYPE_CHECKING:
    from users.password_reset import UserRepositoryProtocol
    from users.services import UserService

# Initialize logger
logger = get_logger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key")

# Create module-level singletons for dependency injection
user_service_dependency = Depends()
oauth2_scheme_dependency = Depends(oauth2_scheme)
api_key_header_dependency = Depends(api_key_header)


class TokenData(BaseModel):
    """Model for token data."""

    sub: str
    scopes: list[str] = []


async def get_current_user(
    token: str = oauth2_scheme_dependency,
    user_service: UserService = user_service_dependency,
) -> dict[str, Any]:
    """
    Get the current user from a JWT token.

    Args:
    ----
        token: The JWT token
        user_service: The user service

    Returns:
    -------
        Dict: The user data

    Raises:
    ------
        HTTPException: If the token is invalid or the user is not found

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token
    success, payload = user_service.verify_token(token)
    if not success or not payload:
        logger.warning("Invalid authentication credentials")
        raise credentials_exception

    # Get the user ID from the token
    user_id = payload.get("sub")
    if not user_id or not isinstance(user_id, str):
        logger.warning("Token missing or invalid subject claim")
        raise credentials_exception

    # Get the user from the repository
    if not user_service.user_repository:
        logger.error("User repository not available")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    user_repo: UserRepositoryProtocol = user_service.user_repository  # type: ignore[assignment]
    user = user_repo.find_by_id(user_id)
    if not user:
        logger.warning("User not found: %s", user_id)
        raise credentials_exception

    # Return the user data without sensitive authentication information
    user_data = user.copy()
    user_data.pop("auth_hash", None)
    user_data.pop("password_hash", None)  # For backward compatibility
    user_data.pop("credential_hash", None)  # Handle all possible names
    return dict(user_data)


# Create a module-level singleton for current_user dependency
current_user_dependency = Depends(get_current_user)


async def get_current_active_user(
    current_user: dict[str, Any] = current_user_dependency,
) -> dict[str, Any]:
    """
    Get the current active user.

    Args:
    ----
        current_user: The current user data

    Returns:
    -------
        Dict: The user data

    Raises:
    ------
        HTTPException: If the user is inactive

    """
    if current_user.get("status") == "inactive":
        logger.warning("Inactive user: %s", current_user.get("id"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def verify_api_key(
    api_key: str = api_key_header_dependency,
    user_service: UserService = user_service_dependency,
) -> dict[str, Any]:
    """
    Verify an API key.

    Args:
    ----
        api_key: The API key
        user_service: The user service

    Returns:
    -------
        Dict: The API key data

    Raises:
    ------
        HTTPException: If the API key is invalid

    """
    if not user_service.user_repository:
        logger.error("User repository not available")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    # Find the API key
    user_repo: UserRepositoryProtocol = user_service.user_repository  # type: ignore[assignment]
    api_key_data = user_repo.find_api_key(api_key)
    if not api_key_data:
        logger.warning("Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Check if the API key is expired
    expires_at = api_key_data.get("expires_at")
    if expires_at:
        # Convert expires_at to datetime if it's a string or int
        if isinstance(expires_at, str):
            try:
                from datetime import datetime as dt

                expires_dt = dt.fromisoformat(expires_at.replace("Z", "+00:00"))
            except ValueError:
                expires_dt = datetime.now(tz=timezone.utc)
        elif isinstance(expires_at, int):
            # Assume it's a Unix timestamp
            expires_dt = datetime.fromtimestamp(expires_at, tz=timezone.utc)
        elif isinstance(expires_at, datetime):
            expires_dt = expires_at
        else:
            # Unknown type, skip expiration check
            expires_dt = None

        if expires_dt and expires_dt < datetime.now(tz=timezone.utc):
            logger.warning("Expired API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired API key",
            )

    return dict(api_key_data)
