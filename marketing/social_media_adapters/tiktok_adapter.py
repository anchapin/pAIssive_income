"""
"""
TikTok adapter for social media integration.
TikTok adapter for social media integration.


This module provides an adapter for connecting to the TikTok API for posting videos,
This module provides an adapter for connecting to the TikTok API for posting videos,
retrieving analytics, and managing TikTok campaigns.
retrieving analytics, and managing TikTok campaigns.
"""
"""


import logging
import logging
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


import requests
import requests


from marketing.social_media_adapters.base_adapter import BaseSocialMediaAdapter
from marketing.social_media_adapters.base_adapter import BaseSocialMediaAdapter


(
(
AuthenticationError,
AuthenticationError,
ContentValidationError,
ContentValidationError,
DeletionError,
DeletionError,
PostingError,
PostingError,
PostNotFoundError,
PostNotFoundError,
SchedulingError,
SchedulingError,
)
)
# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class TikTokAdapter(BaseSocialMediaAdapter):
    class TikTokAdapter(BaseSocialMediaAdapter):
    """
    """
    Adapter for TikTok platform integration.
    Adapter for TikTok platform integration.


    This class implements the BaseSocialMediaAdapter interface for TikTok,
    This class implements the BaseSocialMediaAdapter interface for TikTok,
    providing methods for posting videos, retrieving analytics, and managing
    providing methods for posting videos, retrieving analytics, and managing
    TikTok campaigns.
    TikTok campaigns.
    """
    """


    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    """
    """
    Initialize the TikTok adapter.
    Initialize the TikTok adapter.


    Args:
    Args:
    connection_id: Unique identifier for the connection
    connection_id: Unique identifier for the connection
    connection_data: Connection data including credentials and settings
    connection_data: Connection data including credentials and settings
    """
    """
    super().__init__(connection_id, connection_data)
    super().__init__(connection_id, connection_data)
    self.api_base_url = "https://open.tiktokapis.com/v2"
    self.api_base_url = "https://open.tiktokapis.com/v2"
    self.access_token = self.credentials.get("access_token")
    self.access_token = self.credentials.get("access_token")
    self.refresh_token = self.credentials.get("refresh_token")
    self.refresh_token = self.credentials.get("refresh_token")
    self.client_key = self.credentials.get("client_key")
    self.client_key = self.credentials.get("client_key")
    self.client_secret = self.credentials.get("client_secret")
    self.client_secret = self.credentials.get("client_secret")
    self.open_id = self.credentials.get("open_id")  # User's unique identifier
    self.open_id = self.credentials.get("open_id")  # User's unique identifier
    self.session = requests.Session()
    self.session = requests.Session()


    # Set up authentication if access token is provided
    # Set up authentication if access token is provided
    if self.access_token:
    if self.access_token:
    self.session.headers.update(
    self.session.headers.update(
    {
    {
    "Authorization": f"Bearer {self.access_token}",
    "Authorization": f"Bearer {self.access_token}",
    "Content-Type": "application/json",
    "Content-Type": "application/json",
    }
    }
    )
    )
    self._connected = True
    self._connected = True


    def authenticate(self) -> Dict[str, Any]:
    def authenticate(self) -> Dict[str, Any]:
    """
    """
    Authenticate with the TikTok API.
    Authenticate with the TikTok API.


    Returns:
    Returns:
    Dictionary containing authentication result and any additional platform data
    Dictionary containing authentication result and any additional platform data


    Raises:
    Raises:
    AuthenticationError: If authentication fails
    AuthenticationError: If authentication fails
    """
    """
    try:
    try:
    # If we already have an access token, verify it
    # If we already have an access token, verify it
    if self.access_token and self.open_id:
    if self.access_token and self.open_id:
    # Check if the token is valid by getting user info
    # Check if the token is valid by getting user info
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/user/info/",
    f"{self.api_base_url}/user/info/",
    params={
    params={
    "fields": "open_id,union_id,avatar_url,display_name,bio_description"
    "fields": "open_id,union_id,avatar_url,display_name,bio_description"
    },
    },
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    user_data = response.json().get("data", {})
    user_data = response.json().get("data", {})


    return {
    return {
    "authenticated": True,
    "authenticated": True,
    "open_id": user_data.get("open_id"),
    "open_id": user_data.get("open_id"),
    "union_id": user_data.get("union_id"),
    "union_id": user_data.get("union_id"),
    "display_name": user_data.get("display_name"),
    "display_name": user_data.get("display_name"),
    "avatar_url": user_data.get("avatar_url"),
    "avatar_url": user_data.get("avatar_url"),
    "bio_description": user_data.get("bio_description"),
    "bio_description": user_data.get("bio_description"),
    }
    }


    # If we have refresh token, client key, and client secret, we can refresh the access token
    # If we have refresh token, client key, and client secret, we can refresh the access token
    elif self.refresh_token and self.client_key and self.client_secret:
    elif self.refresh_token and self.client_key and self.client_secret:
    # Refresh the access token
    # Refresh the access token
    token_url = "https://open-api.tiktok.com/oauth/refresh_token/"
    token_url = "https://open-api.tiktok.com/oauth/refresh_token/"
    token_data = {
    token_data = {
    "client_key": self.client_key,
    "client_key": self.client_key,
    "client_secret": self.client_secret,
    "client_secret": self.client_secret,
    "grant_type": "refresh_token",
    "grant_type": "refresh_token",
    "refresh_token": self.refresh_token,
    "refresh_token": self.refresh_token,
    }
    }


    response = requests.post(token_url, data=token_data)
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()
    response.raise_for_status()
    token_response = response.json().get("data", {})
    token_response = response.json().get("data", {})


    # Update the access token
    # Update the access token
    self.access_token = token_response.get("access_token")
    self.access_token = token_response.get("access_token")
    self.refresh_token = token_response.get("refresh_token")
    self.refresh_token = token_response.get("refresh_token")
    self.open_id = token_response.get("open_id")
    self.open_id = token_response.get("open_id")
    self.session.headers.update(
    self.session.headers.update(
    {
    {
    "Authorization": f"Bearer {self.access_token}",
    "Authorization": f"Bearer {self.access_token}",
    "Content-Type": "application/json",
    "Content-Type": "application/json",
    }
    }
    )
    )
    self._connected = True
    self._connected = True


    # Get user information
    # Get user information
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/user/info/",
    f"{self.api_base_url}/user/info/",
    params={
    params={
    "fields": "open_id,union_id,avatar_url,display_name,bio_description"
    "fields": "open_id,union_id,avatar_url,display_name,bio_description"
    },
    },
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    user_data = response.json().get("data", {})
    user_data = response.json().get("data", {})


    return {
    return {
    "authenticated": True,
    "authenticated": True,
    "open_id": user_data.get("open_id"),
    "open_id": user_data.get("open_id"),
    "union_id": user_data.get("union_id"),
    "union_id": user_data.get("union_id"),
    "display_name": user_data.get("display_name"),
    "display_name": user_data.get("display_name"),
    "avatar_url": user_data.get("avatar_url"),
    "avatar_url": user_data.get("avatar_url"),
    "bio_description": user_data.get("bio_description"),
    "bio_description": user_data.get("bio_description"),
    "access_token": self.access_token,
    "access_token": self.access_token,
    "refresh_token": self.refresh_token,
    "refresh_token": self.refresh_token,
    "expires_in": token_response.get("expires_in"),
    "expires_in": token_response.get("expires_in"),
    }
    }


    else:
    else:
    raise AuthenticationError(
    raise AuthenticationError(
    "tiktok",
    "tiktok",
    "Missing required credentials (access_token and open_id, or refresh_token with client_key and client_secret)",
    "Missing required credentials (access_token and open_id, or refresh_token with client_key and client_secret)",
    )
    )


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"TikTok authentication error: {e}")
    logger.error(f"TikTok authentication error: {e}")
    raise AuthenticationError("tiktok", str(e))
    raise AuthenticationError("tiktok", str(e))


    def validate_content(self, content: Dict[str, Any]) -> bool:
    def validate_content(self, content: Dict[str, Any]) -> bool:
    """
    """
    Validate content for posting to TikTok.
    Validate content for posting to TikTok.


    Args:
    Args:
    content: Content to validate
    content: Content to validate


    Returns:
    Returns:
    True if content is valid, False otherwise
    True if content is valid, False otherwise


    Raises:
    Raises:
    ContentValidationError: If content validation fails with specific reason
    ContentValidationError: If content validation fails with specific reason
    """
    """
    # Check if we have a video
    # Check if we have a video
    if "video" not in content:
    if "video" not in content:
    raise ContentValidationError("tiktok", "Video is required for TikTok posts")
    raise ContentValidationError("tiktok", "Video is required for TikTok posts")


    # Check video source
    # Check video source
    if "file_path" not in content["video"] and "url" not in content["video"]:
    if "file_path" not in content["video"] and "url" not in content["video"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "tiktok", "Video must have either a file_path or url"
    "tiktok", "Video must have either a file_path or url"
    )
    )


    # Check caption if present (TikTok's limit is 2200 characters)
    # Check caption if present (TikTok's limit is 2200 characters)
    if "caption" in content and len(content["caption"]) > 2200:
    if "caption" in content and len(content["caption"]) > 2200:
    raise ContentValidationError(
    raise ContentValidationError(
    "tiktok",
    "tiktok",
    f"Caption exceeds 2,200 characters (current: {len(content['caption'])})",
    f"Caption exceeds 2,200 characters (current: {len(content['caption'])})",
    )
    )


    # Check hashtags if present
    # Check hashtags if present
    if "hashtags" in content:
    if "hashtags" in content:
    if not isinstance(content["hashtags"], list):
    if not isinstance(content["hashtags"], list):
    raise ContentValidationError(
    raise ContentValidationError(
    "tiktok", "Hashtags must be a list of strings"
    "tiktok", "Hashtags must be a list of strings"
    )
    )


    # TikTok allows up to 30 hashtags
    # TikTok allows up to 30 hashtags
    if len(content["hashtags"]) > 30:
    if len(content["hashtags"]) > 30:
    raise ContentValidationError(
    raise ContentValidationError(
    "tiktok",
    "tiktok",
    f"Too many hashtags (max: 30, current: {len(content['hashtags'])})",
    f"Too many hashtags (max: 30, current: {len(content['hashtags'])})",
    )
    )


    return True
    return True


    def post_content(
    def post_content(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    visibility: str = "public",
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post content to TikTok.
    Post content to TikTok.


    Args:
    Args:
    content: Content to post
    content: Content to post
    visibility: Visibility setting (public, private, friends)
    visibility: Visibility setting (public, private, friends)
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


    Returns:
    Returns:
    Dictionary containing the post details and platform-assigned ID
    Dictionary containing the post details and platform-assigned ID


    Raises:
    Raises:
    ContentValidationError: If content validation fails
    ContentValidationError: If content validation fails
    PostingError: If posting fails
    PostingError: If posting fails
    """
    """
    # Validate content first
    # Validate content first
    self.validate_content(content)
    self.validate_content(content)


    try:
    try:
    # Check if we have an access token (required for posting)
    # Check if we have an access token (required for posting)
    if not self.access_token or not self.open_id:
    if not self.access_token or not self.open_id:
    raise PostingError(
    raise PostingError(
    "tiktok", "Access token and open_id are required for posting videos"
    "tiktok", "Access token and open_id are required for posting videos"
    )
    )


    # In a real implementation, we would:
    # In a real implementation, we would:
    # 1. Upload the video to TikTok's servers
    # 1. Upload the video to TikTok's servers
    # 2. Create a post with the uploaded video
    # 2. Create a post with the uploaded video
    # 3. Set the caption, hashtags, and other metadata
    # 3. Set the caption, hashtags, and other metadata


    # For demonstration, we'll simulate a successful upload
    # For demonstration, we'll simulate a successful upload
    video_id = f"tiktok_video_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    video_id = f"tiktok_video_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    # Format hashtags if present
    # Format hashtags if present
    hashtags = content.get("hashtags", [])
    hashtags = content.get("hashtags", [])
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags]) if hashtags else ""
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags]) if hashtags else ""


    # Combine caption and hashtags
    # Combine caption and hashtags
    caption = content.get("caption", "")
    caption = content.get("caption", "")
    full_caption = f"{caption} {hashtag_str}".strip()
    full_caption = f"{caption} {hashtag_str}".strip()


    # Map visibility to TikTok privacy setting
    # Map visibility to TikTok privacy setting
    privacy_setting = self._map_visibility(visibility)
    privacy_setting = self._map_visibility(visibility)


    return {
    return {
    "id": video_id,
    "id": video_id,
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "url": f"https://www.tiktok.com/@{self.open_id}/video/{video_id}",
    "url": f"https://www.tiktok.com/@{self.open_id}/video/{video_id}",
    "platform_data": {
    "platform_data": {
    "video_id": video_id,
    "video_id": video_id,
    "caption": full_caption,
    "caption": full_caption,
    "privacy_setting": privacy_setting,
    "privacy_setting": privacy_setting,
    "open_id": self.open_id,
    "open_id": self.open_id,
    },
    },
    }
    }


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"TikTok posting error: {e}")
    logger.error(f"TikTok posting error: {e}")
    raise PostingError("tiktok", str(e))
    raise PostingError("tiktok", str(e))


    def _map_visibility(self, visibility: str) -> str:
    def _map_visibility(self, visibility: str) -> str:
    """
    """
    Map visibility setting to TikTok privacy setting.
    Map visibility setting to TikTok privacy setting.


    Args:
    Args:
    visibility: Visibility setting (public, private, friends)
    visibility: Visibility setting (public, private, friends)


    Returns:
    Returns:
    TikTok privacy setting
    TikTok privacy setting
    """
    """
    if visibility == "public":
    if visibility == "public":
    return "PUBLIC_TO_EVERYONE"
    return "PUBLIC_TO_EVERYONE"
    elif visibility == "friends":
    elif visibility == "friends":
    return "MUTUAL_FOLLOW_FRIENDS"
    return "MUTUAL_FOLLOW_FRIENDS"
    else:  # private
    else:  # private
    return "SELF_ONLY"
    return "SELF_ONLY"


    def schedule_post(
    def schedule_post(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    schedule_time: datetime,
    schedule_time: datetime,
    visibility: str = "public",
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Schedule a video for later publication on TikTok.
    Schedule a video for later publication on TikTok.


    Args:
    Args:
    content: Content to post
    content: Content to post
    schedule_time: Time to publish the video
    schedule_time: Time to publish the video
    visibility: Visibility setting (public, private, friends)
    visibility: Visibility setting (public, private, friends)
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


    Returns:
    Returns:
    Dictionary containing the scheduled video details and ID
    Dictionary containing the scheduled video details and ID


    Raises:
    Raises:
    ContentValidationError: If content validation fails
    ContentValidationError: If content validation fails
    SchedulingError: If scheduling fails
    SchedulingError: If scheduling fails
    NotSupportedError: If scheduling is not supported
    NotSupportedError: If scheduling is not supported
    """
    """
    # Validate content first
    # Validate content first
    self.validate_content(content)
    self.validate_content(content)


    try:
    try:
    # Check if we have an access token (required for posting)
    # Check if we have an access token (required for posting)
    if not self.access_token or not self.open_id:
    if not self.access_token or not self.open_id:
    raise SchedulingError(
    raise SchedulingError(
    "tiktok",
    "tiktok",
    "Access token and open_id are required for scheduling videos",
    "Access token and open_id are required for scheduling videos",
    )
    )


    # Note: TikTok API doesn't directly support scheduling posts
    # Note: TikTok API doesn't directly support scheduling posts
    # In a real implementation, we would use a third-party service or
    # In a real implementation, we would use a third-party service or
    # store the video locally and post it at the scheduled time
    # store the video locally and post it at the scheduled time


    # For demonstration, we'll return a mock scheduled video
    # For demonstration, we'll return a mock scheduled video
    scheduled_id = f"tiktok_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    scheduled_id = f"tiktok_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    # Format hashtags if present
    # Format hashtags if present
    hashtags = content.get("hashtags", [])
    hashtags = content.get("hashtags", [])
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags]) if hashtags else ""
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags]) if hashtags else ""


    # Combine caption and hashtags
    # Combine caption and hashtags
    caption = content.get("caption", "")
    caption = content.get("caption", "")
    full_caption = f"{caption} {hashtag_str}".strip()
    full_caption = f"{caption} {hashtag_str}".strip()


    # Map visibility to TikTok privacy setting
    # Map visibility to TikTok privacy setting
    privacy_setting = self._map_visibility(visibility)
    privacy_setting = self._map_visibility(visibility)


    return {
    return {
    "id": scheduled_id,
    "id": scheduled_id,
    "scheduled_time": schedule_time.isoformat(),
    "scheduled_time": schedule_time.isoformat(),
    "status": "scheduled",
    "status": "scheduled",
    "platform_data": {
    "platform_data": {
    "caption": full_caption,
    "caption": full_caption,
    "privacy_setting": privacy_setting,
    "privacy_setting": privacy_setting,
    "open_id": self.open_id,
    "open_id": self.open_id,
    },
    },
    }
    }


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"TikTok scheduling error: {e}")
    logger.error(f"TikTok scheduling error: {e}")
    raise SchedulingError("tiktok", str(e))
    raise SchedulingError("tiktok", str(e))


    def get_post(self, post_id: str) -> Dict[str, Any]:
    def get_post(self, post_id: str) -> Dict[str, Any]:
    """
    """
    Get details of a specific TikTok video.
    Get details of a specific TikTok video.


    Args:
    Args:
    post_id: ID of the video to retrieve
    post_id: ID of the video to retrieve


    Returns:
    Returns:
    Dictionary containing the video details
    Dictionary containing the video details


    Raises:
    Raises:
    PostNotFoundError: If the video ID is not found
    PostNotFoundError: If the video ID is not found
    """
    """
    try:
    try:
    # Check if we have an access token (required for getting video details)
    # Check if we have an access token (required for getting video details)
    if not self.access_token or not self.open_id:
    if not self.access_token or not self.open_id:
    raise PostingError(
    raise PostingError(
    "tiktok",
    "tiktok",
    "Access token and open_id are required for getting video details",
    "Access token and open_id are required for getting video details",
    )
    )


    # In a real implementation, we would use the TikTok API to get video details
    # In a real implementation, we would use the TikTok API to get video details
    # For demonstration, we'll return mock video details
    # For demonstration, we'll return mock video details


    # Check if the video ID is valid (starts with "tiktok_video_")
    # Check if the video ID is valid (starts with "tiktok_video_")
    if not post_id.startswith("tiktok_video_"):
    if not post_id.startswith("tiktok_video_"):
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)


    return {
    return {
    "id": post_id,
    "id": post_id,
    "caption": "This is a test video #AITools #PassiveIncome",
    "caption": "This is a test video #AITools #PassiveIncome",
    "create_time": (datetime.now() - timedelta(days=1)).isoformat(),
    "create_time": (datetime.now() - timedelta(days=1)).isoformat(),
    "cover_image_url": "https://example.com/cover.jpg",
    "cover_image_url": "https://example.com/cover.jpg",
    "share_url": f"https://www.tiktok.com/@{self.open_id}/video/{post_id}",
    "share_url": f"https://www.tiktok.com/@{self.open_id}/video/{post_id}",
    "video_description": "This is a test video created with the pAIssive Income social media integration module.",
    "video_description": "This is a test video created with the pAIssive Income social media integration module.",
    "duration": 15,  # seconds
    "duration": 15,  # seconds
    "height": 1920,
    "height": 1920,
    "width": 1080,
    "width": 1080,
    "stats": {
    "stats": {
    "comment_count": 25,
    "comment_count": 25,
    "like_count": 150,
    "like_count": 150,
    "share_count": 10,
    "share_count": 10,
    "view_count": 1500,
    "view_count": 1500,
    },
    },
    "platform_data": {"video_id": post_id, "open_id": self.open_id},
    "platform_data": {"video_id": post_id, "open_id": self.open_id},
    }
    }


except PostNotFoundError:
except PostNotFoundError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"TikTok get video error: {e}")
    logger.error(f"TikTok get video error: {e}")
    raise
    raise


    def delete_post(self, post_id: str) -> bool:
    def delete_post(self, post_id: str) -> bool:
    """
    """
    Delete a video from TikTok.
    Delete a video from TikTok.


    Args:
    Args:
    post_id: ID of the video to delete
    post_id: ID of the video to delete


    Returns:
    Returns:
    True if deleted successfully, False otherwise
    True if deleted successfully, False otherwise


    Raises:
    Raises:
    PostNotFoundError: If the video ID is not found
    PostNotFoundError: If the video ID is not found
    DeletionError: If deletion fails
    DeletionError: If deletion fails
    """
    """
    try:
    try:
    # Check if we have an access token (required for deleting videos)
    # Check if we have an access token (required for deleting videos)
    if not self.access_token or not self.open_id:
    if not self.access_token or not self.open_id:
    raise DeletionError(
    raise DeletionError(
    "tiktok",
    "tiktok",
    "Access token and open_id are required for deleting videos",
    "Access token and open_id are required for deleting videos",
    )
    )


    # In a real implementation, we would use the TikTok API to delete the video
    # In a real implementation, we would use the TikTok API to delete the video
    # For demonstration, we'll simulate a successful deletion
    # For demonstration, we'll simulate a successful deletion


    # Check if the video ID is valid (starts with "tiktok_video_")
    # Check if the video ID is valid (starts with "tiktok_video_")
    if not post_id.startswith("tiktok_video_"):
    if not post_id.startswith("tiktok_video_"):
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)


    return True
    return True


except PostNotFoundError:
except PostNotFoundError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"TikTok delete video error: {e}")
    logger.error(f"TikTok delete video error: {e}")
    raise DeletionError("tiktok", str(e))
    raise DeletionError("tiktok", str(e))


    def get_analytics(
    def get_analytics(
    self,
    self,
    post_id: Optional[str] = None,
    post_id: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get analytics data from TikTok.
    Get analytics data from TikTok.


    Args:
    Args:
    post_id: Optional ID of a specific video to get analytics for
    post_id: Optional ID of a specific video to get analytics for
    metrics: Optional list of specific metrics to retrieve
    metrics: Optional list of specific metrics to retrieve
    start_date: Optional start date for the analytics period
    start_date: Optional start date for the analytics period
    end_date: Optional end date for the analytics period
    end_date: Optional end date for the analytics period


    Returns:
    Returns:
    Dictionary containing the analytics data
    Dictionary containing the analytics data
    """
    """
    try:
    try:
    # Check if we have an access token (required for analytics)
    # Check if we have an access token (required for analytics)
    if not self.access_token or not self.open_id:
    if not self.access_token or not self.open_id:
    raise PostingError(
    raise PostingError(
    "tiktok", "Access token and open_id are required for analytics"
    "tiktok", "Access token and open_id are required for analytics"
    )
    )


    # Set default metrics if not provided
    # Set default metrics if not provided
    if not metrics:
    if not metrics:
    metrics = [
    metrics = [
    "video_views",
    "video_views",
    "likes",
    "likes",
    "comments",
    "comments",
    "shares",
    "shares",
    "profile_views",
    "profile_views",
    "new_followers",
    "new_followers",
    "total_time_watched",
    "total_time_watched",
    ]
    ]


    # Set default date range if not provided
    # Set default date range if not provided
    if not start_date:
    if not start_date:
    start_date = datetime.now() - timedelta(days=30)
    start_date = datetime.now() - timedelta(days=30)
    if not end_date:
    if not end_date:
    end_date = datetime.now()
    end_date = datetime.now()


    # Format dates for API
    # Format dates for API
    start_date_str = start_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")


    # If post_id is provided, get analytics for a specific video
    # If post_id is provided, get analytics for a specific video
    if post_id:
    if post_id:
    # In a real implementation, we would use the TikTok API to get video analytics
    # In a real implementation, we would use the TikTok API to get video analytics
    # For demonstration, we'll return mock analytics data
    # For demonstration, we'll return mock analytics data
    return {
    return {
    "video_id": post_id,
    "video_id": post_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": {
    "metrics": {
    "video_views": 1500,
    "video_views": 1500,
    "likes": 150,
    "likes": 150,
    "comments": 25,
    "comments": 25,
    "shares": 10,
    "shares": 10,
    "profile_views": 75,
    "profile_views": 75,
    "new_followers": 5,
    "new_followers": 5,
    "total_time_watched": 3750,  # seconds
    "total_time_watched": 3750,  # seconds
    },
    },
    }
    }


    # Otherwise, get account-level analytics
    # Otherwise, get account-level analytics
    else:
    else:
    # In a real implementation, we would use the TikTok API to get account analytics
    # In a real implementation, we would use the TikTok API to get account analytics
    # For demonstration, we'll return mock analytics data
    # For demonstration, we'll return mock analytics data
    return {
    return {
    "open_id": self.open_id,
    "open_id": self.open_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": {
    "metrics": {
    "video_views": 25000,
    "video_views": 25000,
    "profile_views": 1200,
    "profile_views": 1200,
    "likes": 2500,
    "likes": 2500,
    "comments": 350,
    "comments": 350,
    "shares": 180,
    "shares": 180,
    "new_followers": 85,
    "new_followers": 85,
    "total_followers": 1250,
    "total_followers": 1250,
    "total_time_watched": 62500,  # seconds
    "total_time_watched": 62500,  # seconds
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"TikTok analytics error: {e}")
    logger.error(f"TikTok analytics error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "video_id": post_id,
    "video_id": post_id,
    "open_id": self.open_id,
    "open_id": self.open_id,
    "period": {
    "period": {
    "start_date": start_date_str if start_date else None,
    "start_date": start_date_str if start_date else None,
    "end_date": end_date_str if end_date else None,
    "end_date": end_date_str if end_date else None,
    },
    },
    }
    }


    def get_audience_insights(
    def get_audience_insights(
    self,
    self,
    metrics: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    segment: Optional[Dict[str, Any]] = None,
    segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get audience insights from TikTok.
    Get audience insights from TikTok.


    Args:
    Args:
    metrics: Optional list of specific metrics to retrieve
    metrics: Optional list of specific metrics to retrieve
    segment: Optional audience segment to get insights for
    segment: Optional audience segment to get insights for


    Returns:
    Returns:
    Dictionary containing the audience insights
    Dictionary containing the audience insights
    """
    """
    try:
    try:
    # Check if we have an access token (required for audience insights)
    # Check if we have an access token (required for audience insights)
    if not self.access_token or not self.open_id:
    if not self.access_token or not self.open_id:
    raise PostingError(
    raise PostingError(
    "tiktok",
    "tiktok",
    "Access token and open_id are required for audience insights",
    "Access token and open_id are required for audience insights",
    )
    )


    # Set default metrics if not provided
    # Set default metrics if not provided
    if not metrics:
    if not metrics:
    metrics = ["demographics", "geography", "devices", "interests"]
    metrics = ["demographics", "geography", "devices", "interests"]


    # In a real implementation, we would use the TikTok API to get audience insights
    # In a real implementation, we would use the TikTok API to get audience insights
    # For demonstration, we'll return mock audience insights data
    # For demonstration, we'll return mock audience insights data
    return {
    return {
    "open_id": self.open_id,
    "open_id": self.open_id,
    "segment": segment or "all_followers",
    "segment": segment or "all_followers",
    "demographics": {
    "demographics": {
    "age_groups": {
    "age_groups": {
    "13-17": 0.25,
    "13-17": 0.25,
    "18-24": 0.40,
    "18-24": 0.40,
    "25-34": 0.20,
    "25-34": 0.20,
    "35-44": 0.10,
    "35-44": 0.10,
    "45-54": 0.03,
    "45-54": 0.03,
    "55+": 0.02,
    "55+": 0.02,
    },
    },
    "gender": {"female": 0.60, "male": 0.38, "other": 0.02},
    "gender": {"female": 0.60, "male": 0.38, "other": 0.02},
    },
    },
    "geography": {
    "geography": {
    "countries": {
    "countries": {
    "United States": 0.35,
    "United States": 0.35,
    "United Kingdom": 0.10,
    "United Kingdom": 0.10,
    "Canada": 0.08,
    "Canada": 0.08,
    "Australia": 0.05,
    "Australia": 0.05,
    "Germany": 0.04,
    "Germany": 0.04,
    "India": 0.04,
    "India": 0.04,
    "Other": 0.34,
    "Other": 0.34,
    },
    },
    "cities": [
    "cities": [
    {
    {
    "name": "New York",
    "name": "New York",
    "country": "United States",
    "country": "United States",
    "percentage": 0.07,
    "percentage": 0.07,
    },
    },
    {
    {
    "name": "Los Angeles",
    "name": "Los Angeles",
    "country": "United States",
    "country": "United States",
    "percentage": 0.05,
    "percentage": 0.05,
    },
    },
    {
    {
    "name": "London",
    "name": "London",
    "country": "United Kingdom",
    "country": "United Kingdom",
    "percentage": 0.04,
    "percentage": 0.04,
    },
    },
    {"name": "Toronto", "country": "Canada", "percentage": 0.03},
    {"name": "Toronto", "country": "Canada", "percentage": 0.03},
    {"name": "Sydney", "country": "Australia", "percentage": 0.02},
    {"name": "Sydney", "country": "Australia", "percentage": 0.02},
    ],
    ],
    },
    },
    "devices": {"mobile": 0.90, "tablet": 0.08, "desktop": 0.02},
    "devices": {"mobile": 0.90, "tablet": 0.08, "desktop": 0.02},
    "interests": [
    "interests": [
    {"category": "Entertainment", "score": 0.85},
    {"category": "Entertainment", "score": 0.85},
    {"category": "Comedy", "score": 0.80},
    {"category": "Comedy", "score": 0.80},
    {"category": "Music", "score": 0.75},
    {"category": "Music", "score": 0.75},
    {"category": "Fashion", "score": 0.65},
    {"category": "Fashion", "score": 0.65},
    {"category": "Technology", "score": 0.60},
    {"category": "Technology", "score": 0.60},
    ],
    ],
    "activity": {
    "activity": {
    "peak_times": {
    "peak_times": {
    "weekdays": {
    "weekdays": {
    "morning": 0.15,
    "morning": 0.15,
    "afternoon": 0.25,
    "afternoon": 0.25,
    "evening": 0.45,
    "evening": 0.45,
    "night": 0.15,
    "night": 0.15,
    },
    },
    "weekends": {
    "weekends": {
    "morning": 0.10,
    "morning": 0.10,
    "afternoon": 0.30,
    "afternoon": 0.30,
    "evening": 0.40,
    "evening": 0.40,
    "night": 0.20,
    "night": 0.20,
    },
    },
    }
    }
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"TikTok audience insights error: {e}")
    logger.error(f"TikTok audience insights error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "open_id": self.open_id,
    "open_id": self.open_id,
    "segment": segment or "all_followers",
    "segment": segment or "all_followers",
    }
    }