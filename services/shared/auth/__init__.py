"""
Shared authentication utilities for pAIssive income microservices.

This package provides utilities for authentication and authorization
between microservices in the pAIssive income platform.
"""

from .jwt_auth import (
    create_service_token,
    validate_service_token,
    ServiceTokenPayload,
    ServiceTokenError,
    get_service_secret_key,
)
from .client import ServiceClient

__all__ = [
    "create_service_token",
    "validate_service_token",
    "ServiceTokenPayload",
    "ServiceTokenError",
    "get_service_secret_key",
    "ServiceClient",
]
