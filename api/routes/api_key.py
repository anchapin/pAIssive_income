"""
API key routes for the API server.

This module provides route handlers for API key management.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status

from ..middleware.auth import get_current_user
from ..schemas.api_key import (
    APIKeyCreate,
    APIKeyCreatedResponse,
    APIKeyList,
    APIKeyResponse,
    APIKeyUpdate,
)
from ..services.api_key_service import APIKeyService

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix=" / api - keys", tags=["API Keys"])

# Create API key service
api_key_service = APIKeyService()


@router.post(" / ", response_model=APIKeyCreatedResponse, 
    status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: APIKeyCreate = Body(...), current_user: Dict[str, 
        Any] = Depends(get_current_user)
):
    """Create a new API key."""
    try:
        # Create API key
        api_key = api_key_service.create_api_key(data, user_id=current_user.get("id"))

        # Create response
        return APIKeyCreatedResponse(
            id=api_key.id,
            prefix=api_key.prefix,
            key=api_key.key,
            name=api_key.name,
            description=api_key.description,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            scopes=api_key.scopes,
            is_active=api_key.is_active,
        )
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(" / ", response_model=APIKeyList)
async def list_api_keys(
    current_user: Dict[str, Any] = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """List all API keys for the current user."""
    try:
        api_keys = api_key_service.list_api_keys(
            user_id=current_user.get("id"), page=page, page_size=page_size
        )
        return api_keys
    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: str = Path(...), current_user: Dict[str, 
        Any] = Depends(get_current_user)
):
    """Get a specific API key."""
    try:
        api_key = api_key_service.get_api_key(api_key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        if api_key.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, 
                detail="Not authorized to access this API key")

        return APIKeyResponse(
            id=api_key.id,
            prefix=api_key.prefix,
            name=api_key.name,
            description=api_key.description,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            scopes=api_key.scopes,
            is_active=api_key.is_active,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: str = Path(...),
    data: APIKeyUpdate = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update an API key."""
    try:
        # Get API key
        api_key = api_key_service.get_api_key(api_key_id)

        # Check if API key exists
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Check if API key belongs to the current user
        if api_key.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, 
                detail="Not authorized to update this API key")

        # Update API key
        updated_key = api_key_service.update_api_key(api_key_id, data)

        return APIKeyResponse(
            id=updated_key.id,
            prefix=updated_key.prefix,
            name=updated_key.name,
            description=updated_key.description,
            created_at=updated_key.created_at,
            expires_at=updated_key.expires_at,
            last_used_at=updated_key.last_used_at,
            scopes=updated_key.scopes,
            is_active=updated_key.is_active,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: str = Path(...), current_user: Dict[str, 
        Any] = Depends(get_current_user)
):
    """Delete an API key."""
    try:
        # Get API key
        api_key = api_key_service.get_api_key(api_key_id)

        # Check if API key exists
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Check if API key belongs to the current user
        if api_key.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, 
                detail="Not authorized to delete this API key")

        # Delete API key
        if not api_key_service.delete_api_key(api_key_id):
            raise HTTPException(status_code=500, detail="Failed to delete API key")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{api_key_id}/revoke", response_model=APIKeyResponse)
async def revoke_api_key(
    api_key_id: str = Path(...), current_user: Dict[str, 
        Any] = Depends(get_current_user)
):
    """Revoke an API key."""
    try:
        # Get API key
        api_key = api_key_service.get_api_key(api_key_id)

        # Check if API key exists
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Check if API key belongs to the current user
        if api_key.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, 
                detail="Not authorized to revoke this API key")

        # Revoke API key
        revoked_key = api_key_service.revoke_api_key(api_key_id)

        return APIKeyResponse(
            id=revoked_key.id,
            prefix=revoked_key.prefix,
            name=revoked_key.name,
            description=revoked_key.description,
            created_at=revoked_key.created_at,
            expires_at=revoked_key.expires_at,
            last_used_at=revoked_key.last_used_at,
            scopes=revoked_key.scopes,
            is_active=revoked_key.is_active,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{api_key_id}/regenerate", response_model=APIKeyCreatedResponse)
async def regenerate_api_key(
    api_key_id: str = Path(...), current_user: Dict[str, 
        Any] = Depends(get_current_user)
):
    """Regenerate an API key."""
    try:
        # Get API key
        api_key = api_key_service.get_api_key(api_key_id)

        # Check if API key exists
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Check if API key belongs to the current user
        if api_key.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, 
                detail="Not authorized to regenerate this API key")

        # Regenerate API key
        regenerated_key = api_key_service.regenerate_api_key(api_key_id)

        return APIKeyCreatedResponse(
            id=regenerated_key.id,
            prefix=regenerated_key.prefix,
            key=regenerated_key.key,
            name=regenerated_key.name,
            description=regenerated_key.description,
            created_at=regenerated_key.created_at,
            expires_at=regenerated_key.expires_at,
            last_used_at=regenerated_key.last_used_at,
            scopes=regenerated_key.scopes,
            is_active=regenerated_key.is_active,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
