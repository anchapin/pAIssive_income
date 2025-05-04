"""
"""
Authentication utilities for API endpoints.
Authentication utilities for API endpoints.


This module provides utilities for authentication in API endpoints.
This module provides utilities for authentication in API endpoints.
"""
"""


import os
import os
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


import jwt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer


# Constants
# Constants
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")  # Change in production
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")  # Change in production
ALGORITHM = "HS256"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Security schemes
# Security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="X-API-Key")
api_key_header = APIKeyHeader(name="X-API-Key")




def create_access_token(
def create_access_token(
data: Dict[str, Any], expires_delta: Optional[timedelta] = None
data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    ) -> str:
    """
    """
    Create a JWT access token.
    Create a JWT access token.


    Args:
    Args:
    data: Data to encode in the token
    data: Data to encode in the token
    expires_delta: Optional expiration time
    expires_delta: Optional expiration time


    Returns:
    Returns:
    JWT access token
    JWT access token
    """
    """
    to_encode = data.copy()
    to_encode = data.copy()
    expire = datetime.utcnow() + (
    expire = datetime.utcnow() + (
    expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    )
    to_encode.update({"exp": expire})
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    return encoded_jwt




    def verify_token(token: str) -> Dict[str, Any]:
    def verify_token(token: str) -> Dict[str, Any]:
    """
    """
    Verify a JWT token.
    Verify a JWT token.


    Args:
    Args:
    token: JWT token to verify
    token: JWT token to verify


    Returns:
    Returns:
    Decoded token payload
    Decoded token payload


    Raises:
    Raises:
    HTTPException: If the token is invalid
    HTTPException: If the token is invalid
    """
    """
    try:
    try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
    return payload
except jwt.PyJWTError:
except jwt.PyJWTError:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    headers={"WWW-Authenticate": "Bearer"},
    )
    )




    def get_user_from_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    def get_user_from_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    """
    Get user from a JWT token.
    Get user from a JWT token.


    Args:
    Args:
    token: JWT token
    token: JWT token


    Returns:
    Returns:
    User data from the token
    User data from the token


    Raises:
    Raises:
    HTTPException: If the token is invalid
    HTTPException: If the token is invalid
    """
    """
    payload = verify_token(token)
    payload = verify_token(token)
    user_id = payload.get("id")
    user_id = payload.get("id")
    if user_id is None:
    if user_id is None:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
    headers={"WWW-Authenticate": "Bearer"},
    )
    )
    return payload
    return payload