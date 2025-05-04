"""
"""
Authentication middleware for the API server.
Authentication middleware for the API server.


This module provides middleware for API authentication and authorization.
This module provides middleware for API authentication and authorization.
"""
"""




import logging
import logging
from typing import Any, Callable, Dict, List, Optional
from typing import Any, Callable, Dict, List, Optional


import jwt
import jwt
from fastapi import Depends, HTTPException, Request, Response, Security, status
from fastapi import Depends, HTTPException, Request, Response, Security, status
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from ..models.api_key import APIKey
from ..models.api_key import APIKey
from ..models.user import User
from ..models.user import User
from ..services.api_key_service import APIKeyService
from ..services.api_key_service import APIKeyService


# Configure logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# API key header
# API key header
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


# API key service
# API key service
api_key_service = APIKeyService()
api_key_service = APIKeyService()


# JWT settings
# JWT settings
JWT_SECRET = "your-secret-key"  # Should be loaded from environment variables
JWT_SECRET = "your-secret-key"  # Should be loaded from environment variables
JWT_ALGORITHM = "HS256"
JWT_ALGORITHM = "HS256"




async def verify_token(token: str) -> Dict[str, Any]:
    async def verify_token(token: str) -> Dict[str, Any]:
    """
    """
    Verify a JWT token and return its payload.
    Verify a JWT token and return its payload.


    Args:
    Args:
    token: JWT token to verify
    token: JWT token to verify


    Returns:
    Returns:
    Dict containing the token payload
    Dict containing the token payload


    Raises:
    Raises:
    HTTPException: If the token is invalid or expired
    HTTPException: If the token is invalid or expired
    """
    """
    try:
    try:
    # Remove 'Bearer ' prefix if present
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
    if token.startswith("Bearer "):
    token = token[7:]
    token = token[7:]


    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload
    return payload
except jwt.ExpiredSignatureError:
except jwt.ExpiredSignatureError:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
    )
    )
except jwt.JWTError:
except jwt.JWTError:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    )
    )




    class AuthMiddleware(BaseHTTPMiddleware):
    class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API authentication."""

    def __init__(
    self,
    app,
    api_key_service: Optional[APIKeyService] = None,
    public_paths: List[str] = None,
    auth_header: str = "Authorization",
    ):
    """
    """
    Initialize the middleware.
    Initialize the middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    api_key_service: API key service
    api_key_service: API key service
    public_paths: List of paths that don't require authentication
    public_paths: List of paths that don't require authentication
    auth_header: Name of the authentication header
    auth_header: Name of the authentication header
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.api_key_service = api_key_service or APIKeyService()
    self.api_key_service = api_key_service or APIKeyService()
    self.public_paths = public_paths or [
    self.public_paths = public_paths or [
    "/docs",
    "/docs",
    "/redoc",
    "/redoc",
    "/openapi.json",
    "/openapi.json",
    "/health",
    "/health",
    ]
    ]
    self.auth_header = auth_header
    self.auth_header = auth_header


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    """
    Process the request.
    Process the request.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    call_next: Next middleware or route handler
    call_next: Next middleware or route handler


    Returns:
    Returns:
    Response
    Response
    """
    """
    # Skip authentication for public paths
    # Skip authentication for public paths
    for path in self.public_paths:
    for path in self.public_paths:
    if request.url.path.startswith(path):
    if request.url.path.startswith(path):
    return await call_next(request)
    return await call_next(request)


    # Get API key from header
    # Get API key from header
    auth_header = request.headers.get(self.auth_header)
    auth_header = request.headers.get(self.auth_header)


    if not auth_header:
    if not auth_header:
    logger.warning("Missing authentication header")
    logger.warning("Missing authentication header")
    return JSONResponse(
    return JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    content={"detail": "Authentication required"},
    content={"detail": "Authentication required"},
    )
    )


    # Extract API key from header (Bearer token format)
    # Extract API key from header (Bearer token format)
    if auth_header.startswith("Bearer "):
    if auth_header.startswith("Bearer "):
    api_key = auth_header[7:]
    api_key = auth_header[7:]
    else:
    else:
    api_key = auth_header
    api_key = auth_header


    # Verify API key
    # Verify API key
    api_key_obj = self.api_key_service.verify_api_key(api_key)
    api_key_obj = self.api_key_service.verify_api_key(api_key)


    if not api_key_obj:
    if not api_key_obj:
    logger.warning("Invalid API key")
    logger.warning("Invalid API key")
    return JSONResponse(
    return JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    content={"detail": "Invalid API key"},
    content={"detail": "Invalid API key"},
    )
    )


    # Check if API key is active
    # Check if API key is active
    if not api_key_obj.is_active:
    if not api_key_obj.is_active:
    logger.warning(f"Inactive API key: {api_key_obj.id}")
    logger.warning(f"Inactive API key: {api_key_obj.id}")
    return JSONResponse(
    return JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    content={"detail": "API key is inactive"},
    content={"detail": "API key is inactive"},
    )
    )


    # Check if API key is expired
    # Check if API key is expired
    if not api_key_obj.is_valid():
    if not api_key_obj.is_valid():
    logger.warning(f"Expired API key: {api_key_obj.id}")
    logger.warning(f"Expired API key: {api_key_obj.id}")
    return JSONResponse(
    return JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    content={"detail": "API key has expired"},
    content={"detail": "API key has expired"},
    )
    )


    # Add API key to request state
    # Add API key to request state
    request.state.api_key = api_key_obj
    request.state.api_key = api_key_obj


    # Continue processing
    # Continue processing
    return await call_next(request)
    return await call_next(request)




    async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> APIKey:
    async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> APIKey:
    """
    """
    Get and validate the API key from the request header.
    Get and validate the API key from the request header.


    Args:
    Args:
    api_key_header: API key from the request header
    api_key_header: API key from the request header


    Returns:
    Returns:
    Validated API key
    Validated API key


    Raises:
    Raises:
    HTTPException: If the API key is invalid or expired
    HTTPException: If the API key is invalid or expired
    """
    """
    if not api_key_header:
    if not api_key_header:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
    )
    )


    # Extract API key from header (Bearer token format)
    # Extract API key from header (Bearer token format)
    if api_key_header.startswith("Bearer "):
    if api_key_header.startswith("Bearer "):
    api_key = api_key_header[7:]
    api_key = api_key_header[7:]
    else:
    else:
    api_key = api_key_header
    api_key = api_key_header


    # Verify API key
    # Verify API key
    api_key_obj = api_key_service.verify_api_key(api_key)
    api_key_obj = api_key_service.verify_api_key(api_key)


    if not api_key_obj:
    if not api_key_obj:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
    )
    )


    # Check if API key is active
    # Check if API key is active
    if not api_key_obj.is_active:
    if not api_key_obj.is_active:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is inactive"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is inactive"
    )
    )


    # Check if API key is expired
    # Check if API key is expired
    if not api_key_obj.is_valid():
    if not api_key_obj.is_valid():
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has expired"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has expired"
    )
    )


    return api_key_obj
    return api_key_obj




    async def get_current_user(api_key: APIKey = Depends(get_api_key)) -> User:
    async def get_current_user(api_key: APIKey = Depends(get_api_key)) -> User:
    """
    """
    Get the current user from the API key.
    Get the current user from the API key.


    Args:
    Args:
    api_key: Validated API key
    api_key: Validated API key


    Returns:
    Returns:
    Current user
    Current user


    Raises:
    Raises:
    HTTPException: If the user is not found
    HTTPException: If the user is not found
    """
    """
    # Get user from API key
    # Get user from API key
    user_id = api_key.user_id
    user_id = api_key.user_id


    if not user_id:
    if not user_id:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="API key not associated with a user",
    detail="API key not associated with a user",
    )
    )


    # Get user from database
    # Get user from database
    # This would typically use a user service or repository
    # This would typically use a user service or repository
    # For now, we'll just return a placeholder user
    # For now, we'll just return a placeholder user
    user = User(id=user_id, username="user", email="user@example.com")
    user = User(id=user_id, username="user", email="user@example.com")


    if not user:
    if not user:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
    )
    )


    return user
    return user




    def require_scopes(required_scopes: List[str]):
    def require_scopes(required_scopes: List[str]):
    """
    """
    Dependency for requiring specific API key scopes.
    Dependency for requiring specific API key scopes.


    Args:
    Args:
    required_scopes: List of required scopes
    required_scopes: List of required scopes


    Returns:
    Returns:
    Dependency function
    Dependency function
    """
    """


    async def check_scopes(api_key: APIKey = Depends(get_api_key)):
    async def check_scopes(api_key: APIKey = Depends(get_api_key)):
    # Check if API key has all required scopes
    # Check if API key has all required scopes
    for scope in required_scopes:
    for scope in required_scopes:
    if scope not in api_key.scopes:
    if scope not in api_key.scopes:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    status_code=status.HTTP_403_FORBIDDEN,
    detail=f"API key missing required scope: {scope}",
    detail=f"API key missing required scope: {scope}",
    )
    )
    return api_key
    return api_key


    return check_scopes
    return check_scopes