"""
Token refresh functionality for the pAIssive_income project.

This module provides functions for refreshing authentication tokens
and managing token blacklisting.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

from .auth import create_auth_token, verify_auth_token
from .models import User
from .services import get_user_by_id

# Configure logger
logger = logging.getLogger(__name__)

# Constants
REFRESH_TOKEN_EXPIRY = 30 * 24 * 60 * 60  # 30 days in seconds
REFRESH_TOKEN_SECRET_KEY = os.environ.get(
    "REFRESH_TOKEN_SECRET_KEY", "dev-refresh-token-secret"
)

# In-memory storage for token blacklist
# In a production environment, this would be stored in a database
TOKEN_BLACKLIST: Set[str] = set()


def create_refresh_token(user_id: str) -> str:
    """
    Create a refresh token for a user.

    Args:
        user_id: The user's unique identifier

    Returns:
        Refresh token string
    """
    # Create payload
    now = int(time.time())
    payload = {
        "sub": user_id,  # Subject (user ID)
        "iat": now,  # Issued at time
        "exp": now + REFRESH_TOKEN_EXPIRY,  # Expiry time
        "type": "refresh",  # Token type
    }

    # Convert payload to base64
    payload_json = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")

    # Create header (algorithm information)
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header).encode("utf-8")
    header_b64 = base64.urlsafe_b64encode(header_json).decode("utf-8").rstrip("=")

    # Create signature
    to_sign = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        REFRESH_TOKEN_SECRET_KEY.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    # Combine to create token
    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    return token


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a refresh token.

    Args:
        token: Refresh token to verify

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        # Check if token is blacklisted
        if token in TOKEN_BLACKLIST:
            logger.warning("Blacklisted refresh token used")
            return None

        # Split token into parts
        header_b64, payload_b64, signature_b64 = token.split(".")

        # Verify signature
        to_verify = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            REFRESH_TOKEN_SECRET_KEY.encode("utf-8"),
            to_verify.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        expected_signature_b64 = (
            base64.urlsafe_b64encode(expected_signature).decode("utf-8").rstrip("=")
        )

        if signature_b64 != expected_signature_b64:
            logger.warning("Invalid refresh token signature")
            return None

        # Decode payload
        # Add padding if needed
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8")
        payload = json.loads(payload_json)

        # Check if token is expired
        now = int(time.time())
        if payload.get("exp", 0) < now:
            logger.warning("Expired refresh token")
            return None

        # Check if token is a refresh token
        if payload.get("type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None

        return payload

    except Exception as e:
        logger.error(f"Refresh token verification error: {e}")
        return None


def refresh_auth_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    Refresh an authentication token using a valid refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        Dict with new auth token and expiry if successful, None otherwise
    """
    # Verify refresh token and get payload
    payload = verify_refresh_token(refresh_token)
    if not payload:
        logger.warning("Token refresh failed: invalid refresh token")
        return None

    # Get user ID from payload
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Token refresh failed: missing user ID in token")
        return None

    # Get user from database
    user = get_user_by_id(user_id)
    if not user:
        logger.warning(f"Token refresh failed: user not found (ID: {user_id})")
        return None

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Token refresh failed: user is inactive (ID: {user_id})")
        return None

    # Create new auth token
    new_token = create_auth_token(user_id=user.id, roles=user.roles)

    # Calculate expiry datetime
    expires_at = datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_EXPIRY)

    logger.info(f"Auth token refreshed for user: {user.username} (ID: {user_id})")
    return {"token": new_token, "expires_at": expires_at}


def blacklist_token(token: str) -> bool:
    """
    Add a token to the blacklist.

    Args:
        token: Token to blacklist

    Returns:
        True if token was added to blacklist, False otherwise
    """
    try:
        # Verify token is valid before blacklisting
        payload = verify_auth_token(token)
        if not payload:
            logger.warning("Cannot blacklist invalid token")
            return False

        # Add token to blacklist
        TOKEN_BLACKLIST.add(token)
        logger.info(f"Token blacklisted for user ID: {payload.get('sub')}")
        return True

    except Exception as e:
        logger.error(f"Token blacklisting error: {e}")
        return False


def cleanup_blacklist() -> int:
    """
    Clean up expired tokens from the blacklist.

    Returns:
        Number of tokens removed from blacklist
    """
    now = int(time.time())
    tokens_to_remove = set()

    for token in TOKEN_BLACKLIST:
        try:
            # Split token and decode payload
            _, payload_b64, _ = token.split(".")

            # Add padding if needed
            padding = "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode(
                "utf-8"
            )
            payload = json.loads(payload_json)

            # Check if token is expired
            if payload.get("exp", 0) < now:
                tokens_to_remove.add(token)

        except Exception:
            # If we can't decode the token, keep it in the blacklist to be safe
            pass

    # Remove expired tokens from blacklist
    TOKEN_BLACKLIST.difference_update(tokens_to_remove)

    logger.info(f"Cleaned up {len(tokens_to_remove)} expired tokens from blacklist")
    return len(tokens_to_remove)
