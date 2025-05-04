"""
Instagram adapter for social media integration.

This module provides an adapter for connecting to the Instagram Graph API for posting content,
retrieving analytics, and managing social media campaigns.
"""


import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from marketing.social_media_adapters.base_adapter import BaseSocialMediaAdapter

(
AuthenticationError,
ContentValidationError,
DeletionError,
NotSupportedError,
PostingError,
PostNotFoundError,
SchedulingError,
)
# Set up logging
logger = logging.getLogger(__name__)


class InstagramAdapter(BaseSocialMediaAdapter):
    """
    Adapter for Instagram platform integration.

    This class implements the BaseSocialMediaAdapter interface for Instagram,
    providing methods for posting photos, stories, retrieving analytics, and managing
    Instagram campaigns.
    """

    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    """
    Initialize the Instagram adapter.

    Args:
    connection_id: Unique identifier for the connection
    connection_data: Connection data including credentials and settings
    """
    super().__init__(connection_id, connection_data)
    self.api_base_url = (
    "https://graph.facebook.com/v18.0"  # Instagram uses Facebook Graph API
    )
    self.access_token = self.credentials.get("access_token")
    self.instagram_account_id = self.credentials.get("instagram_account_id")
    self.facebook_page_id = self.credentials.get(
    "facebook_page_id"
    )  # Required for some operations
    self.session = requests.Session()

    # Set up authentication if access token is provided
    if self.access_token:
    self.session.params = {"access_token": self.access_token}
    self._connected = True

    def authenticate(self) -> Dict[str, Any]:
    """
    Authenticate with the Instagram Graph API.

    Returns:
    Dictionary containing authentication result and any additional platform data

    Raises:
    AuthenticationError: If authentication fails
    """
    try:
    # If we already have an access token, verify it
    if self.access_token and self.instagram_account_id:
    # Check if the token is valid by getting basic account info
    response = self.session.get(
    f"{self.api_base_url}/{self.instagram_account_id}"
    )
    response.raise_for_status()
    account_data = response.json()

    return {
    "authenticated": True,
    "account_id": account_data.get("id"),
    "username": account_data.get("username"),
    "name": account_data.get("name"),
    "profile_picture_url": account_data.get("profile_picture_url"),
    }

    else:
    raise AuthenticationError(
    "instagram",
    "Missing required credentials (access_token and instagram_account_id)",
    )

except requests.exceptions.RequestException as e:
    logger.error(f"Instagram authentication error: {e}")
    raise AuthenticationError("instagram", str(e))

    def validate_content(self, content: Dict[str, Any]) -> bool:
    """
    Validate content for posting to Instagram.

    Args:
    content: Content to validate

    Returns:
    True if content is valid, False otherwise

    Raises:
    ContentValidationError: If content validation fails with specific reason
    """
    # Check if we have at least one content type
    if not any(key in content for key in ["image", "video", "carousel", "story"]):
    raise ContentValidationError(
    "instagram",
    "At least one content type (image, video, carousel, story) is required",
    )

    # Check caption length if present (Instagram's limit is 2,200 characters)
    if "caption" in content and len(content["caption"]) > 2200:
    raise ContentValidationError(
    "instagram",
    f"Caption exceeds 2,200 characters (current: {len(content['caption'])})",
    )

    # Check image if present
    if "image" in content:
    if "url" not in content["image"] and "source" not in content["image"]:
    raise ContentValidationError(
    "instagram", "Image must have either a URL or source (base64 data)"
    )

    # Check video if present
    if "video" in content:
    if "url" not in content["video"] and "source" not in content["video"]:
    raise ContentValidationError(
    "instagram", "Video must have either a URL or source (file path)"
    )

    # Check carousel if present
    if "carousel" in content:
    if (
    not isinstance(content["carousel"], list)
    or len(content["carousel"]) < 2
    ):
    raise ContentValidationError(
    "instagram", "Carousel must be a list with at least 2 items"
    )

    for item in content["carousel"]:
    if "type" not in item:
    raise ContentValidationError(
    "instagram",
    "Each carousel item must have a 'type' field (image or video)",
    )

    if item["type"] not in ["image", "video"]:
    raise ContentValidationError(
    "instagram",
    f"Invalid carousel item type: {item['type']}. Allowed types: image, video",
    )

    if (
    item["type"] == "image"
    and "url" not in item
    and "source" not in item
    ):
    raise ContentValidationError(
    "instagram", "Carousel image must have either a URL or source"
    )

    if (
    item["type"] == "video"
    and "url" not in item
    and "source" not in item
    ):
    raise ContentValidationError(
    "instagram", "Carousel video must have either a URL or source"
    )

    # Check story if present
    if "story" in content:
    if "type" not in content["story"]:
    raise ContentValidationError(
    "instagram", "Story must have a 'type' field (image or video)"
    )

    if content["story"]["type"] not in ["image", "video"]:
    raise ContentValidationError(
    "instagram",
    f"Invalid story type: {content['story']['type']}. Allowed types: image, video",
    )

    if (
    content["story"]["type"] == "image"
    and "url" not in content["story"]
    and "source" not in content["story"]
    ):
    raise ContentValidationError(
    "instagram", "Story image must have either a URL or source"
    )

    if (
    content["story"]["type"] == "video"
    and "url" not in content["story"]
    and "source" not in content["story"]
    ):
    raise ContentValidationError(
    "instagram", "Story video must have either a URL or source"
    )

    return True

    def post_content(
    self,
    content: Dict[str, Any],
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Post content to Instagram.

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
    # Validate content first
    self.validate_content(content)

    try:
    # Check if we have an Instagram account ID (required for posting)
    if not self.instagram_account_id:
    raise PostingError(
    "instagram", "Instagram account ID is required for posting"
    )

    # Prepare post data
    post_data = {}

    # Add caption if present
    if "caption" in content:
    post_data["caption"] = content["caption"]

    # Determine the endpoint and method based on content type
    if "story" in content:
    return self._post_story(content["story"])
    elif "carousel" in content:
    return self._post_carousel(content["carousel"], post_data)
    elif "image" in content:
    return self._post_image(content["image"], post_data)
    elif "video" in content:
    return self._post_video(content["video"], post_data)
    else:
    raise ContentValidationError("instagram", "No valid content type found")

except ContentValidationError:
    raise
except requests.exceptions.RequestException as e:
    logger.error(f"Instagram posting error: {e}")
    raise PostingError("instagram", str(e))

    def _post_image(
    self, image: Dict[str, Any], post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    """
    Post an image to Instagram.

    Args:
    image: Image data
    post_data: Additional post data

    Returns:
    Dictionary containing the post details and platform-assigned ID

    Raises:
    PostingError: If posting fails
    """
    try:
    # In a real implementation, we would:
    # 1. Upload the image to Facebook's media endpoint
    # 2. Get the media container ID
    # 3. Publish the media container

    # For demonstration, we'll simulate a successful post
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
    "id": post_id,
    "type": "image",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "id": post_id,
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    },
    }

except Exception as e:
    logger.error(f"Instagram image posting error: {e}")
    raise PostingError("instagram", str(e))

    def _post_video(
    self, video: Dict[str, Any], post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    """
    Post a video to Instagram.

    Args:
    video: Video data
    post_data: Additional post data

    Returns:
    Dictionary containing the post details and platform-assigned ID

    Raises:
    PostingError: If posting fails
    """
    try:
    # In a real implementation, we would:
    # 1. Upload the video to Facebook's media endpoint
    # 2. Get the media container ID
    # 3. Publish the media container

    # For demonstration, we'll simulate a successful post
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
    "id": post_id,
    "type": "video",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "id": post_id,
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    },
    }

except Exception as e:
    logger.error(f"Instagram video posting error: {e}")
    raise PostingError("instagram", str(e))

    def _post_carousel(
    self, carousel: List[Dict[str, Any]], post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    """
    Post a carousel to Instagram.

    Args:
    carousel: List of carousel items
    post_data: Additional post data

    Returns:
    Dictionary containing the post details and platform-assigned ID

    Raises:
    PostingError: If posting fails
    """
    try:
    # In a real implementation, we would:
    # 1. Upload each media item to Facebook's media endpoint
    # 2. Get the media container IDs
    # 3. Create a carousel container with the media IDs
    # 4. Publish the carousel container

    # For demonstration, we'll simulate a successful post
    post_id = f"instagram_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
    "id": post_id,
    "type": "carousel",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "id": post_id,
    "permalink": f"https://www.instagram.com/p/{post_id}/",
    "children_count": len(carousel),
    },
    }

except Exception as e:
    logger.error(f"Instagram carousel posting error: {e}")
    raise PostingError("instagram", str(e))

    def _post_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post a story to Instagram.

    Args:
    story: Story data

    Returns:
    Dictionary containing the post details and platform-assigned ID

    Raises:
    PostingError: If posting fails
    """
    try:
    # In a real implementation, we would:
    # 1. Upload the media to Facebook's media endpoint
    # 2. Get the media container ID
    # 3. Publish the story

    # For demonstration, we'll simulate a successful post
    story_id = f"instagram_story_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
    "id": story_id,
    "type": "story",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "platform_data": {"id": story_id},
    }

except Exception as e:
    logger.error(f"Instagram story posting error: {e}")
    raise PostingError("instagram", str(e))

    def schedule_post(
    self,
    content: Dict[str, Any],
    schedule_time: datetime,
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Schedule a post for later publication on Instagram.

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
    NotSupportedError: If scheduling is not supported for the content type
    """
    # Validate content first
    self.validate_content(content)

    try:
    # Check if we have an Instagram account ID (required for posting)
    if not self.instagram_account_id:
    raise SchedulingError(
    "instagram", "Instagram account ID is required for scheduling posts"
    )

    # Check if the content type is supported for scheduling
    if "story" in content:
    raise NotSupportedError(
    "instagram", "Scheduling stories is not supported"
    )

    # For demonstration, we'll simulate a successful scheduling
    scheduled_id = (
    f"instagram_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    return {
    "id": scheduled_id,
    "scheduled_time": schedule_time.isoformat(),
    "status": "scheduled",
    "platform_data": {
    "content_type": (
    "image"
    if "image" in content
    else "video" if "video" in content else "carousel"
    ),
    "caption": content.get("caption", ""),
    },
    }

except ContentValidationError:
    raise
except NotSupportedError:
    raise
except Exception as e:
    logger.error(f"Instagram scheduling error: {e}")
    raise SchedulingError("instagram", str(e))

    def get_post(self, post_id: str) -> Dict[str, Any]:
    """
    Get details of a specific Instagram post.

    Args:
    post_id: ID of the post to retrieve

    Returns:
    Dictionary containing the post details

    Raises:
    PostNotFoundError: If the post ID is not found
    """
    try:
    # Get post details
    response = self.session.get(
    f"{self.api_base_url}/{post_id}",
    params={
    "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,children{media_type,media_url,thumbnail_url}"
    },
    )
    response.raise_for_status()
    result = response.json()

    # Format the response
    post_data = {
    "id": result.get("id"),
    "caption": result.get("caption"),
    "media_type": result.get("media_type"),
    "media_url": result.get("media_url"),
    "permalink": result.get("permalink"),
    "timestamp": result.get("timestamp"),
    "username": result.get("username"),
    "platform_data": result,
    }

    # Add children data if it's a carousel
    if "children" in result:
    post_data["children"] = result["children"]["data"]

    return post_data

except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Instagram get post error: {e}")
    raise

    def delete_post(self, post_id: str) -> bool:
    """
    Delete a post from Instagram.

    Args:
    post_id: ID of the post to delete

    Returns:
    True if deleted successfully, False otherwise

    Raises:
    PostNotFoundError: If the post ID is not found
    DeletionError: If deletion fails
    """
    try:
    # Delete the post
    response = self.session.delete(f"{self.api_base_url}/{post_id}")
    response.raise_for_status()
    result = response.json()

    # Check if deletion was successful
    if result.get("success", False):
    return True
    else:
    raise DeletionError("instagram", "Failed to delete post")

except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Instagram delete post error: {e}")
    raise DeletionError("instagram", str(e))

    def get_analytics(
    self,
    post_id: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    """
    Get analytics data from Instagram.

    Args:
    post_id: Optional ID of a specific post to get analytics for
    metrics: Optional list of specific metrics to retrieve
    start_date: Optional start date for the analytics period
    end_date: Optional end date for the analytics period

    Returns:
    Dictionary containing the analytics data
    """
    try:
    # Set default metrics if not provided
    if not metrics:
    metrics = [
    "impressions",
    "reach",
    "engagement",
    "saved",
    "video_views",
    "profile_visits",
    "follows",
    ]

    # Set default date range if not provided
    if not start_date:
    start_date = datetime.now() - timedelta(days=30)
    if not end_date:
    end_date = datetime.now()

    # Format dates for API
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # If post_id is provided, get analytics for a specific post
    if post_id:
    # Get post insights
    response = self.session.get(
    f"{self.api_base_url}/{post_id}/insights",
    params={"metric": ",".join(metrics)},
    )
    response.raise_for_status()
    result = response.json()

    # Extract metrics
    analytics = {
    "post_id": post_id,
    "metrics": self._extract_insights(result),
    }

    return analytics

    # Otherwise, get account-level analytics
    else:
    # Get account insights
    response = self.session.get(
    f"{self.api_base_url}/{self.instagram_account_id}/insights",
    params={
    "metric": ",".join(metrics),
    "period": "day",
    "since": start_date_str,
    "until": end_date_str,
    },
    )
    response.raise_for_status()
    result = response.json()

    # Extract metrics
    analytics = {
    "account_id": self.instagram_account_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": self._extract_insights(result),
    }

    return analytics

except requests.exceptions.RequestException as e:
    logger.error(f"Instagram analytics error: {e}")
    return {
    "error": str(e),
    "post_id": post_id,
    "account_id": self.instagram_account_id,
    "period": {
    "start_date": start_date_str if start_date else None,
    "end_date": end_date_str if end_date else None,
    },
    }

    def get_audience_insights(
    self,
    metrics: Optional[List[str]] = None,
    segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Get audience insights from Instagram.

    Args:
    metrics: Optional list of specific metrics to retrieve
    segment: Optional audience segment to get insights for

    Returns:
    Dictionary containing the audience insights
    """
    try:
    # Set default metrics if not provided
    if not metrics:
    metrics = [
    "audience_demographics",
    "audience_interests",
    "audience_locations",
    ]

    # Check if we have an Instagram account ID
    if not self.instagram_account_id:
    return {
    "error": "Instagram account ID is required for audience insights"
    }

    # Get audience insights
    # Note: Instagram's Audience Insights API is limited and requires special permissions
    # For demonstration, we'll return mock audience insights data

    return {
    "account_id": self.instagram_account_id,
    "segment": segment or "all_followers",
    "demographics": {
    "age_gender": {
    "F.13-17": 0.05,
    "F.18-24": 0.15,
    "F.25-34": 0.20,
    "F.35-44": 0.10,
    "F.45-54": 0.05,
    "F.55+": 0.02,
    "M.13-17": 0.03,
    "M.18-24": 0.18,
    "M.25-34": 0.15,
    "M.35-44": 0.05,
    "M.45-54": 0.01,
    "M.55+": 0.01,
    },
    "location": {
    "United States": 0.35,
    "United Kingdom": 0.10,
    "Canada": 0.08,
    "Australia": 0.05,
    "Germany": 0.04,
    "France": 0.03,
    "Other": 0.35,
    },
    },
    "interests": [
    {"category": "Fashion", "score": 0.75},
    {"category": "Travel", "score": 0.70},
    {"category": "Food & Drink", "score": 0.65},
    {"category": "Photography", "score": 0.85},
    {"category": "Fitness", "score": 0.55},
    ],
    "activity": {
    "most_active_times": {
    "days": {
    "Monday": 0.12,
    "Tuesday": 0.13,
    "Wednesday": 0.15,
    "Thursday": 0.18,
    "Friday": 0.20,
    "Saturday": 0.15,
    "Sunday": 0.07,
    },
    "hours": {
    "morning": 0.20,
    "afternoon": 0.25,
    "evening": 0.40,
    "night": 0.15,
    },
    }
    },
    }

except Exception as e:
    logger.error(f"Instagram audience insights error: {e}")
    return {
    "error": str(e),
    "account_id": self.instagram_account_id,
    "segment": segment or "all_followers",
    }

    def _extract_insights(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metrics from Instagram insights data.

    Args:
    insights_data: Raw insights data from Instagram API

    Returns:
    Dictionary of formatted metrics
    """
    metrics = {}

    # Extract data from insights response
    data = insights_data.get("data", [])

    for item in data:
    name = item.get("name")
    values = item.get("values", [])

    if values:
    # Get the most recent value
    latest_value = values[0].get("value")

    # Handle different value types
    if isinstance(latest_value, dict):
    # For metrics with breakdowns
    metrics[name] = latest_value
    else:
    # For simple numeric metrics
    metrics[name] = latest_value

    return metrics