"""
JWT authentication utilities for service-to-service communication.

This module provides utilities for generating and validating JWT tokens
for secure service-to-service communication in the microservices architecture.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

import jwt
from pydantic import BaseModel, ConfigDict, Field

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default token expiration time (15 minutes)
DEFAULT_TOKEN_EXPIRATION = 15 * 60  # seconds

# JWT algorithm
JWT_ALGORITHM = "HS256"


class ServiceTokenError(Exception):
    """Exception raised for errors in the service token authentication."""

    pass


class ServiceTokenPayload(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Payload for service-to-service JWT tokens."""

    # Service that issued the token
    iss: str = Field(..., description="Issuer (service name)")

    # Service that the token is intended for
    aud: str = Field(..., description="Audience (target service name)")

    # Unique token ID
    jti: str = Field(..., description="JWT ID (unique identifier)")

    # Token expiration time (Unix timestamp)
    exp: int = Field(..., description="Expiration time (Unix timestamp)")

    # Token issued at time (Unix timestamp)
    iat: int = Field(..., description="Issued at time (Unix timestamp)")

    # Service-specific claims
    claims: Dict[str, Any] = Field(
        default_factory=dict, description="Service-specific claims"
    )


def get_service_secret_key() -> str:
    """
    Get the secret key for JWT token signing/validation.

    The secret key is read from the SERVICE_AUTH_SECRET environment variable.
    If not set, a default development key is used (not secure for production).

    Returns:
        str: The secret key
    """
    secret_key = os.environ.get("SERVICE_AUTH_SECRET")

    if not secret_key:
        # Use a default key for development (not secure for production)
        default_key = "pAIssive_income_dev_key_not_secure_for_production"
        logger.warning(
            "SERVICE_AUTH_SECRET environment variable not set. "
            "Using default development key. This is not secure for production."
        )
        return default_key

    return secret_key


def create_service_token(
    issuer: str,
    audience: str,
    token_id: Optional[str] = None,
    expiration: Optional[int] = None,
    claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT token for service-to-service authentication.

    Args:
        issuer: Name of the service issuing the token
        audience: Name of the service the token is intended for
        token_id: Unique token ID (defaults to current timestamp)
        expiration: Token expiration time in seconds (defaults to 15 minutes)
        claims: Additional service-specific claims

    Returns:
        str: The JWT token

    Raises:
        ServiceTokenError: If token creation fails
    """
    try:
        # Get current time
        current_time = int(time.time())

        # Set default token ID if not provided
        if token_id is None:
            token_id = f"{issuer}-{current_time}-{os.urandom(4).hex()}"

        # Set default expiration if not provided
        if expiration is None:
            expiration = current_time + DEFAULT_TOKEN_EXPIRATION
        else:
            expiration = current_time + expiration

        # Create token payload
        payload = ServiceTokenPayload(
            iss=issuer,
            aud=audience,
            jti=token_id,
            exp=expiration,
            iat=current_time,
            claims=claims or {},
        )

        # Convert payload to dict
        payload_dict = payload.dict()

        # Get secret key
        secret_key = get_service_secret_key()

        # Create JWT token
        token = jwt.encode(
            payload=payload_dict, key=secret_key, algorithm=JWT_ALGORITHM
        )

        return token

    except Exception as e:
        logger.error(f"Error creating service token: {str(e)}")
        raise ServiceTokenError(f"Failed to create service token: {str(e)}")


def validate_service_token(
    token: str, audience: str, verify_expiration: bool = True
) -> ServiceTokenPayload:
    """
    Validate a JWT token for service-to-service authentication.

    Args:
        token: The JWT token to validate
        audience: Expected audience (service name)
        verify_expiration: Whether to verify token expiration

    Returns:
        ServiceTokenPayload: The validated token payload

    Raises:
        ServiceTokenError: If token validation fails
    """
    try:
        # Get secret key
        secret_key = get_service_secret_key()

        # Decode and validate the token
        payload = jwt.decode(
            jwt=token,
            key=secret_key,
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": verify_expiration,
                "verify_aud": True,
                "require": ["exp", "iat", "iss", "aud", "jti"],
            },
            audience=audience,
        )

        # Create and return the payload model
        return ServiceTokenPayload(**payload)

    except jwt.ExpiredSignatureError:
        logger.warning("Service token has expired")
        raise ServiceTokenError("Service token has expired")

    except jwt.InvalidAudienceError:
        logger.warning(f"Service token has invalid audience (expected: {audience})")
        raise ServiceTokenError(
            f"Service token has invalid audience (expected: {audience})"
        )

    except jwt.PyJWTError as e:
        logger.warning(f"Invalid service token: {str(e)}")
        raise ServiceTokenError(f"Invalid service token: {str(e)}")

    except Exception as e:
        logger.error(f"Error validating service token: {str(e)}")
        raise ServiceTokenError(f"Failed to validate service token: {str(e)}")
