"""
Example usage of the social media integration module.

This script demonstrates how to use the SocialMediaIntegration class to connect to
various social media platforms, post content, and retrieve analytics.
"""


import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path



from marketing import SocialMediaIntegration, SocialMediaPlatform



# Add the parent directory to the path to import the marketing module
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the social media integration example."""
    # Create a directory for storing connection data
    storage_path = Path("./data/social_media")
    storage_path.mkdir(parents=True, exist_ok=True)

    # Initialize the social media integration
    social_media = SocialMediaIntegration(storage_path=str(storage_path))

    # Example: Connect to Twitter
    try:
        twitter_credentials = {
            "api_key": "YOUR_API_KEY",
            "api_secret": "YOUR_API_SECRET",
            "access_token": "YOUR_ACCESS_TOKEN",
            "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET",
            "account_name": "YourTwitterHandle",
            "account_id": "YourTwitterID",
        }

        twitter_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.TWITTER, credentials=twitter_credentials
        )

        logger.info(f"Connected to Twitter: {twitter_connection['id']}")

        # Example: Post a tweet
        tweet_content = {
            "text": "This is a test tweet from the pAIssive Income social media integration module!"
        }

        tweet_result = social_media.post_content(
            platform_id=twitter_connection["id"], content=tweet_content
        )

        logger.info(f"Posted tweet: {tweet_result['id']}")
        logger.info(f"Tweet URL: {tweet_result.get('platform_data', {}).get('url')}")

        # Example: Get analytics for the tweet
        analytics = social_media.get_analytics(
            platform_id=twitter_connection["id"], post_id=tweet_result["id"]
        )

        logger.info(f"Tweet analytics: {json.dumps(analytics, indent=2)}")

        # Example: Get audience insights
        insights = social_media.get_audience_insights(
            platform_id=twitter_connection["id"]
        )

        logger.info(f"Audience insights: {json.dumps(insights, indent=2)}")

    except Exception as e:
        logger.error(f"Error in Twitter example: {e}")

    # Example: Connect to Facebook
    try:
        facebook_credentials = {
            "access_token": "YOUR_FACEBOOK_ACCESS_TOKEN",
            "page_id": "YOUR_FACEBOOK_PAGE_ID",
            "account_name": "Your Facebook Page",
            "account_id": "YourFacebookID",
        }

        facebook_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.FACEBOOK, credentials=facebook_credentials
        )

        logger.info(f"Connected to Facebook: {facebook_connection['id']}")

        # Example: Post to Facebook
        facebook_content = {
            "message": "This is a test post from the pAIssive Income social media integration module!",
            "link": "https://github.com/anchapin/pAIssive_income",
        }

        facebook_result = social_media.post_content(
            platform_id=facebook_connection["id"], content=facebook_content
        )

        logger.info(f"Posted to Facebook: {facebook_result['id']}")
        logger.info(f"Post URL: {facebook_result.get('platform_data', {}).get('url')}")

        # Example: Schedule a post for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)

        scheduled_content = {
            "message": "This is a scheduled post from the pAIssive Income social media integration module!",
            "link": "https://github.com/anchapin/pAIssive_income",
        }

        scheduled_result = social_media.schedule_post(
            platform_id=facebook_connection["id"],
            content=scheduled_content,
            schedule_time=tomorrow,
        )

        logger.info(
            f"Scheduled post for {tomorrow.isoformat()}: {scheduled_result['id']}"
        )

    except Exception as e:
        logger.error(f"Error in Facebook example: {e}")

    # Example: Connect to Instagram
    try:
        instagram_credentials = {
            "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN",
            "instagram_account_id": "YOUR_INSTAGRAM_ACCOUNT_ID",
            "facebook_page_id": "YOUR_FACEBOOK_PAGE_ID",  # Required for some operations
            "account_name": "Your Instagram Handle",
            "account_id": "YourInstagramID",
        }

        instagram_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.INSTAGRAM, credentials=instagram_credentials
        )

        logger.info(f"Connected to Instagram: {instagram_connection['id']}")

        # Example: Post an image to Instagram
        instagram_content = {
            "caption": "This is a test post from the pAIssive Income social media integration module! #AITools #PassiveIncome",
            "image": {
                "url": "https://example.com/image.jpg"  # Replace with a real image URL
            },
        }

        instagram_result = social_media.post_content(
            platform_id=instagram_connection["id"], content=instagram_content
        )

        logger.info(f"Posted to Instagram: {instagram_result['id']}")
        logger.info(
            f"Post URL: {instagram_result.get('platform_data', {}).get('permalink')}"
        )

        # Example: Post a story to Instagram
        story_content = {
            "story": {
                "type": "image",
                "url": "https://example.com/story-image.jpg",  # Replace with a real image URL
            }
        }

        story_result = social_media.post_content(
            platform_id=instagram_connection["id"], content=story_content
        )

        logger.info(f"Posted story to Instagram: {story_result['id']}")

        # Example: Get audience insights
        insights = social_media.get_audience_insights(
            platform_id=instagram_connection["id"]
        )

        logger.info(f"Instagram audience insights: {json.dumps(insights, indent=2)}")

    except Exception as e:
        logger.error(f"Error in Instagram example: {e}")

    # Example: Connect to LinkedIn
    try:
        linkedin_credentials = {
            "access_token": "YOUR_LINKEDIN_ACCESS_TOKEN",
            "organization_id": "YOUR_LINKEDIN_ORGANIZATION_ID",  # For company pages
            "person_id": "YOUR_LINKEDIN_PERSON_ID",  # For personal profiles
            "account_name": "Your LinkedIn Page",
            "account_id": "YourLinkedInID",
        }

        linkedin_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.LINKEDIN, credentials=linkedin_credentials
        )

        logger.info(f"Connected to LinkedIn: {linkedin_connection['id']}")

        # Example: Post text to LinkedIn
        linkedin_text_content = {
            "text": "This is a test post from the pAIssive Income social media integration module! #AITools #PassiveIncome"
        }

        linkedin_text_result = social_media.post_content(
            platform_id=linkedin_connection["id"], content=linkedin_text_content
        )

        logger.info(f"Posted text to LinkedIn: {linkedin_text_result['id']}")

        # Example: Post an article to LinkedIn
        linkedin_article_content = {
            "text": "Check out this great resource for AI tools!",
            "article": {
                "title": "Generate Passive Income with AI Tools",
                "url": "https://github.com/anchapin/pAIssive_income",
                "description": "A comprehensive framework for creating passive income streams using AI tools.",
            },
        }

        linkedin_article_result = social_media.post_content(
            platform_id=linkedin_connection["id"], content=linkedin_article_content
        )

        logger.info(f"Posted article to LinkedIn: {linkedin_article_result['id']}")

        # Example: Schedule a post for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)

        linkedin_scheduled_content = {
            "text": "This is a scheduled post from the pAIssive Income social media integration module! #AITools #PassiveIncome"
        }

        linkedin_scheduled_result = social_media.schedule_post(
            platform_id=linkedin_connection["id"],
            content=linkedin_scheduled_content,
            schedule_time=tomorrow,
        )

        logger.info(
            f"Scheduled post for LinkedIn on {tomorrow.isoformat()}: {linkedin_scheduled_result['id']}"
        )

        # Example: Get audience insights
        insights = social_media.get_audience_insights(
            platform_id=linkedin_connection["id"]
        )

        logger.info(f"LinkedIn audience insights: {json.dumps(insights, indent=2)}")

    except Exception as e:
        logger.error(f"Error in LinkedIn example: {e}")

    # Example: Connect to YouTube
    try:
        youtube_credentials = {
            "access_token": "YOUR_YOUTUBE_ACCESS_TOKEN",
            "refresh_token": "YOUR_YOUTUBE_REFRESH_TOKEN",
            "client_id": "YOUR_YOUTUBE_CLIENT_ID",
            "client_secret": "YOUR_YOUTUBE_CLIENT_SECRET",
            "api_key": "YOUR_YOUTUBE_API_KEY",  # For read-only operations
            "channel_id": "YOUR_YOUTUBE_CHANNEL_ID",
            "account_name": "Your YouTube Channel",
            "account_id": "YourYouTubeID",
        }

        youtube_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.YOUTUBE, credentials=youtube_credentials
        )

        logger.info(f"Connected to YouTube: {youtube_connection['id']}")

        # Example: Upload a video to YouTube
        youtube_content = {
            "title": "Test Video from pAIssive Income",
            "description": "This is a test video uploaded from the pAIssive Income social media integration module!",
            "tags": ["AITools", "PassiveIncome", "Test"],
            "category_id": "22",  # People & Blogs
            "privacy_status": "private",  # Use private for testing
            "video": {
                "file_path": "path/to/test-video.mp4"  # Replace with a real video path
            },
        }

        youtube_result = social_media.post_content(
            platform_id=youtube_connection["id"],
            content=youtube_content,
            visibility="private",  # Use private for testing
        )

        logger.info(f"Uploaded video to YouTube: {youtube_result['id']}")
        logger.info(f"Video URL: {youtube_result.get('url')}")

        # Example: Schedule a video for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)

        youtube_scheduled_content = {
            "title": "Scheduled Test Video from pAIssive Income",
            "description": "This is a scheduled test video from the pAIssive Income social media integration module!",
            "tags": ["AITools", "PassiveIncome", "Test"],
            "category_id": "22",  # People & Blogs
            "privacy_status": "private",  # Use private for testing
            "video": {
                "file_path": "path/to/test-video.mp4"  # Replace with a real video path
            },
        }

        youtube_scheduled_result = social_media.schedule_post(
            platform_id=youtube_connection["id"],
            content=youtube_scheduled_content,
            schedule_time=tomorrow,
            visibility="private",  # Use private for testing
        )

        logger.info(
            f"Scheduled video for YouTube on {tomorrow.isoformat()}: {youtube_scheduled_result['id']}"
        )

        # Example: Get analytics for a video
        if "id" in youtube_result:
            analytics = social_media.get_analytics(
                platform_id=youtube_connection["id"], post_id=youtube_result["id"]
            )

            logger.info(f"YouTube video analytics: {json.dumps(analytics, indent=2)}")

        # Example: Get audience insights
        insights = social_media.get_audience_insights(
            platform_id=youtube_connection["id"]
        )

        logger.info(f"YouTube audience insights: {json.dumps(insights, indent=2)}")

    except Exception as e:
        logger.error(f"Error in YouTube example: {e}")

    # Example: Connect to Pinterest
    try:
        pinterest_credentials = {
            "access_token": "YOUR_PINTEREST_ACCESS_TOKEN",
            "refresh_token": "YOUR_PINTEREST_REFRESH_TOKEN",
            "client_id": "YOUR_PINTEREST_CLIENT_ID",
            "client_secret": "YOUR_PINTEREST_CLIENT_SECRET",
            "user_id": "YOUR_PINTEREST_USERNAME",
            "account_name": "Your Pinterest Account",
            "account_id": "YourPinterestID",
        }

        pinterest_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.PINTEREST, credentials=pinterest_credentials
        )

        logger.info(f"Connected to Pinterest: {pinterest_connection['id']}")

        # Example: Create a pin on Pinterest
        pinterest_content = {
            "pin": {
                "title": "Test Pin from pAIssive Income",
                "description": "This is a test pin created from the pAIssive Income social media integration module! #AITools #PassiveIncome",
                "board_name": "AI Tools",  # Will create the board if it doesn't exist
                "media": {
                    "source_type": "image_url",
                    "url": "https://example.com/image.jpg",  # Replace with a real image URL
                },
                "link": "https://github.com/anchapin/pAIssive_income",
            }
        }

        pinterest_result = social_media.post_content(
            platform_id=pinterest_connection["id"], content=pinterest_content
        )

        logger.info(f"Created pin on Pinterest: {pinterest_result['id']}")
        logger.info(f"Pin URL: {pinterest_result.get('url')}")

        # Example: Get analytics for a pin
        if "id" in pinterest_result:
            analytics = social_media.get_analytics(
                platform_id=pinterest_connection["id"], post_id=pinterest_result["id"]
            )

            logger.info(f"Pinterest pin analytics: {json.dumps(analytics, indent=2)}")

        # Example: Get audience insights
        insights = social_media.get_audience_insights(
            platform_id=pinterest_connection["id"]
        )

        logger.info(f"Pinterest audience insights: {json.dumps(insights, indent=2)}")

    except Exception as e:
        logger.error(f"Error in Pinterest example: {e}")

    # Example: Connect to TikTok
    try:
        tiktok_credentials = {
            "access_token": "YOUR_TIKTOK_ACCESS_TOKEN",
            "refresh_token": "YOUR_TIKTOK_REFRESH_TOKEN",
            "client_key": "YOUR_TIKTOK_CLIENT_KEY",
            "client_secret": "YOUR_TIKTOK_CLIENT_SECRET",
            "open_id": "YOUR_TIKTOK_OPEN_ID",
            "account_name": "Your TikTok Account",
            "account_id": "YourTikTokID",
        }

        tiktok_connection = social_media.connect_platform(
            platform=SocialMediaPlatform.TIKTOK, credentials=tiktok_credentials
        )

        logger.info(f"Connected to TikTok: {tiktok_connection['id']}")

        # Example: Post a video to TikTok
        tiktok_content = {
            "video": {
                "file_path": "path/to/test-video.mp4"  # Replace with a real video path
            },
            "caption": "Testing the pAIssive Income social media integration module!",
            "hashtags": ["AITools", "PassiveIncome", "TikTokAPI", "Test"],
        }

        tiktok_result = social_media.post_content(
            platform_id=tiktok_connection["id"],
            content=tiktok_content,
            visibility="private",  # Use private for testing
        )

        logger.info(f"Posted video to TikTok: {tiktok_result['id']}")
        logger.info(f"Video URL: {tiktok_result.get('url')}")

        # Example: Get analytics for a video
        if "id" in tiktok_result:
            analytics = social_media.get_analytics(
                platform_id=tiktok_connection["id"], post_id=tiktok_result["id"]
            )

            logger.info(f"TikTok video analytics: {json.dumps(analytics, indent=2)}")

        # Example: Get audience insights
        insights = social_media.get_audience_insights(
            platform_id=tiktok_connection["id"]
        )

        logger.info(f"TikTok audience insights: {json.dumps(insights, indent=2)}")

    except Exception as e:
        logger.error(f"Error in TikTok example: {e}")

    # Example: Create a multi-platform campaign
    try:
        # Define platforms to include in the campaign
        platforms = []
        if "twitter_connection" in locals():
            platforms.append(twitter_connection["id"])
        if "facebook_connection" in locals():
            platforms.append(facebook_connection["id"])
        if "instagram_connection" in locals():
            platforms.append(instagram_connection["id"])
        if "linkedin_connection" in locals():
            platforms.append(linkedin_connection["id"])
        if "youtube_connection" in locals():
            platforms.append(youtube_connection["id"])
        if "pinterest_connection" in locals():
            platforms.append(pinterest_connection["id"])
        if "tiktok_connection" in locals():
            platforms.append(tiktok_connection["id"])

        if platforms:
            # Define campaign content
            campaign_name = "Example Campaign"
            content_items = [
                {
                    "text": "Check out our new project on GitHub! #AITools #PassiveIncome",
                    "link": "https://github.com/anchapin/pAIssive_income",
                },
                {
                    "text": "Learn how to generate passive income with AI tools! #AITools #PassiveIncome",
                    "link": "https://github.com/anchapin/pAIssive_income",
                },
            ]

            # Define schedule settings
            start_date = datetime.now() + timedelta(days=2)
            end_date = datetime.now() + timedelta(days=7)
            schedule_settings = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "frequency": "daily",
                "times": ["09:00", "15:00", "19:00"],
                "timezone": "UTC",
            }

            # Create the campaign
            campaign = social_media.schedule_campaign(
                platform_ids=platforms,
                campaign_name=campaign_name,
                content_items=content_items,
                schedule_settings=schedule_settings,
            )

            logger.info(f"Created campaign: {campaign['id']}")
            logger.info(
                f"Campaign schedule: {campaign['start_date']} to {campaign['end_date']}"
            )
            logger.info(
                f"Scheduled posts: {json.dumps(campaign['scheduled_posts'], indent=2)}"
            )

    except Exception as e:
        logger.error(f"Error in campaign example: {e}")


if __name__ == "__main__":
    main()