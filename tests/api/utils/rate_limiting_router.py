"""
Rate limiting router for API tests.

This module provides a router for testing rate limiting functionality.
"""


import asyncio
import random
import threading
import time
from typing import Any, Dict

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, ConfigDict


class RateLimitConfig

(BaseModel):
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
    Create a router for rate limiting tests.

    Returns:
        FastAPI router
    """
    router = APIRouter()

    # Store rate limit state
    rate_limits = {
        "test-rate-limit": {"limit": 3, "window": 60},
        "test-rate-limit-reset": {"limit": 3, "window": 60},
        "test-custom-rate-limit": {"limit": 10, "window": 1},  # 10 per second
        "test-ip-rate-limit": {"limit": 3, "window": 60},
        "test-concurrent-throttling": {"limit": 3, "window": 60},
        "test-degradation": {"limit": 20, "window": 60},
        "test-quota-limit": {"limit": 10, "window": 60},
    }

    # Store request history
    request_history = {}

    # Store throttling configuration
    throttle_config = {"max_concurrent_requests": 3, "timeout_seconds": 5}

    # Store active requests for throttling
    active_requests = {}
    active_requests_lock = threading.Lock()

    # Store quota configuration
    quota_config = {}
    quota_usage = {}

    @router.get("/{endpoint}")
    async def rate_limited_endpoint(
        endpoint: str, request: Request, response: Response
    ):
        """
        Generic rate-limited endpoint.

        Args:
            endpoint: Endpoint name
            request: FastAPI request
            response: FastAPI response

        Returns:
            Response data
        """
        # Get client identifier
        client_id = get_client_id(request)

        # Handle IP-based rate limiting
        if endpoint == "test-ip-rate-limit":
            client_id = request.headers.get("X-Forwarded-For", client_id)

        # Handle throttling
        if endpoint == "test-concurrent-throttling":
            return await handle_throttling(client_id, response)

        # Handle degradation testing
        if endpoint == "test-degradation":
            return await handle_degradation(request, response)

        # Handle quota-based limiting
        if endpoint == "test-quota-limit":
            return await handle_quota(client_id, response)

        # Get rate limit configuration
        limit_config = rate_limits.get(endpoint, {"limit": 3, "window": 60})

        # Check rate limit
        allowed, info = check_rate_limit(client_id, endpoint, limit_config)

        # Add rate limit headers
        add_rate_limit_headers(response, info)

        # Return 429 if rate limited
        if not allowed:
            response.status_code = 429
            return {
                "error": {
                    "message": "Rate limit exceeded",
                    "retry_after": info["retry_after"],
                }
            }

        # Return success response
        return {"status": "ok", "endpoint": endpoint, "client_id": client_id}

    @router.post("/config")
    async def configure_rate_limits(config: RateLimitConfig, response: Response):
        """
        Configure custom rate limits.

        Args:
            config: Rate limit configuration
            response: FastAPI response

        Returns:
            Configuration status
        """
        # Update rate limit configuration for custom rate limit endpoint
        if "requests_per_second" in config.limits:
            rate_limits["test-custom-rate-limit"] = {
                "limit": config.limits["requests_per_second"],
                "window": 1,  # 1 second window
            }

        return {
            "status": "ok",
            "message": "Rate limit configuration updated",
            "tier": config.tier,
            "limits": config.limits,
        }

    @router.post("/throttle-config")
    async def configure_throttling(config: ThrottleConfig, response: Response):
        """
        Configure request throttling.

        Args:
            config: Throttling configuration
            response: FastAPI response

        Returns:
            Configuration status
        """
        # Update throttling configuration
        throttle_config["max_concurrent_requests"] = config.max_concurrent_requests
        throttle_config["timeout_seconds"] = config.timeout_seconds

        return {
            "status": "ok",
            "message": "Throttling configuration updated",
            "config": throttle_config,
        }

    @router.post("/quota")
    async def configure_quota(config: QuotaConfig, response: Response):
        """
        Configure customer-specific quota.

        Args:
            config: Quota configuration
            response: FastAPI response

        Returns:
            Configuration status
        """
        # Update quota configuration
        quota_config[config.customer_id] = {
            "daily_limit": config.daily_limit,
            "monthly_limit": config.monthly_limit,
            "overage_allowed": config.overage_allowed,
            "overage_rate": config.overage_rate,
        }

        # Initialize quota usage
        if config.customer_id not in quota_usage:
            quota_usage[config.customer_id] = {"daily": 0, "monthly": 0}

        return {
            "status": "ok",
            "message": "Quota configuration updated",
            "customer_id": config.customer_id,
            "config": quota_config[config.customer_id],
        }

    async def handle_throttling(client_id: str, response: Response) -> Dict[str, Any]:
        """
        Handle concurrent request throttling.

        Args:
            client_id: Client identifier
            response: FastAPI response

        Returns:
            Response data
        """
        # Check if we're already at max concurrent requests
        with active_requests_lock:
            active_count = active_requests.get(client_id, 0)

            if active_count >= throttle_config["max_concurrent_requests"]:
                response.status_code = 429
                response.headers["Retry-After"] = str(
                    throttle_config["timeout_seconds"]
                )
                return {
                    "error": {
                        "message": "Too many concurrent requests",
                        "retry_after": throttle_config["timeout_seconds"],
                    }
                }

            # Increment active request count
            active_requests[client_id] = active_count + 1

        try:
            # Simulate processing time
            await asyncio.sleep(0.1)

            # Return success response
            return {"status": "ok", "concurrent_requests": active_count + 1}
        finally:
            # Decrement active request count
            with active_requests_lock:
                active_requests[client_id] = max(
                    0, active_requests.get(client_id, 1) - 1
                )

    async def handle_degradation(
        request: Request, response: Response
    ) -> Dict[str, Any]:
        """
        Handle degradation testing.

        Args:
            request: FastAPI request
            response: FastAPI response

        Returns:
            Response data
        """
        # Get start time
        start_time = time.time()

        # Simulate variable processing time based on load
        # More concurrent requests = longer processing time
        concurrent_requests = sum(active_requests.values())
        delay = 0.01 * (1 + concurrent_requests)

        # Add some randomness
        delay *= 0.8 + 0.4 * random.random()

        # Cap the delay
        delay = min(delay, 2.0)

        # Simulate processing
        await asyncio.sleep(delay)

        # Calculate response time
        response_time = time.time() - start_time

        # Add response time header
        response.headers["X-Response-Time"] = str(response_time)

        # Return success response
        return {
            "status": "ok",
            "response_time": response_time,
            "concurrent_requests": concurrent_requests,
        }

    async def handle_quota(client_id: str, response: Response) -> Dict[str, Any]:
        """
        Handle quota-based limiting.

        Args:
            client_id: Client identifier
            response: FastAPI response

        Returns:
            Response data
        """
        # Get the customer ID from the request headers or use a default
        # In a real implementation, this would come from authentication
        customer_id = list(quota_config.keys())[0] if quota_config else "test-customer"

        # If no quota is configured, create a default one for testing
        if customer_id not in quota_config:
            quota_config[customer_id] = {
                "daily_limit": 1000,
                "monthly_limit": 10000,
                "overage_allowed": True,
                "overage_rate": 1.5,
            }

        # Get quota configuration
        config = quota_config[customer_id]

        # Initialize quota usage if not exists
        if customer_id not in quota_usage:
            quota_usage[customer_id] = {"daily": 0, "monthly": 0}

        # Get current usage
        usage = quota_usage[customer_id]

        # Check if daily quota is exceeded
        if usage["daily"] >= config["daily_limit"] and not config["overage_allowed"]:
            response.status_code = 429
            return {
                "error": {
                    "message": "Daily quota exceeded",
                    "limit": config["daily_limit"],
                    "usage": usage["daily"],
                }
            }

        # Check if monthly quota is exceeded
        if (
            usage["monthly"] >= config["monthly_limit"]
            and not config["overage_allowed"]
        ):
            response.status_code = 429
            return {
                "error": {
                    "message": "Monthly quota exceeded",
                    "limit": config["monthly_limit"],
                    "usage": usage["monthly"],
                }
            }

        # Increment usage
        usage["daily"] += 1
        usage["monthly"] += 1
        quota_usage[customer_id] = usage

        # Add quota headers
        response.headers["X-Daily-Quota-Limit"] = str(config["daily_limit"])
        response.headers["X-Daily-Quota-Remaining"] = str(
            max(0, config["daily_limit"] - usage["daily"])
        )
        response.headers["X-Monthly-Quota-Limit"] = str(config["monthly_limit"])
        response.headers["X-Monthly-Quota-Remaining"] = str(
            max(0, config["monthly_limit"] - usage["monthly"])
        )

        # Return success response
        return {
            "status": "ok",
            "daily_usage": usage["daily"],
            "monthly_usage": usage["monthly"],
        }

    def get_client_id(request: Request) -> str:
        """
        Get client identifier from request.

        Args:
            request: FastAPI request

        Returns:
            Client identifier
        """
        # Use client IP as identifier
        return request.client.host if request.client else "unknown"

    def check_rate_limit(
        client_id: str, endpoint: str, config: Dict[str, Any]
    ) -> tuple:
        """
        Check if a request should be rate limited.

        Args:
            client_id: Client identifier
            endpoint: Endpoint name
            config: Rate limit configuration

        Returns:
            Tuple of (allowed, info)
        """
        # Get current time
        current_time = time.time()

        # Initialize request history for client and endpoint
        key = f"{client_id}:{endpoint}"
        if key not in request_history:
            request_history[key] = []

        # Remove requests older than the window
        window = config["window"]
        request_history[key] = [
            timestamp
            for timestamp in request_history[key]
            if current_time - timestamp < window
        ]

        # Check if rate limit is exceeded
        limit = config["limit"]
        count = len(request_history[key])
        allowed = count < limit

        # Calculate reset time
        if count > 0:
            oldest = min(request_history[key]) if request_history[key] else current_time
            reset_after = max(0, window - (current_time - oldest))
        else:
            reset_after = 0

        # Add current request to history if allowed
        if allowed:
            request_history[key].append(current_time)

        # Return rate limit info
        return allowed, {
            "limit": limit,
            "remaining": max(0, limit - count - (1 if allowed else 0)),
            "reset": reset_after,
            "retry_after": reset_after if not allowed else 0,
        }

    def add_rate_limit_headers(response: Response, info: Dict[str, Any]) -> None:
        """
        Add rate limit headers to response.

        Args:
            response: FastAPI response
            info: Rate limit information
        """
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(
            int(info["reset"])
        )  # Convert to integer

        if info["retry_after"] > 0:
            response.headers["Retry-After"] = str(
                int(info["retry_after"])
            )  # Convert to integer

    return router