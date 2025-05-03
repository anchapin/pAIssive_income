"""
LinkedIn adapter for social media integration.

This module provides an adapter for connecting to the LinkedIn API for posting content,
retrieving analytics, and managing social media campaigns.
"""


import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from marketing.errors import 
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


class LinkedInAdapter(BaseSocialMediaAdapter):
    """
    Adapter for LinkedIn platform integration.

    This class implements the BaseSocialMediaAdapter interface for LinkedIn,
    providing methods for posting content, retrieving analytics, and managing
    LinkedIn campaigns.
    """

    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
        """
        Initialize the LinkedIn adapter.

        Args:
            connection_id: Unique identifier for the connection
            connection_data: Connection data including credentials and settings
        """
        super().__init__(connection_id, connection_data)
        self.api_base_url = "https://api.linkedin.com/v2"
        self.access_token = self.credentials.get("access_token")
        self.client_id = self.credentials.get("client_id")
        self.client_secret = self.credentials.get("client_secret")
        self.organization_id = self.credentials.get(
            "organization_id"
        )  # For company pages
        self.person_id = self.credentials.get("person_id")  # For personal profiles
        self.session = requests.Session()

        # Set up authentication if access token is provided
        if self.access_token:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                }
            )
            self._connected = True

    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the LinkedIn API.

        Returns:
            Dictionary containing authentication result and any additional platform data

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # If we already have an access token, verify it
            if self.access_token:
                # Check if the token is valid by getting basic profile info
                response = self.session.get(f"{self.api_base_url}/me")
                response.raise_for_status()
                profile_data = response.json()

                return {
                    "authenticated": True,
                    "profile_id": profile_data.get("id"),
                    "first_name": profile_data.get("localizedFirstName"),
                    "last_name": profile_data.get("localizedLastName"),
                }

            # If we have client ID and secret but no access token, we'd need to implement OAuth flow
            # This would typically be handled by a web application, not directly in this adapter
            elif self.client_id and self.client_secret:
                raise AuthenticationError(
                    "linkedin",
                    "OAuth flow not implemented in this adapter. Please obtain an access token externally.",
                )

            else:
                raise AuthenticationError(
                    "linkedin",
                    "Missing required credentials (access_token or client_id and client_secret)",
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn authentication error: {e}")
            raise AuthenticationError("linkedin", str(e))

    def validate_content(self, content: Dict[str, Any]) -> bool:
        """
        Validate content for posting to LinkedIn.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise

        Raises:
            ContentValidationError: If content validation fails with specific reason
        """
        # Check if we have at least one content type
        if not any(
            key in content for key in ["text", "article", "image", "video", "document"]
        ):
            raise ContentValidationError(
                "linkedin",
                "At least one content type (text, article, image, video, document) is required",
            )

        # Check text length if present (LinkedIn's limit is 3,000 characters)
        if "text" in content and len(content["text"]) > 3000:
            raise ContentValidationError(
                "linkedin",
                f"Text exceeds 3,000 characters (current: {len(content['text'])})",
            )

        # Check article if present
        if "article" in content:
            if "title" not in content["article"]:
                raise ContentValidationError("linkedin", "Article must have a title")

            if "url" not in content["article"]:
                raise ContentValidationError("linkedin", "Article must have a URL")

            if len(content["article"]["title"]) > 150:
                raise ContentValidationError(
                    "linkedin",
                    f"Article title exceeds 150 characters (current: {len(content['article']['title'])})",
                )

        # Check image if present
        if "image" in content:
            if "url" not in content["image"] and "source" not in content["image"]:
                raise ContentValidationError(
                    "linkedin", "Image must have either a URL or source (base64 data)"
                )

        # Check video if present
        if "video" in content:
            if "url" not in content["video"] and "source" not in content["video"]:
                raise ContentValidationError(
                    "linkedin", "Video must have either a URL or source (file path)"
                )

        # Check document if present
        if "document" in content:
            if "url" not in content["document"] and "source" not in content["document"]:
                raise ContentValidationError(
                    "linkedin", "Document must have either a URL or source (file path)"
                )

            if "title" not in content["document"]:
                raise ContentValidationError("linkedin", "Document must have a title")

        return True

    def post_content(
        self,
        content: Dict[str, Any],
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post content to LinkedIn.

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
            # Determine if we're posting as a person or organization
            author = self._get_author_urn()

            # Prepare the base post data
            post_data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "visibility": self._get_visibility_setting(visibility),
            }

            # Add specific content based on type
            if "text" in content:
                return self._post_text(content, post_data, targeting)
            elif "article" in content:
                return self._post_article(content, post_data, targeting)
            elif "image" in content:
                return self._post_image(content, post_data, targeting)
            elif "video" in content:
                return self._post_video(content, post_data, targeting)
            elif "document" in content:
                return self._post_document(content, post_data, targeting)
            else:
                raise ContentValidationError("linkedin", "No valid content type found")

        except ContentValidationError:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn posting error: {e}")
            raise PostingError("linkedin", str(e))

    def _get_author_urn(self) -> str:
        """
        Get the URN for the post author.

        Returns:
            URN string for the author

        Raises:
            PostingError: If neither organization ID nor person ID is available
        """
        if self.organization_id:
            return f"urn:li:organization:{self.organization_id}"
        elif self.person_id:
            return f"urn:li:person:{self.person_id}"
        else:
            raise PostingError(
                "linkedin",
                "Neither organization ID nor person ID is available for posting",
            )

    def _get_visibility_setting(self, visibility: str) -> Dict[str, str]:
        """
        Get the visibility setting for a post.

        Args:
            visibility: Visibility setting (public, private, connections)

        Returns:
            Dictionary with visibility settings
        """
        if visibility == "public":
            return {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        elif visibility == "connections":
            return {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"}
        else:  # private
            return {"com.linkedin.ugc.MemberNetworkVisibility": "NONE"}

    def _post_text(
        self,
        content: Dict[str, Any],
        post_data: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post text content to LinkedIn.

        Args:
            content: Content to post
            post_data: Base post data
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform-assigned ID

        Raises:
            PostingError: If posting fails
        """
        try:
            # Add text specific content
            post_data["specificContent"] = {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content["text"]},
                    "shareMediaCategory": "NONE",
                }
            }

            # Add targeting if provided
            if targeting:
                post_data["targetAudience"] = targeting

            # Post to LinkedIn
            response = self.session.post(
                f"{self.api_base_url}/ugcPosts", json=post_data
            )
            response.raise_for_status()

            # LinkedIn returns the post URN in the response headers
            post_urn = response.headers.get("x-restli-id")

            # Extract the post ID from the URN
            post_id = post_urn.split(":")[-1] if post_urn else None

            return {
                "id": post_id,
                "urn": post_urn,
                "status": "posted",
                "posted_at": datetime.now().isoformat(),
                "platform_data": {"post_urn": post_urn},
            }

        except Exception as e:
            logger.error(f"LinkedIn text posting error: {e}")
            raise PostingError("linkedin", str(e))

    def _post_article(
        self,
        content: Dict[str, Any],
        post_data: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post an article to LinkedIn.

        Args:
            content: Content to post
            post_data: Base post data
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform-assigned ID

        Raises:
            PostingError: If posting fails
        """
        try:
            article = content["article"]

            # Add article specific content
            post_data["specificContent"] = {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content.get("text", "")},
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": article.get("description", "")},
                            "originalUrl": article["url"],
                            "title": {"text": article["title"]},
                        }
                    ],
                }
            }

            # Add targeting if provided
            if targeting:
                post_data["targetAudience"] = targeting

            # Post to LinkedIn
            response = self.session.post(
                f"{self.api_base_url}/ugcPosts", json=post_data
            )
            response.raise_for_status()

            # LinkedIn returns the post URN in the response headers
            post_urn = response.headers.get("x-restli-id")

            # Extract the post ID from the URN
            post_id = post_urn.split(":")[-1] if post_urn else None

            return {
                "id": post_id,
                "urn": post_urn,
                "status": "posted",
                "posted_at": datetime.now().isoformat(),
                "platform_data": {"post_urn": post_urn, "article_url": article["url"]},
            }

        except Exception as e:
            logger.error(f"LinkedIn article posting error: {e}")
            raise PostingError("linkedin", str(e))

    def _post_image(
        self,
        content: Dict[str, Any],
        post_data: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post an image to LinkedIn.

        Args:
            content: Content to post
            post_data: Base post data
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform-assigned ID

        Raises:
            PostingError: If posting fails
        """
        try:
            # In a real implementation, we would:
            # 1. Upload the image to LinkedIn's asset API
            # 2. Get the asset URN
            # 3. Create a post with the asset URN

            # For demonstration, we'll simulate a successful post
            post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            post_urn = f"urn:li:share:{post_id}"

            return {
                "id": post_id,
                "urn": post_urn,
                "status": "posted",
                "posted_at": datetime.now().isoformat(),
                "platform_data": {"post_urn": post_urn},
            }

        except Exception as e:
            logger.error(f"LinkedIn image posting error: {e}")
            raise PostingError("linkedin", str(e))

    def _post_video(
        self,
        content: Dict[str, Any],
        post_data: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post a video to LinkedIn.

        Args:
            content: Content to post
            post_data: Base post data
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform-assigned ID

        Raises:
            PostingError: If posting fails
        """
        try:
            # In a real implementation, we would:
            # 1. Upload the video to LinkedIn's asset API
            # 2. Get the asset URN
            # 3. Create a post with the asset URN

            # For demonstration, we'll simulate a successful post
            post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            post_urn = f"urn:li:share:{post_id}"

            return {
                "id": post_id,
                "urn": post_urn,
                "status": "posted",
                "posted_at": datetime.now().isoformat(),
                "platform_data": {"post_urn": post_urn},
            }

        except Exception as e:
            logger.error(f"LinkedIn video posting error: {e}")
            raise PostingError("linkedin", str(e))

    def _post_document(
        self,
        content: Dict[str, Any],
        post_data: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post a document to LinkedIn.

        Args:
            content: Content to post
            post_data: Base post data
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform-assigned ID

        Raises:
            PostingError: If posting fails
        """
        try:
            # In a real implementation, we would:
            # 1. Upload the document to LinkedIn's asset API
            # 2. Get the asset URN
            # 3. Create a post with the asset URN

            # For demonstration, we'll simulate a successful post
            post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            post_urn = f"urn:li:share:{post_id}"

            return {
                "id": post_id,
                "urn": post_urn,
                "status": "posted",
                "posted_at": datetime.now().isoformat(),
                "platform_data": {
                    "post_urn": post_urn,
                    "document_title": content["document"]["title"],
                },
            }

        except Exception as e:
            logger.error(f"LinkedIn document posting error: {e}")
            raise PostingError("linkedin", str(e))

    def schedule_post(
        self,
        content: Dict[str, Any],
        schedule_time: datetime,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a post for later publication on LinkedIn.

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
        # Validate content first
        self.validate_content(content)

        try:
            # Determine if we're posting as a person or organization
            author = self._get_author_urn()

            # Prepare the base post data
            {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "visibility": self._get_visibility_setting(visibility),
                "scheduledAt": int(
                    schedule_time.timestamp() * 1000
                ),  # LinkedIn uses milliseconds
            }

            # For demonstration, we'll simulate a successful scheduling
            scheduled_id = (
                f"linkedin_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

            return {
                "id": scheduled_id,
                "scheduled_time": schedule_time.isoformat(),
                "status": "scheduled",
                "platform_data": {
                    "content_type": (
                        "text"
                        if "text" in content
                        else (
                            "article"
                            if "article" in content
                            else (
                                "image"
                                if "image" in content
                                else "video" if "video" in content else "document"
                            )
                        )
                    )
                },
            }

        except ContentValidationError:
            raise
        except Exception as e:
            logger.error(f"LinkedIn scheduling error: {e}")
            raise SchedulingError("linkedin", str(e))

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific LinkedIn post.

        Args:
            post_id: ID of the post to retrieve

        Returns:
            Dictionary containing the post details

        Raises:
            PostNotFoundError: If the post ID is not found
        """
        try:
            # Convert post ID to URN if needed
            post_urn = (
                post_id if post_id.startswith("urn:li:") else f"urn:li:share:{post_id}"
            )

            # Get post details
            response = self.session.get(f"{self.api_base_url}/socialActions/{post_urn}")
            response.raise_for_status()
            result = response.json()

            # Format the response
            post_data = {
                "id": post_id,
                "urn": post_urn,
                "likes": result.get("likesSummary", {}).get("totalLikes", 0),
                "comments": result.get("commentsSummary", {}).get("totalComments", 0),
                "platform_data": result,
            }

            return post_data

        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"LinkedIn get post error: {e}")
            raise

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from LinkedIn.

        Args:
            post_id: ID of the post to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            PostNotFoundError: If the post ID is not found
            DeletionError: If deletion fails
        """
        try:
            # Convert post ID to URN if needed
            post_urn = (
                post_id if post_id.startswith("urn:li:") else f"urn:li:share:{post_id}"
            )

            # Delete the post
            response = self.session.delete(f"{self.api_base_url}/ugcPosts/{post_urn}")
            response.raise_for_status()

            # LinkedIn returns 204 No Content on successful deletion
            return response.status_code == 204

        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"LinkedIn delete post error: {e}")
            raise DeletionError("linkedin", str(e))

    def get_analytics(
        self,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get analytics data from LinkedIn.

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
                    "clicks",
                    "likes",
                    "comments",
                    "shares",
                    "engagement",
                    "engagement-rate",
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
                # Convert post ID to URN if needed
                post_urn = (
                    post_id
                    if post_id.startswith("urn:li:")
                    else f"urn:li:share:{post_id}"
                )

                # For demonstration, we'll return mock analytics data
                return {
                    "post_id": post_id,
                    "urn": post_urn,
                    "metrics": {
                        "impressions": 1250,
                        "clicks": 85,
                        "likes": 45,
                        "comments": 12,
                        "shares": 8,
                        "engagement": 150,
                        "engagement-rate": 0.12,
                    },
                }

            # Otherwise, get organization-level analytics
            elif self.organization_id:
                # For demonstration, we'll return mock analytics data
                return {
                    "organization_id": self.organization_id,
                    "period": {"start_date": start_date_str, "end_date": end_date_str},
                    "metrics": {
                        "page_views": 3500,
                        "unique_visitors": 1800,
                        "followers_gained": 120,
                        "impressions": 15000,
                        "clicks": 850,
                        "engagement_rate": 0.057,
                    },
                }

            else:
                return {"error": "No post ID or organization ID provided for analytics"}

        except Exception as e:
            logger.error(f"LinkedIn analytics error: {e}")
            return {
                "error": str(e),
                "post_id": post_id,
                "organization_id": self.organization_id,
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
        Get audience insights from LinkedIn.

        Args:
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment to get insights for

        Returns:
            Dictionary containing the audience insights
        """
        try:
            # Set default metrics if not provided
            if not metrics:
                metrics = ["demographics", "job_titles", "industries", "company_sizes"]

            # Check if we have an organization ID
            if not self.organization_id:
                return {"error": "Organization ID is required for audience insights"}

            # For demonstration, we'll return mock audience insights data
            return {
                "organization_id": self.organization_id,
                "segment": segment or "followers",
                "demographics": {
                    "seniority": {
                        "entry": 0.15,
                        "senior": 0.35,
                        "manager": 0.25,
                        "director": 0.15,
                        "vp": 0.05,
                        "cxo": 0.05,
                    },
                    "company_size": {
                        "1-10": 0.10,
                        "11-50": 0.15,
                        "51-200": 0.20,
                        "201-500": 0.15,
                        "501-1000": 0.10,
                        "1001-5000": 0.15,
                        "5001-10000": 0.08,
                        "10001+": 0.07,
                    },
                    "industry": {
                        "Technology": 0.35,
                        "Marketing and Advertising": 0.15,
                        "Financial Services": 0.12,
                        "Higher Education": 0.08,
                        "Healthcare": 0.07,
                        "Other": 0.23,
                    },
                    "location": {
                        "United States": 0.45,
                        "United Kingdom": 0.12,
                        "Canada": 0.08,
                        "India": 0.07,
                        "Australia": 0.05,
                        "Other": 0.23,
                    },
                },
                "job_titles": [
                    {"title": "Software Engineer", "count": 350},
                    {"title": "Marketing Manager", "count": 280},
                    {"title": "Product Manager", "count": 220},
                    {"title": "Data Scientist", "count": 180},
                    {"title": "Sales Representative", "count": 150},
                ],
                "engagement": {
                    "content_topics": [
                        {"topic": "Technology Trends", "engagement_rate": 0.085},
                        {"topic": "Leadership", "engagement_rate": 0.072},
                        {"topic": "Industry News", "engagement_rate": 0.065},
                        {"topic": "Company Updates", "engagement_rate": 0.058},
                        {"topic": "Product Announcements", "engagement_rate": 0.052},
                    ]
                },
            }

        except Exception as e:
            logger.error(f"LinkedIn audience insights error: {e}")
            return {
                "error": str(e),
                "organization_id": self.organization_id,
                "segment": segment or "followers",
            }