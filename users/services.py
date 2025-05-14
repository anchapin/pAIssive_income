"""User service module."""

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, Union
import uuid

import jwt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from app_flask.models import UserModel
from users.auth import verify_credential
from common_utils.logging import get_logger

logger = get_logger(__name__)
db = SQLAlchemy()

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    USERNAME_REQUIRED = "Username is required"
    EMAIL_REQUIRED = "Email is required"
    PASSWORD_REQUIRED = "Password is required"
    TOKEN_REQUIRED = "Token secret is required"

class DatabaseSessionNotAvailableError(Exception):
    """Raised when database session is not available."""
    pass

class UserExistsError(Exception):
    """Raised when user already exists."""
    USERNAME_EXISTS = "Username already exists"
    EMAIL_EXISTS = "Email address already exists"

class UserModelNotAvailableError(Exception):
    """Raised when User model is not available."""
    pass

class TokenError(Exception):
    """Raised when token validation fails."""
    pass

class UserService:
    """Service for user management operations."""

    def __init__(self, token_secret: str):
        """Initialize the service.
        
        Args:
            token_secret: Secret key for JWT token generation/verification
            
        Raises:
            AuthenticationError: If token_secret is not provided
        """
        if not token_secret:
            logger.error("No token secret provided")
            raise AuthenticationError(AuthenticationError.TOKEN_REQUIRED)
            
        self.__token_secret = token_secret
        self.__token_expiry = 3600  # 1 hour default

    @property
    def token_secret(self) -> str:
        """Get the token secret."""
        return self.__token_secret

    def create_user(self, username: str, email: str, password: str) -> Dict:
        """Create a new user.
        
        Args:
            username: Username for the new user
            email: Email address for the new user
            password: Password for the new user
            
        Returns:
            Dict containing user data
            
        Raises:
            AuthenticationError: If required fields are missing
            UserExistsError: If username/email already exists
            UserModelNotAvailableError: If User model not available
            DatabaseSessionNotAvailableError: If db session not available
        """
        # Validate inputs
        if not username:
            raise AuthenticationError(AuthenticationError.USERNAME_REQUIRED)
        if not email:
            raise AuthenticationError(AuthenticationError.EMAIL_REQUIRED) 
        if not password:
            raise AuthenticationError(AuthenticationError.PASSWORD_REQUIRED)

        # Check if db session is available
        if db.session is None:
            raise DatabaseSessionNotAvailableError()

        # Check if username exists
        existing_user = UserModel.query.filter(
            (UserModel.username == username) | (UserModel.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                raise UserExistsError(UserExistsError.USERNAME_EXISTS)
            raise UserExistsError(UserExistsError.EMAIL_EXISTS)

        # Create user
        new_user = UserModel(
            username=username,
            email=email,
            password=password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user: {e}")
            db.session.rollback()
            raise DatabaseSessionNotAvailableError()

        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username of the user
            password: Password to verify
            
        Returns:
            Tuple of (success, user_data)
            success: True if authentication successful
            user_data: Dict of user data if successful, None otherwise
        """
        if not username or not password:
            return False, None

        user = UserModel.query.filter_by(username=username).first()
        if not user:
            return False, None

        if not verify_credential(password, user.password_hash):
            return False, None

        try:
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False, None

        return True, {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }

    def generate_token(self, user_id: str, **claims: Dict) -> str:
        """Generate a JWT token for a user.
        
        Args:
            user_id: ID of the user
            claims: Additional claims to include in token
            
        Returns:
            JWT token string
        """
        now = datetime.now(timezone.utc)
        
        # Filter out sensitive claims
        safe_claims = {
            k: str(v)[:1000] + "..." if len(str(v)) > 1000 else v
            for k, v in claims.items()
            if k.lower() not in ["password", "token", "secret", "key"]
        }
        
        payload = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": now.timestamp() + self.__token_expiry,
            "jti": str(uuid.uuid4()),
            **safe_claims
        }
        
        return jwt.encode(payload, self.__token_secret, algorithm="HS256")

    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (success, payload)
            success: True if token is valid
            payload: Dict of token claims if valid, None otherwise
        """
        if not token:
            return False, None

        try:
            payload = jwt.decode(
                token,
                self.__token_secret,
                algorithms=["HS256"]
            )

            # Verify required claims are present
            required_claims = ["sub"]
            if not all(claim in payload for claim in required_claims):
                return False, None

            return True, payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return False, None
