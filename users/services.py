"""services - Module for users.services.

This module provides services for user management, including user creation,
authentication, and profile management.
"""

# Standard library imports
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

# Third-party imports
import jwt

from common_utils.logging import get_logger

# Local imports
from users.auth import hash_password, verify_password

# Initialize logger
logger = get_logger(__name__)


class UserService:
    """Service for user management."""

    def __init__(self, user_repository=None, token_secret=None, token_expiry=None):
        """Initialize the user service.

        Args:
        ----
            user_repository: Repository for user data
            token_secret: Secret for JWT token generation
            token_expiry: Expiry time for JWT tokens in seconds

        """
        self.user_repository = user_repository
        self.token_secret = token_secret or "default_secret_change_in_production"
        self.token_expiry = token_expiry or 3600  # 1 hour default

    def create_user(
        self, username: str, email: str, password: str, **kwargs
    ) -> Dict[str, Any]:
        """Create a new user.

        Args:
        ----
            username: Username for the new user
            email: Email for the new user
            password: Password for the new user
            **kwargs: Additional user data

        Returns:
        -------
            Dict: The created user data (without password)

        """
        # Validate inputs
        if not username or not email or not password:
            raise ValueError("Username, email, and password are required")

        # Check if user already exists
        if self.user_repository and self.user_repository.find_by_username(username):
            raise ValueError(f"User with username '{username}' already exists")

        if self.user_repository and self.user_repository.find_by_email(email):
            raise ValueError(f"User with email '{email}' already exists")

        # Hash the password
        hashed_password = hash_password(password)

        # Create user data
        user_data = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs,
        }

        # Save the user
        if self.user_repository:
            user_id = self.user_repository.create(user_data)
            user_data["id"] = user_id

        # Return user data without password
        user_data.pop("password_hash", None)
        logger.info(f"User created: {username}")
        return user_data

    def authenticate_user(
        self, username_or_email: str, password: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authenticate a user.

        Args:
        ----
            username_or_email: Username or email of the user
            password: Password to verify

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
            logger.warning(
                f"Authentication failed: User not found: {username_or_email}"
            )
            return False, None

        # Verify the password
        if not verify_password(password, user.get("password_hash", b"")):
            logger.warning(
                f"Authentication failed: Invalid password for user: {username_or_email}"
            )
            return False, None

        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        if self.user_repository:
            self.user_repository.update(user["id"], {"last_login": user["last_login"]})

        # Return user data without password
        user_data = user.copy()
        user_data.pop("password_hash", None)
        logger.info(f"User authenticated: {username_or_email}")
        return True, user_data

    def generate_token(self, user_id: str, **additional_claims) -> str:
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

        payload = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": expiry.timestamp(),
            **additional_claims,
        }

        token = jwt.encode(payload, self.token_secret, algorithm="HS256")
        logger.debug(f"Token generated for user: {user_id}")
        # Ensure we return a string
        if isinstance(token, bytes):
            return str(token.decode("utf-8"))
        return str(token)

    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify a JWT token.

        Args:
        ----
            token: The JWT token to verify

        Returns:
        -------
            Tuple[bool, Optional[Dict]]: (success, payload)

        """
        try:
            payload = jwt.decode(token, self.token_secret, algorithms=["HS256"])
            return True, payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: Token expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {e}")
            return False, None
