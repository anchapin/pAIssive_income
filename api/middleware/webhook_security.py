"""
"""
Middleware for webhook security.
Middleware for webhook security.


This module provides FastAPI middleware for webhook security:
    This module provides FastAPI middleware for webhook security:
    1. IP allowlisting
    1. IP allowlisting
    2. Rate limiting
    2. Rate limiting
    """
    """




    import logging
    import logging
    import time
    import time
    from typing import Callable, Optional
    from typing import Callable, Optional


    from fastapi import Request, Response, status
    from fastapi import Request, Response, status
    from fastapi.responses import JSONResponse
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware


    from ..services.audit_service import AuditService
    from ..services.audit_service import AuditService
    from ..services.webhook_security import WebhookIPAllowlist, WebhookRateLimiter
    from ..services.webhook_security import WebhookIPAllowlist, WebhookRateLimiter


    # Configure logging
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    class WebhookIPAllowlistMiddleware(BaseHTTPMiddleware):
    class WebhookIPAllowlistMiddleware(BaseHTTPMiddleware):
    """Middleware for IP allowlisting."""

    def __init__(
    self,
    app,
    allowlist: Optional[WebhookIPAllowlist] = None,
    webhook_path_prefix: str = "/api/v1/webhooks",
    audit_service: Optional[AuditService] = None,
    ):
    """
    """
    Initialize the middleware.
    Initialize the middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    allowlist: IP allowlist to use
    allowlist: IP allowlist to use
    webhook_path_prefix: Path prefix for webhook endpoints
    webhook_path_prefix: Path prefix for webhook endpoints
    audit_service: Audit service for recording events
    audit_service: Audit service for recording events
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.allowlist = allowlist or WebhookIPAllowlist()
    self.allowlist = allowlist or WebhookIPAllowlist()
    self.webhook_path_prefix = webhook_path_prefix
    self.webhook_path_prefix = webhook_path_prefix
    self.audit_service = audit_service or AuditService()
    self.audit_service = audit_service or AuditService()


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    """
    Process the request.
    Process the request.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    call_next: Next middleware or route handler
    call_next: Next middleware or route handler


    Returns:
    Returns:
    Response
    Response
    """
    """
    # Only apply to webhook endpoints
    # Only apply to webhook endpoints
    if not request.url.path.startswith(self.webhook_path_prefix):
    if not request.url.path.startswith(self.webhook_path_prefix):
    return await call_next(request)
    return await call_next(request)


    # Get client IP
    # Get client IP
    client_ip = request.client.host if request.client else None
    client_ip = request.client.host if request.client else None


    # Check if IP is allowed
    # Check if IP is allowed
    if client_ip and not self.allowlist.is_allowed(client_ip):
    if client_ip and not self.allowlist.is_allowed(client_ip):
    logger.warning(f"Blocked request from disallowed IP: {client_ip}")
    logger.warning(f"Blocked request from disallowed IP: {client_ip}")


    # Record audit event
    # Record audit event
    if self.audit_service:
    if self.audit_service:
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.ip.blocked",
    event_type="webhook.ip.blocked",
    resource_type="webhook",
    resource_type="webhook",
    action="block",
    action="block",
    resource_id=None,
    resource_id=None,
    actor_id=None,
    actor_id=None,
    actor_type="system",
    actor_type="system",
    status="warning",
    status="warning",
    details={
    details={
    "ip_address": client_ip,
    "ip_address": client_ip,
    "path": request.url.path,
    "path": request.url.path,
    "method": request.method,
    "method": request.method,
    },
    },
    ip_address=client_ip,
    ip_address=client_ip,
    user_agent=request.headers.get("user-agent"),
    user_agent=request.headers.get("user-agent"),
    )
    )


    return JSONResponse(
    return JSONResponse(
    status_code=status.HTTP_403_FORBIDDEN,
    status_code=status.HTTP_403_FORBIDDEN,
    content={"detail": "IP address not allowed"},
    content={"detail": "IP address not allowed"},
    )
    )


    # Continue processing
    # Continue processing
    return await call_next(request)
    return await call_next(request)




    class WebhookRateLimitMiddleware(BaseHTTPMiddleware):
    class WebhookRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting webhook requests."""

    def __init__(
    self,
    app,
    rate_limiter: Optional[WebhookRateLimiter] = None,
    webhook_path_prefix: str = "/api/v1/webhooks",
    limit: int = 100,
    window_seconds: int = 60,
    audit_service: Optional[AuditService] = None,
    ):
    """
    """
    Initialize the middleware.
    Initialize the middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    rate_limiter: Rate limiter to use
    rate_limiter: Rate limiter to use
    webhook_path_prefix: Path prefix for webhook endpoints
    webhook_path_prefix: Path prefix for webhook endpoints
    limit: Maximum number of requests allowed in the time window
    limit: Maximum number of requests allowed in the time window
    window_seconds: Time window in seconds
    window_seconds: Time window in seconds
    audit_service: Audit service for recording events
    audit_service: Audit service for recording events
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.rate_limiter = rate_limiter or WebhookRateLimiter(limit, window_seconds)
    self.rate_limiter = rate_limiter or WebhookRateLimiter(limit, window_seconds)
    self.webhook_path_prefix = webhook_path_prefix
    self.webhook_path_prefix = webhook_path_prefix
    self.audit_service = audit_service or AuditService()
    self.audit_service = audit_service or AuditService()


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    """
    Process the request.
    Process the request.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    call_next: Next middleware or route handler
    call_next: Next middleware or route handler


    Returns:
    Returns:
    Response
    Response
    """
    """
    # Only apply to webhook endpoints
    # Only apply to webhook endpoints
    if not request.url.path.startswith(self.webhook_path_prefix):
    if not request.url.path.startswith(self.webhook_path_prefix):
    return await call_next(request)
    return await call_next(request)


    # Get client IP for rate limiting key
    # Get client IP for rate limiting key
    client_ip = request.client.host if request.client else "unknown"
    client_ip = request.client.host if request.client else "unknown"


    # Check if rate limited
    # Check if rate limited
    if self.rate_limiter.is_rate_limited(client_ip):
    if self.rate_limiter.is_rate_limited(client_ip):
    logger.warning(f"Rate limited request from IP: {client_ip}")
    logger.warning(f"Rate limited request from IP: {client_ip}")


    # Record audit event
    # Record audit event
    if self.audit_service:
    if self.audit_service:
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.rate_limited",
    event_type="webhook.rate_limited",
    resource_type="webhook",
    resource_type="webhook",
    action="limit",
    action="limit",
    resource_id=None,
    resource_id=None,
    actor_id=None,
    actor_id=None,
    actor_type="system",
    actor_type="system",
    status="warning",
    status="warning",
    details={
    details={
    "ip_address": client_ip,
    "ip_address": client_ip,
    "path": request.url.path,
    "path": request.url.path,
    "method": request.method,
    "method": request.method,
    "limit": self.rate_limiter.limit,
    "limit": self.rate_limiter.limit,
    "window_seconds": self.rate_limiter.window_seconds,
    "window_seconds": self.rate_limiter.window_seconds,
    },
    },
    ip_address=client_ip,
    ip_address=client_ip,
    user_agent=request.headers.get("user-agent"),
    user_agent=request.headers.get("user-agent"),
    )
    )


    # Get reset time
    # Get reset time
    reset_time = self.rate_limiter.get_reset_time(client_ip)
    reset_time = self.rate_limiter.get_reset_time(client_ip)
    reset_seconds = int(reset_time - time.time()) if reset_time else 60
    reset_seconds = int(reset_time - time.time()) if reset_time else 60


    # Create response with rate limit headers
    # Create response with rate limit headers
    response = JSONResponse(
    response = JSONResponse(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    content={"detail": "Rate limit exceeded"},
    content={"detail": "Rate limit exceeded"},
    )
    )


    # Add rate limit headers
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.limit)
    response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.limit)
    response.headers["X-RateLimit-Remaining"] = "0"
    response.headers["X-RateLimit-Remaining"] = "0"
    response.headers["X-RateLimit-Reset"] = (
    response.headers["X-RateLimit-Reset"] = (
    str(int(reset_time)) if reset_time else ""
    str(int(reset_time)) if reset_time else ""
    )
    )
    response.headers["Retry-After"] = str(reset_seconds)
    response.headers["Retry-After"] = str(reset_seconds)


    return response
    return response


    # Add request to rate limiter
    # Add request to rate limiter
    self.rate_limiter.add_request(client_ip)
    self.rate_limiter.add_request(client_ip)


    # Process the request
    # Process the request
    response = await call_next(request)
    response = await call_next(request)


    # Add rate limit headers to response
    # Add rate limit headers to response
    remaining = self.rate_limiter.get_remaining_requests(client_ip)
    remaining = self.rate_limiter.get_remaining_requests(client_ip)
    reset_time = self.rate_limiter.get_reset_time(client_ip)
    reset_time = self.rate_limiter.get_reset_time(client_ip)


    response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.limit)
    response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = (
    response.headers["X-RateLimit-Reset"] = (
    str(int(reset_time)) if reset_time else ""
    str(int(reset_time)) if reset_time else ""
    )
    )


    return response
    return response