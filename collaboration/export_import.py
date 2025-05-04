"""
"""
Export and import functionality for the collaboration module.
Export and import functionality for the collaboration module.


This module provides classes for exporting and importing projects and workspaces,
This module provides classes for exporting and importing projects and workspaces,
enabling sharing between different instances of the application.
enabling sharing between different instances of the application.
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
import time
import time
import uuid
import uuid
import zipfile
import zipfile
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class ExportImport:
    class ExportImport:
    """
    """
    Manages export and import of projects and workspaces.
    Manages export and import of projects and workspaces.


    This class provides functionality for exporting projects and workspaces to
    This class provides functionality for exporting projects and workspaces to
    portable formats, and importing them into other instances of the application.
    portable formats, and importing them into other instances of the application.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the export/import manager.
    Initialize the export/import manager.


    Args:
    Args:
    storage_path: Path where export/import data will be stored
    storage_path: Path where export/import data will be stored
    """
    """
    self.storage_path = storage_path or "exports"
    self.storage_path = storage_path or "exports"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    def export_project(
    def export_project(
    self,
    self,
    project_id: str,
    project_id: str,
    project_path: str,
    project_path: str,
    project_data: Dict[str, Any],
    project_data: Dict[str, Any],
    include_history: bool = True,
    include_history: bool = True,
    include_comments: bool = True,
    include_comments: bool = True,
    ) -> str:
    ) -> str:
    """
    """
    Export a project to a portable format.
    Export a project to a portable format.


    Args:
    Args:
    project_id: ID of the project
    project_id: ID of the project
    project_path: Path to the project files
    project_path: Path to the project files
    project_data: Project metadata
    project_data: Project metadata
    include_history: Whether to include version history
    include_history: Whether to include version history
    include_comments: Whether to include comments
    include_comments: Whether to include comments


    Returns:
    Returns:
    Path to the exported file
    Path to the exported file


    Raises:
    Raises:
    ValueError: If the project path does not exist
    ValueError: If the project path does not exist
    """
    """
    if not os.path.exists(project_path):
    if not os.path.exists(project_path):
    raise ValueError(f"Project path does not exist: {project_path}")
    raise ValueError(f"Project path does not exist: {project_path}")


    # Create export directory
    # Create export directory
    export_id = str(uuid.uuid4())
    export_id = str(uuid.uuid4())
    export_dir = os.path.join(self.storage_path, export_id)
    export_dir = os.path.join(self.storage_path, export_id)
    os.makedirs(export_dir, exist_ok=True)
    os.makedirs(export_dir, exist_ok=True)


    # Create export metadata
    # Create export metadata
    export_metadata = {
    export_metadata = {
    "export_id": export_id,
    "export_id": export_id,
    "project_id": project_id,
    "project_id": project_id,
    "exported_at": datetime.now().isoformat(),
    "exported_at": datetime.now().isoformat(),
    "include_history": include_history,
    "include_history": include_history,
    "include_comments": include_comments,
    "include_comments": include_comments,
    "project_data": project_data,
    "project_data": project_data,
    }
    }


    # Save export metadata
    # Save export metadata
    metadata_file = os.path.join(export_dir, "metadata.json")
    metadata_file = os.path.join(export_dir, "metadata.json")
    with open(metadata_file, "w") as f:
    with open(metadata_file, "w") as f:
    json.dump(export_metadata, f, indent=2)
    json.dump(export_metadata, f, indent=2)


    # Create a zip archive of the project files
    # Create a zip archive of the project files
    files_zip = os.path.join(export_dir, "files.zip")
    files_zip = os.path.join(export_dir, "files.zip")
    with zipfile.ZipFile(files_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    with zipfile.ZipFile(files_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(project_path):
    for root, _, files in os.walk(project_path):
    for file in files:
    for file in files:
    file_path = os.path.join(root, file)
    file_path = os.path.join(root, file)
    arcname = os.path.relpath(file_path, project_path)
    arcname = os.path.relpath(file_path, project_path)
    zipf.write(file_path, arcname)
    zipf.write(file_path, arcname)


    # Create the final export file
    # Create the final export file
    export_file = os.path.join(self.storage_path, f"{export_id}.zip")
    export_file = os.path.join(self.storage_path, f"{export_id}.zip")
    with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(metadata_file, "metadata.json")
    zipf.write(metadata_file, "metadata.json")
    zipf.write(files_zip, "files.zip")
    zipf.write(files_zip, "files.zip")


    # Include additional data if requested
    # Include additional data if requested
    if include_history:
    if include_history:
    # Placeholder for version history
    # Placeholder for version history
    history_data = {"versions": []}
    history_data = {"versions": []}
    history_file = os.path.join(export_dir, "history.json")
    history_file = os.path.join(export_dir, "history.json")
    with open(history_file, "w") as f:
    with open(history_file, "w") as f:
    json.dump(history_data, f, indent=2)
    json.dump(history_data, f, indent=2)
    zipf.write(history_file, "history.json")
    zipf.write(history_file, "history.json")


    if include_comments:
    if include_comments:
    # Placeholder for comments
    # Placeholder for comments
    comments_data = {"comments": []}
    comments_data = {"comments": []}
    comments_file = os.path.join(export_dir, "comments.json")
    comments_file = os.path.join(export_dir, "comments.json")
    with open(comments_file, "w") as f:
    with open(comments_file, "w") as f:
    json.dump(comments_data, f, indent=2)
    json.dump(comments_data, f, indent=2)
    zipf.write(comments_file, "comments.json")
    zipf.write(comments_file, "comments.json")


    # Clean up temporary directory
    # Clean up temporary directory
    shutil.rmtree(export_dir)
    shutil.rmtree(export_dir)


    logger.info(f"Exported project {project_id} to {export_file}")
    logger.info(f"Exported project {project_id} to {export_file}")
    return export_file
    return export_file


    def import_project(
    def import_project(
    self, import_file: str, target_path: str, new_project_id: Optional[str] = None
    self, import_file: str, target_path: str, new_project_id: Optional[str] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Import a project from an export file.
    Import a project from an export file.


    Args:
    Args:
    import_file: Path to the export file
    import_file: Path to the export file
    target_path: Path where the project will be imported
    target_path: Path where the project will be imported
    new_project_id: Optional new ID for the imported project
    new_project_id: Optional new ID for the imported project


    Returns:
    Returns:
    Imported project information
    Imported project information


    Raises:
    Raises:
    ValueError: If the import file does not exist or is invalid
    ValueError: If the import file does not exist or is invalid
    """
    """
    if not os.path.exists(import_file):
    if not os.path.exists(import_file):
    raise ValueError(f"Import file does not exist: {import_file}")
    raise ValueError(f"Import file does not exist: {import_file}")


    # Create temporary directory for extraction
    # Create temporary directory for extraction
    import_id = str(uuid.uuid4())
    import_id = str(uuid.uuid4())
    import_dir = os.path.join(self.storage_path, f"import_{import_id}")
    import_dir = os.path.join(self.storage_path, f"import_{import_id}")
    os.makedirs(import_dir, exist_ok=True)
    os.makedirs(import_dir, exist_ok=True)


    try:
    try:
    # Extract the import file
    # Extract the import file
    with zipfile.ZipFile(import_file, "r") as zipf:
    with zipfile.ZipFile(import_file, "r") as zipf:
    zipf.extractall(import_dir)
    zipf.extractall(import_dir)


    # Read metadata
    # Read metadata
    metadata_file = os.path.join(import_dir, "metadata.json")
    metadata_file = os.path.join(import_dir, "metadata.json")
    if not os.path.exists(metadata_file):
    if not os.path.exists(metadata_file):
    raise ValueError("Invalid import file: metadata.json not found")
    raise ValueError("Invalid import file: metadata.json not found")


    with open(metadata_file, "r") as f:
    with open(metadata_file, "r") as f:
    metadata = json.load(f)
    metadata = json.load(f)


    # Extract project files
    # Extract project files
    files_zip = os.path.join(import_dir, "files.zip")
    files_zip = os.path.join(import_dir, "files.zip")
    if not os.path.exists(files_zip):
    if not os.path.exists(files_zip):
    raise ValueError("Invalid import file: files.zip not found")
    raise ValueError("Invalid import file: files.zip not found")


    # Create target directory
    # Create target directory
    os.makedirs(target_path, exist_ok=True)
    os.makedirs(target_path, exist_ok=True)


    # Extract files to target directory
    # Extract files to target directory
    with zipfile.ZipFile(files_zip, "r") as zipf:
    with zipfile.ZipFile(files_zip, "r") as zipf:
    zipf.extractall(target_path)
    zipf.extractall(target_path)


    # Process additional data
    # Process additional data
    history_data = None
    history_data = None
    comments_data = None
    comments_data = None


    history_file = os.path.join(import_dir, "history.json")
    history_file = os.path.join(import_dir, "history.json")
    if os.path.exists(history_file):
    if os.path.exists(history_file):
    with open(history_file, "r") as f:
    with open(history_file, "r") as f:
    history_data = json.load(f)
    history_data = json.load(f)


    comments_file = os.path.join(import_dir, "comments.json")
    comments_file = os.path.join(import_dir, "comments.json")
    if os.path.exists(comments_file):
    if os.path.exists(comments_file):
    with open(comments_file, "r") as f:
    with open(comments_file, "r") as f:
    comments_data = json.load(f)
    comments_data = json.load(f)


    # Create import result
    # Create import result
    project_data = metadata["project_data"]
    project_data = metadata["project_data"]


    # Update project ID if requested
    # Update project ID if requested
    if new_project_id:
    if new_project_id:
    project_data["project_id"] = new_project_id
    project_data["project_id"] = new_project_id


    import_result = {
    import_result = {
    "import_id": import_id,
    "import_id": import_id,
    "imported_at": datetime.now().isoformat(),
    "imported_at": datetime.now().isoformat(),
    "original_project_id": metadata["project_id"],
    "original_project_id": metadata["project_id"],
    "new_project_id": project_data["project_id"],
    "new_project_id": project_data["project_id"],
    "project_data": project_data,
    "project_data": project_data,
    "history_data": history_data,
    "history_data": history_data,
    "comments_data": comments_data,
    "comments_data": comments_data,
    }
    }


    logger.info(f"Imported project to {target_path}")
    logger.info(f"Imported project to {target_path}")
    return import_result
    return import_result


finally:
finally:
    # Clean up temporary directory
    # Clean up temporary directory
    shutil.rmtree(import_dir)
    shutil.rmtree(import_dir)


    def export_workspace(
    def export_workspace(
    self,
    self,
    workspace_id: str,
    workspace_id: str,
    workspace_path: str,
    workspace_path: str,
    workspace_data: Dict[str, Any],
    workspace_data: Dict[str, Any],
    include_projects: bool = True,
    include_projects: bool = True,
    ) -> str:
    ) -> str:
    """
    """
    Export a workspace to a portable format.
    Export a workspace to a portable format.


    Args:
    Args:
    workspace_id: ID of the workspace
    workspace_id: ID of the workspace
    workspace_path: Path to the workspace files
    workspace_path: Path to the workspace files
    workspace_data: Workspace metadata
    workspace_data: Workspace metadata
    include_projects: Whether to include projects
    include_projects: Whether to include projects


    Returns:
    Returns:
    Path to the exported file
    Path to the exported file


    Raises:
    Raises:
    ValueError: If the workspace path does not exist
    ValueError: If the workspace path does not exist
    """
    """
    if not os.path.exists(workspace_path):
    if not os.path.exists(workspace_path):
    raise ValueError(f"Workspace path does not exist: {workspace_path}")
    raise ValueError(f"Workspace path does not exist: {workspace_path}")


    # Create export directory
    # Create export directory
    export_id = str(uuid.uuid4())
    export_id = str(uuid.uuid4())
    export_dir = os.path.join(self.storage_path, export_id)
    export_dir = os.path.join(self.storage_path, export_id)
    os.makedirs(export_dir, exist_ok=True)
    os.makedirs(export_dir, exist_ok=True)


    # Create export metadata
    # Create export metadata
    export_metadata = {
    export_metadata = {
    "export_id": export_id,
    "export_id": export_id,
    "workspace_id": workspace_id,
    "workspace_id": workspace_id,
    "exported_at": datetime.now().isoformat(),
    "exported_at": datetime.now().isoformat(),
    "include_projects": include_projects,
    "include_projects": include_projects,
    "workspace_data": workspace_data,
    "workspace_data": workspace_data,
    }
    }


    # Save export metadata
    # Save export metadata
    metadata_file = os.path.join(export_dir, "metadata.json")
    metadata_file = os.path.join(export_dir, "metadata.json")
    with open(metadata_file, "w") as f:
    with open(metadata_file, "w") as f:
    json.dump(export_metadata, f, indent=2)
    json.dump(export_metadata, f, indent=2)


    # Create the final export file
    # Create the final export file
    export_file = os.path.join(self.storage_path, f"{export_id}_workspace.zip")
    export_file = os.path.join(self.storage_path, f"{export_id}_workspace.zip")
    with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(metadata_file, "metadata.json")
    zipf.write(metadata_file, "metadata.json")


    # Include projects if requested
    # Include projects if requested
    if include_projects and "projects" in workspace_data:
    if include_projects and "projects" in workspace_data:
    projects_dir = os.path.join(workspace_path, "projects")
    projects_dir = os.path.join(workspace_path, "projects")
    if os.path.exists(projects_dir):
    if os.path.exists(projects_dir):
    # Create a zip archive of each project
    # Create a zip archive of each project
    for project_id in workspace_data["projects"]:
    for project_id in workspace_data["projects"]:
    project_path = os.path.join(projects_dir, project_id)
    project_path = os.path.join(projects_dir, project_id)
    if os.path.exists(project_path):
    if os.path.exists(project_path):
    project_zip = os.path.join(export_dir, f"{project_id}.zip")
    project_zip = os.path.join(export_dir, f"{project_id}.zip")
    with zipfile.ZipFile(
    with zipfile.ZipFile(
    project_zip, "w", zipfile.ZIP_DEFLATED
    project_zip, "w", zipfile.ZIP_DEFLATED
    ) as project_zipf:
    ) as project_zipf:
    for root, _, files in os.walk(project_path):
    for root, _, files in os.walk(project_path):
    for file in files:
    for file in files:
    file_path = os.path.join(root, file)
    file_path = os.path.join(root, file)
    arcname = os.path.relpath(
    arcname = os.path.relpath(
    file_path, project_path
    file_path, project_path
    )
    )
    project_zipf.write(file_path, arcname)
    project_zipf.write(file_path, arcname)


    zipf.write(project_zip, f"projects/{project_id}.zip")
    zipf.write(project_zip, f"projects/{project_id}.zip")


    # Clean up temporary directory
    # Clean up temporary directory
    shutil.rmtree(export_dir)
    shutil.rmtree(export_dir)


    logger.info(f"Exported workspace {workspace_id} to {export_file}")
    logger.info(f"Exported workspace {workspace_id} to {export_file}")
    return export_file
    return export_file


    def import_workspace(
    def import_workspace(
    self, import_file: str, target_path: str, new_workspace_id: Optional[str] = None
    self, import_file: str, target_path: str, new_workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Import a workspace from an export file.
    Import a workspace from an export file.


    Args:
    Args:
    import_file: Path to the export file
    import_file: Path to the export file
    target_path: Path where the workspace will be imported
    target_path: Path where the workspace will be imported
    new_workspace_id: Optional new ID for the imported workspace
    new_workspace_id: Optional new ID for the imported workspace


    Returns:
    Returns:
    Imported workspace information
    Imported workspace information


    Raises:
    Raises:
    ValueError: If the import file does not exist or is invalid
    ValueError: If the import file does not exist or is invalid
    """
    """
    if not os.path.exists(import_file):
    if not os.path.exists(import_file):
    raise ValueError(f"Import file does not exist: {import_file}")
    raise ValueError(f"Import file does not exist: {import_file}")


    # Create temporary directory for extraction
    # Create temporary directory for extraction
    import_id = str(uuid.uuid4())
    import_id = str(uuid.uuid4())
    import_dir = os.path.join(self.storage_path, f"import_{import_id}")
    import_dir = os.path.join(self.storage_path, f"import_{import_id}")
    os.makedirs(import_dir, exist_ok=True)
    os.makedirs(import_dir, exist_ok=True)


    try:
    try:
    # Extract the import file
    # Extract the import file
    with zipfile.ZipFile(import_file, "r") as zipf:
    with zipfile.ZipFile(import_file, "r") as zipf:
    zipf.extractall(import_dir)
    zipf.extractall(import_dir)


    # Read metadata
    # Read metadata
    metadata_file = os.path.join(import_dir, "metadata.json")
    metadata_file = os.path.join(import_dir, "metadata.json")
    if not os.path.exists(metadata_file):
    if not os.path.exists(metadata_file):
    raise ValueError("Invalid import file: metadata.json not found")
    raise ValueError("Invalid import file: metadata.json not found")


    with open(metadata_file, "r") as f:
    with open(metadata_file, "r") as f:
    metadata = json.load(f)
    metadata = json.load(f)


    # Create target directory
    # Create target directory
    os.makedirs(target_path, exist_ok=True)
    os.makedirs(target_path, exist_ok=True)


    # Process workspace data
    # Process workspace data
    workspace_data = metadata["workspace_data"]
    workspace_data = metadata["workspace_data"]


    # Update workspace ID if requested
    # Update workspace ID if requested
    if new_workspace_id:
    if new_workspace_id:
    workspace_data["workspace_id"] = new_workspace_id
    workspace_data["workspace_id"] = new_workspace_id


    # Save workspace data
    # Save workspace data
    workspace_file = os.path.join(target_path, "workspace.json")
    workspace_file = os.path.join(target_path, "workspace.json")
    with open(workspace_file, "w") as f:
    with open(workspace_file, "w") as f:
    json.dump(workspace_data, f, indent=2)
    json.dump(workspace_data, f, indent=2)


    # Process projects if included
    # Process projects if included
    imported_projects = []
    imported_projects = []
    projects_dir = os.path.join(import_dir, "projects")
    projects_dir = os.path.join(import_dir, "projects")
    if os.path.exists(projects_dir):
    if os.path.exists(projects_dir):
    target_projects_dir = os.path.join(target_path, "projects")
    target_projects_dir = os.path.join(target_path, "projects")
    os.makedirs(target_projects_dir, exist_ok=True)
    os.makedirs(target_projects_dir, exist_ok=True)


    for item in os.listdir(projects_dir):
    for item in os.listdir(projects_dir):
    if item.endswith(".zip"):
    if item.endswith(".zip"):
    project_id = item[:-4]  # Remove .zip extension
    project_id = item[:-4]  # Remove .zip extension
    project_zip = os.path.join(projects_dir, item)
    project_zip = os.path.join(projects_dir, item)
    project_dir = os.path.join(target_projects_dir, project_id)
    project_dir = os.path.join(target_projects_dir, project_id)
    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(project_dir, exist_ok=True)


    # Extract project files
    # Extract project files
    with zipfile.ZipFile(project_zip, "r") as zipf:
    with zipfile.ZipFile(project_zip, "r") as zipf:
    zipf.extractall(project_dir)
    zipf.extractall(project_dir)


    imported_projects.append(project_id)
    imported_projects.append(project_id)


    # Create import result
    # Create import result
    import_result = {
    import_result = {
    "import_id": import_id,
    "import_id": import_id,
    "imported_at": datetime.now().isoformat(),
    "imported_at": datetime.now().isoformat(),
    "original_workspace_id": metadata["workspace_id"],
    "original_workspace_id": metadata["workspace_id"],
    "new_workspace_id": workspace_data["workspace_id"],
    "new_workspace_id": workspace_data["workspace_id"],
    "workspace_data": workspace_data,
    "workspace_data": workspace_data,
    "imported_projects": imported_projects,
    "imported_projects": imported_projects,
    }
    }


    logger.info(f"Imported workspace to {target_path}")
    logger.info(f"Imported workspace to {target_path}")
    return import_result
    return import_result


finally:
finally:
    # Clean up temporary directory
    # Clean up temporary directory
    shutil.rmtree(import_dir)
    shutil.rmtree(import_dir)


    def list_exports(self) -> List[Dict[str, Any]]:
    def list_exports(self) -> List[Dict[str, Any]]:
    """
    """
    List all available exports.
    List all available exports.


    Returns:
    Returns:
    List of export information
    List of export information
    """
    """
    exports = []
    exports = []


    for item in os.listdir(self.storage_path):
    for item in os.listdir(self.storage_path):
    if item.endswith(".zip"):
    if item.endswith(".zip"):
    export_path = os.path.join(self.storage_path, item)
    export_path = os.path.join(self.storage_path, item)


    try:
    try:
    # Extract metadata
    # Extract metadata
    with zipfile.ZipFile(export_path, "r") as zipf:
    with zipfile.ZipFile(export_path, "r") as zipf:
    if "metadata.json" in zipf.namelist():
    if "metadata.json" in zipf.namelist():
    with zipf.open("metadata.json") as f:
    with zipf.open("metadata.json") as f:
    metadata = json.load(f)
    metadata = json.load(f)


    export_info = {
    export_info = {
    "filename": item,
    "filename": item,
    "path": export_path,
    "path": export_path,
    "size": os.path.getsize(export_path),
    "size": os.path.getsize(export_path),
    "created_at": datetime.fromtimestamp(
    "created_at": datetime.fromtimestamp(
    os.path.getctime(export_path)
    os.path.getctime(export_path)
    ).isoformat(),
    ).isoformat(),
    "metadata": metadata,
    "metadata": metadata,
    }
    }


    exports.append(export_info)
    exports.append(export_info)
except Exception as e:
except Exception as e:
    logger.error(f"Failed to process export file {item}: {e}")
    logger.error(f"Failed to process export file {item}: {e}")


    # Sort by creation time (newest first)
    # Sort by creation time (newest first)
    exports.sort(key=lambda e: e["created_at"], reverse=True)
    exports.sort(key=lambda e: e["created_at"], reverse=True)


    return exports
    return exports


    def delete_export(self, export_id: str) -> bool:
    def delete_export(self, export_id: str) -> bool:
    """
    """
    Delete an export file.
    Delete an export file.


    Args:
    Args:
    export_id: ID of the export to delete
    export_id: ID of the export to delete


    Returns:
    Returns:
    True if the export was deleted, False otherwise
    True if the export was deleted, False otherwise
    """
    """
    for item in os.listdir(self.storage_path):
    for item in os.listdir(self.storage_path):
    if item.startswith(export_id) and item.endswith(".zip"):
    if item.startswith(export_id) and item.endswith(".zip"):
    export_path = os.path.join(self.storage_path, item)
    export_path = os.path.join(self.storage_path, item)
    os.remove(export_path)
    os.remove(export_path)
    logger.info(f"Deleted export file {export_path}")
    logger.info(f"Deleted export file {export_path}")
    return True
    return True


    logger.warning(f"Export file with ID {export_id} not found")
    logger.warning(f"Export file with ID {export_id} not found")
    return False
    return False