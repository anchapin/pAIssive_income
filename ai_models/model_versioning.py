"""
Model versioning system for the AI Models module.

This module provides a comprehensive system for managing versioning of AI models,
including version tracking, compatibility checking, and version migration.
"""

import copy
import hashlib
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import semver

from errors import ConfigurationError

from .model_base_types import ModelInfo

# Set up logging with secure defaults
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelVersion:
    """
    Represents a version of an AI model.

    This class follows semantic versioning (major.minor.patch) with additional
    information specific to AI models.
    """

    def __init__(
        self,
        version: str,
        model_id: str,
        timestamp: str = "",
        hash_value: str = "",
        features: Optional[List[str]] = None,
        dependencies: Optional[Dict[str, str]] = None,
        is_compatible_with: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a model version.

        Args:
            version: Version string following semver format (e.g., "1.0.0")
            model_id: ID of the model this version belongs to
            timestamp: Optional timestamp of when this version was created
            hash_value: Optional hash of the model file for verification
            features: Optional list of features this version supports
            dependencies: Optional dependencies required by this version
            is_compatible_with: Optional list of other model versions this is compatible with
            metadata: Optional additional metadata for this version

        Raises:
            ValueError: If the version string is not in valid semver format
        """
        # Validate the version string
        try:
            semver.parse(version)
        except ValueError as e:
            raise ValueError(
                f"Invalid version string: {version}. Must follow semver format (e.g., 
                    '1.0.0')"
            ) from e

        self.version: str = version
        self.model_id: str = model_id
        self.timestamp: str = timestamp or datetime.now().isoformat()
        self.hash_value: str = hash_value
        self.features: List[str] = features or []
        self.dependencies: Dict[str, str] = dependencies or {}
        self.is_compatible_with: List[str] = is_compatible_with or []
        self.metadata: Dict[str, Any] = metadata or {}

    @property
    def major(self) -> int:
        """Get the major version number."""
        return semver.parse(self.version)["major"]

    @property
    def minor(self) -> int:
        """Get the minor version number."""
        return semver.parse(self.version)["minor"]

    @property
    def patch(self) -> int:
        """Get the patch version number."""
        return semver.parse(self.version)["patch"]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the version to a dictionary.

        Returns:
            Dictionary representation of the version
        """
        return {
            "version": self.version,
            "model_id": self.model_id,
            "timestamp": self.timestamp,
            "hash_value": self.hash_value,
            "features": self.features,
            "dependencies": self.dependencies,
            "is_compatible_with": self.is_compatible_with,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelVersion":
        """
        Create a ModelVersion instance from a dictionary.

        Args:
            data: Dictionary containing version information

        Returns:
            ModelVersion instance
        """
        try:
            return cls(
                version=data["version"],
                model_id=data["model_id"],
                timestamp=data.get("timestamp", ""),
                hash_value=data.get("hash_value", ""),
                features=data.get("features", []),
                dependencies=data.get("dependencies", {}),
                is_compatible_with=data.get("is_compatible_with", []),
                metadata=data.get("metadata", {}),
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in version data: {e}")

    def is_compatible_with_version(self, other_version: Union[str, 
        "ModelVersion"]) -> bool:
        """
        Check if this version is compatible with another version.

        By default, follows semantic versioning rules:
        - Major version changes indicate incompatible API changes
        - Minor and patch version changes should be backward compatible
        - Also checks explicit compatibility list

        Args:
            other_version: Another version to check compatibility with

        Returns:
            True if compatible, False otherwise
        """
        try:
            if isinstance(other_version, ModelVersion):
                other_ver_str = other_version.version
            else:
                other_ver_str = other_version

            # Check explicit compatibility list
            if other_ver_str in self.is_compatible_with:
                return True

            # Parse versions
            this_parsed = semver.parse(self.version)
            try:
                other_parsed = semver.parse(other_ver_str)
            except ValueError:
                return False

            # Major version must match for compatibility by default
            return this_parsed["major"] == other_parsed["major"]
        except Exception as e:
            logger.error(f"Error checking version compatibility: {e}")
            return False

    def __str__(self) -> str:
        """String representation of the version."""
        return f"v{self.version} ({self.timestamp})"

    def __eq__(self, other: object) -> bool:
        """Check if two versions are equal."""
        if not isinstance(other, ModelVersion):
            return False
        return self.version == other.version and self.model_id == other.model_id

    def __lt__(self, other: "ModelVersion") -> bool:
        """Compare versions based on semver."""
        return semver.compare(self.version, other.version) < 0

    def __gt__(self, other: "ModelVersion") -> bool:
        """Compare versions based on semver."""
        return semver.compare(self.version, other.version) > 0


class ModelVersionRegistry:
    """
    Registry for tracking versions of AI models.
    """

    def __init__(self, registry_path: str):
        """
        Initialize the model version registry.

        Args:
            registry_path: Path to the registry file
        """
        self.registry_path = registry_path
        self.versions: Dict[str, Dict[str, ModelVersion]] = (
            {}
        )  # model_id -> version_str -> ModelVersion

        # Create directory with secure permissions if it doesn't exist
        os.makedirs(os.path.dirname(self.registry_path), mode=0o750, exist_ok=True)

        # Load existing registry if available
        self._load_registry()

    def _load_registry(self) -> None:
        """Load the registry from disk."""
        if not os.path.exists(self.registry_path):
            logger.info(
                f"Model version registry not found at {self.registry_path}. Creating new registry."
            )
            return

        try:
            # Verify file permissions
            stat = os.stat(self.registry_path)
            if stat.st_mode & 0o777 != 0o640:
                logger.warning(
                    f"Insecure permissions on registry file {self.registry_path}")
                os.chmod(self.registry_path, 0o640)

            with open(self.registry_path, "r", encoding="utf - 8") as f:
                data = json.load(f)

            for model_id, versions_data in data.items():
                if model_id not in self.versions:
                    self.versions[model_id] = {}

                for version_str, version_data in versions_data.items():
                    self.versions[model_id][version_str] = \
                        ModelVersion.from_dict(version_data)

            logger.info(f"Loaded version registry with {len(self.versions)} models")

        except json.JSONDecodeError as e:
            error = ConfigurationError(
                message=f"Invalid JSON format in model version registry: {e}",
                config_key=self.registry_path,
                original_exception=e,
            )
            error.log()
            # Create a new registry
            self._save_registry()
        except Exception as e:
            logger.error(f"Error loading model version registry: {e}")
            # Create a new registry
            self._save_registry()

    def _save_registry(self) -> None:
        """Save the registry to disk securely."""
        try:
            # Convert to a serializable format
            registry_data: Dict[str, Dict[str, Any]] = {}

            for model_id, versions in self.versions.items():
                registry_data[model_id] = {}
                for version_str, version_obj in versions.items():
                    registry_data[model_id][version_str] = version_obj.to_dict()

            # Create parent directory with secure permissions if needed
            os.makedirs(os.path.dirname(self.registry_path), mode=0o750, exist_ok=True)

            # Write with secure permissions
            with open(self.registry_path, "w", encoding="utf - 8") as f:
                os.chmod(self.registry_path, 0o640)
                json.dump(registry_data, f, indent=2)

            logger.info(f"Saved version registry with {len(self.versions)} models")

        except Exception as e:
            logger.error(f"Error saving model version registry: {e}")

    # ... Rest of the ModelVersionRegistry class implementation ...
    # (Note: Previous methods remain unchanged - they operate on in - memory data
    # and don't need security enhancements)


class ModelMigrationTool:
    """
    Tool for migrating models between different versions.
    """

    def __init__(self, version_registry: ModelVersionRegistry):
        """
        Initialize the model migration tool.

        Args:
            version_registry: ModelVersionRegistry instance
        """
        self.version_registry: ModelVersionRegistry = version_registry
        self.migration_functions: Dict[str, Dict[Tuple[str, str], Callable[..., 
            ModelInfo]]] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)

    # ... Rest of the ModelMigrationTool class implementation ...
    # (Note: Previous methods remain unchanged as they don't involve file operations
    # or security - sensitive operations)


class VersionedModelManager:
    """
    Extension of ModelManager that adds versioning capabilities.
    """

    def __init__(self, model_manager: Any, models_dir: str):
        """
        Initialize the versioned model manager.

        Args:
            model_manager: ModelManager instance
            models_dir: Directory where models are stored
        """
        self.model_manager: Any = model_manager
        self.version_registry: ModelVersionRegistry = ModelVersionRegistry(
            os.path.join(models_dir, "version_registry.json")
        )
        self.migration_tool: ModelMigrationTool = \
            ModelMigrationTool(self.version_registry)
        self.logger: logging.Logger = logging.getLogger(__name__)

    # ... Rest of the VersionedModelManager class implementation ...
    # (Note: Previous methods remain unchanged as they depend on the security
    # improvements in ModelVersionRegistry)
