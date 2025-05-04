"""
"""
Rate limit manager.
Rate limit manager.


This module provides a manager for rate limiting.
This module provides a manager for rate limiting.
"""
"""




import logging
import logging
from typing import Any, Dict, Optional, Tuple
from typing import Any, Dict, Optional, Tuple


from ..config import APIConfig, RateLimitScope
from ..config import APIConfig, RateLimitScope
from .algorithms import RateLimiter, create_rate_limiter
from .algorithms import RateLimiter, create_rate_limiter
from .storage import create_storage
from .storage import create_storage


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class RateLimitManager:
    class RateLimitManager:
    """
    """
    Manager for rate limiting.
    Manager for rate limiting.
    """
    """


    def __init__(
    def __init__(
    self, config: APIConfig, storage_type: str = "memory", **storage_kwargs
    self, config: APIConfig, storage_type: str = "memory", **storage_kwargs
    ):
    ):
    """
    """
    Initialize the rate limit manager.
    Initialize the rate limit manager.


    Args:
    Args:
    config: API configuration
    config: API configuration
    storage_type: Storage type ("memory" or "redis")
    storage_type: Storage type ("memory" or "redis")
    **storage_kwargs: Additional arguments for the storage backend
    **storage_kwargs: Additional arguments for the storage backend
    """
    """
    self.config = config
    self.config = config
    self.storage = create_storage(storage_type, **storage_kwargs)
    self.storage = create_storage(storage_type, **storage_kwargs)


    # Create rate limiter
    # Create rate limiter
    self.rate_limiter = create_rate_limiter(
    self.rate_limiter = create_rate_limiter(
    strategy=self.config.rate_limit_strategy.value,
    strategy=self.config.rate_limit_strategy.value,
    limit=self.config.rate_limit_requests,
    limit=self.config.rate_limit_requests,
    period=self.config.rate_limit_period,
    period=self.config.rate_limit_period,
    burst=self.config.rate_limit_burst,
    burst=self.config.rate_limit_burst,
    )
    )


    # Create endpoint-specific rate limiters
    # Create endpoint-specific rate limiters
    self.endpoint_rate_limiters: Dict[str, RateLimiter] = {}
    self.endpoint_rate_limiters: Dict[str, RateLimiter] = {}
    for endpoint, limit in self.config.endpoint_rate_limits.items():
    for endpoint, limit in self.config.endpoint_rate_limits.items():
    self.endpoint_rate_limiters[endpoint] = create_rate_limiter(
    self.endpoint_rate_limiters[endpoint] = create_rate_limiter(
    strategy=self.config.rate_limit_strategy.value,
    strategy=self.config.rate_limit_strategy.value,
    limit=limit,
    limit=limit,
    period=self.config.rate_limit_period,
    period=self.config.rate_limit_period,
    burst=self.config.rate_limit_burst,
    burst=self.config.rate_limit_burst,
    )
    )


    def get_rate_limit_key(
    def get_rate_limit_key(
    self, identifier: str, endpoint: Optional[str] = None
    self, identifier: str, endpoint: Optional[str] = None
    ) -> str:
    ) -> str:
    """
    """
    Get the rate limit key for an identifier.
    Get the rate limit key for an identifier.


    Args:
    Args:
    identifier: Client identifier (IP, API key, user ID)
    identifier: Client identifier (IP, API key, user ID)
    endpoint: Optional endpoint path
    endpoint: Optional endpoint path


    Returns:
    Returns:
    Rate limit key
    Rate limit key
    """
    """
    if self.config.rate_limit_scope == RateLimitScope.GLOBAL:
    if self.config.rate_limit_scope == RateLimitScope.GLOBAL:
    return "global"
    return "global"
    elif self.config.rate_limit_scope == RateLimitScope.ENDPOINT and endpoint:
    elif self.config.rate_limit_scope == RateLimitScope.ENDPOINT and endpoint:
    return f"endpoint:{endpoint}"
    return f"endpoint:{endpoint}"
    elif self.config.rate_limit_scope == RateLimitScope.IP:
    elif self.config.rate_limit_scope == RateLimitScope.IP:
    return f"ip:{identifier}"
    return f"ip:{identifier}"
    elif self.config.rate_limit_scope == RateLimitScope.API_KEY:
    elif self.config.rate_limit_scope == RateLimitScope.API_KEY:
    return f"api_key:{identifier}"
    return f"api_key:{identifier}"
    elif self.config.rate_limit_scope == RateLimitScope.USER:
    elif self.config.rate_limit_scope == RateLimitScope.USER:
    return f"user:{identifier}"
    return f"user:{identifier}"
    else:
    else:
    # Default to IP-based rate limiting
    # Default to IP-based rate limiting
    return f"ip:{identifier}"
    return f"ip:{identifier}"


    def is_exempt(self, identifier: str) -> bool:
    def is_exempt(self, identifier: str) -> bool:
    """
    """
    Check if an identifier is exempt from rate limiting.
    Check if an identifier is exempt from rate limiting.


    Args:
    Args:
    identifier: Client identifier (IP, API key)
    identifier: Client identifier (IP, API key)


    Returns:
    Returns:
    True if exempt, False otherwise
    True if exempt, False otherwise
    """
    """
    # Check if rate limiting is disabled
    # Check if rate limiting is disabled
    if not self.config.enable_rate_limit:
    if not self.config.enable_rate_limit:
    return True
    return True


    # Check if IP is exempt
    # Check if IP is exempt
    if identifier in self.config.rate_limit_exempt_ips:
    if identifier in self.config.rate_limit_exempt_ips:
    return True
    return True


    # Check if API key is exempt
    # Check if API key is exempt
    if identifier in self.config.rate_limit_exempt_api_keys:
    if identifier in self.config.rate_limit_exempt_api_keys:
    return True
    return True


    return False
    return False


    def get_rate_limit_tier(self, api_key: Optional[str]) -> int:
    def get_rate_limit_tier(self, api_key: Optional[str]) -> int:
    """
    """
    Get the rate limit tier for an API key.
    Get the rate limit tier for an API key.


    Args:
    Args:
    api_key: API key or None
    api_key: API key or None


    Returns:
    Returns:
    Rate limit for the tier
    Rate limit for the tier
    """
    """
    if api_key is None:
    if api_key is None:
    return self.config.rate_limit_tiers.get(
    return self.config.rate_limit_tiers.get(
    "default", self.config.rate_limit_requests
    "default", self.config.rate_limit_requests
    )
    )


    # In a real implementation, you would look up the tier for the API key
    # In a real implementation, you would look up the tier for the API key
    # For now, we'll just return the default tier
    # For now, we'll just return the default tier
    return self.config.rate_limit_tiers.get(
    return self.config.rate_limit_tiers.get(
    "default", self.config.rate_limit_requests
    "default", self.config.rate_limit_requests
    )
    )


    def get_endpoint_cost(self, endpoint: str) -> float:
    def get_endpoint_cost(self, endpoint: str) -> float:
    """
    """
    Get the cost factor for an endpoint.
    Get the cost factor for an endpoint.


    Args:
    Args:
    endpoint: Endpoint path
    endpoint: Endpoint path


    Returns:
    Returns:
    Cost factor for the endpoint
    Cost factor for the endpoint
    """
    """
    # In a real implementation, you would have a mapping of endpoints to cost factors
    # In a real implementation, you would have a mapping of endpoints to cost factors
    # For now, we'll just return the default cost factor
    # For now, we'll just return the default cost factor
    return self.config.rate_limit_cost_factor
    return self.config.rate_limit_cost_factor


    def check_rate_limit(
    def check_rate_limit(
    self,
    self,
    identifier: str,
    identifier: str,
    endpoint: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    api_key: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
    ) -> Tuple[bool, Dict[str, Any]]:
    """
    """
    Check if a request should be rate limited.
    Check if a request should be rate limited.


    Args:
    Args:
    identifier: Client identifier (IP, API key, user ID)
    identifier: Client identifier (IP, API key, user ID)
    endpoint: Optional endpoint path
    endpoint: Optional endpoint path
    api_key: Optional API key
    api_key: Optional API key


    Returns:
    Returns:
    Tuple of (allowed, limit_info)
    Tuple of (allowed, limit_info)
    - allowed: True if the request is allowed, False if it should be rate limited
    - allowed: True if the request is allowed, False if it should be rate limited
    - limit_info: Dictionary with rate limit information
    - limit_info: Dictionary with rate limit information
    """
    """
    # Check if exempt
    # Check if exempt
    if self.is_exempt(identifier) or self.is_exempt(api_key or ""):
    if self.is_exempt(identifier) or self.is_exempt(api_key or ""):
    return True, {
    return True, {
    "limit": 0,  # 0 means no limit
    "limit": 0,  # 0 means no limit
    "remaining": 0,
    "remaining": 0,
    "reset": 0,
    "reset": 0,
    "retry_after": 0,
    "retry_after": 0,
    }
    }


    # Get rate limit key
    # Get rate limit key
    key = self.get_rate_limit_key(identifier, endpoint)
    key = self.get_rate_limit_key(identifier, endpoint)


    # Get endpoint cost
    # Get endpoint cost
    cost = self.get_endpoint_cost(endpoint or "")
    cost = self.get_endpoint_cost(endpoint or "")


    # Check endpoint-specific rate limit if applicable
    # Check endpoint-specific rate limit if applicable
    if endpoint and endpoint in self.endpoint_rate_limiters:
    if endpoint and endpoint in self.endpoint_rate_limiters:
    endpoint_key = f"{key}:{endpoint}"
    endpoint_key = f"{key}:{endpoint}"
    allowed, limit_info = self.endpoint_rate_limiters[
    allowed, limit_info = self.endpoint_rate_limiters[
    endpoint
    endpoint
    ].check_rate_limit(endpoint_key, cost)
    ].check_rate_limit(endpoint_key, cost)


    if not allowed:
    if not allowed:
    return allowed, limit_info
    return allowed, limit_info


    # Check global rate limit
    # Check global rate limit
    return self.rate_limiter.check_rate_limit(key, cost)
    return self.rate_limiter.check_rate_limit(key, cost)


    def get_rate_limit_headers(self, limit_info: Dict[str, Any]) -> Dict[str, str]:
    def get_rate_limit_headers(self, limit_info: Dict[str, Any]) -> Dict[str, str]:
    """
    """
    Get rate limit headers for a response.
    Get rate limit headers for a response.


    Args:
    Args:
    limit_info: Rate limit information
    limit_info: Rate limit information


    Returns:
    Returns:
    Dictionary of rate limit headers
    Dictionary of rate limit headers
    """
    """
    if not self.config.enable_rate_limit_headers:
    if not self.config.enable_rate_limit_headers:
    return {}
    return {}


    headers = {}
    headers = {}


    # Add rate limit headers
    # Add rate limit headers
    if "limit" in limit_info:
    if "limit" in limit_info:
    headers[self.config.rate_limit_limit_header] = str(int(limit_info["limit"]))
    headers[self.config.rate_limit_limit_header] = str(int(limit_info["limit"]))


    if "remaining" in limit_info:
    if "remaining" in limit_info:
    headers[self.config.rate_limit_remaining_header] = str(
    headers[self.config.rate_limit_remaining_header] = str(
    int(limit_info["remaining"])
    int(limit_info["remaining"])
    )
    )


    if "reset" in limit_info:
    if "reset" in limit_info:
    headers[self.config.rate_limit_reset_header] = str(int(limit_info["reset"]))
    headers[self.config.rate_limit_reset_header] = str(int(limit_info["reset"]))


    # Add retry-after header if rate limited
    # Add retry-after header if rate limited
    if "retry_after" in limit_info and limit_info["retry_after"] > 0:
    if "retry_after" in limit_info and limit_info["retry_after"] > 0:
    headers[self.config.rate_limit_retry_after_header] = str(
    headers[self.config.rate_limit_retry_after_header] = str(
    int(limit_info["retry_after"])
    int(limit_info["retry_after"])
    )
    )


    return headers
    return headers