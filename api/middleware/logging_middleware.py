"""
Logging middleware for the API server.

This module provides middleware for request logging and performance monitoring.
"""

import logging
import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.logging_service import LoggingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""
    
    def __init__(
        self, 
        app,
        logging_service: Optional[LoggingService] = None,
        exclude_paths: list = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            logging_service: Logging service
            exclude_paths: Paths to exclude from logging
        """
        super().__init__(app)
        self.logging_service = logging_service or LoggingService()
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Get start time
        start_time = time.time()
        
        # Get client info
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Get user ID if available
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
        elif hasattr(request.state, "api_key") and request.state.api_key:
            user_id = request.state.api_key.user_id
        
        # Process request
        try:
            # Add request ID header to response
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log request
            self.logging_service.log_api_request(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=user_id,
                ip_address=client_host,
                user_agent=user_agent,
                request_size=int(request.headers.get("content-length", 0)),
                response_size=int(response.headers.get("content-length", 0))
            )
            
            return response
        
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logging_service.log_api_request(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
                user_id=user_id,
                ip_address=client_host,
                user_agent=user_agent,
                request_size=int(request.headers.get("content-length", 0)),
                error=str(e)
            )
            
            # Re-raise exception
            raise

class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for security event logging."""
    
    def __init__(
        self, 
        app,
        logging_service: Optional[LoggingService] = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            logging_service: Logging service
        """
        super().__init__(app)
        self.logging_service = logging_service or LoggingService()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Process request
        response = await call_next(request)
        
        # Check for security-related responses
        if response.status_code == 401:
            # Log authentication failure
            self.logging_service.log_security_event(
                message="Authentication failed",
                level="WARNING",
                security_level="AUTH",
                event_type="auth.failed",
                ip_address=request.client.host if request.client else None,
                resource_type="api",
                action="access",
                status="failure",
                details={
                    "path": request.url.path,
                    "method": request.method,
                    "user_agent": request.headers.get("user-agent")
                }
            )
        
        elif response.status_code == 403:
            # Log authorization failure
            self.logging_service.log_security_event(
                message="Authorization failed",
                level="WARNING",
                security_level="AUTH",
                event_type="permission.denied",
                user_id=request.state.user.id if hasattr(request.state, "user") and request.state.user else None,
                ip_address=request.client.host if request.client else None,
                resource_type="api",
                action="access",
                status="failure",
                details={
                    "path": request.url.path,
                    "method": request.method,
                    "user_agent": request.headers.get("user-agent")
                }
            )
        
        elif response.status_code == 429:
            # Log rate limit exceeded
            self.logging_service.log_security_event(
                message="Rate limit exceeded",
                level="WARNING",
                security_level="SECURITY",
                event_type="rate_limit.exceeded",
                user_id=request.state.user.id if hasattr(request.state, "user") and request.state.user else None,
                ip_address=request.client.host if request.client else None,
                resource_type="api",
                action="limit",
                status="warning",
                details={
                    "path": request.url.path,
                    "method": request.method,
                    "user_agent": request.headers.get("user-agent")
                }
            )
        
        return response
