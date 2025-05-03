"""
Social media adapter package for pAIssive Income marketing module.

This package provides adapters for various social media platforms to enable
posting content, retrieving analytics, and managing social media campaigns.
"""

from .base_adapter import BaseSocialMediaAdapter
from .facebook_adapter import FacebookAdapter
from .instagram_adapter import InstagramAdapter
from .linkedin_adapter import LinkedInAdapter
from .pinterest_adapter import PinterestAdapter
from .tiktok_adapter import TikTokAdapter
from .twitter_adapter import TwitterAdapter
from .youtube_adapter import YouTubeAdapter

__all__ = [
    'BaseSocialMediaAdapter',
    'TwitterAdapter',
    'FacebookAdapter',
    'InstagramAdapter',
    'LinkedInAdapter',
    'YouTubeAdapter',
    'PinterestAdapter',
    'TikTokAdapter'
]