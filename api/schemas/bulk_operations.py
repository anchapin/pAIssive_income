"""
Bulk operation schemas for the API server.

This module provides Pydantic models for bulk operation API request and response validation.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Define generic type variable for bulk operations
T = TypeVar("T")
R = TypeVar("R")


class BulkOperationStats(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Statistics for a bulk operation."""

    total_items: int = Field(..., description="Total number of items in the request")
    successful_items: int = Field(
        ..., description="Number of successfully processed items"
    )
    failed_items: int = Field(..., description="Number of failed items")
    processing_time_ms: float = Field(
        ..., description="Processing time in milliseconds"
    )


class BulkOperationError(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Error information for a failed item in a bulk operation."""

    index: int = Field(
        ..., description="Index of the failed item in the original request"
    )
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    item_id: Optional[str] = Field(None, description="ID of the item if available")


class BulkResponse(BaseModel, Generic[R]):
    """Generic response model for bulk operations."""

    results: List[R] = Field(..., description="List of successful results")
    errors: List[BulkOperationError] = Field(..., description="List of errors")
    stats: BulkOperationStats = Field(..., description="Operation statistics")
    operation_id: str = Field(..., description="Unique ID for the bulk operation")


class BulkCreateRequest(BaseModel, Generic[T]):
    """Generic request model for bulk create operations."""

    items: List[T] = Field(..., description="List of items to create")
    options: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters for the operation"
    )


class BulkCreateResponse(BaseModel, Generic[R]):
    """Generic response model for bulk create operations."""

    items: List[R] = Field(..., description="List of created items")
    errors: List[BulkOperationError] = Field(..., description="List of errors")
    stats: BulkOperationStats = Field(..., description="Operation statistics")
    operation_id: str = Field(..., description="Unique ID for the bulk operation")


class BulkUpdateRequest(BaseModel, Generic[T]):
    """Generic request model for bulk update operations."""

    items: List[Dict[str, Any]] = Field(
        ..., description="List of items to update with IDs"
    )
    options: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters for the operation"
    )


class BulkUpdateResponse(BaseModel, Generic[R]):
    """Generic response model for bulk update operations."""

    items: List[R] = Field(..., description="List of updated items")
    errors: List[BulkOperationError] = Field(..., description="List of errors")
    stats: BulkOperationStats = Field(..., description="Operation statistics")
    operation_id: str = Field(..., description="Unique ID for the bulk operation")


class BulkDeleteRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Request model for bulk delete operations."""

    ids: List[str] = Field(..., description="List of IDs to delete")
    options: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters for the operation"
    )


class BulkDeleteResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Response model for bulk delete operations."""

    deleted_ids: List[str] = Field(..., description="List of successfully deleted IDs")
    errors: List[BulkOperationError] = Field(..., description="List of errors")
    stats: BulkOperationStats = Field(..., description="Operation statistics")
    operation_id: str = Field(..., description="Unique ID for the bulk operation")
