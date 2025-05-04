"""
"""
Social media integration module for the pAIssive Income project.
Social media integration module for the pAIssive Income project.


This module provides functionality for integrating with various social media platforms
This module provides functionality for integrating with various social media platforms
for content posting, analytics tracking, and audience insights.
for content posting, analytics tracking, and audience insights.
"""
"""


import importlib
import importlib
import json
import json
import logging
import logging
import os
import os
import time
import time
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from interfaces.marketing_interfaces import ISocialMediaIntegration
from interfaces.marketing_interfaces import ISocialMediaIntegration


# Local imports
# Local imports
(
(
AuthenticationError,
AuthenticationError,
ContentValidationError,
ContentValidationError,
DeletionError,
DeletionError,
NotSupportedError,
NotSupportedError,
PlatformNotFoundError,
PlatformNotFoundError,
PlatformNotSupportedError,
PlatformNotSupportedError,
PostingError,
PostingError,
PostNotFoundError,
PostNotFoundError,
SchedulingError,
SchedulingError,
)
)
from marketing.schemas import PostScheduleType, SocialMediaPlatform
from marketing.schemas import PostScheduleType, SocialMediaPlatform


# Configure logging
# Configure logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Define constants
# Define constants
SUPPORTED_PLATFORMS = {
SUPPORTED_PLATFORMS = {
SocialMediaPlatform.TWITTER: {
SocialMediaPlatform.TWITTER: {
"name": "Twitter",
"name": "Twitter",
"capabilities": [
"capabilities": [
"post_text",
"post_text",
"post_media",
"post_media",
"analytics",
"analytics",
"audience_insights",
"audience_insights",
"scheduling",
"scheduling",
],
],
"adapter_module": "marketing.social_media_adapters.twitter_adapter",
"adapter_module": "marketing.social_media_adapters.twitter_adapter",
},
},
SocialMediaPlatform.FACEBOOK: {
SocialMediaPlatform.FACEBOOK: {
"name": "Facebook",
"name": "Facebook",
"capabilities": [
"capabilities": [
"post_text",
"post_text",
"post_media",
"post_media",
"post_link",
"post_link",
"analytics",
"analytics",
"audience_insights",
"audience_insights",
"scheduling",
"scheduling",
],
],
"adapter_module": "marketing.social_media_adapters.facebook_adapter",
"adapter_module": "marketing.social_media_adapters.facebook_adapter",
},
},
SocialMediaPlatform.INSTAGRAM: {
SocialMediaPlatform.INSTAGRAM: {
"name": "Instagram",
"name": "Instagram",
"capabilities": ["post_media", "post_story", "analytics", "audience_insights"],
"capabilities": ["post_media", "post_story", "analytics", "audience_insights"],
"adapter_module": "marketing.social_media_adapters.instagram_adapter",
"adapter_module": "marketing.social_media_adapters.instagram_adapter",
},
},
SocialMediaPlatform.LINKEDIN: {
SocialMediaPlatform.LINKEDIN: {
"name": "LinkedIn",
"name": "LinkedIn",
"capabilities": [
"capabilities": [
"post_text",
"post_text",
"post_media",
"post_media",
"post_article",
"post_article",
"analytics",
"analytics",
"audience_insights",
"audience_insights",
"scheduling",
"scheduling",
],
],
"adapter_module": "marketing.social_media_adapters.linkedin_adapter",
"adapter_module": "marketing.social_media_adapters.linkedin_adapter",
},
},
SocialMediaPlatform.YOUTUBE: {
SocialMediaPlatform.YOUTUBE: {
"name": "YouTube",
"name": "YouTube",
"capabilities": ["post_video", "analytics", "audience_insights", "scheduling"],
"capabilities": ["post_video", "analytics", "audience_insights", "scheduling"],
"adapter_module": "marketing.social_media_adapters.youtube_adapter",
"adapter_module": "marketing.social_media_adapters.youtube_adapter",
},
},
SocialMediaPlatform.PINTEREST: {
SocialMediaPlatform.PINTEREST: {
"name": "Pinterest",
"name": "Pinterest",
"capabilities": ["post_pin", "analytics", "audience_insights", "scheduling"],
"capabilities": ["post_pin", "analytics", "audience_insights", "scheduling"],
"adapter_module": "marketing.social_media_adapters.pinterest_adapter",
"adapter_module": "marketing.social_media_adapters.pinterest_adapter",
},
},
SocialMediaPlatform.TIKTOK: {
SocialMediaPlatform.TIKTOK: {
"name": "TikTok",
"name": "TikTok",
"capabilities": ["post_video", "analytics", "audience_insights"],
"capabilities": ["post_video", "analytics", "audience_insights"],
"adapter_module": "marketing.social_media_adapters.tiktok_adapter",
"adapter_module": "marketing.social_media_adapters.tiktok_adapter",
},
},
}
}




class SocialMediaIntegration(ISocialMediaIntegration):
    class SocialMediaIntegration(ISocialMediaIntegration):
    """
    """
    Class for integrating with social media platforms.
    Class for integrating with social media platforms.


    This class provides functionality to:
    This class provides functionality to:
    1. Connect to various social media platforms
    1. Connect to various social media platforms
    2. Post content to connected platforms
    2. Post content to connected platforms
    3. Retrieve analytics data from platforms
    3. Retrieve analytics data from platforms
    4. Schedule content for posting
    4. Schedule content for posting
    5. Retrieve audience insights
    5. Retrieve audience insights
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the social media integration.
    Initialize the social media integration.


    Args:
    Args:
    storage_path: Optional path to store connection data. If None, data will be stored
    storage_path: Optional path to store connection data. If None, data will be stored
    in memory only.
    in memory only.
    """
    """
    self.connections = {}
    self.connections = {}
    self.platform_adapters = {}
    self.platform_adapters = {}
    self.posts = {}
    self.posts = {}
    self.campaigns = {}
    self.campaigns = {}
    self.storage_path = storage_path
    self.storage_path = storage_path


    # Create storage directory if it doesn't exist
    # Create storage directory if it doesn't exist
    if storage_path and not os.path.exists(storage_path):
    if storage_path and not os.path.exists(storage_path):
    os.makedirs(storage_path)
    os.makedirs(storage_path)


    # Load existing data if available
    # Load existing data if available
    if storage_path:
    if storage_path:
    self._load_connections()
    self._load_connections()
    self._load_posts()
    self._load_posts()
    self._load_campaigns()
    self._load_campaigns()


    def _load_connections(self):
    def _load_connections(self):
    """Load connection data from storage."""
    connections_path = os.path.join(self.storage_path, "connections.json")
    try:
    if os.path.exists(connections_path):
    with open(connections_path, "r", encoding="utf-8") as file:
    connections_data = json.load(file)
    self.connections = connections_data
    # Initialize adapters for loaded connections
    for connection_id, connection in self.connections.items():
    self._init_platform_adapter(
    connection["platform"], connection_id
    )

except Exception as e:
    logger.error(f"Error loading social media connections: {e}")

    def _load_posts(self):
    """Load posts data from storage."""
    posts_path = os.path.join(self.storage_path, "posts.json")
    try:
    if os.path.exists(posts_path):
    with open(posts_path, "r", encoding="utf-8") as file:
    posts_data = json.load(file)
    self.posts = posts_data
except Exception as e:
    logger.error(f"Error loading social media posts: {e}")

    def _load_campaigns(self):
    """Load campaigns data from storage."""
    campaigns_path = os.path.join(self.storage_path, "campaigns.json")
    try:
    if os.path.exists(campaigns_path):
    with open(campaigns_path, "r", encoding="utf-8") as file:
    campaigns_data = json.load(file)
    self.campaigns = campaigns_data
except Exception as e:
    logger.error(f"Error loading social media campaigns: {e}")

    def _save_connections(self):
    """Save connection data to storage."""
    if not self.storage_path:
    return connections_path = os.path.join(self.storage_path, "connections.json")
    try:
    with open(connections_path, "w", encoding="utf-8") as file:
    json.dump(self.connections, file, indent=2)
except Exception as e:
    logger.error(f"Error saving social media connections: {e}")

    def _save_posts(self):
    """Save posts data to storage."""
    if not self.storage_path:
    return posts_path = os.path.join(self.storage_path, "posts.json")
    try:
    with open(posts_path, "w", encoding="utf-8") as file:
    json.dump(self.posts, file, indent=2)
except Exception as e:
    logger.error(f"Error saving social media posts: {e}")

    def _save_campaigns(self):
    """Save campaigns data to storage."""
    if not self.storage_path:
    return campaigns_path = os.path.join(self.storage_path, "campaigns.json")
    try:
    with open(campaigns_path, "w", encoding="utf-8") as file:
    json.dump(self.campaigns, file, indent=2)
except Exception as e:
    logger.error(f"Error saving social media campaigns: {e}")

    def _init_platform_adapter(self, platform: str, connection_id: str):
    """
    """
    Initialize a platform adapter for a connection.
    Initialize a platform adapter for a connection.


    Args:
    Args:
    platform: Social media platform name
    platform: Social media platform name
    connection_id: Connection ID
    connection_id: Connection ID


    Returns:
    Returns:
    Platform adapter instance
    Platform adapter instance


    Raises:
    Raises:
    PlatformNotSupportedError: If the platform is not supported
    PlatformNotSupportedError: If the platform is not supported
    ImportError: If the adapter module cannot be imported
    ImportError: If the adapter module cannot be imported
    """
    """
    if platform not in SUPPORTED_PLATFORMS:
    if platform not in SUPPORTED_PLATFORMS:
    raise PlatformNotSupportedError(platform)
    raise PlatformNotSupportedError(platform)


    adapter_module_path = SUPPORTED_PLATFORMS[platform]["adapter_module"]
    adapter_module_path = SUPPORTED_PLATFORMS[platform]["adapter_module"]


    try:
    try:
    # Check if adapter is already loaded
    # Check if adapter is already loaded
    if connection_id not in self.platform_adapters:
    if connection_id not in self.platform_adapters:
    # Use importlib to dynamically import the adapter
    # Use importlib to dynamically import the adapter
    module_name = adapter_module_path
    module_name = adapter_module_path
    adapter_module = importlib.import_module(module_name)
    adapter_module = importlib.import_module(module_name)


    # Get the adapter class (should be the first class in the module)
    # Get the adapter class (should be the first class in the module)
    adapter_class = None
    adapter_class = None
    for attr_name in dir(adapter_module):
    for attr_name in dir(adapter_module):
    attr = getattr(adapter_module, attr_name)
    attr = getattr(adapter_module, attr_name)
    if (
    if (
    isinstance(attr, type)
    isinstance(attr, type)
    and attr.__module__ == adapter_module.__name__
    and attr.__module__ == adapter_module.__name__
    ):
    ):
    adapter_class = attr
    adapter_class = attr
    break
    break


    if not adapter_class:
    if not adapter_class:
    raise ImportError(
    raise ImportError(
    f"Could not find adapter class in {adapter_module_path}"
    f"Could not find adapter class in {adapter_module_path}"
    )
    )


    # Create instance of adapter
    # Create instance of adapter
    connection_data = self.connections[connection_id]
    connection_data = self.connections[connection_id]
    adapter = adapter_class(
    adapter = adapter_class(
    connection_id=connection_id, connection_data=connection_data
    connection_id=connection_id, connection_data=connection_data
    )
    )


    # Store adapter
    # Store adapter
    self.platform_adapters[connection_id] = adapter
    self.platform_adapters[connection_id] = adapter


    return self.platform_adapters[connection_id]
    return self.platform_adapters[connection_id]


except ImportError as e:
except ImportError as e:
    logger.error(f"Could not import adapter module for {platform}: {e}")
    logger.error(f"Could not import adapter module for {platform}: {e}")
    if platform not in SUPPORTED_PLATFORMS:
    if platform not in SUPPORTED_PLATFORMS:
    raise PlatformNotSupportedError(platform)
    raise PlatformNotSupportedError(platform)
    else:
    else:
    # Still raise but with the original exception
    # Still raise but with the original exception
    raise
    raise


    def _generate_platform_id(self, platform: str) -> str:
    def _generate_platform_id(self, platform: str) -> str:
    """
    """
    Generate a unique platform connection ID.
    Generate a unique platform connection ID.


    Args:
    Args:
    platform: Social media platform name
    platform: Social media platform name


    Returns:
    Returns:
    Unique platform connection ID
    Unique platform connection ID
    """
    """
    return f"{platform}_{uuid.uuid4().hex[:8]}"
    return f"{platform}_{uuid.uuid4().hex[:8]}"


    def connect_platform(
    def connect_platform(
    self,
    self,
    platform: str,
    platform: str,
    credentials: Dict[str, Any],
    credentials: Dict[str, Any],
    settings: Optional[Dict[str, Any]] = None,
    settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Connect to a social media platform with provided credentials.
    Connect to a social media platform with provided credentials.


    Args:
    Args:
    platform: Social media platform name (e.g., "twitter", "facebook", "linkedin")
    platform: Social media platform name (e.g., "twitter", "facebook", "linkedin")
    credentials: Platform-specific authentication credentials
    credentials: Platform-specific authentication credentials
    settings: Optional platform-specific settings
    settings: Optional platform-specific settings


    Returns:
    Returns:
    Dictionary containing the connection details
    Dictionary containing the connection details


    Raises:
    Raises:
    PlatformNotSupportedError: If the platform is not supported
    PlatformNotSupportedError: If the platform is not supported
    AuthenticationError: If authentication fails
    AuthenticationError: If authentication fails
    """
    """
    # Check if the platform is supported
    # Check if the platform is supported
    if platform not in SUPPORTED_PLATFORMS:
    if platform not in SUPPORTED_PLATFORMS:
    raise PlatformNotSupportedError(platform)
    raise PlatformNotSupportedError(platform)


    # Generate a unique connection ID
    # Generate a unique connection ID
    connection_id = self._generate_platform_id(platform)
    connection_id = self._generate_platform_id(platform)


    # Create connection object
    # Create connection object
    connection = {
    connection = {
    "id": connection_id,
    "id": connection_id,
    "platform": platform,
    "platform": platform,
    "account_name": credentials.get("account_name", "Unknown"),
    "account_name": credentials.get("account_name", "Unknown"),
    "account_id": credentials.get("account_id", "Unknown"),
    "account_id": credentials.get("account_id", "Unknown"),
    "profile_url": credentials.get("profile_url"),
    "profile_url": credentials.get("profile_url"),
    "connected_at": datetime.now().isoformat(),
    "connected_at": datetime.now().isoformat(),
    "last_synced_at": None,
    "last_synced_at": None,
    "status": "active",
    "status": "active",
    "settings": settings or {},
    "settings": settings or {},
    "capabilities": SUPPORTED_PLATFORMS[platform]["capabilities"],
    "capabilities": SUPPORTED_PLATFORMS[platform]["capabilities"],
    "credentials": credentials,
    "credentials": credentials,
    }
    }


    # Store the connection
    # Store the connection
    self.connections[connection_id] = connection
    self.connections[connection_id] = connection


    # Initialize the platform adapter
    # Initialize the platform adapter
    adapter = self._init_platform_adapter(platform, connection_id)
    adapter = self._init_platform_adapter(platform, connection_id)


    # Verify credentials with the adapter
    # Verify credentials with the adapter
    try:
    try:
    verified_connection = adapter.verify_credentials()
    verified_connection = adapter.verify_credentials()


    # Update connection with verified data
    # Update connection with verified data
    self.connections[connection_id].update(
    self.connections[connection_id].update(
    {
    {
    "account_name": verified_connection.get(
    "account_name": verified_connection.get(
    "account_name", connection["account_name"]
    "account_name", connection["account_name"]
    ),
    ),
    "account_id": verified_connection.get(
    "account_id": verified_connection.get(
    "account_id", connection["account_id"]
    "account_id", connection["account_id"]
    ),
    ),
    "profile_url": verified_connection.get(
    "profile_url": verified_connection.get(
    "profile_url", connection["profile_url"]
    "profile_url", connection["profile_url"]
    ),
    ),
    "verified": True,
    "verified": True,
    }
    }
    )
    )


    # Save connections
    # Save connections
    self._save_connections()
    self._save_connections()


    # Return the connection without credentials for security
    # Return the connection without credentials for security
    connection_copy = self.connections[connection_id].copy()
    connection_copy = self.connections[connection_id].copy()
    connection_copy.pop("credentials", None)
    connection_copy.pop("credentials", None)
    return connection_copy
    return connection_copy


except Exception as e:
except Exception as e:
    # Remove the connection on failure
    # Remove the connection on failure
    self.connections.pop(connection_id, None)
    self.connections.pop(connection_id, None)
    if hasattr(e, "platform") and hasattr(e, "message"):
    if hasattr(e, "platform") and hasattr(e, "message"):
    raise e
    raise e
    else:
    else:
    raise AuthenticationError(platform, str(e))
    raise AuthenticationError(platform, str(e))


    def disconnect_platform(self, platform_id: str) -> bool:
    def disconnect_platform(self, platform_id: str) -> bool:
    """
    """
    Disconnect from a connected social media platform.
    Disconnect from a connected social media platform.


    Args:
    Args:
    platform_id: ID of the connected platform
    platform_id: ID of the connected platform


    Returns:
    Returns:
    True if disconnected successfully, False otherwise
    True if disconnected successfully, False otherwise


    Raises:
    Raises:
    PlatformNotFoundError: If the platform ID is not found
    PlatformNotFoundError: If the platform ID is not found
    """
    """
    # Check if the platform connection exists
    # Check if the platform connection exists
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    try:
    try:
    # If adapter exists, call its disconnect method
    # If adapter exists, call its disconnect method
    if platform_id in self.platform_adapters:
    if platform_id in self.platform_adapters:
    adapter = self.platform_adapters[platform_id]
    adapter = self.platform_adapters[platform_id]
    adapter.disconnect()
    adapter.disconnect()
    del self.platform_adapters[platform_id]
    del self.platform_adapters[platform_id]


    # Remove the connection
    # Remove the connection
    del self.connections[platform_id]
    del self.connections[platform_id]


    # Save connections
    # Save connections
    self._save_connections()
    self._save_connections()


    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Error disconnecting from platform {platform_id}: {e}")
    logger.error(f"Error disconnecting from platform {platform_id}: {e}")
    return False
    return False


    def get_connected_platforms(self) -> List[Dict[str, Any]]:
    def get_connected_platforms(self) -> List[Dict[str, Any]]:
    """
    """
    Get a list of connected social media platforms.
    Get a list of connected social media platforms.


    Returns:
    Returns:
    List of dictionaries containing connected platform details
    List of dictionaries containing connected platform details
    """
    """
    # Return all connections without credentials
    # Return all connections without credentials
    return [
    return [
    {k: v for k, v in connection.items() if k != "credentials"}
    {k: v for k, v in connection.items() if k != "credentials"}
    for connection in self.connections.values()
    for connection in self.connections.values()
    ]
    ]


    def post_content(
    def post_content(
    self,
    self,
    platform_id: str,
    platform_id: str,
    content: Dict[str, Any],
    content: Dict[str, Any],
    schedule_time: Optional[datetime] = None,
    schedule_time: Optional[datetime] = None,
    visibility: str = "public",
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post content to a connected social media platform.
    Post content to a connected social media platform.


    Args:
    Args:
    platform_id: ID of the connected platform
    platform_id: ID of the connected platform
    content: Content to post (text, media, etc.)
    content: Content to post (text, media, etc.)
    schedule_time: Optional time to schedule the post for
    schedule_time: Optional time to schedule the post for
    visibility: Visibility setting (public, private, etc.)
    visibility: Visibility setting (public, private, etc.)
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


    Returns:
    Returns:
    Dictionary containing the post details and ID
    Dictionary containing the post details and ID


    Raises:
    Raises:
    PlatformNotFoundError: If the platform ID is not found
    PlatformNotFoundError: If the platform ID is not found
    ContentValidationError: If the content is invalid
    ContentValidationError: If the content is invalid
    PostingError: If posting fails
    PostingError: If posting fails
    """
    """
    # Check if the platform connection exists
    # Check if the platform connection exists
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    # Get the platform adapter
    # Get the platform adapter
    adapter = self._init_platform_adapter(
    adapter = self._init_platform_adapter(
    self.connections[platform_id]["platform"], platform_id
    self.connections[platform_id]["platform"], platform_id
    )
    )


    # Prepare the post content
    # Prepare the post content
    post_data = {
    post_data = {
    "platform_id": platform_id,
    "platform_id": platform_id,
    "content": content,
    "content": content,
    "schedule_time": schedule_time.isoformat() if schedule_time else None,
    "schedule_time": schedule_time.isoformat() if schedule_time else None,
    "schedule_type": (
    "schedule_type": (
    PostScheduleType.SCHEDULED if schedule_time else PostScheduleType.NOW
    PostScheduleType.SCHEDULED if schedule_time else PostScheduleType.NOW
    ),
    ),
    "visibility": visibility,
    "visibility": visibility,
    "targeting": targeting,
    "targeting": targeting,
    "status": "scheduled" if schedule_time else "pending",
    "status": "scheduled" if schedule_time else "pending",
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    try:
    try:
    # Validate the content
    # Validate the content
    adapter.validate_content(content)
    adapter.validate_content(content)


    # If scheduled for the future
    # If scheduled for the future
    if schedule_time and schedule_time > datetime.now():
    if schedule_time and schedule_time > datetime.now():
    # Generate local post ID
    # Generate local post ID
    post_id = f"post_{uuid.uuid4().hex}"
    post_id = f"post_{uuid.uuid4().hex}"
    post_data["id"] = post_id
    post_data["id"] = post_id


    # Store the scheduled post
    # Store the scheduled post
    if platform_id not in self.posts:
    if platform_id not in self.posts:
    self.posts[platform_id] = {}
    self.posts[platform_id] = {}


    self.posts[platform_id][post_id] = post_data
    self.posts[platform_id][post_id] = post_data
    self._save_posts()
    self._save_posts()


    return {
    return {
    "id": post_id,
    "id": post_id,
    "platform_id": platform_id,
    "platform_id": platform_id,
    "status": "scheduled",
    "status": "scheduled",
    "schedule_time": post_data["schedule_time"],
    "schedule_time": post_data["schedule_time"],
    "created_at": post_data["created_at"],
    "created_at": post_data["created_at"],
    }
    }
    else:
    else:
    # Post immediately
    # Post immediately
    result = adapter.post_content(content, visibility, targeting)
    result = adapter.post_content(content, visibility, targeting)


    # Store the post with the platform-assigned ID
    # Store the post with the platform-assigned ID
    post_id = result["id"]
    post_id = result["id"]
    post_data["id"] = post_id
    post_data["id"] = post_id
    post_data["status"] = "posted"
    post_data["status"] = "posted"
    post_data["posted_at"] = datetime.now().isoformat()
    post_data["posted_at"] = datetime.now().isoformat()
    post_data["platform_data"] = result.get("platform_data", {})
    post_data["platform_data"] = result.get("platform_data", {})


    if platform_id not in self.posts:
    if platform_id not in self.posts:
    self.posts[platform_id] = {}
    self.posts[platform_id] = {}


    self.posts[platform_id][post_id] = post_data
    self.posts[platform_id][post_id] = post_data
    self._save_posts()
    self._save_posts()


    return {
    return {
    "id": post_id,
    "id": post_id,
    "platform_id": platform_id,
    "platform_id": platform_id,
    "status": "posted",
    "status": "posted",
    "posted_at": post_data["posted_at"],
    "posted_at": post_data["posted_at"],
    "created_at": post_data["created_at"],
    "created_at": post_data["created_at"],
    "platform_data": result.get("platform_data", {}),
    "platform_data": result.get("platform_data", {}),
    }
    }


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except Exception as e:
except Exception as e:
    raise PostingError(self.connections[platform_id]["platform"], str(e))
    raise PostingError(self.connections[platform_id]["platform"], str(e))


    def get_post(self, platform_id: str, post_id: str) -> Dict[str, Any]:
    def get_post(self, platform_id: str, post_id: str) -> Dict[str, Any]:
    """
    """
    Get details of a specific post.
    Get details of a specific post.


    Args:
    Args:
    platform_id: ID of the connected platform
    platform_id: ID of the connected platform
    post_id: ID of the post to retrieve
    post_id: ID of the post to retrieve


    Returns:
    Returns:
    Dictionary containing the post details
    Dictionary containing the post details


    Raises:
    Raises:
    PlatformNotFoundError: If the platform ID is not found
    PlatformNotFoundError: If the platform ID is not found
    PostNotFoundError: If the post ID is not found
    PostNotFoundError: If the post ID is not found
    """
    """
    # Check if the platform connection exists
    # Check if the platform connection exists
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    # Check if we have the post locally
    # Check if we have the post locally
    if platform_id in self.posts and post_id in self.posts[platform_id]:
    if platform_id in self.posts and post_id in self.posts[platform_id]:
    post_data = self.posts[platform_id][post_id]
    post_data = self.posts[platform_id][post_id]


    # If post was already posted, try to get latest data from platform
    # If post was already posted, try to get latest data from platform
    if post_data["status"] == "posted":
    if post_data["status"] == "posted":
    try:
    try:
    adapter = self._init_platform_adapter(
    adapter = self._init_platform_adapter(
    self.connections[platform_id]["platform"], platform_id
    self.connections[platform_id]["platform"], platform_id
    )
    )


    # Get updated post data from the platform
    # Get updated post data from the platform
    updated_post = adapter.get_post(post_id)
    updated_post = adapter.get_post(post_id)
    post_data["platform_data"] = updated_post
    post_data["platform_data"] = updated_post
    self._save_posts()
    self._save_posts()
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Could not get updated post data for {post_id}: {e}"
    f"Could not get updated post data for {post_id}: {e}"
    )
    )


    return post_data
    return post_data


    # If not found locally, try to get from platform
    # If not found locally, try to get from platform
    try:
    try:
    adapter = self._init_platform_adapter(
    adapter = self._init_platform_adapter(
    self.connections[platform_id]["platform"], platform_id
    self.connections[platform_id]["platform"], platform_id
    )
    )


    post_data = adapter.get_post(post_id)
    post_data = adapter.get_post(post_id)


    # Store the post
    # Store the post
    if platform_id not in self.posts:
    if platform_id not in self.posts:
    self.posts[platform_id] = {}
    self.posts[platform_id] = {}


    self.posts[platform_id][post_id] = {
    self.posts[platform_id][post_id] = {
    "id": post_id,
    "id": post_id,
    "platform_id": platform_id,
    "platform_id": platform_id,
    "status": "posted",
    "status": "posted",
    "platform_data": post_data,
    "platform_data": post_data,
    "created_at": post_data.get("created_time", datetime.now().isoformat()),
    "created_at": post_data.get("created_time", datetime.now().isoformat()),
    }
    }


    self._save_posts()
    self._save_posts()
    return self.posts[platform_id][post_id]
    return self.posts[platform_id][post_id]


except Exception:
except Exception:
    raise PostNotFoundError(platform_id, post_id)
    raise PostNotFoundError(platform_id, post_id)


    def delete_post(self, platform_id: str, post_id: str) -> bool:
    def delete_post(self, platform_id: str, post_id: str) -> bool:
    """
    """
    Delete a post from a connected social media platform.
    Delete a post from a connected social media platform.


    Args:
    Args:
    platform_id: ID of the connected platform
    platform_id: ID of the connected platform
    post_id: ID of the post to delete
    post_id: ID of the post to delete


    Returns:
    Returns:
    True if deleted successfully, False otherwise
    True if deleted successfully, False otherwise


    Raises:
    Raises:
    PlatformNotFoundError: If the platform ID is not found
    PlatformNotFoundError: If the platform ID is not found
    PostNotFoundError: If the post ID is not found
    PostNotFoundError: If the post ID is not found
    DeletionError: If deletion fails
    DeletionError: If deletion fails
    """
    """
    # Check if the platform connection exists
    # Check if the platform connection exists
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    # Check if we have the post locally
    # Check if we have the post locally
    post_exists_locally = (
    post_exists_locally = (
    platform_id in self.posts and post_id in self.posts[platform_id]
    platform_id in self.posts and post_id in self.posts[platform_id]
    )
    )


    # If it's a scheduled post that hasn't been posted yet
    # If it's a scheduled post that hasn't been posted yet
    if (
    if (
    post_exists_locally
    post_exists_locally
    and self.posts[platform_id][post_id]["status"] == "scheduled"
    and self.posts[platform_id][post_id]["status"] == "scheduled"
    ):
    ):
    # Just remove it from our storage
    # Just remove it from our storage
    del self.posts[platform_id][post_id]
    del self.posts[platform_id][post_id]
    self._save_posts()
    self._save_posts()
    return True
    return True


    # Otherwise, we need to delete from the platform
    # Otherwise, we need to delete from the platform
    try:
    try:
    adapter = self._init_platform_adapter(
    adapter = self._init_platform_adapter(
    self.connections[platform_id]["platform"], platform_id
    self.connections[platform_id]["platform"], platform_id
    )
    )


    result = adapter.delete_post(post_id)
    result = adapter.delete_post(post_id)


    # If successfully deleted from platform, remove from local storage
    # If successfully deleted from platform, remove from local storage
    if post_exists_locally:
    if post_exists_locally:
    del self.posts[platform_id][post_id]
    del self.posts[platform_id][post_id]
    self._save_posts()
    self._save_posts()


    return result
    return result


except Exception as e:
except Exception as e:
    raise DeletionError(
    raise DeletionError(
    self.connections[platform_id]["platform"], post_id, str(e)
    self.connections[platform_id]["platform"], post_id, str(e)
    )
    )


    def get_analytics(
    def get_analytics(
    self,
    self,
    platform_id: str,
    platform_id: str,
    post_id: Optional[str] = None,
    post_id: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    granularity: str = "day",
    granularity: str = "day",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get analytics for posts on a connected social media platform.
    Get analytics for posts on a connected social media platform.


    Args:
    Args:
    platform_id: ID of the connected platform
    platform_id: ID of the connected platform
    post_id: Optional ID of a specific post to get analytics for
    post_id: Optional ID of a specific post to get analytics for
    metrics: Optional list of specific metrics to retrieve
    metrics: Optional list of specific metrics to retrieve
    start_date: Optional start date for analytics data
    start_date: Optional start date for analytics data
    end_date: Optional end date for analytics data
    end_date: Optional end date for analytics data
    granularity: Time granularity for data (day, week, month)
    granularity: Time granularity for data (day, week, month)


    Returns:
    Returns:
    Dictionary containing analytics data
    Dictionary containing analytics data


    Raises:
    Raises:
    PlatformNotFoundError: If the platform ID is not found
    PlatformNotFoundError: If the platform ID is not found
    PostNotFoundError: If the post ID is not found
    PostNotFoundError: If the post ID is not found
    InvalidParameterError: If parameters are invalid
    InvalidParameterError: If parameters are invalid
    """
    """
    # Check if the platform connection exists
    # Check if the platform connection exists
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    # Set default date range if not provided
    # Set default date range if not provided
    if not end_date:
    if not end_date:
    end_date = datetime.now()
    end_date = datetime.now()


    if not start_date:
    if not start_date:
    start_date = end_date - timedelta(days=30)
    start_date = end_date - timedelta(days=30)


    # Check if analytics is supported
    # Check if analytics is supported
    platform = self.connections[platform_id]["platform"]
    platform = self.connections[platform_id]["platform"]
    capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]
    capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]


    if "analytics" not in capabilities:
    if "analytics" not in capabilities:
    raise NotSupportedError(platform, "analytics")
    raise NotSupportedError(platform, "analytics")


    # Get the platform adapter
    # Get the platform adapter
    adapter = self._init_platform_adapter(platform, platform_id)
    adapter = self._init_platform_adapter(platform, platform_id)


    try:
    try:
    # Get analytics data from the platform
    # Get analytics data from the platform
    analytics_data = adapter.get_analytics(
    analytics_data = adapter.get_analytics(
    post_id=post_id,
    post_id=post_id,
    metrics=metrics,
    metrics=metrics,
    start_date=start_date,
    start_date=start_date,
    end_date=end_date,
    end_date=end_date,
    granularity=granularity,
    granularity=granularity,
    )
    )


    # Format the results
    # Format the results
    result = {
    result = {
    "platform_id": platform_id,
    "platform_id": platform_id,
    "post_id": post_id,
    "post_id": post_id,
    "time_period": {
    "time_period": {
    "start": start_date.isoformat(),
    "start": start_date.isoformat(),
    "end": end_date.isoformat(),
    "end": end_date.isoformat(),
    },
    },
    "granularity": granularity,
    "granularity": granularity,
    "metrics": analytics_data.get("metrics", {}),
    "metrics": analytics_data.get("metrics", {}),
    "aggregates": analytics_data.get("aggregates", {}),
    "aggregates": analytics_data.get("aggregates", {}),
    "insights": analytics_data.get("insights", []),
    "insights": analytics_data.get("insights", []),
    }
    }


    return result
    return result


except PostNotFoundError:
except PostNotFoundError:
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"Error getting analytics from {platform}: {e}")
    logger.error(f"Error getting analytics from {platform}: {e}")
    return {
    return {
    "platform_id": platform_id,
    "platform_id": platform_id,
    "post_id": post_id,
    "post_id": post_id,
    "time_period": {
    "time_period": {
    "start": start_date.isoformat(),
    "start": start_date.isoformat(),
    "end": end_date.isoformat(),
    "end": end_date.isoformat(),
    },
    },
    "granularity": granularity,
    "granularity": granularity,
    "metrics": {},
    "metrics": {},
    "aggregates": {},
    "aggregates": {},
    "insights": [],
    "insights": [],
    "error": str(e),
    "error": str(e),
    }
    }


    def schedule_campaign(
    def schedule_campaign(
    self,
    self,
    platform_ids: List[str],
    platform_ids: List[str],
    campaign_name: str,
    campaign_name: str,
    content_items: List[Dict[str, Any]],
    content_items: List[Dict[str, Any]],
    schedule_settings: Dict[str, Any],
    schedule_settings: Dict[str, Any],
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Schedule a social media campaign with multiple content items.
    Schedule a social media campaign with multiple content items.


    Args:
    Args:
    platform_ids: List of connected platform IDs
    platform_ids: List of connected platform IDs
    campaign_name: Name of the campaign
    campaign_name: Name of the campaign
    content_items: List of content items to post
    content_items: List of content items to post
    schedule_settings: Settings for content scheduling
    schedule_settings: Settings for content scheduling
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


    Returns:
    Returns:
    Dictionary containing the campaign details and scheduled post IDs
    Dictionary containing the campaign details and scheduled post IDs


    Raises:
    Raises:
    PlatformNotFoundError: If a platform ID is not found
    PlatformNotFoundError: If a platform ID is not found
    ContentValidationError: If content validation fails
    ContentValidationError: If content validation fails
    SchedulingError: If scheduling fails
    SchedulingError: If scheduling fails
    """
    """
    # Check if all platform IDs exist
    # Check if all platform IDs exist
    for platform_id in platform_ids:
    for platform_id in platform_ids:
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    # Check if scheduling is supported for all platforms
    # Check if scheduling is supported for all platforms
    for platform_id in platform_ids:
    for platform_id in platform_ids:
    platform = self.connections[platform_id]["platform"]
    platform = self.connections[platform_id]["platform"]
    capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]
    capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]


    if "scheduling" not in capabilities:
    if "scheduling" not in capabilities:
    raise NotSupportedError(platform, "scheduling")
    raise NotSupportedError(platform, "scheduling")


    # Validate all content items
    # Validate all content items
    for platform_id in platform_ids:
    for platform_id in platform_ids:
    adapter = self._init_platform_adapter(
    adapter = self._init_platform_adapter(
    self.connections[platform_id]["platform"], platform_id
    self.connections[platform_id]["platform"], platform_id
    )
    )


    # Validate each content item for this platform
    # Validate each content item for this platform
    for content_item in content_items:
    for content_item in content_items:
    try:
    try:
    adapter.validate_content(content_item)
    adapter.validate_content(content_item)
except ContentValidationError as e:
except ContentValidationError as e:
    raise ContentValidationError(
    raise ContentValidationError(
    self.connections[platform_id]["platform"],
    self.connections[platform_id]["platform"],
    f"Invalid content for item: {str(e)}",
    f"Invalid content for item: {str(e)}",
    )
    )


    # Generate a campaign ID
    # Generate a campaign ID
    campaign_id = f"campaign_{uuid.uuid4().hex}"
    campaign_id = f"campaign_{uuid.uuid4().hex}"


    # Handle schedule settings
    # Handle schedule settings
    start_date = datetime.fromisoformat(schedule_settings.get("start_date"))
    start_date = datetime.fromisoformat(schedule_settings.get("start_date"))
    end_date = None
    end_date = None
    if "end_date" in schedule_settings:
    if "end_date" in schedule_settings:
    end_date = datetime.fromisoformat(schedule_settings["end_date"])
    end_date = datetime.fromisoformat(schedule_settings["end_date"])


    schedule_type = schedule_settings.get("type", "spread")
    schedule_type = schedule_settings.get("type", "spread")


    # Calculate post times based on schedule settings
    # Calculate post times based on schedule settings
    scheduled_posts = {}
    scheduled_posts = {}


    if schedule_type == "spread":
    if schedule_type == "spread":
    # Distribute posts evenly between start and end date
    # Distribute posts evenly between start and end date
    if not end_date:
    if not end_date:
    end_date = start_date + timedelta(days=30)  # Default to 30 days
    end_date = start_date + timedelta(days=30)  # Default to 30 days


    total_duration = (end_date - start_date).total_seconds()
    total_duration = (end_date - start_date).total_seconds()
    interval = total_duration / (len(content_items) + 1)
    interval = total_duration / (len(content_items) + 1)


    for i, content_item in enumerate(content_items):
    for i, content_item in enumerate(content_items):
    post_time = start_date + timedelta(seconds=(i + 1) * interval)
    post_time = start_date + timedelta(seconds=(i + 1) * interval)


    for platform_id in platform_ids:
    for platform_id in platform_ids:
    try:
    try:
    post_result = self.post_content(
    post_result = self.post_content(
    platform_id=platform_id,
    platform_id=platform_id,
    content=content_item,
    content=content_item,
    schedule_time=post_time,
    schedule_time=post_time,
    visibility=content_item.get("visibility", "public"),
    visibility=content_item.get("visibility", "public"),
    targeting=targeting,
    targeting=targeting,
    )
    )


    if platform_id not in scheduled_posts:
    if platform_id not in scheduled_posts:
    scheduled_posts[platform_id] = []
    scheduled_posts[platform_id] = []


    scheduled_posts[platform_id].append(post_result["id"])
    scheduled_posts[platform_id].append(post_result["id"])


except Exception as e:
except Exception as e:
    logger.error(f"Error scheduling post to {platform_id}: {e}")
    logger.error(f"Error scheduling post to {platform_id}: {e}")
    raise SchedulingError(
    raise SchedulingError(
    f"Error scheduling to {platform_id}: {str(e)}"
    f"Error scheduling to {platform_id}: {str(e)}"
    )
    )


    elif schedule_type == "best_time":
    elif schedule_type == "best_time":
    # Schedule at optimal times (would need platform-specific logic)
    # Schedule at optimal times (would need platform-specific logic)
    raise NotImplementedError("Best time scheduling not yet implemented")
    raise NotImplementedError("Best time scheduling not yet implemented")


    else:
    else:
    # Custom schedule or other types
    # Custom schedule or other types
    raise SchedulingError(f"Unsupported schedule type: {schedule_type}")
    raise SchedulingError(f"Unsupported schedule type: {schedule_type}")


    # Create campaign object
    # Create campaign object
    campaign = {
    campaign = {
    "id": campaign_id,
    "id": campaign_id,
    "name": campaign_name,
    "name": campaign_name,
    "platform_ids": platform_ids,
    "platform_ids": platform_ids,
    "content_items": content_items,
    "content_items": content_items,
    "schedule_settings": schedule_settings,
    "schedule_settings": schedule_settings,
    "targeting": targeting,
    "targeting": targeting,
    "start_date": start_date.isoformat(),
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat() if end_date else None,
    "end_date": end_date.isoformat() if end_date else None,
    "status": "scheduled",
    "status": "scheduled",
    "scheduled_posts": scheduled_posts,
    "scheduled_posts": scheduled_posts,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store the campaign
    # Store the campaign
    self.campaigns[campaign_id] = campaign
    self.campaigns[campaign_id] = campaign
    self._save_campaigns()
    self._save_campaigns()


    return campaign
    return campaign


    def get_audience_insights(
    def get_audience_insights(
    self,
    self,
    platform_id: str,
    platform_id: str,
    metrics: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    segment: Optional[Dict[str, Any]] = None,
    segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get audience insights from a connected social media platform.
    Get audience insights from a connected social media platform.


    Args:
    Args:
    platform_id: ID of the connected platform
    platform_id: ID of the connected platform
    metrics: Optional list of specific metrics to retrieve
    metrics: Optional list of specific metrics to retrieve
    segment: Optional audience segment parameters
    segment: Optional audience segment parameters


    Returns:
    Returns:
    Dictionary containing audience insights data
    Dictionary containing audience insights data


    Raises:
    Raises:
    PlatformNotFoundError: If the platform ID is not found
    PlatformNotFoundError: If the platform ID is not found
    InvalidParameterError: If parameters are invalid
    InvalidParameterError: If parameters are invalid
    NotSupportedError: If the platform doesn't support audience insights
    NotSupportedError: If the platform doesn't support audience insights
    """
    """
    # Check if the platform connection exists
    # Check if the platform connection exists
    if platform_id not in self.connections:
    if platform_id not in self.connections:
    raise PlatformNotFoundError(platform_id)
    raise PlatformNotFoundError(platform_id)


    # Check if audience insights is supported
    # Check if audience insights is supported
    platform = self.connections[platform_id]["platform"]
    platform = self.connections[platform_id]["platform"]
    capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]
    capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]


    if "audience_insights" not in capabilities:
    if "audience_insights" not in capabilities:
    raise NotSupportedError(platform, "audience_insights")
    raise NotSupportedError(platform, "audience_insights")


    # Get the platform adapter
    # Get the platform adapter
    adapter = self._init_platform_adapter(platform, platform_id)
    adapter = self._init_platform_adapter(platform, platform_id)


    try:
    try:
    # Get audience insights from the platform
    # Get audience insights from the platform
    insights = adapter.get_audience_insights(metrics, segment)
    insights = adapter.get_audience_insights(metrics, segment)


    # Format the results
    # Format the results
    result = {
    result = {
    "platform_id": platform_id,
    "platform_id": platform_id,
    "segment": segment,
    "segment": segment,
    "demographics": insights.get("demographics"),
    "demographics": insights.get("demographics"),
    "interests": insights.get("interests"),
    "interests": insights.get("interests"),
    "behaviors": insights.get("behaviors"),
    "behaviors": insights.get("behaviors"),
    "engagement_metrics": insights.get("engagement_metrics"),
    "engagement_metrics": insights.get("engagement_metrics"),
    "active_times": insights.get("active_times"),
    "active_times": insights.get("active_times"),
    "insights": insights.get("insights", []),
    "insights": insights.get("insights", []),
    }
    }


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error getting audience insights from {platform}: {e}")
    logger.error(f"Error getting audience insights from {platform}: {e}")
    return {"platform_id": platform_id, "segment": segment, "error": str(e)}
    return {"platform_id": platform_id, "segment": segment, "error": str(e)}


    # Additional methods that could be implemented:
    # Additional methods that could be implemented:
    # - get_campaigns() - Get list of campaigns
    # - get_campaigns() - Get list of campaigns
    # - get_campaign(campaign_id) - Get campaign details
    # - get_campaign(campaign_id) - Get campaign details
    # - update_campaign(campaign_id, ...) - Update campaign
    # - update_campaign(campaign_id, ...) - Update campaign
    # - delete_campaign(campaign_id) - Delete campaign
    # - delete_campaign(campaign_id) - Delete campaign