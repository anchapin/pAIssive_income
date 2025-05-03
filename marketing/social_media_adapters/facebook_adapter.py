"""
Facebook adapter for social media integration.

This module provides an adapter for connecting to the Facebook Graph API for posting content,
retrieving analytics, and managing social media campaigns.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import requests

from marketing.errors import (
    AuthenticationError,
    ContentValidationError,
    DeletionError,
    NotSupportedError,
    PostingError,
    PostNotFoundError,
    SchedulingError,
)
from marketing.social_media_adapters.base_adapter import BaseSocialMediaAdapter

# Set up logging
logger = logging.getLogger(__name__)


class FacebookAdapter(BaseSocialMediaAdapter):
    """
    Adapter for Facebook platform integration.

    This class implements the BaseSocialMediaAdapter interface for Facebook,
    providing methods for posting content, retrieving analytics, and managing
    Facebook campaigns.
    """

    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
        """
        Initialize the Facebook adapter.

        Args:
            connection_id: Unique identifier for the connection
            connection_data: Connection data including credentials and settings
        """
        super().__init__(connection_id, connection_data)
        self.api_base_url = "https://graph.facebook.com / v18.0"  # Using latest version as of 2023
        self.app_id = self.credentials.get("app_id")
        self.app_secret = self.credentials.get("app_secret")
        self.access_token = self.credentials.get("access_token")
        self.page_id = self.credentials.get("page_id")
        self.session = requests.Session()

        # Set up authentication if access token is provided
        if self.access_token:
            self.session.params = {"access_token": self.access_token}
            self._connected = True

    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the Facebook Graph API.

        Returns:
            Dictionary containing authentication result and any additional platform data

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # If we already have an access token, verify it
            if self.access_token:
                # Check if the token is valid by getting basic account info
                response = self.session.get(f"{self.api_base_url}/me")
                response.raise_for_status()
                user_data = response.json()

                # If we have a page ID, get page details
                page_data = {}
                if self.page_id:
                    page_response = self.session.get(f"{self.api_base_url}/{self.page_id}")
                    if page_response.status_code == 200:
                        page_data = page_response.json()

                return {
                    "authenticated": True,
                    "user_id": user_data.get("id"),
                    "name": user_data.get("name"),
                    "page_id": self.page_id,
                    "page_name": page_data.get("name") if page_data else None,
                }

            # If we have app ID and secret but no access token, get an app token
            # Note: App tokens have limited permissions, user tokens are preferred
            elif self.app_id and self.app_secret:
                response = self.session.get(
                    f"{self.api_base_url}/oauth / access_token",
                    params={
                        "client_id": self.app_id,
                        "client_secret": self.app_secret,
                        "grant_type": "client_credentials",
                    },
                )
                response.raise_for_status()
                token_data = response.json()

                # Update session with new access token
                self.access_token = token_data.get("access_token")
                self.session.params = {"access_token": self.access_token}
                self._connected = True

                return {
                    "authenticated": True,
                    "access_token": self.access_token,
                    "token_type": "app_token",
                }

            else:
                raise AuthenticationError(
                    "facebook",
                    "Missing required credentials (access_token or app_id and app_secret)",
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook authentication error: {e}")
            raise AuthenticationError("facebook", str(e))

    def validate_content(self, content: Dict[str, Any]) -> bool:
        """
        Validate content for posting to Facebook.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise

        Raises:
            ContentValidationError: If content validation fails with specific reason
        """
        # Check if we have at least one content type
        if not any(key in content for key in ["message", "link", "photo", "video"]):
            raise ContentValidationError(
                "facebook", "At least one content type (message, link, photo, video) is required"
            )

        # Check message length if present (Facebook's limit is 63,206 characters)
        if "message" in content and len(content["message"]) > 63206:
            raise ContentValidationError(
                "facebook",
                f"Message exceeds 63,206 characters (current: {len(content['message'])})",
            )

        # Check link if present
        if "link" in content:
            if not content["link"].startswith(("http://", "https://")):
                raise ContentValidationError("facebook", "Link must start with http:// or https://")

        # Check photo if present
        if "photo" in content:
            if "url" not in content["photo"] and "source" not in content["photo"]:
                raise ContentValidationError(
                    "facebook", "Photo must have either a URL or source (base64 data)"
                )

        # Check video if present
        if "video" in content:
            if "url" not in content["video"] and "source" not in content["video"]:
                raise ContentValidationError(
                    "facebook", "Video must have either a URL or source (file path)"
                )

        return True

    def post_content(
        self,
        content: Dict[str, Any],
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post content to Facebook.

        Args:
            content: Content to post
            visibility: Visibility setting (public, private, etc.)
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and platform - assigned ID

        Raises:
            ContentValidationError: If content validation fails
            PostingError: If posting fails
        """
        # Validate content first
        self.validate_content(content)

        try:
            # Check if we have a page ID (required for posting)
            if not self.page_id:
                raise PostingError("facebook", "Page ID is required for posting")

            # Prepare post data
            post_data = {}

            # Add message if present
            if "message" in content:
                post_data["message"] = content["message"]

            # Add link if present
            if "link" in content:
                post_data["link"] = content["link"]

            # Add privacy settings based on visibility
            if visibility == "private":
                post_data["privacy"] = {"value": "SELF"}
            elif visibility == "friends" or visibility == "followers":
                post_data["privacy"] = {"value": "ALL_FRIENDS"}
            else:  # public
                post_data["privacy"] = {"value": "EVERYONE"}

            # Add targeting if present
            if targeting:
                post_data["targeting"] = targeting

            # Determine the endpoint based on content type
            endpoint = f"{self.api_base_url}/{self.page_id}/feed"

            # Handle photo posts
            if "photo" in content:
                endpoint = f"{self.api_base_url}/{self.page_id}/photos"
                if "url" in content["photo"]:
                    post_data["url"] = content["photo"]["url"]
                elif "source" in content["photo"]:
                    # For file uploads, we'd need to handle multipart / form - data
                    # This is simplified for demonstration
                    post_data["source"] = content["photo"]["source"]

            # Handle video posts
            elif "video" in content:
                endpoint = f"{self.api_base_url}/{self.page_id}/videos"
                if "url" in content["video"]:
                    post_data["file_url"] = content["video"]["url"]
                elif "source" in content["video"]:
                    # For file uploads, we'd need to handle multipart / form - data
                    # This is simplified for demonstration
                    post_data["source"] = content["video"]["source"]

            # Post the content
            response = self.session.post(endpoint, data=post_data)
            response.raise_for_status()
            result = response.json()

            # Extract post ID
            post_id = result.get("id")

            # Get the post URL
            post_url = f"https://facebook.com/{post_id}"

            return {"id": post_id, "platform_data": result, "url": post_url}

        except ContentValidationError:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook posting error: {e}")
            raise PostingError("facebook", str(e))

    def schedule_post(
        self,
        content: Dict[str, Any],
        schedule_time: datetime,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a post for later publication on Facebook.

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
            # Check if we have a page ID (required for posting)
            if not self.page_id:
                raise SchedulingError("facebook", "Page ID is required for scheduling posts")

            # Prepare post data
            post_data = {}

            # Add message if present
            if "message" in content:
                post_data["message"] = content["message"]

            # Add link if present
            if "link" in content:
                post_data["link"] = content["link"]

            # Add privacy settings based on visibility
            if visibility == "private":
                post_data["privacy"] = {"value": "SELF"}
            elif visibility == "friends" or visibility == "followers":
                post_data["privacy"] = {"value": "ALL_FRIENDS"}
            else:  # public
                post_data["privacy"] = {"value": "EVERYONE"}

            # Add targeting if present
            if targeting:
                post_data["targeting"] = targeting

            # Add scheduled publish time
            post_data["scheduled_publish_time"] = int(schedule_time.timestamp())
            post_data["published"] = False

            # Determine the endpoint based on content type
            endpoint = f"{self.api_base_url}/{self.page_id}/feed"

            # Handle photo posts
            if "photo" in content:
                endpoint = f"{self.api_base_url}/{self.page_id}/photos"
                if "url" in content["photo"]:
                    post_data["url"] = content["photo"]["url"]
                elif "source" in content["photo"]:
                    # For file uploads, we'd need to handle multipart / form - data
                    # This is simplified for demonstration
                    post_data["source"] = content["photo"]["source"]

            # Handle video posts
            elif "video" in content:
                endpoint = f"{self.api_base_url}/{self.page_id}/videos"
                if "url" in content["video"]:
                    post_data["file_url"] = content["video"]["url"]
                elif "source" in content["video"]:
                    # For file uploads, we'd need to handle multipart / form - data
                    # This is simplified for demonstration
                    post_data["source"] = content["video"]["source"]

            # Schedule the post
            response = self.session.post(endpoint, data=post_data)
            response.raise_for_status()
            result = response.json()

            # Extract post ID
            post_id = result.get("id")

            return {
                "id": post_id,
                "scheduled_time": schedule_time.isoformat(),
                "status": "scheduled",
                "platform_data": result,
            }

        except ContentValidationError:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook scheduling error: {e}")
            raise SchedulingError("facebook", str(e))

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific Facebook post.

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
                    "fields": "id,message,created_time,permalink_url,type,attachments,insights.metric(post_impressions,post_engagements,post_reactions_by_type)"
                },
            )
            response.raise_for_status()
            result = response.json()

            # Format the response
            return {
                "id": result.get("id"),
                "text": result.get("message"),
                "created_at": result.get("created_time"),
                "url": result.get("permalink_url"),
                "type": result.get("type"),
                "attachments": result.get("attachments", {}).get("data", []),
                "metrics": self._extract_insights(result.get("insights", {})),
                "platform_data": result,
            }

        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"Facebook get post error: {e}")
            raise

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from Facebook.

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
                raise DeletionError("facebook", "Failed to delete post")

        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"Facebook delete post error: {e}")
            raise DeletionError("facebook", str(e))

    def get_analytics(
        self,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get analytics data from Facebook.

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
                    "page_impressions",
                    "page_engaged_users",
                    "page_post_engagements",
                    "page_fans",
                    "page_fan_adds",
                    "page_views_total",
                ]

            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Format dates for API
            start_date_str = start_date.strftime(" % Y-%m-%d")
            end_date_str = end_date.strftime(" % Y-%m-%d")

            # If post_id is provided, get analytics for a specific post
            if post_id:
                # Get post insights
                response = self.session.get(
                    f"{self.api_base_url}/{post_id}/insights",
                    params={"metric": "post_impressions,post_engagements,post_reactions_by_type"},
                )
                response.raise_for_status()
                result = response.json()

                # Extract metrics
                analytics = {"post_id": post_id, "metrics": self._extract_insights(result)}

                return analytics

            # Otherwise, get page - level analytics
            elif self.page_id:
                # Get page insights
                response = self.session.get(
                    f"{self.api_base_url}/{self.page_id}/insights",
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
                    "page_id": self.page_id,
                    "period": {"start_date": start_date_str, "end_date": end_date_str},
                    "metrics": self._extract_insights(result),
                }

                return analytics

            else:
                return {"error": "No page ID or post ID provided for analytics"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook analytics error: {e}")
            return {
                "error": str(e),
                "post_id": post_id,
                "page_id": self.page_id,
                "period": {
                    "start_date": start_date_str if start_date else None,
                    "end_date": end_date_str if end_date else None,
                },
            }

    def get_audience_insights(
        self, metrics: Optional[List[str]] = None, segment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get audience insights from Facebook.

        Args:
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment to get insights for

        Returns:
            Dictionary containing the audience insights
        """
        try:
            # Set default metrics if not provided
            if not metrics:
                metrics = ["demographics", "interests", "page_likes"]

            # Check if we have a page ID
            if not self.page_id:
                return {"error": "Page ID is required for audience insights"}

            # Get audience insights
            # Note: Facebook's Audience Insights API is limited and requires special permissions
            # For demonstration, we'll return mock audience insights data

            return {
                "page_id": self.page_id,
                "segment": segment or "all_fans",
                "demographics": {
                    "age_gender": {
                        "F.13 - 17": 0.02,
                        "F.18 - 24": 0.12,
                        "F.25 - 34": 0.18,
                        "F.35 - 44": 0.08,
                        "F.45 - 54": 0.05,
                        "F.55 + ": 0.03,
                        "M.13 - 17": 0.03,
                        "M.18 - 24": 0.15,
                        "M.25 - 34": 0.22,
                        "M.35 - 44": 0.07,
                        "M.45 - 54": 0.04,
                        "M.55 + ": 0.01,
                    },
                    "location": {
                        "United States": 0.4,
                        "United Kingdom": 0.12,
                        "Canada": 0.08,
                        "Australia": 0.05,
                        "Germany": 0.04,
                        "France": 0.03,
                        "Other": 0.28,
                    },
                    "language": {
                        "English": 0.75,
                        "Spanish": 0.08,
                        "French": 0.05,
                        "German": 0.04,
                        "Other": 0.08,
                    },
                },
                "interests": [
                    {"category": "Technology", "score": 0.82},
                    {"category": "Entertainment", "score": 0.65},
                    {"category": "Shopping", "score": 0.58},
                    {"category": "Travel", "score": 0.45},
                    {"category": "Fitness", "score": 0.38},
                ],
                "page_likes": [
                    {"name": "Technology News", "category": "News", "affinity": 0.85},
                    {"name": "Gadget Reviews", "category": "Technology", "affinity": 0.78},
                    {"name": "Digital Marketing", "category": "Business", "affinity": 0.72},
                    {"name": "Startup Culture", "category": "Business", "affinity": 0.65},
                    {"name": "Travel Destinations", "category": "Travel", "affinity": 0.45},
                ],
                "activity": {
                    "frequency": {
                        "daily_active": 0.25,
                        "weekly_active": 0.45,
                        "monthly_active": 0.3,
                    },
                    "devices": {"mobile": 0.75, "desktop": 0.25},
                },
            }

        except Exception as e:
            logger.error(f"Facebook audience insights error: {e}")
            return {"error": str(e), "page_id": self.page_id, "segment": segment or "all_fans"}

    def _extract_insights(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metrics from Facebook insights data.

        Args:
            insights_data: Raw insights data from Facebook API

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
                    # For metrics like reactions_by_type
                    metrics[name] = latest_value
                else:
                    # For simple numeric metrics
                    metrics[name] = latest_value

        return metrics
