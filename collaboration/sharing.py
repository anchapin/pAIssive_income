"""
Project sharing functionality for the collaboration module.

This module provides classes for sharing projects between users and workspaces,
with appropriate permissions and access controls.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from .errors import SharingError

# Set up logging
logger = logging.getLogger(__name__)


class SharingPermission(Enum):
    """Permissions that can be granted when sharing a project."""

    VIEW = "view"
    EDIT = "edit"
    MANAGE = "manage"
    FULL_ACCESS = "full_access"


class ProjectSharing:
    """
    Manages project sharing between users and workspaces.

    This class provides functionality for sharing projects with specific permissions,
    managing shared projects, and controlling access to shared resources.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the project sharing manager.

        Args:
            storage_path: Path where sharing data will be stored
        """
        self.storage_path = storage_path or "sharing"
        os.makedirs(self.storage_path, exist_ok=True)

        self.shared_projects: Dict[str, Dict[str, Any]] = {}
        self.shared_links: Dict[str, Dict[str, Any]] = {}

        self._load_sharing_data()

    def _load_sharing_data(self):
        """Load sharing data from disk."""
        projects_file = os.path.join(self.storage_path, "shared_projects.json")
        links_file = os.path.join(self.storage_path, "shared_links.json")

        if os.path.exists(projects_file):
            try:
                with open(projects_file, "r") as f:
                    self.shared_projects = json.load(f)
                logger.info(f"Loaded {len(self.shared_projects)} shared projects")
            except Exception as e:
                logger.error(f"Failed to load shared projects: {e}")
                self.shared_projects = {}

        if os.path.exists(links_file):
            try:
                with open(links_file, "r") as f:
                    self.shared_links = json.load(f)
                logger.info(f"Loaded {len(self.shared_links)} shared links")
            except Exception as e:
                logger.error(f"Failed to load shared links: {e}")
                self.shared_links = {}

    def _save_sharing_data(self):
        """Save sharing data to disk."""
        projects_file = os.path.join(self.storage_path, "shared_projects.json")
        links_file = os.path.join(self.storage_path, "shared_links.json")

        with open(projects_file, "w") as f:
            json.dump(self.shared_projects, f, indent=2)

        with open(links_file, "w") as f:
            json.dump(self.shared_links, f, indent=2)

    def share_project_with_user(
        self,
        project_id: str,
        user_id: str,
        permission: SharingPermission,
        shared_by: str,
        workspace_id: Optional[str] = None,
        expiry: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Share a project with a specific user.

        Args:
            project_id: ID of the project to share
            user_id: ID of the user to share with
            permission: Permission to grant
            shared_by: ID of the user sharing the project
            workspace_id: Optional ID of the workspace containing the project
            expiry: Optional expiry time in seconds

        Returns:
            Sharing information

        Raises:
            SharingError: If the project is already shared with the user
        """
        # Create a unique ID for this sharing
        sharing_id = str(uuid.uuid4())

        # Check if project is already shared with this user
        for share_info in self.shared_projects.values():
            if (
                share_info["project_id"] == project_id
                and share_info["shared_with_user"] == user_id
                and not share_info.get("revoked", False)
            ):
                raise SharingError(
                    f"Project {project_id} is already shared with user {user_id}"
                )

        # Calculate expiry time if provided
        expires_at = None
        if expiry:
            expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()

        # Create sharing information
        share_info = {
            "sharing_id": sharing_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "shared_with_user": user_id,
            "permission": permission.value,
            "shared_by": shared_by,
            "shared_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "revoked": False,
        }

        self.shared_projects[sharing_id] = share_info
        self._save_sharing_data()

        logger.info(
            f"Shared project {project_id} with user {user_id} (permission: {permission.value})"
        )
        return share_info

    def share_project_with_workspace(
        self,
        project_id: str,
        source_workspace_id: str,
        target_workspace_id: str,
        permission: SharingPermission,
        shared_by: str,
        expiry: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Share a project with another workspace.

        Args:
            project_id: ID of the project to share
            source_workspace_id: ID of the workspace containing the project
            target_workspace_id: ID of the workspace to share with
            permission: Permission to grant
            shared_by: ID of the user sharing the project
            expiry: Optional expiry time in seconds

        Returns:
            Sharing information

        Raises:
            SharingError: If the project is already shared with the workspace
        """
        # Create a unique ID for this sharing
        sharing_id = str(uuid.uuid4())

        # Check if project is already shared with this workspace
        for share_info in self.shared_projects.values():
            if (
                share_info["project_id"] == project_id
                and share_info.get("shared_with_workspace") == target_workspace_id
                and not share_info.get("revoked", False)
            ):
                raise SharingError(
                    f"Project {project_id} is already shared with workspace {target_workspace_id}"
                )

        # Calculate expiry time if provided
        expires_at = None
        if expiry:
            expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()

        # Create sharing information
        share_info = {
            "sharing_id": sharing_id,
            "project_id": project_id,
            "source_workspace_id": source_workspace_id,
            "shared_with_workspace": target_workspace_id,
            "permission": permission.value,
            "shared_by": shared_by,
            "shared_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "revoked": False,
        }

        self.shared_projects[sharing_id] = share_info
        self._save_sharing_data()

        logger.info(
            f"Shared project {project_id} with workspace {target_workspace_id} (permission: {permission.value})"
        )
        return share_info

    def create_sharing_link(
        self,
        project_id: str,
        permission: SharingPermission,
        created_by: str,
        workspace_id: Optional[str] = None,
        expiry: Optional[int] = None,
        max_uses: Optional[int] = None,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a sharing link for a project.

        Args:
            project_id: ID of the project to share
            permission: Permission to grant
            created_by: ID of the user creating the link
            workspace_id: Optional ID of the workspace containing the project
            expiry: Optional expiry time in seconds
            max_uses: Optional maximum number of uses
            password: Optional password to protect the link

        Returns:
            Link information
        """
        # Create a unique ID for this link
        link_id = str(uuid.uuid4())

        # Calculate expiry time if provided
        expires_at = None
        if expiry:
            expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()

        # Create link information
        link_info = {
            "link_id": link_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "permission": permission.value,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "max_uses": max_uses,
            "uses": 0,
            "password": password,
            "revoked": False,
        }

        self.shared_links[link_id] = link_info
        self._save_sharing_data()

        logger.info(
            f"Created sharing link for project {project_id} (permission: {permission.value})"
        )
        return link_info

    def revoke_sharing(self, sharing_id: str, revoked_by: str) -> bool:
        """
        Revoke a project sharing.

        Args:
            sharing_id: ID of the sharing to revoke
            revoked_by: ID of the user revoking the sharing

        Returns:
            True if the sharing was revoked, False otherwise

        Raises:
            SharingError: If the sharing does not exist
        """
        if sharing_id not in self.shared_projects:
            raise SharingError(f"Sharing {sharing_id} does not exist")

        self.shared_projects[sharing_id]["revoked"] = True
        self.shared_projects[sharing_id]["revoked_by"] = revoked_by
        self.shared_projects[sharing_id]["revoked_at"] = datetime.now().isoformat()

        self._save_sharing_data()

        logger.info(f"Revoked sharing {sharing_id}")
        return True

    def revoke_link(self, link_id: str, revoked_by: str) -> bool:
        """
        Revoke a sharing link.

        Args:
            link_id: ID of the link to revoke
            revoked_by: ID of the user revoking the link

        Returns:
            True if the link was revoked, False otherwise

        Raises:
            SharingError: If the link does not exist
        """
        if link_id not in self.shared_links:
            raise SharingError(f"Link {link_id} does not exist")

        self.shared_links[link_id]["revoked"] = True
        self.shared_links[link_id]["revoked_by"] = revoked_by
        self.shared_links[link_id]["revoked_at"] = datetime.now().isoformat()

        self._save_sharing_data()

        logger.info(f"Revoked link {link_id}")
        return True

    def use_link(self, link_id: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Use a sharing link to access a project.

        Args:
            link_id: ID of the link
            password: Optional password for protected links

        Returns:
            Project information

        Raises:
            SharingError: If the link does not exist, is revoked, expired, or password is incorrect
        """
        if link_id not in self.shared_links:
            raise SharingError(f"Link {link_id} does not exist")

        link_info = self.shared_links[link_id]

        # Check if link is revoked
        if link_info.get("revoked", False):
            raise SharingError(f"Link {link_id} has been revoked")

        # Check if link is expired
        if link_info.get("expires_at"):
            expires_at = datetime.fromisoformat(link_info["expires_at"])
            if datetime.now() > expires_at:
                raise SharingError(f"Link {link_id} has expired")

        # Check if link has reached maximum uses
        if (
            link_info.get("max_uses")
            and link_info.get("uses", 0) >= link_info["max_uses"]
        ):
            raise SharingError(f"Link {link_id} has reached maximum uses")

        # Check password if required
        if link_info.get("password") and link_info["password"] != password:
            raise SharingError(f"Invalid password for link {link_id}")

        # Increment uses
        link_info["uses"] = link_info.get("uses", 0) + 1
        self._save_sharing_data()

        logger.info(f"Used link {link_id} to access project {link_info['project_id']}")
        return {
            "project_id": link_info["project_id"],
            "workspace_id": link_info.get("workspace_id"),
            "permission": link_info["permission"],
        }

    def get_user_shared_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all projects shared with a user.

        Args:
            user_id: ID of the user

        Returns:
            List of shared project information
        """
        shared_projects = []

        for share_info in self.shared_projects.values():
            if share_info.get("shared_with_user") == user_id and not share_info.get(
                "revoked", False
            ):

                # Check if sharing has expired
                if share_info.get("expires_at"):
                    expires_at = datetime.fromisoformat(share_info["expires_at"])
                    if datetime.now() > expires_at:
                        continue

                shared_projects.append(share_info)

        return shared_projects

    def get_workspace_shared_projects(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Get all projects shared with a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of shared project information
        """
        shared_projects = []

        for share_info in self.shared_projects.values():
            if share_info.get(
                "shared_with_workspace"
            ) == workspace_id and not share_info.get("revoked", False):

                # Check if sharing has expired
                if share_info.get("expires_at"):
                    expires_at = datetime.fromisoformat(share_info["expires_at"])
                    if datetime.now() > expires_at:
                        continue

                shared_projects.append(share_info)

        return shared_projects

    def get_project_sharing(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all sharing information for a project.

        Args:
            project_id: ID of the project

        Returns:
            List of sharing information
        """
        project_sharing = []

        for share_info in self.shared_projects.values():
            if share_info["project_id"] == project_id and not share_info.get(
                "revoked", False
            ):
                # Check if sharing has expired
                if share_info.get("expires_at"):
                    expires_at = datetime.fromisoformat(share_info["expires_at"])
                    if datetime.now() > expires_at:
                        continue

                project_sharing.append(share_info)

        return project_sharing

    def get_project_links(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all sharing links for a project.

        Args:
            project_id: ID of the project

        Returns:
            List of link information
        """
        project_links = []

        for link_info in self.shared_links.values():
            if link_info["project_id"] == project_id and not link_info.get(
                "revoked", False
            ):
                # Check if link has expired
                if link_info.get("expires_at"):
                    expires_at = datetime.fromisoformat(link_info["expires_at"])
                    if datetime.now() > expires_at:
                        continue

                project_links.append(link_info)

        return project_links
