"""
Users module for the pAIssive_income project.

This module handles user authentication, authorization, and user management.
"""

from .models import User, Role, Permission
from .auth import create_auth_token, verify_auth_token, hash_password, verify_password
from .permissions import has_permission, PERMISSION_LEVELS

__all__ = [
    'User', 
    'Role',
    'Permission',
    'create_auth_token',
    'verify_auth_token',
    'hash_password',
    'verify_password',
    'has_permission',
    'PERMISSION_LEVELS'
]