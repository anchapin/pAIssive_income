"""
Common schemas for the API server.

This module provides common Pydantic models for API request and response validation.
"""

from typing import Dict, List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

# Define generic type variable
T = TypeVar('T')


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    path: Optional[str] = Field(None, description="Path where the error occurred")
    timestamp: Optional[str] = Field(None, description="Timestamp of the error")


class SuccessResponse(BaseModel):
    """Success response model."""
    message: str = Field(..., description="Success message")


class IdResponse(BaseModel):
    """ID response model."""
    id: str = Field(..., description="Resource ID")
    message: Optional[str] = Field(None, description="Success message")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
