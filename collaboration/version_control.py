"""
Version control functionality for the collaboration module.

This module provides classes for tracking versions of projects and resources,
allowing teams to manage changes, track history, and restore previous versions.
"""

import difflib
import json
import logging
import os
import shutil
import uuid
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)


class VersionInfo:
    """
    Information about a specific version of a project or resource.

    This class stores metadata about a version, such as who created it,
    when it was created, and a description of the changes.
    """

    def __init__(
        self,
        version_id: Optional[str] = None,
        project_id: Optional[str] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize version information.

        Args:
            version_id: Optional ID for the version (generated if not provided)
            project_id: ID of the project this version belongs to
            created_by: ID of the user who created this version
            description: Optional description of the changes in this version
        """
        self.version_id = version_id or str(uuid.uuid4())
        self.project_id = project_id
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()
        self.description = description or "Version created"
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def add_tag(self, tag: str):
        """
        Add a tag to the version.

        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the version.

        Args:
            tag: Tag to remove

        Returns:
            True if the tag was removed, False otherwise
        """
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to the version.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the version information to a dictionary.

        Returns:
            Dictionary representation of the version information
        """
        return {
            "version_id": self.version_id,
            "project_id": self.project_id,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionInfo":
        """
        Create version information from a dictionary.

        Args:
            data: Dictionary representation of version information

        Returns:
            VersionInfo object
        """
        version = cls(
            version_id=data["version_id"],
            project_id=data["project_id"],
            created_by=data["created_by"],
            description=data["description"],
        )

        version.created_at = data["created_at"]
        version.tags = data["tags"]
        version.metadata = data["metadata"]

        return version


class VersionControl:
    """
    Manages version control for projects and resources.

    This class provides functionality for creating, tracking, and restoring
    versions of projects and resources.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the version control system.

        Args:
            storage_path: Path where version data will be stored
        """
        self.storage_path = storage_path or "versions"
        os.makedirs(self.storage_path, exist_ok=True)

        self.versions: Dict[str, Dict[str, Any]] = {}
        self.project_versions: Dict[str, List[str]] = {}

        self._load_version_data()

    def _load_version_data(self):
        """Load version data from disk."""
        versions_file = os.path.join(self.storage_path, "versions.json")
        project_versions_file = os.path.join(self.storage_path, "project_versions.json")

        if os.path.exists(versions_file):
            try:
                with open(versions_file, "r") as f:
                    self.versions = json.load(f)
                logger.info(f"Loaded {len(self.versions)} versions")
            except Exception as e:
                logger.error(f"Failed to load versions: {e}")
                self.versions = {}

        if os.path.exists(project_versions_file):
            try:
                with open(project_versions_file, "r") as f:
                    self.project_versions = json.load(f)
                logger.info(
                    f"Loaded version history for {len(self.project_versions)} projects"
                )
            except Exception as e:
                logger.error(f"Failed to load project versions: {e}")
                self.project_versions = {}

    def _save_version_data(self):
        """Save version data to disk."""
        versions_file = os.path.join(self.storage_path, "versions.json")
        project_versions_file = os.path.join(self.storage_path, "project_versions.json")

        with open(versions_file, "w") as f:
            json.dump(self.versions, f, indent=2)

        with open(project_versions_file, "w") as f:
            json.dump(self.project_versions, f, indent=2)

    def create_version(
        self,
        project_id: str,
        project_path: str,
        created_by: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VersionInfo:
        """
        Create a new version of a project.

        Args:
            project_id: ID of the project
            project_path: Path to the project files
            created_by: ID of the user creating the version
            description: Optional description of the changes
            tags: Optional tags for the version
            metadata: Optional metadata for the version

        Returns:
            Version information
        """
        # Create version info
        version_info = VersionInfo(
            project_id=project_id, created_by=created_by, description=description
        )

        # Add tags if provided
        if tags:
            for tag in tags:
                version_info.add_tag(tag)

        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                version_info.add_metadata(key, value)

        # Create version directory
        version_dir = os.path.join(self.storage_path, "data", version_info.version_id)
        os.makedirs(version_dir, exist_ok=True)

        # Create a zip archive of the project
        zip_path = os.path.join(version_dir, "project.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)

        # Save version info
        self.versions[version_info.version_id] = version_info.to_dict()

        # Update project versions
        if project_id not in self.project_versions:
            self.project_versions[project_id] = []
        self.project_versions[project_id].append(version_info.version_id)

        self._save_version_data()

        logger.info(
            f"Created version {version_info.version_id} for project {project_id}"
        )
        return version_info

    def get_version(self, version_id: str) -> Optional[VersionInfo]:
        """
        Get version information.

        Args:
            version_id: ID of the version

        Returns:
            VersionInfo object or None if not found
        """
        if version_id not in self.versions:
            return None

        return VersionInfo.from_dict(self.versions[version_id])

    def get_project_versions(self, project_id: str) -> List[VersionInfo]:
        """
        Get all versions of a project.

        Args:
            project_id: ID of the project

        Returns:
            List of VersionInfo objects
        """
        if project_id not in self.project_versions:
            return []

        versions = []
        for version_id in self.project_versions[project_id]:
            version_info = self.get_version(version_id)
            if version_info:
                versions.append(version_info)

        # Sort by creation time (newest first)
        versions.sort(key=lambda v: v.created_at, reverse=True)

        return versions

    def restore_version(
        self, version_id: str, target_path: str, restore_by: str
    ) -> bool:
        """
        Restore a project to a specific version.

        Args:
            version_id: ID of the version to restore
            target_path: Path where the project will be restored
            restore_by: ID of the user restoring the version

        Returns:
            True if the version was restored, False otherwise
        """
        if version_id not in self.versions:
            logger.error(f"Version {version_id} not found")
            return False

        # Get version info
        version_info = self.get_version(version_id)
        if not version_info:
            logger.error(f"Failed to get version info for {version_id}")
            return False

        # Get version data
        version_dir = os.path.join(self.storage_path, "data", version_id)
        zip_path = os.path.join(version_dir, "project.zip")

        if not os.path.exists(zip_path):
            logger.error(f"Version data not found for {version_id}")
            return False

        # Clear target directory
        if os.path.exists(target_path):
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        else:
            os.makedirs(target_path, exist_ok=True)

        # Extract version data to target directory
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(target_path)

        logger.info(f"Restored version {version_id} to {target_path}")

        # Add metadata about restoration
        version_info.add_metadata("restored_by", restore_by)
        version_info.add_metadata("restored_at", datetime.now().isoformat())
        self.versions[version_id] = version_info.to_dict()
        self._save_version_data()

        return True

    def compare_versions(
        self, version_id1: str, version_id2: str, file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare two versions of a project.

        Args:
            version_id1: ID of the first version
            version_id2: ID of the second version
            file_path: Optional path to a specific file to compare

        Returns:
            Dictionary with comparison results

        Raises:
            ValueError: If either version is not found
        """
        if version_id1 not in self.versions:
            raise ValueError(f"Version {version_id1} not found")

        if version_id2 not in self.versions:
            raise ValueError(f"Version {version_id2} not found")

        # Get version info
        version1 = self.get_version(version_id1)
        version2 = self.get_version(version_id2)

        if not version1 or not version2:
            raise ValueError("Failed to get version information")

        # Create temporary directories for extraction
        temp_dir1 = os.path.join(self.storage_path, "temp", version_id1)
        temp_dir2 = os.path.join(self.storage_path, "temp", version_id2)

        os.makedirs(temp_dir1, exist_ok=True)
        os.makedirs(temp_dir2, exist_ok=True)

        # Extract version data
        zip_path1 = os.path.join(self.storage_path, "data", version_id1, "project.zip")
        zip_path2 = os.path.join(self.storage_path, "data", version_id2, "project.zip")

        with zipfile.ZipFile(zip_path1, "r") as zipf:
            zipf.extractall(temp_dir1)

        with zipfile.ZipFile(zip_path2, "r") as zipf:
            zipf.extractall(temp_dir2)

        # Compare files
        comparison_results = {
            "version1": version1.to_dict(),
            "version2": version2.to_dict(),
            "differences": [],
        }

        if file_path:
            # Compare specific file
            file_path1 = os.path.join(temp_dir1, file_path)
            file_path2 = os.path.join(temp_dir2, file_path)

            if os.path.exists(file_path1) and os.path.exists(file_path2):
                with open(file_path1, "r") as f1, open(file_path2, "r") as f2:
                    diff = list(
                        difflib.unified_diff(
                            f1.readlines(),
                            f2.readlines(),
                            fromfile=f"Version {version_id1}",
                            tofile=f"Version {version_id2}",
                        )
                    )

                comparison_results["differences"].append(
                    {"file": file_path, "diff": "".join(diff)}
                )
            elif os.path.exists(file_path1):
                comparison_results["differences"].append(
                    {"file": file_path, "status": "deleted"}
                )
            elif os.path.exists(file_path2):
                comparison_results["differences"].append(
                    {"file": file_path, "status": "added"}
                )
        else:
            # Compare all files
            files1 = set()
            files2 = set()

            for root, _, files in os.walk(temp_dir1):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir1)
                    files1.add(rel_path)

            for root, _, files in os.walk(temp_dir2):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir2)
                    files2.add(rel_path)

            # Files in both versions
            common_files = files1.intersection(files2)
            for file in common_files:
                file_path1 = os.path.join(temp_dir1, file)
                file_path2 = os.path.join(temp_dir2, file)

                with open(file_path1, "r") as f1, open(file_path2, "r") as f2:
                    content1 = f1.read()
                    content2 = f2.read()

                if content1 != content2:
                    comparison_results["differences"].append(
                        {"file": file, "status": "modified"}
                    )

            # Files only in version 1
            for file in files1 - files2:
                comparison_results["differences"].append(
                    {"file": file, "status": "deleted"}
                )

            # Files only in version 2
            for file in files2 - files1:
                comparison_results["differences"].append(
                    {"file": file, "status": "added"}
                )

        # Clean up temporary directories
        shutil.rmtree(temp_dir1)
        shutil.rmtree(temp_dir2)

        return comparison_results

    def delete_version(self, version_id: str) -> bool:
        """
        Delete a version.

        Args:
            version_id: ID of the version to delete

        Returns:
            True if the version was deleted, False otherwise
        """
        if version_id not in self.versions:
            logger.error(f"Version {version_id} not found")
            return False

        # Get project ID
        version_info = self.get_version(version_id)
        if not version_info:
            logger.error(f"Failed to get version info for {version_id}")
            return False

        project_id = version_info.project_id

        # Remove version from project versions
        if (
            project_id in self.project_versions
            and version_id in self.project_versions[project_id]
        ):
            self.project_versions[project_id].remove(version_id)

        # Remove version info
        del self.versions[version_id]

        # Remove version data
        version_dir = os.path.join(self.storage_path, "data", version_id)
        if os.path.exists(version_dir):
            shutil.rmtree(version_dir)

        self._save_version_data()

        logger.info(f"Deleted version {version_id}")
        return True

    def tag_version(self, version_id: str, tag: str) -> bool:
        """
        Add a tag to a version.

        Args:
            version_id: ID of the version
            tag: Tag to add

        Returns:
            True if the tag was added, False otherwise
        """
        if version_id not in self.versions:
            logger.error(f"Version {version_id} not found")
            return False

        version_info = self.get_version(version_id)
        if not version_info:
            logger.error(f"Failed to get version info for {version_id}")
            return False

        version_info.add_tag(tag)
        self.versions[version_id] = version_info.to_dict()
        self._save_version_data()

        logger.info(f"Added tag '{tag}' to version {version_id}")
        return True

    def get_tagged_versions(self, project_id: str, tag: str) -> List[VersionInfo]:
        """
        Get all versions of a project with a specific tag.

        Args:
            project_id: ID of the project
            tag: Tag to filter by

        Returns:
            List of VersionInfo objects
        """
        versions = self.get_project_versions(project_id)
        return [v for v in versions if tag in v.tags]
