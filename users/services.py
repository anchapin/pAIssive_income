"""
User services for authentication and user management.

This module provides service functions for user operations like registration,
authentication, user management, etc.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from .auth import hash_password, verify_password
from .models import User, UserCreate, UserPublic, UserUpdate
from .permissions import ROLES

# Configure logger
logger = logging.getLogger(__name__)

# Mock user database - in production this would be a real database
# This is just for demonstration purposes
USER_DB: Dict[str, User] = {
    "user1": User(
        id="user1",
        username="demo",
        email="demo@example.com",
        name="Demo User",
        password_hash=hash_password("password"),  # In real app, would be pre - hashed
        roles=["user"],
        is_active=True,
        created_at=datetime.utcnow(),
    ),
    "user2": User(
        id="user2",
        username="creator",
        email="creator@example.com",
        name="Creator User",
        password_hash=hash_password("creator123"),  # In real app, would be pre - hashed
        roles=["creator"],
        is_active=True,
        created_at=datetime.utcnow(),
    ),
    "user3": User(
        id="user3",
        username="admin",
        email="admin@example.com",
        name="Admin User",
        password_hash=hash_password("admin123"),  # In real app, would be pre - hashed
        roles=["admin"],
        is_active=True,
        created_at=datetime.utcnow(),
    ),
}


# User lookup indexes
USERNAME_INDEX = {user.username: user.id for user in USER_DB.values()}
EMAIL_INDEX = {user.email: user.id for user in USER_DB.values()}


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.

    Args:
        username: Username to authenticate
        password: Password to verify

    Returns:
        User object if authentication successful, None otherwise
    """
    # Find user by username
    user_id = USERNAME_INDEX.get(username)
    if not user_id:
        logger.warning(f"Authentication attempt for non - existent user: {username}")
        return None

    user = USER_DB.get(user_id)
    if not user:
        logger.error(f"User ID {user_id} in index but not in database")
        return None

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Authentication attempt for inactive user: {username}")
        return None

    # Verify password
    if not verify_password(user.password_hash, password):
        logger.warning(f"Failed authentication attempt for user: {username}")
        return None

    logger.info(f"User authenticated successfully: {username}")
    return user


def create_user(user_data: UserCreate, roles: List[str] = None) -> User:
    """
    Create a new user.

    Args:
        user_data: User creation data
        roles: List of role IDs to assign (defaults to ["user"])

    Returns:
        The created User object

    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    if user_data.username in USERNAME_INDEX:
        raise ValueError(f"Username '{user_data.username}' is already taken")

    # Check if email exists
    if user_data.email in EMAIL_INDEX:
        raise ValueError(f"Email '{user_data.email}' is already registered")

    # Set default roles if none provided
    if roles is None:
        roles = ["user"]

    # Validate roles
    for role in roles:
        if role not in ROLES:
            raise ValueError(f"Invalid role: {role}")

    # Create user ID
    user_id = str(uuid.uuid4())

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create user object
    user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash,
        roles=roles,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Add to database
    USER_DB[user_id] = user

    # Update indexes
    USERNAME_INDEX[user.username] = user_id
    EMAIL_INDEX[user.email] = user_id

    logger.info(f"Created new user: {user.username} (ID: {user_id})")
    return user


def update_user(user_id: str, user_data: UserUpdate) -> Optional[User]:
    """
    Update an existing user.

    Args:
        user_id: ID of the user to update
        user_data: User update data

    Returns:
        Updated User object, or None if user not found

    Raises:
        ValueError: If attempting to use an email that already exists for another user
    """
    # Check if user exists
    user = USER_DB.get(user_id)
    if not user:
        logger.warning(f"Attempted to update non - existent user ID: {user_id}")
        return None

    # Update email if provided
    if user_data.email is not None and user_data.email != user.email:
        # Check if email is already registered to another user
        if user_data.email in EMAIL_INDEX and EMAIL_INDEX[user_data.email] != user_id:
            raise ValueError(f"Email '{user_data.email}' is already registered")

        # Update email index
        del EMAIL_INDEX[user.email]
        EMAIL_INDEX[user_data.email] = user_id

        # Update user email
        user.email = user_data.email

    # Update name if provided
    if user_data.name is not None:
        user.name = user_data.name

    # Update password if provided
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)

    # Update timestamp
    user.updated_at = datetime.utcnow()

    logger.info(f"Updated user: {user.username} (ID: {user_id})")
    return user


def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        user_id: User ID to look up

    Returns:
        User object if found, None otherwise
    """
    return USER_DB.get(user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        username: Username to look up

    Returns:
        User object if found, None otherwise
    """
    user_id = USERNAME_INDEX.get(username)
    if not user_id:
        return None
    return USER_DB.get(user_id)


def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        email: Email to look up

    Returns:
        User object if found, None otherwise
    """
    user_id = EMAIL_INDEX.get(email)
    if not user_id:
        return None
    return USER_DB.get(user_id)


def list_users(skip: int = 0, limit: int = 100) -> List[UserPublic]:
    """
    List users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of UserPublic objects
    """
    # Get subset of users with pagination
    users = list(USER_DB.values())[skip : skip + limit]

    # Convert to UserPublic objects
    public_users = [
        UserPublic(
            id=user.id,
            username=user.username,
            email=user.email,
            name=user.name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
        )
        for user in users
    ]

    return public_users
