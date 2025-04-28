"""
API key routes for the API server.

This module provides route handlers for API key management.
"""

import logging
from typing import List, Optional, Dict, Any

# Try to import FastAPI
try:
    from fastapi import APIRouter, Depends, HTTPException, status, Security
    from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Create dummy classes for type hints
    class APIRouter:
        pass

from ..schemas.api_key import (
    APIKeyCreate, APIKeyResponse, APIKeyCreatedResponse,
    APIKeyUpdate, APIKeyList
)
from ..services.api_key_service import APIKeyService
from ..middleware.auth import get_current_user

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api-keys", tags=["API Keys"])

# Create API key service
api_key_service = APIKeyService()


@router.post("/", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: APIKeyCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new API key.
    
    Args:
        data: API key creation data
        current_user: Current user
        
    Returns:
        Created API key
    """
    # Create API key
    api_key = api_key_service.create_api_key(data, user_id=current_user.get("id"))
    
    # Create response
    response = APIKeyCreatedResponse(
        id=api_key.id,
        prefix=api_key.prefix,
        key=api_key.key,  # Include full key in response (only shown once)
        name=api_key.name,
        description=api_key.description,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        scopes=api_key.scopes,
        is_active=api_key.is_active
    )
    
    return response


@router.get("/", response_model=APIKeyList)
async def get_api_keys(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all API keys for the current user.
    
    Args:
        current_user: Current user
        
    Returns:
        List of API keys
    """
    # Get API keys for the current user
    api_keys = api_key_service.get_api_keys_by_user(current_user.get("id"))
    
    # Create response items
    items = [
        APIKeyResponse(
            id=api_key.id,
            prefix=api_key.prefix,
            name=api_key.name,
            description=api_key.description,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            scopes=api_key.scopes,
            is_active=api_key.is_active
        )
        for api_key in api_keys
    ]
    
    # Create response
    response = APIKeyList(
        items=items,
        total=len(items)
    )
    
    return response


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get an API key by ID.
    
    Args:
        api_key_id: API key ID
        current_user: Current user
        
    Returns:
        API key
    """
    # Get API key
    api_key = api_key_service.get_api_key(api_key_id)
    
    # Check if API key exists
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check if API key belongs to the current user
    if api_key.user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this API key"
        )
    
    # Create response
    response = APIKeyResponse(
        id=api_key.id,
        prefix=api_key.prefix,
        name=api_key.name,
        description=api_key.description,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        scopes=api_key.scopes,
        is_active=api_key.is_active
    )
    
    return response


@router.put("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: str,
    data: APIKeyUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an API key.
    
    Args:
        api_key_id: API key ID
        data: API key update data
        current_user: Current user
        
    Returns:
        Updated API key
    """
    # Get API key
    api_key = api_key_service.get_api_key(api_key_id)
    
    # Check if API key exists
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check if API key belongs to the current user
    if api_key.user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this API key"
        )
    
    # Update API key
    api_key = api_key_service.update_api_key(api_key_id, data)
    
    # Create response
    response = APIKeyResponse(
        id=api_key.id,
        prefix=api_key.prefix,
        name=api_key.name,
        description=api_key.description,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        scopes=api_key.scopes,
        is_active=api_key.is_active
    )
    
    return response


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete an API key.
    
    Args:
        api_key_id: API key ID
        current_user: Current user
    """
    # Get API key
    api_key = api_key_service.get_api_key(api_key_id)
    
    # Check if API key exists
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check if API key belongs to the current user
    if api_key.user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this API key"
        )
    
    # Delete API key
    api_key_service.delete_api_key(api_key_id)


@router.post("/{api_key_id}/revoke", response_model=APIKeyResponse)
async def revoke_api_key(
    api_key_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Revoke an API key.
    
    Args:
        api_key_id: API key ID
        current_user: Current user
        
    Returns:
        Revoked API key
    """
    # Get API key
    api_key = api_key_service.get_api_key(api_key_id)
    
    # Check if API key exists
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check if API key belongs to the current user
    if api_key.user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to revoke this API key"
        )
    
    # Revoke API key
    api_key = api_key_service.revoke_api_key(api_key_id)
    
    # Create response
    response = APIKeyResponse(
        id=api_key.id,
        prefix=api_key.prefix,
        name=api_key.name,
        description=api_key.description,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        scopes=api_key.scopes,
        is_active=api_key.is_active
    )
    
    return response
