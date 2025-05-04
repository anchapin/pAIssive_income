"""
"""
Instagram adapter for social media integration.
Instagram adapter for social media integration.


This module provides an adapter for connecting to the Instagram Graph API for posting content,
This module provides an adapter for connecting to the Instagram Graph API for posting content,
retrieving analytics, and managing social media campaigns.
retrieving analytics, and managing social media campaigns.
"""
"""




import logging
import logging
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
NotSupportedError,
NotSupportedError,
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




class InstagramAdapter(BaseSocialMediaAdapter):
    class InstagramAdapter(BaseSocialMediaAdapter):
    """
    """
    Adapter for Instagram platform integration.
    Adapter for Instagram platform integration.


    This class implements the BaseSocialMediaAdapter interface for Instagram,
    This class implements the BaseSocialMediaAdapter interface for Instagram,
    providing methods for posting photos, stories, retrieving analytics, and managing
    providing methods for posting photos, stories, retrieving analytics, and managing
    Instagram campaigns.
    Instagram campaigns.
    """
    """


    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    """
    """
    Initialize the Instagram adapter.
    Initialize the Instagram adapter.


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
    self.api_base_url = (
    self.api_base_url = (
    "https://graph.facebook.com/v18.0"  # Instagram uses Facebook Graph API
    "https://graph.facebook.com/v18.0"  # Instagram uses Facebook Graph API
    )
    )
    self.access_token = self.credentials.get("access_token")
    self.access_token = self.credentials.get("access_token")
    self.instagram_account_id = self.credentials.get("instagram_account_id")
    self.instagram_account_id = self.credentials.get("instagram_account_id")
    self.facebook_page_id = self.credentials.get(
    self.facebook_page_id = self.credentials.get(
    "facebook_page_id"
    "facebook_page_id"
    )  # Required for some operations
    )  # Required for some operations
    self.session = requests.Session()
    self.session = requests.Session()


    # Set up authentication if access token is provided
    # Set up authentication if access token is provided
    if self.access_token:
    if self.access_token:
    self.session.params = {"access_token": self.access_token}
    self.session.params = {"access_token": self.access_token}
    self._connected = True
    self._connected = True


    def authenticate(self) -> Dict[str, Any]:
    def authenticate(self) -> Dict[str, Any]:
    """
    """
    Authenticate with the Instagram Graph API.
    Authenticate with the Instagram Graph API.


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
    if self.access_token and self.instagram_account_id:
    if self.access_token and self.instagram_account_id:
    # Check if the token is valid by getting basic account info
    # Check if the token is valid by getting basic account info
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/{self.instagram_account_id}"
    f"{self.api_base_url}/{self.instagram_account_id}"
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    account_data = response.json()
    account_data = response.json()


    return {
    return {
    "authenticated": True,
    "authenticated": True,
    "account_id": account_data.get("id"),
    "account_id": account_data.get("id"),
    "username": account_data.get("username"),
    "username": account_data.get("username"),
    "name": account_data.get("name"),
    "name": account_data.get("name"),
    "profile_picture_url": account_data.get("profile_picture_url"),
    "profile_picture_url": account_data.get("profile_picture_url"),
    }
    }


    else:
    else:
    raise AuthenticationError(
    raise AuthenticationError(
    "instagram",
    "instagram",
    "Missing required credentials (access_token and instagram_account_id)",
    "Missing required credentials (access_token and instagram_account_id)",
    )
    )


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Instagram authentication error: {e}")
    logger.error(f"Instagram authentication error: {e}")
    raise AuthenticationError("instagram", str(e))
    raise AuthenticationError("instagram", str(e))


    def validate_content(self, content: Dict[str, Any]) -> bool:
    def validate_content(self, content: Dict[str, Any]) -> bool:
    """
    """
    Validate content for posting to Instagram.
    Validate content for posting to Instagram.


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
    # Check if we have at least one content type
    # Check if we have at least one content type
    if not any(key in content for key in ["image", "video", "carousel", "story"]):
    if not any(key in content for key in ["image", "video", "carousel", "story"]):
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram",
    "instagram",
    "At least one content type (image, video, carousel, story) is required",
    "At least one content type (image, video, carousel, story) is required",
    )
    )


    # Check caption length if present (Instagram's limit is 2,200 characters)
    # Check caption length if present (Instagram's limit is 2,200 characters)
    if "caption" in content and len(content["caption"]) > 2200:
    if "caption" in content and len(content["caption"]) > 2200:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram",
    "instagram",
    f"Caption exceeds 2,200 characters (current: {len(content['caption'])})",
    f"Caption exceeds 2,200 characters (current: {len(content['caption'])})",
    )
    )


    # Check image if present
    # Check image if present
    if "image" in content:
    if "image" in content:
    if "url" not in content["image"] and "source" not in content["image"]:
    if "url" not in content["image"] and "source" not in content["image"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Image must have either a URL or source (base64 data)"
    "instagram", "Image must have either a URL or source (base64 data)"
    )
    )


    # Check video if present
    # Check video if present
    if "video" in content:
    if "video" in content:
    if "url" not in content["video"] and "source" not in content["video"]:
    if "url" not in content["video"] and "source" not in content["video"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Video must have either a URL or source (file path)"
    "instagram", "Video must have either a URL or source (file path)"
    )
    )


    # Check carousel if present
    # Check carousel if present
    if "carousel" in content:
    if "carousel" in content:
    if (
    if (
    not isinstance(content["carousel"], list)
    not isinstance(content["carousel"], list)
    or len(content["carousel"]) < 2
    or len(content["carousel"]) < 2
    ):
    ):
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Carousel must be a list with at least 2 items"
    "instagram", "Carousel must be a list with at least 2 items"
    )
    )


    for item in content["carousel"]:
    for item in content["carousel"]:
    if "type" not in item:
    if "type" not in item:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram",
    "instagram",
    "Each carousel item must have a 'type' field (image or video)",
    "Each carousel item must have a 'type' field (image or video)",
    )
    )


    if item["type"] not in ["image", "video"]:
    if item["type"] not in ["image", "video"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram",
    "instagram",
    f"Invalid carousel item type: {item['type']}. Allowed types: image, video",
    f"Invalid carousel item type: {item['type']}. Allowed types: image, video",
    )
    )


    if (
    if (
    item["type"] == "image"
    item["type"] == "image"
    and "url" not in item
    and "url" not in item
    and "source" not in item
    and "source" not in item
    ):
    ):
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Carousel image must have either a URL or source"
    "instagram", "Carousel image must have either a URL or source"
    )
    )


    if (
    if (
    item["type"] == "video"
    item["type"] == "video"
    and "url" not in item
    and "url" not in item
    and "source" not in item
    and "source" not in item
    ):
    ):
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Carousel video must have either a URL or source"
    "instagram", "Carousel video must have either a URL or source"
    )
    )


    # Check story if present
    # Check story if present
    if "story" in content:
    if "story" in content:
    if "type" not in content["story"]:
    if "type" not in content["story"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Story must have a 'type' field (image or video)"
    "instagram", "Story must have a 'type' field (image or video)"
    )
    )


    if content["story"]["type"] not in ["image", "video"]:
    if content["story"]["type"] not in ["image", "video"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram",
    "instagram",
    f"Invalid story type: {content['story']['type']}. Allowed types: image, video",
    f"Invalid story type: {content['story']['type']}. Allowed types: image, video",
    )
    )


    if (
    if (
    content["story"]["type"] == "image"
    content["story"]["type"] == "image"
    and "url" not in content["story"]
    and "url" not in content["story"]
    and "source" not in content["story"]
    and "source" not in content["story"]
    ):
    ):
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Story image must have either a URL or source"
    "instagram", "Story image must have either a URL or source"
    )
    )


    if (
    if (
    content["story"]["type"] == "video"
    content["story"]["type"] == "video"
    and "url" not in content["story"]
    and "url" not in content["story"]
    and "source" not in content["story"]
    and "source" not in content["story"]
    ):
    ):
    raise ContentValidationError(
    raise ContentValidationError(
    "instagram", "Story video must have either a URL or source"
    "instagram", "Story video must have either a URL or source"
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
    Post content to Instagram.
    Post content to Instagram.


    Args:
    Args:
    content: Content to post
    content: Content to post
    visibility: Visibility setting (public, private, etc.)
    visibility: Visibility setting (public, private, etc.)
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
    # Check if we have an Instagram account ID (required for posting)
    # Check if we have an Instagram account ID (required for posting)
    if not self.instagram_account_id:
    if not self.instagram_account_id:
    raise PostingError(
    raise PostingError(
    "instagram", "Instagram account ID is required for posting"
    "instagram", "Instagram account ID is required for posting"
    )
    )


    # Prepare post data
    # Prepare post data
    post_data = {}
    post_data = {}


    # Add caption if present
    # Add caption if present
    if "caption" in content:
    if "caption" in content:
    post_data["caption"] = content["caption"]
    post_data["caption"] = content["caption"]


    # Determine the endpoint and method based on content type
    # Determine the endpoint and method based on content type
    if "story" in content:
    if "story" in content:
    return self._post_story(content["story"])
    return self._post_story(content["story"])
    elif "carousel" in content:
    elif "carousel" in content:
    return self._post_carousel(content["carousel"], post_data)
    return self._post_carousel(content["carousel"], post_data)
    elif "image" in content:
    elif "image" in content:
    return self._post_image(content["image"], post_data)
    return self._post_image(content["image"], post_data)
    elif "video" in content:
    elif "video" in content:
    return self._post_video(content["video"], post_data)
    return self._post_video(content["video"], post_data)
    else:
    else:
    raise ContentValidationError("instagram", "No valid content type found")
    raise ContentValidationError("instagram", "No valid content type found")


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Instagram posting error: {e}")
    logger.error(f"Instagram posting error: {e}")
    raise PostingError("instagram", str(e))
    raise PostingError("instagram", str(e))


    def _post_image(
    def _post_image(
    self, image: Dict[str, Any], post_data: Dict[str, Any]
    self, image: Dict[str, Any], post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post an image to Instagram.
    Post an image to Instagram.


    Args:
    Args:
    image: Image data
    image: Image data
    post_data: Additional post data
    post_data: Additional post data


    Returns:
    Returns:
    Dictionary containing the post details and platform-assigned ID
    Dictionary containing the post details and platform-assigned ID


    Raises:
    Raises:
    PostingError: If posting fails
    PostingError: If posting fails
    """
    """
    try:
    try:
    # In a real implementation, we would:
    # In a real implementation, we would:
    # 1. Upload the image to Facebook's media endpoint
    # 1. Upload the image to Facebook's media endpoint
    # 2. Get the media container ID
    # 2. Get the media container ID
    # 3. Publish the media container
    # 3. Publish the media container


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    return {
    return {
    "id": post_id,
    "id": post_id,
    "type": "image",
    "type": "image",
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "platform_data": {
    "id": post_id,
    "id": post_id,
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"Instagram image posting error: {e}")
    logger.error(f"Instagram image posting error: {e}")
    raise PostingError("instagram", str(e))
    raise PostingError("instagram", str(e))


    def _post_video(
    def _post_video(
    self, video: Dict[str, Any], post_data: Dict[str, Any]
    self, video: Dict[str, Any], post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post a video to Instagram.
    Post a video to Instagram.


    Args:
    Args:
    video: Video data
    video: Video data
    post_data: Additional post data
    post_data: Additional post data


    Returns:
    Returns:
    Dictionary containing the post details and platform-assigned ID
    Dictionary containing the post details and platform-assigned ID


    Raises:
    Raises:
    PostingError: If posting fails
    PostingError: If posting fails
    """
    """
    try:
    try:
    # In a real implementation, we would:
    # In a real implementation, we would:
    # 1. Upload the video to Facebook's media endpoint
    # 1. Upload the video to Facebook's media endpoint
    # 2. Get the media container ID
    # 2. Get the media container ID
    # 3. Publish the media container
    # 3. Publish the media container


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    return {
    return {
    "id": post_id,
    "id": post_id,
    "type": "video",
    "type": "video",
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "platform_data": {
    "id": post_id,
    "id": post_id,
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"Instagram video posting error: {e}")
    logger.error(f"Instagram video posting error: {e}")
    raise PostingError("instagram", str(e))
    raise PostingError("instagram", str(e))


    def _post_carousel(
    def _post_carousel(
    self, carousel: List[Dict[str, Any]], post_data: Dict[str, Any]
    self, carousel: List[Dict[str, Any]], post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post a carousel to Instagram.
    Post a carousel to Instagram.


    Args:
    Args:
    carousel: List of carousel items
    carousel: List of carousel items
    post_data: Additional post data
    post_data: Additional post data


    Returns:
    Returns:
    Dictionary containing the post details and platform-assigned ID
    Dictionary containing the post details and platform-assigned ID


    Raises:
    Raises:
    PostingError: If posting fails
    PostingError: If posting fails
    """
    """
    try:
    try:
    # In a real implementation, we would:
    # In a real implementation, we would:
    # 1. Upload each media item to Facebook's media endpoint
    # 1. Upload each media item to Facebook's media endpoint
    # 2. Get the media container IDs
    # 2. Get the media container IDs
    # 3. Create a carousel container with the media IDs
    # 3. Create a carousel container with the media IDs
    # 4. Publish the carousel container
    # 4. Publish the carousel container


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    return {
    return {
    "id": post_id,
    "id": post_id,
    "type": "carousel",
    "type": "carousel",
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "platform_data": {
    "id": post_id,
    "id": post_id,
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    "children_count": len(carousel),
    "children_count": len(carousel),
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"Instagram carousel posting error: {e}")
    logger.error(f"Instagram carousel posting error: {e}")
    raise PostingError("instagram", str(e))
    raise PostingError("instagram", str(e))


    def _post_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
    def _post_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Post a story to Instagram.
    Post a story to Instagram.


    Args:
    Args:
    story: Story data
    story: Story data


    Returns:
    Returns:
    Dictionary containing the post details and platform-assigned ID
    Dictionary containing the post details and platform-assigned ID


    Raises:
    Raises:
    PostingError: If posting fails
    PostingError: If posting fails
    """
    """
    try:
    try:
    # In a real implementation, we would:
    # In a real implementation, we would:
    # 1. Upload the media to Facebook's media endpoint
    # 1. Upload the media to Facebook's media endpoint
    # 2. Get the media container ID
    # 2. Get the media container ID
    # 3. Publish the story
    # 3. Publish the story


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    story_id = f"instagram_story_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    story_id = f"instagram_story_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    return {
    return {
    "id": story_id,
    "id": story_id,
    "type": "story",
    "type": "story",
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {"id": story_id},
    "platform_data": {"id": story_id},
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"Instagram story posting error: {e}")
    logger.error(f"Instagram story posting error: {e}")
    raise PostingError("instagram", str(e))
    raise PostingError("instagram", str(e))


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
    Schedule a post for later publication on Instagram.
    Schedule a post for later publication on Instagram.


    Args:
    Args:
    content: Content to post
    content: Content to post
    schedule_time: Time to publish the post
    schedule_time: Time to publish the post
    visibility: Visibility setting (public, private, etc.)
    visibility: Visibility setting (public, private, etc.)
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


    Returns:
    Returns:
    Dictionary containing the scheduled post details and ID
    Dictionary containing the scheduled post details and ID


    Raises:
    Raises:
    ContentValidationError: If content validation fails
    ContentValidationError: If content validation fails
    SchedulingError: If scheduling fails
    SchedulingError: If scheduling fails
    NotSupportedError: If scheduling is not supported for the content type
    NotSupportedError: If scheduling is not supported for the content type
    """
    """
    # Validate content first
    # Validate content first
    self.validate_content(content)
    self.validate_content(content)


    try:
    try:
    # Check if we have an Instagram account ID (required for posting)
    # Check if we have an Instagram account ID (required for posting)
    if not self.instagram_account_id:
    if not self.instagram_account_id:
    raise SchedulingError(
    raise SchedulingError(
    "instagram", "Instagram account ID is required for scheduling posts"
    "instagram", "Instagram account ID is required for scheduling posts"
    )
    )


    # Check if the content type is supported for scheduling
    # Check if the content type is supported for scheduling
    if "story" in content:
    if "story" in content:
    raise NotSupportedError(
    raise NotSupportedError(
    "instagram", "Scheduling stories is not supported"
    "instagram", "Scheduling stories is not supported"
    )
    )


    # For demonstration, we'll simulate a successful scheduling
    # For demonstration, we'll simulate a successful scheduling
    scheduled_id = (
    scheduled_id = (
    f"instagram_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    f"instagram_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    )


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
    "content_type": (
    "content_type": (
    "image"
    "image"
    if "image" in content
    if "image" in content
    else "video" if "video" in content else "carousel"
    else "video" if "video" in content else "carousel"
    ),
    ),
    "caption": content.get("caption", ""),
    "caption": content.get("caption", ""),
    },
    },
    }
    }


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except NotSupportedError:
except NotSupportedError:
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"Instagram scheduling error: {e}")
    logger.error(f"Instagram scheduling error: {e}")
    raise SchedulingError("instagram", str(e))
    raise SchedulingError("instagram", str(e))


    def get_post(self, post_id: str) -> Dict[str, Any]:
    def get_post(self, post_id: str) -> Dict[str, Any]:
    """
    """
    Get details of a specific Instagram post.
    Get details of a specific Instagram post.


    Args:
    Args:
    post_id: ID of the post to retrieve
    post_id: ID of the post to retrieve


    Returns:
    Returns:
    Dictionary containing the post details
    Dictionary containing the post details


    Raises:
    Raises:
    PostNotFoundError: If the post ID is not found
    PostNotFoundError: If the post ID is not found
    """
    """
    try:
    try:
    # Get post details
    # Get post details
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/{post_id}",
    f"{self.api_base_url}/{post_id}",
    params={
    params={
    "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,children{media_type,media_url,thumbnail_url}"
    "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,children{media_type,media_url,thumbnail_url}"
    },
    },
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Format the response
    # Format the response
    post_data = {
    post_data = {
    "id": result.get("id"),
    "id": result.get("id"),
    "caption": result.get("caption"),
    "caption": result.get("caption"),
    "media_type": result.get("media_type"),
    "media_type": result.get("media_type"),
    "media_url": result.get("media_url"),
    "media_url": result.get("media_url"),
    "permalink": result.get("permalink"),
    "permalink": result.get("permalink"),
    "timestamp": result.get("timestamp"),
    "timestamp": result.get("timestamp"),
    "username": result.get("username"),
    "username": result.get("username"),
    "platform_data": result,
    "platform_data": result,
    }
    }


    # Add children data if it's a carousel
    # Add children data if it's a carousel
    if "children" in result:
    if "children" in result:
    post_data["children"] = result["children"]["data"]
    post_data["children"] = result["children"]["data"]


    return post_data
    return post_data


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Instagram get post error: {e}")
    logger.error(f"Instagram get post error: {e}")
    raise
    raise


    def delete_post(self, post_id: str) -> bool:
    def delete_post(self, post_id: str) -> bool:
    """
    """
    Delete a post from Instagram.
    Delete a post from Instagram.


    Args:
    Args:
    post_id: ID of the post to delete
    post_id: ID of the post to delete


    Returns:
    Returns:
    True if deleted successfully, False otherwise
    True if deleted successfully, False otherwise


    Raises:
    Raises:
    PostNotFoundError: If the post ID is not found
    PostNotFoundError: If the post ID is not found
    DeletionError: If deletion fails
    DeletionError: If deletion fails
    """
    """
    try:
    try:
    # Delete the post
    # Delete the post
    response = self.session.delete(f"{self.api_base_url}/{post_id}")
    response = self.session.delete(f"{self.api_base_url}/{post_id}")
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Check if deletion was successful
    # Check if deletion was successful
    if result.get("success", False):
    if result.get("success", False):
    return True
    return True
    else:
    else:
    raise DeletionError("instagram", "Failed to delete post")
    raise DeletionError("instagram", "Failed to delete post")


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Instagram delete post error: {e}")
    logger.error(f"Instagram delete post error: {e}")
    raise DeletionError("instagram", str(e))
    raise DeletionError("instagram", str(e))


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
    Get analytics data from Instagram.
    Get analytics data from Instagram.


    Args:
    Args:
    post_id: Optional ID of a specific post to get analytics for
    post_id: Optional ID of a specific post to get analytics for
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
    # Set default metrics if not provided
    # Set default metrics if not provided
    if not metrics:
    if not metrics:
    metrics = [
    metrics = [
    "impressions",
    "impressions",
    "reach",
    "reach",
    "engagement",
    "engagement",
    "saved",
    "saved",
    "video_views",
    "video_views",
    "profile_visits",
    "profile_visits",
    "follows",
    "follows",
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


    # If post_id is provided, get analytics for a specific post
    # If post_id is provided, get analytics for a specific post
    if post_id:
    if post_id:
    # Get post insights
    # Get post insights
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/{post_id}/insights",
    f"{self.api_base_url}/{post_id}/insights",
    params={"metric": ",".join(metrics)},
    params={"metric": ",".join(metrics)},
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Extract metrics
    # Extract metrics
    analytics = {
    analytics = {
    "post_id": post_id,
    "post_id": post_id,
    "metrics": self._extract_insights(result),
    "metrics": self._extract_insights(result),
    }
    }


    return analytics
    return analytics


    # Otherwise, get account-level analytics
    # Otherwise, get account-level analytics
    else:
    else:
    # Get account insights
    # Get account insights
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/{self.instagram_account_id}/insights",
    f"{self.api_base_url}/{self.instagram_account_id}/insights",
    params={
    params={
    "metric": ",".join(metrics),
    "metric": ",".join(metrics),
    "period": "day",
    "period": "day",
    "since": start_date_str,
    "since": start_date_str,
    "until": end_date_str,
    "until": end_date_str,
    },
    },
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Extract metrics
    # Extract metrics
    analytics = {
    analytics = {
    "account_id": self.instagram_account_id,
    "account_id": self.instagram_account_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": self._extract_insights(result),
    "metrics": self._extract_insights(result),
    }
    }


    return analytics
    return analytics


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Instagram analytics error: {e}")
    logger.error(f"Instagram analytics error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "post_id": post_id,
    "post_id": post_id,
    "account_id": self.instagram_account_id,
    "account_id": self.instagram_account_id,
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
    Get audience insights from Instagram.
    Get audience insights from Instagram.


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
    # Set default metrics if not provided
    # Set default metrics if not provided
    if not metrics:
    if not metrics:
    metrics = [
    metrics = [
    "audience_demographics",
    "audience_demographics",
    "audience_interests",
    "audience_interests",
    "audience_locations",
    "audience_locations",
    ]
    ]


    # Check if we have an Instagram account ID
    # Check if we have an Instagram account ID
    if not self.instagram_account_id:
    if not self.instagram_account_id:
    return {
    return {
    "error": "Instagram account ID is required for audience insights"
    "error": "Instagram account ID is required for audience insights"
    }
    }


    # Get audience insights
    # Get audience insights
    # Note: Instagram's Audience Insights API is limited and requires special permissions
    # Note: Instagram's Audience Insights API is limited and requires special permissions
    # For demonstration, we'll return mock audience insights data
    # For demonstration, we'll return mock audience insights data


    return {
    return {
    "account_id": self.instagram_account_id,
    "account_id": self.instagram_account_id,
    "segment": segment or "all_followers",
    "segment": segment or "all_followers",
    "demographics": {
    "demographics": {
    "age_gender": {
    "age_gender": {
    "F.13-17": 0.05,
    "F.13-17": 0.05,
    "F.18-24": 0.15,
    "F.18-24": 0.15,
    "F.25-34": 0.20,
    "F.25-34": 0.20,
    "F.35-44": 0.10,
    "F.35-44": 0.10,
    "F.45-54": 0.05,
    "F.45-54": 0.05,
    "F.55+": 0.02,
    "F.55+": 0.02,
    "M.13-17": 0.03,
    "M.13-17": 0.03,
    "M.18-24": 0.18,
    "M.18-24": 0.18,
    "M.25-34": 0.15,
    "M.25-34": 0.15,
    "M.35-44": 0.05,
    "M.35-44": 0.05,
    "M.45-54": 0.01,
    "M.45-54": 0.01,
    "M.55+": 0.01,
    "M.55+": 0.01,
    },
    },
    "location": {
    "location": {
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
    "France": 0.03,
    "France": 0.03,
    "Other": 0.35,
    "Other": 0.35,
    },
    },
    },
    },
    "interests": [
    "interests": [
    {"category": "Fashion", "score": 0.75},
    {"category": "Fashion", "score": 0.75},
    {"category": "Travel", "score": 0.70},
    {"category": "Travel", "score": 0.70},
    {"category": "Food & Drink", "score": 0.65},
    {"category": "Food & Drink", "score": 0.65},
    {"category": "Photography", "score": 0.85},
    {"category": "Photography", "score": 0.85},
    {"category": "Fitness", "score": 0.55},
    {"category": "Fitness", "score": 0.55},
    ],
    ],
    "activity": {
    "activity": {
    "most_active_times": {
    "most_active_times": {
    "days": {
    "days": {
    "Monday": 0.12,
    "Monday": 0.12,
    "Tuesday": 0.13,
    "Tuesday": 0.13,
    "Wednesday": 0.15,
    "Wednesday": 0.15,
    "Thursday": 0.18,
    "Thursday": 0.18,
    "Friday": 0.20,
    "Friday": 0.20,
    "Saturday": 0.15,
    "Saturday": 0.15,
    "Sunday": 0.07,
    "Sunday": 0.07,
    },
    },
    "hours": {
    "hours": {
    "morning": 0.20,
    "morning": 0.20,
    "afternoon": 0.25,
    "afternoon": 0.25,
    "evening": 0.40,
    "evening": 0.40,
    "night": 0.15,
    "night": 0.15,
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
    logger.error(f"Instagram audience insights error: {e}")
    logger.error(f"Instagram audience insights error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "account_id": self.instagram_account_id,
    "account_id": self.instagram_account_id,
    "segment": segment or "all_followers",
    "segment": segment or "all_followers",
    }
    }


    def _extract_insights(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
    def _extract_insights(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Extract metrics from Instagram insights data.
    Extract metrics from Instagram insights data.


    Args:
    Args:
    insights_data: Raw insights data from Instagram API
    insights_data: Raw insights data from Instagram API


    Returns:
    Returns:
    Dictionary of formatted metrics
    Dictionary of formatted metrics
    """
    """
    metrics = {}
    metrics = {}


    # Extract data from insights response
    # Extract data from insights response
    data = insights_data.get("data", [])
    data = insights_data.get("data", [])


    for item in data:
    for item in data:
    name = item.get("name")
    name = item.get("name")
    values = item.get("values", [])
    values = item.get("values", [])


    if values:
    if values:
    # Get the most recent value
    # Get the most recent value
    latest_value = values[0].get("value")
    latest_value = values[0].get("value")


    # Handle different value types
    # Handle different value types
    if isinstance(latest_value, dict):
    if isinstance(latest_value, dict):
    # For metrics with breakdowns
    # For metrics with breakdowns
    metrics[name] = latest_value
    metrics[name] = latest_value
    else:
    else:
    # For simple numeric metrics
    # For simple numeric metrics
    metrics[name] = latest_value
    metrics[name] = latest_value


    return metrics
    return metrics