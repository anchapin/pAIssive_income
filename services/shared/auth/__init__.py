"""
"""
Shared authentication utilities for pAIssive income microservices.
Shared authentication utilities for pAIssive income microservices.


This package provides utilities for authentication and authorization
This package provides utilities for authentication and authorization
between microservices in the pAIssive income platform.
between microservices in the pAIssive income platform.
"""
"""




from .client import ServiceClient
from .client import ServiceClient


(
(
ServiceTokenError,
ServiceTokenError,
ServiceTokenPayload,
ServiceTokenPayload,
create_service_token,
create_service_token,
get_service_secret_key,
get_service_secret_key,
validate_service_token,
validate_service_token,
)
)


__all__ = [
__all__ = [
"create_service_token",
"create_service_token",
"validate_service_token",
"validate_service_token",
"ServiceTokenPayload",
"ServiceTokenPayload",
"ServiceTokenError",
"ServiceTokenError",
"get_service_secret_key",
"get_service_secret_key",
"ServiceClient",
"ServiceClient",
]
]