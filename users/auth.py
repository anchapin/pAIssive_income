"""auth - Module for users.auth.

This module provides functions for user authentication, including password hashing and
verification.
"""

# Standard library imports

# Third-party imports
import bcrypt

# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt.

    Args:
    ----
        password: The plain text password to hash

    Returns:
    -------
        bytes: The hashed password

    """
    if not password:
        raise ValueError("Password cannot be empty")

    # Generate a salt and hash the password
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)  # 12 is a good default for security/performance
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    logger.debug("Password hashed successfully")
    # Ensure we return bytes
    return bytes(hashed_password)


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify a password against a hashed password.

    Args:
    ----
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
    -------
        bool: True if the password matches, False otherwise

    """
    if not plain_password or not hashed_password:
        return False

    # Verify the password
    password_bytes = plain_password.encode("utf-8")
    try:
        result = bcrypt.checkpw(password_bytes, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return bool(result)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False
