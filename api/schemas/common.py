"""
Common schemas for the API server.

This module provides common Pydantic models for API request and response validation.
"""

from typing import Dict, List, Optional, Any, Generic, TypeVar, Union
from enum import Enum
from pydantic import BaseModel, Field

# Define generic type variable
T = TypeVar("T")


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


class SortDirection(str, Enum):
    """Sort direction enum."""

    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Filter operator enum."""

    EQ = "eq"  # Equal
    NEQ = "neq"  # Not equal
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    CONTAINS = "contains"  # Contains (string)
    STARTS_WITH = "startswith"  # Starts with (string)
    ENDS_WITH = "endswith"  # Ends with (string)
    IN = "in"  # In list
    NOT_IN = "notin"  # Not in list


class FilterParam(BaseModel):
    """Filter parameter model."""

    field: str = Field(..., description="Field to filter by")
    operator: FilterOperator = Field(FilterOperator.EQ, description="Filter operator")
    value: Any = Field(..., description="Filter value")


class SortParam(BaseModel):
    """Sort parameter model."""

    field: str = Field(..., description="Field to sort by")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")


class PaginationParams(BaseModel):
    """Pagination parameters model."""

    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(10, description="Number of items per page", ge=1, le=100)


class QueryParams(BaseModel):
    """Query parameters model."""

    pagination: PaginationParams = Field(
        default_factory=PaginationParams, description="Pagination parameters"
    )
    sort: Optional[SortParam] = Field(None, description="Sort parameters")
    filters: List[FilterParam] = Field(
        default_factory=list, description="Filter parameters"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
