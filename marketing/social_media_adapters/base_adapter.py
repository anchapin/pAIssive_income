"""
Base adapter for social media platforms.

This module provides a base class for adapters that connect to various social media platforms.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)


class BaseSocialMediaAdapter(ABC):
    """
    Base class for social media platform adapters.

    This class defines the interface that all social media platform adapters must implement.
    It provides methods for authenticating with platforms, posting content, retrieving analytics,
    and managing social media campaigns.
    """

    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
        """
        Initialize the base social media adapter.

        Args:
            connection_id: Unique identifier for the connection
            connection_data: Connection data including credentials and settings
        """
        self.connection_id = connection_id
        self.platform = connection_data.get("platform")
        self.account_name = connection_data.get("account_name", "Unknown")
        self.account_id = connection_data.get("account_id", "Unknown")
        self.credentials = connection_data.get("credentials", {})
        self.settings = connection_data.get("settings", {})
        self.capabilities = connection_data.get("capabilities", [])
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if the adapter is connected to the platform."""
        return self._connected

    @abstractmethod
    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the social media platform.

        Returns:
            Dictionary containing authentication result and any additional platform data

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """
        Validate content for posting to the platform.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise

        Raises:
            ContentValidationError: If content validation fails with specific reason
        """
        pass

    @abstractmethod
    def post_content(
        self,
        content: Dict[str, Any],
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post content to the platform.

        Args:
            content: Content to post
            visibility: Visibility setting (public, private, etc.)
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform-assigned ID

        Raises:
            ContentValidationError: If content validation fails
            PostingError: If posting fails
        """
        pass

    @abstractmethod
    def schedule_post(
        self,
        content: Dict[str, Any],
        schedule_time: datetime,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a post for later publication.

        Args:
            content: Content to post
            schedule_time: Time to publish the post
            visibility: Visibility setting (public, private, etc.)
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the scheduled post details and ID

        Raises:
            ContentValidationError: If content validation fails
            SchedulingError: If scheduling fails
        """
        pass

    @abstractmethod
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific post.

        Args:
            post_id: ID of the post to retrieve

        Returns:
            Dictionary containing the post details

        Raises:
            PostNotFoundError: If the post ID is not found
        """
        pass

    @abstractmethod
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the platform.

        Args:
            post_id: ID of the post to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            PostNotFoundError: If the post ID is not found
            DeletionError: If deletion fails
        """
        pass

    @abstractmethod
    def get_analytics(
        self,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get analytics data from the platform.

        Args:
            post_id: Optional ID of a specific post to get analytics for
            metrics: Optional list of specific metrics to retrieve
            start_date: Optional start date for the analytics period
            end_date: Optional end date for the analytics period

        Returns:
            Dictionary containing the analytics data
        """
        pass

    @abstractmethod
    def get_audience_insights(
        self, metrics: Optional[List[str]] = None, segment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get audience insights from the platform.

        Args:
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment to get insights for

        Returns:
            Dictionary containing the audience insights
        """
        pass

    def has_capability(self, capability: str) -> bool:
        """
        Check if the platform has a specific capability.

        Args:
            capability: Capability to check for

        Returns:
            True if the platform has the capability, False otherwise
        """
        return capability in self.capabilities
