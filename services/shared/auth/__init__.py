"""
Shared authentication utilities for pAIssive income microservices.

This package provides utilities for authentication and authorization
between microservices in the pAIssive income platform.
"""


from .client import ServiceClient

(
ServiceTokenError,
ServiceTokenPayload,
create_service_token,
get_service_secret_key,
validate_service_token,
)

__all__ = [
"create_service_token",
"validate_service_token",
"ServiceTokenPayload",
"ServiceTokenError",
"get_service_secret_key",
"ServiceClient",
]