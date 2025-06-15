"""
services - Module for users.services.

This module provides services for user management, including user creation,
authentication, and profile management.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Final, Protocol, TypeVar, cast

# Third-party imports
import jwt
from typing_extensions import TypeAlias

# Local imports
from common_utils.logging import get_logger
from users.auth import hash_credential, verify_credential

# Type variable for generic user model
T = TypeVar("T", bound="UserProtocol")

# Type aliases
UserData: TypeAlias = Dict[str, Any]


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

    @classmethod
    def find_by_username(cls, username: str) -> T | None:
        """Find a user by username."""

    @classmethod
    def find_by_email(cls, email: str) -> T | None:
        """Find a user by email."""


# Define protocol for DB session
class DBSessionProtocol(Protocol):
    """Protocol defining the interface for database session objects."""

    session: Any

    def add(self, obj: object) -> None:
        """Add an object to the session."""

    def commit(self) -> None:
        """Commit the current transaction."""

    def rollback(self) -> None:
        """Rollback the current transaction."""


# Define protocol for User Repository
class UserRepositoryProtocol(Protocol):
    """Protocol defining the interface for user repository objects."""

    def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Find a user by ID."""

    def find_by_username(self, username: str) -> dict[str, Any] | None:
        """Find a user by username."""

    def find_by_email(self, email: str) -> dict[str, Any] | None:
        """Find a user by email."""

    def find_api_key(self, api_key: str) -> dict[str, Any] | None:
        """Find an API key."""

    def update(self, user_id: int, data: dict[str, Any]) -> bool:  # noqa: ARG002
        """Update a user."""
        return False  # Placeholder implementation


# Initialize logger
logger: Final = get_logger(__name__)

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

    MISSING_FIELDS = "Missing required fields"
    INVALID_CREDENTIALS = "Invalid username or password"


class UserExistsError(ValueError):
    """Raised when a user already exists."""

    USERNAME_EXISTS: Final[str] = "Username already exists"
    EMAIL_EXISTS: Final[str] = "Email already exists"


class UserModelNotAvailableError(RuntimeError):
    """Raised when UserModel is not available."""

    MODEL_NOT_AVAILABLE = "UserModel is not available"


class DatabaseSessionNotAvailableError(RuntimeError):
    """Raised when database session is not available."""

    SESSION_NOT_AVAILABLE = "Database session is not available"


class TokenError(ValueError):
    """Raised when there's a token-related error."""

    TOKEN_EXPIRED = "Token has expired"  # nosec B105 - Not a password, just error message
    INVALID_TOKEN = "Invalid token"  # nosec B105 - Not a password, just error message


class UserService:
    """Service class for user-related operations."""

    def __init__(
        self,
        token_secret: str | None = None,
        token_expiry: int | None = None,
        user_repository: object | None = None,
    ) -> None:
        """
        Initialize the UserService.

        Args:
            token_secret: Secret key for JWT generation
            token_expiry: Token expiry in seconds (default: 3600)
            user_repository: Optional user repository implementation

        Raises:
            ValueError: If token_secret is not provided

        """
        if not token_secret:
            token_secret = str(uuid.uuid4())
            logger.warning("No token secret provided, using generated secret")

        self.__token_secret: str = token_secret
        self.token_expiry: int = token_expiry or 3600  # 1 hour default
        self.user_repository: object | None = user_repository

    @property
    def token_secret(self) -> str:
        """
        Securely access the token secret.

        Returns:
            str: The token secret string

        """
        return self.__token_secret

    def create_user(
        self, username: str, email: str, auth_credential: str, **kwargs: object
    ) -> UserData:
        """
        Create a new user.

        Args:
            username: Username for the new user
            email: Email for the new user
            auth_credential: Authentication credential for the new user
            **kwargs: Additional user data

        Returns:
            dict[str, Any]: Dict containing the created user data (without sensitive information)

        Raises:
            AuthenticationError: If required fields are missing
            UserExistsError: If username or email already exists
            UserModelNotAvailableError: If user model is not available
            DatabaseSessionNotAvailableError: If database session is not available

        """
        # Validate inputs
        if not username or not email or not auth_credential:
            raise AuthenticationError(AuthenticationError.MISSING_FIELDS)

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
                raise UserModelNotAvailableError(
                    UserModelNotAvailableError.MODEL_NOT_AVAILABLE
                )

            # Use UserModel directly
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

        if UserModel is None:
            raise UserModelNotAvailableError(
                UserModelNotAvailableError.MODEL_NOT_AVAILABLE
            )

        if db_session is None:
            raise DatabaseSessionNotAvailableError(
                DatabaseSessionNotAvailableError.SESSION_NOT_AVAILABLE
            )

        # Create User model instance
        model = UserModel
        db = db_session

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
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
        }

    def authenticate_user(
        self, username: str, auth_credential: str
    ) -> tuple[bool, UserData | None]:
        """
        Authenticate a user.

        Args:
            username: Username of the user to authenticate
            auth_credential: Authentication credential to verify

        Returns:
            Tuple containing authentication success flag and user data

        Raises:
            AuthenticationError: If authentication fails
            UserModelNotAvailableError: If user model is not available
            DatabaseSessionNotAvailableError: If database session is not available

        """
        if not username or not auth_credential:
            raise AuthenticationError(AuthenticationError.MISSING_FIELDS)

        if UserModel is None:
            raise UserModelNotAvailableError(
                UserModelNotAvailableError.MODEL_NOT_AVAILABLE
            )

        model = UserModel

        # Find the user by username or email
        user = model.query.filter(
            (model.username == username) | (model.email == username)
        ).first()

        if not user:
            # Don't leak whether the username exists - just log an event with a hash
            user_hash = hash(username) % 10000  # Simple hash for privacy
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

            if db_session is None:
                raise DatabaseSessionNotAvailableError(
                    DatabaseSessionNotAvailableError.SESSION_NOT_AVAILABLE
                )

            db_session.session.commit()

        # Return user data without sensitive information
        user_data: UserData = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        logger.info("Authentication successful", extra={"user_id": user.id})
        return True, user_data

    def authenticate(self, username: str, auth_credential: str) -> dict[str, Any]:
        """
        Authenticate a user and generate a JWT token.

        Args:
            username: User's username
            auth_credential: User's authentication credential

        Returns:
            dict[str, Any]: Dict containing user data and JWT token

        Raises:
            AuthenticationError: If credentials are invalid
            UserModelNotAvailableError: If user model is not available

        """
        if not username or not auth_credential:
            raise AuthenticationError(AuthenticationError.MISSING_FIELDS)

        # Check if UserModel is available
        if UserModel is None:
            raise UserModelNotAvailableError(
                UserModelNotAvailableError.MODEL_NOT_AVAILABLE
            )

        # Get user and verify credentials
        model = UserModel
        user = model.query.filter_by(username=username).first()

        if not user or not verify_credential(auth_credential, user.password_hash):
            logger.warning(
                "Authentication failed for username: %s",
                username,
                extra={"username": username},
            )
            raise AuthenticationError(AuthenticationError.INVALID_CREDENTIALS)

        # Generate JWT token
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(seconds=self.token_expiry),
            "username": user.username,
            "email": user.email,
        }

        token = jwt.encode(payload, self.token_secret, algorithm="HS256")

        logger.info("User authenticated successfully", extra={"user_id": user.id})

        created_at = getattr(user, "created_at", None)
        updated_at = getattr(user, "updated_at", None)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
            "token": token,
            "token_expires": payload["exp"].isoformat(),
        }

    def validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate a JWT token.

        Args:
            token: JWT token to validate

        Returns:
            Dict containing decoded token data

        Raises:
            TokenError: If token is invalid or expired

        """
        try:
            payload = jwt.decode(token, self.token_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as e:
            logger.warning("Authentication verification failed: expired material")
            raise TokenError(TokenError.TOKEN_EXPIRED) from e
        except jwt.InvalidTokenError as e:
            logger.warning("Authentication verification failed: invalid material")
            raise TokenError(TokenError.INVALID_TOKEN) from e
        except Exception:
            logger.exception("Token verification failed")
            raise
        else:
            return payload

    def generate_token(self, user_id: str, expiry: int | None = None) -> str:
        """
        Generate a JWT token.

        Args:
            user_id: ID of the user to generate token for
            expiry: Token expiry time in seconds (optional)

        Returns:
            Generated JWT token string

        """
        now = datetime.now(tz=timezone.utc)
        expiry = now + timedelta(seconds=expiry or self.token_expiry)

        payload = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": expiry.timestamp(),
            "jti": str(uuid.uuid4()),  # Add unique JWT ID to prevent replay attacks
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

    def refresh_token(self, token: str) -> str:
        """
        Refresh an existing JWT token.

        Args:
            token: Existing JWT token to refresh

        Returns:
            New JWT token string

        Raises:
            TokenError: If token is invalid or expired

        """
        # Validate the existing token
        payload = self.validate_token(token)

        # Generate a new token with the same subject but updated expiry
        return self.generate_token(payload["sub"])
