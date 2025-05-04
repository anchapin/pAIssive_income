"""
Pinterest adapter for social media integration.

This module provides an adapter for connecting to the Pinterest API for posting pins,
creating boards, retrieving analytics, and managing Pinterest campaigns.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from marketing.social_media_adapters.base_adapter import BaseSocialMediaAdapter

(
AuthenticationError,
ContentValidationError,
DeletionError,
PostingError,
PostNotFoundError,
SchedulingError,
)
# Set up logging
logger = logging.getLogger(__name__)


class PinterestAdapter(BaseSocialMediaAdapter):
    """
    Adapter for Pinterest platform integration.

    This class implements the BaseSocialMediaAdapter interface for Pinterest,
    providing methods for posting pins, creating boards, retrieving analytics,
    and managing Pinterest campaigns.
    """

    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    """
    Initialize the Pinterest adapter.

    Args:
    connection_id: Unique identifier for the connection
    connection_data: Connection data including credentials and settings
    """
    super().__init__(connection_id, connection_data)
    self.api_base_url = "https://api.pinterest.com/v5"
    self.access_token = self.credentials.get("access_token")
    self.refresh_token = self.credentials.get("refresh_token")
    self.client_id = self.credentials.get("client_id")
    self.client_secret = self.credentials.get("client_secret")
    self.user_id = self.credentials.get("user_id")
    self.session = requests.Session()

    # Set up authentication if access token is provided
    if self.access_token:
    self.session.headers.update(
    {
    "Authorization": f"Bearer {self.access_token}",
    "Content-Type": "application/json",
    }
    )
    self._connected = True

    def authenticate(self) -> Dict[str, Any]:
    """
    Authenticate with the Pinterest API.

    Returns:
    Dictionary containing authentication result and any additional platform data

    Raises:
    AuthenticationError: If authentication fails
    """
    try:
    # If we already have an access token, verify it
    if self.access_token:
    # Check if the token is valid by getting user info
    response = self.session.get(f"{self.api_base_url}/user_account")
    response.raise_for_status()
    user_data = response.json()

    # Store the user ID
    self.user_id = user_data.get("username")

    return {
    "authenticated": True,
    "user_id": user_data.get("username"),
    "account_type": user_data.get("account_type"),
    "profile_image": user_data.get("profile_image"),
    "website_url": user_data.get("website_url"),
    }

    # If we have refresh token, client ID, and client secret, we can refresh the access token
    elif self.refresh_token and self.client_id and self.client_secret:
    # Refresh the access token
    token_url = "https://api.pinterest.com/v5/oauth/token"
    token_data = {
    "grant_type": "refresh_token",
    "refresh_token": self.refresh_token,
    "client_id": self.client_id,
    "client_secret": self.client_secret,
    }

    response = requests.post(token_url, data=token_data)
    response.raise_for_status()
    token_response = response.json()

    # Update the access token
    self.access_token = token_response["access_token"]
    self.refresh_token = token_response.get(
    "refresh_token", self.refresh_token
    )
    self.session.headers.update(
    {
    "Authorization": f"Bearer {self.access_token}",
    "Content-Type": "application/json",
    }
    )
    self._connected = True

    # Get user information
    response = self.session.get(f"{self.api_base_url}/user_account")
    response.raise_for_status()
    user_data = response.json()

    # Store the user ID
    self.user_id = user_data.get("username")

    return {
    "authenticated": True,
    "user_id": user_data.get("username"),
    "account_type": user_data.get("account_type"),
    "profile_image": user_data.get("profile_image"),
    "website_url": user_data.get("website_url"),
    "access_token": self.access_token,
    "refresh_token": self.refresh_token,
    "expires_in": token_response.get("expires_in"),
    }

    else:
    raise AuthenticationError(
    "pinterest",
    "Missing required credentials (access_token or refresh_token with client_id and client_secret)",
    )

except requests.exceptions.RequestException as e:
    logger.error(f"Pinterest authentication error: {e}")
    raise AuthenticationError("pinterest", str(e))

    def validate_content(self, content: Dict[str, Any]) -> bool:
    """
    Validate content for posting to Pinterest.

    Args:
    content: Content to validate

    Returns:
    True if content is valid, False otherwise

    Raises:
    ContentValidationError: If content validation fails with specific reason
    """
    # Check if we have a pin
    if "pin" not in content:
    raise ContentValidationError(
    "pinterest", "Pin data is required for Pinterest posts"
    )

    pin = content["pin"]

    # Check if we have a title
    if "title" not in pin:
    raise ContentValidationError(
    "pinterest", "Title is required for Pinterest pins"
    )

    # Check title length (Pinterest's limit is 100 characters)
    if len(pin["title"]) > 100:
    raise ContentValidationError(
    "pinterest",
    f"Title exceeds 100 characters (current: {len(pin['title'])})",
    )

    # Check if we have a description
    if "description" not in pin:
    raise ContentValidationError(
    "pinterest", "Description is required for Pinterest pins"
    )

    # Check description length (Pinterest's limit is 500 characters)
    if len(pin["description"]) > 500:
    raise ContentValidationError(
    "pinterest",
    f"Description exceeds 500 characters (current: {len(pin['description'])})",
    )

    # Check if we have a board ID or name
    if "board_id" not in pin and "board_name" not in pin:
    raise ContentValidationError(
    "pinterest",
    "Either board_id or board_name is required for Pinterest pins",
    )

    # Check if we have media
    if "media" not in pin:
    raise ContentValidationError(
    "pinterest", "Media is required for Pinterest pins"
    )

    # Check media source
    if "source_type" not in pin["media"]:
    raise ContentValidationError(
    "pinterest",
    "Media source_type is required (image_url, image_base64, video_url)",
    )

    source_type = pin["media"]["source_type"]
    if source_type not in ["image_url", "image_base64", "video_url"]:
    raise ContentValidationError(
    "pinterest",
    f"Invalid media source_type: {source_type}. Allowed values: image_url, image_base64, video_url",
    )

    # Check media source data
    if source_type == "image_url" and "url" not in pin["media"]:
    raise ContentValidationError(
    "pinterest", "URL is required for image_url source type"
    )

    if source_type == "image_base64" and "base64" not in pin["media"]:
    raise ContentValidationError(
    "pinterest", "Base64 data is required for image_base64 source type"
    )

    if source_type == "video_url" and "url" not in pin["media"]:
    raise ContentValidationError(
    "pinterest", "URL is required for video_url source type"
    )

    # Check link if present
    if "link" in pin and not pin["link"].startswith(("http://", "https://")):
    raise ContentValidationError(
    "pinterest", "Link must start with http:// or https://"
    )

    return True

    def post_content(
    self,
    content: Dict[str, Any],
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Post content to Pinterest.

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
    # Check if we have an access token (required for posting)
    if not self.access_token:
    raise PostingError(
    "pinterest", "Access token is required for posting pins"
    )

    pin_data = content["pin"]

    # If board_name is provided but not board_id, find or create the board
    if "board_name" in pin_data and "board_id" not in pin_data:
    board_id = self._find_or_create_board(pin_data["board_name"])
    pin_data["board_id"] = board_id

    # Prepare the pin creation data
    create_pin_data = {
    "board_id": pin_data["board_id"],
    "title": pin_data["title"],
    "description": pin_data["description"],
    }

    # Add link if present
    if "link" in pin_data:
    create_pin_data["link"] = pin_data["link"]

    # Add alt text if present
    if "alt_text" in pin_data:
    create_pin_data["alt_text"] = pin_data["alt_text"]

    # Add media data
    media = pin_data["media"]
    source_type = media["source_type"]

    if source_type == "image_url":
    create_pin_data["media_source"] = {
    "source_type": "image_url",
    "url": media["url"],
    }
    elif source_type == "image_base64":
    create_pin_data["media_source"] = {
    "source_type": "image_base64",
    "content_type": media.get("content_type", "image/jpeg"),
    "data": media["base64"],
    }
    elif source_type == "video_url":
    create_pin_data["media_source"] = {
    "source_type": "video_url",
    "cover_image_url": media.get("cover_image_url"),
    "url": media["url"],
    }

    # Create the pin
    response = self.session.post(
    f"{self.api_base_url}/pins", json=create_pin_data
    )
    response.raise_for_status()
    result = response.json()

    # Extract pin ID
    pin_id = result.get("id")

    return {
    "id": pin_id,
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "url": f"https://www.pinterest.com/pin/{pin_id}/",
    "platform_data": result,
    }

except ContentValidationError:
    raise
except requests.exceptions.RequestException as e:
    logger.error(f"Pinterest posting error: {e}")
    raise PostingError("pinterest", str(e))

    def _find_or_create_board(self, board_name: str) -> str:
    """
    Find a board by name or create a new one.

    Args:
    board_name: Name of the board to find or create

    Returns:
    Board ID

    Raises:
    PostingError: If finding or creating the board fails
    """
    try:
    # List all boards
    response = self.session.get(
    f"{self.api_base_url}/boards", params={"page_size": 100}
    )
    response.raise_for_status()
    boards = response.json().get("items", [])

    # Look for a board with the given name
    for board in boards:
    if board["name"].lower() == board_name.lower():
    return board["id"]

    # If not found, create a new board
    response = self.session.post(
    f"{self.api_base_url}/boards", json={"name": board_name}
    )
    response.raise_for_status()
    new_board = response.json()

    return new_board["id"]

except requests.exceptions.RequestException as e:
    logger.error(f"Pinterest board error: {e}")
    raise PostingError(
    "pinterest", f"Failed to find or create board '{board_name}': {str(e)}"
    )

    def schedule_post(
    self,
    content: Dict[str, Any],
    schedule_time: datetime,
    visibility: str = "public",
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Schedule a pin for later publication on Pinterest.

    Args:
    content: Content to post
    schedule_time: Time to publish the pin
    visibility: Visibility setting (public, private, etc.)
    targeting: Optional audience targeting parameters

    Returns:
    Dictionary containing the scheduled pin details and ID

    Raises:
    ContentValidationError: If content validation fails
    SchedulingError: If scheduling fails
    NotSupportedError: If scheduling is not supported
    """
    # Validate content first
    self.validate_content(content)

    try:
    # Check if we have an access token (required for posting)
    if not self.access_token:
    raise SchedulingError(
    "pinterest", "Access token is required for scheduling pins"
    )

    # Note: Pinterest API v5 doesn't directly support scheduling pins
    # In a real implementation, we would use a third-party service or
    # store the pin locally and post it at the scheduled time

    # For demonstration, we'll return a mock scheduled pin
    scheduled_id = (
    f"pinterest_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    return {
    "id": scheduled_id,
    "scheduled_time": schedule_time.isoformat(),
    "status": "scheduled",
    "platform_data": {
    "content": content,
    "visibility": visibility,
    "targeting": targeting,
    },
    }

except ContentValidationError:
    raise
except Exception as e:
    logger.error(f"Pinterest scheduling error: {e}")
    raise SchedulingError("pinterest", str(e))

    def get_post(self, post_id: str) -> Dict[str, Any]:
    """
    Get details of a specific Pinterest pin.

    Args:
    post_id: ID of the pin to retrieve

    Returns:
    Dictionary containing the pin details

    Raises:
    PostNotFoundError: If the pin ID is not found
    """
    try:
    # Get pin details
    response = self.session.get(f"{self.api_base_url}/pins/{post_id}")
    response.raise_for_status()
    result = response.json()

    # Format the response
    return {
    "id": result["id"],
    "title": result.get("title", ""),
    "description": result.get("description", ""),
    "link": result.get("link", ""),
    "created_at": result.get("created_at", ""),
    "board_id": result.get("board_id", ""),
    "board_section_id": result.get("board_section_id", ""),
    "media": {
    "images": result.get("media", {}).get("images", {}),
    "media_type": result.get("media", {}).get("media_type", ""),
    },
    "url": f"https://www.pinterest.com/pin/{result['id']}/",
    "platform_data": result,
    }

except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Pinterest get pin error: {e}")
    raise

    def delete_post(self, post_id: str) -> bool:
    """
    Delete a pin from Pinterest.

    Args:
    post_id: ID of the pin to delete

    Returns:
    True if deleted successfully, False otherwise

    Raises:
    PostNotFoundError: If the pin ID is not found
    DeletionError: If deletion fails
    """
    try:
    # Delete the pin
    response = self.session.delete(f"{self.api_base_url}/pins/{post_id}")
    response.raise_for_status()

    # Pinterest returns 204 No Content on successful deletion
    return response.status_code == 204

except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Pinterest delete pin error: {e}")
    raise DeletionError("pinterest", str(e))

    def get_analytics(
    self,
    post_id: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    """
    Get analytics data from Pinterest.

    Args:
    post_id: Optional ID of a specific pin to get analytics for
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
    "IMPRESSION",
    "SAVE",
    "PIN_CLICK",
    "OUTBOUND_CLICK",
    "VIDEO_VIEW",
    "ENGAGEMENT",
    "ENGAGEMENT_RATE",
    ]

    # Set default date range if not provided
    if not start_date:
    start_date = datetime.now() - timedelta(days=30)
    if not end_date:
    end_date = datetime.now()

    # Format dates for API
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # If post_id is provided, get analytics for a specific pin
    if post_id:
    # Get pin analytics
    response = self.session.get(
    f"{self.api_base_url}/pins/{post_id}/analytics",
    params={
    "start_date": start_date_str,
    "end_date": end_date_str,
    "metric_types": ",".join(metrics),
    },
    )
    response.raise_for_status()
    result = response.json()

    # Format the response
    return {
    "pin_id": post_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": self._format_analytics_data(result),
    "platform_data": result,
    }

    # Otherwise, get user-level analytics
    else:
    # Get user analytics
    response = self.session.get(
    f"{self.api_base_url}/user_account/analytics",
    params={
    "start_date": start_date_str,
    "end_date": end_date_str,
    "metric_types": ",".join(metrics),
    },
    )
    response.raise_for_status()
    result = response.json()

    # Format the response
    return {
    "user_id": self.user_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": self._format_analytics_data(result),
    "platform_data": result,
    }

except requests.exceptions.RequestException as e:
    logger.error(f"Pinterest analytics error: {e}")
    return {
    "error": str(e),
    "pin_id": post_id,
    "user_id": self.user_id,
    "period": {
    "start_date": start_date_str if start_date else None,
    "end_date": end_date_str if end_date else None,
    },
    }

    def _format_analytics_data(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format analytics data from Pinterest API.

    Args:
    analytics_data: Raw analytics data from Pinterest API

    Returns:
    Formatted analytics data
    """
    formatted_data = {}

    # Extract metrics from the response
    metrics = analytics_data.get("metrics", [])

    for metric in metrics:
    metric_type = metric.get("metric_type", "")
    data_points = metric.get("data_points", [])

    if data_points:
    # Sum up the values for the metric
    total = sum(point.get("value", 0) for point in data_points)
    formatted_data[metric_type.lower()] = total

    return formatted_data

    def get_audience_insights(
    self,
    metrics: Optional[List[str]] = None,
    segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Get audience insights from Pinterest.

    Args:
    metrics: Optional list of specific metrics to retrieve
    segment: Optional audience segment to get insights for

    Returns:
    Dictionary containing the audience insights
    """
    try:
    # Set default metrics if not provided
    if not metrics:
    metrics = ["demographics", "interests", "locations"]

    # Note: Pinterest API v5 doesn't directly support audience insights
    # In a real implementation, we would use the Pinterest Analytics API

    # For demonstration, we'll return mock audience insights data
    return {
    "user_id": self.user_id,
    "segment": segment or "all_audience",
    "demographics": {
    "age_groups": {
    "18-24": 0.15,
    "25-34": 0.35,
    "35-44": 0.25,
    "45-54": 0.15,
    "55-64": 0.07,
    "65+": 0.03,
    },
    "gender": {"female": 0.75, "male": 0.24, "other": 0.01},
    },
    "interests": [
    {"category": "Home Decor", "score": 0.85},
    {"category": "DIY & Crafts", "score": 0.78},
    {"category": "Food & Drink", "score": 0.65},
    {"category": "Fashion", "score": 0.60},
    {"category": "Travel", "score": 0.55},
    ],
    "locations": {
    "countries": {
    "United States": 0.45,
    "United Kingdom": 0.12,
    "Canada": 0.08,
    "Australia": 0.05,
    "Germany": 0.04,
    "France": 0.03,
    "Other": 0.23,
    },
    "cities": [
    {
    "name": "New York",
    "country": "United States",
    "percentage": 0.08,
    },
    {
    "name": "Los Angeles",
    "country": "United States",
    "percentage": 0.06,
    },
    {
    "name": "London",
    "country": "United Kingdom",
    "percentage": 0.05,
    },
    {
    "name": "Chicago",
    "country": "United States",
    "percentage": 0.04,
    },
    {"name": "Toronto", "country": "Canada", "percentage": 0.03},
    ],
    },
    "devices": {"mobile": 0.70, "desktop": 0.25, "tablet": 0.05},
    "activity": {
    "peak_times": {
    "weekdays": {
    "morning": 0.15,
    "afternoon": 0.25,
    "evening": 0.45,
    "night": 0.15,
    },
    "weekends": {
    "morning": 0.10,
    "afternoon": 0.30,
    "evening": 0.40,
    "night": 0.20,
    },
    }
    },
    }

except Exception as e:
    logger.error(f"Pinterest audience insights error: {e}")
    return {
    "error": str(e),
    "user_id": self.user_id,
    "segment": segment or "all_audience",
    }