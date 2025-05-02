"""
Password reset functionality for the pAIssive_income project.

This module provides functions for generating password reset tokens,
validating tokens, and resetting passwords.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from .services import UserUpdate, get_user_by_email, update_user

# Configure logger
logger = logging.getLogger(__name__)

# Constants
PASSWORD_RESET_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
PASSWORD_RESET_SECRET_KEY = os.environ.get("PASSWORD_RESET_SECRET_KEY", "dev-password-reset-secret")

# In-memory storage for password reset tokens
# In a production environment, this would be stored in a database
PASSWORD_RESET_TOKENS = {}  # token -> user_id


def generate_password_reset_token(user_email: str) -> Optional[Tuple[str, datetime]]:
    """
    Generate a password reset token for a user.

    Args:
        user_email: Email of the user requesting password reset

    Returns:
        Tuple of (token, expiry_datetime) if user found, None otherwise
    """
    # Find user by email
    user = get_user_by_email(user_email)
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {user_email}")
        return None

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Password reset requested for inactive user: {user_email}")
        return None

    # Generate a unique token
    token_id = str(uuid.uuid4())
    now = int(time.time())
    expiry = now + PASSWORD_RESET_TOKEN_EXPIRY

    # Create payload
    payload = {
        "sub": user.id,  # Subject (user ID)
        "jti": token_id,  # JWT ID (unique identifier for this token)
        "iat": now,  # Issued at time
        "exp": expiry,  # Expiry time
        "purpose": "password_reset",
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
        PASSWORD_RESET_SECRET_KEY.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    # Combine to create token
    token = f"{header_b64}.{payload_b64}.{signature_b64}"

    # Store token in memory
    PASSWORD_RESET_TOKENS[token] = user.id

    # Calculate expiry datetime for user-friendly display
    expiry_datetime = datetime.utcnow() + timedelta(seconds=PASSWORD_RESET_TOKEN_EXPIRY)

    logger.info(f"Generated password reset token for user: {user.username} (ID: {user.id})")
    return token, expiry_datetime


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.

    Args:
        token: Password reset token to verify

    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        # Split token into parts
        header_b64, payload_b64, signature_b64 = token.split(".")

        # Verify signature
        to_verify = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            PASSWORD_RESET_SECRET_KEY.encode("utf-8"),
            to_verify.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        expected_signature_b64 = (
            base64.urlsafe_b64encode(expected_signature).decode("utf-8").rstrip("=")
        )

        if signature_b64 != expected_signature_b64:
            logger.warning("Invalid password reset token signature")
            return None

        # Decode payload
        # Add padding if needed
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8")
        payload = json.loads(payload_json)

        # Check if token is expired
        now = int(time.time())
        if payload.get("exp", 0) < now:
            logger.warning("Expired password reset token")
            return None

        # Check if token is for password reset
        if payload.get("purpose") != "password_reset":
            logger.warning("Token is not for password reset")
            return None

        # Check if token is in our storage
        if token not in PASSWORD_RESET_TOKENS:
            logger.warning("Token not found in storage")
            return None

        # Get user ID from token
        user_id = payload.get("sub")

        # Verify user ID matches stored token
        if PASSWORD_RESET_TOKENS[token] != user_id:
            logger.warning("Token user ID mismatch")
            return None

        return user_id

    except Exception as e:
        logger.error(f"Password reset token verification error: {e}")
        return None


def reset_password(token: str, new_password: str) -> bool:
    """
    Reset a user's password using a valid reset token.

    Args:
        token: Valid password reset token
        new_password: New password to set

    Returns:
        True if password was reset successfully, False otherwise
    """
    # Verify token and get user ID
    user_id = verify_password_reset_token(token)
    if not user_id:
        logger.warning("Password reset failed: invalid token")
        return False

    try:
        # Update user's password
        user_data = UserUpdate(password=new_password)
        user = update_user(user_id, user_data)

        if not user:
            logger.error(f"Password reset failed: user not found (ID: {user_id})")
            return False

        # Invalidate token
        if token in PASSWORD_RESET_TOKENS:
            del PASSWORD_RESET_TOKENS[token]

        logger.info(f"Password reset successful for user: {user.username} (ID: {user_id})")
        return True

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return False


def cleanup_expired_tokens() -> int:
    """
    Clean up expired password reset tokens.

    Returns:
        Number of tokens removed
    """
    now = int(time.time())
    tokens_to_remove = []

    for token in PASSWORD_RESET_TOKENS:
        try:
            # Split token and decode payload
            _, payload_b64, _ = token.split(".")

            # Add padding if needed
            padding = "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8")
            payload = json.loads(payload_json)

            # Check if token is expired
            if payload.get("exp", 0) < now:
                tokens_to_remove.append(token)

        except Exception:
            # If we can't decode the token, it's probably invalid
            tokens_to_remove.append(token)

    # Remove expired tokens
    for token in tokens_to_remove:
        del PASSWORD_RESET_TOKENS[token]

    logger.info(f"Cleaned up {len(tokens_to_remove)} expired password reset tokens")
    return len(tokens_to_remove)
