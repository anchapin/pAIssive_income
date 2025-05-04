"""
Dependencies for API endpoints.

This module provides dependencies for FastAPI routes.
"""


from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from .utils.auth import get_user_from_token, verify_token

# Security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="X-API-Key")


def get_niche_service():
    """
    Get the niche service.

    Returns:
    Niche service
    """
    # In a real application, this would return a service instance
    # For now, we'll return a mock service
    return {
    "get_niches": lambda: [],
    "get_niche": lambda id: {"id": id, "name": "Test Niche"},
    "create_niche": lambda niche: {"id": "new-id", **niche},
    "update_niche": lambda id, niche: {"id": id, **niche},
    "delete_niche": lambda id: {"id": id, "deleted": True},
    }


    def get_market_segment_service():
    """
    Get the market segment service.

    Returns:
    Market segment service
    """
    # In a real application, this would return a service instance
    # For now, we'll return a mock service
    return {
    "get_segments": lambda: [],
    "get_segment": lambda id: {"id": id, "name": "Test Segment"},
    "create_segment": lambda segment: {"id": "new-id", **segment},
    "update_segment": lambda id, segment: {"id": id, **segment},
    "delete_segment": lambda id: {"id": id, "deleted": True},
    }


    def get_problem_service():
    """
    Get the problem service.

    Returns:
    Problem service
    """
    # In a real application, this would return a service instance
    # For now, we'll return a mock service
    return {
    "get_problems": lambda: [],
    "get_problem": lambda id: {"id": id, "name": "Test Problem"},
    "create_problem": lambda problem: {"id": "new-id", **problem},
    "update_problem": lambda id, problem: {"id": id, **problem},
    "delete_problem": lambda id: {"id": id, "deleted": True},
    }


    def get_opportunity_service():
    """
    Get the opportunity service.

    Returns:
    Opportunity service
    """
    # In a real application, this would return a service instance
    # For now, we'll return a mock service
    return {
    "get_opportunities": lambda: [],
    "get_opportunity": lambda id: {"id": id, "name": "Test Opportunity"},
    "create_opportunity": lambda opportunity: {"id": "new-id", **opportunity},
    "update_opportunity": lambda id, opportunity: {"id": id, **opportunity},
    "delete_opportunity": lambda id: {"id": id, "deleted": True},
    }


    def validate_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validate a JWT token.

    Args:
    token: JWT token

    Returns:
    Decoded token payload

    Raises:
    HTTPException: If the token is invalid
    """
    return verify_token(token)


    def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from a JWT token.

    Args:
    token: JWT token

    Returns:
    User data from the token

    Raises:
    HTTPException: If the token is invalid
    """
    return get_user_from_token(token)


    def validate_api_key(api_key: str = Depends(api_key_header)) -> Dict[str, Any]:
    """
    Validate an API key.

    Args:
    api_key: API key

    Returns:
    API key data

    Raises:
    HTTPException: If the API key is invalid
    """
    # In a real application, this would validate the API key against a database
    # For now, we'll just check if it's a non-empty string
    if not api_key:
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid API key",
    headers={"WWW-Authenticate": "ApiKey"},
    )

    # Return mock API key data
    return {
    "id": "api-key-id",
    "name": "Test API Key",
    "scopes": ["read:niche_analysis", "write:niche_analysis"],
    }