"""
Configuration for the API server.
"""

import os
import enum
from typing import List, Optional, Dict, Any

class APIVersion(enum.Enum):
    """API version enum."""
    V1 = "1"

class APIConfig:
    """Configuration for the API server."""
    
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: APIVersion = APIVersion.V1,
        active_versions: List[APIVersion] = None,
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        openapi_url: str = "/openapi.json",
        cors_origins: List[str] = None,
        enable_auth: bool = True,
        enable_niche_analysis: bool = True,
        enable_monetization: bool = True,
        enable_marketing: bool = True,
        enable_ai_models: bool = True,
        enable_agent_team: bool = True,
        enable_dashboard: bool = True,
        enable_analytics: bool = True,
        enable_developer: bool = True,
        webhook_allowed_ips: List[str] = None,
        webhook_rate_limit: int = 100,
        webhook_rate_limit_window: int = 60,
    ):
        """
        Initialize the API configuration.
        
        Args:
            title: API title
            description: API description
            version: API version
            active_versions: List of active API versions
            docs_url: URL for the API documentation
            redoc_url: URL for the ReDoc documentation
            openapi_url: URL for the OpenAPI schema
            cors_origins: List of allowed CORS origins
            enable_auth: Whether to enable authentication
            enable_niche_analysis: Whether to enable niche analysis
            enable_monetization: Whether to enable monetization
            enable_marketing: Whether to enable marketing
            enable_ai_models: Whether to enable AI models
            enable_agent_team: Whether to enable agent team
            enable_dashboard: Whether to enable dashboard
            enable_analytics: Whether to enable analytics
            enable_developer: Whether to enable developer
            webhook_allowed_ips: List of allowed IPs for webhooks
            webhook_rate_limit: Rate limit for webhooks
            webhook_rate_limit_window: Rate limit window for webhooks in seconds
        """
        self.title = title
        self.description = description
        self.version = version
        self.active_versions = active_versions or [APIVersion.V1]
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        self.cors_origins = cors_origins or ["*"]
        self.enable_auth = enable_auth
        self.enable_niche_analysis = enable_niche_analysis
        self.enable_monetization = enable_monetization
        self.enable_marketing = enable_marketing
        self.enable_ai_models = enable_ai_models
        self.enable_agent_team = enable_agent_team
        self.enable_dashboard = enable_dashboard
        self.enable_analytics = enable_analytics
        self.enable_developer = enable_developer
        self.webhook_allowed_ips = webhook_allowed_ips or ["192.0.2.1", "192.0.2.2", "192.0.2.3", "192.0.2.4"]
        self.webhook_rate_limit = webhook_rate_limit
        self.webhook_rate_limit_window = webhook_rate_limit_window

# Default configuration
default_config = APIConfig()
