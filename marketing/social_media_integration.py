"""
Social media integration module for the pAIssive Income project.

This module provides functionality for integrating with various social media platforms
for content posting, analytics tracking, and audience insights.
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import importlib
from pathlib import Path

# Local imports
from interfaces.marketing_interfaces import ISocialMediaIntegration
from marketing.errors import (
    PlatformNotSupportedError,
    PlatformNotFoundError,
    AuthenticationError,
    ContentValidationError,
    PostNotFoundError,
    PostingError,
    DeletionError,
    SchedulingError,
    NotSupportedError,
)
from marketing.schemas import (
    SocialMediaPlatform,
    SocialMediaConnectionSchema,
    SocialMediaAuthSchema,
    SocialMediaPostSchema,
    SocialMediaAnalyticsSchema,
    SocialMediaCampaignSchema,
    AudienceInsightSchema,
    ContentVisibility,
    PostScheduleType,
)

# Configure logging
logger = logging.getLogger(__name__)

# Define constants
SUPPORTED_PLATFORMS = {
    SocialMediaPlatform.TWITTER: {
        "name": "Twitter",
        "capabilities": [
            "post_text",
            "post_media",
            "analytics",
            "audience_insights",
            "scheduling",
        ],
        "adapter_module": "marketing.social_media_adapters.twitter_adapter",
    },
    SocialMediaPlatform.FACEBOOK: {
        "name": "Facebook",
        "capabilities": [
            "post_text",
            "post_media",
            "post_link",
            "analytics",
            "audience_insights",
            "scheduling",
        ],
        "adapter_module": "marketing.social_media_adapters.facebook_adapter",
    },
    SocialMediaPlatform.INSTAGRAM: {
        "name": "Instagram",
        "capabilities": ["post_media", "post_story", "analytics", "audience_insights"],
        "adapter_module": "marketing.social_media_adapters.instagram_adapter",
    },
    SocialMediaPlatform.LINKEDIN: {
        "name": "LinkedIn",
        "capabilities": [
            "post_text",
            "post_media",
            "post_article",
            "analytics",
            "audience_insights",
            "scheduling",
        ],
        "adapter_module": "marketing.social_media_adapters.linkedin_adapter",
    },
    SocialMediaPlatform.YOUTUBE: {
        "name": "YouTube",
        "capabilities": ["post_video", "analytics", "audience_insights", "scheduling"],
        "adapter_module": "marketing.social_media_adapters.youtube_adapter",
    },
    SocialMediaPlatform.PINTEREST: {
        "name": "Pinterest",
        "capabilities": ["post_pin", "analytics", "audience_insights", "scheduling"],
        "adapter_module": "marketing.social_media_adapters.pinterest_adapter",
    },
    SocialMediaPlatform.TIKTOK: {
        "name": "TikTok",
        "capabilities": ["post_video", "analytics", "audience_insights"],
        "adapter_module": "marketing.social_media_adapters.tiktok_adapter",
    },
}


class SocialMediaIntegration(ISocialMediaIntegration):
    """
    Class for integrating with social media platforms.

    This class provides functionality to:
    1. Connect to various social media platforms
    2. Post content to connected platforms
    3. Retrieve analytics data from platforms
    4. Schedule content for posting
    5. Retrieve audience insights
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the social media integration.

        Args:
            storage_path: Optional path to store connection data. If None, data will be stored
                          in memory only.
        """
        self.connections = {}
        self.platform_adapters = {}
        self.posts = {}
        self.campaigns = {}
        self.storage_path = storage_path

        # Create storage directory if it doesn't exist
        if storage_path and not os.path.exists(storage_path):
            os.makedirs(storage_path)

        # Load existing data if available
        if storage_path:
            self._load_connections()
            self._load_posts()
            self._load_campaigns()

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
            return

        connections_path = os.path.join(self.storage_path, "connections.json")
        try:
            with open(connections_path, "w", encoding="utf-8") as file:
                json.dump(self.connections, file, indent=2)
        except Exception as e:
            logger.error(f"Error saving social media connections: {e}")

    def _save_posts(self):
        """Save posts data to storage."""
        if not self.storage_path:
            return

        posts_path = os.path.join(self.storage_path, "posts.json")
        try:
            with open(posts_path, "w", encoding="utf-8") as file:
                json.dump(self.posts, file, indent=2)
        except Exception as e:
            logger.error(f"Error saving social media posts: {e}")

    def _save_campaigns(self):
        """Save campaigns data to storage."""
        if not self.storage_path:
            return

        campaigns_path = os.path.join(self.storage_path, "campaigns.json")
        try:
            with open(campaigns_path, "w", encoding="utf-8") as file:
                json.dump(self.campaigns, file, indent=2)
        except Exception as e:
            logger.error(f"Error saving social media campaigns: {e}")

    def _init_platform_adapter(self, platform: str, connection_id: str):
        """
        Initialize a platform adapter for a connection.

        Args:
            platform: Social media platform name
            connection_id: Connection ID

        Returns:
            Platform adapter instance

        Raises:
            PlatformNotSupportedError: If the platform is not supported
            ImportError: If the adapter module cannot be imported
        """
        if platform not in SUPPORTED_PLATFORMS:
            raise PlatformNotSupportedError(platform)

        adapter_module_path = SUPPORTED_PLATFORMS[platform]["adapter_module"]

        try:
            # Check if adapter is already loaded
            if connection_id not in self.platform_adapters:
                # Use importlib to dynamically import the adapter
                module_name = adapter_module_path
                adapter_module = importlib.import_module(module_name)

                # Get the adapter class (should be the first class in the module)
                adapter_class = None
                for attr_name in dir(adapter_module):
                    attr = getattr(adapter_module, attr_name)
                    if (
                        isinstance(attr, type)
                        and attr.__module__ == adapter_module.__name__
                    ):
                        adapter_class = attr
                        break

                if not adapter_class:
                    raise ImportError(
                        f"Could not find adapter class in {adapter_module_path}"
                    )

                # Create instance of adapter
                connection_data = self.connections[connection_id]
                adapter = adapter_class(
                    connection_id=connection_id, connection_data=connection_data
                )

                # Store adapter
                self.platform_adapters[connection_id] = adapter

            return self.platform_adapters[connection_id]

        except ImportError as e:
            logger.error(f"Could not import adapter module for {platform}: {e}")
            if platform not in SUPPORTED_PLATFORMS:
                raise PlatformNotSupportedError(platform)
            else:
                # Still raise but with the original exception
                raise

    def _generate_platform_id(self, platform: str) -> str:
        """
        Generate a unique platform connection ID.

        Args:
            platform: Social media platform name

        Returns:
            Unique platform connection ID
        """
        return f"{platform}_{uuid.uuid4().hex[:8]}"

    def connect_platform(
        self,
        platform: str,
        credentials: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Connect to a social media platform with provided credentials.

        Args:
            platform: Social media platform name (e.g., "twitter", "facebook", "linkedin")
            credentials: Platform-specific authentication credentials
            settings: Optional platform-specific settings

        Returns:
            Dictionary containing the connection details

        Raises:
            PlatformNotSupportedError: If the platform is not supported
            AuthenticationError: If authentication fails
        """
        # Check if the platform is supported
        if platform not in SUPPORTED_PLATFORMS:
            raise PlatformNotSupportedError(platform)

        # Generate a unique connection ID
        connection_id = self._generate_platform_id(platform)

        # Create connection object
        connection = {
            "id": connection_id,
            "platform": platform,
            "account_name": credentials.get("account_name", "Unknown"),
            "account_id": credentials.get("account_id", "Unknown"),
            "profile_url": credentials.get("profile_url"),
            "connected_at": datetime.now().isoformat(),
            "last_synced_at": None,
            "status": "active",
            "settings": settings or {},
            "capabilities": SUPPORTED_PLATFORMS[platform]["capabilities"],
            "credentials": credentials,
        }

        # Store the connection
        self.connections[connection_id] = connection

        # Initialize the platform adapter
        adapter = self._init_platform_adapter(platform, connection_id)

        # Verify credentials with the adapter
        try:
            verified_connection = adapter.verify_credentials()

            # Update connection with verified data
            self.connections[connection_id].update(
                {
                    "account_name": verified_connection.get(
                        "account_name", connection["account_name"]
                    ),
                    "account_id": verified_connection.get(
                        "account_id", connection["account_id"]
                    ),
                    "profile_url": verified_connection.get(
                        "profile_url", connection["profile_url"]
                    ),
                    "verified": True,
                }
            )

            # Save connections
            self._save_connections()

            # Return the connection without credentials for security
            connection_copy = self.connections[connection_id].copy()
            connection_copy.pop("credentials", None)
            return connection_copy

        except Exception as e:
            # Remove the connection on failure
            self.connections.pop(connection_id, None)
            if hasattr(e, "platform") and hasattr(e, "message"):
                raise e
            else:
                raise AuthenticationError(platform, str(e))

    def disconnect_platform(self, platform_id: str) -> bool:
        """
        Disconnect from a connected social media platform.

        Args:
            platform_id: ID of the connected platform

        Returns:
            True if disconnected successfully, False otherwise

        Raises:
            PlatformNotFoundError: If the platform ID is not found
        """
        # Check if the platform connection exists
        if platform_id not in self.connections:
            raise PlatformNotFoundError(platform_id)

        try:
            # If adapter exists, call its disconnect method
            if platform_id in self.platform_adapters:
                adapter = self.platform_adapters[platform_id]
                adapter.disconnect()
                del self.platform_adapters[platform_id]

            # Remove the connection
            del self.connections[platform_id]

            # Save connections
            self._save_connections()

            return True
        except Exception as e:
            logger.error(f"Error disconnecting from platform {platform_id}: {e}")
            return False

    def get_connected_platforms(self) -> List[Dict[str, Any]]:
        """
        Get a list of connected social media platforms.

        Returns:
            List of dictionaries containing connected platform details
        """
        # Return all connections without credentials
        return [
            {k: v for k, v in connection.items() if k != "credentials"}
            for connection in self.connections.values()
        ]

    def post_content(
        self,
        platform_id: str,
        content: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post content to a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            content: Content to post (text, media, etc.)
            schedule_time: Optional time to schedule the post for
            visibility: Visibility setting (public, private, etc.)
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and ID

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            ContentValidationError: If the content is invalid
            PostingError: If posting fails
        """
        # Check if the platform connection exists
        if platform_id not in self.connections:
            raise PlatformNotFoundError(platform_id)

        # Get the platform adapter
        adapter = self._init_platform_adapter(
            self.connections[platform_id]["platform"], platform_id
        )

        # Prepare the post content
        post_data = {
            "platform_id": platform_id,
            "content": content,
            "schedule_time": schedule_time.isoformat() if schedule_time else None,
            "schedule_type": (
                PostScheduleType.SCHEDULED if schedule_time else PostScheduleType.NOW
            ),
            "visibility": visibility,
            "targeting": targeting,
            "status": "scheduled" if schedule_time else "pending",
            "created_at": datetime.now().isoformat(),
        }

        try:
            # Validate the content
            adapter.validate_content(content)

            # If scheduled for the future
            if schedule_time and schedule_time > datetime.now():
                # Generate local post ID
                post_id = f"post_{uuid.uuid4().hex}"
                post_data["id"] = post_id

                # Store the scheduled post
                if platform_id not in self.posts:
                    self.posts[platform_id] = {}

                self.posts[platform_id][post_id] = post_data
                self._save_posts()

                return {
                    "id": post_id,
                    "platform_id": platform_id,
                    "status": "scheduled",
                    "schedule_time": post_data["schedule_time"],
                    "created_at": post_data["created_at"],
                }
            else:
                # Post immediately
                result = adapter.post_content(content, visibility, targeting)

                # Store the post with the platform-assigned ID
                post_id = result["id"]
                post_data["id"] = post_id
                post_data["status"] = "posted"
                post_data["posted_at"] = datetime.now().isoformat()
                post_data["platform_data"] = result.get("platform_data", {})

                if platform_id not in self.posts:
                    self.posts[platform_id] = {}

                self.posts[platform_id][post_id] = post_data
                self._save_posts()

                return {
                    "id": post_id,
                    "platform_id": platform_id,
                    "status": "posted",
                    "posted_at": post_data["posted_at"],
                    "created_at": post_data["created_at"],
                    "platform_data": result.get("platform_data", {}),
                }

        except ContentValidationError:
            raise
        except Exception as e:
            raise PostingError(self.connections[platform_id]["platform"], str(e))

    def get_post(self, platform_id: str, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific post.

        Args:
            platform_id: ID of the connected platform
            post_id: ID of the post to retrieve

        Returns:
            Dictionary containing the post details

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            PostNotFoundError: If the post ID is not found
        """
        # Check if the platform connection exists
        if platform_id not in self.connections:
            raise PlatformNotFoundError(platform_id)

        # Check if we have the post locally
        if platform_id in self.posts and post_id in self.posts[platform_id]:
            post_data = self.posts[platform_id][post_id]

            # If post was already posted, try to get latest data from platform
            if post_data["status"] == "posted":
                try:
                    adapter = self._init_platform_adapter(
                        self.connections[platform_id]["platform"], platform_id
                    )

                    # Get updated post data from the platform
                    updated_post = adapter.get_post(post_id)
                    post_data["platform_data"] = updated_post
                    self._save_posts()
                except Exception as e:
                    logger.warning(
                        f"Could not get updated post data for {post_id}: {e}"
                    )

            return post_data

        # If not found locally, try to get from platform
        try:
            adapter = self._init_platform_adapter(
                self.connections[platform_id]["platform"], platform_id
            )

            post_data = adapter.get_post(post_id)

            # Store the post
            if platform_id not in self.posts:
                self.posts[platform_id] = {}

            self.posts[platform_id][post_id] = {
                "id": post_id,
                "platform_id": platform_id,
                "status": "posted",
                "platform_data": post_data,
                "created_at": post_data.get("created_time", datetime.now().isoformat()),
            }

            self._save_posts()
            return self.posts[platform_id][post_id]

        except Exception as e:
            raise PostNotFoundError(platform_id, post_id)

    def delete_post(self, platform_id: str, post_id: str) -> bool:
        """
        Delete a post from a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            post_id: ID of the post to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            PostNotFoundError: If the post ID is not found
            DeletionError: If deletion fails
        """
        # Check if the platform connection exists
        if platform_id not in self.connections:
            raise PlatformNotFoundError(platform_id)

        # Check if we have the post locally
        post_exists_locally = (
            platform_id in self.posts and post_id in self.posts[platform_id]
        )

        # If it's a scheduled post that hasn't been posted yet
        if (
            post_exists_locally
            and self.posts[platform_id][post_id]["status"] == "scheduled"
        ):
            # Just remove it from our storage
            del self.posts[platform_id][post_id]
            self._save_posts()
            return True

        # Otherwise, we need to delete from the platform
        try:
            adapter = self._init_platform_adapter(
                self.connections[platform_id]["platform"], platform_id
            )

            result = adapter.delete_post(post_id)

            # If successfully deleted from platform, remove from local storage
            if post_exists_locally:
                del self.posts[platform_id][post_id]
                self._save_posts()

            return result

        except Exception as e:
            raise DeletionError(
                self.connections[platform_id]["platform"], post_id, str(e)
            )

    def get_analytics(
        self,
        platform_id: str,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "day",
    ) -> Dict[str, Any]:
        """
        Get analytics for posts on a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            post_id: Optional ID of a specific post to get analytics for
            metrics: Optional list of specific metrics to retrieve
            start_date: Optional start date for analytics data
            end_date: Optional end date for analytics data
            granularity: Time granularity for data (day, week, month)

        Returns:
            Dictionary containing analytics data

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            PostNotFoundError: If the post ID is not found
            InvalidParameterError: If parameters are invalid
        """
        # Check if the platform connection exists
        if platform_id not in self.connections:
            raise PlatformNotFoundError(platform_id)

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()

        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Check if analytics is supported
        platform = self.connections[platform_id]["platform"]
        capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]

        if "analytics" not in capabilities:
            raise NotSupportedError(platform, "analytics")

        # Get the platform adapter
        adapter = self._init_platform_adapter(platform, platform_id)

        try:
            # Get analytics data from the platform
            analytics_data = adapter.get_analytics(
                post_id=post_id,
                metrics=metrics,
                start_date=start_date,
                end_date=end_date,
                granularity=granularity,
            )

            # Format the results
            result = {
                "platform_id": platform_id,
                "post_id": post_id,
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "granularity": granularity,
                "metrics": analytics_data.get("metrics", {}),
                "aggregates": analytics_data.get("aggregates", {}),
                "insights": analytics_data.get("insights", []),
            }

            return result

        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting analytics from {platform}: {e}")
            return {
                "platform_id": platform_id,
                "post_id": post_id,
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "granularity": granularity,
                "metrics": {},
                "aggregates": {},
                "insights": [],
                "error": str(e),
            }

    def schedule_campaign(
        self,
        platform_ids: List[str],
        campaign_name: str,
        content_items: List[Dict[str, Any]],
        schedule_settings: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a social media campaign with multiple content items.

        Args:
            platform_ids: List of connected platform IDs
            campaign_name: Name of the campaign
            content_items: List of content items to post
            schedule_settings: Settings for content scheduling
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the campaign details and scheduled post IDs

        Raises:
            PlatformNotFoundError: If a platform ID is not found
            ContentValidationError: If content validation fails
            SchedulingError: If scheduling fails
        """
        # Check if all platform IDs exist
        for platform_id in platform_ids:
            if platform_id not in self.connections:
                raise PlatformNotFoundError(platform_id)

        # Check if scheduling is supported for all platforms
        for platform_id in platform_ids:
            platform = self.connections[platform_id]["platform"]
            capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]

            if "scheduling" not in capabilities:
                raise NotSupportedError(platform, "scheduling")

        # Validate all content items
        for platform_id in platform_ids:
            adapter = self._init_platform_adapter(
                self.connections[platform_id]["platform"], platform_id
            )

            # Validate each content item for this platform
            for content_item in content_items:
                try:
                    adapter.validate_content(content_item)
                except ContentValidationError as e:
                    raise ContentValidationError(
                        self.connections[platform_id]["platform"],
                        f"Invalid content for item: {str(e)}",
                    )

        # Generate a campaign ID
        campaign_id = f"campaign_{uuid.uuid4().hex}"

        # Handle schedule settings
        start_date = datetime.fromisoformat(schedule_settings.get("start_date"))
        end_date = None
        if "end_date" in schedule_settings:
            end_date = datetime.fromisoformat(schedule_settings["end_date"])

        schedule_type = schedule_settings.get("type", "spread")

        # Calculate post times based on schedule settings
        scheduled_posts = {}

        if schedule_type == "spread":
            # Distribute posts evenly between start and end date
            if not end_date:
                end_date = start_date + timedelta(days=30)  # Default to 30 days

            total_duration = (end_date - start_date).total_seconds()
            interval = total_duration / (len(content_items) + 1)

            for i, content_item in enumerate(content_items):
                post_time = start_date + timedelta(seconds=(i + 1) * interval)

                for platform_id in platform_ids:
                    try:
                        post_result = self.post_content(
                            platform_id=platform_id,
                            content=content_item,
                            schedule_time=post_time,
                            visibility=content_item.get("visibility", "public"),
                            targeting=targeting,
                        )

                        if platform_id not in scheduled_posts:
                            scheduled_posts[platform_id] = []

                        scheduled_posts[platform_id].append(post_result["id"])

                    except Exception as e:
                        logger.error(f"Error scheduling post to {platform_id}: {e}")
                        raise SchedulingError(
                            f"Error scheduling to {platform_id}: {str(e)}"
                        )

        elif schedule_type == "best_time":
            # Schedule at optimal times (would need platform-specific logic)
            raise NotImplementedError("Best time scheduling not yet implemented")

        else:
            # Custom schedule or other types
            raise SchedulingError(f"Unsupported schedule type: {schedule_type}")

        # Create campaign object
        campaign = {
            "id": campaign_id,
            "name": campaign_name,
            "platform_ids": platform_ids,
            "content_items": content_items,
            "schedule_settings": schedule_settings,
            "targeting": targeting,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "status": "scheduled",
            "scheduled_posts": scheduled_posts,
            "created_at": datetime.now().isoformat(),
        }

        # Store the campaign
        self.campaigns[campaign_id] = campaign
        self._save_campaigns()

        return campaign

    def get_audience_insights(
        self,
        platform_id: str,
        metrics: Optional[List[str]] = None,
        segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get audience insights from a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment parameters

        Returns:
            Dictionary containing audience insights data

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            InvalidParameterError: If parameters are invalid
            NotSupportedError: If the platform doesn't support audience insights
        """
        # Check if the platform connection exists
        if platform_id not in self.connections:
            raise PlatformNotFoundError(platform_id)

        # Check if audience insights is supported
        platform = self.connections[platform_id]["platform"]
        capabilities = SUPPORTED_PLATFORMS[platform]["capabilities"]

        if "audience_insights" not in capabilities:
            raise NotSupportedError(platform, "audience_insights")

        # Get the platform adapter
        adapter = self._init_platform_adapter(platform, platform_id)

        try:
            # Get audience insights from the platform
            insights = adapter.get_audience_insights(metrics, segment)

            # Format the results
            result = {
                "platform_id": platform_id,
                "segment": segment,
                "demographics": insights.get("demographics"),
                "interests": insights.get("interests"),
                "behaviors": insights.get("behaviors"),
                "engagement_metrics": insights.get("engagement_metrics"),
                "active_times": insights.get("active_times"),
                "insights": insights.get("insights", []),
            }

            return result

        except Exception as e:
            logger.error(f"Error getting audience insights from {platform}: {e}")
            return {"platform_id": platform_id, "segment": segment, "error": str(e)}

    # Additional methods that could be implemented:
    # - get_campaigns() - Get list of campaigns
    # - get_campaign(campaign_id) - Get campaign details
    # - update_campaign(campaign_id, ...) - Update campaign
    # - delete_campaign(campaign_id) - Delete campaign
