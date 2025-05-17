"""
services - Module for users.services.

This module provides services for user management, including user creation,
authentication, and profile management.
"""

# Standard library imports
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol, cast

# Third-party imports
import jwt

# Local imports
from common_utils.logging import get_logger
from users.auth import hash_credential, verify_credential


# Define protocol for User model to help with type checking
class UserProtocol(Protocol):
    """Protocol defining the interface for User models."""

    id: str
    username: str
    email: str
    password_hash: str
    query: Any

    def __init__(
        self, username: str, email: str, password_hash: str, **kwargs: object
    ) -> None:
        """Initialize a user model with required attributes."""

    @classmethod
    def filter(cls, *args: object) -> object:
        """Filter users based on provided criteria."""


# Define protocol for DB session
class DBSessionProtocol(Protocol):
    """Protocol defining the interface for database session objects."""

    session: Any

    def add(self, obj: object) -> None:
        """Add an object to the session."""

    def commit(self) -> None:
        """Commit the current transaction."""


# Initialize logger
logger = get_logger(__name__)

# Initialize with None values that will be replaced if imports succeed
UserModel: type[UserProtocol] | None = None
db_session: DBSessionProtocol | None = None

try:
    from app_flask.models import User, db

    UserModel = cast("type[UserProtocol]", User)
    db_session = cast("DBSessionProtocol", db)
except ImportError:
    # Keep UserModel and db_session as None if import fails
    logger.debug(
        "Failed to import User model from app_flask.models, using fallback mechanisms"
    )


class AuthenticationError(ValueError):
    """Raised when there's an authentication-related error."""


class UserExistsError(ValueError):
    """Raised when a user already exists."""

    USERNAME_EXISTS = "Username already exists"
    EMAIL_EXISTS = "Email already exists"

    def __init__(self, message: str | None = None) -> None:
        """Initialize with a default message if none provided."""
        super().__init__(message or "User already exists")


class UserNotFoundError(ValueError):
    """Raised when a user is not found."""


class TokenError(ValueError):
    """Raised when there's a token-related error."""


class UserModelNotAvailableError(ValueError):
    """Raised when the User model is not available."""


class DatabaseSessionNotAvailableError(ValueError):
    """Raised when the database session is not available."""


# Remove redundant import fallback - already handled above


class UserService:
    """Service for user management."""

    def __init__(
        self,
        user_repository: object | None = None,
        token_secret: str | None = None,
        token_expiry: int | None = None,
    ) -> None:
        """
        Initialize the user service.

        Args:
            user_repository: Repository for user data
            token_secret: Secret for JWT token generation
            token_expiry: Expiry time for JWT tokens in seconds

        """
        # Store the user repository if provided
        if user_repository is not None:
            self.user_repository = user_repository

        # Don't set a default token secret - require it to be provided
        if not token_secret:
            logger.error("No token secret provided")
            raise AuthenticationError

        # Enhanced security: Store token secret in a private variable
        self.__token_secret = token_secret

        logger.debug("Token secret configured successfully")

        self.token_expiry = token_expiry or 3600  # 1 hour default

    @property
    def token_secret(self) -> str:
        """Securely access the token secret."""
        return self.__token_secret

    def create_user(
        self, username: str, email: str, auth_credential: str, **kwargs: object
    ) -> dict[str, object]:
        """
        Create a new user.

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
            raise AuthenticationError

        # Check if user already exists
        if hasattr(self, "user_repository") and self.user_repository:
            user_repo = cast("Any", self.user_repository)
            if user_repo.find_by_username(username):
                raise UserExistsError(UserExistsError.USERNAME_EXISTS)

            if user_repo.find_by_email(email):
                raise UserExistsError(UserExistsError.EMAIL_EXISTS)
        else:
            # Check if UserModel is available
            if UserModel is None:
                raise UserModelNotAvailableError

            # Use UserModel directly since we've checked it's not None
            model = UserModel
            existing_user = model.query.filter(
                (model.username == username) | (model.email == email)
            ).first()
            if existing_user:
                if existing_user.username == username:
                    raise UserExistsError(UserExistsError.USERNAME_EXISTS)
                raise UserExistsError(UserExistsError.EMAIL_EXISTS)

        # Hash the credential
        hashed_credential = hash_credential(auth_credential)

        # Check if UserModel is available
        if UserModel is None:
            raise UserModelNotAvailableError

        # Check if db_session is available
        if db_session is None:
            raise DatabaseSessionNotAvailableError

        # Use variables directly since we've checked they're not None
        model = UserModel
        db = db_session

        # Create User model instance
        user = model(
            username=username,
            email=email,
            password_hash=hashed_credential,
            **{k: v for k, v in kwargs.items() if hasattr(model, k)},
        )
        db.session.add(user)
        db.session.commit()

        logger.info("User created successfully", extra={"user_id": user.id})

        # Return user data without sensitive information
        created_at = getattr(user, "created_at", None)
        updated_at = getattr(user, "updated_at", None)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": str(created_at) if created_at else None,
            "updated_at": str(updated_at) if updated_at else None,
        }

    def authenticate_user(
        self, username_or_email: str, auth_credential: str
    ) -> tuple[bool, dict[str, object] | None]:
        """
        Authenticate a user.

        Args:
        ----
            username_or_email: Username or email of the user
            auth_credential: Authentication credential to verify

        Returns:
        -------
            Tuple[bool, Optional[Dict]]: (success, user_data)

        """
        # Check if UserModel is available
        if UserModel is None:
            raise UserModelNotAvailableError

        # Use UserModel directly since we've checked it's not None
        model = UserModel

        # Find the user by username or email
        user = model.query.filter(
            (model.username == username_or_email) | (model.email == username_or_email)
        ).first()

        if not user:
            # Don't leak whether the username exists - just log an event with a hash
            user_hash = hash(username_or_email) % 10000  # Simple hash for privacy
            logger.info(
                "Authentication attempt for non-existent user",
                extra={"user_hash": user_hash},
            )
            return False, None

        # Verify the credential
        if not verify_credential(auth_credential, user.password_hash):
            logger.info("Failed authentication attempt", extra={"user_id": user.id})
            return False, None

        # Update last login time if field exists
        if hasattr(user, "last_login"):
            user.last_login = datetime.now(tz=timezone.utc)

            # Check if db_session is available
            if db_session is None:
                raise DatabaseSessionNotAvailableError

            # Use db_session directly since we've checked it's not None
            db = db_session
            db.session.commit()

        # Return user data without sensitive information
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        logger.info("Authentication successful", extra={"user_id": user.id})
        return True, user_data

    def generate_token(self, user_id: str, **additional_claims: object) -> str:
        """
        Generate a JWT token for a user.

        Args:
        ----
            user_id: ID of the user
            **additional_claims: Additional claims to include in the token

        Returns:
        -------
            str: The generated JWT token

        """
        now = datetime.now(tz=timezone.utc)
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
                    "Potentially sensitive claim '%s' was excluded from token", key
                )
                continue
            # Avoid adding large values to token payload
            if isinstance(value, str) and len(value) > max_claim_length:
                logger.warning("Oversized claim '%s' was truncated", key)
                safe_claims[key] = value[:100] + "..."
            else:
                # Ensure we're storing a string value
                safe_claims[key] = str(value) if value is not None else ""

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
        # Explicitly cast to string to satisfy mypy
        return str(auth_token)

    def verify_token(self, auth_token: str) -> tuple[bool, dict[str, object] | None]:
        """
        Verify a JWT token.

        Args:
            auth_token: The JWT token to verify

        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: (success, payload)

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
