"""
"""
LinkedIn adapter for social media integration.
LinkedIn adapter for social media integration.


This module provides an adapter for connecting to the LinkedIn API for posting content,
This module provides an adapter for connecting to the LinkedIn API for posting content,
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




class LinkedInAdapter(BaseSocialMediaAdapter):
    class LinkedInAdapter(BaseSocialMediaAdapter):
    """
    """
    Adapter for LinkedIn platform integration.
    Adapter for LinkedIn platform integration.


    This class implements the BaseSocialMediaAdapter interface for LinkedIn,
    This class implements the BaseSocialMediaAdapter interface for LinkedIn,
    providing methods for posting content, retrieving analytics, and managing
    providing methods for posting content, retrieving analytics, and managing
    LinkedIn campaigns.
    LinkedIn campaigns.
    """
    """


    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
    """
    """
    Initialize the LinkedIn adapter.
    Initialize the LinkedIn adapter.


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
    self.api_base_url = "https://api.linkedin.com/v2"
    self.api_base_url = "https://api.linkedin.com/v2"
    self.access_token = self.credentials.get("access_token")
    self.access_token = self.credentials.get("access_token")
    self.client_id = self.credentials.get("client_id")
    self.client_id = self.credentials.get("client_id")
    self.client_secret = self.credentials.get("client_secret")
    self.client_secret = self.credentials.get("client_secret")
    self.organization_id = self.credentials.get(
    self.organization_id = self.credentials.get(
    "organization_id"
    "organization_id"
    )  # For company pages
    )  # For company pages
    self.person_id = self.credentials.get("person_id")  # For personal profiles
    self.person_id = self.credentials.get("person_id")  # For personal profiles
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
    "X-Restli-Protocol-Version": "2.0.0",
    "X-Restli-Protocol-Version": "2.0.0",
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
    Authenticate with the LinkedIn API.
    Authenticate with the LinkedIn API.


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
    # Check if the token is valid by getting basic profile info
    # Check if the token is valid by getting basic profile info
    response = self.session.get(f"{self.api_base_url}/me")
    response = self.session.get(f"{self.api_base_url}/me")
    response.raise_for_status()
    response.raise_for_status()
    profile_data = response.json()
    profile_data = response.json()


    return {
    return {
    "authenticated": True,
    "authenticated": True,
    "profile_id": profile_data.get("id"),
    "profile_id": profile_data.get("id"),
    "first_name": profile_data.get("localizedFirstName"),
    "first_name": profile_data.get("localizedFirstName"),
    "last_name": profile_data.get("localizedLastName"),
    "last_name": profile_data.get("localizedLastName"),
    }
    }


    # If we have client ID and secret but no access token, we'd need to implement OAuth flow
    # If we have client ID and secret but no access token, we'd need to implement OAuth flow
    # This would typically be handled by a web application, not directly in this adapter
    # This would typically be handled by a web application, not directly in this adapter
    elif self.client_id and self.client_secret:
    elif self.client_id and self.client_secret:
    raise AuthenticationError(
    raise AuthenticationError(
    "linkedin",
    "linkedin",
    "OAuth flow not implemented in this adapter. Please obtain an access token externally.",
    "OAuth flow not implemented in this adapter. Please obtain an access token externally.",
    )
    )


    else:
    else:
    raise AuthenticationError(
    raise AuthenticationError(
    "linkedin",
    "linkedin",
    "Missing required credentials (access_token or client_id and client_secret)",
    "Missing required credentials (access_token or client_id and client_secret)",
    )
    )


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"LinkedIn authentication error: {e}")
    logger.error(f"LinkedIn authentication error: {e}")
    raise AuthenticationError("linkedin", str(e))
    raise AuthenticationError("linkedin", str(e))


    def validate_content(self, content: Dict[str, Any]) -> bool:
    def validate_content(self, content: Dict[str, Any]) -> bool:
    """
    """
    Validate content for posting to LinkedIn.
    Validate content for posting to LinkedIn.


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
    if not any(
    if not any(
    key in content for key in ["text", "article", "image", "video", "document"]
    key in content for key in ["text", "article", "image", "video", "document"]
    ):
    ):
    raise ContentValidationError(
    raise ContentValidationError(
    "linkedin",
    "linkedin",
    "At least one content type (text, article, image, video, document) is required",
    "At least one content type (text, article, image, video, document) is required",
    )
    )


    # Check text length if present (LinkedIn's limit is 3,000 characters)
    # Check text length if present (LinkedIn's limit is 3,000 characters)
    if "text" in content and len(content["text"]) > 3000:
    if "text" in content and len(content["text"]) > 3000:
    raise ContentValidationError(
    raise ContentValidationError(
    "linkedin",
    "linkedin",
    f"Text exceeds 3,000 characters (current: {len(content['text'])})",
    f"Text exceeds 3,000 characters (current: {len(content['text'])})",
    )
    )


    # Check article if present
    # Check article if present
    if "article" in content:
    if "article" in content:
    if "title" not in content["article"]:
    if "title" not in content["article"]:
    raise ContentValidationError("linkedin", "Article must have a title")
    raise ContentValidationError("linkedin", "Article must have a title")


    if "url" not in content["article"]:
    if "url" not in content["article"]:
    raise ContentValidationError("linkedin", "Article must have a URL")
    raise ContentValidationError("linkedin", "Article must have a URL")


    if len(content["article"]["title"]) > 150:
    if len(content["article"]["title"]) > 150:
    raise ContentValidationError(
    raise ContentValidationError(
    "linkedin",
    "linkedin",
    f"Article title exceeds 150 characters (current: {len(content['article']['title'])})",
    f"Article title exceeds 150 characters (current: {len(content['article']['title'])})",
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
    "linkedin", "Image must have either a URL or source (base64 data)"
    "linkedin", "Image must have either a URL or source (base64 data)"
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
    "linkedin", "Video must have either a URL or source (file path)"
    "linkedin", "Video must have either a URL or source (file path)"
    )
    )


    # Check document if present
    # Check document if present
    if "document" in content:
    if "document" in content:
    if "url" not in content["document"] and "source" not in content["document"]:
    if "url" not in content["document"] and "source" not in content["document"]:
    raise ContentValidationError(
    raise ContentValidationError(
    "linkedin", "Document must have either a URL or source (file path)"
    "linkedin", "Document must have either a URL or source (file path)"
    )
    )


    if "title" not in content["document"]:
    if "title" not in content["document"]:
    raise ContentValidationError("linkedin", "Document must have a title")
    raise ContentValidationError("linkedin", "Document must have a title")


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
    Post content to LinkedIn.
    Post content to LinkedIn.


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
    # Determine if we're posting as a person or organization
    # Determine if we're posting as a person or organization
    author = self._get_author_urn()
    author = self._get_author_urn()


    # Prepare the base post data
    # Prepare the base post data
    post_data = {
    post_data = {
    "author": author,
    "author": author,
    "lifecycleState": "PUBLISHED",
    "lifecycleState": "PUBLISHED",
    "visibility": self._get_visibility_setting(visibility),
    "visibility": self._get_visibility_setting(visibility),
    }
    }


    # Add specific content based on type
    # Add specific content based on type
    if "text" in content:
    if "text" in content:
    return self._post_text(content, post_data, targeting)
    return self._post_text(content, post_data, targeting)
    elif "article" in content:
    elif "article" in content:
    return self._post_article(content, post_data, targeting)
    return self._post_article(content, post_data, targeting)
    elif "image" in content:
    elif "image" in content:
    return self._post_image(content, post_data, targeting)
    return self._post_image(content, post_data, targeting)
    elif "video" in content:
    elif "video" in content:
    return self._post_video(content, post_data, targeting)
    return self._post_video(content, post_data, targeting)
    elif "document" in content:
    elif "document" in content:
    return self._post_document(content, post_data, targeting)
    return self._post_document(content, post_data, targeting)
    else:
    else:
    raise ContentValidationError("linkedin", "No valid content type found")
    raise ContentValidationError("linkedin", "No valid content type found")


except ContentValidationError:
except ContentValidationError:
    raise
    raise
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"LinkedIn posting error: {e}")
    logger.error(f"LinkedIn posting error: {e}")
    raise PostingError("linkedin", str(e))
    raise PostingError("linkedin", str(e))


    def _get_author_urn(self) -> str:
    def _get_author_urn(self) -> str:
    """
    """
    Get the URN for the post author.
    Get the URN for the post author.


    Returns:
    Returns:
    URN string for the author
    URN string for the author


    Raises:
    Raises:
    PostingError: If neither organization ID nor person ID is available
    PostingError: If neither organization ID nor person ID is available
    """
    """
    if self.organization_id:
    if self.organization_id:
    return f"urn:li:organization:{self.organization_id}"
    return f"urn:li:organization:{self.organization_id}"
    elif self.person_id:
    elif self.person_id:
    return f"urn:li:person:{self.person_id}"
    return f"urn:li:person:{self.person_id}"
    else:
    else:
    raise PostingError(
    raise PostingError(
    "linkedin",
    "linkedin",
    "Neither organization ID nor person ID is available for posting",
    "Neither organization ID nor person ID is available for posting",
    )
    )


    def _get_visibility_setting(self, visibility: str) -> Dict[str, str]:
    def _get_visibility_setting(self, visibility: str) -> Dict[str, str]:
    """
    """
    Get the visibility setting for a post.
    Get the visibility setting for a post.


    Args:
    Args:
    visibility: Visibility setting (public, private, connections)
    visibility: Visibility setting (public, private, connections)


    Returns:
    Returns:
    Dictionary with visibility settings
    Dictionary with visibility settings
    """
    """
    if visibility == "public":
    if visibility == "public":
    return {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    return {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    elif visibility == "connections":
    elif visibility == "connections":
    return {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"}
    return {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"}
    else:  # private
    else:  # private
    return {"com.linkedin.ugc.MemberNetworkVisibility": "NONE"}
    return {"com.linkedin.ugc.MemberNetworkVisibility": "NONE"}


    def _post_text(
    def _post_text(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    post_data: Dict[str, Any],
    post_data: Dict[str, Any],
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post text content to LinkedIn.
    Post text content to LinkedIn.


    Args:
    Args:
    content: Content to post
    content: Content to post
    post_data: Base post data
    post_data: Base post data
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


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
    # Add text specific content
    # Add text specific content
    post_data["specificContent"] = {
    post_data["specificContent"] = {
    "com.linkedin.ugc.ShareContent": {
    "com.linkedin.ugc.ShareContent": {
    "shareCommentary": {"text": content["text"]},
    "shareCommentary": {"text": content["text"]},
    "shareMediaCategory": "NONE",
    "shareMediaCategory": "NONE",
    }
    }
    }
    }


    # Add targeting if provided
    # Add targeting if provided
    if targeting:
    if targeting:
    post_data["targetAudience"] = targeting
    post_data["targetAudience"] = targeting


    # Post to LinkedIn
    # Post to LinkedIn
    response = self.session.post(
    response = self.session.post(
    f"{self.api_base_url}/ugcPosts", json=post_data
    f"{self.api_base_url}/ugcPosts", json=post_data
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    # LinkedIn returns the post URN in the response headers
    # LinkedIn returns the post URN in the response headers
    post_urn = response.headers.get("x-restli-id")
    post_urn = response.headers.get("x-restli-id")


    # Extract the post ID from the URN
    # Extract the post ID from the URN
    post_id = post_urn.split(":")[-1] if post_urn else None
    post_id = post_urn.split(":")[-1] if post_urn else None


    return {
    return {
    "id": post_id,
    "id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {"post_urn": post_urn},
    "platform_data": {"post_urn": post_urn},
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn text posting error: {e}")
    logger.error(f"LinkedIn text posting error: {e}")
    raise PostingError("linkedin", str(e))
    raise PostingError("linkedin", str(e))


    def _post_article(
    def _post_article(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    post_data: Dict[str, Any],
    post_data: Dict[str, Any],
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post an article to LinkedIn.
    Post an article to LinkedIn.


    Args:
    Args:
    content: Content to post
    content: Content to post
    post_data: Base post data
    post_data: Base post data
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


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
    article = content["article"]
    article = content["article"]


    # Add article specific content
    # Add article specific content
    post_data["specificContent"] = {
    post_data["specificContent"] = {
    "com.linkedin.ugc.ShareContent": {
    "com.linkedin.ugc.ShareContent": {
    "shareCommentary": {"text": content.get("text", "")},
    "shareCommentary": {"text": content.get("text", "")},
    "shareMediaCategory": "ARTICLE",
    "shareMediaCategory": "ARTICLE",
    "media": [
    "media": [
    {
    {
    "status": "READY",
    "status": "READY",
    "description": {"text": article.get("description", "")},
    "description": {"text": article.get("description", "")},
    "originalUrl": article["url"],
    "originalUrl": article["url"],
    "title": {"text": article["title"]},
    "title": {"text": article["title"]},
    }
    }
    ],
    ],
    }
    }
    }
    }


    # Add targeting if provided
    # Add targeting if provided
    if targeting:
    if targeting:
    post_data["targetAudience"] = targeting
    post_data["targetAudience"] = targeting


    # Post to LinkedIn
    # Post to LinkedIn
    response = self.session.post(
    response = self.session.post(
    f"{self.api_base_url}/ugcPosts", json=post_data
    f"{self.api_base_url}/ugcPosts", json=post_data
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    # LinkedIn returns the post URN in the response headers
    # LinkedIn returns the post URN in the response headers
    post_urn = response.headers.get("x-restli-id")
    post_urn = response.headers.get("x-restli-id")


    # Extract the post ID from the URN
    # Extract the post ID from the URN
    post_id = post_urn.split(":")[-1] if post_urn else None
    post_id = post_urn.split(":")[-1] if post_urn else None


    return {
    return {
    "id": post_id,
    "id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {"post_urn": post_urn, "article_url": article["url"]},
    "platform_data": {"post_urn": post_urn, "article_url": article["url"]},
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn article posting error: {e}")
    logger.error(f"LinkedIn article posting error: {e}")
    raise PostingError("linkedin", str(e))
    raise PostingError("linkedin", str(e))


    def _post_image(
    def _post_image(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    post_data: Dict[str, Any],
    post_data: Dict[str, Any],
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post an image to LinkedIn.
    Post an image to LinkedIn.


    Args:
    Args:
    content: Content to post
    content: Content to post
    post_data: Base post data
    post_data: Base post data
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


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
    # 1. Upload the image to LinkedIn's asset API
    # 1. Upload the image to LinkedIn's asset API
    # 2. Get the asset URN
    # 2. Get the asset URN
    # 3. Create a post with the asset URN
    # 3. Create a post with the asset URN


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_urn = f"urn:li:share:{post_id}"
    post_urn = f"urn:li:share:{post_id}"


    return {
    return {
    "id": post_id,
    "id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {"post_urn": post_urn},
    "platform_data": {"post_urn": post_urn},
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn image posting error: {e}")
    logger.error(f"LinkedIn image posting error: {e}")
    raise PostingError("linkedin", str(e))
    raise PostingError("linkedin", str(e))


    def _post_video(
    def _post_video(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    post_data: Dict[str, Any],
    post_data: Dict[str, Any],
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post a video to LinkedIn.
    Post a video to LinkedIn.


    Args:
    Args:
    content: Content to post
    content: Content to post
    post_data: Base post data
    post_data: Base post data
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


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
    # 1. Upload the video to LinkedIn's asset API
    # 1. Upload the video to LinkedIn's asset API
    # 2. Get the asset URN
    # 2. Get the asset URN
    # 3. Create a post with the asset URN
    # 3. Create a post with the asset URN


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_urn = f"urn:li:share:{post_id}"
    post_urn = f"urn:li:share:{post_id}"


    return {
    return {
    "id": post_id,
    "id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {"post_urn": post_urn},
    "platform_data": {"post_urn": post_urn},
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn video posting error: {e}")
    logger.error(f"LinkedIn video posting error: {e}")
    raise PostingError("linkedin", str(e))
    raise PostingError("linkedin", str(e))


    def _post_document(
    def _post_document(
    self,
    self,
    content: Dict[str, Any],
    content: Dict[str, Any],
    post_data: Dict[str, Any],
    post_data: Dict[str, Any],
    targeting: Optional[Dict[str, Any]] = None,
    targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Post a document to LinkedIn.
    Post a document to LinkedIn.


    Args:
    Args:
    content: Content to post
    content: Content to post
    post_data: Base post data
    post_data: Base post data
    targeting: Optional audience targeting parameters
    targeting: Optional audience targeting parameters


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
    # 1. Upload the document to LinkedIn's asset API
    # 1. Upload the document to LinkedIn's asset API
    # 2. Get the asset URN
    # 2. Get the asset URN
    # 3. Create a post with the asset URN
    # 3. Create a post with the asset URN


    # For demonstration, we'll simulate a successful post
    # For demonstration, we'll simulate a successful post
    post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    post_urn = f"urn:li:share:{post_id}"
    post_urn = f"urn:li:share:{post_id}"


    return {
    return {
    "id": post_id,
    "id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "status": "posted",
    "status": "posted",
    "posted_at": datetime.now().isoformat(),
    "posted_at": datetime.now().isoformat(),
    "platform_data": {
    "platform_data": {
    "post_urn": post_urn,
    "post_urn": post_urn,
    "document_title": content["document"]["title"],
    "document_title": content["document"]["title"],
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn document posting error: {e}")
    logger.error(f"LinkedIn document posting error: {e}")
    raise PostingError("linkedin", str(e))
    raise PostingError("linkedin", str(e))


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
    Schedule a post for later publication on LinkedIn.
    Schedule a post for later publication on LinkedIn.


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
    # Determine if we're posting as a person or organization
    # Determine if we're posting as a person or organization
    author = self._get_author_urn()
    author = self._get_author_urn()


    # Prepare the base post data
    # Prepare the base post data
    {
    {
    "author": author,
    "author": author,
    "lifecycleState": "PUBLISHED",
    "lifecycleState": "PUBLISHED",
    "visibility": self._get_visibility_setting(visibility),
    "visibility": self._get_visibility_setting(visibility),
    "scheduledAt": int(
    "scheduledAt": int(
    schedule_time.timestamp() * 1000
    schedule_time.timestamp() * 1000
    ),  # LinkedIn uses milliseconds
    ),  # LinkedIn uses milliseconds
    }
    }


    # For demonstration, we'll simulate a successful scheduling
    # For demonstration, we'll simulate a successful scheduling
    scheduled_id = (
    scheduled_id = (
    f"linkedin_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    f"linkedin_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
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
    "text"
    "text"
    if "text" in content
    if "text" in content
    else (
    else (
    "article"
    "article"
    if "article" in content
    if "article" in content
    else (
    else (
    "image"
    "image"
    if "image" in content
    if "image" in content
    else "video" if "video" in content else "document"
    else "video" if "video" in content else "document"
    )
    )
    )
    )
    )
    )
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
    logger.error(f"LinkedIn scheduling error: {e}")
    logger.error(f"LinkedIn scheduling error: {e}")
    raise SchedulingError("linkedin", str(e))
    raise SchedulingError("linkedin", str(e))


    def get_post(self, post_id: str) -> Dict[str, Any]:
    def get_post(self, post_id: str) -> Dict[str, Any]:
    """
    """
    Get details of a specific LinkedIn post.
    Get details of a specific LinkedIn post.


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
    # Convert post ID to URN if needed
    # Convert post ID to URN if needed
    post_urn = (
    post_urn = (
    post_id if post_id.startswith("urn:li:") else f"urn:li:share:{post_id}"
    post_id if post_id.startswith("urn:li:") else f"urn:li:share:{post_id}"
    )
    )


    # Get post details
    # Get post details
    response = self.session.get(f"{self.api_base_url}/socialActions/{post_urn}")
    response = self.session.get(f"{self.api_base_url}/socialActions/{post_urn}")
    response.raise_for_status()
    response.raise_for_status()
    result = response.json()
    result = response.json()


    # Format the response
    # Format the response
    post_data = {
    post_data = {
    "id": post_id,
    "id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "likes": result.get("likesSummary", {}).get("totalLikes", 0),
    "likes": result.get("likesSummary", {}).get("totalLikes", 0),
    "comments": result.get("commentsSummary", {}).get("totalComments", 0),
    "comments": result.get("commentsSummary", {}).get("totalComments", 0),
    "platform_data": result,
    "platform_data": result,
    }
    }


    return post_data
    return post_data


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"LinkedIn get post error: {e}")
    logger.error(f"LinkedIn get post error: {e}")
    raise
    raise


    def delete_post(self, post_id: str) -> bool:
    def delete_post(self, post_id: str) -> bool:
    """
    """
    Delete a post from LinkedIn.
    Delete a post from LinkedIn.


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
    # Convert post ID to URN if needed
    # Convert post ID to URN if needed
    post_urn = (
    post_urn = (
    post_id if post_id.startswith("urn:li:") else f"urn:li:share:{post_id}"
    post_id if post_id.startswith("urn:li:") else f"urn:li:share:{post_id}"
    )
    )


    # Delete the post
    # Delete the post
    response = self.session.delete(f"{self.api_base_url}/ugcPosts/{post_urn}")
    response = self.session.delete(f"{self.api_base_url}/ugcPosts/{post_urn}")
    response.raise_for_status()
    response.raise_for_status()


    # LinkedIn returns 204 No Content on successful deletion
    # LinkedIn returns 204 No Content on successful deletion
    return response.status_code == 204
    return response.status_code == 204


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    if e.response and e.response.status_code == 404:
    if e.response and e.response.status_code == 404:
    raise PostNotFoundError(self.connection_id, post_id)
    raise PostNotFoundError(self.connection_id, post_id)
    logger.error(f"LinkedIn delete post error: {e}")
    logger.error(f"LinkedIn delete post error: {e}")
    raise DeletionError("linkedin", str(e))
    raise DeletionError("linkedin", str(e))


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
    Get analytics data from LinkedIn.
    Get analytics data from LinkedIn.


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
    "clicks",
    "clicks",
    "likes",
    "likes",
    "comments",
    "comments",
    "shares",
    "shares",
    "engagement",
    "engagement",
    "engagement-rate",
    "engagement-rate",
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
    # Convert post ID to URN if needed
    # Convert post ID to URN if needed
    post_urn = (
    post_urn = (
    post_id
    post_id
    if post_id.startswith("urn:li:")
    if post_id.startswith("urn:li:")
    else f"urn:li:share:{post_id}"
    else f"urn:li:share:{post_id}"
    )
    )


    # For demonstration, we'll return mock analytics data
    # For demonstration, we'll return mock analytics data
    return {
    return {
    "post_id": post_id,
    "post_id": post_id,
    "urn": post_urn,
    "urn": post_urn,
    "metrics": {
    "metrics": {
    "impressions": 1250,
    "impressions": 1250,
    "clicks": 85,
    "clicks": 85,
    "likes": 45,
    "likes": 45,
    "comments": 12,
    "comments": 12,
    "shares": 8,
    "shares": 8,
    "engagement": 150,
    "engagement": 150,
    "engagement-rate": 0.12,
    "engagement-rate": 0.12,
    },
    },
    }
    }


    # Otherwise, get organization-level analytics
    # Otherwise, get organization-level analytics
    elif self.organization_id:
    elif self.organization_id:
    # For demonstration, we'll return mock analytics data
    # For demonstration, we'll return mock analytics data
    return {
    return {
    "organization_id": self.organization_id,
    "organization_id": self.organization_id,
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "period": {"start_date": start_date_str, "end_date": end_date_str},
    "metrics": {
    "metrics": {
    "page_views": 3500,
    "page_views": 3500,
    "unique_visitors": 1800,
    "unique_visitors": 1800,
    "followers_gained": 120,
    "followers_gained": 120,
    "impressions": 15000,
    "impressions": 15000,
    "clicks": 850,
    "clicks": 850,
    "engagement_rate": 0.057,
    "engagement_rate": 0.057,
    },
    },
    }
    }


    else:
    else:
    return {"error": "No post ID or organization ID provided for analytics"}
    return {"error": "No post ID or organization ID provided for analytics"}


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn analytics error: {e}")
    logger.error(f"LinkedIn analytics error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "post_id": post_id,
    "post_id": post_id,
    "organization_id": self.organization_id,
    "organization_id": self.organization_id,
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
    Get audience insights from LinkedIn.
    Get audience insights from LinkedIn.


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
    metrics = ["demographics", "job_titles", "industries", "company_sizes"]
    metrics = ["demographics", "job_titles", "industries", "company_sizes"]


    # Check if we have an organization ID
    # Check if we have an organization ID
    if not self.organization_id:
    if not self.organization_id:
    return {"error": "Organization ID is required for audience insights"}
    return {"error": "Organization ID is required for audience insights"}


    # For demonstration, we'll return mock audience insights data
    # For demonstration, we'll return mock audience insights data
    return {
    return {
    "organization_id": self.organization_id,
    "organization_id": self.organization_id,
    "segment": segment or "followers",
    "segment": segment or "followers",
    "demographics": {
    "demographics": {
    "seniority": {
    "seniority": {
    "entry": 0.15,
    "entry": 0.15,
    "senior": 0.35,
    "senior": 0.35,
    "manager": 0.25,
    "manager": 0.25,
    "director": 0.15,
    "director": 0.15,
    "vp": 0.05,
    "vp": 0.05,
    "cxo": 0.05,
    "cxo": 0.05,
    },
    },
    "company_size": {
    "company_size": {
    "1-10": 0.10,
    "1-10": 0.10,
    "11-50": 0.15,
    "11-50": 0.15,
    "51-200": 0.20,
    "51-200": 0.20,
    "201-500": 0.15,
    "201-500": 0.15,
    "501-1000": 0.10,
    "501-1000": 0.10,
    "1001-5000": 0.15,
    "1001-5000": 0.15,
    "5001-10000": 0.08,
    "5001-10000": 0.08,
    "10001+": 0.07,
    "10001+": 0.07,
    },
    },
    "industry": {
    "industry": {
    "Technology": 0.35,
    "Technology": 0.35,
    "Marketing and Advertising": 0.15,
    "Marketing and Advertising": 0.15,
    "Financial Services": 0.12,
    "Financial Services": 0.12,
    "Higher Education": 0.08,
    "Higher Education": 0.08,
    "Healthcare": 0.07,
    "Healthcare": 0.07,
    "Other": 0.23,
    "Other": 0.23,
    },
    },
    "location": {
    "location": {
    "United States": 0.45,
    "United States": 0.45,
    "United Kingdom": 0.12,
    "United Kingdom": 0.12,
    "Canada": 0.08,
    "Canada": 0.08,
    "India": 0.07,
    "India": 0.07,
    "Australia": 0.05,
    "Australia": 0.05,
    "Other": 0.23,
    "Other": 0.23,
    },
    },
    },
    },
    "job_titles": [
    "job_titles": [
    {"title": "Software Engineer", "count": 350},
    {"title": "Software Engineer", "count": 350},
    {"title": "Marketing Manager", "count": 280},
    {"title": "Marketing Manager", "count": 280},
    {"title": "Product Manager", "count": 220},
    {"title": "Product Manager", "count": 220},
    {"title": "Data Scientist", "count": 180},
    {"title": "Data Scientist", "count": 180},
    {"title": "Sales Representative", "count": 150},
    {"title": "Sales Representative", "count": 150},
    ],
    ],
    "engagement": {
    "engagement": {
    "content_topics": [
    "content_topics": [
    {"topic": "Technology Trends", "engagement_rate": 0.085},
    {"topic": "Technology Trends", "engagement_rate": 0.085},
    {"topic": "Leadership", "engagement_rate": 0.072},
    {"topic": "Leadership", "engagement_rate": 0.072},
    {"topic": "Industry News", "engagement_rate": 0.065},
    {"topic": "Industry News", "engagement_rate": 0.065},
    {"topic": "Company Updates", "engagement_rate": 0.058},
    {"topic": "Company Updates", "engagement_rate": 0.058},
    {"topic": "Product Announcements", "engagement_rate": 0.052},
    {"topic": "Product Announcements", "engagement_rate": 0.052},
    ]
    ]
    },
    },
    }
    }


except Exception as e:
except Exception as e:
    logger.error(f"LinkedIn audience insights error: {e}")
    logger.error(f"LinkedIn audience insights error: {e}")
    return {
    return {
    "error": str(e),
    "error": str(e),
    "organization_id": self.organization_id,
    "organization_id": self.organization_id,
    "segment": segment or "followers",
    "segment": segment or "followers",
    }
    }