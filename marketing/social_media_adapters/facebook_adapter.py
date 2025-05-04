"""
"""
Facebook adapter for social media integration.
Facebook adapter for social media integration.


This module provides an adapter for connecting to the Facebook Graph API for posting content,
This module provides an adapter for connecting to the Facebook Graph API for posting content,
retrieving analytics, and managing social media campaigns.
retrieving analytics, and managing social media campaigns.
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




class FacebookAdapter(BaseSocialMediaAdapter):
    class FacebookAdapter(BaseSocialMediaAdapter):
    """
    """
    Adapter for Facebook platform integration.
    Adapter for Facebook platform integration.


    This class implements the BaseSocialMediaAdapter interface for Facebook,
    This class implements the BaseSocialMediaAdapter interface for Facebook,
    providing methods for posting content, retrieving analytics, and managing
    providing methods for posting content, retrieving analytics, and managing
    Facebook campaigns.
    Facebook campaigns.
    """
    """


    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    """
    """
    Initialize the Facebook adapter.
    Initialize the Facebook adapter.


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
    "https://graph.facebook.com/v18.0"  # Using latest version as of 2023
    "https://graph.facebook.com/v18.0"  # Using latest version as of 2023
    )
    )
    self.app_id = self.credentials.get("app_id")
    self.app_id = self.credentials.get("app_id")
    self.app_secret = self.credentials.get("app_secret")
    self.app_secret = self.credentials.get("app_secret")
    self.access_token = self.credentials.get("access_token")
    self.access_token = self.credentials.get("access_token")
    self.page_id = self.credentials.get("page_id")
    self.page_id = self.credentials.get("page_id")
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
    Authenticate with the Facebook Graph API.
    Authenticate with the Facebook Graph API.


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
    if self.access_token:
    if self.access_token:
    # Check if the token is valid by getting basic account info
    # Check if the token is valid by getting basic account info
    response = self.session.get(f"{self.api_base_url}/me")
    response = self.session.get(f"{self.api_base_url}/me")
    response.raise_for_status()
    response.raise_for_status()
    user_data = response.json()
    user_data = response.json()


    # If we have a page ID, get page details
    # If we have a page ID, get page details
    page_data = {}
    page_data = {}
    if self.page_id:
    if self.page_id:
    page_response = self.session.get(
    page_response = self.session.get(
    f"{self.api_base_url}/{self.page_id}"
    f"{self.api_base_url}/{self.page_id}"
    )
    )
    if page_response.status_code == 200:
    if page_response.status_code == 200:
    page_data = page_response.json()
    page_data = page_response.json()


    return {
    return {
    "authenticated": True,
    "authenticated": True,
    "user_id": user_data.get("id"),
    "user_id": user_data.get("id"),
    "name": user_data.get("name"),
    "name": user_data.get("name"),
    "page_id": self.page_id,
    "page_id": self.page_id,
    "page_name": page_data.get("name") if page_data else None,
    "page_name": page_data.get("name") if page_data else None,
    }
    }


    # If we have app ID and secret but no access token, get an app token
    # If we have app ID and secret but no access token, get an app token
    # Note: App tokens have limited permissions, user tokens are preferred
    # Note: App tokens have limited permissions, user tokens are preferred
    elif self.app_id and self.app_secret:
    elif self.app_id and self.app_secret:
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/oauth/access_token",
    f"{self.api_base_url}/oauth/access_token",
    params={
    params={
    "client_id": self.app_id,
    "client_id": self.app_id,
    "client_secret": self.app_secret,
    "client_secret": self.app_secret,
    "grant_type": "client_credentials",
    "grant_type": "client_credentials",
    },
    },
    )
    )
    response.raise_for_status()
    response.raise_for_status()
    token_data = response.json()
    token_data = response.json()


    # Update session with new access token
    # Update session with new access token
    self.access_token = token_data.get("access_token")
    self.access_token = token_data.get("access_token")
    self.session.params = {"access_token": self.access_token}
    self.session.params = {"access_token": self.access_token}
    self._connected = True
    self._connected = True


    return {
    return {
    "authenticated": True,
    "authenticated": True,
    "access_token": self.access_token,
    "access_token": self.access_token,
    "token_type": "app_token",
    "token_type": "app_token",
    }
    }


    else:
    else:
    raise AuthenticationError(
    raise AuthenticationError(
    "facebook",
    "facebook",
    "Missing required credentials (access_token or app_id and app_secret)",
    "Missing required credentials (access_token or app_id and app_secret)",
    )
    )


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Facebook authentication error: {e}")
    logger.error(f"Facebook authentication error: {e}")
    raise AuthenticationError("facebook", str(e))
    raise AuthenticationError("facebook", str(e))


    def validate_content(self, content: Dict[str, Any]) -> bool:
    def validate_content(self, content: Dict[str, Any]) -> bool:
    """
    """
    Validate content for posting to Facebook.
    Validate content for posting to Facebook.


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
    if not any(key in content for key in ["message", "link", "photo", "video"]):
    if not any(key in content for key in ["message", "link", "photo", "video"]):
    raise ContentValidationError(
    raise ContentValidationError(
    "facebook",
    "facebook",
    "At least one content type (message, link, photo, video) is required",
    "At least one content type (message, link, photo, video) is required",
    )
    )


    # Check message length if present (Facebook's limit is 63,206 characters)
    # Check message length if present (Facebook's limit is 63,206 characters)
    if "message" in content and len(content["message"]) > 63206:
    if "message" in content and len(content["message"]) > 63206:
    raise ContentValidationError(
    raise ContentValidationError(
    "facebook",
    "facebook",
    f"Message exceeds 63,206 characters (current: {len(content['message'])})",
    f"Message exceeds 63,206 characters (current: {len(content['message'])})",
    )
    )


    # Check link if present
    # Check link if present
    if "link" in content:
    if "link" in content:
    if not content["link"].startswith(("http://", "https://")):
    if not content["link"].startswith(("http://", "https://")):
    raise ContentValidationError(
    raise ContentValidationError(
    "facebook", "Link must start with http:// or https://"
    "facebook", "Link must start with http:// or https://"
    )
    )


    # Check photo if present
    # Check photo if present
    if "photo" in content:
    if "photo" in content:
    if "url" not in content["photo"] and "source" not in content["photo"]:
    if "url" not in content["photo"] and "source" not in content["photo"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "facebook", "Photo must have either a URL or source (base64 data)"
    "facebook", "Photo must have either a URL or source (base64 data)"
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
    "facebook", "Video must have either a URL or source (file path)"
    "facebook", "Video must have either a URL or source (file path)"
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
    Post content to Facebook.
    Post content to Facebook.


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
    # Check if we have a page ID (required for posting)
    # Check if we have a page ID (required for posting)
    if not self.page_id:
    if not self.page_id:
    raise PostingError("facebook", "Page ID is required for posting")
    raise PostingError("facebook", "Page ID is required for posting")


    # Prepare post data
    # Prepare post data
    post_data = {}
    post_data = {}


    # Add message if present
    # Add message if present
    if "message" in content:
    if "message" in content:
    post_data["message"] = content["message"]
    post_data["message"] = content["message"]


    # Add link if present
    # Add link if present
    if "link" in content:
    if "link" in content:
    post_data["link"] = content["link"]
    post_data["link"] = content["link"]


    # Add privacy settings based on visibility
    # Add privacy settings based on visibility
    if visibility == "private":
    if visibility == "private":
    post_data["privacy"] = {"value": "SELF"}
    post_data["privacy"] = {"value": "SELF"}
    elif visibility == "friends" or visibility == "followers":
    elif visibility == "friends" or visibility == "followers":
    post_data["privacy"] = {"value": "ALL_FRIENDS"}
    post_data["privacy"] = {"value": "ALL_FRIENDS"}
    else:  # public
    else:  # public
    post_data["privacy"] = {"value": "EVERYONE"}
    post_data["privacy"] = {"value": "EVERYONE"}


    # Add targeting if present
    # Add targeting if present
    if targeting:
    if targeting:
    post_data["targeting"] = targeting
    post_data["targeting"] = targeting


    # Determine the endpoint based on content type
    # Determine the endpoint based on content type
    endpoint = f"{self.api_base_url}/{self.page_id}/feed"
    endpoint = f"{self.api_base_url}/{self.page_id}/feed"


    # Handle photo posts
    # Handle photo posts
    if "photo" in content:
    if "photo" in content:
    endpoint = f"{self.api_base_url}/{self.page_id}/photos"
    endpoint = f"{self.api_base_url}/{self.page_id}/photos"
    if "url" in content["photo"]:
    if "url" in content["photo"]:
    post_data["url"] = content["photo"]["url"]
    post_data["url"] = content["photo"]["url"]
    elif "source" in content["photo"]:
    elif "source" in content["photo"]:
    # For file uploads, we'd need to handle multipart/form-data
    # For file uploads, we'd need to handle multipart/form-data
    # This is simplified for demonstration
    # This is simplified for demonstration
    post_data["source"] = content["photo"]["source"]
    post_data["source"] = content["photo"]["source"]


    # Handle video posts
    # Handle video posts
    elif "video" in content:
    elif "video" in content:
    endpoint = f"{self.api_base_url}/{self.page_id}/videos"
    endpoint = f"{self.api_base_url}/{self.page_id}/videos"
    if "url" in content["video"]:
    if "url" in content["video"]:
    post_data["file_url"] = content["video"]["url"]
    post_data["file_url"] = content["video"]["url"]
    elif "source" in content["video"]:
    elif "source" in content["video"]:
    # For file uploads, we'd need to handle multipart/form-data
    # For file uploads, we'd need to handle multipart/form-data
    # This is simplified for demonstration
    # This is simplified for demonstration
    post_data["source"] = content["video"]["source"]
    post_data["source"] = content["video"]["source"]


    # Post the content
    # Post the content
    response = self.session.post(endpoint, data=post_data)
    response = self.session.post(endpoint, data=post_data)
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Extract post ID
    # Extract post ID
    post_id = result.get("id")
    post_id = result.get("id")


    # Get the post URL
    # Get the post URL
    post_url = f"https://facebook.com/{post_id}"
    post_url = f"https://facebook.com/{post_id}"


    return {"id": post_id, "platform_data": result, "url": post_url}
    return {"id": post_id, "platform_data": result, "url": post_url}


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Facebook posting error: {e}")
    logger.error(f"Facebook posting error: {e}")
    raise PostingError("facebook", str(e))
    raise PostingError("facebook", str(e))


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
    Schedule a post for later publication on Facebook.
    Schedule a post for later publication on Facebook.


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
    """
    """
    # Validate content first
    # Validate content first
    self.validate_content(content)
    self.validate_content(content)


    try:
    try:
    # Check if we have a page ID (required for posting)
    # Check if we have a page ID (required for posting)
    if not self.page_id:
    if not self.page_id:
    raise SchedulingError(
    raise SchedulingError(
    "facebook", "Page ID is required for scheduling posts"
    "facebook", "Page ID is required for scheduling posts"
    )
    )


    # Prepare post data
    # Prepare post data
    post_data = {}
    post_data = {}


    # Add message if present
    # Add message if present
    if "message" in content:
    if "message" in content:
    post_data["message"] = content["message"]
    post_data["message"] = content["message"]


    # Add link if present
    # Add link if present
    if "link" in content:
    if "link" in content:
    post_data["link"] = content["link"]
    post_data["link"] = content["link"]


    # Add privacy settings based on visibility
    # Add privacy settings based on visibility
    if visibility == "private":
    if visibility == "private":
    post_data["privacy"] = {"value": "SELF"}
    post_data["privacy"] = {"value": "SELF"}
    elif visibility == "friends" or visibility == "followers":
    elif visibility == "friends" or visibility == "followers":
    post_data["privacy"] = {"value": "ALL_FRIENDS"}
    post_data["privacy"] = {"value": "ALL_FRIENDS"}
    else:  # public
    else:  # public
    post_data["privacy"] = {"value": "EVERYONE"}
    post_data["privacy"] = {"value": "EVERYONE"}


    # Add targeting if present
    # Add targeting if present
    if targeting:
    if targeting:
    post_data["targeting"] = targeting
    post_data["targeting"] = targeting


    # Add scheduled publish time
    # Add scheduled publish time
    post_data["scheduled_publish_time"] = int(schedule_time.timestamp())
    post_data["scheduled_publish_time"] = int(schedule_time.timestamp())
    post_data["published"] = False
    post_data["published"] = False


    # Determine the endpoint based on content type
    # Determine the endpoint based on content type
    endpoint = f"{self.api_base_url}/{self.page_id}/feed"
    endpoint = f"{self.api_base_url}/{self.page_id}/feed"


    # Handle photo posts
    # Handle photo posts
    if "photo" in content:
    if "photo" in content:
    endpoint = f"{self.api_base_url}/{self.page_id}/photos"
    endpoint = f"{self.api_base_url}/{self.page_id}/photos"
    if "url" in content["photo"]:
    if "url" in content["photo"]:
    post_data["url"] = content["photo"]["url"]
    post_data["url"] = content["photo"]["url"]
    elif "source" in content["photo"]:
    elif "source" in content["photo"]:
    # For file uploads, we'd need to handle multipart/form-data
    # For file uploads, we'd need to handle multipart/form-data
    # This is simplified for demonstration
    # This is simplified for demonstration
    post_data["source"] = content["photo"]["source"]
    post_data["source"] = content["photo"]["source"]


    # Handle video posts
    # Handle video posts
    elif "video" in content:
    elif "video" in content:
    endpoint = f"{self.api_base_url}/{self.page_id}/videos"
    endpoint = f"{self.api_base_url}/{self.page_id}/videos"
    if "url" in content["video"]:
    if "url" in content["video"]:
    post_data["file_url"] = content["video"]["url"]
    post_data["file_url"] = content["video"]["url"]
    elif "source" in content["video"]:
    elif "source" in content["video"]:
    # For file uploads, we'd need to handle multipart/form-data
    # For file uploads, we'd need to handle multipart/form-data
    # This is simplified for demonstration
    # This is simplified for demonstration
    post_data["source"] = content["video"]["source"]
    post_data["source"] = content["video"]["source"]


    # Schedule the post
    # Schedule the post
    response = self.session.post(endpoint, data=post_data)
    response = self.session.post(endpoint, data=post_data)
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Extract post ID
    # Extract post ID
    post_id = result.get("id")
    post_id = result.get("id")


    return {
    return {
    "id": post_id,
    "id": post_id,
    "scheduled_time": schedule_time.isoformat(),
    "scheduled_time": schedule_time.isoformat(),
    "status": "scheduled",
    "status": "scheduled",
    "platform_data": result,
    "platform_data": result,
    }
    }


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Facebook scheduling error: {e}")
    logger.error(f"Facebook scheduling error: {e}")
    raise SchedulingError("facebook", str(e))
    raise SchedulingError("facebook", str(e))


    def get_post(self, post_id: str) -> Dict[str, Any]:
    def get_post(self, post_id: str) -> Dict[str, Any]:
    """
    """
    Get details of a specific Facebook post.
    Get details of a specific Facebook post.


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
    "fields": "id,message,created_time,permalink_url,type,attachments,insights.metric(post_impressions,post_engagements,post_reactions_by_type)"
    "fields": "id,message,created_time,permalink_url,type,attachments,insights.metric(post_impressions,post_engagements,post_reactions_by_type)"
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
    return {
    return {
    "id": result.get("id"),
    "id": result.get("id"),
    "text": result.get("message"),
    "text": result.get("message"),
    "created_at": result.get("created_time"),
    "created_at": result.get("created_time"),
    "url": result.get("permalink_url"),
    "url": result.get("permalink_url"),
    "type": result.get("type"),
    "type": result.get("type"),
    "attachments": result.get("attachments", {}).get("data", []),
    "attachments": result.get("attachments", {}).get("data", []),
    "metrics": self._extract_insights(result.get("insights", {})),
    "metrics": self._extract_insights(result.get("insights", {})),
    "platform_data": result,
    "platform_data": result,
    }
    }


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Facebook get post error: {e}")
    logger.error(f"Facebook get post error: {e}")
    raise
    raise


    def delete_post(self, post_id: str) -> bool:
    def delete_post(self, post_id: str) -> bool:
    """
    """
    Delete a post from Facebook.
    Delete a post from Facebook.


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
    raise DeletionError("facebook", "Failed to delete post")
    raise DeletionError("facebook", "Failed to delete post")


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"Facebook delete post error: {e}")
    logger.error(f"Facebook delete post error: {e}")
    raise DeletionError("facebook", str(e))
    raise DeletionError("facebook", str(e))


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
    Get analytics data from Facebook.
    Get analytics data from Facebook.


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
    "page_impressions",
    "page_impressions",
    "page_engaged_users",
    "page_engaged_users",
    "page_post_engagements",
    "page_post_engagements",
    "page_fans",
    "page_fans",
    "page_fan_adds",
    "page_fan_adds",
    "page_views_total",
    "page_views_total",
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
    params={
    params={
    "metric": "post_impressions,post_engagements,post_reactions_by_type"
    "metric": "post_impressions,post_engagements,post_reactions_by_type"
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
    "post_id": post_id,
    "post_id": post_id,
    "metrics": self._extract_insights(result),
    "metrics": self._extract_insights(result),
    }
    }


    return analytics
    return analytics


    # Otherwise, get page-level analytics
    # Otherwise, get page-level analytics
    elif self.page_id:
    elif self.page_id:
    # Get page insights
    # Get page insights
    response = self.session.get(
    response = self.session.get(
    f"{self.api_base_url}/{self.page_id}/insights",
    f"{self.api_base_url}/{self.page_id}/insights",
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
    "page_id": self.page_id,
    "page_id": self.page_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": self._extract_insights(result),
    "metrics": self._extract_insights(result),
    }
    }


    return analytics
    return analytics


    else:
    else:
    return {"error": "No page ID or post ID provided for analytics"}
    return {"error": "No page ID or post ID provided for analytics"}


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Facebook analytics error: {e}")
    logger.error(f"Facebook analytics error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "post_id": post_id,
    "post_id": post_id,
    "page_id": self.page_id,
    "page_id": self.page_id,
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
    Get audience insights from Facebook.
    Get audience insights from Facebook.


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
    metrics = ["demographics", "interests", "page_likes"]
    metrics = ["demographics", "interests", "page_likes"]


    # Check if we have a page ID
    # Check if we have a page ID
    if not self.page_id:
    if not self.page_id:
    return {"error": "Page ID is required for audience insights"}
    return {"error": "Page ID is required for audience insights"}


    # Get audience insights
    # Get audience insights
    # Note: Facebook's Audience Insights API is limited and requires special permissions
    # Note: Facebook's Audience Insights API is limited and requires special permissions
    # For demonstration, we'll return mock audience insights data
    # For demonstration, we'll return mock audience insights data


    return {
    return {
    "page_id": self.page_id,
    "page_id": self.page_id,
    "segment": segment or "all_fans",
    "segment": segment or "all_fans",
    "demographics": {
    "demographics": {
    "age_gender": {
    "age_gender": {
    "F.13-17": 0.02,
    "F.13-17": 0.02,
    "F.18-24": 0.12,
    "F.18-24": 0.12,
    "F.25-34": 0.18,
    "F.25-34": 0.18,
    "F.35-44": 0.08,
    "F.35-44": 0.08,
    "F.45-54": 0.05,
    "F.45-54": 0.05,
    "F.55+": 0.03,
    "F.55+": 0.03,
    "M.13-17": 0.03,
    "M.13-17": 0.03,
    "M.18-24": 0.15,
    "M.18-24": 0.15,
    "M.25-34": 0.22,
    "M.25-34": 0.22,
    "M.35-44": 0.07,
    "M.35-44": 0.07,
    "M.45-54": 0.04,
    "M.45-54": 0.04,
    "M.55+": 0.01,
    "M.55+": 0.01,
    },
    },
    "location": {
    "location": {
    "United States": 0.4,
    "United States": 0.4,
    "United Kingdom": 0.12,
    "United Kingdom": 0.12,
    "Canada": 0.08,
    "Canada": 0.08,
    "Australia": 0.05,
    "Australia": 0.05,
    "Germany": 0.04,
    "Germany": 0.04,
    "France": 0.03,
    "France": 0.03,
    "Other": 0.28,
    "Other": 0.28,
    },
    },
    "language": {
    "language": {
    "English": 0.75,
    "English": 0.75,
    "Spanish": 0.08,
    "Spanish": 0.08,
    "French": 0.05,
    "French": 0.05,
    "German": 0.04,
    "German": 0.04,
    "Other": 0.08,
    "Other": 0.08,
    },
    },
    },
    },
    "interests": [
    "interests": [
    {"category": "Technology", "score": 0.82},
    {"category": "Technology", "score": 0.82},
    {"category": "Entertainment", "score": 0.65},
    {"category": "Entertainment", "score": 0.65},
    {"category": "Shopping", "score": 0.58},
    {"category": "Shopping", "score": 0.58},
    {"category": "Travel", "score": 0.45},
    {"category": "Travel", "score": 0.45},
    {"category": "Fitness", "score": 0.38},
    {"category": "Fitness", "score": 0.38},
    ],
    ],
    "page_likes": [
    "page_likes": [
    {"name": "Technology News", "category": "News", "affinity": 0.85},
    {"name": "Technology News", "category": "News", "affinity": 0.85},
    {
    {
    "name": "Gadget Reviews",
    "name": "Gadget Reviews",
    "category": "Technology",
    "category": "Technology",
    "affinity": 0.78,
    "affinity": 0.78,
    },
    },
    {
    {
    "name": "Digital Marketing",
    "name": "Digital Marketing",
    "category": "Business",
    "category": "Business",
    "affinity": 0.72,
    "affinity": 0.72,
    },
    },
    {
    {
    "name": "Startup Culture",
    "name": "Startup Culture",
    "category": "Business",
    "category": "Business",
    "affinity": 0.65,
    "affinity": 0.65,
    },
    },
    {
    {
    "name": "Travel Destinations",
    "name": "Travel Destinations",
    "category": "Travel",
    "category": "Travel",
    "affinity": 0.45,
    "affinity": 0.45,
    },
    },
    ],
    ],
    "activity": {
    "activity": {
    "frequency": {
    "frequency": {
    "daily_active": 0.25,
    "daily_active": 0.25,
    "weekly_active": 0.45,
    "weekly_active": 0.45,
    "monthly_active": 0.3,
    "monthly_active": 0.3,
    },
    },
    "devices": {"mobile": 0.75, "desktop": 0.25},
    "devices": {"mobile": 0.75, "desktop": 0.25},
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"Facebook audience insights error: {e}")
    logger.error(f"Facebook audience insights error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "page_id": self.page_id,
    "page_id": self.page_id,
    "segment": segment or "all_fans",
    "segment": segment or "all_fans",
    }
    }


    def _extract_insights(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
    def _extract_insights(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Extract metrics from Facebook insights data.
    Extract metrics from Facebook insights data.


    Args:
    Args:
    insights_data: Raw insights data from Facebook API
    insights_data: Raw insights data from Facebook API


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
    # For metrics like reactions_by_type
    # For metrics like reactions_by_type
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