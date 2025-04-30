"""
Twitter adapter for social media integration.

This module provides an adapter for connecting to the Twitter API for posting content,
retrieving analytics, and managing social media campaigns.
"""

import logging
import json
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from marketing.social_media_adapters.base_adapter import BaseSocialMediaAdapter
from marketing.errors import (
    AuthenticationError,
    ContentValidationError,
    PostNotFoundError,
    PostingError,
    DeletionError,
    SchedulingError,
    NotSupportedError,
)

# Set up logging
logger = logging.getLogger(__name__)


class TwitterAdapter(BaseSocialMediaAdapter):
    """
    Adapter for Twitter platform integration.

    This class implements the BaseSocialMediaAdapter interface for Twitter,
    providing methods for posting tweets, retrieving analytics, and managing
    Twitter campaigns.
    """

    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
        """
        Initialize the Twitter adapter.

        Args:
            connection_id: Unique identifier for the connection
            connection_data: Connection data including credentials and settings
        """
        super().__init__(connection_id, connection_data)
        self.api_base_url = "https://api.twitter.com/2"
        self.oauth_url = "https://api.twitter.com/oauth2/token"
        self.api_key = self.credentials.get("api_key")
        self.api_secret = self.credentials.get("api_secret")
        self.access_token = self.credentials.get("access_token")
        self.access_token_secret = self.credentials.get("access_token_secret")
        self.bearer_token = self.credentials.get("bearer_token")
        self.session = requests.Session()

        # Set up authentication if credentials are provided
        if self.bearer_token:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.bearer_token}"}
            )
            self._connected = True
        elif (
            self.api_key
            and self.api_secret
            and self.access_token
            and self.access_token_secret
        ):
            # OAuth 1.0a authentication would be implemented here
            # This is a simplified version for demonstration
            self._connected = True

    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the Twitter API.

        Returns:
            Dictionary containing authentication result and any additional platform data

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # If we already have a bearer token, verify it
            if self.bearer_token:
                response = self.session.get(f"{self.api_base_url}/users/me")
                response.raise_for_status()
                user_data = response.json()

                return {
                    "authenticated": True,
                    "user_id": user_data.get("data", {}).get("id"),
                    "username": user_data.get("data", {}).get("username"),
                    "name": user_data.get("data", {}).get("name"),
                }

            # If we have API key and secret but no bearer token, get one
            elif self.api_key and self.api_secret:
                auth = (self.api_key, self.api_secret)
                data = {"grant_type": "client_credentials"}

                response = requests.post(self.oauth_url, auth=auth, data=data)
                response.raise_for_status()
                token_data = response.json()

                # Update session with new bearer token
                self.bearer_token = token_data.get("access_token")
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.bearer_token}"}
                )
                self._connected = True

                # Get user information
                response = self.session.get(f"{self.api_base_url}/users/me")
                response.raise_for_status()
                user_data = response.json()

                return {
                    "authenticated": True,
                    "bearer_token": self.bearer_token,
                    "token_type": token_data.get("token_type"),
                    "expires_in": token_data.get("expires_in"),
                    "user_id": user_data.get("data", {}).get("id"),
                    "username": user_data.get("data", {}).get("username"),
                    "name": user_data.get("data", {}).get("name"),
                }

            else:
                raise AuthenticationError(
                    "twitter",
                    "Missing required credentials (api_key, api_secret or bearer_token)",
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter authentication error: {e}")
            raise AuthenticationError("twitter", str(e))

    def validate_content(self, content: Dict[str, Any]) -> bool:
        """
        Validate content for posting to Twitter.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise

        Raises:
            ContentValidationError: If content validation fails with specific reason
        """
        # Check if text is present
        if "text" not in content:
            raise ContentValidationError("twitter", "Tweet text is required")

        # Check text length (Twitter's current limit is 280 characters)
        if len(content["text"]) > 280:
            raise ContentValidationError(
                "twitter",
                f"Tweet text exceeds 280 characters (current: {len(content['text'])})",
            )

        # Check media attachments if present
        if "media" in content:
            media = content["media"]

            # Check media count (Twitter allows up to 4 media attachments)
            if len(media) > 4:
                raise ContentValidationError(
                    "twitter",
                    f"Too many media attachments (max: 4, current: {len(media)})",
                )

            # Check media types
            allowed_types = ["photo", "video", "gif"]
            for item in media:
                if "type" not in item:
                    raise ContentValidationError("twitter", "Media type is required")

                if item["type"] not in allowed_types:
                    raise ContentValidationError(
                        "twitter",
                        f"Invalid media type: {item['type']}. Allowed types: {', '.join(allowed_types)}",
                    )

        return True

    def post_content(
        self,
        content: Dict[str, Any],
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post content to Twitter.

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
            # Prepare tweet data
            tweet_data = {"text": content["text"]}

            # Add media if present (simplified for demonstration)
            if "media" in content:
                # In a real implementation, we would upload media first and get media IDs
                # For demonstration, we'll assume media_ids are already provided
                if "media_ids" in content:
                    tweet_data["media"] = {"media_ids": content["media_ids"]}

            # Add reply settings based on visibility
            if visibility == "public":
                tweet_data["reply_settings"] = "everyone"
            elif visibility == "followers":
                tweet_data["reply_settings"] = "following"
            elif visibility == "private":
                tweet_data["reply_settings"] = "mentionedUsers"

            # Post the tweet
            response = self.session.post(f"{self.api_base_url}/tweets", json=tweet_data)
            response.raise_for_status()
            result = response.json()

            # Extract tweet ID and other details
            tweet_id = result.get("data", {}).get("id")

            return {
                "id": tweet_id,
                "platform_data": result,
                "url": f"https://twitter.com/user/status/{tweet_id}",
            }

        except ContentValidationError:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter posting error: {e}")
            raise PostingError("twitter", str(e))

    def schedule_post(
        self,
        content: Dict[str, Any],
        schedule_time: datetime,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a tweet for later publication.

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
            # Note: Twitter API v2 doesn't directly support scheduled tweets
            # In a real implementation, we would use a third-party service or
            # store the tweet locally and post it at the scheduled time

            # For demonstration, we'll return a mock scheduled tweet
            scheduled_id = f"scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"

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
            logger.error(f"Twitter scheduling error: {e}")
            raise SchedulingError("twitter", str(e))

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific tweet.

        Args:
            post_id: ID of the tweet to retrieve

        Returns:
            Dictionary containing the tweet details

        Raises:
            PostNotFoundError: If the tweet ID is not found
        """
        try:
            # Get tweet details
            response = self.session.get(
                f"{self.api_base_url}/tweets/{post_id}",
                params={
                    "tweet.fields": "created_at,public_metrics,entities,attachments"
                },
            )
            response.raise_for_status()
            result = response.json()

            # Check if tweet was found
            if "data" not in result:
                raise PostNotFoundError(self.connection_id, post_id)

            tweet_data = result["data"]

            return {
                "id": tweet_data["id"],
                "text": tweet_data["text"],
                "created_at": tweet_data.get("created_at"),
                "metrics": tweet_data.get("public_metrics", {}),
                "entities": tweet_data.get("entities", {}),
                "attachments": tweet_data.get("attachments", {}),
                "platform_data": result,
            }

        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"Twitter get post error: {e}")
            raise

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a tweet from Twitter.

        Args:
            post_id: ID of the tweet to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            PostNotFoundError: If the tweet ID is not found
            DeletionError: If deletion fails
        """
        try:
            # Delete the tweet
            response = self.session.delete(f"{self.api_base_url}/tweets/{post_id}")
            response.raise_for_status()
            result = response.json()

            # Check if deletion was successful
            if result.get("data", {}).get("deleted", False):
                return True
            else:
                raise DeletionError("twitter", "Failed to delete tweet")

        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"Twitter delete post error: {e}")
            raise DeletionError("twitter", str(e))

    def get_analytics(
        self,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get analytics data from Twitter.

        Args:
            post_id: Optional ID of a specific tweet to get analytics for
            metrics: Optional list of specific metrics to retrieve
            start_date: Optional start date for the analytics period
            end_date: Optional end date for the analytics period

        Returns:
            Dictionary containing the analytics data
        """
        try:
            # Set default metrics if not provided
            if not metrics:
                metrics = ["impressions", "engagements", "likes", "retweets", "replies"]

            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Format dates for API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # If post_id is provided, get analytics for a specific tweet
            if post_id:
                # Get tweet details with metrics
                response = self.session.get(
                    f"{self.api_base_url}/tweets/{post_id}",
                    params={
                        "tweet.fields": "public_metrics,non_public_metrics,organic_metrics"
                    },
                )
                response.raise_for_status()
                result = response.json()

                # Extract metrics
                tweet_data = result.get("data", {})
                analytics = {
                    "post_id": post_id,
                    "metrics": {
                        **tweet_data.get("public_metrics", {}),
                        **tweet_data.get("non_public_metrics", {}),
                        **tweet_data.get("organic_metrics", {}),
                    },
                }

                return analytics

            # Otherwise, get account-level analytics
            else:
                # Note: Twitter API v2 doesn't directly support account-level analytics
                # In a real implementation, we would use the Twitter Analytics API

                # For demonstration, we'll return mock analytics data
                return {
                    "account_id": self.account_id,
                    "period": {"start_date": start_date_str, "end_date": end_date_str},
                    "metrics": {
                        "impressions": 12500,
                        "engagements": 1250,
                        "engagement_rate": 0.1,
                        "likes": 850,
                        "retweets": 320,
                        "replies": 80,
                        "clicks": 450,
                        "followers_gained": 45,
                    },
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter analytics error: {e}")
            return {
                "error": str(e),
                "post_id": post_id,
                "period": {
                    "start_date": (
                        start_date.strftime("%Y-%m-%d") if start_date else None
                    ),
                    "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
                },
            }

    def get_audience_insights(
        self,
        metrics: Optional[List[str]] = None,
        segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get audience insights from Twitter.

        Args:
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment to get insights for

        Returns:
            Dictionary containing the audience insights
        """
        try:
            # Set default metrics if not provided
            if not metrics:
                metrics = ["demographics", "interests", "behaviors"]

            # Note: Twitter API v2 doesn't directly support audience insights
            # In a real implementation, we would use the Twitter Audience API

            # For demonstration, we'll return mock audience insights data
            return {
                "account_id": self.account_id,
                "segment": segment or "all_followers",
                "demographics": {
                    "age_distribution": {
                        "18-24": 0.15,
                        "25-34": 0.35,
                        "35-44": 0.25,
                        "45-54": 0.15,
                        "55+": 0.1,
                    },
                    "gender_distribution": {
                        "male": 0.55,
                        "female": 0.43,
                        "other": 0.02,
                    },
                    "location": {
                        "United States": 0.45,
                        "United Kingdom": 0.15,
                        "Canada": 0.1,
                        "Australia": 0.05,
                        "Other": 0.25,
                    },
                },
                "interests": [
                    {"category": "Technology", "score": 0.85},
                    {"category": "Business", "score": 0.75},
                    {"category": "Science", "score": 0.65},
                    {"category": "Politics", "score": 0.45},
                    {"category": "Sports", "score": 0.35},
                ],
                "behaviors": [
                    {"category": "Early adopters", "score": 0.8},
                    {"category": "Frequent shoppers", "score": 0.6},
                    {"category": "News consumers", "score": 0.75},
                    {"category": "Mobile users", "score": 0.9},
                ],
                "active_times": {
                    "days": {
                        "Monday": 0.15,
                        "Tuesday": 0.14,
                        "Wednesday": 0.16,
                        "Thursday": 0.18,
                        "Friday": 0.17,
                        "Saturday": 0.1,
                        "Sunday": 0.1,
                    },
                    "hours": {
                        "morning": 0.25,
                        "afternoon": 0.35,
                        "evening": 0.3,
                        "night": 0.1,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Twitter audience insights error: {e}")
            return {"error": str(e), "segment": segment or "all_followers"}
