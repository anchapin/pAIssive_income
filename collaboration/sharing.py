"""
"""
Project sharing functionality for the collaboration module.
Project sharing functionality for the collaboration module.


This module provides classes for sharing projects between users and workspaces,
This module provides classes for sharing projects between users and workspaces,
with appropriate permissions and access controls.
with appropriate permissions and access controls.
"""
"""


import json
import json
import logging
import logging
import os
import os
import time
import time
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from enum import Enum
from enum import Enum
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .errors import SharingError
from .errors import SharingError


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class SharingPermission(Enum):
    class SharingPermission(Enum):
    """Permissions that can be granted when sharing a project."""

    VIEW = "view"
    EDIT = "edit"
    MANAGE = "manage"
    FULL_ACCESS = "full_access"


    class ProjectSharing:
    """
    """
    Manages project sharing between users and workspaces.
    Manages project sharing between users and workspaces.


    This class provides functionality for sharing projects with specific permissions,
    This class provides functionality for sharing projects with specific permissions,
    managing shared projects, and controlling access to shared resources.
    managing shared projects, and controlling access to shared resources.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the project sharing manager.
    Initialize the project sharing manager.


    Args:
    Args:
    storage_path: Path where sharing data will be stored
    storage_path: Path where sharing data will be stored
    """
    """
    self.storage_path = storage_path or "sharing"
    self.storage_path = storage_path or "sharing"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    self.shared_projects: Dict[str, Dict[str, Any]] = {}
    self.shared_projects: Dict[str, Dict[str, Any]] = {}
    self.shared_links: Dict[str, Dict[str, Any]] = {}
    self.shared_links: Dict[str, Dict[str, Any]] = {}


    self._load_sharing_data()
    self._load_sharing_data()


    def _load_sharing_data(self):
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
    """
    Share a project with a specific user.
    Share a project with a specific user.


    Args:
    Args:
    project_id: ID of the project to share
    project_id: ID of the project to share
    user_id: ID of the user to share with
    user_id: ID of the user to share with
    permission: Permission to grant
    permission: Permission to grant
    shared_by: ID of the user sharing the project
    shared_by: ID of the user sharing the project
    workspace_id: Optional ID of the workspace containing the project
    workspace_id: Optional ID of the workspace containing the project
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds


    Returns:
    Returns:
    Sharing information
    Sharing information


    Raises:
    Raises:
    SharingError: If the project is already shared with the user
    SharingError: If the project is already shared with the user
    """
    """
    # Create a unique ID for this sharing
    # Create a unique ID for this sharing
    sharing_id = str(uuid.uuid4())
    sharing_id = str(uuid.uuid4())


    # Check if project is already shared with this user
    # Check if project is already shared with this user
    for share_info in self.shared_projects.values():
    for share_info in self.shared_projects.values():
    if (
    if (
    share_info["project_id"] == project_id
    share_info["project_id"] == project_id
    and share_info["shared_with_user"] == user_id
    and share_info["shared_with_user"] == user_id
    and not share_info.get("revoked", False)
    and not share_info.get("revoked", False)
    ):
    ):
    raise SharingError(
    raise SharingError(
    f"Project {project_id} is already shared with user {user_id}"
    f"Project {project_id} is already shared with user {user_id}"
    )
    )


    # Calculate expiry time if provided
    # Calculate expiry time if provided
    expires_at = None
    expires_at = None
    if expiry:
    if expiry:
    expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()
    expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()


    # Create sharing information
    # Create sharing information
    share_info = {
    share_info = {
    "sharing_id": sharing_id,
    "sharing_id": sharing_id,
    "project_id": project_id,
    "project_id": project_id,
    "workspace_id": workspace_id,
    "workspace_id": workspace_id,
    "shared_with_user": user_id,
    "shared_with_user": user_id,
    "permission": permission.value,
    "permission": permission.value,
    "shared_by": shared_by,
    "shared_by": shared_by,
    "shared_at": datetime.now().isoformat(),
    "shared_at": datetime.now().isoformat(),
    "expires_at": expires_at,
    "expires_at": expires_at,
    "revoked": False,
    "revoked": False,
    }
    }


    self.shared_projects[sharing_id] = share_info
    self.shared_projects[sharing_id] = share_info
    self._save_sharing_data()
    self._save_sharing_data()


    logger.info(
    logger.info(
    f"Shared project {project_id} with user {user_id} (permission: {permission.value})"
    f"Shared project {project_id} with user {user_id} (permission: {permission.value})"
    )
    )
    return share_info
    return share_info


    def share_project_with_workspace(
    def share_project_with_workspace(
    self,
    self,
    project_id: str,
    project_id: str,
    source_workspace_id: str,
    source_workspace_id: str,
    target_workspace_id: str,
    target_workspace_id: str,
    permission: SharingPermission,
    permission: SharingPermission,
    shared_by: str,
    shared_by: str,
    expiry: Optional[int] = None,
    expiry: Optional[int] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Share a project with another workspace.
    Share a project with another workspace.


    Args:
    Args:
    project_id: ID of the project to share
    project_id: ID of the project to share
    source_workspace_id: ID of the workspace containing the project
    source_workspace_id: ID of the workspace containing the project
    target_workspace_id: ID of the workspace to share with
    target_workspace_id: ID of the workspace to share with
    permission: Permission to grant
    permission: Permission to grant
    shared_by: ID of the user sharing the project
    shared_by: ID of the user sharing the project
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds


    Returns:
    Returns:
    Sharing information
    Sharing information


    Raises:
    Raises:
    SharingError: If the project is already shared with the workspace
    SharingError: If the project is already shared with the workspace
    """
    """
    # Create a unique ID for this sharing
    # Create a unique ID for this sharing
    sharing_id = str(uuid.uuid4())
    sharing_id = str(uuid.uuid4())


    # Check if project is already shared with this workspace
    # Check if project is already shared with this workspace
    for share_info in self.shared_projects.values():
    for share_info in self.shared_projects.values():
    if (
    if (
    share_info["project_id"] == project_id
    share_info["project_id"] == project_id
    and share_info.get("shared_with_workspace") == target_workspace_id
    and share_info.get("shared_with_workspace") == target_workspace_id
    and not share_info.get("revoked", False)
    and not share_info.get("revoked", False)
    ):
    ):
    raise SharingError(
    raise SharingError(
    f"Project {project_id} is already shared with workspace {target_workspace_id}"
    f"Project {project_id} is already shared with workspace {target_workspace_id}"
    )
    )


    # Calculate expiry time if provided
    # Calculate expiry time if provided
    expires_at = None
    expires_at = None
    if expiry:
    if expiry:
    expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()
    expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()


    # Create sharing information
    # Create sharing information
    share_info = {
    share_info = {
    "sharing_id": sharing_id,
    "sharing_id": sharing_id,
    "project_id": project_id,
    "project_id": project_id,
    "source_workspace_id": source_workspace_id,
    "source_workspace_id": source_workspace_id,
    "shared_with_workspace": target_workspace_id,
    "shared_with_workspace": target_workspace_id,
    "permission": permission.value,
    "permission": permission.value,
    "shared_by": shared_by,
    "shared_by": shared_by,
    "shared_at": datetime.now().isoformat(),
    "shared_at": datetime.now().isoformat(),
    "expires_at": expires_at,
    "expires_at": expires_at,
    "revoked": False,
    "revoked": False,
    }
    }


    self.shared_projects[sharing_id] = share_info
    self.shared_projects[sharing_id] = share_info
    self._save_sharing_data()
    self._save_sharing_data()


    logger.info(
    logger.info(
    f"Shared project {project_id} with workspace {target_workspace_id} (permission: {permission.value})"
    f"Shared project {project_id} with workspace {target_workspace_id} (permission: {permission.value})"
    )
    )
    return share_info
    return share_info


    def create_sharing_link(
    def create_sharing_link(
    self,
    self,
    project_id: str,
    project_id: str,
    permission: SharingPermission,
    permission: SharingPermission,
    created_by: str,
    created_by: str,
    workspace_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    expiry: Optional[int] = None,
    expiry: Optional[int] = None,
    max_uses: Optional[int] = None,
    max_uses: Optional[int] = None,
    password: Optional[str] = None,
    password: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a sharing link for a project.
    Create a sharing link for a project.


    Args:
    Args:
    project_id: ID of the project to share
    project_id: ID of the project to share
    permission: Permission to grant
    permission: Permission to grant
    created_by: ID of the user creating the link
    created_by: ID of the user creating the link
    workspace_id: Optional ID of the workspace containing the project
    workspace_id: Optional ID of the workspace containing the project
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds
    max_uses: Optional maximum number of uses
    max_uses: Optional maximum number of uses
    password: Optional password to protect the link
    password: Optional password to protect the link


    Returns:
    Returns:
    Link information
    Link information
    """
    """
    # Create a unique ID for this link
    # Create a unique ID for this link
    link_id = str(uuid.uuid4())
    link_id = str(uuid.uuid4())


    # Calculate expiry time if provided
    # Calculate expiry time if provided
    expires_at = None
    expires_at = None
    if expiry:
    if expiry:
    expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()
    expires_at = (datetime.now() + timedelta(seconds=expiry)).isoformat()


    # Create link information
    # Create link information
    link_info = {
    link_info = {
    "link_id": link_id,
    "link_id": link_id,
    "project_id": project_id,
    "project_id": project_id,
    "workspace_id": workspace_id,
    "workspace_id": workspace_id,
    "permission": permission.value,
    "permission": permission.value,
    "created_by": created_by,
    "created_by": created_by,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "expires_at": expires_at,
    "expires_at": expires_at,
    "max_uses": max_uses,
    "max_uses": max_uses,
    "uses": 0,
    "uses": 0,
    "password": password,
    "password": password,
    "revoked": False,
    "revoked": False,
    }
    }


    self.shared_links[link_id] = link_info
    self.shared_links[link_id] = link_info
    self._save_sharing_data()
    self._save_sharing_data()


    logger.info(
    logger.info(
    f"Created sharing link for project {project_id} (permission: {permission.value})"
    f"Created sharing link for project {project_id} (permission: {permission.value})"
    )
    )
    return link_info
    return link_info


    def revoke_sharing(self, sharing_id: str, revoked_by: str) -> bool:
    def revoke_sharing(self, sharing_id: str, revoked_by: str) -> bool:
    """
    """
    Revoke a project sharing.
    Revoke a project sharing.


    Args:
    Args:
    sharing_id: ID of the sharing to revoke
    sharing_id: ID of the sharing to revoke
    revoked_by: ID of the user revoking the sharing
    revoked_by: ID of the user revoking the sharing


    Returns:
    Returns:
    True if the sharing was revoked, False otherwise
    True if the sharing was revoked, False otherwise


    Raises:
    Raises:
    SharingError: If the sharing does not exist
    SharingError: If the sharing does not exist
    """
    """
    if sharing_id not in self.shared_projects:
    if sharing_id not in self.shared_projects:
    raise SharingError(f"Sharing {sharing_id} does not exist")
    raise SharingError(f"Sharing {sharing_id} does not exist")


    self.shared_projects[sharing_id]["revoked"] = True
    self.shared_projects[sharing_id]["revoked"] = True
    self.shared_projects[sharing_id]["revoked_by"] = revoked_by
    self.shared_projects[sharing_id]["revoked_by"] = revoked_by
    self.shared_projects[sharing_id]["revoked_at"] = datetime.now().isoformat()
    self.shared_projects[sharing_id]["revoked_at"] = datetime.now().isoformat()


    self._save_sharing_data()
    self._save_sharing_data()


    logger.info(f"Revoked sharing {sharing_id}")
    logger.info(f"Revoked sharing {sharing_id}")
    return True
    return True


    def revoke_link(self, link_id: str, revoked_by: str) -> bool:
    def revoke_link(self, link_id: str, revoked_by: str) -> bool:
    """
    """
    Revoke a sharing link.
    Revoke a sharing link.


    Args:
    Args:
    link_id: ID of the link to revoke
    link_id: ID of the link to revoke
    revoked_by: ID of the user revoking the link
    revoked_by: ID of the user revoking the link


    Returns:
    Returns:
    True if the link was revoked, False otherwise
    True if the link was revoked, False otherwise


    Raises:
    Raises:
    SharingError: If the link does not exist
    SharingError: If the link does not exist
    """
    """
    if link_id not in self.shared_links:
    if link_id not in self.shared_links:
    raise SharingError(f"Link {link_id} does not exist")
    raise SharingError(f"Link {link_id} does not exist")


    self.shared_links[link_id]["revoked"] = True
    self.shared_links[link_id]["revoked"] = True
    self.shared_links[link_id]["revoked_by"] = revoked_by
    self.shared_links[link_id]["revoked_by"] = revoked_by
    self.shared_links[link_id]["revoked_at"] = datetime.now().isoformat()
    self.shared_links[link_id]["revoked_at"] = datetime.now().isoformat()


    self._save_sharing_data()
    self._save_sharing_data()


    logger.info(f"Revoked link {link_id}")
    logger.info(f"Revoked link {link_id}")
    return True
    return True


    def use_link(self, link_id: str, password: Optional[str] = None) -> Dict[str, Any]:
    def use_link(self, link_id: str, password: Optional[str] = None) -> Dict[str, Any]:
    """
    """
    Use a sharing link to access a project.
    Use a sharing link to access a project.


    Args:
    Args:
    link_id: ID of the link
    link_id: ID of the link
    password: Optional password for protected links
    password: Optional password for protected links


    Returns:
    Returns:
    Project information
    Project information


    Raises:
    Raises:
    SharingError: If the link does not exist, is revoked, expired, or password is incorrect
    SharingError: If the link does not exist, is revoked, expired, or password is incorrect
    """
    """
    if link_id not in self.shared_links:
    if link_id not in self.shared_links:
    raise SharingError(f"Link {link_id} does not exist")
    raise SharingError(f"Link {link_id} does not exist")


    link_info = self.shared_links[link_id]
    link_info = self.shared_links[link_id]


    # Check if link is revoked
    # Check if link is revoked
    if link_info.get("revoked", False):
    if link_info.get("revoked", False):
    raise SharingError(f"Link {link_id} has been revoked")
    raise SharingError(f"Link {link_id} has been revoked")


    # Check if link is expired
    # Check if link is expired
    if link_info.get("expires_at"):
    if link_info.get("expires_at"):
    expires_at = datetime.fromisoformat(link_info["expires_at"])
    expires_at = datetime.fromisoformat(link_info["expires_at"])
    if datetime.now() > expires_at:
    if datetime.now() > expires_at:
    raise SharingError(f"Link {link_id} has expired")
    raise SharingError(f"Link {link_id} has expired")


    # Check if link has reached maximum uses
    # Check if link has reached maximum uses
    if (
    if (
    link_info.get("max_uses")
    link_info.get("max_uses")
    and link_info.get("uses", 0) >= link_info["max_uses"]
    and link_info.get("uses", 0) >= link_info["max_uses"]
    ):
    ):
    raise SharingError(f"Link {link_id} has reached maximum uses")
    raise SharingError(f"Link {link_id} has reached maximum uses")


    # Check password if required
    # Check password if required
    if link_info.get("password") and link_info["password"] != password:
    if link_info.get("password") and link_info["password"] != password:
    raise SharingError(f"Invalid password for link {link_id}")
    raise SharingError(f"Invalid password for link {link_id}")


    # Increment uses
    # Increment uses
    link_info["uses"] = link_info.get("uses", 0) + 1
    link_info["uses"] = link_info.get("uses", 0) + 1
    self._save_sharing_data()
    self._save_sharing_data()


    logger.info(f"Used link {link_id} to access project {link_info['project_id']}")
    logger.info(f"Used link {link_id} to access project {link_info['project_id']}")
    return {
    return {
    "project_id": link_info["project_id"],
    "project_id": link_info["project_id"],
    "workspace_id": link_info.get("workspace_id"),
    "workspace_id": link_info.get("workspace_id"),
    "permission": link_info["permission"],
    "permission": link_info["permission"],
    }
    }


    def get_user_shared_projects(self, user_id: str) -> List[Dict[str, Any]]:
    def get_user_shared_projects(self, user_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all projects shared with a user.
    Get all projects shared with a user.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    List of shared project information
    List of shared project information
    """
    """
    shared_projects = []
    shared_projects = []


    for share_info in self.shared_projects.values():
    for share_info in self.shared_projects.values():
    if share_info.get("shared_with_user") == user_id and not share_info.get(
    if share_info.get("shared_with_user") == user_id and not share_info.get(
    "revoked", False
    "revoked", False
    ):
    ):


    # Check if sharing has expired
    # Check if sharing has expired
    if share_info.get("expires_at"):
    if share_info.get("expires_at"):
    expires_at = datetime.fromisoformat(share_info["expires_at"])
    expires_at = datetime.fromisoformat(share_info["expires_at"])
    if datetime.now() > expires_at:
    if datetime.now() > expires_at:
    continue
    continue


    shared_projects.append(share_info)
    shared_projects.append(share_info)


    return shared_projects
    return shared_projects


    def get_workspace_shared_projects(self, workspace_id: str) -> List[Dict[str, Any]]:
    def get_workspace_shared_projects(self, workspace_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all projects shared with a workspace.
    Get all projects shared with a workspace.


    Args:
    Args:
    workspace_id: ID of the workspace
    workspace_id: ID of the workspace


    Returns:
    Returns:
    List of shared project information
    List of shared project information
    """
    """
    shared_projects = []
    shared_projects = []


    for share_info in self.shared_projects.values():
    for share_info in self.shared_projects.values():
    if share_info.get(
    if share_info.get(
    "shared_with_workspace"
    "shared_with_workspace"
    ) == workspace_id and not share_info.get("revoked", False):
    ) == workspace_id and not share_info.get("revoked", False):


    # Check if sharing has expired
    # Check if sharing has expired
    if share_info.get("expires_at"):
    if share_info.get("expires_at"):
    expires_at = datetime.fromisoformat(share_info["expires_at"])
    expires_at = datetime.fromisoformat(share_info["expires_at"])
    if datetime.now() > expires_at:
    if datetime.now() > expires_at:
    continue
    continue


    shared_projects.append(share_info)
    shared_projects.append(share_info)


    return shared_projects
    return shared_projects


    def get_project_sharing(self, project_id: str) -> List[Dict[str, Any]]:
    def get_project_sharing(self, project_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all sharing information for a project.
    Get all sharing information for a project.


    Args:
    Args:
    project_id: ID of the project
    project_id: ID of the project


    Returns:
    Returns:
    List of sharing information
    List of sharing information
    """
    """
    project_sharing = []
    project_sharing = []


    for share_info in self.shared_projects.values():
    for share_info in self.shared_projects.values():
    if share_info["project_id"] == project_id and not share_info.get(
    if share_info["project_id"] == project_id and not share_info.get(
    "revoked", False
    "revoked", False
    ):
    ):
    # Check if sharing has expired
    # Check if sharing has expired
    if share_info.get("expires_at"):
    if share_info.get("expires_at"):
    expires_at = datetime.fromisoformat(share_info["expires_at"])
    expires_at = datetime.fromisoformat(share_info["expires_at"])
    if datetime.now() > expires_at:
    if datetime.now() > expires_at:
    continue
    continue


    project_sharing.append(share_info)
    project_sharing.append(share_info)


    return project_sharing
    return project_sharing


    def get_project_links(self, project_id: str) -> List[Dict[str, Any]]:
    def get_project_links(self, project_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all sharing links for a project.
    Get all sharing links for a project.


    Args:
    Args:
    project_id: ID of the project
    project_id: ID of the project


    Returns:
    Returns:
    List of link information
    List of link information
    """
    """
    project_links = []
    project_links = []


    for link_info in self.shared_links.values():
    for link_info in self.shared_links.values():
    if link_info["project_id"] == project_id and not link_info.get(
    if link_info["project_id"] == project_id and not link_info.get(
    "revoked", False
    "revoked", False
    ):
    ):
    # Check if link has expired
    # Check if link has expired
    if link_info.get("expires_at"):
    if link_info.get("expires_at"):
    expires_at = datetime.fromisoformat(link_info["expires_at"])
    expires_at = datetime.fromisoformat(link_info["expires_at"])
    if datetime.now() > expires_at:
    if datetime.now() > expires_at:
    continue
    continue


    project_links.append(link_info)
    project_links.append(link_info)


    return project_links
    return project_links