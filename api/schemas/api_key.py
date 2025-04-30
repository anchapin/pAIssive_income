"""
API key schemas for the API server.

This module provides Pydantic models for API key management.
"""

import uuid
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator


class APIKeyCreate(BaseModel):
    """
    Schema for creating a new API key.
    """

    name: str = Field(..., description="Name of the API key")
    description: Optional[str] = Field(None, description="Description of the API key")
    expires_at: Optional[datetime] = Field(
        None, description="Expiration date of the API key"
    )
    scopes: List[str] = Field(
        default_factory=list, description="Scopes (permissions) for the API key"
    )

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "name": "My API Key",
                "description": "API key for testing",
                "expires_at": "2023-12-31T23:59:59",
                "scopes": ["read:niche_analysis", "write:niche_analysis"],
            }
        }


class APIKeyResponse(BaseModel):
    """
    Schema for API key response.
    """

    id: str = Field(..., description="Unique identifier for the API key")
    prefix: str = Field(..., description="Prefix of the API key (first 8 characters)")
    name: str = Field(..., description="Name of the API key")
    description: Optional[str] = Field(None, description="Description of the API key")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(
        None, description="Expiration date of the API key"
    )
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    scopes: List[str] = Field(
        default_factory=list, description="Scopes (permissions) for the API key"
    )
    is_active: bool = Field(..., description="Whether the API key is active")

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "id": "01234567-89ab-cdef-0123-456789abcdef",
                "prefix": "sk_12345678",
                "name": "My API Key",
                "description": "API key for testing",
                "created_at": "2023-01-01T00:00:00",
                "expires_at": "2023-12-31T23:59:59",
                "last_used_at": "2023-01-02T12:34:56",
                "scopes": ["read:niche_analysis", "write:niche_analysis"],
                "is_active": True,
            }
        }


class APIKeyCreatedResponse(APIKeyResponse):
    """
    Schema for API key creation response, including the full key.
    """

    key: str = Field(..., description="Full API key (only shown once)")

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "id": "01234567-89ab-cdef-0123-456789abcdef",
                "prefix": "sk_12345678",
                "key": "sk_12345678abcdefghijklmnopqrstuvwxyz",
                "name": "My API Key",
                "description": "API key for testing",
                "created_at": "2023-01-01T00:00:00",
                "expires_at": "2023-12-31T23:59:59",
                "last_used_at": None,
                "scopes": ["read:niche_analysis", "write:niche_analysis"],
                "is_active": True,
            }
        }


class APIKeyUpdate(BaseModel):
    """
    Schema for updating an API key.
    """

    name: Optional[str] = Field(None, description="Name of the API key")
    description: Optional[str] = Field(None, description="Description of the API key")
    expires_at: Optional[datetime] = Field(
        None, description="Expiration date of the API key"
    )
    scopes: Optional[List[str]] = Field(
        None, description="Scopes (permissions) for the API key"
    )
    is_active: Optional[bool] = Field(None, description="Whether the API key is active")

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "name": "Updated API Key",
                "description": "Updated description",
                "expires_at": "2024-12-31T23:59:59",
                "scopes": [
                    "read:niche_analysis",
                    "write:niche_analysis",
                    "read:monetization",
                ],
                "is_active": True,
            }
        }


class APIKeyList(BaseModel):
    """
    Schema for a list of API keys.
    """

    items: List[APIKeyResponse] = Field(..., description="List of API keys")
    total: int = Field(..., description="Total number of API keys")

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "01234567-89ab-cdef-0123-456789abcdef",
                        "prefix": "sk_12345678",
                        "name": "My API Key",
                        "description": "API key for testing",
                        "created_at": "2023-01-01T00:00:00",
                        "expires_at": "2023-12-31T23:59:59",
                        "last_used_at": "2023-01-02T12:34:56",
                        "scopes": ["read:niche_analysis", "write:niche_analysis"],
                        "is_active": True,
                    }
                ],
                "total": 1,
            }
        }
