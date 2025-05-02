"""
Authorization and permission checking utilities for the pAIssive_income project.

This module includes functions for checking user permissions and role-based authorization.
"""

import logging
from enum import IntEnum
from typing import List, Optional, Set

# Configure logger
logger = logging.getLogger(__name__)


# Define permission levels as an enum
class PermissionLevel(IntEnum):
    """
    Enum for permission levels, with higher values representing higher access levels.
    """

    NONE = 0
    VIEW = 10
    EDIT = 20
    CREATE = 30
    DELETE = 40
    ADMIN = 100


# Export for easier usage
PERMISSION_LEVELS = PermissionLevel


# Permission registry - mapping of permission IDs to their details
# This would be stored in a database in a full implementation
PERMISSIONS = {
    # Niche analysis permissions
    "niche:view": {"name": "View Niche Analysis", "level": PermissionLevel.VIEW},
    "niche:create": {"name": "Create Niche Analysis", "level": PermissionLevel.CREATE},
    "niche:edit": {"name": "Edit Niche Analysis", "level": PermissionLevel.EDIT},
    # Solution permissions
    "solution:view": {"name": "View Solutions", "level": PermissionLevel.VIEW},
    "solution:create": {"name": "Create Solutions", "level": PermissionLevel.CREATE},
    "solution:edit": {"name": "Edit Solutions", "level": PermissionLevel.EDIT},
    # Monetization permissions
    "monetization:view": {
        "name": "View Monetization Strategies",
        "level": PermissionLevel.VIEW,
    },
    "monetization:create": {
        "name": "Create Monetization Strategies",
        "level": PermissionLevel.CREATE,
    },
    "monetization:edit": {
        "name": "Edit Monetization Strategies",
        "level": PermissionLevel.EDIT,
    },
    # Marketing permissions
    "marketing:view": {
        "name": "View Marketing Campaigns",
        "level": PermissionLevel.VIEW,
    },
    "marketing:create": {
        "name": "Create Marketing Campaigns",
        "level": PermissionLevel.CREATE,
    },
    "marketing:edit": {
        "name": "Edit Marketing Campaigns",
        "level": PermissionLevel.EDIT,
    },
    # User management permissions
    "user:view": {"name": "View Users", "level": PermissionLevel.VIEW},
    "user:create": {"name": "Create Users", "level": PermissionLevel.CREATE},
    "user:edit": {"name": "Edit Users", "level": PermissionLevel.EDIT},
    "user:delete": {"name": "Delete Users", "level": PermissionLevel.DELETE},
    # Admin permissions
    "admin:settings": {
        "name": "Manage System Settings",
        "level": PermissionLevel.ADMIN,
    },
    "admin:logs": {"name": "View System Logs", "level": PermissionLevel.ADMIN},
}


# Role registry - mapping of role IDs to their permissions
# This would be stored in a database in a full implementation
ROLES = {
    "user": {
        "name": "Basic User",
        "description": "Basic user with limited permissions",
        "permissions": [
            "niche:view",
            "niche:create",
            "solution:view",
            "monetization:view",
            "marketing:view",
        ],
    },
    "creator": {
        "name": "Content Creator",
        "description": "User who can create content and manage their own projects",
        "permissions": [
            "niche:view",
            "niche:create",
            "niche:edit",
            "solution:view",
            "solution:create",
            "solution:edit",
            "monetization:view",
            "monetization:create",
            "monetization:edit",
            "marketing:view",
            "marketing:create",
            "marketing:edit",
        ],
    },
    "admin": {
        "name": "Administrator",
        "description": "Full administrative access",
        "permissions": [
            "niche:view",
            "niche:create",
            "niche:edit",
            "solution:view",
            "solution:create",
            "solution:edit",
            "monetization:view",
            "monetization:create",
            "monetization:edit",
            "marketing:view",
            "marketing:create",
            "marketing:edit",
            "user:view",
            "user:create",
            "user:edit",
            "user:delete",
            "admin:settings",
            "admin:logs",
        ],
    },
}


def get_user_permissions(roles: List[str]) -> Set[str]:
    """
    Get all permissions assigned to a user based on their roles.

    Args:
        roles: List of role IDs

    Returns:
        Set of permission IDs
    """
    permissions = set()

    for role_id in roles:
        if role_id in ROLES:
            role_permissions = ROLES[role_id].get("permissions", [])
            permissions.update(role_permissions)

    return permissions


def has_permission(
    user_roles: List[str],
    required_permission: str,
    required_level: Optional[PermissionLevel] = None,
) -> bool:
    """
    Check if a user has a specific permission.

    Args:
        user_roles: List of the user's role IDs
        required_permission: Permission ID to check
        required_level: Optional minimum permission level required

    Returns:
        True if the user has the required permission, False otherwise
    """
    # If admin role is present, grant all permissions
    if "admin" in user_roles:
        return True

    # Get user permissions
    user_permissions = get_user_permissions(user_roles)

    # Check for the specific permission
    has_specific_permission = required_permission in user_permissions

    # If a level is required, check if the user has permissions at or above that level
    if required_level is not None:
        # Check permissions for this resource at or above the required level
        permission_base = required_permission.split(":")[0]  # e.g., "niche" from "niche:view"

        for perm in user_permissions:
            if not perm.startswith(permission_base + ":"):
                continue

            # Get the level of this permission
            perm_details = PERMISSIONS.get(perm, {})
            perm_level = perm_details.get("level", PermissionLevel.NONE)

            # If the user has a permission with a level >= the required level, grant access
            if perm_level >= required_level:
                return True

        # No permission found at the required level
        return False

    # Just check if the specific permission is granted
    return has_specific_permission
