"""
Authentication middleware for the API server.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

from api.config import APIConfig

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# JWT configuration
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthMiddleware:
    """Authentication middleware."""
    
    def __init__(self, config: APIConfig | str):
        if isinstance(config, APIConfig):
            if not config.jwt_secret:
                raise ValueError("JWT secret is not configured")
            self.secret_key = config.jwt_secret
            self.algorithm = config.jwt_algorithm or JWT_ALGORITHM
            self.access_token_expire_minutes = config.jwt_expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
            self.api_keys = config.api_keys or []
        else:
            self.secret_key = config
            self.algorithm = JWT_ALGORITHM
            self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
            self.api_keys = []
    
    def create_token(self, data: dict) -> str:
        """Create a JWT token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")

    def verify_api_key(self, api_key: str) -> bool:
        """Verify an API key."""
        # Return False for empty API keys
        if not api_key:
            return False
            
        # Check if API key exists in configured keys
        return api_key in self.api_keys


# Create middleware instance
auth_middleware = AuthMiddleware("test-secret")  # Default for testing

async def verify_token(token: str = Depends(security)) -> Dict[str, Any]:
    """Verify a JWT token."""
    try:
        return auth_middleware.verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_user(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get the current authenticated user."""
    try:
        # The token payload contains the user info
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
