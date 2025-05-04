"""
"""
Model versioning system for the AI Models module.
Model versioning system for the AI Models module.


This module provides a comprehensive system for managing versioning of AI models,
This module provides a comprehensive system for managing versioning of AI models,
including version tracking, compatibility checking, and version migration.
including version tracking, compatibility checking, and version migration.
"""
"""




import copy
import copy
import hashlib
import hashlib
import json
import json
import logging
import logging
import os
import os
import sys
import sys
from datetime import datetime
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


import semver
import semver


sys.path.insert
sys.path.insert
from errors import ConfigurationError
from errors import ConfigurationError


from .model_base_types import ModelInfo
from .model_base_types import ModelInfo


(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class ModelVersion:
    class ModelVersion:
    """
    """
    Represents a version of an AI model.
    Represents a version of an AI model.


    This class follows semantic versioning (major.minor.patch) with additional
    This class follows semantic versioning (major.minor.patch) with additional
    information specific to AI models.
    information specific to AI models.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    version: str,
    version: str,
    model_id: str,
    model_id: str,
    timestamp: str = "",
    timestamp: str = "",
    hash_value: str = "",
    hash_value: str = "",
    features: List[str] = None,
    features: List[str] = None,
    dependencies: Dict[str, str] = None,
    dependencies: Dict[str, str] = None,
    is_compatible_with: List[str] = None,
    is_compatible_with: List[str] = None,
    metadata: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    ):
    ):
    """
    """
    Initialize a model version.
    Initialize a model version.


    Args:
    Args:
    version: Version string following semver format (e.g., "1.0.0")
    version: Version string following semver format (e.g., "1.0.0")
    model_id: ID of the model this version belongs to
    model_id: ID of the model this version belongs to
    timestamp: Optional timestamp of when this version was created
    timestamp: Optional timestamp of when this version was created
    hash_value: Optional hash of the model file for verification
    hash_value: Optional hash of the model file for verification
    features: Optional list of features this version supports
    features: Optional list of features this version supports
    dependencies: Optional dependencies required by this version
    dependencies: Optional dependencies required by this version
    is_compatible_with: Optional list of other model versions this is compatible with
    is_compatible_with: Optional list of other model versions this is compatible with
    metadata: Optional additional metadata for this version
    metadata: Optional additional metadata for this version


    Raises:
    Raises:
    ValueError: If the version string is not in valid semver format
    ValueError: If the version string is not in valid semver format
    """
    """
    # Validate the version string
    # Validate the version string
    try:
    try:
    semver.Version.parse(version)
    semver.Version.parse(version)
except ValueError as e:
except ValueError as e:
    raise ValueError(
    raise ValueError(
    f"Invalid version string: {version}. Must follow semver format (e.g., '1.0.0')"
    f"Invalid version string: {version}. Must follow semver format (e.g., '1.0.0')"
    ) from e
    ) from e


    self.version = version
    self.version = version
    self.model_id = model_id
    self.model_id = model_id
    self.timestamp = timestamp or datetime.now().isoformat()
    self.timestamp = timestamp or datetime.now().isoformat()
    self.hash_value = hash_value
    self.hash_value = hash_value
    self.features = features or []
    self.features = features or []
    self.dependencies = dependencies or {}
    self.dependencies = dependencies or {}
    self.is_compatible_with = is_compatible_with or []
    self.is_compatible_with = is_compatible_with or []
    self.metadata = metadata or {}
    self.metadata = metadata or {}


    @property
    @property
    def major(self) -> int:
    def major(self) -> int:
    """Get the major version number."""
    return semver.Version.parse(self.version).major

    @property
    def minor(self) -> int:
    """Get the minor version number."""
    return semver.Version.parse(self.version).minor

    @property
    def patch(self) -> int:
    """Get the patch version number."""
    return semver.Version.parse(self.version).patch

    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the version to a dictionary.
    Convert the version to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the version
    Dictionary representation of the version
    """
    """
    return {
    return {
    "version": self.version,
    "version": self.version,
    "model_id": self.model_id,
    "model_id": self.model_id,
    "timestamp": self.timestamp,
    "timestamp": self.timestamp,
    "hash_value": self.hash_value,
    "hash_value": self.hash_value,
    "features": self.features,
    "features": self.features,
    "dependencies": self.dependencies,
    "dependencies": self.dependencies,
    "is_compatible_with": self.is_compatible_with,
    "is_compatible_with": self.is_compatible_with,
    "metadata": self.metadata,
    "metadata": self.metadata,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelVersion":
    def from_dict(cls, data: Dict[str, Any]) -> "ModelVersion":
    """
    """
    Create a ModelVersion instance from a dictionary.
    Create a ModelVersion instance from a dictionary.


    Args:
    Args:
    data: Dictionary containing version information
    data: Dictionary containing version information


    Returns:
    Returns:
    ModelVersion instance
    ModelVersion instance
    """
    """
    return cls(
    return cls(
    version=data["version"],
    version=data["version"],
    model_id=data["model_id"],
    model_id=data["model_id"],
    timestamp=data.get("timestamp", ""),
    timestamp=data.get("timestamp", ""),
    hash_value=data.get("hash_value", ""),
    hash_value=data.get("hash_value", ""),
    features=data.get("features", []),
    features=data.get("features", []),
    dependencies=data.get("dependencies", {}),
    dependencies=data.get("dependencies", {}),
    is_compatible_with=data.get("is_compatible_with", []),
    is_compatible_with=data.get("is_compatible_with", []),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    def is_compatible_with_version(
    def is_compatible_with_version(
    self, other_version: Union[str, "ModelVersion"]
    self, other_version: Union[str, "ModelVersion"]
    ) -> bool:
    ) -> bool:
    """
    """
    Check if this version is compatible with another version.
    Check if this version is compatible with another version.


    By default, follows semantic versioning rules:
    By default, follows semantic versioning rules:
    - Major version changes indicate incompatible API changes
    - Major version changes indicate incompatible API changes
    - Minor and patch version changes should be backward compatible
    - Minor and patch version changes should be backward compatible
    - Also checks explicit compatibility list
    - Also checks explicit compatibility list


    Args:
    Args:
    other_version: Another version to check compatibility with
    other_version: Another version to check compatibility with


    Returns:
    Returns:
    True if compatible, False otherwise
    True if compatible, False otherwise
    """
    """
    if isinstance(other_version, ModelVersion):
    if isinstance(other_version, ModelVersion):
    other_ver_str = other_version.version
    other_ver_str = other_version.version
    else:
    else:
    other_ver_str = other_version
    other_ver_str = other_version


    # Check explicit compatibility list
    # Check explicit compatibility list
    if other_ver_str in self.is_compatible_with:
    if other_ver_str in self.is_compatible_with:
    return True
    return True


    # Parse versions
    # Parse versions
    this_parsed = semver.Version.parse(self.version)
    this_parsed = semver.Version.parse(self.version)
    try:
    try:
    other_parsed = semver.Version.parse(other_ver_str)
    other_parsed = semver.Version.parse(other_ver_str)
except ValueError:
except ValueError:
    return False
    return False


    # Major version must match for compatibility by default
    # Major version must match for compatibility by default
    return this_parsed.major == other_parsed.major
    return this_parsed.major == other_parsed.major


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the version."""
    return f"v{self.version} ({self.timestamp})"

    def __eq__(self, other: object) -> bool:
    """
    """
    Check if two versions are equal.
    Check if two versions are equal.


    Args:
    Args:
    other: Another version to compare with
    other: Another version to compare with


    Returns:
    Returns:
    True if the versions are equal, False otherwise
    True if the versions are equal, False otherwise
    """
    """
    if not isinstance(other, ModelVersion):
    if not isinstance(other, ModelVersion):
    return False
    return False
    return self.version == other.version and self.model_id == other.model_id
    return self.version == other.version and self.model_id == other.model_id


    def __lt__(self, other: "ModelVersion") -> bool:
    def __lt__(self, other: "ModelVersion") -> bool:
    """
    """
    Compare versions based on semver.
    Compare versions based on semver.


    Args:
    Args:
    other: Another version to compare with
    other: Another version to compare with


    Returns:
    Returns:
    True if this version is less than the other version, False otherwise
    True if this version is less than the other version, False otherwise
    """
    """
    return semver.compare(self.version, other.version) < 0
    return semver.compare(self.version, other.version) < 0


    def __gt__(self, other: "ModelVersion") -> bool:
    def __gt__(self, other: "ModelVersion") -> bool:
    """
    """
    Compare versions based on semver.
    Compare versions based on semver.


    Args:
    Args:
    other: Another version to compare with
    other: Another version to compare with


    Returns:
    Returns:
    True if this version is greater than the other version, False otherwise
    True if this version is greater than the other version, False otherwise
    """
    """
    return semver.compare(self.version, other.version) > 0
    return semver.compare(self.version, other.version) > 0




    class ModelVersionRegistry:
    class ModelVersionRegistry:
    """
    """
    Registry for tracking versions of AI models.
    Registry for tracking versions of AI models.
    """
    """


    def __init__(self, registry_path: str):
    def __init__(self, registry_path: str):
    """
    """
    Initialize the model version registry.
    Initialize the model version registry.


    Args:
    Args:
    registry_path: Path to the registry file
    registry_path: Path to the registry file
    """
    """
    self.registry_path = registry_path
    self.registry_path = registry_path
    self.versions: Dict[str, Dict[str, ModelVersion]] = (
    self.versions: Dict[str, Dict[str, ModelVersion]] = (
    {}
    {}
    )  # model_id -> version_str -> ModelVersion
    )  # model_id -> version_str -> ModelVersion


    # Create directory if it doesn't exist
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
    os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)


    # Load existing registry if available
    # Load existing registry if available
    self._load_registry()
    self._load_registry()


    def _load_registry(self) -> None:
    def _load_registry(self) -> None:
    """
    """
    Load the registry from disk.
    Load the registry from disk.
    """
    """
    if not os.path.exists(self.registry_path):
    if not os.path.exists(self.registry_path):
    logger.info(
    logger.info(
    f"Model version registry not found at {self.registry_path}. Creating new registry."
    f"Model version registry not found at {self.registry_path}. Creating new registry."
    )
    )
    return try:
    return try:
    with open(self.registry_path, "r") as f:
    with open(self.registry_path, "r") as f:
    data = json.load(f)
    data = json.load(f)


    for model_id, versions_data in data.items():
    for model_id, versions_data in data.items():
    if model_id not in self.versions:
    if model_id not in self.versions:
    self.versions[model_id] = {}
    self.versions[model_id] = {}


    for version_str, version_data in versions_data.items():
    for version_str, version_data in versions_data.items():
    self.versions[model_id][version_str] = ModelVersion.from_dict(
    self.versions[model_id][version_str] = ModelVersion.from_dict(
    version_data
    version_data
    )
    )


    logger.info(f"Loaded version registry with {len(self.versions)} models")
    logger.info(f"Loaded version registry with {len(self.versions)} models")


except json.JSONDecodeError as e:
except json.JSONDecodeError as e:
    error = ConfigurationError(
    error = ConfigurationError(
    message=f"Invalid JSON format in model version registry: {e}",
    message=f"Invalid JSON format in model version registry: {e}",
    config_key=self.registry_path,
    config_key=self.registry_path,
    original_exception=e,
    original_exception=e,
    )
    )
    error.log()
    error.log()
    # Create a new registry
    # Create a new registry
    self._save_registry()
    self._save_registry()
except Exception as e:
except Exception as e:
    logger.error(f"Error loading model version registry: {e}")
    logger.error(f"Error loading model version registry: {e}")
    # Create a new registry
    # Create a new registry
    self._save_registry()
    self._save_registry()


    def _save_registry(self) -> None:
    def _save_registry(self) -> None:
    """
    """
    Save the registry to disk.
    Save the registry to disk.
    """
    """
    try:
    try:
    # Convert to a serializable format
    # Convert to a serializable format
    registry_data = {}
    registry_data = {}


    for model_id, versions in self.versions.items():
    for model_id, versions in self.versions.items():
    registry_data[model_id] = {}
    registry_data[model_id] = {}
    for version_str, version_obj in versions.items():
    for version_str, version_obj in versions.items():
    registry_data[model_id][version_str] = version_obj.to_dict()
    registry_data[model_id][version_str] = version_obj.to_dict()


    with open(self.registry_path, "w") as f:
    with open(self.registry_path, "w") as f:
    json.dump(registry_data, f, indent=2)
    json.dump(registry_data, f, indent=2)


    logger.info(f"Saved version registry with {len(self.versions)} models")
    logger.info(f"Saved version registry with {len(self.versions)} models")


except Exception as e:
except Exception as e:
    logger.error(f"Error saving model version registry: {e}")
    logger.error(f"Error saving model version registry: {e}")


    def register_version(self, version: ModelVersion) -> None:
    def register_version(self, version: ModelVersion) -> None:
    """
    """
    Register a new model version.
    Register a new model version.


    Args:
    Args:
    version: ModelVersion to register
    version: ModelVersion to register


    Raises:
    Raises:
    ValueError: If version already exists or there are conflicts
    ValueError: If version already exists or there are conflicts
    """
    """
    model_id = version.model_id
    model_id = version.model_id
    version_str = version.version
    version_str = version.version


    # Check if version already exists
    # Check if version already exists
    if model_id in self.versions and version_str in self.versions[model_id]:
    if model_id in self.versions and version_str in self.versions[model_id]:
    existing = self.versions[model_id][version_str]
    existing = self.versions[model_id][version_str]


    # Same version string but different content is a conflict
    # Same version string but different content is a conflict
    if existing.hash_value != version.hash_value:
    if existing.hash_value != version.hash_value:
    raise ValueError(
    raise ValueError(
    f"Version {version_str} already exists with different content"
    f"Version {version_str} already exists with different content"
    )
    )


    # Same version string with different features is a conflict
    # Same version string with different features is a conflict
    if set(existing.features) != set(version.features):
    if set(existing.features) != set(version.features):
    raise ValueError(
    raise ValueError(
    f"Version {version_str} already exists with different features"
    f"Version {version_str} already exists with different features"
    )
    )


    # Same version string with different metadata is a conflict
    # Same version string with different metadata is a conflict
    if existing.metadata != version.metadata:
    if existing.metadata != version.metadata:
    raise ValueError(
    raise ValueError(
    f"Version {version_str} already exists with different metadata"
    f"Version {version_str} already exists with different metadata"
    )
    )


    # If we get here, it's an identical version - just log and return
    # If we get here, it's an identical version - just log and return
    logger.info(
    logger.info(
    f"Version {version_str} already registered with identical content"
    f"Version {version_str} already registered with identical content"
    )
    )
    return # Add to registry
    return # Add to registry
    if model_id not in self.versions:
    if model_id not in self.versions:
    self.versions[model_id] = {}
    self.versions[model_id] = {}


    self.versions[model_id][version_str] = version
    self.versions[model_id][version_str] = version


    # Save updated registry
    # Save updated registry
    self._save_registry()
    self._save_registry()


    logger.info(f"Registered version {version_str} for model {model_id}")
    logger.info(f"Registered version {version_str} for model {model_id}")


    def get_version(self, model_id: str, version_str: str) -> Optional[ModelVersion]:
    def get_version(self, model_id: str, version_str: str) -> Optional[ModelVersion]:
    """
    """
    Get a specific version of a model.
    Get a specific version of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    version_str: Version string
    version_str: Version string


    Returns:
    Returns:
    ModelVersion instance or None if not found
    ModelVersion instance or None if not found
    """
    """
    if model_id in self.versions and version_str in self.versions[model_id]:
    if model_id in self.versions and version_str in self.versions[model_id]:
    return self.versions[model_id][version_str]
    return self.versions[model_id][version_str]
    return None
    return None


    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
    """
    """
    Get the latest version of a model.
    Get the latest version of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    Latest ModelVersion instance or None if no versions exist
    Latest ModelVersion instance or None if no versions exist
    """
    """
    if model_id not in self.versions or not self.versions[model_id]:
    if model_id not in self.versions or not self.versions[model_id]:
    return None
    return None


    # Convert to list and sort by version
    # Convert to list and sort by version
    versions = list(self.versions[model_id].values())
    versions = list(self.versions[model_id].values())
    versions.sort(reverse=True)  # Sort in descending order
    versions.sort(reverse=True)  # Sort in descending order


    return versions[0] if versions else None
    return versions[0] if versions else None


    def get_all_versions(self, model_id: str) -> List[ModelVersion]:
    def get_all_versions(self, model_id: str) -> List[ModelVersion]:
    """
    """
    Get all versions of a model.
    Get all versions of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    List of ModelVersion instances sorted in descending order
    List of ModelVersion instances sorted in descending order
    """
    """
    if model_id not in self.versions:
    if model_id not in self.versions:
    return []
    return []


    versions = list(self.versions[model_id].values())
    versions = list(self.versions[model_id].values())
    versions.sort(reverse=True)  # Sort in descending order
    versions.sort(reverse=True)  # Sort in descending order


    return versions
    return versions


    def delete_version(self, model_id: str, version_str: str) -> bool:
    def delete_version(self, model_id: str, version_str: str) -> bool:
    """
    """
    Delete a specific version of a model.
    Delete a specific version of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    version_str: Version string
    version_str: Version string


    Returns:
    Returns:
    True if deleted, False if not found
    True if deleted, False if not found
    """
    """
    if model_id in self.versions and version_str in self.versions[model_id]:
    if model_id in self.versions and version_str in self.versions[model_id]:
    del self.versions[model_id][version_str]
    del self.versions[model_id][version_str]


    # Clean up if no more versions
    # Clean up if no more versions
    if not self.versions[model_id]:
    if not self.versions[model_id]:
    del self.versions[model_id]
    del self.versions[model_id]


    # Save updated registry
    # Save updated registry
    self._save_registry()
    self._save_registry()


    logger.info(f"Deleted version {version_str} of model {model_id}")
    logger.info(f"Deleted version {version_str} of model {model_id}")
    return True
    return True


    return False
    return False


    def check_compatibility(
    def check_compatibility(
    self,
    self,
    source_model_id: str,
    source_model_id: str,
    source_version: str,
    source_version: str,
    target_model_id: str,
    target_model_id: str,
    target_version: str,
    target_version: str,
    ) -> bool:
    ) -> bool:
    """
    """
    Check if two model versions are compatible.
    Check if two model versions are compatible.


    Args:
    Args:
    source_model_id: ID of the source model
    source_model_id: ID of the source model
    source_version: Version string of the source model
    source_version: Version string of the source model
    target_model_id: ID of the target model
    target_model_id: ID of the target model
    target_version: Version string of the target model
    target_version: Version string of the target model


    Returns:
    Returns:
    True if compatible, False otherwise
    True if compatible, False otherwise
    """
    """
    source = self.get_version(source_model_id, source_version)
    source = self.get_version(source_model_id, source_version)
    target = self.get_version(target_model_id, target_version)
    target = self.get_version(target_model_id, target_version)


    if not source or not target:
    if not source or not target:
    return False
    return False


    # Check if models are the same
    # Check if models are the same
    if source_model_id == target_model_id:
    if source_model_id == target_model_id:
    return source.is_compatible_with_version(target)
    return source.is_compatible_with_version(target)


    # Check explicit cross-model compatibility
    # Check explicit cross-model compatibility
    # You might want to implement this based on your specific needs
    # You might want to implement this based on your specific needs


    return False
    return False


    def create_version_from_model(
    def create_version_from_model(
    self,
    self,
    model_info: ModelInfo,
    model_info: ModelInfo,
    version_str: str,
    version_str: str,
    features: List[str] = None,
    features: List[str] = None,
    dependencies: Dict[str, str] = None,
    dependencies: Dict[str, str] = None,
    compatibility: List[str] = None,
    compatibility: List[str] = None,
    metadata: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    ) -> ModelVersion:
    ) -> ModelVersion:
    """
    """
    Create a new version from a model info.
    Create a new version from a model info.


    Args:
    Args:
    model_info: ModelInfo instance
    model_info: ModelInfo instance
    version_str: Version string (e.g., "1.0.0")
    version_str: Version string (e.g., "1.0.0")
    features: Optional list of features this version supports
    features: Optional list of features this version supports
    dependencies: Optional dependencies required by this version
    dependencies: Optional dependencies required by this version
    compatibility: Optional list of other model versions this is compatible with
    compatibility: Optional list of other model versions this is compatible with
    metadata: Optional additional metadata for this version
    metadata: Optional additional metadata for this version


    Returns:
    Returns:
    ModelVersion instance
    ModelVersion instance


    Raises:
    Raises:
    ValueError: If version string is invalid
    ValueError: If version string is invalid
    """
    """
    # Calculate hash of model file if it exists
    # Calculate hash of model file if it exists
    hash_value = ""
    hash_value = ""
    if os.path.exists(model_info.path):
    if os.path.exists(model_info.path):
    try:
    try:
    if os.path.isfile(model_info.path):
    if os.path.isfile(model_info.path):
    # For files, calculate SHA256 hash
    # For files, calculate SHA256 hash
    hash_value = self._calculate_file_hash(model_info.path)
    hash_value = self._calculate_file_hash(model_info.path)
    else:
    else:
    # For directories, calculate hash based on contents
    # For directories, calculate hash based on contents
    hash_value = self._calculate_directory_hash(model_info.path)
    hash_value = self._calculate_directory_hash(model_info.path)
except Exception as e:
except Exception as e:
    logger.warning(f"Error calculating hash for {model_info.path}: {e}")
    logger.warning(f"Error calculating hash for {model_info.path}: {e}")


    # Create a new version
    # Create a new version
    version = ModelVersion(
    version = ModelVersion(
    version=version_str,
    version=version_str,
    model_id=model_info.id,
    model_id=model_info.id,
    hash_value=hash_value,
    hash_value=hash_value,
    features=features or [],
    features=features or [],
    dependencies=dependencies or {},
    dependencies=dependencies or {},
    is_compatible_with=compatibility or [],
    is_compatible_with=compatibility or [],
    metadata=metadata or {},
    metadata=metadata or {},
    )
    )


    # Register the version
    # Register the version
    self.register_version(version)
    self.register_version(version)


    return version
    return version


    def _calculate_file_hash(self, file_path: str) -> str:
    def _calculate_file_hash(self, file_path: str) -> str:
    """
    """
    Calculate SHA256 hash of a file.
    Calculate SHA256 hash of a file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    SHA256 hash as a hexadecimal string
    SHA256 hash as a hexadecimal string
    """
    """
    hash_obj = hashlib.sha256()
    hash_obj = hashlib.sha256()


    # Read file in chunks to handle large files
    # Read file in chunks to handle large files
    with open(file_path, "rb") as f:
    with open(file_path, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
    for chunk in iter(lambda: f.read(4096), b""):
    hash_obj.update(chunk)
    hash_obj.update(chunk)


    return hash_obj.hexdigest()
    return hash_obj.hexdigest()


    def _calculate_directory_hash(self, dir_path: str) -> str:
    def _calculate_directory_hash(self, dir_path: str) -> str:
    """
    """
    Calculate hash for a directory by combining hashes of all files.
    Calculate hash for a directory by combining hashes of all files.


    Args:
    Args:
    dir_path: Path to the directory
    dir_path: Path to the directory


    Returns:
    Returns:
    Combined hash as a hexadecimal string
    Combined hash as a hexadecimal string
    """
    """
    hash_obj = hashlib.sha256()
    hash_obj = hashlib.sha256()


    # Get all files in the directory and its subdirectories
    # Get all files in the directory and its subdirectories
    for root, _, files in os.walk(dir_path):
    for root, _, files in os.walk(dir_path):
    for file in sorted(files):  # Sort for deterministic ordering
    for file in sorted(files):  # Sort for deterministic ordering
    file_path = os.path.join(root, file)
    file_path = os.path.join(root, file)


    # Skip hidden files
    # Skip hidden files
    if os.path.basename(file_path).startswith("."):
    if os.path.basename(file_path).startswith("."):
    continue
    continue


    # Update hash with file path (relative to dir_path) and content hash
    # Update hash with file path (relative to dir_path) and content hash
    rel_path = os.path.relpath(file_path, dir_path)
    rel_path = os.path.relpath(file_path, dir_path)
    hash_obj.update(rel_path.encode())
    hash_obj.update(rel_path.encode())


    try:
    try:
    file_hash = self._calculate_file_hash(file_path)
    file_hash = self._calculate_file_hash(file_path)
    hash_obj.update(file_hash.encode())
    hash_obj.update(file_hash.encode())
except Exception as e:
except Exception as e:
    logger.warning(f"Error calculating hash for {file_path}: {e}")
    logger.warning(f"Error calculating hash for {file_path}: {e}")


    return hash_obj.hexdigest()
    return hash_obj.hexdigest()




    class ModelMigrationTool:
    class ModelMigrationTool:
    """
    """
    Tool for migrating models between different versions.
    Tool for migrating models between different versions.
    """
    """


    def __init__(self, version_registry: ModelVersionRegistry):
    def __init__(self, version_registry: ModelVersionRegistry):
    """
    """
    Initialize the model migration tool.
    Initialize the model migration tool.


    Args:
    Args:
    version_registry: ModelVersionRegistry instance
    version_registry: ModelVersionRegistry instance
    """
    """
    self.version_registry = version_registry
    self.version_registry = version_registry
    self.migration_functions: Dict[str, Dict[Tuple[str, str], Callable]] = {}
    self.migration_functions: Dict[str, Dict[Tuple[str, str], Callable]] = {}


    def register_migration_function(
    def register_migration_function(
    self,
    self,
    model_id: str,
    model_id: str,
    source_version: str,
    source_version: str,
    target_version: str,
    target_version: str,
    migration_fn: Callable,
    migration_fn: Callable,
    ) -> None:
    ) -> None:
    """
    """
    Register a migration function for a specific model version transition.
    Register a migration function for a specific model version transition.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    source_version: Source version string
    source_version: Source version string
    target_version: Target version string
    target_version: Target version string
    migration_fn: Function that handles the migration
    migration_fn: Function that handles the migration
    """
    """
    if model_id not in self.migration_functions:
    if model_id not in self.migration_functions:
    self.migration_functions[model_id] = {}
    self.migration_functions[model_id] = {}


    self.migration_functions[model_id][
    self.migration_functions[model_id][
    (source_version, target_version)
    (source_version, target_version)
    ] = migration_fn
    ] = migration_fn
    logger.info(
    logger.info(
    f"Registered migration function from {source_version} to {target_version} for model {model_id}"
    f"Registered migration function from {source_version} to {target_version} for model {model_id}"
    )
    )


    def can_migrate(
    def can_migrate(
    self, model_id: str, source_version: str, target_version: str
    self, model_id: str, source_version: str, target_version: str
    ) -> bool:
    ) -> bool:
    """
    """
    Check if migration is possible between two versions.
    Check if migration is possible between two versions.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    source_version: Source version string
    source_version: Source version string
    target_version: Target version string
    target_version: Target version string


    Returns:
    Returns:
    True if migration is possible, False otherwise
    True if migration is possible, False otherwise
    """
    """
    # Direct migration path exists
    # Direct migration path exists
    if (
    if (
    model_id in self.migration_functions
    model_id in self.migration_functions
    and (source_version, target_version) in self.migration_functions[model_id]
    and (source_version, target_version) in self.migration_functions[model_id]
    ):
    ):
    return True
    return True


    # Find a migration path
    # Find a migration path
    migration_path = self._find_migration_path(
    migration_path = self._find_migration_path(
    model_id, source_version, target_version
    model_id, source_version, target_version
    )
    )
    return bool(migration_path)
    return bool(migration_path)


    def migrate(
    def migrate(
    self, model_info: ModelInfo, source_version: str, target_version: str, **kwargs
    self, model_info: ModelInfo, source_version: str, target_version: str, **kwargs
    ) -> ModelInfo:
    ) -> ModelInfo:
    """
    """
    Migrate a model from one version to another.
    Migrate a model from one version to another.


    Args:
    Args:
    model_info: ModelInfo instance to migrate
    model_info: ModelInfo instance to migrate
    source_version: Source version string
    source_version: Source version string
    target_version: Target version string
    target_version: Target version string
    **kwargs: Additional parameters for the migration
    **kwargs: Additional parameters for the migration


    Returns:
    Returns:
    Updated ModelInfo instance
    Updated ModelInfo instance


    Raises:
    Raises:
    ValueError: If migration is not possible
    ValueError: If migration is not possible
    """
    """
    model_id = model_info.id
    model_id = model_info.id


    # Check if direct migration is possible
    # Check if direct migration is possible
    if (
    if (
    model_id in self.migration_functions
    model_id in self.migration_functions
    and (source_version, target_version) in self.migration_functions[model_id]
    and (source_version, target_version) in self.migration_functions[model_id]
    ):
    ):
    # Execute direct migration
    # Execute direct migration
    migration_fn = self.migration_functions[model_id][
    migration_fn = self.migration_functions[model_id][
    (source_version, target_version)
    (source_version, target_version)
    ]
    ]
    return migration_fn(model_info, **kwargs)
    return migration_fn(model_info, **kwargs)


    # Find a migration path
    # Find a migration path
    migration_path = self._find_migration_path(
    migration_path = self._find_migration_path(
    model_id, source_version, target_version
    model_id, source_version, target_version
    )
    )


    if not migration_path:
    if not migration_path:
    raise ValueError(
    raise ValueError(
    f"No migration path found from {source_version} to {target_version} for model {model_id}"
    f"No migration path found from {source_version} to {target_version} for model {model_id}"
    )
    )


    logger.info(
    logger.info(
    f"Found migration path for model {model_id}: {' -> '.join(migration_path)}"
    f"Found migration path for model {model_id}: {' -> '.join(migration_path)}"
    )
    )


    # Execute migrations in sequence
    # Execute migrations in sequence
    current_info = copy.deepcopy(model_info)
    current_info = copy.deepcopy(model_info)
    current_version = source_version
    current_version = source_version


    for next_version in migration_path[1:]:  # Skip the first version (source)
    for next_version in migration_path[1:]:  # Skip the first version (source)
    migration_fn = self.migration_functions[model_id][
    migration_fn = self.migration_functions[model_id][
    (current_version, next_version)
    (current_version, next_version)
    ]
    ]
    current_info = migration_fn(current_info, **kwargs)
    current_info = migration_fn(current_info, **kwargs)
    current_version = next_version
    current_version = next_version


    return current_info
    return current_info


    def _find_migration_path(
    def _find_migration_path(
    self, model_id: str, source_version: str, target_version: str
    self, model_id: str, source_version: str, target_version: str
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    Find a path of migrations from source to target version.
    Find a path of migrations from source to target version.


    Uses breadth-first search to find the shortest path.
    Uses breadth-first search to find the shortest path.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    source_version: Source version string
    source_version: Source version string
    target_version: Target version string
    target_version: Target version string


    Returns:
    Returns:
    List of version strings forming a path, or empty list if no path exists
    List of version strings forming a path, or empty list if no path exists
    """
    """
    if model_id not in self.migration_functions:
    if model_id not in self.migration_functions:
    return []
    return []


    # Get all available migrations for this model
    # Get all available migrations for this model
    migrations = self.migration_functions[model_id]
    migrations = self.migration_functions[model_id]


    # BFS to find shortest path
    # BFS to find shortest path
    queue = [(source_version, [source_version])]
    queue = [(source_version, [source_version])]
    visited = set([source_version])
    visited = set([source_version])


    while queue:
    while queue:
    current_version, path = queue.pop(0)
    current_version, path = queue.pop(0)


    if current_version == target_version:
    if current_version == target_version:
    return path
    return path


    # Add all connected versions
    # Add all connected versions
    for src, dst in migrations.keys():
    for src, dst in migrations.keys():
    if src == current_version and dst not in visited:
    if src == current_version and dst not in visited:
    visited.add(dst)
    visited.add(dst)
    queue.append((dst, path + [dst]))
    queue.append((dst, path + [dst]))


    return []  # No path found
    return []  # No path found




    class VersionedModelManager:
    class VersionedModelManager:
    """
    """
    Extension of ModelManager that adds versioning capabilities.
    Extension of ModelManager that adds versioning capabilities.
    """
    """


    def __init__(self, model_manager, models_dir: str):
    def __init__(self, model_manager, models_dir: str):
    """
    """
    Initialize the versioned model manager.
    Initialize the versioned model manager.


    Args:
    Args:
    model_manager: ModelManager instance
    model_manager: ModelManager instance
    models_dir: Directory where models are stored
    models_dir: Directory where models are stored
    """
    """
    self.model_manager = model_manager
    self.model_manager = model_manager
    self.version_registry = ModelVersionRegistry(
    self.version_registry = ModelVersionRegistry(
    os.path.join(models_dir, "version_registry.json")
    os.path.join(models_dir, "version_registry.json")
    )
    )
    self.migration_tool = ModelMigrationTool(self.version_registry)
    self.migration_tool = ModelMigrationTool(self.version_registry)


    def register_model_version(
    def register_model_version(
    self,
    self,
    model_info: ModelInfo,
    model_info: ModelInfo,
    version_str: str,
    version_str: str,
    features: List[str] = None,
    features: List[str] = None,
    dependencies: Dict[str, str] = None,
    dependencies: Dict[str, str] = None,
    compatibility: List[str] = None,
    compatibility: List[str] = None,
    metadata: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    ) -> ModelVersion:
    ) -> ModelVersion:
    """
    """
    Register a new version for a model.
    Register a new version for a model.


    Args:
    Args:
    model_info: ModelInfo instance
    model_info: ModelInfo instance
    version_str: Version string (e.g., "1.0.0")
    version_str: Version string (e.g., "1.0.0")
    features: Optional list of features this version supports
    features: Optional list of features this version supports
    dependencies: Optional dependencies required by this version
    dependencies: Optional dependencies required by this version
    compatibility: Optional list of other model versions this is compatible with
    compatibility: Optional list of other model versions this is compatible with
    metadata: Optional additional metadata for this version
    metadata: Optional additional metadata for this version


    Returns:
    Returns:
    ModelVersion instance
    ModelVersion instance
    """
    """
    return self.version_registry.create_version_from_model(
    return self.version_registry.create_version_from_model(
    model_info=model_info,
    model_info=model_info,
    version_str=version_str,
    version_str=version_str,
    features=features,
    features=features,
    dependencies=dependencies,
    dependencies=dependencies,
    compatibility=compatibility,
    compatibility=compatibility,
    metadata=metadata,
    metadata=metadata,
    )
    )


    def get_model_version(
    def get_model_version(
    self, model_id: str, version_str: str = None
    self, model_id: str, version_str: str = None
    ) -> Optional[ModelVersion]:
    ) -> Optional[ModelVersion]:
    """
    """
    Get a specific version of a model, or latest if version not specified.
    Get a specific version of a model, or latest if version not specified.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    version_str: Optional version string, defaults to latest
    version_str: Optional version string, defaults to latest


    Returns:
    Returns:
    ModelVersion instance or None if not found
    ModelVersion instance or None if not found
    """
    """
    if version_str:
    if version_str:
    return self.version_registry.get_version(model_id, version_str)
    return self.version_registry.get_version(model_id, version_str)
    else:
    else:
    return self.version_registry.get_latest_version(model_id)
    return self.version_registry.get_latest_version(model_id)


    def get_all_model_versions(self, model_id: str) -> List[ModelVersion]:
    def get_all_model_versions(self, model_id: str) -> List[ModelVersion]:
    """
    """
    Get all versions of a model.
    Get all versions of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    List of ModelVersion instances sorted in descending order
    List of ModelVersion instances sorted in descending order
    """
    """
    return self.version_registry.get_all_versions(model_id)
    return self.version_registry.get_all_versions(model_id)


    def load_model_version(
    def load_model_version(
    self, model_id: str, version_str: str = None, **kwargs
    self, model_id: str, version_str: str = None, **kwargs
    ) -> Any:
    ) -> Any:
    """
    """
    Load a specific version of a model.
    Load a specific version of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    version_str: Optional version string, defaults to latest
    version_str: Optional version string, defaults to latest
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ValueError: If model or version not found
    ValueError: If model or version not found
    """
    """
    # Get the model info
    # Get the model info
    model_info = self.model_manager.get_model_info(model_id)
    model_info = self.model_manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ValueError(f"Model with ID {model_id} not found")
    raise ValueError(f"Model with ID {model_id} not found")


    # Get version info
    # Get version info
    version = self.get_model_version(model_id, version_str)
    version = self.get_model_version(model_id, version_str)
    if not version:
    if not version:
    if version_str:
    if version_str:
    raise ValueError(f"Version {version_str} of model {model_id} not found")
    raise ValueError(f"Version {version_str} of model {model_id} not found")
    else:
    else:
    raise ValueError(f"No versions found for model {model_id}")
    raise ValueError(f"No versions found for model {model_id}")


    # Verify model integrity if hash is available
    # Verify model integrity if hash is available
    if version.hash_value and os.path.exists(model_info.path):
    if version.hash_value and os.path.exists(model_info.path):
    if os.path.isfile(model_info.path):
    if os.path.isfile(model_info.path):
    current_hash = self.version_registry._calculate_file_hash(
    current_hash = self.version_registry._calculate_file_hash(
    model_info.path
    model_info.path
    )
    )
    else:
    else:
    current_hash = self.version_registry._calculate_directory_hash(
    current_hash = self.version_registry._calculate_directory_hash(
    model_info.path
    model_info.path
    )
    )


    if current_hash != version.hash_value:
    if current_hash != version.hash_value:
    logger.warning(
    logger.warning(
    f"Model hash mismatch for {model_id} version {version.version}. "
    f"Model hash mismatch for {model_id} version {version.version}. "
    "The model may have been modified since this version was created."
    "The model may have been modified since this version was created."
    )
    )


    # Load the model
    # Load the model
    return self.model_manager.load_model(model_id, **kwargs)
    return self.model_manager.load_model(model_id, **kwargs)


    def register_migration_function(
    def register_migration_function(
    self,
    self,
    model_id: str,
    model_id: str,
    source_version: str,
    source_version: str,
    target_version: str,
    target_version: str,
    migration_fn: Callable,
    migration_fn: Callable,
    ) -> None:
    ) -> None:
    """
    """
    Register a migration function for version transitions.
    Register a migration function for version transitions.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    source_version: Source version string
    source_version: Source version string
    target_version: Target version string
    target_version: Target version string
    migration_fn: Function that handles the migration
    migration_fn: Function that handles the migration
    """
    """
    self.migration_tool.register_migration_function(
    self.migration_tool.register_migration_function(
    model_id=model_id,
    model_id=model_id,
    source_version=source_version,
    source_version=source_version,
    target_version=target_version,
    target_version=target_version,
    migration_fn=migration_fn,
    migration_fn=migration_fn,
    )
    )


    def migrate_model(
    def migrate_model(
    self, model_info: ModelInfo, target_version: str, **kwargs
    self, model_info: ModelInfo, target_version: str, **kwargs
    ) -> ModelInfo:
    ) -> ModelInfo:
    """
    """
    Migrate a model to a specific version.
    Migrate a model to a specific version.


    Args:
    Args:
    model_info: ModelInfo instance to migrate
    model_info: ModelInfo instance to migrate
    target_version: Target version string
    target_version: Target version string
    **kwargs: Additional parameters for the migration
    **kwargs: Additional parameters for the migration


    Returns:
    Returns:
    Updated ModelInfo instance
    Updated ModelInfo instance


    Raises:
    Raises:
    ValueError: If migration is not possible
    ValueError: If migration is not possible
    """
    """
    # Get current version
    # Get current version
    current_version = self.version_registry.get_latest_version(model_info.id)
    current_version = self.version_registry.get_latest_version(model_info.id)
    if not current_version:
    if not current_version:
    raise ValueError(f"No versions found for model {model_info.id}")
    raise ValueError(f"No versions found for model {model_info.id}")


    # If already at target version, return as is
    # If already at target version, return as is
    if current_version.version == target_version:
    if current_version.version == target_version:
    return model_info
    return model_info


    # Migrate
    # Migrate
    return self.migration_tool.migrate(
    return self.migration_tool.migrate(
    model_info=model_info,
    model_info=model_info,
    source_version=current_version.version,
    source_version=current_version.version,
    target_version=target_version,
    target_version=target_version,
    **kwargs,
    **kwargs,
    )
    )


    def check_compatibility(
    def check_compatibility(
    self, model_id1: str, version1: str, model_id2: str, version2: str
    self, model_id1: str, version1: str, model_id2: str, version2: str
    ) -> bool:
    ) -> bool:
    """
    """
    Check if two model versions are compatible.
    Check if two model versions are compatible.


    Args:
    Args:
    model_id1: ID of the first model
    model_id1: ID of the first model
    version1: Version of the first model
    version1: Version of the first model
    model_id2: ID of the second model
    model_id2: ID of the second model
    version2: Version of the second model
    version2: Version of the second model


    Returns:
    Returns:
    True if compatible, False otherwise
    True if compatible, False otherwise
    """
    """
    return self.version_registry.check_compatibility(
    return self.version_registry.check_compatibility(
    source_model_id=model_id1,
    source_model_id=model_id1,
    source_version=version1,
    source_version=version1,
    target_model_id=model_id2,
    target_model_id=model_id2,
    target_version=version2,
    target_version=version2,
    )
    )