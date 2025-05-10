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
from users.auth import hash_credential, verify_credential

# Database imports
from flask import current_app
from flask import has_app_context
from flask import Flask
from flask import g
from flask import cli
from flask import Blueprint

from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from flask import current_app
from flask import has_app_context

from flask import current_app
from flask import has_app_context

from flask import current_app
from flask import has_app_context

# Import the db and User model from the Flask app
from flask import current_app
from flask import has_app_context
from flask import g

from flask import current_app
from flask import has_app_context

from flask import current_app
from flask import has_app_context

from flask import current_app

from flask import has_app_context

try:
    from flask import current_app
    from flask import has_app_context
    from flask import g
    from flask import cli
    from flask_sqlalchemy import SQLAlchemy

    from flask import current_app
    from flask_sqlalchemy import SQLAlchemy
    from flask import current_app
    from flask import has_app_context

    from flask import current_app
    from flask import has_app_context

    from flask import current_app
    from flask import has_app_context

    from flask import current_app

    from flask import has_app_context

    # Import db and User from the actual Flask app package
    from flask import current_app
    from flask import has_app_context
    from flask.models import User, db
except ImportError:
    User = None
    db = None

# Initialize logger
logger = get_logger(__name__)


class UserService:
    """Service for user management."""

    def __init__(self, token_secret=None, token_expiry=None):
        """Initialize the user service.

        Args:
        ----
            token_secret: Secret for JWT token generation
            token_expiry: Expiry time for JWT tokens in seconds

        """
        # Don't set a default token secret - require it to be provided
        if not token_secret:
            logger.error("No token secret provided")
            raise ValueError("Authentication token secret must be provided")

        # Enhanced security: Store token secret in a private variable
        self.__token_secret = token_secret

        logger.debug("Token secret configured successfully")

        self.token_expiry = token_expiry or 3600  # 1 hour default

    @property
    def token_secret(self):
        """Securely access the token secret."""
        return self.__token_secret

    def create_user(
        self, username: str, email: str, auth_credential: str, **kwargs
    ) -> Dict[str, Any]:
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
            raise ValueError(
                "Username, email, and authentication credential are required"
            )

        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            if existing_user.username == username:
                raise ValueError(f"User with username '{username}' already exists")
            else:
                raise ValueError(f"User with email '{email}' already exists")

        # Hash the credential
        hashed_credential = hash_credential(auth_credential)

        # Create User model instance
        user = User(
            username=username,
            email=email,
            password_hash=hashed_credential,
            **{k: v for k, v in kwargs.items() if hasattr(User, k)},
        )
        db.session.add(user)
        db.session.commit()

        logger.info("User created successfully", extra={"user_id": user.id})

        # Return user data without sensitive information
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": getattr(user, "created_at", None),
            "updated_at": getattr(user, "updated_at", None),
        }

    def authenticate_user(
        self, username_or_email: str, auth_credential: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authenticate a user.

        Args:
        ----
            username_or_email: Username or email of the user
            auth_credential: Authentication credential to verify

        Returns:
        -------
            Tuple[bool, Optional[Dict]]: (success, user_data)

        """
        # Find the user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
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
            user.last_login = datetime.utcnow()
            db.session.commit()

        # Return user data without sensitive information
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        logger.info("Authentication successful", extra={"user_id": user.id})
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
            if isinstance(value, str) and len(value) > 1000:
                logger.warning(f"Oversized claim '{key}' was truncated in token")
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
        # Ensure we return a string
        if isinstance(auth_token, bytes):
            return auth_token.decode("utf-8")
        return str(auth_token)  # Explicitly cast to string to satisfy mypy

    def verify_token(self, auth_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify a JWT token.

        Args:
        ----
            auth_token: The JWT token to verify

        Returns:
        -------
            Tuple[bool, Optional[Dict]]: (success, payload)

        """
        try:
            payload = jwt.decode(auth_token, self.token_secret, algorithms=["HS256"])
            return True, payload
        except jwt.ExpiredSignatureError:
            # Don't include token details in logs
            logger.warning("Authentication verification failed: expired material")
            return False, None
        except jwt.InvalidTokenError:
            # Don't include the specific error type or token details in logs
            logger.warning("Authentication verification failed: invalid material")
            return False, None
