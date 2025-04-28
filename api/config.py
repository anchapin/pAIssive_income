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

    # API configuration
    version: APIVersion = APIVersion.latest_version()  # Default to latest version
    active_versions: List[APIVersion] = field(default_factory=lambda: list(APIVersion))  # All versions active by default
    prefix: str = "/api"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"

    # Versioning configuration
    enable_version_header: bool = True  # Add API version to response headers
    version_header_name: str = "X-API-Version"
    enable_version_deprecation_header: bool = True  # Add deprecation notice to response headers
    deprecation_header_name: str = "X-API-Deprecated"
    sunset_header_name: str = "X-API-Sunset-Date"

    # Middleware configuration
    enable_cors: bool = True
    enable_gzip: bool = True
    enable_https: bool = False
    enable_auth: bool = False
    enable_rate_limit: bool = False

    # HTTPS configuration
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None

    # Authentication configuration
    api_keys: List[str] = field(default_factory=list)
    jwt_secret: Optional[str] = None
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

    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
