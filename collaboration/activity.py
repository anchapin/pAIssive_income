"""
Activity tracking and notification system for the collaboration module.

This module provides classes for tracking user activity and sending notifications
to team members about important events and changes.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# Set up logging
logger = logging.getLogger(__name__)


class ActivityType(Enum):
    """Types of activities that can be tracked."""

    # Workspace activities
    WORKSPACE_CREATED = "workspace_created"
    WORKSPACE_UPDATED = "workspace_updated"
    WORKSPACE_DELETED = "workspace_deleted"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_UPDATED = "member_role_updated"

    # Project activities
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_SHARED = "project_shared"
    PROJECT_UNSHARED = "project_unshared"

    # Version control activities
    VERSION_CREATED = "version_created"
    VERSION_RESTORED = "version_restored"
    VERSION_TAGGED = "version_tagged"

    # Comment activities
    COMMENT_ADDED = "comment_added"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"

    # Integration activities
    INTEGRATION_ADDED = "integration_added"
    INTEGRATION_REMOVED = "integration_removed"
    INTEGRATION_UPDATED = "integration_updated"

    # User activities
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"


class ActivityLog:
    """
    Represents a log of user activity.

    This class stores information about an activity, such as who performed it,
    when it occurred, and what resources were affected.
    """

    def __init__(
        self,
        activity_id: Optional[str] = None,
        activity_type: Optional[ActivityType] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize an activity log.

        Args:
            activity_id: Optional ID for the activity (generated if not provided)
            activity_type: Type of activity
            user_id: ID of the user who performed the activity
            workspace_id: Optional ID of the workspace affected
            project_id: Optional ID of the project affected
            resource_id: Optional ID of the resource affected
            description: Optional description of the activity
        """
        self.activity_id = activity_id or str(uuid.uuid4())
        self.activity_type = activity_type
        self.user_id = user_id
        self.timestamp = datetime.now().isoformat()
        self.workspace_id = workspace_id
        self.project_id = project_id
        self.resource_id = resource_id
        self.description = description
        self.metadata: Dict[str, Any] = {}

    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to the activity log.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the activity log to a dictionary.

        Returns:
            Dictionary representation of the activity log
        """
        return {
            "activity_id": self.activity_id,
            "activity_type": self.activity_type.value if self.activity_type else None,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "resource_id": self.resource_id,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityLog":
        """
        Create an activity log from a dictionary.

        Args:
            data: Dictionary representation of an activity log

        Returns:
            ActivityLog object
        """
        activity_type = None
        if data.get("activity_type"):
            try:
                activity_type = ActivityType(data["activity_type"])
            except ValueError:
                logger.warning(f"Unknown activity type: {data['activity_type']}")

        activity = cls(
            activity_id=data["activity_id"],
            activity_type=activity_type,
            user_id=data["user_id"],
            workspace_id=data.get("workspace_id"),
            project_id=data.get("project_id"),
            resource_id=data.get("resource_id"),
            description=data.get("description"),
        )

        activity.timestamp = data["timestamp"]
        activity.metadata = data.get("metadata", {})

        return activity


class ActivityTracker:
    """
    Tracks user activity in workspaces and projects.

    This class provides functionality for logging and querying user activity,
    which can be used for auditing, analytics, and notifications.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the activity tracker.

        Args:
            storage_path: Path where activity logs will be stored
        """
        self.storage_path = storage_path or "activity_logs"
        os.makedirs(self.storage_path, exist_ok=True)

        self.activities: Dict[str, Dict[str, Any]] = {}
        self.workspace_activities: Dict[str, List[str]] = {}
        self.project_activities: Dict[str, List[str]] = {}
        self.user_activities: Dict[str, List[str]] = {}

        self._load_activity_data()

    def _load_activity_data(self):
        """Load activity data from disk."""
        activities_file = os.path.join(self.storage_path, "activities.json")
        workspace_activities_file = os.path.join(self.storage_path, 
            "workspace_activities.json")
        project_activities_file = os.path.join(self.storage_path, 
            "project_activities.json")
        user_activities_file = os.path.join(self.storage_path, "user_activities.json")

        if os.path.exists(activities_file):
            try:
                with open(activities_file, "r") as f:
                    self.activities = json.load(f)
                logger.info(f"Loaded {len(self.activities)} activity logs")
            except Exception as e:
                logger.error(f"Failed to load activity logs: {e}")
                self.activities = {}

        if os.path.exists(workspace_activities_file):
            try:
                with open(workspace_activities_file, "r") as f:
                    self.workspace_activities = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load workspace activities: {e}")
                self.workspace_activities = {}

        if os.path.exists(project_activities_file):
            try:
                with open(project_activities_file, "r") as f:
                    self.project_activities = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load project activities: {e}")
                self.project_activities = {}

        if os.path.exists(user_activities_file):
            try:
                with open(user_activities_file, "r") as f:
                    self.user_activities = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load user activities: {e}")
                self.user_activities = {}

    def _save_activity_data(self):
        """Save activity data to disk."""
        activities_file = os.path.join(self.storage_path, "activities.json")
        workspace_activities_file = os.path.join(self.storage_path, 
            "workspace_activities.json")
        project_activities_file = os.path.join(self.storage_path, 
            "project_activities.json")
        user_activities_file = os.path.join(self.storage_path, "user_activities.json")

        with open(activities_file, "w") as f:
            json.dump(self.activities, f, indent=2)

        with open(workspace_activities_file, "w") as f:
            json.dump(self.workspace_activities, f, indent=2)

        with open(project_activities_file, "w") as f:
            json.dump(self.project_activities, f, indent=2)

        with open(user_activities_file, "w") as f:
            json.dump(self.user_activities, f, indent=2)

    def log_activity(
        self,
        activity_type: ActivityType,
        user_id: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ActivityLog:
        """
        Log a user activity.

        Args:
            activity_type: Type of activity
            user_id: ID of the user who performed the activity
            workspace_id: Optional ID of the workspace affected
            project_id: Optional ID of the project affected
            resource_id: Optional ID of the resource affected
            description: Optional description of the activity
            metadata: Optional metadata for the activity

        Returns:
            ActivityLog object
        """
        activity = ActivityLog(
            activity_type=activity_type,
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            resource_id=resource_id,
            description=description,
        )

        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                activity.add_metadata(key, value)

        # Store activity
        self.activities[activity.activity_id] = activity.to_dict()

        # Update workspace activities
        if workspace_id:
            if workspace_id not in self.workspace_activities:
                self.workspace_activities[workspace_id] = []
            self.workspace_activities[workspace_id].append(activity.activity_id)

        # Update project activities
        if project_id:
            if project_id not in self.project_activities:
                self.project_activities[project_id] = []
            self.project_activities[project_id].append(activity.activity_id)

        # Update user activities
        if user_id not in self.user_activities:
            self.user_activities[user_id] = []
        self.user_activities[user_id].append(activity.activity_id)

        self._save_activity_data()

        logger.info(f"Logged activity: {activity_type.value} by user {user_id}")
        return activity

    def get_activity(self, activity_id: str) -> Optional[ActivityLog]:
        """
        Get an activity log by ID.

        Args:
            activity_id: ID of the activity

        Returns:
            ActivityLog object or None if not found
        """
        if activity_id not in self.activities:
            return None

        return ActivityLog.from_dict(self.activities[activity_id])

    def get_workspace_activities(
        self,
        workspace_id: str,
        limit: Optional[int] = None,
        activity_types: Optional[List[ActivityType]] = None,
    ) -> List[ActivityLog]:
        """
        Get activities for a workspace.

        Args:
            workspace_id: ID of the workspace
            limit: Optional maximum number of activities to return
            activity_types: Optional list of activity types to filter by

        Returns:
            List of ActivityLog objects
        """
        if workspace_id not in self.workspace_activities:
            return []

        activity_ids = self.workspace_activities[workspace_id]
        activities = []

        for activity_id in reversed(activity_ids):  # Newest first
            activity = self.get_activity(activity_id)
            if activity:
                if activity_types and activity.activity_type not in activity_types:
                    continue
                activities.append(activity)
                if limit and len(activities) >= limit:
                    break

        return activities

    def get_project_activities(
        self,
        project_id: str,
        limit: Optional[int] = None,
        activity_types: Optional[List[ActivityType]] = None,
    ) -> List[ActivityLog]:
        """
        Get activities for a project.

        Args:
            project_id: ID of the project
            limit: Optional maximum number of activities to return
            activity_types: Optional list of activity types to filter by

        Returns:
            List of ActivityLog objects
        """
        if project_id not in self.project_activities:
            return []

        activity_ids = self.project_activities[project_id]
        activities = []

        for activity_id in reversed(activity_ids):  # Newest first
            activity = self.get_activity(activity_id)
            if activity:
                if activity_types and activity.activity_type not in activity_types:
                    continue
                activities.append(activity)
                if limit and len(activities) >= limit:
                    break

        return activities

    def get_user_activities(
        self,
        user_id: str,
        limit: Optional[int] = None,
        activity_types: Optional[List[ActivityType]] = None,
    ) -> List[ActivityLog]:
        """
        Get activities for a user.

        Args:
            user_id: ID of the user
            limit: Optional maximum number of activities to return
            activity_types: Optional list of activity types to filter by

        Returns:
            List of ActivityLog objects
        """
        if user_id not in self.user_activities:
            return []

        activity_ids = self.user_activities[user_id]
        activities = []

        for activity_id in reversed(activity_ids):  # Newest first
            activity = self.get_activity(activity_id)
            if activity:
                if activity_types and activity.activity_type not in activity_types:
                    continue
                activities.append(activity)
                if limit and len(activities) >= limit:
                    break

        return activities

    def search_activities(
        self,
        query: str,
        limit: Optional[int] = None,
        activity_types: Optional[List[ActivityType]] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[ActivityLog]:
        """
        Search for activities.

        Args:
            query: Search query
            limit: Optional maximum number of activities to return
            activity_types: Optional list of activity types to filter by
            user_id: Optional user ID to filter by
            workspace_id: Optional workspace ID to filter by
            project_id: Optional project ID to filter by

        Returns:
            List of ActivityLog objects
        """
        activities = []
        query = query.lower()

        for activity_data in reversed(list(self.activities.values())):  # Newest first
            activity = ActivityLog.from_dict(activity_data)

            # Apply filters
            if activity_types and activity.activity_type not in activity_types:
                continue

            if user_id and activity.user_id != user_id:
                continue

            if workspace_id and activity.workspace_id != workspace_id:
                continue

            if project_id and activity.project_id != project_id:
                continue

            # Check if query matches
            if query in (activity.description or "").lower() or any(
                query in str(value).lower() for value in activity.metadata.values()
            ):
                activities.append(activity)
                if limit and len(activities) >= limit:
                    break

        return activities


class NotificationManager:
    """
    Manages notifications for users.

    This class provides functionality for creating, sending, and managing
    notifications about important events and activities.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the notification manager.

        Args:
            storage_path: Path where notification data will be stored
        """
        self.storage_path = storage_path or "notifications"
        os.makedirs(self.storage_path, exist_ok=True)

        self.notifications: Dict[str, Dict[str, Any]] = {}
        self.user_notifications: Dict[str, List[str]] = {}

        self._load_notification_data()

    def _load_notification_data(self):
        """Load notification data from disk."""
        notifications_file = os.path.join(self.storage_path, "notifications.json")
        user_notifications_file = os.path.join(self.storage_path, 
            "user_notifications.json")

        if os.path.exists(notifications_file):
            try:
                with open(notifications_file, "r") as f:
                    self.notifications = json.load(f)
                logger.info(f"Loaded {len(self.notifications)} notifications")
            except Exception as e:
                logger.error(f"Failed to load notifications: {e}")
                self.notifications = {}

        if os.path.exists(user_notifications_file):
            try:
                with open(user_notifications_file, "r") as f:
                    self.user_notifications = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load user notifications: {e}")
                self.user_notifications = {}

    def _save_notification_data(self):
        """Save notification data to disk."""
        notifications_file = os.path.join(self.storage_path, "notifications.json")
        user_notifications_file = os.path.join(self.storage_path, 
            "user_notifications.json")

        with open(notifications_file, "w") as f:
            json.dump(self.notifications, f, indent=2)

        with open(user_notifications_file, "w") as f:
            json.dump(self.user_notifications, f, indent=2)

    def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        activity_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        link: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a notification for a user.

        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            activity_id: Optional ID of the related activity
            workspace_id: Optional ID of the related workspace
            project_id: Optional ID of the related project
            resource_id: Optional ID of the related resource
            link: Optional link to include in the notification
            metadata: Optional metadata for the notification

        Returns:
            Notification information
        """
        notification_id = str(uuid.uuid4())

        notification = {
            "notification_id": notification_id,
            "user_id": user_id,
            "title": title,
            "message": message,
            "activity_id": activity_id,
            "workspace_id": workspace_id,
            "project_id": project_id,
            "resource_id": resource_id,
            "link": link,
            "created_at": datetime.now().isoformat(),
            "read": False,
            "metadata": metadata or {},
        }

        self.notifications[notification_id] = notification

        if user_id not in self.user_notifications:
            self.user_notifications[user_id] = []
        self.user_notifications[user_id].append(notification_id)

        self._save_notification_data()

        logger.info(f"Created notification for user {user_id}: {title}")
        return notification

    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: ID of the notification

        Returns:
            True if the notification was marked as read, False otherwise
        """
        if notification_id not in self.notifications:
            logger.error(f"Notification {notification_id} not found")
            return False

        self.notifications[notification_id]["read"] = True
        self.notifications[notification_id]["read_at"] = datetime.now().isoformat()

        self._save_notification_data()

        logger.info(f"Marked notification {notification_id} as read")
        return True

    def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all notifications for a user as read.

        Args:
            user_id: ID of the user

        Returns:
            Number of notifications marked as read
        """
        if user_id not in self.user_notifications:
            return 0

        count = 0
        for notification_id in self.user_notifications[user_id]:
            if (
                notification_id in self.notifications
                and not self.notifications[notification_id]["read"]
            ):
                self.notifications[notification_id]["read"] = True
                self.notifications[notification_id]["read_at"] = \
                    datetime.now().isoformat()
                count += 1

        self._save_notification_data()

        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification.

        Args:
            notification_id: ID of the notification

        Returns:
            True if the notification was deleted, False otherwise
        """
        if notification_id not in self.notifications:
            logger.error(f"Notification {notification_id} not found")
            return False

        user_id = self.notifications[notification_id]["user_id"]

        del self.notifications[notification_id]

        if (
            user_id in self.user_notifications
            and notification_id in self.user_notifications[user_id]
        ):
            self.user_notifications[user_id].remove(notification_id)

        self._save_notification_data()

        logger.info(f"Deleted notification {notification_id}")
        return True

    def get_user_notifications(
        self, user_id: str, limit: Optional[int] = None, unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.

        Args:
            user_id: ID of the user
            limit: Optional maximum number of notifications to return
            unread_only: If True, only return unread notifications

        Returns:
            List of notification information
        """
        if user_id not in self.user_notifications:
            return []

        notification_ids = self.user_notifications[user_id]
        notifications = []

        for notification_id in reversed(notification_ids):  # Newest first
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                if unread_only and notification["read"]:
                    continue
                notifications.append(notification)
                if limit and len(notifications) >= limit:
                    break

        return notifications

    def get_unread_count(self, user_id: str) -> int:
        """
        Get the number of unread notifications for a user.

        Args:
            user_id: ID of the user

        Returns:
            Number of unread notifications
        """
        if user_id not in self.user_notifications:
            return 0

        count = 0
        for notification_id in self.user_notifications[user_id]:
            if (
                notification_id in self.notifications
                and not self.notifications[notification_id]["read"]
            ):
                count += 1

        return count

    def create_activity_notification(
        self,
        activity: ActivityLog,
        user_ids: List[str],
        title: Optional[str] = None,
        message: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create notifications for an activity.

        Args:
            activity: ActivityLog object
            user_ids: List of user IDs to notify
            title: Optional notification title (generated if not provided)
            message: Optional notification message (generated if not provided)

        Returns:
            List of created notification information
        """
        notifications = []

        # Generate title and message if not provided
        if not title or not message:
            title, message = self._generate_activity_notification(activity)

        for user_id in user_ids:
            # Don't notify the user who performed the activity
            if user_id == activity.user_id:
                continue

            notification = self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                activity_id=activity.activity_id,
                workspace_id=activity.workspace_id,
                project_id=activity.project_id,
                resource_id=activity.resource_id,
            )

            notifications.append(notification)

        return notifications

    def _generate_activity_notification(self, activity: ActivityLog) -> tuple[str, str]:
        """
        Generate a notification title and message for an activity.

        Args:
            activity: ActivityLog object

        Returns:
            Tuple of (title, message)
        """
        # Default values
        title = "New activity"
        message = "There is a new activity in your workspace."

        # Generate based on activity type
        if activity.activity_type == ActivityType.WORKSPACE_CREATED:
            title = "New workspace created"
            message = f"A new workspace has been created: {activity.metadata.get('workspace_name', 
                'Unnamed workspace')}"

        elif activity.activity_type == ActivityType.WORKSPACE_UPDATED:
            title = "Workspace updated"
            message = f"A workspace has been updated: {activity.metadata.get('workspace_name', 
                'Unnamed workspace')}"

        elif activity.activity_type == ActivityType.WORKSPACE_DELETED:
            title = "Workspace deleted"
            message = f"A workspace has been deleted: {activity.metadata.get('workspace_name', 
                'Unnamed workspace')}"

        elif activity.activity_type == ActivityType.MEMBER_ADDED:
            title = "New member added"
            message = f"A new member has been added to the workspace: {activity.metadata.get('member_name', 
                'Unknown member')}"

        elif activity.activity_type == ActivityType.MEMBER_REMOVED:
            title = "Member removed"
            message = f"A member has been removed from the workspace: {activity.metadata.get('member_name', 
                'Unknown member')}"

        elif activity.activity_type == ActivityType.MEMBER_ROLE_UPDATED:
            title = "Member role updated"
            message = f"A member's role has been updated: {activity.metadata.get('member_name', 
                'Unknown member')}"

        elif activity.activity_type == ActivityType.PROJECT_CREATED:
            title = "New project created"
            message = f"A new project has been created: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.PROJECT_UPDATED:
            title = "Project updated"
            message = f"A project has been updated: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.PROJECT_DELETED:
            title = "Project deleted"
            message = f"A project has been deleted: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.PROJECT_SHARED:
            title = "Project shared"
            message = f"A project has been shared: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.PROJECT_UNSHARED:
            title = "Project unshared"
            message = f"A project is no longer shared: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.VERSION_CREATED:
            title = "New version created"
            message = f"A new version has been created for project: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.VERSION_RESTORED:
            title = "Version restored"
            message = f"A version has been restored for project: {activity.metadata.get('project_name', 
                'Unnamed project')}"

        elif activity.activity_type == ActivityType.COMMENT_ADDED:
            title = "New comment"
            message = f"A new comment has been added to: {activity.metadata.get('resource_name', 
                'Unknown resource')}"

        elif activity.activity_type == ActivityType.COMMENT_UPDATED:
            title = "Comment updated"
            message = f"A comment has been updated on: {activity.metadata.get('resource_name', 
                'Unknown resource')}"

        elif activity.activity_type == ActivityType.COMMENT_DELETED:
            title = "Comment deleted"
            message = f"A comment has been deleted from: {activity.metadata.get('resource_name', 
                'Unknown resource')}"

        return title, message
