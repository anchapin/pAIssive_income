"""
API key schemas for the API server.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class APIKeyCreate(BaseModel):
    """Request model for creating an API key."""
    name: str = Field(..., description="Name of the API key")
    description: Optional[str] = Field(None, description="Description of the API key")
    expires_at: Optional[datetime] = Field(None, description="Expiration date of the API key")
    scopes: Optional[List[str]] = Field(None, description="List of permission scopes")

class APIKeyResponse(BaseModel):
    """Response model for API key operations."""
    id: str = Field(..., description="API key ID")
    prefix: str = Field(..., description="API key prefix")
    name: str = Field(..., description="Name of the API key")
    description: Optional[str] = Field(None, description="Description of the API key")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    scopes: List[str] = Field(default_factory=list, description="List of permission scopes")
    is_active: bool = Field(True, description="Whether the API key is active")

class APIKeyCreatedResponse(APIKeyResponse):
    """Response model for API key creation, including the full key."""
    key: str = Field(..., description="The full API key (only shown once)")

class APIKeyUpdate(BaseModel):
    """Request model for updating an API key."""
    name: Optional[str] = Field(None, description="New name for the API key")
    description: Optional[str] = Field(None, description="New description for the API key")
    expires_at: Optional[datetime] = Field(None, description="New expiration timestamp")
    scopes: Optional[List[str]] = Field(None, description="New list of permission scopes")
    is_active: Optional[bool] = Field(None, description="New active status")

class APIKeyList(BaseModel):
    """Response model for listing API keys."""
    items: List[APIKeyResponse] = Field(..., description="List of API keys")
    total: int = Field(..., description="Total number of keys")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of keys per page")
    pages: int = Field(..., description="Total number of pages")
