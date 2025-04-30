"""
Stub implementation for the services.errors module.
Provides minimal functionality for error handling.
"""

class ServiceError(Exception):
    """
    Base exception for service-related errors.
    """
    pass

class AuthenticationError(ServiceError):
    """
    Exception raised for authentication failures.
    """
    pass

class RateLimitExceededError(ServiceError):
    """
    Exception raised when a rate limit is exceeded.
    """
    pass

class RoutingError(ServiceError):
    """
    Exception raised for routing-related errors.
    """
    pass

class CircuitBreakerError(ServiceError):
    """
    Exception raised when a circuit breaker error occurs.
    """
    pass

class ServiceUnavailableError(ServiceError):
    """
    Exception raised when a service is unavailable.
    """
    pass
