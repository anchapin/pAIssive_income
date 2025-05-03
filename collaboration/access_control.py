"""
Role-based access control for the collaboration module.

This module provides classes for managing roles and permissions
to control access to workspaces, projects, and resources.
"""

import enum
import logging
from typing import Any, Dict, List, Optional, Set

# Set up logging
logger = logging.getLogger(__name__)


class Permission(enum.Enum):
    """Permissions that can be granted to roles."""

    # Special permission that grants all permissions
    ALL = "all"

    # Workspace permissions
    VIEW_WORKSPACE = "view_workspace"
    EDIT_WORKSPACE = "edit_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    MANAGE_MEMBERS = "manage_members"

    # Project permissions
    CREATE_PROJECT = "create_project"
    VIEW_ALL_PROJECTS = "view_all_projects"
    VIEW_ASSIGNED_PROJECTS = "view_assigned_projects"
    EDIT_ALL_PROJECTS = "edit_all_projects"
    EDIT_ASSIGNED_PROJECTS = "edit_assigned_projects"
    DELETE_PROJECT = "delete_project"

    # Role permissions
    MANAGE_ROLES = "manage_roles"

    # Version control permissions
    CREATE_VERSION = "create_version"
    VIEW_VERSION_HISTORY = "view_version_history"
    RESTORE_VERSION = "restore_version"

    # Comment permissions
    ADD_COMMENT = "add_comment"
    EDIT_OWN_COMMENT = "edit_own_comment"
    EDIT_ANY_COMMENT = "edit_any_comment"
    DELETE_OWN_COMMENT = "delete_own_comment"
    DELETE_ANY_COMMENT = "delete_any_comment"

    # Integration permissions
    MANAGE_INTEGRATIONS = "manage_integrations"
    USE_INTEGRATIONS = "use_integrations"


class Role:
    """
    Represents a role with a set of permissions.

    A role defines what actions a user can perform within a workspace or project.
    """

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a new role.

        Args:
            name: Name of the role
            description: Optional description of the role
        """
        self.name = name
        self.description = description or f"Role: {name}"
        self.permissions: Set[Permission] = set()

    def add_permission(self, permission: Permission):
        """
        Add a permission to the role.

        Args:
            permission: Permission to add
        """
        self.permissions.add(permission)
        logger.debug(f"Added permission {permission.name} to role {self.name}")

    def remove_permission(self, permission: Permission):
        """
        Remove a permission from the role.

        Args:
            permission: Permission to remove
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
            logger.debug(f"Removed permission {permission.name} from role {self.name}")

    def has_permission(self, permission: Permission) -> bool:
        """
        Check if the role has a specific permission.

        Args:
            permission: Permission to check

        Returns:
            True if the role has the permission, False otherwise
        """
        # Special case: ALL permission grants all permissions
        if Permission.ALL in self.permissions:
            return True

        return permission in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the role to a dictionary.

        Returns:
            Dictionary representation of the role
        """
        return {
            "name": self.name,
            "description": self.description,
            "permissions": [p.value for p in self.permissions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """
        Create a role from a dictionary.

        Args:
            data: Dictionary representation of the role

        Returns:
            Role object
        """
        role = cls(data["name"], data["description"])
        for perm_value in data["permissions"]:
            try:
                permission = Permission(perm_value)
                role.add_permission(permission)
            except ValueError:
                logger.warning(f"Unknown permission: {perm_value}")

        return role


class RoleManager:
    """
    Manages roles and their permissions.

    This class provides functionality for creating, updating, and managing roles.
    """

    def __init__(self):
        """Initialize the role manager."""
        self.roles: Dict[str, Role] = {}

    def add_role(self, role: Role):
        """
        Add a role to the manager.

        Args:
            role: Role to add
        """
        self.roles[role.name] = role
        logger.debug(f"Added role {role.name} to role manager")

    def remove_role(self, role_name: str) -> bool:
        """
        Remove a role from the manager.

        Args:
            role_name: Name of the role to remove

        Returns:
            True if the role was removed, False otherwise
        """
        if role_name in self.roles:
            del self.roles[role_name]
            logger.debug(f"Removed role {role_name} from role manager")
            return True
        return False

    def get_role(self, role_name: str) -> Optional[Role]:
        """
        Get a role by name.

        Args:
            role_name: Name of the role

        Returns:
            Role object or None if not found
        """
        return self.roles.get(role_name)

    def role_exists(self, role_name: str) -> bool:
        """
        Check if a role exists.

        Args:
            role_name: Name of the role

        Returns:
            True if the role exists, False otherwise
        """
        return role_name in self.roles

    def list_roles(self) -> List[Role]:
        """
        List all roles.

        Returns:
            List of roles
        """
        return list(self.roles.values())

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert all roles to a dictionary.

        Returns:
            Dictionary of role dictionaries
        """
        return {name: role.to_dict() for name, role in self.roles.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> "RoleManager":
        """
        Create a role manager from a dictionary.

        Args:
            data: Dictionary of role dictionaries

        Returns:
            RoleManager object
        """
        manager = cls()
        for role_data in data.values():
            role = Role.from_dict(role_data)
            manager.add_role(role)

        return manager
