"""
auth_reset - Module for users.password_reset.

This module provides functionality for authentication credential reset operations.
"""

# Standard library imports
from __future__ import annotations

import hashlib
import secrets
import string
import time
from datetime import datetime, timedelta, timezone
from typing import TypeAlias

from common_utils.logging import get_logger
from users.auth import hash_credential

# Type aliases
ResetResult: TypeAlias = tuple[bool, str | None]
UserDict: TypeAlias = dict[str, str | None | int]


# Define a proper interface for UserRepository
class UserRepository:
    """Interface for user repository operations."""

    def find_by_email(self, email: str) -> UserDict | None:
        """Find a user by email."""
        raise NotImplementedError

    def find_by_reset_token(self, token: str) -> UserDict | None:
        """Find a user by reset token."""
        raise NotImplementedError

    def update(self, user_id: int, data: dict) -> bool:
        """Update a user."""
        raise NotImplementedError


# Initialize logger
logger = get_logger(__name__)


def generate_reset_code(length: int = 32) -> str:
    """
    Generate a secure random code for authentication credential reset.

    Args:
    ----
        length: Length of the code

    Returns:
    -------
        str: The generated code

    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class PasswordResetService:
    """Service for authentication credential reset operations."""

    def __init__(
        self,
        user_repository: UserRepository | None = None,
        code_expiry: int | None = None,
    ) -> None:
        """
        Initialize the credential reset service.

        Args:
        ----
            user_repository: Repository for user data
            code_expiry: Expiry time for reset codes in seconds

        """
        self.user_repository = user_repository
        self.code_expiry = code_expiry or 3600  # 1 hour default

    def request_reset(self, email: str) -> ResetResult:
        """
        Request an authentication credential reset.

        Args:
        ----
            email: Email of the user

        Returns:
        -------
            Tuple[bool, Optional[str]]: (success, masked_code)

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False, None

        # Find the user
        user: UserDict | None = self.user_repository.find_by_email(email)
        if not user:
            # Don't reveal whether email exists or not for security
            logger.info(
                "Authentication reset requested for unregistered email",
                extra={"email_hash": hash(email) % 10000},
            )
            # Simulate the time it would take to process a valid request
            # to prevent timing attacks that could reveal if an email exists
            time.sleep(0.2)  # 200ms delay
            return False, None

        # Generate a secure reset code with high entropy
        reset_code = generate_reset_code(48)  # Use longer code for better security
        expiry = datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.code_expiry
        )

        # Hash the reset token before storing it
        # This prevents exposure in case of DB breach
        hashed_reset_token = hashlib.sha256(reset_code.encode()).hexdigest()

        # Update the user with the hashed reset code
        # Ensure user ID is an integer
        user_id = int(user["id"]) if user["id"] is not None else 0
        self.user_repository.update(
            user_id,
            {
                "auth_reset_token": hashed_reset_token,
                "auth_reset_expires": expiry.isoformat(),
            },
        )

        # Log with user ID but not the actual code
        logger.info(
            "Authentication reset initiated",
            extra={
                "user_id": user["id"],
                "expiry": expiry.isoformat(),
            },
        )

        # Mask the reset code for security in production
        # Only return the first 2 characters and last 2 characters
        # with asterisks in between
        mask_length = len(reset_code) - 4
        if reset_code:
            masked_code = reset_code[:2] + "*" * mask_length + reset_code[-2:]
        else:
            masked_code = None

        return True, masked_code  # Return masked code instead of actual code

    def reset_auth_credential(self, reset_code: str, new_credential: str) -> bool:
        """
        Reset an authentication credential using a reset code.

        Args:
        ----
            reset_code: The reset code
            new_credential: The new authentication credential

        Returns:
        -------
            bool: True if the credential was reset, False otherwise

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False

        # Hash the provided reset code the same way we stored it
        hashed_reset_token = hashlib.sha256(reset_code.encode()).hexdigest()

        # Find the user with the reset code hash
        user: UserDict | None = self.user_repository.find_by_reset_token(
            hashed_reset_token
        )
        if not user:
            # Don't reveal whether code exists
            logger.warning(
                "Authentication reset attempt with invalid code",
                extra={"code_hash": hash(reset_code) % 10000},
            )
            return False

        # Check if the code is expired
        if not user.get("auth_reset_expires"):
            logger.warning("Reset code has no expiry", extra={"user_id": user["id"]})
            return False

        expiry = datetime.fromisoformat(user["auth_reset_expires"])
        if expiry < datetime.now(tz=timezone.utc):
            logger.warning(
                "Expired authentication reset attempt", extra={"user_id": user["id"]}
            )
            return False

        # Hash the new credential
        hashed_credential = hash_credential(new_credential)

        # Update the user with the new credential
        # Ensure user ID is an integer
        user_id = int(user["id"]) if user["id"] is not None else 0
        self.user_repository.update(
            user_id,
            {
                "auth_hash": hashed_credential,
                "auth_reset_token": None,
                "auth_reset_expires": None,
                "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            },
        )

        logger.info("Authentication reset successful", extra={"user_id": user["id"]})
        return True
