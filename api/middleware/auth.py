"""
Authentication middleware for the API server.
"""

import logging
from typing import Optional, Callable
from fastapi import HTTPException, Header, Depends, status, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify the authorization token.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        The verified token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme"
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

async def get_current_user(token: str = Depends(verify_token)):
    """
    Get the current authenticated user.
    
    Args:
        token: The verified authentication token
        
    Returns:
        User data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # TODO: Add proper token validation and user lookup
    # For now, return mock user data
    return {
        "id": "test_user_id",
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "created_at": "2025-04-30T00:00:00Z"
    }

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""

    def __init__(self, app, exclude_paths: Optional[list[str]] = None):
        """Initialize middleware."""
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/user/login",
            "/user/register",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request."""
        # Skip auth for excluded paths
        if any(request.url.path.endswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content='{"detail":"Missing authorization header"}',
                media_type="application/json"
            )

        try:
            # Verify token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content='{"detail":"Invalid authorization scheme"}',
                    media_type="application/json"
                )

            # TODO: Add proper token validation
            # For now, we just check if it's our mock token
            if token != "mock_token":
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content='{"detail":"Invalid token"}',
                    media_type="application/json"
                )

            # Continue processing
            return await call_next(request)

        except ValueError:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content='{"detail":"Invalid authorization header format"}',
                media_type="application/json"
            )
