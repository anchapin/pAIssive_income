"""
Export and import functionality for the collaboration module.

This module provides classes for exporting and importing projects and workspaces,
enabling sharing between different instances of the application.
"""

import os
import json
import zipfile
import logging
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import shutil

# Set up logging
logger = logging.getLogger(__name__)

class ExportImport:
    """
    Manages export and import of projects and workspaces.
    
    This class provides functionality for exporting projects and workspaces to
    portable formats, and importing them into other instances of the application.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the export/import manager.
        
        Args:
            storage_path: Path where export/import data will be stored
        """
        self.storage_path = storage_path or "exports"
        os.makedirs(self.storage_path, exist_ok=True)
    
    def export_project(self, 
                      project_id: str,
                      project_path: str,
                      project_data: Dict[str, Any],
                      include_history: bool = True,
                      include_comments: bool = True) -> str:
        """
        Export a project to a portable format.
        
        Args:
            project_id: ID of the project
            project_path: Path to the project files
            project_data: Project metadata
            include_history: Whether to include version history
            include_comments: Whether to include comments
            
        Returns:
            Path to the exported file
            
        Raises:
            ValueError: If the project path does not exist
        """
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")
        
        # Create export directory
        export_id = str(uuid.uuid4())
        export_dir = os.path.join(self.storage_path, export_id)
        os.makedirs(export_dir, exist_ok=True)
        
        # Create export metadata
        export_metadata = {
            "export_id": export_id,
            "project_id": project_id,
            "exported_at": datetime.now().isoformat(),
            "include_history": include_history,
            "include_comments": include_comments,
            "project_data": project_data
        }
        
        # Save export metadata
        metadata_file = os.path.join(export_dir, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(export_metadata, f, indent=2)
        
        # Create a zip archive of the project files
        files_zip = os.path.join(export_dir, "files.zip")
        with zipfile.ZipFile(files_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
        
        # Create the final export file
        export_file = os.path.join(self.storage_path, f"{export_id}.zip")
        with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(metadata_file, "metadata.json")
            zipf.write(files_zip, "files.zip")
            
            # Include additional data if requested
            if include_history:
                # Placeholder for version history
                history_data = {"versions": []}
                history_file = os.path.join(export_dir, "history.json")
                with open(history_file, "w") as f:
                    json.dump(history_data, f, indent=2)
                zipf.write(history_file, "history.json")
            
            if include_comments:
                # Placeholder for comments
                comments_data = {"comments": []}
                comments_file = os.path.join(export_dir, "comments.json")
                with open(comments_file, "w") as f:
                    json.dump(comments_data, f, indent=2)
                zipf.write(comments_file, "comments.json")
        
        # Clean up temporary directory
        shutil.rmtree(export_dir)
        
        logger.info(f"Exported project {project_id} to {export_file}")
        return export_file
    
    def import_project(self, 
                      import_file: str,
                      target_path: str,
                      new_project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Import a project from an export file.
        
        Args:
            import_file: Path to the export file
            target_path: Path where the project will be imported
            new_project_id: Optional new ID for the imported project
            
        Returns:
            Imported project information
            
        Raises:
            ValueError: If the import file does not exist or is invalid
        """
        if not os.path.exists(import_file):
            raise ValueError(f"Import file does not exist: {import_file}")
        
        # Create temporary directory for extraction
        import_id = str(uuid.uuid4())
        import_dir = os.path.join(self.storage_path, f"import_{import_id}")
        os.makedirs(import_dir, exist_ok=True)
        
        try:
            # Extract the import file
            with zipfile.ZipFile(import_file, "r") as zipf:
                zipf.extractall(import_dir)
            
            # Read metadata
            metadata_file = os.path.join(import_dir, "metadata.json")
            if not os.path.exists(metadata_file):
                raise ValueError(f"Invalid import file: metadata.json not found")
            
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            
            # Extract project files
            files_zip = os.path.join(import_dir, "files.zip")
            if not os.path.exists(files_zip):
                raise ValueError(f"Invalid import file: files.zip not found")
            
            # Create target directory
            os.makedirs(target_path, exist_ok=True)
            
            # Extract files to target directory
            with zipfile.ZipFile(files_zip, "r") as zipf:
                zipf.extractall(target_path)
            
            # Process additional data
            history_data = None
            comments_data = None
            
            history_file = os.path.join(import_dir, "history.json")
            if os.path.exists(history_file):
                with open(history_file, "r") as f:
                    history_data = json.load(f)
            
            comments_file = os.path.join(import_dir, "comments.json")
            if os.path.exists(comments_file):
                with open(comments_file, "r") as f:
                    comments_data = json.load(f)
            
            # Create import result
            project_data = metadata["project_data"]
            
            # Update project ID if requested
            if new_project_id:
                project_data["project_id"] = new_project_id
            
            import_result = {
                "import_id": import_id,
                "imported_at": datetime.now().isoformat(),
                "original_project_id": metadata["project_id"],
                "new_project_id": project_data["project_id"],
                "project_data": project_data,
                "history_data": history_data,
                "comments_data": comments_data
            }
            
            logger.info(f"Imported project to {target_path}")
            return import_result
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(import_dir)
    
    def export_workspace(self, 
                        workspace_id: str,
                        workspace_path: str,
                        workspace_data: Dict[str, Any],
                        include_projects: bool = True) -> str:
        """
        Export a workspace to a portable format.
        
        Args:
            workspace_id: ID of the workspace
            workspace_path: Path to the workspace files
            workspace_data: Workspace metadata
            include_projects: Whether to include projects
            
        Returns:
            Path to the exported file
            
        Raises:
            ValueError: If the workspace path does not exist
        """
        if not os.path.exists(workspace_path):
            raise ValueError(f"Workspace path does not exist: {workspace_path}")
        
        # Create export directory
        export_id = str(uuid.uuid4())
        export_dir = os.path.join(self.storage_path, export_id)
        os.makedirs(export_dir, exist_ok=True)
        
        # Create export metadata
        export_metadata = {
            "export_id": export_id,
            "workspace_id": workspace_id,
            "exported_at": datetime.now().isoformat(),
            "include_projects": include_projects,
            "workspace_data": workspace_data
        }
        
        # Save export metadata
        metadata_file = os.path.join(export_dir, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(export_metadata, f, indent=2)
        
        # Create the final export file
        export_file = os.path.join(self.storage_path, f"{export_id}_workspace.zip")
        with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(metadata_file, "metadata.json")
            
            # Include projects if requested
            if include_projects and "projects" in workspace_data:
                projects_dir = os.path.join(workspace_path, "projects")
                if os.path.exists(projects_dir):
                    # Create a zip archive of each project
                    for project_id in workspace_data["projects"]:
                        project_path = os.path.join(projects_dir, project_id)
                        if os.path.exists(project_path):
                            project_zip = os.path.join(export_dir, f"{project_id}.zip")
                            with zipfile.ZipFile(project_zip, "w", zipfile.ZIP_DEFLATED) as project_zipf:
                                for root, _, files in os.walk(project_path):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, project_path)
                                        project_zipf.write(file_path, arcname)
                            
                            zipf.write(project_zip, f"projects/{project_id}.zip")
        
        # Clean up temporary directory
        shutil.rmtree(export_dir)
        
        logger.info(f"Exported workspace {workspace_id} to {export_file}")
        return export_file
    
    def import_workspace(self, 
                        import_file: str,
                        target_path: str,
                        new_workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Import a workspace from an export file.
        
        Args:
            import_file: Path to the export file
            target_path: Path where the workspace will be imported
            new_workspace_id: Optional new ID for the imported workspace
            
        Returns:
            Imported workspace information
            
        Raises:
            ValueError: If the import file does not exist or is invalid
        """
        if not os.path.exists(import_file):
            raise ValueError(f"Import file does not exist: {import_file}")
        
        # Create temporary directory for extraction
        import_id = str(uuid.uuid4())
        import_dir = os.path.join(self.storage_path, f"import_{import_id}")
        os.makedirs(import_dir, exist_ok=True)
        
        try:
            # Extract the import file
            with zipfile.ZipFile(import_file, "r") as zipf:
                zipf.extractall(import_dir)
            
            # Read metadata
            metadata_file = os.path.join(import_dir, "metadata.json")
            if not os.path.exists(metadata_file):
                raise ValueError(f"Invalid import file: metadata.json not found")
            
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            
            # Create target directory
            os.makedirs(target_path, exist_ok=True)
            
            # Process workspace data
            workspace_data = metadata["workspace_data"]
            
            # Update workspace ID if requested
            if new_workspace_id:
                workspace_data["workspace_id"] = new_workspace_id
            
            # Save workspace data
            workspace_file = os.path.join(target_path, "workspace.json")
            with open(workspace_file, "w") as f:
                json.dump(workspace_data, f, indent=2)
            
            # Process projects if included
            imported_projects = []
            projects_dir = os.path.join(import_dir, "projects")
            if os.path.exists(projects_dir):
                target_projects_dir = os.path.join(target_path, "projects")
                os.makedirs(target_projects_dir, exist_ok=True)
                
                for item in os.listdir(projects_dir):
                    if item.endswith(".zip"):
                        project_id = item[:-4]  # Remove .zip extension
                        project_zip = os.path.join(projects_dir, item)
                        project_dir = os.path.join(target_projects_dir, project_id)
                        os.makedirs(project_dir, exist_ok=True)
                        
                        # Extract project files
                        with zipfile.ZipFile(project_zip, "r") as zipf:
                            zipf.extractall(project_dir)
                        
                        imported_projects.append(project_id)
            
            # Create import result
            import_result = {
                "import_id": import_id,
                "imported_at": datetime.now().isoformat(),
                "original_workspace_id": metadata["workspace_id"],
                "new_workspace_id": workspace_data["workspace_id"],
                "workspace_data": workspace_data,
                "imported_projects": imported_projects
            }
            
            logger.info(f"Imported workspace to {target_path}")
            return import_result
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(import_dir)
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """
        List all available exports.
        
        Returns:
            List of export information
        """
        exports = []
        
        for item in os.listdir(self.storage_path):
            if item.endswith(".zip"):
                export_path = os.path.join(self.storage_path, item)
                
                try:
                    # Extract metadata
                    with zipfile.ZipFile(export_path, "r") as zipf:
                        if "metadata.json" in zipf.namelist():
                            with zipf.open("metadata.json") as f:
                                metadata = json.load(f)
                            
                            export_info = {
                                "filename": item,
                                "path": export_path,
                                "size": os.path.getsize(export_path),
                                "created_at": datetime.fromtimestamp(os.path.getctime(export_path)).isoformat(),
                                "metadata": metadata
                            }
                            
                            exports.append(export_info)
                except Exception as e:
                    logger.error(f"Failed to process export file {item}: {e}")
        
        # Sort by creation time (newest first)
        exports.sort(key=lambda e: e["created_at"], reverse=True)
        
        return exports
    
    def delete_export(self, export_id: str) -> bool:
        """
        Delete an export file.
        
        Args:
            export_id: ID of the export to delete
            
        Returns:
            True if the export was deleted, False otherwise
        """
        for item in os.listdir(self.storage_path):
            if item.startswith(export_id) and item.endswith(".zip"):
                export_path = os.path.join(self.storage_path, item)
                os.remove(export_path)
                logger.info(f"Deleted export file {export_path}")
                return True
        
        logger.warning(f"Export file with ID {export_id} not found")
        return False
