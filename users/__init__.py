"""
Users module for the pAIssive_income project.

This module handles user authentication, authorization, and user management.
"""

from .models import User, Role, Permission, UserCreate, UserUpdate, UserPublic
from .auth import create_auth_token, verify_auth_token, hash_password, verify_password
from .permissions import has_permission, PERMISSION_LEVELS
from .password_reset import generate_password_reset_token, reset_password, cleanup_expired_tokens
from .token_refresh import create_refresh_token, refresh_auth_token, blacklist_token, cleanup_blacklist
from .rate_limiting import rate_limit_login, record_login_attempt, cleanup_rate_limiting_data
from .session_management import (
    create_session, get_session, get_user_sessions, update_session_activity,
    terminate_session, terminate_all_user_sessions, cleanup_expired_sessions
)

__all__ = [
    # Models
    'User',
    'Role',
    'Permission',
    'UserCreate',
    'UserUpdate',
    'UserPublic',

    # Authentication
    'create_auth_token',
    'verify_auth_token',
    'hash_password',
    'verify_password',

    # Authorization
    'has_permission',
    'PERMISSION_LEVELS',

    # Password Reset
    'generate_password_reset_token',
    'reset_password',
    'cleanup_expired_tokens',

    # Token Refresh
    'create_refresh_token',
    'refresh_auth_token',
    'blacklist_token',
    'cleanup_blacklist',

    # Rate Limiting
    'rate_limit_login',
    'record_login_attempt',
    'cleanup_rate_limiting_data',

    # Session Management
    'create_session',
    'get_session',
    'get_user_sessions',
    'update_session_activity',
    'terminate_session',
    'terminate_all_user_sessions',
    'cleanup_expired_sessions'
]