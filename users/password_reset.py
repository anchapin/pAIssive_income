"""auth_reset - Module for users.password_reset.

This module provides functionality for authentication credential reset operations.
"""

# Standard library imports
import hashlib
import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

from common_utils.logging import get_logger

# Third-party imports
# Local imports
from users.auth import hash_credential

# Initialize logger
logger = get_logger(__name__)


def generate_reset_code(length: int = 32) -> str:
    """Generate a secure random code for authentication credential reset.

    Args:
    ----
        length: Length of the code

    Returns:
    -------
        str: The generated code

    """
    alphabet = string.ascii_letters + string.digits
    code = "".join(secrets.choice(alphabet) for _ in range(length))
    return code


class PasswordResetService:
    """Service for authentication credential reset operations."""

    def __init__(self, user_repository=None, code_expiry=None):
        """Initialize the credential reset service.

        Args:
        ----
            user_repository: Repository for user data
            code_expiry: Expiry time for reset codes in seconds

        """
        self.user_repository = user_repository
        self.code_expiry = code_expiry or 3600  # 1 hour default

    def request_reset(self, email: str) -> Tuple[bool, Optional[str]]:
        """Request an authentication credential reset.

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
        user = self.user_repository.find_by_email(email)
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
        expiry = datetime.utcnow() + timedelta(seconds=self.code_expiry)

        # Hash the reset token before storing it
        # This prevents exposure in case of DB breach
        hashed_reset_token = hashlib.sha256(reset_code.encode()).hexdigest()

        # Update the user with the hashed reset code
        self.user_repository.update(
            user["id"],
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

        # Send the actual code via secure email channel (not implemented here)
        # self.email_service.send_reset_code(email, reset_code)

        return True, masked_code  # Return masked code instead of actual code

    def reset_auth_credential(self, reset_code: str, new_credential: str) -> bool:
        """Reset an authentication credential using a reset code.

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
        user = self.user_repository.find_by_reset_token(hashed_reset_token)
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
        if expiry < datetime.utcnow():
            logger.warning(
                "Expired authentication reset attempt", extra={"user_id": user["id"]}
            )
            return False

        # Hash the new credential
        hashed_credential = hash_credential(new_credential)

        # Update the user with the new credential
        self.user_repository.update(
            user["id"],
            {
                "auth_hash": hashed_credential,
                "auth_reset_token": None,
                "auth_reset_expires": None,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        logger.info("Authentication reset successful", extra={"user_id": user["id"]})
        return True
