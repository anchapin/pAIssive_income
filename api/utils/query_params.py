"""
Query parameter utilities for API endpoints.

This module provides utilities for handling query parameters in API endpoints.
"""
from typing import Dict, Any, List, Optional, TypeVar, Generic, Union, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


T = TypeVar('T')

class SortDirection(str, Enum):
    """Sort direction for query parameters."""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Filter operator for query parameters."""
    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GE = "ge"  # Greater than or equal
    LT = "lt"  # Less than
    LE = "le"  # Less than or equal
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list
    CONTAINS = "contains"  # Contains substring
    STARTS_WITH = "starts_with"  # Starts with substring
    ENDS_WITH = "ends_with"  # Ends with substring
    REGEX = "regex"  # Matches regex pattern


class FilterParam(BaseModel):
    """Filter parameter for query parameters."""
    field: str = Field(..., description="Field to filter by")
    operator: FilterOperator = Field(FilterOperator.EQ, description="Filter operator")
    value: Any = Field(..., description="Filter value")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class QueryParams(BaseModel):
    """Query parameters for API endpoints."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_dir: SortDirection = Field(SortDirection.ASC, description="Sort direction")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filters")
    filter_operators: Dict[str, FilterOperator] = Field(
        default_factory=dict, description="Filter operators"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response for API endpoints."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(arbitrary_types_allowed=True)


def apply_pagination(items: List[Any], params: QueryParams) -> Dict[str, Any]:
    """
    Apply pagination to a list of items.

    Args:
        items: List of items to paginate
        params: Query parameters

    Returns:
        Paginated response
    """
    total = len(items)
    start = (params.page - 1) * params.page_size
    end = start + params.page_size
    pages = (total + params.page_size - 1) // params.page_size

    return {
        "items": items[start:end],
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "pages": pages,
    }


def apply_filtering(items: List[T], query_params: QueryParams,
                  field_getter: Callable[[T, str], Any] = None) -> List[T]:
    """
    Apply filtering to a list of items.

    Args:
        items: List of items to filter
        query_params: Query parameters
        field_getter: Function to get field value from item (defaults to getattr or dict access)

    Returns:
        Filtered list of items
    """
    if not query_params.filters:
        return items

    # Default field getter function
    if field_getter is None:
        def field_getter(item, field):
            if hasattr(item, field):
                return getattr(item, field)
            elif isinstance(item, dict):
                return item.get(field)
            return None

    filtered_items = []

    for item in items:
        include = True

        for field, value in query_params.filters.items():
            operator = query_params.filter_operators.get(field, FilterOperator.EQ)
            field_value = field_getter(item, field)

            # Apply filter based on operator
            if operator == FilterOperator.EQ:
                if field_value != value:
                    include = False
                    break
            elif operator == FilterOperator.NE:
                if field_value == value:
                    include = False
                    break
            elif operator == FilterOperator.GT:
                if not (field_value is not None and field_value > value):
                    include = False
                    break
            elif operator == FilterOperator.GE:
                if not (field_value is not None and field_value >= value):
                    include = False
                    break
            elif operator == FilterOperator.LT:
                if not (field_value is not None and field_value < value):
                    include = False
                    break
            elif operator == FilterOperator.LE:
                if not (field_value is not None and field_value <= value):
                    include = False
                    break
            elif operator == FilterOperator.CONTAINS:
                if not (isinstance(field_value, str) and isinstance(value, str) 
                       and value in field_value):
                    include = False
                    break
            elif operator == FilterOperator.STARTS_WITH:
                if not (isinstance(field_value, str) and isinstance(value, str) 
                       and field_value.startswith(value)):
                    include = False
                    break
            elif operator == FilterOperator.ENDS_WITH:
                if not (isinstance(field_value, str) and isinstance(value, str) 
                       and field_value.endswith(value)):
                    include = False
                    break
            elif operator == FilterOperator.IN:
                if not (isinstance(value, list) and field_value in value):
                    include = False
                    break
            elif operator == FilterOperator.NOT_IN:
                if not (isinstance(value, list) and field_value not in value):
                    include = False
                    break
            elif operator == FilterOperator.REGEX:
                import re
                if not (isinstance(field_value, str) and isinstance(value, str) 
                       and bool(re.search(value, field_value))):
                    include = False
                    break

        if include:
            filtered_items.append(item)

    return filtered_items


def apply_sorting(items: List[T], query_params: QueryParams,
                field_getter: Callable[[T, str], Any] = None) -> List[T]:
    """
    Apply sorting to a list of items.

    Args:
        items: List of items to sort
        query_params: Query parameters
        field_getter: Function to get field value from item (defaults to getattr or dict access)

    Returns:
        Sorted list of items
    """
    if not query_params.sort_by:
        return items

    # Default field getter function
    if field_getter is None:
        def field_getter(item, field):
            if hasattr(item, field):
                return getattr(item, field)
            elif isinstance(item, dict):
                return item.get(field)
            return None

    # Create key function for sorting that handles None values
    def sort_key(item):
        value = field_getter(item, query_params.sort_by)
        if value is None:
            # Sort None values last in ascending order, first in descending
            return (1, None) if query_params.sort_dir == SortDirection.ASC else (0, None)
        return (0, value) if query_params.sort_dir == SortDirection.ASC else (1, value)

    # Sort items
    return sorted(items, key=sort_key)
