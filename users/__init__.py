"""
Users module for the pAIssive_income project.

This module handles user authentication, authorization, and user management.
"""

from .auth import create_auth_token, hash_password, verify_auth_token, verify_password
from .models import Permission, Role, User, UserCreate, UserPublic, UserUpdate
from .password_reset import (
    cleanup_expired_tokens,
    generate_password_reset_token,
    reset_password,
)
from .permissions import PERMISSION_LEVELS, has_permission
from .rate_limiting import (
    cleanup_rate_limiting_data,
    rate_limit_login,
    record_login_attempt,
)
from .session_management import (
    cleanup_expired_sessions,
    create_session,
    get_session,
    get_user_sessions,
    terminate_all_user_sessions,
    terminate_session,
    update_session_activity,
)
from .token_refresh import (
    blacklist_token,
    cleanup_blacklist,
    create_refresh_token,
    refresh_auth_token,
)

__all__ = [
    # Models
    "User",
    "Role",
    "Permission",
    "UserCreate",
    "UserUpdate",
    "UserPublic",
    # Authentication
    "create_auth_token",
    "verify_auth_token",
    "hash_password",
    "verify_password",
    # Authorization
    "has_permission",
    "PERMISSION_LEVELS",
    # Password Reset
    "generate_password_reset_token",
    "reset_password",
    "cleanup_expired_tokens",
    # Token Refresh
    "create_refresh_token",
    "refresh_auth_token",
    "blacklist_token",
    "cleanup_blacklist",
    # Rate Limiting
    "rate_limit_login",
    "record_login_attempt",
    "cleanup_rate_limiting_data",
    # Session Management
    "create_session",
    "get_session",
    "get_user_sessions",
    "update_session_activity",
    "terminate_session",
    "terminate_all_user_sessions",
    "cleanup_expired_sessions",
]
