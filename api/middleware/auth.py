"""
Authentication middleware for the API server.

This module provides authentication middleware for the API server.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta

from ..config import APIConfig
from ..services.api_key_service import APIKeyService

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import FastAPI and JWT
try:
    from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
    from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
    import jwt

    FASTAPI_AVAILABLE = True
    JWT_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI and PyJWT are required for authentication middleware")
    FASTAPI_AVAILABLE = False
    JWT_AVAILABLE = False


class AuthMiddleware:
    """
    Authentication middleware for the API server.
    """

    def __init__(self, config: APIConfig):
        """
        Initialize the authentication middleware.

        Args:
            config: API configuration
        """
        self.config = config
        self.api_keys = set(config.api_keys)
        self.jwt_secret = config.jwt_secret
        self.jwt_algorithm = config.jwt_algorithm
        self.jwt_expires_minutes = config.jwt_expires_minutes

        # Initialize API key service
        self.api_key_service = APIKeyService()

    def create_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT token.

        Args:
            data: Token data

        Returns:
            JWT token
        """
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT is required for JWT token creation")

        if not self.jwt_secret:
            raise ValueError("JWT secret is not configured")

        # Set expiration time
        expires = datetime.utcnow() + timedelta(minutes=self.jwt_expires_minutes)

        # Create token data
        token_data = {**data, "exp": expires}

        # Create token
        token = jwt.encode(token_data, self.jwt_secret, algorithm=self.jwt_algorithm)

        return token

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token.

        Args:
            token: JWT token

        Returns:
            Token data
        """
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT is required for JWT token verification")

        if not self.jwt_secret:
            raise ValueError("JWT secret is not configured")

        try:
            # Decode token
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")

        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def verify_api_key(self, api_key: str) -> bool:
        """
        Verify an API key.

        Args:
            api_key: API key

        Returns:
            True if the API key is valid, False otherwise
        """
        # First check legacy API keys (from config)
        if api_key in self.api_keys:
            return True

        # Then check API keys from the API key service
        api_key_obj = self.api_key_service.verify_api_key(api_key)
        return api_key_obj is not None


async def get_current_user(
    request: Request = None,
    api_key_header: str = Depends(APIKeyHeader(name="X-API-Key", auto_error=False)),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
) -> Dict[str, Any]:
    """
    Get the current user from the request.

    Args:
        request: HTTP request
        api_key_header: API key from header
        token: JWT token

    Returns:
        User data
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for authentication")

    # Create auth middleware
    from ..config import APIConfig

    config = APIConfig()
    auth_middleware = AuthMiddleware(config)

    # Check API key
    if api_key_header:
        # First check legacy API keys
        if api_key_header in auth_middleware.api_keys:
            # For legacy API keys, use a default user
            return {"id": "system", "name": "System", "role": "system"}

        # Then check API keys from the API key service
        api_key = auth_middleware.api_key_service.verify_api_key(api_key_header)
        if api_key:
            # For API keys from the service, use the user ID from the API key
            return {
                "id": api_key.user_id or "system",
                "name": "API Key User",
                "role": "api_key",
            }

    # Check JWT token
    if token:
        try:
            # Verify token
            payload = auth_middleware.verify_token(token)

            # Return user data from token
            return payload
        except ValueError:
            pass

    # Authentication failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def setup_auth_middleware(app: Any, config: APIConfig) -> None:
    """
    Set up authentication middleware for the API server.

    Args:
        app: FastAPI application
        config: API configuration
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI is required for authentication middleware")
        return

    # Create middleware
    auth_middleware = AuthMiddleware(config)

    # Set up API key authentication
    api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    # Set up JWT authentication
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

    @app.middleware("http")
    async def auth_middleware_func(request: Request, call_next: Callable) -> Response:
        """
        Authentication middleware function.

        Args:
            request: HTTP request
            call_next: Next middleware function

        Returns:
            HTTP response
        """
        # Skip authentication for certain paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/token"]:
            return await call_next(request)

        # Check API key
        api_key = request.headers.get("X-API-Key")
        if api_key and auth_middleware.verify_api_key(api_key):
            return await call_next(request)

        # Check JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                auth_middleware.verify_token(token)
                return await call_next(request)
            except ValueError:
                pass

        # Authentication failed
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content='{"detail":"Invalid authentication credentials"}',
            media_type="application/json",
        )
