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
from typing import Any, Final, Protocol, TypeAlias, TypedDict, cast

from common_utils.logging import get_logger
from users.auth import hash_credential

# Type aliases
ResetResult: TypeAlias = tuple[bool, str | None]


class UserData(TypedDict):
    """Type definition for user data dictionary."""

    id: int
    email: str | None
    reset_token: str | None
    reset_expires: float | None
    password_hash: str | None


UserDict: TypeAlias = UserData


# Define a proper interface for UserRepository using Protocol
class UserRepository(Protocol):
    """Interface for user repository operations."""

    def find_by_email(self, email: str) -> UserDict | None:
        """Find a user by email."""
        ...

    def find_by_reset_token(self, token: str) -> UserDict | None:
        """Find a user by reset token."""
        ...

    def update(self, user_id: int, data: dict[str, Any]) -> bool:
        """Update a user."""
        ...


# Initialize logger
logger: Final = get_logger(__name__)


def generate_reset_code(length: int = 32) -> str:
    """
    Generate a secure random code for authentication credential reset.

    Args:
        length: Length of the code

    Returns:
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
            user_repository: Repository for user data
            code_expiry: Expiry time for reset codes in seconds

        """
        self.user_repository: UserRepository | None = user_repository
        self.code_expiry: int = code_expiry or 3600  # 1 hour default

    def request_reset(self, email: str) -> ResetResult:
        """
        Request an authentication credential reset.

        Args:
            email: Email of the user

        Returns:
            tuple[bool, str | None]: A tuple of (success, masked_code)

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False, None

        # Find the user
        user: UserDict | None = self.user_repository.find_by_email(email)

        if not user:
            logger.warning("Reset requested for non-existent email: %s", email)
            # Return success to avoid leaking user existence
            return True, None

        # Generate reset code
        reset_code: str = generate_reset_code()
        reset_token: str = hashlib.sha256(reset_code.encode()).hexdigest()
        reset_expires: datetime = datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.code_expiry
        )

        # Update user with reset token
        user_id = cast("int", user["id"])
        success: bool = self.user_repository.update(
            user_id,
            {
                "reset_token": reset_token,
                "reset_expires": reset_expires.timestamp(),
            },
        )

        if not success:
            logger.error("Failed to save reset token for user: %s", user_id)
            return False, None

        # Mask the reset code for logging
        masked_code: str = reset_code[:4] + "*" * (len(reset_code) - 4)
        logger.info("Reset code generated for user", extra={"user_id": user_id})

        return True, masked_code

    def validate_reset(self, reset_code: str) -> tuple[bool, UserDict | None]:
        """
        Validate a reset code.

        Args:
            reset_code: The reset code to validate

        Returns:
            tuple[bool, UserDict | None]: A tuple of (is_valid, user_data)

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False, None

        # Hash the provided code
        reset_token: str = hashlib.sha256(reset_code.encode()).hexdigest()

        # Find user by reset token
        user: UserDict | None = self.user_repository.find_by_reset_token(reset_token)

        if not user:
            logger.warning("Invalid reset code attempt")
            return False, None

        # Check if reset code has expired
        reset_expires = user.get("reset_expires")
        if reset_expires is None:
            logger.warning("Reset code has no expiry time")
            return False, None

        expires_ts = float(reset_expires)
        if time.time() > expires_ts:
            user_id = cast("int", user["id"])
            logger.warning("Expired reset code attempt for user: %s", user_id)
            return False, None

        return True, user

    def complete_reset(
        self, reset_code: str, new_credential: str
    ) -> tuple[bool, str | None]:
        """
        Complete the authentication credential reset process.

        Args:
            reset_code: The reset code to validate
            new_credential: The new authentication credential

        Returns:
            tuple[bool, str | None]: A tuple of (success, error_message)

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False, "Service unavailable"

        # Validate the reset code first
        is_valid, user = self.validate_reset(reset_code)

        if not is_valid or not user:
            return False, "Invalid or expired reset code"

        # Hash the new credential
        new_hash: str = hash_credential(new_credential)

        # Cast user id to int
        user_id = cast("int", user["id"])

        # Update the user's credential and clear reset token
        success: bool = self.user_repository.update(
            user_id,
            {
                "password_hash": new_hash,
                "reset_token": None,
                "reset_expires": None,
            },
        )

        if not success:
            logger.error("Failed to update credential for user: %s", user_id)
            return False, "Failed to update authentication credential"

        logger.info("Credential reset successful", extra={"user_id": user_id})
        return True, None
