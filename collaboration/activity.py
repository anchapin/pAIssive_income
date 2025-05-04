"""
"""
Activity tracking and notification system for the collaboration module.
Activity tracking and notification system for the collaboration module.


This module provides classes for tracking user activity and sending notifications
This module provides classes for tracking user activity and sending notifications
to team members about important events and changes.
to team members about important events and changes.
"""
"""




import json
import json
import logging
import logging
import os
import os
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from enum import Enum
from enum import Enum
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class ActivityType(Enum):
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
    """
    Represents a log of user activity.
    Represents a log of user activity.


    This class stores information about an activity, such as who performed it,
    This class stores information about an activity, such as who performed it,
    when it occurred, and what resources were affected.
    when it occurred, and what resources were affected.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    activity_id: Optional[str] = None,
    activity_id: Optional[str] = None,
    activity_type: Optional[ActivityType] = None,
    activity_type: Optional[ActivityType] = None,
    user_id: Optional[str] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    project_id: Optional[str] = None,
    project_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    description: Optional[str] = None,
    description: Optional[str] = None,
    ):
    ):
    """
    """
    Initialize an activity log.
    Initialize an activity log.


    Args:
    Args:
    activity_id: Optional ID for the activity (generated if not provided)
    activity_id: Optional ID for the activity (generated if not provided)
    activity_type: Type of activity
    activity_type: Type of activity
    user_id: ID of the user who performed the activity
    user_id: ID of the user who performed the activity
    workspace_id: Optional ID of the workspace affected
    workspace_id: Optional ID of the workspace affected
    project_id: Optional ID of the project affected
    project_id: Optional ID of the project affected
    resource_id: Optional ID of the resource affected
    resource_id: Optional ID of the resource affected
    description: Optional description of the activity
    description: Optional description of the activity
    """
    """
    self.activity_id = activity_id or str(uuid.uuid4())
    self.activity_id = activity_id or str(uuid.uuid4())
    self.activity_type = activity_type
    self.activity_type = activity_type
    self.user_id = user_id
    self.user_id = user_id
    self.timestamp = datetime.now().isoformat()
    self.timestamp = datetime.now().isoformat()
    self.workspace_id = workspace_id
    self.workspace_id = workspace_id
    self.project_id = project_id
    self.project_id = project_id
    self.resource_id = resource_id
    self.resource_id = resource_id
    self.description = description
    self.description = description
    self.metadata: Dict[str, Any] = {}
    self.metadata: Dict[str, Any] = {}


    def add_metadata(self, key: str, value: Any):
    def add_metadata(self, key: str, value: Any):
    """
    """
    Add metadata to the activity log.
    Add metadata to the activity log.


    Args:
    Args:
    key: Metadata key
    key: Metadata key
    value: Metadata value
    value: Metadata value
    """
    """
    self.metadata[key] = value
    self.metadata[key] = value


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the activity log to a dictionary.
    Convert the activity log to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the activity log
    Dictionary representation of the activity log
    """
    """
    return {
    return {
    "activity_id": self.activity_id,
    "activity_id": self.activity_id,
    "activity_type": self.activity_type.value if self.activity_type else None,
    "activity_type": self.activity_type.value if self.activity_type else None,
    "user_id": self.user_id,
    "user_id": self.user_id,
    "timestamp": self.timestamp,
    "timestamp": self.timestamp,
    "workspace_id": self.workspace_id,
    "workspace_id": self.workspace_id,
    "project_id": self.project_id,
    "project_id": self.project_id,
    "resource_id": self.resource_id,
    "resource_id": self.resource_id,
    "description": self.description,
    "description": self.description,
    "metadata": self.metadata,
    "metadata": self.metadata,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityLog":
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityLog":
    """
    """
    Create an activity log from a dictionary.
    Create an activity log from a dictionary.


    Args:
    Args:
    data: Dictionary representation of an activity log
    data: Dictionary representation of an activity log


    Returns:
    Returns:
    ActivityLog object
    ActivityLog object
    """
    """
    activity_type = None
    activity_type = None
    if data.get("activity_type"):
    if data.get("activity_type"):
    try:
    try:
    activity_type = ActivityType(data["activity_type"])
    activity_type = ActivityType(data["activity_type"])
except ValueError:
except ValueError:
    logger.warning(f"Unknown activity type: {data['activity_type']}")
    logger.warning(f"Unknown activity type: {data['activity_type']}")


    activity = cls(
    activity = cls(
    activity_id=data["activity_id"],
    activity_id=data["activity_id"],
    activity_type=activity_type,
    activity_type=activity_type,
    user_id=data["user_id"],
    user_id=data["user_id"],
    workspace_id=data.get("workspace_id"),
    workspace_id=data.get("workspace_id"),
    project_id=data.get("project_id"),
    project_id=data.get("project_id"),
    resource_id=data.get("resource_id"),
    resource_id=data.get("resource_id"),
    description=data.get("description"),
    description=data.get("description"),
    )
    )


    activity.timestamp = data["timestamp"]
    activity.timestamp = data["timestamp"]
    activity.metadata = data.get("metadata", {})
    activity.metadata = data.get("metadata", {})


    return activity
    return activity




    class ActivityTracker:
    class ActivityTracker:
    """
    """
    Tracks user activity in workspaces and projects.
    Tracks user activity in workspaces and projects.


    This class provides functionality for logging and querying user activity,
    This class provides functionality for logging and querying user activity,
    which can be used for auditing, analytics, and notifications.
    which can be used for auditing, analytics, and notifications.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the activity tracker.
    Initialize the activity tracker.


    Args:
    Args:
    storage_path: Path where activity logs will be stored
    storage_path: Path where activity logs will be stored
    """
    """
    self.storage_path = storage_path or "activity_logs"
    self.storage_path = storage_path or "activity_logs"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    self.activities: Dict[str, Dict[str, Any]] = {}
    self.activities: Dict[str, Dict[str, Any]] = {}
    self.workspace_activities: Dict[str, List[str]] = {}
    self.workspace_activities: Dict[str, List[str]] = {}
    self.project_activities: Dict[str, List[str]] = {}
    self.project_activities: Dict[str, List[str]] = {}
    self.user_activities: Dict[str, List[str]] = {}
    self.user_activities: Dict[str, List[str]] = {}


    self._load_activity_data()
    self._load_activity_data()


    def _load_activity_data(self):
    def _load_activity_data(self):
    """Load activity data from disk."""
    activities_file = os.path.join(self.storage_path, "activities.json")
    workspace_activities_file = os.path.join(
    self.storage_path, "workspace_activities.json"
    )
    project_activities_file = os.path.join(
    self.storage_path, "project_activities.json"
    )
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
    workspace_activities_file = os.path.join(
    self.storage_path, "workspace_activities.json"
    )
    project_activities_file = os.path.join(
    self.storage_path, "project_activities.json"
    )
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
    """
    Log a user activity.
    Log a user activity.


    Args:
    Args:
    activity_type: Type of activity
    activity_type: Type of activity
    user_id: ID of the user who performed the activity
    user_id: ID of the user who performed the activity
    workspace_id: Optional ID of the workspace affected
    workspace_id: Optional ID of the workspace affected
    project_id: Optional ID of the project affected
    project_id: Optional ID of the project affected
    resource_id: Optional ID of the resource affected
    resource_id: Optional ID of the resource affected
    description: Optional description of the activity
    description: Optional description of the activity
    metadata: Optional metadata for the activity
    metadata: Optional metadata for the activity


    Returns:
    Returns:
    ActivityLog object
    ActivityLog object
    """
    """
    activity = ActivityLog(
    activity = ActivityLog(
    activity_type=activity_type,
    activity_type=activity_type,
    user_id=user_id,
    user_id=user_id,
    workspace_id=workspace_id,
    workspace_id=workspace_id,
    project_id=project_id,
    project_id=project_id,
    resource_id=resource_id,
    resource_id=resource_id,
    description=description,
    description=description,
    )
    )


    # Add metadata if provided
    # Add metadata if provided
    if metadata:
    if metadata:
    for key, value in metadata.items():
    for key, value in metadata.items():
    activity.add_metadata(key, value)
    activity.add_metadata(key, value)


    # Store activity
    # Store activity
    self.activities[activity.activity_id] = activity.to_dict()
    self.activities[activity.activity_id] = activity.to_dict()


    # Update workspace activities
    # Update workspace activities
    if workspace_id:
    if workspace_id:
    if workspace_id not in self.workspace_activities:
    if workspace_id not in self.workspace_activities:
    self.workspace_activities[workspace_id] = []
    self.workspace_activities[workspace_id] = []
    self.workspace_activities[workspace_id].append(activity.activity_id)
    self.workspace_activities[workspace_id].append(activity.activity_id)


    # Update project activities
    # Update project activities
    if project_id:
    if project_id:
    if project_id not in self.project_activities:
    if project_id not in self.project_activities:
    self.project_activities[project_id] = []
    self.project_activities[project_id] = []
    self.project_activities[project_id].append(activity.activity_id)
    self.project_activities[project_id].append(activity.activity_id)


    # Update user activities
    # Update user activities
    if user_id not in self.user_activities:
    if user_id not in self.user_activities:
    self.user_activities[user_id] = []
    self.user_activities[user_id] = []
    self.user_activities[user_id].append(activity.activity_id)
    self.user_activities[user_id].append(activity.activity_id)


    self._save_activity_data()
    self._save_activity_data()


    logger.info(f"Logged activity: {activity_type.value} by user {user_id}")
    logger.info(f"Logged activity: {activity_type.value} by user {user_id}")
    return activity
    return activity


    def get_activity(self, activity_id: str) -> Optional[ActivityLog]:
    def get_activity(self, activity_id: str) -> Optional[ActivityLog]:
    """
    """
    Get an activity log by ID.
    Get an activity log by ID.


    Args:
    Args:
    activity_id: ID of the activity
    activity_id: ID of the activity


    Returns:
    Returns:
    ActivityLog object or None if not found
    ActivityLog object or None if not found
    """
    """
    if activity_id not in self.activities:
    if activity_id not in self.activities:
    return None
    return None


    return ActivityLog.from_dict(self.activities[activity_id])
    return ActivityLog.from_dict(self.activities[activity_id])


    def get_workspace_activities(
    def get_workspace_activities(
    self,
    self,
    workspace_id: str,
    workspace_id: str,
    limit: Optional[int] = None,
    limit: Optional[int] = None,
    activity_types: Optional[List[ActivityType]] = None,
    activity_types: Optional[List[ActivityType]] = None,
    ) -> List[ActivityLog]:
    ) -> List[ActivityLog]:
    """
    """
    Get activities for a workspace.
    Get activities for a workspace.


    Args:
    Args:
    workspace_id: ID of the workspace
    workspace_id: ID of the workspace
    limit: Optional maximum number of activities to return
    limit: Optional maximum number of activities to return
    activity_types: Optional list of activity types to filter by
    activity_types: Optional list of activity types to filter by


    Returns:
    Returns:
    List of ActivityLog objects
    List of ActivityLog objects
    """
    """
    if workspace_id not in self.workspace_activities:
    if workspace_id not in self.workspace_activities:
    return []
    return []


    activity_ids = self.workspace_activities[workspace_id]
    activity_ids = self.workspace_activities[workspace_id]
    activities = []
    activities = []


    for activity_id in reversed(activity_ids):  # Newest first
    for activity_id in reversed(activity_ids):  # Newest first
    activity = self.get_activity(activity_id)
    activity = self.get_activity(activity_id)
    if activity:
    if activity:
    if activity_types and activity.activity_type not in activity_types:
    if activity_types and activity.activity_type not in activity_types:
    continue
    continue
    activities.append(activity)
    activities.append(activity)
    if limit and len(activities) >= limit:
    if limit and len(activities) >= limit:
    break
    break


    return activities
    return activities


    def get_project_activities(
    def get_project_activities(
    self,
    self,
    project_id: str,
    project_id: str,
    limit: Optional[int] = None,
    limit: Optional[int] = None,
    activity_types: Optional[List[ActivityType]] = None,
    activity_types: Optional[List[ActivityType]] = None,
    ) -> List[ActivityLog]:
    ) -> List[ActivityLog]:
    """
    """
    Get activities for a project.
    Get activities for a project.


    Args:
    Args:
    project_id: ID of the project
    project_id: ID of the project
    limit: Optional maximum number of activities to return
    limit: Optional maximum number of activities to return
    activity_types: Optional list of activity types to filter by
    activity_types: Optional list of activity types to filter by


    Returns:
    Returns:
    List of ActivityLog objects
    List of ActivityLog objects
    """
    """
    if project_id not in self.project_activities:
    if project_id not in self.project_activities:
    return []
    return []


    activity_ids = self.project_activities[project_id]
    activity_ids = self.project_activities[project_id]
    activities = []
    activities = []


    for activity_id in reversed(activity_ids):  # Newest first
    for activity_id in reversed(activity_ids):  # Newest first
    activity = self.get_activity(activity_id)
    activity = self.get_activity(activity_id)
    if activity:
    if activity:
    if activity_types and activity.activity_type not in activity_types:
    if activity_types and activity.activity_type not in activity_types:
    continue
    continue
    activities.append(activity)
    activities.append(activity)
    if limit and len(activities) >= limit:
    if limit and len(activities) >= limit:
    break
    break


    return activities
    return activities


    def get_user_activities(
    def get_user_activities(
    self,
    self,
    user_id: str,
    user_id: str,
    limit: Optional[int] = None,
    limit: Optional[int] = None,
    activity_types: Optional[List[ActivityType]] = None,
    activity_types: Optional[List[ActivityType]] = None,
    ) -> List[ActivityLog]:
    ) -> List[ActivityLog]:
    """
    """
    Get activities for a user.
    Get activities for a user.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user
    limit: Optional maximum number of activities to return
    limit: Optional maximum number of activities to return
    activity_types: Optional list of activity types to filter by
    activity_types: Optional list of activity types to filter by


    Returns:
    Returns:
    List of ActivityLog objects
    List of ActivityLog objects
    """
    """
    if user_id not in self.user_activities:
    if user_id not in self.user_activities:
    return []
    return []


    activity_ids = self.user_activities[user_id]
    activity_ids = self.user_activities[user_id]
    activities = []
    activities = []


    for activity_id in reversed(activity_ids):  # Newest first
    for activity_id in reversed(activity_ids):  # Newest first
    activity = self.get_activity(activity_id)
    activity = self.get_activity(activity_id)
    if activity:
    if activity:
    if activity_types and activity.activity_type not in activity_types:
    if activity_types and activity.activity_type not in activity_types:
    continue
    continue
    activities.append(activity)
    activities.append(activity)
    if limit and len(activities) >= limit:
    if limit and len(activities) >= limit:
    break
    break


    return activities
    return activities


    def search_activities(
    def search_activities(
    self,
    self,
    query: str,
    query: str,
    limit: Optional[int] = None,
    limit: Optional[int] = None,
    activity_types: Optional[List[ActivityType]] = None,
    activity_types: Optional[List[ActivityType]] = None,
    user_id: Optional[str] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    project_id: Optional[str] = None,
    project_id: Optional[str] = None,
    ) -> List[ActivityLog]:
    ) -> List[ActivityLog]:
    """
    """
    Search for activities.
    Search for activities.


    Args:
    Args:
    query: Search query
    query: Search query
    limit: Optional maximum number of activities to return
    limit: Optional maximum number of activities to return
    activity_types: Optional list of activity types to filter by
    activity_types: Optional list of activity types to filter by
    user_id: Optional user ID to filter by
    user_id: Optional user ID to filter by
    workspace_id: Optional workspace ID to filter by
    workspace_id: Optional workspace ID to filter by
    project_id: Optional project ID to filter by
    project_id: Optional project ID to filter by


    Returns:
    Returns:
    List of ActivityLog objects
    List of ActivityLog objects
    """
    """
    activities = []
    activities = []
    query = query.lower()
    query = query.lower()


    for activity_data in reversed(list(self.activities.values())):  # Newest first
    for activity_data in reversed(list(self.activities.values())):  # Newest first
    activity = ActivityLog.from_dict(activity_data)
    activity = ActivityLog.from_dict(activity_data)


    # Apply filters
    # Apply filters
    if activity_types and activity.activity_type not in activity_types:
    if activity_types and activity.activity_type not in activity_types:
    continue
    continue


    if user_id and activity.user_id != user_id:
    if user_id and activity.user_id != user_id:
    continue
    continue


    if workspace_id and activity.workspace_id != workspace_id:
    if workspace_id and activity.workspace_id != workspace_id:
    continue
    continue


    if project_id and activity.project_id != project_id:
    if project_id and activity.project_id != project_id:
    continue
    continue


    # Check if query matches
    # Check if query matches
    if query in (activity.description or "").lower() or any(
    if query in (activity.description or "").lower() or any(
    query in str(value).lower() for value in activity.metadata.values()
    query in str(value).lower() for value in activity.metadata.values()
    ):
    ):
    activities.append(activity)
    activities.append(activity)
    if limit and len(activities) >= limit:
    if limit and len(activities) >= limit:
    break
    break


    return activities
    return activities




    class NotificationManager:
    class NotificationManager:
    """
    """
    Manages notifications for users.
    Manages notifications for users.


    This class provides functionality for creating, sending, and managing
    This class provides functionality for creating, sending, and managing
    notifications about important events and activities.
    notifications about important events and activities.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the notification manager.
    Initialize the notification manager.


    Args:
    Args:
    storage_path: Path where notification data will be stored
    storage_path: Path where notification data will be stored
    """
    """
    self.storage_path = storage_path or "notifications"
    self.storage_path = storage_path or "notifications"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    self.notifications: Dict[str, Dict[str, Any]] = {}
    self.notifications: Dict[str, Dict[str, Any]] = {}
    self.user_notifications: Dict[str, List[str]] = {}
    self.user_notifications: Dict[str, List[str]] = {}


    self._load_notification_data()
    self._load_notification_data()


    def _load_notification_data(self):
    def _load_notification_data(self):
    """Load notification data from disk."""
    notifications_file = os.path.join(self.storage_path, "notifications.json")
    user_notifications_file = os.path.join(
    self.storage_path, "user_notifications.json"
    )

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
    user_notifications_file = os.path.join(
    self.storage_path, "user_notifications.json"
    )

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
    """
    Create a notification for a user.
    Create a notification for a user.


    Args:
    Args:
    user_id: ID of the user to notify
    user_id: ID of the user to notify
    title: Notification title
    title: Notification title
    message: Notification message
    message: Notification message
    activity_id: Optional ID of the related activity
    activity_id: Optional ID of the related activity
    workspace_id: Optional ID of the related workspace
    workspace_id: Optional ID of the related workspace
    project_id: Optional ID of the related project
    project_id: Optional ID of the related project
    resource_id: Optional ID of the related resource
    resource_id: Optional ID of the related resource
    link: Optional link to include in the notification
    link: Optional link to include in the notification
    metadata: Optional metadata for the notification
    metadata: Optional metadata for the notification


    Returns:
    Returns:
    Notification information
    Notification information
    """
    """
    notification_id = str(uuid.uuid4())
    notification_id = str(uuid.uuid4())


    notification = {
    notification = {
    "notification_id": notification_id,
    "notification_id": notification_id,
    "user_id": user_id,
    "user_id": user_id,
    "title": title,
    "title": title,
    "message": message,
    "message": message,
    "activity_id": activity_id,
    "activity_id": activity_id,
    "workspace_id": workspace_id,
    "workspace_id": workspace_id,
    "project_id": project_id,
    "project_id": project_id,
    "resource_id": resource_id,
    "resource_id": resource_id,
    "link": link,
    "link": link,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "read": False,
    "read": False,
    "metadata": metadata or {},
    "metadata": metadata or {},
    }
    }


    self.notifications[notification_id] = notification
    self.notifications[notification_id] = notification


    if user_id not in self.user_notifications:
    if user_id not in self.user_notifications:
    self.user_notifications[user_id] = []
    self.user_notifications[user_id] = []
    self.user_notifications[user_id].append(notification_id)
    self.user_notifications[user_id].append(notification_id)


    self._save_notification_data()
    self._save_notification_data()


    logger.info(f"Created notification for user {user_id}: {title}")
    logger.info(f"Created notification for user {user_id}: {title}")
    return notification
    return notification


    def mark_as_read(self, notification_id: str) -> bool:
    def mark_as_read(self, notification_id: str) -> bool:
    """
    """
    Mark a notification as read.
    Mark a notification as read.


    Args:
    Args:
    notification_id: ID of the notification
    notification_id: ID of the notification


    Returns:
    Returns:
    True if the notification was marked as read, False otherwise
    True if the notification was marked as read, False otherwise
    """
    """
    if notification_id not in self.notifications:
    if notification_id not in self.notifications:
    logger.error(f"Notification {notification_id} not found")
    logger.error(f"Notification {notification_id} not found")
    return False
    return False


    self.notifications[notification_id]["read"] = True
    self.notifications[notification_id]["read"] = True
    self.notifications[notification_id]["read_at"] = datetime.now().isoformat()
    self.notifications[notification_id]["read_at"] = datetime.now().isoformat()


    self._save_notification_data()
    self._save_notification_data()


    logger.info(f"Marked notification {notification_id} as read")
    logger.info(f"Marked notification {notification_id} as read")
    return True
    return True


    def mark_all_as_read(self, user_id: str) -> int:
    def mark_all_as_read(self, user_id: str) -> int:
    """
    """
    Mark all notifications for a user as read.
    Mark all notifications for a user as read.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    Number of notifications marked as read
    Number of notifications marked as read
    """
    """
    if user_id not in self.user_notifications:
    if user_id not in self.user_notifications:
    return 0
    return 0


    count = 0
    count = 0
    for notification_id in self.user_notifications[user_id]:
    for notification_id in self.user_notifications[user_id]:
    if (
    if (
    notification_id in self.notifications
    notification_id in self.notifications
    and not self.notifications[notification_id]["read"]
    and not self.notifications[notification_id]["read"]
    ):
    ):
    self.notifications[notification_id]["read"] = True
    self.notifications[notification_id]["read"] = True
    self.notifications[notification_id][
    self.notifications[notification_id][
    "read_at"
    "read_at"
    ] = datetime.now().isoformat()
    ] = datetime.now().isoformat()
    count += 1
    count += 1


    self._save_notification_data()
    self._save_notification_data()


    logger.info(f"Marked {count} notifications as read for user {user_id}")
    logger.info(f"Marked {count} notifications as read for user {user_id}")
    return count
    return count


    def delete_notification(self, notification_id: str) -> bool:
    def delete_notification(self, notification_id: str) -> bool:
    """
    """
    Delete a notification.
    Delete a notification.


    Args:
    Args:
    notification_id: ID of the notification
    notification_id: ID of the notification


    Returns:
    Returns:
    True if the notification was deleted, False otherwise
    True if the notification was deleted, False otherwise
    """
    """
    if notification_id not in self.notifications:
    if notification_id not in self.notifications:
    logger.error(f"Notification {notification_id} not found")
    logger.error(f"Notification {notification_id} not found")
    return False
    return False


    user_id = self.notifications[notification_id]["user_id"]
    user_id = self.notifications[notification_id]["user_id"]


    del self.notifications[notification_id]
    del self.notifications[notification_id]


    if (
    if (
    user_id in self.user_notifications
    user_id in self.user_notifications
    and notification_id in self.user_notifications[user_id]
    and notification_id in self.user_notifications[user_id]
    ):
    ):
    self.user_notifications[user_id].remove(notification_id)
    self.user_notifications[user_id].remove(notification_id)


    self._save_notification_data()
    self._save_notification_data()


    logger.info(f"Deleted notification {notification_id}")
    logger.info(f"Deleted notification {notification_id}")
    return True
    return True


    def get_user_notifications(
    def get_user_notifications(
    self, user_id: str, limit: Optional[int] = None, unread_only: bool = False
    self, user_id: str, limit: Optional[int] = None, unread_only: bool = False
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get notifications for a user.
    Get notifications for a user.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user
    limit: Optional maximum number of notifications to return
    limit: Optional maximum number of notifications to return
    unread_only: If True, only return unread notifications
    unread_only: If True, only return unread notifications


    Returns:
    Returns:
    List of notification information
    List of notification information
    """
    """
    if user_id not in self.user_notifications:
    if user_id not in self.user_notifications:
    return []
    return []


    notification_ids = self.user_notifications[user_id]
    notification_ids = self.user_notifications[user_id]
    notifications = []
    notifications = []


    for notification_id in reversed(notification_ids):  # Newest first
    for notification_id in reversed(notification_ids):  # Newest first
    if notification_id in self.notifications:
    if notification_id in self.notifications:
    notification = self.notifications[notification_id]
    notification = self.notifications[notification_id]
    if unread_only and notification["read"]:
    if unread_only and notification["read"]:
    continue
    continue
    notifications.append(notification)
    notifications.append(notification)
    if limit and len(notifications) >= limit:
    if limit and len(notifications) >= limit:
    break
    break


    return notifications
    return notifications


    def get_unread_count(self, user_id: str) -> int:
    def get_unread_count(self, user_id: str) -> int:
    """
    """
    Get the number of unread notifications for a user.
    Get the number of unread notifications for a user.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    Number of unread notifications
    Number of unread notifications
    """
    """
    if user_id not in self.user_notifications:
    if user_id not in self.user_notifications:
    return 0
    return 0


    count = 0
    count = 0
    for notification_id in self.user_notifications[user_id]:
    for notification_id in self.user_notifications[user_id]:
    if (
    if (
    notification_id in self.notifications
    notification_id in self.notifications
    and not self.notifications[notification_id]["read"]
    and not self.notifications[notification_id]["read"]
    ):
    ):
    count += 1
    count += 1


    return count
    return count


    def create_activity_notification(
    def create_activity_notification(
    self,
    self,
    activity: ActivityLog,
    activity: ActivityLog,
    user_ids: List[str],
    user_ids: List[str],
    title: Optional[str] = None,
    title: Optional[str] = None,
    message: Optional[str] = None,
    message: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Create notifications for an activity.
    Create notifications for an activity.


    Args:
    Args:
    activity: ActivityLog object
    activity: ActivityLog object
    user_ids: List of user IDs to notify
    user_ids: List of user IDs to notify
    title: Optional notification title (generated if not provided)
    title: Optional notification title (generated if not provided)
    message: Optional notification message (generated if not provided)
    message: Optional notification message (generated if not provided)


    Returns:
    Returns:
    List of created notification information
    List of created notification information
    """
    """
    notifications = []
    notifications = []


    # Generate title and message if not provided
    # Generate title and message if not provided
    if not title or not message:
    if not title or not message:
    title, message = self._generate_activity_notification(activity)
    title, message = self._generate_activity_notification(activity)


    for user_id in user_ids:
    for user_id in user_ids:
    # Don't notify the user who performed the activity
    # Don't notify the user who performed the activity
    if user_id == activity.user_id:
    if user_id == activity.user_id:
    continue
    continue


    notification = self.create_notification(
    notification = self.create_notification(
    user_id=user_id,
    user_id=user_id,
    title=title,
    title=title,
    message=message,
    message=message,
    activity_id=activity.activity_id,
    activity_id=activity.activity_id,
    workspace_id=activity.workspace_id,
    workspace_id=activity.workspace_id,
    project_id=activity.project_id,
    project_id=activity.project_id,
    resource_id=activity.resource_id,
    resource_id=activity.resource_id,
    )
    )


    notifications.append(notification)
    notifications.append(notification)


    return notifications
    return notifications


    def _generate_activity_notification(self, activity: ActivityLog) -> tuple[str, str]:
    def _generate_activity_notification(self, activity: ActivityLog) -> tuple[str, str]:
    """
    """
    Generate a notification title and message for an activity.
    Generate a notification title and message for an activity.


    Args:
    Args:
    activity: ActivityLog object
    activity: ActivityLog object


    Returns:
    Returns:
    Tuple of (title, message)
    Tuple of (title, message)
    """
    """
    # Default values
    # Default values
    title = "New activity"
    title = "New activity"
    message = "There is a new activity in your workspace."
    message = "There is a new activity in your workspace."


    # Generate based on activity type
    # Generate based on activity type
    if activity.activity_type == ActivityType.WORKSPACE_CREATED:
    if activity.activity_type == ActivityType.WORKSPACE_CREATED:
    title = "New workspace created"
    title = "New workspace created"
    message = f"A new workspace has been created: {activity.metadata.get('workspace_name', 'Unnamed workspace')}"
    message = f"A new workspace has been created: {activity.metadata.get('workspace_name', 'Unnamed workspace')}"


    elif activity.activity_type == ActivityType.WORKSPACE_UPDATED:
    elif activity.activity_type == ActivityType.WORKSPACE_UPDATED:
    title = "Workspace updated"
    title = "Workspace updated"
    message = f"A workspace has been updated: {activity.metadata.get('workspace_name', 'Unnamed workspace')}"
    message = f"A workspace has been updated: {activity.metadata.get('workspace_name', 'Unnamed workspace')}"


    elif activity.activity_type == ActivityType.WORKSPACE_DELETED:
    elif activity.activity_type == ActivityType.WORKSPACE_DELETED:
    title = "Workspace deleted"
    title = "Workspace deleted"
    message = f"A workspace has been deleted: {activity.metadata.get('workspace_name', 'Unnamed workspace')}"
    message = f"A workspace has been deleted: {activity.metadata.get('workspace_name', 'Unnamed workspace')}"


    elif activity.activity_type == ActivityType.MEMBER_ADDED:
    elif activity.activity_type == ActivityType.MEMBER_ADDED:
    title = "New member added"
    title = "New member added"
    message = f"A new member has been added to the workspace: {activity.metadata.get('member_name', 'Unknown member')}"
    message = f"A new member has been added to the workspace: {activity.metadata.get('member_name', 'Unknown member')}"


    elif activity.activity_type == ActivityType.MEMBER_REMOVED:
    elif activity.activity_type == ActivityType.MEMBER_REMOVED:
    title = "Member removed"
    title = "Member removed"
    message = f"A member has been removed from the workspace: {activity.metadata.get('member_name', 'Unknown member')}"
    message = f"A member has been removed from the workspace: {activity.metadata.get('member_name', 'Unknown member')}"


    elif activity.activity_type == ActivityType.MEMBER_ROLE_UPDATED:
    elif activity.activity_type == ActivityType.MEMBER_ROLE_UPDATED:
    title = "Member role updated"
    title = "Member role updated"
    message = f"A member's role has been updated: {activity.metadata.get('member_name', 'Unknown member')}"
    message = f"A member's role has been updated: {activity.metadata.get('member_name', 'Unknown member')}"


    elif activity.activity_type == ActivityType.PROJECT_CREATED:
    elif activity.activity_type == ActivityType.PROJECT_CREATED:
    title = "New project created"
    title = "New project created"
    message = f"A new project has been created: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A new project has been created: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.PROJECT_UPDATED:
    elif activity.activity_type == ActivityType.PROJECT_UPDATED:
    title = "Project updated"
    title = "Project updated"
    message = f"A project has been updated: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A project has been updated: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.PROJECT_DELETED:
    elif activity.activity_type == ActivityType.PROJECT_DELETED:
    title = "Project deleted"
    title = "Project deleted"
    message = f"A project has been deleted: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A project has been deleted: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.PROJECT_SHARED:
    elif activity.activity_type == ActivityType.PROJECT_SHARED:
    title = "Project shared"
    title = "Project shared"
    message = f"A project has been shared: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A project has been shared: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.PROJECT_UNSHARED:
    elif activity.activity_type == ActivityType.PROJECT_UNSHARED:
    title = "Project unshared"
    title = "Project unshared"
    message = f"A project is no longer shared: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A project is no longer shared: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.VERSION_CREATED:
    elif activity.activity_type == ActivityType.VERSION_CREATED:
    title = "New version created"
    title = "New version created"
    message = f"A new version has been created for project: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A new version has been created for project: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.VERSION_RESTORED:
    elif activity.activity_type == ActivityType.VERSION_RESTORED:
    title = "Version restored"
    title = "Version restored"
    message = f"A version has been restored for project: {activity.metadata.get('project_name', 'Unnamed project')}"
    message = f"A version has been restored for project: {activity.metadata.get('project_name', 'Unnamed project')}"


    elif activity.activity_type == ActivityType.COMMENT_ADDED:
    elif activity.activity_type == ActivityType.COMMENT_ADDED:
    title = "New comment"
    title = "New comment"
    message = f"A new comment has been added to: {activity.metadata.get('resource_name', 'Unknown resource')}"
    message = f"A new comment has been added to: {activity.metadata.get('resource_name', 'Unknown resource')}"


    elif activity.activity_type == ActivityType.COMMENT_UPDATED:
    elif activity.activity_type == ActivityType.COMMENT_UPDATED:
    title = "Comment updated"
    title = "Comment updated"
    message = f"A comment has been updated on: {activity.metadata.get('resource_name', 'Unknown resource')}"
    message = f"A comment has been updated on: {activity.metadata.get('resource_name', 'Unknown resource')}"


    elif activity.activity_type == ActivityType.COMMENT_DELETED:
    elif activity.activity_type == ActivityType.COMMENT_DELETED:
    title = "Comment deleted"
    title = "Comment deleted"
    message = f"A comment has been deleted from: {activity.metadata.get('resource_name', 'Unknown resource')}"
    message = f"A comment has been deleted from: {activity.metadata.get('resource_name', 'Unknown resource')}"


    return title, message
    return title, message