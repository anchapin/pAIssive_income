"""
Common error classes used throughout the application.

This module defines base exception classes that should be used
instead of generic exceptions to provide more specific error handling.
"""


class BaseError(Exception):
    """Base error class for all application errors."""

    def __init__(self, message="An error occurred", *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)


class NicheAnalysisError(BaseError):
    """Error raised during niche analysis operations."""

    def __init__(self, message="An error occurred during niche analysis", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ModelError(BaseError):
    """Error raised during AI model operations."""

    def __init__(self, message="An error occurred with the AI model", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ValidationError(BaseError):
    """Error raised during data validation."""

    def __init__(self, message="Validation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class AuthenticationError(BaseError):
    """Error raised during authentication."""

    def __init__(self, message="Authentication error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class AuthorizationError(BaseError):
    """Error raised during authorization."""

    def __init__(self, message="Authorization error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ConfigurationError(BaseError):
    """Error raised during configuration."""

    def __init__(self, message="Configuration error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class DatabaseError(BaseError):
    """Error raised during database operations."""

    def __init__(self, message="Database error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class APIError(BaseError):
    """Error raised during API operations."""

    def __init__(self, message="API error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class NetworkError(BaseError):
    """Error raised during network operations."""

    def __init__(self, message="Network error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
