"""password_reset - Module for users.password_reset.

This module provides functionality for password reset operations.
"""

# Standard library imports
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple

from common_utils.logging import get_logger

# Third-party imports
# Local imports
from users.auth import hash_password

# Initialize logger
logger = get_logger(__name__)


def generate_reset_token(length: int = 32) -> str:
    """Generate a secure random token for password reset.

    Args:
    ----
        length: Length of the token

    Returns:
    -------
        str: The generated token

    """
    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    return token


class PasswordResetService:
    """Service for password reset operations."""

    def __init__(self, user_repository=None, token_expiry=None):
        """Initialize the password reset service.

        Args:
        ----
            user_repository: Repository for user data
            token_expiry: Expiry time for reset tokens in seconds

        """
        self.user_repository = user_repository
        self.token_expiry = token_expiry or 3600  # 1 hour default

    def request_reset(self, email: str) -> Tuple[bool, Optional[str]]:
        """Request a password reset.

        Args:
        ----
            email: Email of the user

        Returns:
        -------
            Tuple[bool, Optional[str]]: (success, token)

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False, None

        # Find the user
        user = self.user_repository.find_by_email(email)
        if not user:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return False, None

        # Generate a reset token
        token = generate_reset_token()
        expiry = datetime.utcnow() + timedelta(seconds=self.token_expiry)

        # Update the user with the reset token
        self.user_repository.update(
            user["id"],
            {
                "password_reset_token": token,
                "password_reset_expires": expiry.isoformat(),
            },
        )

        logger.info(f"Password reset token generated for user: {user['id']}")
        return True, token

    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset a password using a reset token.

        Args:
        ----
            token: The reset token
            new_password: The new password

        Returns:
        -------
            bool: True if the password was reset, False otherwise

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False

        # Find the user with the reset token
        user = self.user_repository.find_by_reset_token(token)
        if not user:
            logger.warning("Invalid password reset token")
            return False

        # Check if the token is expired
        if not user.get("password_reset_expires"):
            logger.warning("Reset token has no expiry")
            return False

        expiry = datetime.fromisoformat(user["password_reset_expires"])
        if expiry < datetime.utcnow():
            logger.warning("Expired password reset token")
            return False

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Update the user with the new password
        self.user_repository.update(
            user["id"],
            {
                "password_hash": hashed_password,
                "password_reset_token": None,
                "password_reset_expires": None,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"Password reset successful for user: {user['id']}")
        return True
