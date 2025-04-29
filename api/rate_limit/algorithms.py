"""
Rate limiting algorithms.

This module provides various rate limiting algorithms.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple, List
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter(ABC):
    """
    Abstract base class for rate limiters.
    """
    
    @abstractmethod
    def check_rate_limit(self, key: str, cost: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Identifier for the client (e.g., IP address, API key)
            cost: Cost of the request (default: 1.0)
            
        Returns:
            Tuple of (allowed, limit_info)
            - allowed: True if the request is allowed, False if it should be rate limited
            - limit_info: Dictionary with rate limit information
        """
        pass


class FixedWindowRateLimiter(RateLimiter):
    """
    Fixed window rate limiter.
    
    This rate limiter uses a fixed time window to limit requests.
    """
    
    def __init__(self, limit: int, window: int):
        """
        Initialize the fixed window rate limiter.
        
        Args:
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
        """
        self.limit = limit
        self.window = window
        self.counters: Dict[str, Dict[str, Any]] = {}
    
    def check_rate_limit(self, key: str, cost: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Identifier for the client (e.g., IP address, API key)
            cost: Cost of the request (default: 1.0)
            
        Returns:
            Tuple of (allowed, limit_info)
            - allowed: True if the request is allowed, False if it should be rate limited
            - limit_info: Dictionary with rate limit information
        """
        current_time = int(time.time())
        window_start = current_time - (current_time % self.window)
        window_end = window_start + self.window
        
        # Initialize or reset counter if needed
        if key not in self.counters or self.counters[key]["window_start"] != window_start:
            self.counters[key] = {
                "window_start": window_start,
                "count": 0
            }
        
        # Check if limit is exceeded
        if self.counters[key]["count"] >= self.limit:
            reset_time = window_end
            retry_after = reset_time - current_time
            
            return False, {
                "limit": self.limit,
                "remaining": 0,
                "reset": reset_time,
                "retry_after": retry_after
            }
        
        # Increment counter
        self.counters[key]["count"] += cost
        remaining = max(0, self.limit - self.counters[key]["count"])
        
        return True, {
            "limit": self.limit,
            "remaining": remaining,
            "reset": window_end,
            "retry_after": 0
        }


class TokenBucketRateLimiter(RateLimiter):
    """
    Token bucket rate limiter.
    
    This rate limiter uses the token bucket algorithm to limit requests.
    """
    
    def __init__(self, rate: float, burst: int):
        """
        Initialize the token bucket rate limiter.
        
        Args:
            rate: Token refill rate per second
            burst: Maximum bucket size (burst capacity)
        """
        self.rate = rate
        self.burst = burst
        self.buckets: Dict[str, Dict[str, Any]] = {}
    
    def check_rate_limit(self, key: str, cost: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Identifier for the client (e.g., IP address, API key)
            cost: Cost of the request (default: 1.0)
            
        Returns:
            Tuple of (allowed, limit_info)
            - allowed: True if the request is allowed, False if it should be rate limited
            - limit_info: Dictionary with rate limit information
        """
        current_time = time.time()
        
        # Initialize bucket if needed
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.burst,
                "last_refill": current_time
            }
        
        # Refill tokens
        time_passed = current_time - self.buckets[key]["last_refill"]
        new_tokens = time_passed * self.rate
        self.buckets[key]["tokens"] = min(self.burst, self.buckets[key]["tokens"] + new_tokens)
        self.buckets[key]["last_refill"] = current_time
        
        # Check if enough tokens are available
        if self.buckets[key]["tokens"] < cost:
            # Calculate time until enough tokens are available
            tokens_needed = cost - self.buckets[key]["tokens"]
            retry_after = tokens_needed / self.rate
            reset_time = current_time + retry_after
            
            return False, {
                "limit": self.burst,
                "remaining": self.buckets[key]["tokens"],
                "reset": reset_time,
                "retry_after": retry_after
            }
        
        # Consume tokens
        self.buckets[key]["tokens"] -= cost
        
        # Calculate time until bucket is full
        time_to_full = (self.burst - self.buckets[key]["tokens"]) / self.rate
        reset_time = current_time + time_to_full
        
        return True, {
            "limit": self.burst,
            "remaining": self.buckets[key]["tokens"],
            "reset": reset_time,
            "retry_after": 0
        }


class LeakyBucketRateLimiter(RateLimiter):
    """
    Leaky bucket rate limiter.
    
    This rate limiter uses the leaky bucket algorithm to limit requests.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the leaky bucket rate limiter.
        
        Args:
            rate: Leak rate per second
            capacity: Bucket capacity
        """
        self.rate = rate
        self.capacity = capacity
        self.buckets: Dict[str, Dict[str, Any]] = {}
    
    def check_rate_limit(self, key: str, cost: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Identifier for the client (e.g., IP address, API key)
            cost: Cost of the request (default: 1.0)
            
        Returns:
            Tuple of (allowed, limit_info)
            - allowed: True if the request is allowed, False if it should be rate limited
            - limit_info: Dictionary with rate limit information
        """
        current_time = time.time()
        
        # Initialize bucket if needed
        if key not in self.buckets:
            self.buckets[key] = {
                "water_level": 0,
                "last_leak": current_time
            }
        
        # Leak water
        time_passed = current_time - self.buckets[key]["last_leak"]
        leaked = time_passed * self.rate
        self.buckets[key]["water_level"] = max(0, self.buckets[key]["water_level"] - leaked)
        self.buckets[key]["last_leak"] = current_time
        
        # Check if adding water would overflow the bucket
        if self.buckets[key]["water_level"] + cost > self.capacity:
            # Calculate time until enough water has leaked
            water_to_leak = self.buckets[key]["water_level"] + cost - self.capacity
            retry_after = water_to_leak / self.rate
            reset_time = current_time + retry_after
            
            return False, {
                "limit": self.capacity,
                "remaining": self.capacity - self.buckets[key]["water_level"],
                "reset": reset_time,
                "retry_after": retry_after
            }
        
        # Add water to bucket
        self.buckets[key]["water_level"] += cost
        
        # Calculate time until bucket is empty
        time_to_empty = self.buckets[key]["water_level"] / self.rate
        reset_time = current_time + time_to_empty
        
        return True, {
            "limit": self.capacity,
            "remaining": self.capacity - self.buckets[key]["water_level"],
            "reset": reset_time,
            "retry_after": 0
        }


class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding window rate limiter.
    
    This rate limiter uses a sliding window to limit requests.
    """
    
    def __init__(self, limit: int, window: int):
        """
        Initialize the sliding window rate limiter.
        
        Args:
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
        """
        self.limit = limit
        self.window = window
        self.requests: Dict[str, List[float]] = {}
    
    def check_rate_limit(self, key: str, cost: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Identifier for the client (e.g., IP address, API key)
            cost: Cost of the request (default: 1.0)
            
        Returns:
            Tuple of (allowed, limit_info)
            - allowed: True if the request is allowed, False if it should be rate limited
            - limit_info: Dictionary with rate limit information
        """
        current_time = time.time()
        window_start = current_time - self.window
        
        # Initialize request list if needed
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove expired requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        # Check if limit is exceeded
        if sum(1 for _ in self.requests[key]) >= self.limit:
            # Calculate time until a request expires
            if self.requests[key]:
                oldest_request = min(self.requests[key])
                retry_after = oldest_request + self.window - current_time
            else:
                retry_after = self.window
            
            reset_time = current_time + retry_after
            
            return False, {
                "limit": self.limit,
                "remaining": 0,
                "reset": reset_time,
                "retry_after": retry_after
            }
        
        # Add current request
        for _ in range(int(cost)):
            self.requests[key].append(current_time)
        
        # Calculate remaining requests
        remaining = max(0, self.limit - len(self.requests[key]))
        
        # Calculate reset time (when the oldest request expires)
        if self.requests[key]:
            oldest_request = min(self.requests[key])
            reset_time = oldest_request + self.window
        else:
            reset_time = current_time + self.window
        
        return True, {
            "limit": self.limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": 0
        }


def create_rate_limiter(strategy: str, limit: int, period: int, burst: Optional[int] = None) -> RateLimiter:
    """
    Create a rate limiter based on the specified strategy.
    
    Args:
        strategy: Rate limiting strategy
        limit: Rate limit
        period: Time period in seconds
        burst: Burst capacity (for token bucket)
        
    Returns:
        Rate limiter instance
    """
    if strategy == "fixed":
        return FixedWindowRateLimiter(limit, period)
    elif strategy == "token_bucket":
        rate = limit / period
        burst_size = burst or limit
        return TokenBucketRateLimiter(rate, burst_size)
    elif strategy == "leaky_bucket":
        rate = limit / period
        return LeakyBucketRateLimiter(rate, limit)
    elif strategy == "sliding_window":
        return SlidingWindowRateLimiter(limit, period)
    else:
        raise ValueError(f"Unknown rate limiting strategy: {strategy}")
