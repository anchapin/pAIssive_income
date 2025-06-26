"""errors - Module for api.errors."""

# Standard library imports

# Third-party imports

# Local imports


class APIError(Exception):
    """Base exception for API-related errors."""


class ValidationError(Exception):
    """Exception for validation errors."""
