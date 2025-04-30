"""
Configuration for the API server.

This module provides configuration classes for the API server.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
from enum import Enum, auto

class RateLimitStrategy(str, Enum):
    """
    Rate limiting strategy enumeration.

    This enum defines the available rate limiting strategies.
    """
    FIXED = "fixed"  # Fixed number of requests per time period
    TOKEN_BUCKET = "token_bucket"  # Token bucket algorithm
    LEAKY_BUCKET = "leaky_bucket"  # Leaky bucket algorithm
    SLIDING_WINDOW = "sliding_window"  # Sliding window algorithm

class RateLimitScope(str, Enum):
    """
    Rate limiting scope enumeration.

    This enum defines the available scopes for rate limiting.
    """
    GLOBAL = "global"  # Global rate limit for all clients
    IP = "ip"  # Rate limit per IP address
    API_KEY = "api_key"  # Rate limit per API key
    USER = "user"  # Rate limit per authenticated user
    ENDPOINT = "endpoint"  # Rate limit per endpoint

class WebhookEventType(str, Enum):
    """
    Webhook event types enumeration.

    This enum defines the available webhook event types.
    """
    NICHE_ANALYSIS_CREATED = "niche_analysis.created"
    NICHE_ANALYSIS_UPDATED = "niche_analysis.updated"
    NICHE_ANALYSIS_DELETED = "niche_analysis.deleted"
    OPPORTUNITY_SCORED = "opportunity.scored"
    MONETIZATION_PLAN_CREATED = "monetization.plan.created"
    MONETIZATION_PLAN_UPDATED = "monetization.plan.updated"
    MARKETING_CAMPAIGN_CREATED = "marketing.campaign.created"
    MARKETING_CAMPAIGN_UPDATED = "marketing.campaign.updated"
    MARKETING_CAMPAIGN_COMPLETED = "marketing.campaign.completed"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_SHARED = "project.shared"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    MODEL_INFERENCE_COMPLETED = "model.inference.completed"
    CUSTOM = "custom"  # For custom event types

class APIVersion(str, Enum):
    """
    API version enumeration.

    This enum defines the available API versions. When adding a new version,
    add it to the end of the list to maintain the order for the latest_version property.
    """
    V1 = "v1"
    V2 = "v2"

    @classmethod
    def latest_version(cls) -> 'APIVersion':
        """
        Get the latest API version.

        Returns:
            The latest API version
        """
        return list(cls)[-1]

    @classmethod
    def is_valid_version(cls, version: str) -> bool:
        """
        Check if a version string is valid.

        Args:
            version: Version string to check

        Returns:
            True if the version is valid, False otherwise
        """
        return version in [v.value for v in cls]

@dataclass
class APIConfig:
    """
    Configuration for the API server.
    """
    # Basic configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    title: str = "pAIssive Income API"  
    description: str = "RESTful API for pAIssive Income services"

    # API configuration
    version: APIVersion = APIVersion.latest_version()  # Default to latest version
    active_versions: List[APIVersion] = field(default_factory=lambda: list(APIVersion))  # All versions active by default
    prefix: str = "/api"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"

    # GraphQL configuration
    enable_graphql: bool = True
    graphql_path: str = "/graphql"
    graphiql: bool = True  # Interactive GraphQL interface
    graphql_batch_enabled: bool = True
    graphql_introspection_enabled: bool = True
    graphql_playground: bool = True  # Alternative to GraphiQL

    # Versioning configuration
    enable_version_header: bool = True  # Add API version to response headers
    version_header_name: str = "X-API-Version"
    enable_version_deprecation_header: bool = True  # Add deprecation notice to response headers
    deprecation_header_name: str = "X-API-Deprecated"
    sunset_header_name: str = "X-API-Sunset-Date"

    # Middleware configuration
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])  # Allow all origins by default
    enable_gzip: bool = True
    enable_https: bool = False
    enable_auth: bool = False
    enable_rate_limit: bool = False
    enable_analytics: bool = True

    # Webhook configuration
    enable_webhooks: bool = True
    webhook_secret_header: str = "X-Webhook-Signature"
    webhook_max_retries: int = 3
    webhook_retry_delay: int = 60  # Seconds between webhook delivery attempts
    webhook_timeout: int = 5  # Timeout for webhook delivery in seconds
    webhook_batch_size: int = 100  # Maximum number of events to process in a batch
    webhook_workers: int = 5  # Number of worker threads for webhook delivery
    webhook_events_retention_days: int = 30  # Number of days to retain webhook events
    webhook_allowed_event_types: List[WebhookEventType] = field(
        default_factory=lambda: list(WebhookEventType)
    )

    # Analytics configuration
    analytics_db_path: Optional[str] = None  # Path to analytics database (None for default)
    analytics_retention_days: int = 365  # Number of days to retain analytics data
    analytics_dashboard_enabled: bool = True  # Enable analytics dashboard
    analytics_dashboard_path: str = "/analytics"  # Path to analytics dashboard
    analytics_export_enabled: bool = True  # Enable analytics export

    # HTTPS configuration
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None

    # Authentication configuration
    api_keys: List[str] = field(default_factory=list)
    jwt_secret: Optional[str] = "test_jwt_secret"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24  # 24 hours

    # Rate limiting configuration
    rate_limit_strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    rate_limit_scope: RateLimitScope = RateLimitScope.IP
    rate_limit_requests: int = 100  # Default requests per period
    rate_limit_period: int = 60  # Default period in seconds (1 minute)
    rate_limit_burst: int = 50  # Default burst size for token bucket
    rate_limit_cost_factor: float = 1.0  # Default cost factor for expensive endpoints

    # Rate limit tiers (requests per minute)
    rate_limit_tiers: Dict[str, int] = field(default_factory=lambda: {
        "default": 100,
        "basic": 300,
        "premium": 1000,
        "unlimited": 0  # 0 means no limit
    })

    # Endpoint-specific rate limits
    endpoint_rate_limits: Dict[str, int] = field(default_factory=dict)

    # Rate limit exemptions
    rate_limit_exempt_ips: Set[str] = field(default_factory=set)
    rate_limit_exempt_api_keys: Set[str] = field(default_factory=set)

    # Rate limit headers
    enable_rate_limit_headers: bool = True
    rate_limit_remaining_header: str = "X-RateLimit-Remaining"
    rate_limit_limit_header: str = "X-RateLimit-Limit"
    rate_limit_reset_header: str = "X-RateLimit-Reset"
    rate_limit_retry_after_header: str = "Retry-After"

    # Module configuration
    enable_niche_analysis: bool = True
    enable_monetization: bool = True
    enable_marketing: bool = True
    enable_ai_models: bool = True
    enable_agent_team: bool = True
    enable_user: bool = True
    enable_dashboard: bool = True
    enable_developer: bool = True

    # Pagination, filtering, and sorting configuration
    max_page_size: int = 100  # Maximum number of items per page
    default_page_size: int = 10  # Default number of items per page
    enable_advanced_filtering: bool = True  # Enable advanced filtering
    enable_advanced_sorting: bool = True  # Enable advanced sorting

    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_api_config() -> APIConfig:
    """
    Retrieve the API configuration.

    Returns:
        An instance of APIConfig with default or customized settings.
    """
    return APIConfig()
