"""
"""
Rate limiting router for API tests.
Rate limiting router for API tests.


This module provides a router for testing rate limiting functionality.
This module provides a router for testing rate limiting functionality.
"""
"""




import asyncio
import asyncio
import random
import random
import threading
import threading
import time
import time
from typing import Any, Dict
from typing import Any, Dict


from fastapi import APIRouter, Request, Response
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, ConfigDict




class RateLimitConfig
class RateLimitConfig


(BaseModel):
    (BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_config = ConfigDict(protected_namespaces=())
    """Rate limit configuration."""
    tier: str
    limits: Dict[str, int]


    class ThrottleConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Throttling configuration."""
    max_concurrent_requests: int
    timeout_seconds: int


    class QuotaConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Quota configuration."""
    customer_id: str
    daily_limit: int
    monthly_limit: int
    overage_allowed: bool
    overage_rate: float


    def create_rate_limiting_router() -> APIRouter:
    """
    """
    Create a router for rate limiting tests.
    Create a router for rate limiting tests.


    Returns:
    Returns:
    FastAPI router
    FastAPI router
    """
    """
    router = APIRouter()
    router = APIRouter()


    # Store rate limit state
    # Store rate limit state
    rate_limits = {
    rate_limits = {
    "test-rate-limit": {"limit": 3, "window": 60},
    "test-rate-limit": {"limit": 3, "window": 60},
    "test-rate-limit-reset": {"limit": 3, "window": 60},
    "test-rate-limit-reset": {"limit": 3, "window": 60},
    "test-custom-rate-limit": {"limit": 10, "window": 1},  # 10 per second
    "test-custom-rate-limit": {"limit": 10, "window": 1},  # 10 per second
    "test-ip-rate-limit": {"limit": 3, "window": 60},
    "test-ip-rate-limit": {"limit": 3, "window": 60},
    "test-concurrent-throttling": {"limit": 3, "window": 60},
    "test-concurrent-throttling": {"limit": 3, "window": 60},
    "test-degradation": {"limit": 20, "window": 60},
    "test-degradation": {"limit": 20, "window": 60},
    "test-quota-limit": {"limit": 10, "window": 60},
    "test-quota-limit": {"limit": 10, "window": 60},
    }
    }


    # Store request history
    # Store request history
    request_history = {}
    request_history = {}


    # Store throttling configuration
    # Store throttling configuration
    throttle_config = {"max_concurrent_requests": 3, "timeout_seconds": 5}
    throttle_config = {"max_concurrent_requests": 3, "timeout_seconds": 5}


    # Store active requests for throttling
    # Store active requests for throttling
    active_requests = {}
    active_requests = {}
    active_requests_lock = threading.Lock()
    active_requests_lock = threading.Lock()


    # Store quota configuration
    # Store quota configuration
    quota_config = {}
    quota_config = {}
    quota_usage = {}
    quota_usage = {}


    @router.get("/{endpoint}")
    @router.get("/{endpoint}")
    async def rate_limited_endpoint(
    async def rate_limited_endpoint(
    endpoint: str, request: Request, response: Response
    endpoint: str, request: Request, response: Response
    ):
    ):
    """
    """
    Generic rate-limited endpoint.
    Generic rate-limited endpoint.


    Args:
    Args:
    endpoint: Endpoint name
    endpoint: Endpoint name
    request: FastAPI request
    request: FastAPI request
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    # Get client identifier
    # Get client identifier
    client_id = get_client_id(request)
    client_id = get_client_id(request)


    # Handle IP-based rate limiting
    # Handle IP-based rate limiting
    if endpoint == "test-ip-rate-limit":
    if endpoint == "test-ip-rate-limit":
    client_id = request.headers.get("X-Forwarded-For", client_id)
    client_id = request.headers.get("X-Forwarded-For", client_id)


    # Handle throttling
    # Handle throttling
    if endpoint == "test-concurrent-throttling":
    if endpoint == "test-concurrent-throttling":
    return await handle_throttling(client_id, response)
    return await handle_throttling(client_id, response)


    # Handle degradation testing
    # Handle degradation testing
    if endpoint == "test-degradation":
    if endpoint == "test-degradation":
    return await handle_degradation(request, response)
    return await handle_degradation(request, response)


    # Handle quota-based limiting
    # Handle quota-based limiting
    if endpoint == "test-quota-limit":
    if endpoint == "test-quota-limit":
    return await handle_quota(client_id, response)
    return await handle_quota(client_id, response)


    # Get rate limit configuration
    # Get rate limit configuration
    limit_config = rate_limits.get(endpoint, {"limit": 3, "window": 60})
    limit_config = rate_limits.get(endpoint, {"limit": 3, "window": 60})


    # Check rate limit
    # Check rate limit
    allowed, info = check_rate_limit(client_id, endpoint, limit_config)
    allowed, info = check_rate_limit(client_id, endpoint, limit_config)


    # Add rate limit headers
    # Add rate limit headers
    add_rate_limit_headers(response, info)
    add_rate_limit_headers(response, info)


    # Return 429 if rate limited
    # Return 429 if rate limited
    if not allowed:
    if not allowed:
    response.status_code = 429
    response.status_code = 429
    return {
    return {
    "error": {
    "error": {
    "message": "Rate limit exceeded",
    "message": "Rate limit exceeded",
    "retry_after": info["retry_after"],
    "retry_after": info["retry_after"],
    }
    }
    }
    }


    # Return success response
    # Return success response
    return {"status": "ok", "endpoint": endpoint, "client_id": client_id}
    return {"status": "ok", "endpoint": endpoint, "client_id": client_id}


    @router.post("/config")
    @router.post("/config")
    async def configure_rate_limits(config: RateLimitConfig, response: Response):
    async def configure_rate_limits(config: RateLimitConfig, response: Response):
    """
    """
    Configure custom rate limits.
    Configure custom rate limits.


    Args:
    Args:
    config: Rate limit configuration
    config: Rate limit configuration
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Configuration status
    Configuration status
    """
    """
    # Update rate limit configuration for custom rate limit endpoint
    # Update rate limit configuration for custom rate limit endpoint
    if "requests_per_second" in config.limits:
    if "requests_per_second" in config.limits:
    rate_limits["test-custom-rate-limit"] = {
    rate_limits["test-custom-rate-limit"] = {
    "limit": config.limits["requests_per_second"],
    "limit": config.limits["requests_per_second"],
    "window": 1,  # 1 second window
    "window": 1,  # 1 second window
    }
    }


    return {
    return {
    "status": "ok",
    "status": "ok",
    "message": "Rate limit configuration updated",
    "message": "Rate limit configuration updated",
    "tier": config.tier,
    "tier": config.tier,
    "limits": config.limits,
    "limits": config.limits,
    }
    }


    @router.post("/throttle-config")
    @router.post("/throttle-config")
    async def configure_throttling(config: ThrottleConfig, response: Response):
    async def configure_throttling(config: ThrottleConfig, response: Response):
    """
    """
    Configure request throttling.
    Configure request throttling.


    Args:
    Args:
    config: Throttling configuration
    config: Throttling configuration
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Configuration status
    Configuration status
    """
    """
    # Update throttling configuration
    # Update throttling configuration
    throttle_config["max_concurrent_requests"] = config.max_concurrent_requests
    throttle_config["max_concurrent_requests"] = config.max_concurrent_requests
    throttle_config["timeout_seconds"] = config.timeout_seconds
    throttle_config["timeout_seconds"] = config.timeout_seconds


    return {
    return {
    "status": "ok",
    "status": "ok",
    "message": "Throttling configuration updated",
    "message": "Throttling configuration updated",
    "config": throttle_config,
    "config": throttle_config,
    }
    }


    @router.post("/quota")
    @router.post("/quota")
    async def configure_quota(config: QuotaConfig, response: Response):
    async def configure_quota(config: QuotaConfig, response: Response):
    """
    """
    Configure customer-specific quota.
    Configure customer-specific quota.


    Args:
    Args:
    config: Quota configuration
    config: Quota configuration
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Configuration status
    Configuration status
    """
    """
    # Update quota configuration
    # Update quota configuration
    quota_config[config.customer_id] = {
    quota_config[config.customer_id] = {
    "daily_limit": config.daily_limit,
    "daily_limit": config.daily_limit,
    "monthly_limit": config.monthly_limit,
    "monthly_limit": config.monthly_limit,
    "overage_allowed": config.overage_allowed,
    "overage_allowed": config.overage_allowed,
    "overage_rate": config.overage_rate,
    "overage_rate": config.overage_rate,
    }
    }


    # Initialize quota usage
    # Initialize quota usage
    if config.customer_id not in quota_usage:
    if config.customer_id not in quota_usage:
    quota_usage[config.customer_id] = {"daily": 0, "monthly": 0}
    quota_usage[config.customer_id] = {"daily": 0, "monthly": 0}


    return {
    return {
    "status": "ok",
    "status": "ok",
    "message": "Quota configuration updated",
    "message": "Quota configuration updated",
    "customer_id": config.customer_id,
    "customer_id": config.customer_id,
    "config": quota_config[config.customer_id],
    "config": quota_config[config.customer_id],
    }
    }


    async def handle_throttling(client_id: str, response: Response) -> Dict[str, Any]:
    async def handle_throttling(client_id: str, response: Response) -> Dict[str, Any]:
    """
    """
    Handle concurrent request throttling.
    Handle concurrent request throttling.


    Args:
    Args:
    client_id: Client identifier
    client_id: Client identifier
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    # Check if we're already at max concurrent requests
    # Check if we're already at max concurrent requests
    with active_requests_lock:
    with active_requests_lock:
    active_count = active_requests.get(client_id, 0)
    active_count = active_requests.get(client_id, 0)


    if active_count >= throttle_config["max_concurrent_requests"]:
    if active_count >= throttle_config["max_concurrent_requests"]:
    response.status_code = 429
    response.status_code = 429
    response.headers["Retry-After"] = str(
    response.headers["Retry-After"] = str(
    throttle_config["timeout_seconds"]
    throttle_config["timeout_seconds"]
    )
    )
    return {
    return {
    "error": {
    "error": {
    "message": "Too many concurrent requests",
    "message": "Too many concurrent requests",
    "retry_after": throttle_config["timeout_seconds"],
    "retry_after": throttle_config["timeout_seconds"],
    }
    }
    }
    }


    # Increment active request count
    # Increment active request count
    active_requests[client_id] = active_count + 1
    active_requests[client_id] = active_count + 1


    try:
    try:
    # Simulate processing time
    # Simulate processing time
    await asyncio.sleep(0.1)
    await asyncio.sleep(0.1)


    # Return success response
    # Return success response
    return {"status": "ok", "concurrent_requests": active_count + 1}
    return {"status": "ok", "concurrent_requests": active_count + 1}
finally:
finally:
    # Decrement active request count
    # Decrement active request count
    with active_requests_lock:
    with active_requests_lock:
    active_requests[client_id] = max(
    active_requests[client_id] = max(
    0, active_requests.get(client_id, 1) - 1
    0, active_requests.get(client_id, 1) - 1
    )
    )


    async def handle_degradation(
    async def handle_degradation(
    request: Request, response: Response
    request: Request, response: Response
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Handle degradation testing.
    Handle degradation testing.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    # Get start time
    # Get start time
    start_time = time.time()
    start_time = time.time()


    # Simulate variable processing time based on load
    # Simulate variable processing time based on load
    # More concurrent requests = longer processing time
    # More concurrent requests = longer processing time
    concurrent_requests = sum(active_requests.values())
    concurrent_requests = sum(active_requests.values())
    delay = 0.01 * (1 + concurrent_requests)
    delay = 0.01 * (1 + concurrent_requests)


    # Add some randomness
    # Add some randomness
    delay *= 0.8 + 0.4 * random.random()
    delay *= 0.8 + 0.4 * random.random()


    # Cap the delay
    # Cap the delay
    delay = min(delay, 2.0)
    delay = min(delay, 2.0)


    # Simulate processing
    # Simulate processing
    await asyncio.sleep(delay)
    await asyncio.sleep(delay)


    # Calculate response time
    # Calculate response time
    response_time = time.time() - start_time
    response_time = time.time() - start_time


    # Add response time header
    # Add response time header
    response.headers["X-Response-Time"] = str(response_time)
    response.headers["X-Response-Time"] = str(response_time)


    # Return success response
    # Return success response
    return {
    return {
    "status": "ok",
    "status": "ok",
    "response_time": response_time,
    "response_time": response_time,
    "concurrent_requests": concurrent_requests,
    "concurrent_requests": concurrent_requests,
    }
    }


    async def handle_quota(client_id: str, response: Response) -> Dict[str, Any]:
    async def handle_quota(client_id: str, response: Response) -> Dict[str, Any]:
    """
    """
    Handle quota-based limiting.
    Handle quota-based limiting.


    Args:
    Args:
    client_id: Client identifier
    client_id: Client identifier
    response: FastAPI response
    response: FastAPI response


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    # Get the customer ID from the request headers or use a default
    # Get the customer ID from the request headers or use a default
    # In a real implementation, this would come from authentication
    # In a real implementation, this would come from authentication
    customer_id = list(quota_config.keys())[0] if quota_config else "test-customer"
    customer_id = list(quota_config.keys())[0] if quota_config else "test-customer"


    # If no quota is configured, create a default one for testing
    # If no quota is configured, create a default one for testing
    if customer_id not in quota_config:
    if customer_id not in quota_config:
    quota_config[customer_id] = {
    quota_config[customer_id] = {
    "daily_limit": 1000,
    "daily_limit": 1000,
    "monthly_limit": 10000,
    "monthly_limit": 10000,
    "overage_allowed": True,
    "overage_allowed": True,
    "overage_rate": 1.5,
    "overage_rate": 1.5,
    }
    }


    # Get quota configuration
    # Get quota configuration
    config = quota_config[customer_id]
    config = quota_config[customer_id]


    # Initialize quota usage if not exists
    # Initialize quota usage if not exists
    if customer_id not in quota_usage:
    if customer_id not in quota_usage:
    quota_usage[customer_id] = {"daily": 0, "monthly": 0}
    quota_usage[customer_id] = {"daily": 0, "monthly": 0}


    # Get current usage
    # Get current usage
    usage = quota_usage[customer_id]
    usage = quota_usage[customer_id]


    # Check if daily quota is exceeded
    # Check if daily quota is exceeded
    if usage["daily"] >= config["daily_limit"] and not config["overage_allowed"]:
    if usage["daily"] >= config["daily_limit"] and not config["overage_allowed"]:
    response.status_code = 429
    response.status_code = 429
    return {
    return {
    "error": {
    "error": {
    "message": "Daily quota exceeded",
    "message": "Daily quota exceeded",
    "limit": config["daily_limit"],
    "limit": config["daily_limit"],
    "usage": usage["daily"],
    "usage": usage["daily"],
    }
    }
    }
    }


    # Check if monthly quota is exceeded
    # Check if monthly quota is exceeded
    if (
    if (
    usage["monthly"] >= config["monthly_limit"]
    usage["monthly"] >= config["monthly_limit"]
    and not config["overage_allowed"]
    and not config["overage_allowed"]
    ):
    ):
    response.status_code = 429
    response.status_code = 429
    return {
    return {
    "error": {
    "error": {
    "message": "Monthly quota exceeded",
    "message": "Monthly quota exceeded",
    "limit": config["monthly_limit"],
    "limit": config["monthly_limit"],
    "usage": usage["monthly"],
    "usage": usage["monthly"],
    }
    }
    }
    }


    # Increment usage
    # Increment usage
    usage["daily"] += 1
    usage["daily"] += 1
    usage["monthly"] += 1
    usage["monthly"] += 1
    quota_usage[customer_id] = usage
    quota_usage[customer_id] = usage


    # Add quota headers
    # Add quota headers
    response.headers["X-Daily-Quota-Limit"] = str(config["daily_limit"])
    response.headers["X-Daily-Quota-Limit"] = str(config["daily_limit"])
    response.headers["X-Daily-Quota-Remaining"] = str(
    response.headers["X-Daily-Quota-Remaining"] = str(
    max(0, config["daily_limit"] - usage["daily"])
    max(0, config["daily_limit"] - usage["daily"])
    )
    )
    response.headers["X-Monthly-Quota-Limit"] = str(config["monthly_limit"])
    response.headers["X-Monthly-Quota-Limit"] = str(config["monthly_limit"])
    response.headers["X-Monthly-Quota-Remaining"] = str(
    response.headers["X-Monthly-Quota-Remaining"] = str(
    max(0, config["monthly_limit"] - usage["monthly"])
    max(0, config["monthly_limit"] - usage["monthly"])
    )
    )


    # Return success response
    # Return success response
    return {
    return {
    "status": "ok",
    "status": "ok",
    "daily_usage": usage["daily"],
    "daily_usage": usage["daily"],
    "monthly_usage": usage["monthly"],
    "monthly_usage": usage["monthly"],
    }
    }


    def get_client_id(request: Request) -> str:
    def get_client_id(request: Request) -> str:
    """
    """
    Get client identifier from request.
    Get client identifier from request.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request


    Returns:
    Returns:
    Client identifier
    Client identifier
    """
    """
    # Use client IP as identifier
    # Use client IP as identifier
    return request.client.host if request.client else "unknown"
    return request.client.host if request.client else "unknown"


    def check_rate_limit(
    def check_rate_limit(
    client_id: str, endpoint: str, config: Dict[str, Any]
    client_id: str, endpoint: str, config: Dict[str, Any]
    ) -> tuple:
    ) -> tuple:
    """
    """
    Check if a request should be rate limited.
    Check if a request should be rate limited.


    Args:
    Args:
    client_id: Client identifier
    client_id: Client identifier
    endpoint: Endpoint name
    endpoint: Endpoint name
    config: Rate limit configuration
    config: Rate limit configuration


    Returns:
    Returns:
    Tuple of (allowed, info)
    Tuple of (allowed, info)
    """
    """
    # Get current time
    # Get current time
    current_time = time.time()
    current_time = time.time()


    # Initialize request history for client and endpoint
    # Initialize request history for client and endpoint
    key = f"{client_id}:{endpoint}"
    key = f"{client_id}:{endpoint}"
    if key not in request_history:
    if key not in request_history:
    request_history[key] = []
    request_history[key] = []


    # Remove requests older than the window
    # Remove requests older than the window
    window = config["window"]
    window = config["window"]
    request_history[key] = [
    request_history[key] = [
    timestamp
    timestamp
    for timestamp in request_history[key]
    for timestamp in request_history[key]
    if current_time - timestamp < window
    if current_time - timestamp < window
    ]
    ]


    # Check if rate limit is exceeded
    # Check if rate limit is exceeded
    limit = config["limit"]
    limit = config["limit"]
    count = len(request_history[key])
    count = len(request_history[key])
    allowed = count < limit
    allowed = count < limit


    # Calculate reset time
    # Calculate reset time
    if count > 0:
    if count > 0:
    oldest = min(request_history[key]) if request_history[key] else current_time
    oldest = min(request_history[key]) if request_history[key] else current_time
    reset_after = max(0, window - (current_time - oldest))
    reset_after = max(0, window - (current_time - oldest))
    else:
    else:
    reset_after = 0
    reset_after = 0


    # Add current request to history if allowed
    # Add current request to history if allowed
    if allowed:
    if allowed:
    request_history[key].append(current_time)
    request_history[key].append(current_time)


    # Return rate limit info
    # Return rate limit info
    return allowed, {
    return allowed, {
    "limit": limit,
    "limit": limit,
    "remaining": max(0, limit - count - (1 if allowed else 0)),
    "remaining": max(0, limit - count - (1 if allowed else 0)),
    "reset": reset_after,
    "reset": reset_after,
    "retry_after": reset_after if not allowed else 0,
    "retry_after": reset_after if not allowed else 0,
    }
    }


    def add_rate_limit_headers(response: Response, info: Dict[str, Any]) -> None:
    def add_rate_limit_headers(response: Response, info: Dict[str, Any]) -> None:
    """
    """
    Add rate limit headers to response.
    Add rate limit headers to response.


    Args:
    Args:
    response: FastAPI response
    response: FastAPI response
    info: Rate limit information
    info: Rate limit information
    """
    """
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(
    response.headers["X-RateLimit-Reset"] = str(
    int(info["reset"])
    int(info["reset"])
    )  # Convert to integer
    )  # Convert to integer


    if info["retry_after"] > 0:
    if info["retry_after"] > 0:
    response.headers["Retry-After"] = str(
    response.headers["Retry-After"] = str(
    int(info["retry_after"]
    int(info["retry_after"]
    # Convert to integer
    # Convert to integer


    return router
    return router