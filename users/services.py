"""services - Module for users.services.

This module provides services for user management, including user creation,
authentication, and profile management.
"""

# Standard library imports
import uuid

from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Optional

# Third-party imports
import jwt

from common_utils.logging import get_logger

# Local imports
from users.auth import hash_credential
from users.auth import verify_credential


class AuthenticationError(ValueError):
    """Raised when there's an authentication-related error."""

    pass


class UserExistsError(ValueError):
    """Raised when a user already exists."""

    pass


class UserNotFoundError(ValueError):
    """Raised when a user is not found."""

    pass


class TokenError(ValueError):
    """Raised when there's a token-related error."""

    pass


# Initialize logger
logger = get_logger(__name__)


class UserService:
    """Service for user management."""

    def __init__(
        self,
        user_repository: Optional[Any] = None,
        token_secret: Optional[str] = None,
        token_expiry: Optional[int] = None,
    ) -> None:
        """Initialize the user service.

        Args:
            user_repository: Repository for user data
            token_secret: Secret for JWT token generation
            token_expiry: Expiry time for JWT tokens in seconds

        """
        self.user_repository = user_repository

        # Don't set a default token secret - require it to be provided
        if not token_secret:
            logger.error("No token secret provided")
            raise AuthenticationError()

        # Enhanced security: Store token secret in a private variable
        # Use double underscore for name mangling in Python
        self.__token_secret = token_secret

        # Don't log the secret or any part of it
        logger.debug("Token secret configured successfully")

        self.token_expiry = token_expiry or 3600  # 1 hour default

    @property
    def token_secret(self) -> str:
        """Securely access the token secret."""
        return self.__token_secret

    def create_user(
        self, username: str, email: str, auth_credential: str, **kwargs: Any
    ) -> dict[str, str]:
        """Create a new user.

        Args:
        ----
            username: Username for the new user
            email: Email for the new user
            auth_credential: Authentication credential for the new user
            **kwargs: Additional user data

        Returns:
        -------
            Dict: The created user data (without sensitive information)

        """
        # Validate inputs
        if not username or not email or not auth_credential:
            raise AuthenticationError()

        # Check if user already exists
        if self.user_repository and self.user_repository.find_by_username(username):
            raise UserExistsError()

        if self.user_repository and self.user_repository.find_by_email(email):
            raise UserExistsError()

        # Hash the credential
        hashed_credential = hash_credential(auth_credential)

        # Create user data
        user_data = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "auth_hash": hashed_credential,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs,
        }

        # Save the user
        if self.user_repository:
            user_id = self.user_repository.create(user_data)
            user_data["id"] = user_id

        # Return user data without sensitive information
        user_data.pop("auth_hash", None)
        logger.info("User created successfully", extra={"user_id": user_data["id"]})
        return user_data

    def authenticate_user(
        self, username_or_email: str, auth_credential: str
    ) -> tuple[bool, Optional[dict[str, str]]]:
        """Authenticate a user.

        Args:
        ----
            username_or_email: Username or email of the user
            auth_credential: Authentication credential to verify

        Returns:
        -------
            Tuple[bool, Optional[Dict]]: (success, user_data)

        """
        if not self.user_repository:
            logger.error("User repository not available")
            return False, None

        # Find the user
        user = self.user_repository.find_by_username(username_or_email)
        if not user:
            user = self.user_repository.find_by_email(username_or_email)

        if not user:
            # Don't leak whether the username exists - just log an event with a hash
            user_hash = (
                hash(username_or_email) % 10000
            )  # Simple hash to identify attempts while preserving privacy
            logger.info(
                "Authentication attempt for non-existent user",
                extra={"user_hash": user_hash},
            )
            return False, None

        # Verify the credential
        stored_hash = user.get("auth_hash") or user.get("credential_hash", b"")
        if not verify_credential(auth_credential, stored_hash):
            # Don't log the username directly to avoid leaking valid usernames
            logger.info("Failed authentication attempt", extra={"user_id": user["id"]})
            return False, None

        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        if self.user_repository:
            self.user_repository.update(user["id"], {"last_login": user["last_login"]})

        # Return user data without sensitive information
        user_data = user.copy()
        user_data.pop("auth_hash", None)
        user_data.pop(
            "credential_hash", None
        )  # Handle both field names for compatibility
        logger.info("Authentication successful", extra={"user_id": user["id"]})
        return True, user_data

    def generate_token(self, user_id: str, **additional_claims: Any) -> str:
        """Generate a JWT token for a user.

        Args:
        ----
            user_id: ID of the user
            **additional_claims: Additional claims to include in the token

        Returns:
        -------
            str: The generated JWT token

        """
        now = datetime.utcnow()
        expiry = now + timedelta(seconds=self.token_expiry)

        # Sanitize additional claims to prevent sensitive data leakage
        safe_claims = {}
        sensitive_claim_keys = [
            "password",
            "token",
            "secret",
            "credential",
            "key",
            "auth",
        ]
        max_claim_length = 1000  # Maximum length for token claims
        for key, value in additional_claims.items():
            # Skip any sensitive looking claims
            if any(
                sensitive_term in key.lower() for sensitive_term in sensitive_claim_keys
            ):
                logger.warning(
                    f"Potentially sensitive claim '{key}' was excluded from token"
                )
                continue
            # Avoid adding large values to token payload
            if isinstance(value, str) and len(value) > max_claim_length:
                logger.warning(f"Oversized claim '{key}' was truncated")
                safe_claims[key] = value[:100] + "..."
            else:
                safe_claims[key] = value

        payload = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": expiry.timestamp(),
            "jti": str(uuid.uuid4()),  # Add unique JWT ID to prevent replay attacks
            **safe_claims,
        }

        auth_token = jwt.encode(payload, self.__token_secret, algorithm="HS256")
        # Don't log sensitive information
        logger.debug(
            "Authentication token generated",
            extra={
                "user_id": user_id,
                "expiry": expiry.isoformat(),
                "token_id": payload["jti"],
                "token_type": "JWT",
            },
        )
        # Ensure auth_token is a string
        if isinstance(auth_token, bytes):
            return auth_token.decode("utf-8")
        return str(auth_token)

    def verify_token(self, auth_token: str) -> tuple[bool, Optional[dict[str, Any]]]:
        """Verify a JWT token.

        Args:
            auth_token: The JWT token to verify

        Returns:
            tuple[bool, dict[str, Any] | None]: (success, payload)
        """
        try:
            payload = jwt.decode(auth_token, self.token_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logger.warning("Authentication verification failed: expired material")
            return False, None
        except jwt.InvalidTokenError:
            logger.warning("Authentication verification failed: invalid material")
            return False, None
        except Exception:
            logger.exception("Token verification failed")
            raise
        else:
            return True, payload
