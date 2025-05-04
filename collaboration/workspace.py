"""
"""
Team workspace functionality for the collaboration module.
Team workspace functionality for the collaboration module.


This module provides classes for creating and managing team workspaces,
This module provides classes for creating and managing team workspaces,
which serve as shared environments for teams to collaborate on projects.
which serve as shared environments for teams to collaborate on projects.
"""
"""




import json
import json
import logging
import logging
import os
import os
import shutil
import shutil
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .access_control import Permission, Role, RoleManager
from .access_control import Permission, Role, RoleManager
from .errors import WorkspaceError
from .errors import WorkspaceError


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class TeamWorkspace:
    class TeamWorkspace:
    """
    """
    Represents a shared workspace for a team.
    Represents a shared workspace for a team.


    A workspace contains projects, resources, and settings that are shared
    A workspace contains projects, resources, and settings that are shared
    among team members with appropriate permissions.
    among team members with appropriate permissions.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str,
    name: str,
    workspace_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    description: Optional[str] = None,
    description: Optional[str] = None,
    owner_id: Optional[str] = None,
    owner_id: Optional[str] = None,
    storage_path: Optional[str] = None,
    storage_path: Optional[str] = None,
    ):
    ):
    """
    """
    Initialize a new team workspace.
    Initialize a new team workspace.


    Args:
    Args:
    name: Name of the workspace
    name: Name of the workspace
    workspace_id: Optional ID for the workspace (generated if not provided)
    workspace_id: Optional ID for the workspace (generated if not provided)
    description: Optional description of the workspace
    description: Optional description of the workspace
    owner_id: ID of the workspace owner
    owner_id: ID of the workspace owner
    storage_path: Path where workspace data will be stored
    storage_path: Path where workspace data will be stored
    """
    """
    self.name = name
    self.name = name
    self.workspace_id = workspace_id or str(uuid.uuid4())
    self.workspace_id = workspace_id or str(uuid.uuid4())
    self.description = description or f"Workspace for {name}"
    self.description = description or f"Workspace for {name}"
    self.owner_id = owner_id
    self.owner_id = owner_id
    self.created_at = datetime.now().isoformat()
    self.created_at = datetime.now().isoformat()
    self.updated_at = self.created_at
    self.updated_at = self.created_at
    self.members: Dict[str, Dict[str, Any]] = {}
    self.members: Dict[str, Dict[str, Any]] = {}
    self.projects: Dict[str, Dict[str, Any]] = {}
    self.projects: Dict[str, Dict[str, Any]] = {}
    self.settings: Dict[str, Any] = {
    self.settings: Dict[str, Any] = {
    "default_role": "viewer",
    "default_role": "viewer",
    "allow_public_sharing": False,
    "allow_public_sharing": False,
    "require_approval_for_new_members": True,
    "require_approval_for_new_members": True,
    "enable_activity_tracking": True,
    "enable_activity_tracking": True,
    "enable_notifications": True,
    "enable_notifications": True,
    }
    }


    # Set up storage
    # Set up storage
    self.storage_path = storage_path or os.path.join(
    self.storage_path = storage_path or os.path.join(
    "workspaces", self.workspace_id
    "workspaces", self.workspace_id
    )
    )
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    # Set up role manager
    # Set up role manager
    self.role_manager = RoleManager()
    self.role_manager = RoleManager()
    self._setup_default_roles()
    self._setup_default_roles()


    logger.info(f"Created workspace '{name}' with ID {self.workspace_id}")
    logger.info(f"Created workspace '{name}' with ID {self.workspace_id}")


    def _setup_default_roles(self):
    def _setup_default_roles(self):
    """Set up default roles for the workspace."""
    # Owner role - full access
    owner_role = Role("owner", "Workspace owner with full access")
    owner_role.add_permission(Permission.ALL)
    self.role_manager.add_role(owner_role)

    # Admin role - can manage workspace but can't delete it
    admin_role = Role("admin", "Workspace administrator")
    admin_permissions = [
    Permission.VIEW_WORKSPACE,
    Permission.EDIT_WORKSPACE,
    Permission.MANAGE_MEMBERS,
    Permission.CREATE_PROJECT,
    Permission.VIEW_ALL_PROJECTS,
    Permission.EDIT_ALL_PROJECTS,
    Permission.DELETE_PROJECT,
    Permission.MANAGE_ROLES,
    ]
    for perm in admin_permissions:
    admin_role.add_permission(perm)
    self.role_manager.add_role(admin_role)

    # Editor role - can edit projects but not manage workspace
    editor_role = Role("editor", "Can edit projects")
    editor_permissions = [
    Permission.VIEW_WORKSPACE,
    Permission.CREATE_PROJECT,
    Permission.VIEW_ALL_PROJECTS,
    Permission.EDIT_ALL_PROJECTS,
    ]
    for perm in editor_permissions:
    editor_role.add_permission(perm)
    self.role_manager.add_role(editor_role)

    # Contributor role - can edit assigned projects
    contributor_role = Role("contributor", "Can edit assigned projects")
    contributor_permissions = [
    Permission.VIEW_WORKSPACE,
    Permission.CREATE_PROJECT,
    Permission.VIEW_ASSIGNED_PROJECTS,
    Permission.EDIT_ASSIGNED_PROJECTS,
    ]
    for perm in contributor_permissions:
    contributor_role.add_permission(perm)
    self.role_manager.add_role(contributor_role)

    # Viewer role - can only view
    viewer_role = Role("viewer", "Can only view projects")
    viewer_permissions = [
    Permission.VIEW_WORKSPACE,
    Permission.VIEW_ASSIGNED_PROJECTS,
    ]
    for perm in viewer_permissions:
    viewer_role.add_permission(perm)
    self.role_manager.add_role(viewer_role)

    def add_member(
    self, user_id: str, role: str = "viewer", added_by: Optional[str] = None
    ) -> Dict[str, Any]:
    """
    """
    Add a member to the workspace.
    Add a member to the workspace.


    Args:
    Args:
    user_id: ID of the user to add
    user_id: ID of the user to add
    role: Role to assign to the user
    role: Role to assign to the user
    added_by: ID of the user who added this member
    added_by: ID of the user who added this member


    Returns:
    Returns:
    Member information
    Member information


    Raises:
    Raises:
    WorkspaceError: If the user is already a member or the role is invalid
    WorkspaceError: If the user is already a member or the role is invalid
    """
    """
    if user_id in self.members:
    if user_id in self.members:
    raise WorkspaceError(
    raise WorkspaceError(
    f"User {user_id} is already a member of this workspace"
    f"User {user_id} is already a member of this workspace"
    )
    )


    if not self.role_manager.role_exists(role):
    if not self.role_manager.role_exists(role):
    raise WorkspaceError(f"Invalid role: {role}")
    raise WorkspaceError(f"Invalid role: {role}")


    member_info = {
    member_info = {
    "user_id": user_id,
    "user_id": user_id,
    "role": role,
    "role": role,
    "added_at": datetime.now().isoformat(),
    "added_at": datetime.now().isoformat(),
    "added_by": added_by,
    "added_by": added_by,
    "status": "active",
    "status": "active",
    "projects": [],
    "projects": [],
    }
    }


    self.members[user_id] = member_info
    self.members[user_id] = member_info
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self._save_workspace_data()
    self._save_workspace_data()


    logger.info(
    logger.info(
    f"Added user {user_id} to workspace {self.workspace_id} with role {role}"
    f"Added user {user_id} to workspace {self.workspace_id} with role {role}"
    )
    )
    return member_info
    return member_info


    def remove_member(self, user_id: str, removed_by: Optional[str] = None) -> bool:
    def remove_member(self, user_id: str, removed_by: Optional[str] = None) -> bool:
    """
    """
    Remove a member from the workspace.
    Remove a member from the workspace.


    Args:
    Args:
    user_id: ID of the user to remove
    user_id: ID of the user to remove
    removed_by: ID of the user who removed this member
    removed_by: ID of the user who removed this member


    Returns:
    Returns:
    True if the member was removed, False otherwise
    True if the member was removed, False otherwise


    Raises:
    Raises:
    WorkspaceError: If the user is not a member or is the owner
    WorkspaceError: If the user is not a member or is the owner
    """
    """
    if user_id not in self.members:
    if user_id not in self.members:
    raise WorkspaceError(f"User {user_id} is not a member of this workspace")
    raise WorkspaceError(f"User {user_id} is not a member of this workspace")


    if user_id == self.owner_id:
    if user_id == self.owner_id:
    raise WorkspaceError("Cannot remove the workspace owner")
    raise WorkspaceError("Cannot remove the workspace owner")


    del self.members[user_id]
    del self.members[user_id]
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self._save_workspace_data()
    self._save_workspace_data()


    logger.info(f"Removed user {user_id} from workspace {self.workspace_id}")
    logger.info(f"Removed user {user_id} from workspace {self.workspace_id}")
    return True
    return True


    def update_member_role(
    def update_member_role(
    self, user_id: str, new_role: str, updated_by: Optional[str] = None
    self, user_id: str, new_role: str, updated_by: Optional[str] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a member's role.
    Update a member's role.


    Args:
    Args:
    user_id: ID of the user to update
    user_id: ID of the user to update
    new_role: New role to assign
    new_role: New role to assign
    updated_by: ID of the user who updated this role
    updated_by: ID of the user who updated this role


    Returns:
    Returns:
    Updated member information
    Updated member information


    Raises:
    Raises:
    WorkspaceError: If the user is not a member or the role is invalid
    WorkspaceError: If the user is not a member or the role is invalid
    """
    """
    if user_id not in self.members:
    if user_id not in self.members:
    raise WorkspaceError(f"User {user_id} is not a member of this workspace")
    raise WorkspaceError(f"User {user_id} is not a member of this workspace")


    if not self.role_manager.role_exists(new_role):
    if not self.role_manager.role_exists(new_role):
    raise WorkspaceError(f"Invalid role: {new_role}")
    raise WorkspaceError(f"Invalid role: {new_role}")


    # Cannot change owner's role
    # Cannot change owner's role
    if user_id == self.owner_id and new_role != "owner":
    if user_id == self.owner_id and new_role != "owner":
    raise WorkspaceError("Cannot change the workspace owner's role")
    raise WorkspaceError("Cannot change the workspace owner's role")


    self.members[user_id]["role"] = new_role
    self.members[user_id]["role"] = new_role
    self.members[user_id]["updated_at"] = datetime.now().isoformat()
    self.members[user_id]["updated_at"] = datetime.now().isoformat()
    self.members[user_id]["updated_by"] = updated_by
    self.members[user_id]["updated_by"] = updated_by


    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self._save_workspace_data()
    self._save_workspace_data()


    logger.info(
    logger.info(
    f"Updated role for user {user_id} to {new_role} in workspace {self.workspace_id}"
    f"Updated role for user {user_id} to {new_role} in workspace {self.workspace_id}"
    )
    )
    return self.members[user_id]
    return self.members[user_id]


    def add_project(
    def add_project(
    self,
    self,
    project_id: str,
    project_id: str,
    project_name: str,
    project_name: str,
    description: Optional[str] = None,
    description: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Add a project to the workspace.
    Add a project to the workspace.


    Args:
    Args:
    project_id: ID of the project
    project_id: ID of the project
    project_name: Name of the project
    project_name: Name of the project
    description: Optional description of the project
    description: Optional description of the project
    created_by: ID of the user who created the project
    created_by: ID of the user who created the project


    Returns:
    Returns:
    Project information
    Project information


    Raises:
    Raises:
    WorkspaceError: If the project already exists
    WorkspaceError: If the project already exists
    """
    """
    if project_id in self.projects:
    if project_id in self.projects:
    raise WorkspaceError(
    raise WorkspaceError(
    f"Project {project_id} already exists in this workspace"
    f"Project {project_id} already exists in this workspace"
    )
    )


    project_info = {
    project_info = {
    "project_id": project_id,
    "project_id": project_id,
    "name": project_name,
    "name": project_name,
    "description": description or f"Project {project_name}",
    "description": description or f"Project {project_name}",
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "created_by": created_by,
    "created_by": created_by,
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "status": "active",
    "status": "active",
    "members": {},
    "members": {},
    }
    }


    # Add creator as a member with editor role
    # Add creator as a member with editor role
    if created_by and created_by in self.members:
    if created_by and created_by in self.members:
    project_info["members"][created_by] = {
    project_info["members"][created_by] = {
    "role": "editor",
    "role": "editor",
    "added_at": datetime.now().isoformat(),
    "added_at": datetime.now().isoformat(),
    }
    }


    self.projects[project_id] = project_info
    self.projects[project_id] = project_info
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self._save_workspace_data()
    self._save_workspace_data()


    # Create project directory
    # Create project directory
    project_dir = os.path.join(self.storage_path, "projects", project_id)
    project_dir = os.path.join(self.storage_path, "projects", project_id)
    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(project_dir, exist_ok=True)


    logger.info(
    logger.info(
    f"Added project {project_name} ({project_id}) to workspace {self.workspace_id}"
    f"Added project {project_name} ({project_id}) to workspace {self.workspace_id}"
    )
    )
    return project_info
    return project_info


    def remove_project(self, project_id: str, removed_by: Optional[str] = None) -> bool:
    def remove_project(self, project_id: str, removed_by: Optional[str] = None) -> bool:
    """
    """
    Remove a project from the workspace.
    Remove a project from the workspace.


    Args:
    Args:
    project_id: ID of the project to remove
    project_id: ID of the project to remove
    removed_by: ID of the user who removed the project
    removed_by: ID of the user who removed the project


    Returns:
    Returns:
    True if the project was removed, False otherwise
    True if the project was removed, False otherwise


    Raises:
    Raises:
    WorkspaceError: If the project does not exist
    WorkspaceError: If the project does not exist
    """
    """
    if project_id not in self.projects:
    if project_id not in self.projects:
    raise WorkspaceError(
    raise WorkspaceError(
    f"Project {project_id} does not exist in this workspace"
    f"Project {project_id} does not exist in this workspace"
    )
    )


    del self.projects[project_id]
    del self.projects[project_id]
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self._save_workspace_data()
    self._save_workspace_data()


    # Remove project directory
    # Remove project directory
    project_dir = os.path.join(self.storage_path, "projects", project_id)
    project_dir = os.path.join(self.storage_path, "projects", project_id)
    if os.path.exists(project_dir):
    if os.path.exists(project_dir):
    shutil.rmtree(project_dir)
    shutil.rmtree(project_dir)


    logger.info(f"Removed project {project_id} from workspace {self.workspace_id}")
    logger.info(f"Removed project {project_id} from workspace {self.workspace_id}")
    return True
    return True


    def get_member_projects(self, user_id: str) -> List[Dict[str, Any]]:
    def get_member_projects(self, user_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all projects that a member has access to.
    Get all projects that a member has access to.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    List of project information
    List of project information


    Raises:
    Raises:
    WorkspaceError: If the user is not a member
    WorkspaceError: If the user is not a member
    """
    """
    if user_id not in self.members:
    if user_id not in self.members:
    raise WorkspaceError(f"User {user_id} is not a member of this workspace")
    raise WorkspaceError(f"User {user_id} is not a member of this workspace")


    # Get user's role
    # Get user's role
    role_name = self.members[user_id]["role"]
    role_name = self.members[user_id]["role"]
    role = self.role_manager.get_role(role_name)
    role = self.role_manager.get_role(role_name)


    # If user has permission to view all projects, return all
    # If user has permission to view all projects, return all
    if role.has_permission(Permission.VIEW_ALL_PROJECTS):
    if role.has_permission(Permission.VIEW_ALL_PROJECTS):
    return list(self.projects.values())
    return list(self.projects.values())


    # Otherwise, return only projects the user is a member of
    # Otherwise, return only projects the user is a member of
    user_projects = []
    user_projects = []
    for project_id, project_info in self.projects.items():
    for project_id, project_info in self.projects.items():
    if user_id in project_info["members"]:
    if user_id in project_info["members"]:
    user_projects.append(project_info)
    user_projects.append(project_info)


    return user_projects
    return user_projects


    def update_settings(
    def update_settings(
    self, new_settings: Dict[str, Any], updated_by: Optional[str] = None
    self, new_settings: Dict[str, Any], updated_by: Optional[str] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update workspace settings.
    Update workspace settings.


    Args:
    Args:
    new_settings: New settings to apply
    new_settings: New settings to apply
    updated_by: ID of the user who updated the settings
    updated_by: ID of the user who updated the settings


    Returns:
    Returns:
    Updated settings
    Updated settings
    """
    """
    self.settings.update(new_settings)
    self.settings.update(new_settings)
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self._save_workspace_data()
    self._save_workspace_data()


    logger.info(f"Updated settings for workspace {self.workspace_id}")
    logger.info(f"Updated settings for workspace {self.workspace_id}")
    return self.settings
    return self.settings


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the workspace to a dictionary.
    Convert the workspace to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the workspace
    Dictionary representation of the workspace
    """
    """
    return {
    return {
    "workspace_id": self.workspace_id,
    "workspace_id": self.workspace_id,
    "name": self.name,
    "name": self.name,
    "description": self.description,
    "description": self.description,
    "owner_id": self.owner_id,
    "owner_id": self.owner_id,
    "created_at": self.created_at,
    "created_at": self.created_at,
    "updated_at": self.updated_at,
    "updated_at": self.updated_at,
    "members": self.members,
    "members": self.members,
    "projects": self.projects,
    "projects": self.projects,
    "settings": self.settings,
    "settings": self.settings,
    }
    }


    def _save_workspace_data(self):
    def _save_workspace_data(self):
    """Save workspace data to disk."""
    data_file = os.path.join(self.storage_path, "workspace.json")
    with open(data_file, "w") as f:
    json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(
    cls, workspace_id: str, storage_path: Optional[str] = None
    ) -> "TeamWorkspace":
    """
    """
    Load a workspace from disk.
    Load a workspace from disk.


    Args:
    Args:
    workspace_id: ID of the workspace to load
    workspace_id: ID of the workspace to load
    storage_path: Optional custom storage path
    storage_path: Optional custom storage path


    Returns:
    Returns:
    Loaded workspace
    Loaded workspace


    Raises:
    Raises:
    WorkspaceError: If the workspace does not exist
    WorkspaceError: If the workspace does not exist
    """
    """
    storage_path = storage_path or os.path.join("workspaces", workspace_id)
    storage_path = storage_path or os.path.join("workspaces", workspace_id)
    data_file = os.path.join(storage_path, "workspace.json")
    data_file = os.path.join(storage_path, "workspace.json")


    if not os.path.exists(data_file):
    if not os.path.exists(data_file):
    raise WorkspaceError(f"Workspace {workspace_id} does not exist")
    raise WorkspaceError(f"Workspace {workspace_id} does not exist")


    with open(data_file, "r") as f:
    with open(data_file, "r") as f:
    data = json.load(f)
    data = json.load(f)


    workspace = cls(
    workspace = cls(
    name=data["name"],
    name=data["name"],
    workspace_id=data["workspace_id"],
    workspace_id=data["workspace_id"],
    description=data["description"],
    description=data["description"],
    owner_id=data["owner_id"],
    owner_id=data["owner_id"],
    storage_path=storage_path,
    storage_path=storage_path,
    )
    )


    workspace.created_at = data["created_at"]
    workspace.created_at = data["created_at"]
    workspace.updated_at = data["updated_at"]
    workspace.updated_at = data["updated_at"]
    workspace.members = data["members"]
    workspace.members = data["members"]
    workspace.projects = data["projects"]
    workspace.projects = data["projects"]
    workspace.settings = data["settings"]
    workspace.settings = data["settings"]


    return workspace
    return workspace




    class WorkspaceManager:
    class WorkspaceManager:
    """
    """
    Manages multiple team workspaces.
    Manages multiple team workspaces.


    This class provides functionality for creating, loading, and managing
    This class provides functionality for creating, loading, and managing
    multiple team workspaces.
    multiple team workspaces.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the workspace manager.
    Initialize the workspace manager.


    Args:
    Args:
    storage_path: Path where workspace data will be stored
    storage_path: Path where workspace data will be stored
    """
    """
    self.storage_path = storage_path or "workspaces"
    self.storage_path = storage_path or "workspaces"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    self.workspaces: Dict[str, TeamWorkspace] = {}
    self.workspaces: Dict[str, TeamWorkspace] = {}
    self._load_workspaces()
    self._load_workspaces()


    def _load_workspaces(self):
    def _load_workspaces(self):
    """Load all workspaces from disk."""
    # Get all subdirectories in the storage path
    for item in os.listdir(self.storage_path):
    workspace_path = os.path.join(self.storage_path, item)
    if os.path.isdir(workspace_path):
    workspace_id = item
    try:
    workspace = TeamWorkspace.load(workspace_id, workspace_path)
    self.workspaces[workspace_id] = workspace
    logger.info(f"Loaded workspace {workspace.name} ({workspace_id})")
except Exception as e:
    logger.error(f"Failed to load workspace {workspace_id}: {e}")

    def create_workspace(
    self,
    name: str,
    description: Optional[str] = None,
    owner_id: Optional[str] = None,
    ) -> TeamWorkspace:
    """
    """
    Create a new workspace.
    Create a new workspace.


    Args:
    Args:
    name: Name of the workspace
    name: Name of the workspace
    description: Optional description of the workspace
    description: Optional description of the workspace
    owner_id: ID of the workspace owner
    owner_id: ID of the workspace owner


    Returns:
    Returns:
    New workspace
    New workspace
    """
    """
    workspace_id = str(uuid.uuid4())
    workspace_id = str(uuid.uuid4())
    workspace_path = os.path.join(self.storage_path, workspace_id)
    workspace_path = os.path.join(self.storage_path, workspace_id)


    workspace = TeamWorkspace(
    workspace = TeamWorkspace(
    name=name,
    name=name,
    workspace_id=workspace_id,
    workspace_id=workspace_id,
    description=description,
    description=description,
    owner_id=owner_id,
    owner_id=owner_id,
    storage_path=workspace_path,
    storage_path=workspace_path,
    )
    )


    self.workspaces[workspace_id] = workspace
    self.workspaces[workspace_id] = workspace
    workspace._save_workspace_data()
    workspace._save_workspace_data()


    logger.info(f"Created new workspace {name} ({workspace_id})")
    logger.info(f"Created new workspace {name} ({workspace_id})")
    return workspace
    return workspace


    def get_workspace(self, workspace_id: str) -> TeamWorkspace:
    def get_workspace(self, workspace_id: str) -> TeamWorkspace:
    """
    """
    Get a workspace by ID.
    Get a workspace by ID.


    Args:
    Args:
    workspace_id: ID of the workspace
    workspace_id: ID of the workspace


    Returns:
    Returns:
    Workspace
    Workspace


    Raises:
    Raises:
    WorkspaceError: If the workspace does not exist
    WorkspaceError: If the workspace does not exist
    """
    """
    if workspace_id not in self.workspaces:
    if workspace_id not in self.workspaces:
    raise WorkspaceError(f"Workspace {workspace_id} does not exist")
    raise WorkspaceError(f"Workspace {workspace_id} does not exist")


    return self.workspaces[workspace_id]
    return self.workspaces[workspace_id]


    def delete_workspace(self, workspace_id: str) -> bool:
    def delete_workspace(self, workspace_id: str) -> bool:
    """
    """
    Delete a workspace.
    Delete a workspace.


    Args:
    Args:
    workspace_id: ID of the workspace to delete
    workspace_id: ID of the workspace to delete


    Returns:
    Returns:
    True if the workspace was deleted, False otherwise
    True if the workspace was deleted, False otherwise


    Raises:
    Raises:
    WorkspaceError: If the workspace does not exist
    WorkspaceError: If the workspace does not exist
    """
    """
    if workspace_id not in self.workspaces:
    if workspace_id not in self.workspaces:
    raise WorkspaceError(f"Workspace {workspace_id} does not exist")
    raise WorkspaceError(f"Workspace {workspace_id} does not exist")


    # Remove workspace from memory
    # Remove workspace from memory
    del self.workspaces[workspace_id]
    del self.workspaces[workspace_id]


    # Remove workspace directory
    # Remove workspace directory
    workspace_path = os.path.join(self.storage_path, workspace_id)
    workspace_path = os.path.join(self.storage_path, workspace_id)
    if os.path.exists(workspace_path):
    if os.path.exists(workspace_path):
    shutil.rmtree(workspace_path)
    shutil.rmtree(workspace_path)


    logger.info(f"Deleted workspace {workspace_id}")
    logger.info(f"Deleted workspace {workspace_id}")
    return True
    return True


    def get_user_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
    def get_user_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all workspaces that a user is a member of.
    Get all workspaces that a user is a member of.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    List of workspace information
    List of workspace information
    """
    """
    user_workspaces = []
    user_workspaces = []


    for workspace in self.workspaces.values():
    for workspace in self.workspaces.values():
    if user_id in workspace.members or user_id == workspace.owner_id:
    if user_id in workspace.members or user_id == workspace.owner_id:
    user_workspaces.append(workspace.to_dict())
    user_workspaces.append(workspace.to_dict())


    return user_workspaces
    return user_workspaces


    def list_workspaces(self) -> List[Dict[str, Any]]:
    def list_workspaces(self) -> List[Dict[str, Any]]:
    """
    """
    List all workspaces.
    List all workspaces.


    Returns:
    Returns:
    List of workspace information
    List of workspace information
    """
    """
    return [workspace.to_dict() for workspace in self.workspaces.values()]
    return [workspace.to_dict() for workspace in self.workspaces.values()]