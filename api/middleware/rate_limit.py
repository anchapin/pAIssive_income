"""
Rate limiting middleware for the API server.

This module provides rate limiting middleware for the API server.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta

from ..config import APIConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import FastAPI, Request, Response
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for rate limiting middleware")
    FASTAPI_AVAILABLE = False


class RateLimitMiddleware:
    """
    Rate limiting middleware for the API server.
    """
    
    def __init__(self, config: APIConfig):
        """
        Initialize the rate limiting middleware.
        
        Args:
            config: API configuration
        """
        self.config = config
        self.rate_limit_requests = config.rate_limit_requests
        self.rate_limit_period = config.rate_limit_period
        
        # Initialize request tracking
        self.request_counts: Dict[str, List[float]] = {}
    
    def is_rate_limited(self, client_id: str) -> bool:
        """
        Check if a client is rate limited.
        
        Args:
            client_id: Client identifier (e.g., IP address)
            
        Returns:
            True if the client is rate limited, False otherwise
        """
        # Get current time
        current_time = time.time()
        
        # Get request timestamps for the client
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []
        
        # Remove old timestamps
        self.request_counts[client_id] = [
            ts for ts in self.request_counts[client_id]
            if current_time - ts < self.rate_limit_period
        ]
        
        # Check if the client has exceeded the rate limit
        if len(self.request_counts[client_id]) >= self.rate_limit_requests:
            return True
        
        # Add current timestamp
        self.request_counts[client_id].append(current_time)
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """
        Get the number of remaining requests for a client.
        
        Args:
            client_id: Client identifier (e.g., IP address)
            
        Returns:
            Number of remaining requests
        """
        # Get current time
        current_time = time.time()
        
        # Get request timestamps for the client
        if client_id not in self.request_counts:
            return self.rate_limit_requests
        
        # Remove old timestamps
        self.request_counts[client_id] = [
            ts for ts in self.request_counts[client_id]
            if current_time - ts < self.rate_limit_period
        ]
        
        # Calculate remaining requests
        return max(0, self.rate_limit_requests - len(self.request_counts[client_id]))
    
    def get_reset_time(self, client_id: str) -> float:
        """
        Get the time until the rate limit resets for a client.
        
        Args:
            client_id: Client identifier (e.g., IP address)
            
        Returns:
            Time until the rate limit resets in seconds
        """
        # Get current time
        current_time = time.time()
        
        # Get request timestamps for the client
        if client_id not in self.request_counts or not self.request_counts[client_id]:
            return 0
        
        # Get the oldest timestamp
        oldest_timestamp = min(self.request_counts[client_id])
        
        # Calculate reset time
        return max(0, self.rate_limit_period - (current_time - oldest_timestamp))


def setup_rate_limit_middleware(app: Any, config: APIConfig) -> None:
    """
    Set up rate limiting middleware for the API server.
    
    Args:
        app: FastAPI application
        config: API configuration
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI is required for rate limiting middleware")
        return
    
    # Create middleware
    rate_limit_middleware = RateLimitMiddleware(config)
    
    @app.middleware("http")
    async def rate_limit_middleware_func(request: Request, call_next: Callable) -> Response:
        """
        Rate limiting middleware function.
        
        Args:
            request: HTTP request
            call_next: Next middleware function
            
        Returns:
            HTTP response
        """
        # Skip rate limiting for certain paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client ID (IP address)
        client_id = request.client.host if request.client else "unknown"
        
        # Check if the client is rate limited
        if rate_limit_middleware.is_rate_limited(client_id):
            # Get reset time
            reset_time = rate_limit_middleware.get_reset_time(client_id)
            
            # Return rate limit exceeded response
            return Response(
                status_code=429,
                content='{"detail":"Rate limit exceeded"}',
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(rate_limit_middleware.rate_limit_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(int(reset_time))
                }
            )
        
        # Get remaining requests
        remaining_requests = rate_limit_middleware.get_remaining_requests(client_id)
        
        # Get reset time
        reset_time = rate_limit_middleware.get_reset_time(client_id)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit_middleware.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        
        return response
