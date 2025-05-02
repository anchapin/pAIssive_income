"""
API version management.

This module provides classes and functions for managing API versions.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from .config import APIVersion


class ChangeType(str, Enum):
    """
    Enum for types of API changes.
    """

    ADDED = "added"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class VersionChange:
    """
    Represents a change between API versions.
    """

    def __init__(
        self,
        endpoint: str,
        change_type: ChangeType,
        description: str,
        from_version: Optional[APIVersion] = None,
        to_version: Optional[APIVersion] = None,
        sunset_date: Optional[datetime] = None,
    ):
        """
        Initialize a version change.

        Args:
            endpoint: The API endpoint that changed
            change_type: Type of change
            description: Description of the change
            from_version: Version where the change was introduced (for MODIFIED, DEPRECATED)
            to_version: Version where the endpoint was removed (for REMOVED)
            sunset_date: Date when the deprecated endpoint will be removed
        """
        self.endpoint = endpoint
        self.change_type = change_type
        self.description = description
        self.from_version = from_version
        self.to_version = to_version
        self.sunset_date = sunset_date

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the change to a dictionary.

        Returns:
            Dictionary representation of the change
        """
        return {
            "endpoint": self.endpoint,
            "change_type": self.change_type.value,
            "description": self.description,
            "from_version": self.from_version.value if self.from_version else None,
            "to_version": self.to_version.value if self.to_version else None,
            "sunset_date": self.sunset_date.isoformat() if self.sunset_date else None,
        }


class VersionManager:
    """
    Manages API versions and changes between versions.
    """

    def __init__(self, default_deprecation_period: int = 180):
        """
        Initialize the version manager.

        Args:
            default_deprecation_period: Default number of days before a deprecated endpoint is removed
        """
        self.changes: Dict[APIVersion, List[VersionChange]] = {}
        self.default_deprecation_period = default_deprecation_period

        # Initialize changes for each version
        for version in APIVersion:
            self.changes[version] = []

    def add_endpoint(
        self, endpoint: str, version: APIVersion, description: str
    ) -> None:
        """
        Add a new endpoint to a version.

        Args:
            endpoint: The new endpoint
            version: Version where the endpoint was added
            description: Description of the endpoint
        """
        change = VersionChange(
            endpoint=endpoint,
            change_type=ChangeType.ADDED,
            description=description,
            from_version=version,
        )
        self.changes[version].append(change)

    def modify_endpoint(
        self, endpoint: str, version: APIVersion, description: str
    ) -> None:
        """
        Mark an endpoint as modified in a version.

        Args:
            endpoint: The modified endpoint
            version: Version where the endpoint was modified
            description: Description of the modification
        """
        change = VersionChange(
            endpoint=endpoint,
            change_type=ChangeType.MODIFIED,
            description=description,
            from_version=version,
        )
        self.changes[version].append(change)

    def deprecate_endpoint(
        self,
        endpoint: str,
        version: APIVersion,
        description: str,
        sunset_date: Optional[datetime] = None,
    ) -> None:
        """
        Mark an endpoint as deprecated in a version.

        Args:
            endpoint: The deprecated endpoint
            version: Version where the endpoint was deprecated
            description: Description of the deprecation
            sunset_date: Date when the endpoint will be removed
        """
        if sunset_date is None:
            sunset_date = datetime.now() + timedelta(
                days=self.default_deprecation_period
            )

        change = VersionChange(
            endpoint=endpoint,
            change_type=ChangeType.DEPRECATED,
            description=description,
            from_version=version,
            sunset_date=sunset_date,
        )
        self.changes[version].append(change)

    def remove_endpoint(
        self,
        endpoint: str,
        version: APIVersion,
        description: str,
        from_version: Optional[APIVersion] = None,
    ) -> None:
        """
        Mark an endpoint as removed in a version.

        Args:
            endpoint: The removed endpoint
            version: Version where the endpoint was removed
            description: Description of the removal
            from_version: Version where the endpoint was originally added
        """
        change = VersionChange(
            endpoint=endpoint,
            change_type=ChangeType.REMOVED,
            description=description,
            from_version=from_version,
            to_version=version,
        )
        self.changes[version].append(change)

    def get_changes_for_version(self, version: APIVersion) -> List[Dict[str, Any]]:
        """
        Get all changes for a specific version.

        Args:
            version: The version to get changes for

        Returns:
            List of changes for the version
        """
        return [change.to_dict() for change in self.changes.get(version, [])]

    def get_deprecated_endpoints(self) -> List[Dict[str, Any]]:
        """
        Get all deprecated endpoints across all versions.

        Returns:
            List of deprecated endpoints
        """
        deprecated = []
        for version in self.changes:
            for change in self.changes[version]:
                if change.change_type == ChangeType.DEPRECATED:
                    deprecated.append(change.to_dict())
        return deprecated

    def get_removed_endpoints(self) -> List[Dict[str, Any]]:
        """
        Get all removed endpoints across all versions.

        Returns:
            List of removed endpoints
        """
        removed = []
        for version in self.changes:
            for change in self.changes[version]:
                if change.change_type == ChangeType.REMOVED:
                    removed.append(change.to_dict())
        return removed

    def get_changelog(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a complete changelog for all versions.

        Returns:
            Dictionary mapping version values to lists of changes
        """
        changelog = {}
        for version in self.changes:
            changelog[version.value] = self.get_changes_for_version(version)
        return changelog

    def is_endpoint_available(self, endpoint: str, version: APIVersion) -> bool:
        """
        Check if an endpoint is available in a specific version.

        Args:
            endpoint: The endpoint to check
            version: The version to check

        Returns:
            True if the endpoint is available, False otherwise
        """
        # Check if the endpoint was removed in this version
        for change in self.changes.get(version, []):
            if change.endpoint == endpoint and change.change_type == ChangeType.REMOVED:
                return False

        # Check if the endpoint was added in this version or an earlier version
        versions = list(APIVersion)
        version_idx = versions.index(version)

        for i in range(version_idx + 1):
            current_version = versions[i]
            for change in self.changes.get(current_version, []):
                if (
                    change.endpoint == endpoint
                    and change.change_type == ChangeType.ADDED
                ):
                    return True

        return False
