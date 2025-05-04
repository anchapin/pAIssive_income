"""
Middleware for webhook security.

This module provides FastAPI middleware for webhook security:
1. IP allowlisting
2. Rate limiting
"""

import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.audit_service import AuditService
from ..services.webhook_security import WebhookIPAllowlist, WebhookRateLimiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookIPAllowlistMiddleware(BaseHTTPMiddleware):
    """Middleware for IP allowlisting."""

    def __init__(
        self,
        app,
        allowlist: Optional[WebhookIPAllowlist] = None,
        webhook_path_prefix: str = " / api / v1 / webhooks",
        audit_service: Optional[AuditService] = None,
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            allowlist: IP allowlist to use
            webhook_path_prefix: Path prefix for webhook endpoints
            audit_service: Audit service for recording events
        """
        super().__init__(app)
        self.allowlist = allowlist or WebhookIPAllowlist()
        self.webhook_path_prefix = webhook_path_prefix
        self.audit_service = audit_service or AuditService()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Only apply to webhook endpoints
        if not request.url.path.startswith(self.webhook_path_prefix):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else None

        # Check if IP is allowed
        if client_ip and not self.allowlist.is_allowed(client_ip):
            logger.warning(f"Blocked request from disallowed IP: {client_ip}")

            # Record audit event
            if self.audit_service:
                self.audit_service.create_event(
                    event_type="webhook.ip.blocked",
                    resource_type="webhook",
                    action="block",
                    resource_id=None,
                    actor_id=None,
                    actor_type="system",
                    status="warning",
                    details={
                        "ip_address": client_ip,
                        "path": request.url.path,
                        "method": request.method,
                    },
                    ip_address=client_ip,
                    user_agent=request.headers.get("user - agent"),
                )

            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                    content={"detail": "IP address not allowed"}
            )

        # Continue processing
        return await call_next(request)

class WebhookRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting webhook requests."""

    def __init__(
        self,
        app,
        rate_limiter: Optional[WebhookRateLimiter] = None,
        webhook_path_prefix: str = " / api / v1 / webhooks",
        limit: int = 100,
        window_seconds: int = 60,
        audit_service: Optional[AuditService] = None,
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            rate_limiter: Rate limiter to use
            webhook_path_prefix: Path prefix for webhook endpoints
            limit: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
            audit_service: Audit service for recording events
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter or WebhookRateLimiter(limit, window_seconds)
        self.webhook_path_prefix = webhook_path_prefix
        self.audit_service = audit_service or AuditService()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Only apply to webhook endpoints
        if not request.url.path.startswith(self.webhook_path_prefix):
            return await call_next(request)

        # Get client IP for rate limiting key
        client_ip = request.client.host if request.client else "unknown"

        # Check if rate limited
        if self.rate_limiter.is_rate_limited(client_ip):
            logger.warning(f"Rate limited request from IP: {client_ip}")

            # Record audit event
            if self.audit_service:
                self.audit_service.create_event(
                    event_type="webhook.rate_limited",
                    resource_type="webhook",
                    action="limit",
                    resource_id=None,
                    actor_id=None,
                    actor_type="system",
                    status="warning",
                    details={
                        "ip_address": client_ip,
                        "path": request.url.path,
                        "method": request.method,
                        "limit": self.rate_limiter.limit,
                        "window_seconds": self.rate_limiter.window_seconds,
                    },
                    ip_address=client_ip,
                    user_agent=request.headers.get("user - agent"),
                )

            # Get reset time
            reset_time = self.rate_limiter.get_reset_time(client_ip)
            reset_seconds = int(reset_time - time.time()) if reset_time else 60

            # Create response with rate limit headers
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
            )

            # Add rate limit headers
            response.headers["X - RateLimit - Limit"] = str(self.rate_limiter.limit)
            response.headers["X - RateLimit - Remaining"] = "0"
            response.headers["X - \
                RateLimit - Reset"] = str(int(reset_time)) if reset_time else ""
            response.headers["Retry - After"] = str(reset_seconds)

            return response

        # Add request to rate limiter
        self.rate_limiter.add_request(client_ip)

        # Process the request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = self.rate_limiter.get_remaining_requests(client_ip)
        reset_time = self.rate_limiter.get_reset_time(client_ip)

        response.headers["X - RateLimit - Limit"] = str(self.rate_limiter.limit)
        response.headers["X - RateLimit - Remaining"] = str(remaining)
        response.headers["X - \
            RateLimit - Reset"] = str(int(reset_time)) if reset_time else ""

        return response
