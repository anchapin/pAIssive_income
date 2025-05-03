"""
YouTube adapter for social media integration.

This module provides an adapter for connecting to the YouTube API for uploading videos,
retrieving analytics, and managing YouTube channels.
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


class YouTubeAdapter(BaseSocialMediaAdapter):
    """
    Adapter for YouTube platform integration.
    
    This class implements the BaseSocialMediaAdapter interface for YouTube,
    providing methods for uploading videos, retrieving analytics, and managing
    YouTube channels.
    """
    
    def __init__(self, connection_id: str, connection_data: Dict[str, Any]):
        """
        Initialize the YouTube adapter.
        
        Args:
            connection_id: Unique identifier for the connection
            connection_data: Connection data including credentials and settings
        """
        super().__init__(connection_id, connection_data)
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.access_token = self.credentials.get("access_token")
        self.refresh_token = self.credentials.get("refresh_token")
        self.client_id = self.credentials.get("client_id")
        self.client_secret = self.credentials.get("client_secret")
        self.api_key = self.credentials.get("api_key")
        self.channel_id = self.credentials.get("channel_id")
        self.session = requests.Session()
        
        # Set up authentication if access token is provided
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            self._connected = True
        elif self.api_key:
            # For read-only operations, API key can be used
            self._connected = True
    
    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the YouTube API.
        
        Returns:
            Dictionary containing authentication result and any additional platform data
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # If we already have an access token, verify it
            if self.access_token:
                # Check if the token is valid by getting channel info
                response = self.session.get(
                    f"{self.api_base_url}/channels",
                    params={
                        "part": "snippet",
                        "mine": "true"
                    }
                )
                response.raise_for_status()
                channel_data = response.json()
                
                # Extract channel information
                if "items" in channel_data and len(channel_data["items"]) > 0:
                    channel = channel_data["items"][0]
                    self.channel_id = channel["id"]
                    
                    return {
                        "authenticated": True,
                        "channel_id": channel["id"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"]["description"],
                        "thumbnail_url": channel["snippet"]["thumbnails"]["default"]["url"]
                    }
                else:
                    raise AuthenticationError(
                        "youtube",
                        "No channels found for the authenticated user"
                    )
            
            # If we have API key but no access token, we can only do read-only operations
            elif self.api_key and self.channel_id:
                # Check if the channel exists
                response = requests.get(
                    f"{self.api_base_url}/channels",
                    params={
                        "part": "snippet",
                        "id": self.channel_id,
                        "key": self.api_key
                    }
                )
                response.raise_for_status()
                channel_data = response.json()
                
                # Extract channel information
                if "items" in channel_data and len(channel_data["items"]) > 0:
                    channel = channel_data["items"][0]
                    
                    return {
                        "authenticated": True,
                        "channel_id": channel["id"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"]["description"],
                        "thumbnail_url": channel["snippet"]["thumbnails"]["default"]["url"],
                        "read_only": True
                    }
                else:
                    raise AuthenticationError(
                        "youtube",
                        f"Channel with ID {self.channel_id} not found"
                    )
            
            # If we have refresh token, client ID, and client secret, we can refresh the access token
            elif self.refresh_token and self.client_id and self.client_secret:
                # Refresh the access token
                token_url = "https://oauth2.googleapis.com/token"
                token_data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token"
                }
                
                response = requests.post(token_url, data=token_data)
                response.raise_for_status()
                token_response = response.json()
                
                # Update the access token
                self.access_token = token_response["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                self._connected = True
                
                # Get channel information
                response = self.session.get(
                    f"{self.api_base_url}/channels",
                    params={
                        "part": "snippet",
                        "mine": "true"
                    }
                )
                response.raise_for_status()
                channel_data = response.json()
                
                # Extract channel information
                if "items" in channel_data and len(channel_data["items"]) > 0:
                    channel = channel_data["items"][0]
                    self.channel_id = channel["id"]
                    
                    return {
                        "authenticated": True,
                        "channel_id": channel["id"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"]["description"],
                        "thumbnail_url": channel["snippet"]["thumbnails"]["default"]["url"],
                        "access_token": self.access_token,
                        "token_type": token_response["token_type"],
                        "expires_in": token_response["expires_in"]
                    }
                else:
                    raise AuthenticationError(
                        "youtube",
                        "No channels found for the authenticated user"
                    )
            
            else:
                raise AuthenticationError(
                    "youtube",
                    "Missing required credentials (access_token, api_key, or refresh_token with client_id and client_secret)"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube authentication error: {e}")
            raise AuthenticationError("youtube", str(e))
    
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """
        Validate content for posting to YouTube.
        
        Args:
            content: Content to validate
            
        Returns:
            True if content is valid, False otherwise
            
        Raises:
            ContentValidationError: If content validation fails with specific reason
        """
        # Check if we have a video
        if "video" not in content:
            raise ContentValidationError(
                "youtube", 
                "Video is required for YouTube posts"
            )
        
        # Check video source
        if "url" not in content["video"] and "source" not in content["video"] and "file_path" not in content["video"]:
            raise ContentValidationError(
                "youtube",
                "Video must have either a URL, source, or file_path"
            )
        
        # Check title
        if "title" not in content:
            raise ContentValidationError(
                "youtube",
                "Title is required for YouTube videos"
            )
        
        # Check title length (YouTube's limit is 100 characters)
        if len(content["title"]) > 100:
            raise ContentValidationError(
                "youtube", 
                f"Title exceeds 100 characters (current: {len(content['title'])})"
            )
        
        # Check description length if present (YouTube's limit is 5,000 characters)
        if "description" in content and len(content["description"]) > 5000:
            raise ContentValidationError(
                "youtube", 
                f"Description exceeds 5,000 characters (current: {len(content['description'])})"
            )
        
        # Check tags if present (YouTube allows up to 500 characters total for tags)
        if "tags" in content:
            if not isinstance(content["tags"], list):
                raise ContentValidationError(
                    "youtube",
                    "Tags must be a list of strings"
                )
            
            total_tags_length = sum(len(tag) for tag in content["tags"]) + len(content["tags"]) - 1
            if total_tags_length > 500:
                raise ContentValidationError(
                    "youtube",
                    f"Total tags length exceeds 500 characters (current: {total_tags_length})"
                )
        
        # Check category ID if present
        if "category_id" in content and not isinstance(content["category_id"], str):
            raise ContentValidationError(
                "youtube",
                "Category ID must be a string"
            )
        
        # Check privacy status if present
        if "privacy_status" in content and content["privacy_status"] not in ["public", "unlisted", "private"]:
            raise ContentValidationError(
                "youtube",
                f"Invalid privacy status: {content['privacy_status']}. Allowed values: public, unlisted, private"
            )
        
        return True
    
    def post_content(
        self,
        content: Dict[str, Any],
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Post content to YouTube.
        
        Args:
            content: Content to post
            visibility: Visibility setting (public, unlisted, private)
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
                raise PostingError("youtube", "Access token is required for posting videos")
            
            # Map visibility to YouTube privacy status
            privacy_status = content.get("privacy_status", self._map_visibility(visibility))
            
            # In a real implementation, we would:
            # 1. Upload the video file to YouTube using the resumable upload API
            # 2. Set the video metadata (title, description, tags, etc.)
            # 3. Publish the video
            
            # For demonstration, we'll simulate a successful upload
            video_id = f"youtube_video_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                "id": video_id,
                "status": "uploaded",
                "posted_at": datetime.now().isoformat(),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "platform_data": {
                    "video_id": video_id,
                    "title": content["title"],
                    "description": content.get("description", ""),
                    "tags": content.get("tags", []),
                    "category_id": content.get("category_id", "22"),  # Default to "People & Blogs"
                    "privacy_status": privacy_status
                }
            }
            
        except ContentValidationError:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube posting error: {e}")
            raise PostingError("youtube", str(e))
    
    def _map_visibility(self, visibility: str) -> str:
        """
        Map visibility setting to YouTube privacy status.
        
        Args:
            visibility: Visibility setting (public, private, etc.)
            
        Returns:
            YouTube privacy status
        """
        if visibility == "public":
            return "public"
        elif visibility == "unlisted":
            return "unlisted"
        else:  # private
            return "private"
    
    def schedule_post(
        self,
        content: Dict[str, Any],
        schedule_time: datetime,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a video for later publication on YouTube.
        
        Args:
            content: Content to post
            schedule_time: Time to publish the video
            visibility: Visibility setting (public, unlisted, private)
            targeting: Optional audience targeting parameters
            
        Returns:
            Dictionary containing the scheduled video details and ID
            
        Raises:
            ContentValidationError: If content validation fails
            SchedulingError: If scheduling fails
        """
        # Validate content first
        self.validate_content(content)
        
        try:
            # Check if we have an access token (required for posting)
            if not self.access_token:
                raise SchedulingError("youtube", "Access token is required for scheduling videos")
            
            # Map visibility to YouTube privacy status
            privacy_status = content.get("privacy_status", self._map_visibility(visibility))
            
            # In a real implementation, we would:
            # 1. Upload the video file to YouTube using the resumable upload API
            # 2. Set the video metadata (title, description, tags, etc.)
            # 3. Set the publishAt parameter to schedule the video
            
            # For demonstration, we'll simulate a successful scheduling
            video_id = f"youtube_scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                "id": video_id,
                "scheduled_time": schedule_time.isoformat(),
                "status": "scheduled",
                "platform_data": {
                    "video_id": video_id,
                    "title": content["title"],
                    "description": content.get("description", ""),
                    "tags": content.get("tags", []),
                    "category_id": content.get("category_id", "22"),  # Default to "People & Blogs"
                    "privacy_status": privacy_status,
                    "publish_at": schedule_time.isoformat()
                }
            }
            
        except ContentValidationError:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube scheduling error: {e}")
            raise SchedulingError("youtube", str(e))
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific YouTube video.
        
        Args:
            post_id: ID of the video to retrieve
            
        Returns:
            Dictionary containing the video details
            
        Raises:
            PostNotFoundError: If the video ID is not found
        """
        try:
            # Determine the authentication method
            params = {
                "part": "snippet,statistics,status",
                "id": post_id
            }
            
            if self.access_token:
                # Use OAuth authentication
                response = self.session.get(
                    f"{self.api_base_url}/videos",
                    params=params
                )
            elif self.api_key:
                # Use API key authentication
                params["key"] = self.api_key
                response = requests.get(
                    f"{self.api_base_url}/videos",
                    params=params
                )
            else:
                raise PostingError("youtube", "Either access token or API key is required")
            
            response.raise_for_status()
            result = response.json()
            
            # Check if video was found
            if "items" not in result or len(result["items"]) == 0:
                raise PostNotFoundError(self.connection_id, post_id)
            
            # Extract video data
            video = result["items"][0]
            snippet = video["snippet"]
            statistics = video["statistics"]
            status = video["status"]
            
            return {
                "id": video["id"],
                "title": snippet["title"],
                "description": snippet["description"],
                "published_at": snippet["publishedAt"],
                "thumbnail_url": snippet["thumbnails"]["default"]["url"],
                "channel_id": snippet["channelId"],
                "channel_title": snippet["channelTitle"],
                "tags": snippet.get("tags", []),
                "category_id": snippet["categoryId"],
                "privacy_status": status["privacyStatus"],
                "views": int(statistics.get("viewCount", 0)),
                "likes": int(statistics.get("likeCount", 0)),
                "dislikes": int(statistics.get("dislikeCount", 0)) if "dislikeCount" in statistics else 0,
                "comments": int(statistics.get("commentCount", 0)),
                "url": f"https://www.youtube.com/watch?v={video['id']}",
                "platform_data": video
            }
            
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"YouTube get video error: {e}")
            raise
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a video from YouTube.
        
        Args:
            post_id: ID of the video to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            PostNotFoundError: If the video ID is not found
            DeletionError: If deletion fails
        """
        try:
            # Check if we have an access token (required for deletion)
            if not self.access_token:
                raise DeletionError("youtube", "Access token is required for deleting videos")
            
            # Delete the video
            response = self.session.delete(
                f"{self.api_base_url}/videos",
                params={"id": post_id}
            )
            response.raise_for_status()
            
            # YouTube returns 204 No Content on successful deletion
            return response.status_code == 204
            
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                raise PostNotFoundError(self.connection_id, post_id)
            logger.error(f"YouTube delete video error: {e}")
            raise DeletionError("youtube", str(e))
    
    def get_analytics(
        self,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get analytics data from YouTube.
        
        Args:
            post_id: Optional ID of a specific video to get analytics for
            metrics: Optional list of specific metrics to retrieve
            start_date: Optional start date for the analytics period
            end_date: Optional end date for the analytics period
            
        Returns:
            Dictionary containing the analytics data
        """
        try:
            # Check if we have an access token (required for analytics)
            if not self.access_token:
                raise PostingError("youtube", "Access token is required for analytics")
            
            # Set default metrics if not provided
            if not metrics:
                metrics = [
                    "views", "likes", "dislikes", "comments", "shares",
                    "averageViewDuration", "averageViewPercentage"
                ]
            
            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Format dates for API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # If post_id is provided, get analytics for a specific video
            if post_id:
                # In a real implementation, we would use the YouTube Analytics API
                # For demonstration, we'll return mock analytics data
                return {
                    "video_id": post_id,
                    "period": {
                        "start_date": start_date_str,
                        "end_date": end_date_str
                    },
                    "metrics": {
                        "views": 1250,
                        "likes": 85,
                        "dislikes": 5,
                        "comments": 32,
                        "shares": 18,
                        "averageViewDuration": 125,  # seconds
                        "averageViewPercentage": 65  # percent
                    }
                }
            
            # Otherwise, get channel-level analytics
            else:
                # In a real implementation, we would use the YouTube Analytics API
                # For demonstration, we'll return mock analytics data
                return {
                    "channel_id": self.channel_id,
                    "period": {
                        "start_date": start_date_str,
                        "end_date": end_date_str
                    },
                    "metrics": {
                        "views": 25000,
                        "watch_time": 750000,  # seconds
                        "subscribers_gained": 350,
                        "subscribers_lost": 50,
                        "likes": 1500,
                        "dislikes": 75,
                        "comments": 620,
                        "shares": 280,
                        "average_view_duration": 180,  # seconds
                        "average_view_percentage": 55  # percent
                    }
                }
                
        except Exception as e:
            logger.error(f"YouTube analytics error: {e}")
            return {
                "error": str(e),
                "video_id": post_id,
                "channel_id": self.channel_id,
                "period": {
                    "start_date": start_date_str if start_date else None,
                    "end_date": end_date_str if end_date else None
                }
            }
    
    def get_audience_insights(
        self,
        metrics: Optional[List[str]] = None,
        segment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get audience insights from YouTube.
        
        Args:
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment to get insights for
            
        Returns:
            Dictionary containing the audience insights
        """
        try:
            # Check if we have an access token (required for audience insights)
            if not self.access_token:
                raise PostingError("youtube", "Access token is required for audience insights")
            
            # Set default metrics if not provided
            if not metrics:
                metrics = ["demographics", "geography", "devices", "traffic_sources"]
            
            # In a real implementation, we would use the YouTube Analytics API
            # For demonstration, we'll return mock audience insights data
            return {
                "channel_id": self.channel_id,
                "segment": segment or "all_viewers",
                "demographics": {
                    "age_gender": {
                        "13-17": {
                            "male": 0.05,
                            "female": 0.03,
                            "other": 0.01
                        },
                        "18-24": {
                            "male": 0.20,
                            "female": 0.15,
                            "other": 0.02
                        },
                        "25-34": {
                            "male": 0.25,
                            "female": 0.15,
                            "other": 0.01
                        },
                        "35-44": {
                            "male": 0.08,
                            "female": 0.04,
                            "other": 0.01
                        },
                        "45-54": {
                            "male": 0.03,
                            "female": 0.02,
                            "other": 0.00
                        },
                        "55+": {
                            "male": 0.02,
                            "female": 0.01,
                            "other": 0.00
                        }
                    }
                },
                "geography": {
                    "countries": {
                        "United States": 0.40,
                        "United Kingdom": 0.12,
                        "Canada": 0.08,
                        "Australia": 0.05,
                        "Germany": 0.04,
                        "India": 0.04,
                        "Other": 0.27
                    }
                },
                "devices": {
                    "mobile": 0.65,
                    "desktop": 0.25,
                    "tablet": 0.05,
                    "tv": 0.04,
                    "game_console": 0.01
                },
                "traffic_sources": {
                    "youtube_search": 0.30,
                    "suggested_videos": 0.25,
                    "external": 0.20,
                    "browse_features": 0.15,
                    "playlist": 0.05,
                    "notifications": 0.03,
                    "other": 0.02
                },
                "watch_time": {
                    "average_view_duration": 180,  # seconds
                    "average_view_percentage": 55,  # percent
                    "peak_viewing_times": {
                        "weekdays": {
                            "morning": 0.15,
                            "afternoon": 0.25,
                            "evening": 0.45,
                            "night": 0.15
                        },
                        "weekends": {
                            "morning": 0.10,
                            "afternoon": 0.30,
                            "evening": 0.40,
                            "night": 0.20
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"YouTube audience insights error: {e}")
            return {
                "error": str(e),
                "channel_id": self.channel_id,
                "segment": segment or "all_viewers"
            }
