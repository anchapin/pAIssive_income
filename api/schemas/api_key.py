"""
API key schemas for the API server.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class APIKeyBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Base schema for API key operations."""
    name: str = Field(..., description="Name of the API key")
    description: Optional[str] = Field(None, description="Description of the API key")
    scopes: List[str] = Field(
    default=["read"], description="Scopes the API key has access to"
    )


    class APIKeyCreate(APIKeyBase):

    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


    class APIKeyUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Schema for updating an API key."""
    name: Optional[str] = Field(None, description="New name of the API key")
    description: Optional[str] = Field(
    None, description="New description of the API key"
    )
    scopes: Optional[List[str]] = Field(
    None, description="New scopes the API key has access to"
    )
    expires_at: Optional[datetime] = Field(None, description="New expiration timestamp")
    is_active: Optional[bool] = Field(None, description="New active status")


    class APIKeyResponse(APIKeyBase):

    id: str = Field(..., description="API key ID")
    key: str = Field(..., description="API key value")
    user_id: Optional[str] = Field(
    None, description="ID of the user who owns the API key"
    )
    is_active: bool = Field(True, description="Whether the API key is active")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")

    class Config:

    orm_mode = True


    class APIKeyList(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Schema for listing API keys."""
    items: List[APIKeyResponse] = Field(..., description="List of API keys")
    total: int = Field(..., description="Total number of API keys")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of API keys per page")
    pages: int = Field(..., description="Total number of pages")
