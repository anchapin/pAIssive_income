"""
Authentication middleware for the API server.

This module provides middleware for API authentication and authorization.
"""

import logging
from typing import Optional, List, Callable, Dict, Any
from fastapi import Request, Response, status, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.api_key_service import APIKeyService
from ..models.api_key import APIKey
from ..models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API key header
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)

# API key service
api_key_service = APIKeyService()

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API authentication."""

    def __init__(
        self,
        app,
        api_key_service: Optional[APIKeyService] = None,
        public_paths: List[str] = None,
        auth_header: str = "Authorization"
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            api_key_service: API key service
            public_paths: List of paths that don't require authentication
            auth_header: Name of the authentication header
        """
        super().__init__(app)
        self.api_key_service = api_key_service or APIKeyService()
        self.public_paths = public_paths or ["/docs", "/redoc", "/openapi.json", "/health"]
        self.auth_header = auth_header

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Skip authentication for public paths
        for path in self.public_paths:
            if request.url.path.startswith(path):
                return await call_next(request)

        # Get API key from header
        auth_header = request.headers.get(self.auth_header)

        if not auth_header:
            logger.warning("Missing authentication header")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )

        # Extract API key from header (Bearer token format)
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]
        else:
            api_key = auth_header

        # Verify API key
        api_key_obj = self.api_key_service.verify_api_key(api_key)

        if not api_key_obj:
            logger.warning("Invalid API key")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"}
            )

        # Check if API key is active
        if not api_key_obj.is_active:
            logger.warning(f"Inactive API key: {api_key_obj.id}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key is inactive"}
            )

        # Check if API key is expired
        if not api_key_obj.is_valid():
            logger.warning(f"Expired API key: {api_key_obj.id}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key has expired"}
            )

        # Add API key to request state
        request.state.api_key = api_key_obj

        # Continue processing
        return await call_next(request)

async def get_api_key(
    api_key_header: str = Security(API_KEY_HEADER)
) -> APIKey:
    """
    Get and validate the API key from the request header.

    Args:
        api_key_header: API key from the request header

    Returns:
        Validated API key

    Raises:
        HTTPException: If the API key is invalid or expired
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Extract API key from header (Bearer token format)
    if api_key_header.startswith("Bearer "):
        api_key = api_key_header[7:]
    else:
        api_key = api_key_header

    # Verify API key
    api_key_obj = api_key_service.verify_api_key(api_key)

    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check if API key is active
    if not api_key_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive"
        )

    # Check if API key is expired
    if not api_key_obj.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )

    return api_key_obj

async def get_current_user(
    api_key: APIKey = Depends(get_api_key)
) -> User:
    """
    Get the current user from the API key.

    Args:
        api_key: Validated API key

    Returns:
        Current user

    Raises:
        HTTPException: If the user is not found
    """
    # Get user from API key
    user_id = api_key.user_id

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not associated with a user"
        )

    # Get user from database
    # This would typically use a user service or repository
    # For now, we'll just return a placeholder user
    user = User(id=user_id, username="user", email="user@example.com")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def require_scopes(required_scopes: List[str]):
    """
    Dependency for requiring specific API key scopes.

    Args:
        required_scopes: List of required scopes

    Returns:
        Dependency function
    """
    async def check_scopes(api_key: APIKey = Depends(get_api_key)):
        # Check if API key has all required scopes
        for scope in required_scopes:
            if scope not in api_key.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"API key missing required scope: {scope}"
                )
        return api_key

    return check_scopes
