"""
Authentication utilities for the pAIssive_income project.

This module includes functions for password hashing, token generation and validation.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from .models import User, UserPublic

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
TOKEN_ALGORITHM = "HS256"

# Secret key for JWT (should be loaded from environment or secrets management service)
# In production, use os.environ.get("JWT_SECRET_KEY") or another secrets management approach
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "development_secret_key")


# Password hashing using hashlib
def hash_password(password: str) -> str:
    """
    Hash a password using a secure algorithm (PBKDF2 with SHA256).

    Args:
        password: The plain text password

    Returns:
        The hashed password as a string
    """
    salt = os.urandom(32)
    iterations = 100000  # Number of iterations (adjust based on security requirements)

    # Use PBKDF2 with SHA256
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    # Store iterations:salt:key
    storage = f"{iterations}:{base64.b64encode(salt).decode('utf-8')}:{base64.b64encode(key).decode('utf-8')}"
    return storage


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a provided password against a stored hash.

    Args:
        stored_password: The previously hashed password
        provided_password: The plain text password to verify

    Returns:
        True if the password matches, False otherwise
    """
    try:
        # Extract components
        iterations, salt, stored_key = stored_password.split(":")
        iterations = int(iterations)
        salt = base64.b64decode(salt)
        stored_key = base64.b64decode(stored_key)

        # Hash the provided password
        key = hashlib.pbkdf2_hmac(
            "sha256", provided_password.encode("utf-8"), salt, iterations
        )

        # Compare using constant-time comparison (to prevent timing attacks)
        return hmac.compare_digest(key, stored_key)

    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_auth_token(
    user_id: str, roles: list[str], expiry: int = DEFAULT_TOKEN_EXPIRY
) -> str:
    """
    Create a JWT-like authentication token for a user.

    Args:
        user_id: The user's unique identifier
        roles: The user's roles for authorization
        expiry: Token expiry time in seconds

    Returns:
        JWT token string
    """
    # Create payload
    now = int(time.time())
    payload = {
        "sub": user_id,  # Subject (user ID)
        "roles": roles,  # User roles for authorization
        "iat": now,  # Issued at time
        "exp": now + expiry,  # Expiry time
    }

    # Convert payload to base64
    payload_json = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")

    # Create header (algorithm information)
    header = {"alg": TOKEN_ALGORITHM, "typ": "JWT"}
    header_json = json.dumps(header).encode("utf-8")
    header_b64 = base64.urlsafe_b64encode(header_json).decode("utf-8").rstrip("=")

    # Create signature
    to_sign = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"), to_sign.encode("utf-8"), hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    # Combine to create token
    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    return token


def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT-like authentication token.

    Args:
        token: The JWT token to verify

    Returns:
        The decoded payload if valid, None otherwise
    """
    try:
        # Split token into components
        header_b64, payload_b64, signature_b64 = token.split(".")

        # Pad base64 if necessary
        def add_padding(b64_str):
            padding = 4 - (len(b64_str) % 4)
            if padding < 4:
                return b64_str + ("=" * padding)
            return b64_str

        # Verify signature
        to_verify = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            JWT_SECRET_KEY.encode("utf-8"), to_verify.encode("utf-8"), hashlib.sha256
        ).digest()

        received_signature = base64.urlsafe_b64decode(add_padding(signature_b64))

        # Use constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(expected_signature, received_signature):
            logger.warning("Token signature verification failed")
            return None

        # Decode payload
        payload_json = base64.urlsafe_b64decode(add_padding(payload_b64))
        payload = json.loads(payload_json)

        # Check expiry
        now = int(time.time())
        if payload.get("exp", 0) < now:
            logger.warning("Token has expired")
            return None

        return payload

    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def create_session_for_user(user: User) -> Dict[str, Union[str, UserPublic]]:
    """
    Create a session for a user, including token generation.

    Args:
        user: The authenticated user

    Returns:
        Dict with token and user info
    """
    # Update last login time
    user.last_login = datetime.utcnow()

    # Create token
    token = create_auth_token(
        user_id=user.id,
        roles=user.roles,
    )

    # Create public user object (without sensitive data)
    user_public = UserPublic(
        id=user.id,
        username=user.username,
        email=user.email,
        name=user.name,
        roles=user.roles,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )

    # Return session data
    return {
        "token": token,
        "user": user_public,
        "expires_at": datetime.utcnow() + timedelta(seconds=DEFAULT_TOKEN_EXPIRY),
    }
