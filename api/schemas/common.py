"""
"""
Common schemas for the API server.
Common schemas for the API server.


This module provides common schema models used throughout the API.
This module provides common schema models used throughout the API.
"""
"""


from enum import Enum
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from typing import Any, Dict, Generic, List, Optional, TypeVar


from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field


# Define generic type variable
# Define generic type variable
T = TypeVar("T")
T = TypeVar("T")




class ErrorResponse(BaseModel):
    class ErrorResponse(BaseModel):
    """Error response model."""

    model_config = ConfigDict(protected_namespaces=())

    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    path: Optional[str] = Field(None, description="Path where the error occurred")
    timestamp: Optional[str] = Field(None, description="Timestamp of the error")
    error: Optional[Dict[str, Any]] = Field(
    None,
    description="Error details",
    example={
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": {"field": "email", "reason": "Invalid email format"},
    },
    )


    class SuccessResponse(BaseModel):

    model_config = ConfigDict(protected_namespaces=())

    success: bool = Field(..., description="Success status")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


    class IdResponse(BaseModel):

    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(..., description="Resource ID")
    message: Optional[str] = Field(None, description="Success message")


    class SortDirection(str, Enum):

    ASC = "asc"
    DESC = "desc"


    class FilterOperator(str, Enum):


    EQ = "eq"  # Equal
    EQ = "eq"  # Equal
    NEQ = "neq"  # Not equal
    NEQ = "neq"  # Not equal
    GT = "gt"  # Greater than
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    LTE = "lte"  # Less than or equal
    CONTAINS = "contains"  # Contains (string)
    CONTAINS = "contains"  # Contains (string)
    STARTS_WITH = "startswith"  # Starts with (string)
    STARTS_WITH = "startswith"  # Starts with (string)
    ENDS_WITH = "endswith"  # Ends with (string)
    ENDS_WITH = "endswith"  # Ends with (string)
    IN = "in"  # In list
    IN = "in"  # In list
    NOT_IN = "notin"  # Not in list
    NOT_IN = "notin"  # Not in list




    class FilterParam(BaseModel):
    class FilterParam(BaseModel):


    model_config = ConfigDict(
    model_config = ConfigDict(
    protected_namespaces=(), arbitrary_types_allowed=True, extra="allow"
    protected_namespaces=(), arbitrary_types_allowed=True, extra="allow"
    )
    )


    field: str = Field(..., description="Field to filter by")
    field: str = Field(..., description="Field to filter by")
    operator: FilterOperator = Field(FilterOperator.EQ, description="Filter operator")
    operator: FilterOperator = Field(FilterOperator.EQ, description="Filter operator")
    value: Any = Field(..., description="Filter value")
    value: Any = Field(..., description="Filter value")




    class SortParam(BaseModel):
    class SortParam(BaseModel):


    model_config = ConfigDict(protected_namespaces=())
    model_config = ConfigDict(protected_namespaces=())


    field: str = Field(..., description="Field to sort by")
    field: str = Field(..., description="Field to sort by")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")




    class PaginationParams(BaseModel):
    class PaginationParams(BaseModel):


    model_config = ConfigDict(protected_namespaces=())
    model_config = ConfigDict(protected_namespaces=())


    page: int = Field(1, description="Page number", ge=1)
    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(10, description="Number of items per page", ge=1, le=100)
    page_size: int = Field(10, description="Number of items per page", ge=1, le=100)




    class QueryParams(BaseModel):
    class QueryParams(BaseModel):
    """Query parameters model."""

    model_config = ConfigDict(protected_namespaces=(), arbitrary_types_allowed=True)

    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(10, description="Number of items per page", ge=1, le=100)
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_direction: SortDirection = Field(
    SortDirection.ASC, description="Sort direction"
    )
    filters: List[FilterParam] = Field(
    default_factory=list, description="Filter parameters"
    )


    class PaginatedResponse(BaseModel, Generic[T]):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
