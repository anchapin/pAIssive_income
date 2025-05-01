"""
Query parameter utilities for API endpoints.

This module provides utilities for handling query parameters in API endpoints.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, TypeVar, Generic, Union
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


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
    NIN = "nin"  # Not in list
    CONTAINS = "contains"  # Contains substring
    STARTS_WITH = "starts_with"  # Starts with substring
    ENDS_WITH = "ends_with"  # Ends with substring
    REGEX = "regex"  # Matches regex


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


def apply_sorting(items: List[Dict[str, Any]], params: QueryParams) -> List[Dict[str, Any]]:
    """
    Apply sorting to a list of items.

    Args:
        items: List of items to sort
        params: Query parameters

    Returns:
        Sorted list of items
    """
    if not params.sort_by:
        return items

    # Define a key function that handles None values
    def sort_key(item):
        value = item.get(params.sort_by)
        # None values should be sorted last in ascending order
        # and first in descending order
        if value is None:
            return (1, None) if params.sort_dir == SortDirection.ASC else (0, None)
        return (0, value) if params.sort_dir == SortDirection.ASC else (1, value)

    return sorted(items, key=sort_key)


def apply_filtering(items: List[Dict[str, Any]], params: QueryParams) -> List[Dict[str, Any]]:
    """
    Apply filtering to a list of items.

    Args:
        items: List of items to filter
        params: Query parameters

    Returns:
        Filtered list of items
    """
    if not params.filters:
        return items

    result = items
    for field, value in params.filters.items():
        operator = params.filter_operators.get(field, FilterOperator.EQ)
        result = [item for item in result if _apply_filter(item, field, operator, value)]

    return result


def _apply_filter(item: Dict[str, Any], field: str, operator: FilterOperator, value: Any) -> bool:
    """
    Apply a filter to an item.

    Args:
        item: Item to filter
        field: Field to filter by
        operator: Filter operator
        value: Filter value

    Returns:
        True if the item matches the filter, False otherwise
    """
    if field not in item:
        return False

    item_value = item[field]
    if item_value is None:
        # None values only match equality operators
        return (operator == FilterOperator.EQ and value is None) or (
            operator == FilterOperator.NE and value is not None
        )

    if operator == FilterOperator.EQ:
        return item_value == value
    elif operator == FilterOperator.NE:
        return item_value != value
    elif operator == FilterOperator.GT:
        return item_value > value
    elif operator == FilterOperator.GE:
        return item_value >= value
    elif operator == FilterOperator.LT:
        return item_value < value
    elif operator == FilterOperator.LE:
        return item_value <= value
    elif operator == FilterOperator.IN:
        return item_value in value
    elif operator == FilterOperator.NIN:
        return item_value not in value
    elif operator == FilterOperator.CONTAINS:
        return value in item_value
    elif operator == FilterOperator.STARTS_WITH:
        return item_value.startswith(value)
    elif operator == FilterOperator.ENDS_WITH:
        return item_value.endswith(value)
    elif operator == FilterOperator.REGEX:
        import re
        return bool(re.search(value, item_value))
    else:
        return False
