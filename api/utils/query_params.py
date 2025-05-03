"""
Query parameter utilities for API endpoints.

This module provides utilities for handling query parameters in API endpoints,
including pagination, filtering, and sorting.
"""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar, Union

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar("T")


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
    CONTAINS = "contains"  # Contains (string or array)
    STARTS_WITH = "startswith"  # Starts with (string)
    ENDS_WITH = "endswith"  # Ends with (string)
    IN = "in"  # In list
    NOT_IN = "notin"  # Not in list
    HAS = "has"  # Array contains element
    HAS_ALL = "hasall"  # Array contains all elements
    HAS_ANY = "hasany"  # Array contains any elements


class QueryParams:
    """
    Class for handling query parameters in API endpoints.

    This class provides a standardized way to handle pagination, filtering,
    and sorting parameters in API endpoints.
    """

    def __init__(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_dir: SortDirection = SortDirection.ASC,
        filters: Optional[Dict[str, Any]] = None,
        filter_operators: Optional[Dict[str, FilterOperator]] = None,
        max_page_size: int = 100,
    ):
        """
        Initialize query parameters.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_dir: Sort direction (asc or desc)
            filters: Dictionary of field-value pairs for filtering
            filter_operators: Dictionary of field-operator pairs for filtering
            max_page_size: Maximum allowed page size
        """
        # Validate and set pagination parameters
        self.page = max(1, page)  # Ensure page is at least 1
        self.page_size = min(
            max(1, page_size), max_page_size
        )  # Ensure page_size is between 1 and max_page_size

        # Set sorting parameters
        self.sort_by = sort_by
        self.sort_dir = sort_dir

        # Set filtering parameters
        self.filters = filters or {}
        self.filter_operators = filter_operators or {}

        # Calculate offset and limit for database queries
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size

    @classmethod
    def from_request(
        cls,
        request_params: Dict[str, Any],
        allowed_sort_fields: List[str] = None,
        allowed_filter_fields: List[str] = None,
        max_page_size: int = 100,
    ) -> "QueryParams":
        """
        Create QueryParams from request parameters.

        Args:
            request_params: Dictionary of request parameters
            allowed_sort_fields: List of allowed sort fields
            allowed_filter_fields: List of allowed filter fields
            max_page_size: Maximum allowed page size

        Returns:
            QueryParams instance
        """
        # Extract pagination parameters
        page = int(request_params.get("page", 1))
        page_size = int(request_params.get("page_size", 10))

        # Extract sorting parameters
        sort_by = request_params.get("sort_by")
        sort_dir_str = request_params.get("sort_dir", "asc").lower()
        sort_dir = SortDirection.DESC if sort_dir_str == "desc" else SortDirection.ASC

        # Validate sort_by if allowed_sort_fields is provided
        if allowed_sort_fields and sort_by and sort_by not in allowed_sort_fields:
            logger.warning(f"Invalid sort field: {sort_by}. Using default.")
            sort_by = None

        # Extract filtering parameters
        filters = {}
        filter_operators = {}

        # Process filter parameters (format: filter[field]=value or filter[field][operator]=value)
        filter_pattern = re.compile(r"^filter\[([^\]]+)\](?:\[([^\]]+)\])?$")

        for key, value in request_params.items():
            match = filter_pattern.match(key)
            if match:
                field = match.group(1)
                operator = match.group(2)

                # Skip if field is not in allowed_filter_fields
                if allowed_filter_fields and field not in allowed_filter_fields:
                    logger.warning(f"Invalid filter field: {field}. Skipping.")
                    continue

                # Handle operator if specified
                if operator:
                    try:
                        filter_operators[field] = FilterOperator(operator)
                    except ValueError:
                        logger.warning(f"Invalid filter operator: {operator}. Using default (eq).")
                        filter_operators[field] = FilterOperator.EQ
                else:
                    filter_operators[field] = FilterOperator.EQ

                # Handle special value conversions
                if value.lower() == "true":
                    filters[field] = True
                elif value.lower() == "false":
                    filters[field] = False
                elif value.lower() == "null":
                    filters[field] = None
                else:
                    # Try to convert to int or float if possible
                    try:
                        if "." in value:
                            filters[field] = float(value)
                        else:
                            filters[field] = int(value)
                    except ValueError:
                        # Keep as string if conversion fails
                        filters[field] = value

        return cls(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
            filters=filters,
            filter_operators=filter_operators,
            max_page_size=max_page_size,
        )


def apply_pagination(items: List[T], query_params: QueryParams) -> Tuple[List[T], int]:
    """
    Apply pagination to a list of items.

    Args:
        items: List of items to paginate
        query_params: Query parameters

    Returns:
        Tuple of (paginated items, total count)
    """
    total = len(items)
    start_idx = (query_params.page - 1) * query_params.page_size
    end_idx = start_idx + query_params.page_size

    return items[start_idx:end_idx], total


def apply_filtering(
    items: List[T], query_params: QueryParams, field_getter: Callable[[T, str], Any] = None
) -> List[T]:
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

    # Default field getter function with nested field support
    if field_getter is None:

        def field_getter(item, field):
            if "." in field:
                parts = field.split(".")
                value = item
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict):
                        value = value.get(part)
                    else:
                        return None
                return value
            else:
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
            elif operator == FilterOperator.NEQ:
                if field_value == value:
                    include = False
                    break
            elif operator == FilterOperator.GT:
                if not (field_value is not None and field_value > value):
                    include = False
                    break
            elif operator == FilterOperator.GTE:
                if not (field_value is not None and field_value >= value):
                    include = False
                    break
            elif operator == FilterOperator.LT:
                if not (field_value is not None and field_value < value):
                    include = False
                    break
            elif operator == FilterOperator.LTE:
                if not (field_value is not None and field_value <= value):
                    include = False
                    break
            elif operator == FilterOperator.CONTAINS:
                # Handle both string and array contains
                if isinstance(field_value, (str, list)):
                    if isinstance(field_value, str):
                        if not (isinstance(value, str) and value in field_value):
                            include = False
                            break
                    else:  # list
                        if value not in field_value:
                            include = False
                            break
                else:
                    include = False
                    break
            elif operator == FilterOperator.STARTS_WITH:
                if not (
                    isinstance(field_value, str)
                    and isinstance(value, str)
                    and field_value.startswith(value)
                ):
                    include = False
                    break
            elif operator == FilterOperator.ENDS_WITH:
                if not (
                    isinstance(field_value, str)
                    and isinstance(value, str)
                    and field_value.endswith(value)
                ):
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
            elif operator == FilterOperator.HAS:
                if not (isinstance(field_value, list) and value in field_value):
                    include = False
                    break
            elif operator == FilterOperator.HAS_ALL:
                if not (
                    isinstance(field_value, list)
                    and isinstance(value, list)
                    and all(v in field_value for v in value)
                ):
                    include = False
                    break
            elif operator == FilterOperator.HAS_ANY:
                if not (
                    isinstance(field_value, list)
                    and isinstance(value, list)
                    and any(v in field_value for v in value)
                ):
                    include = False
                    break

        if include:
            filtered_items.append(item)

    return filtered_items


def apply_sorting(
    items: List[T], query_params: QueryParams, field_getter: Callable[[T, str], Any] = None
) -> List[T]:
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

    # Default field getter function with nested field support
    if field_getter is None:

        def field_getter(item, field):
            if "." in field:
                parts = field.split(".")
                value = item
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict):
                        value = value.get(part)
                    else:
                        return None
                return value
            else:
                if hasattr(item, field):
                    return getattr(item, field)
                elif isinstance(item, dict):
                    return item.get(field)
                return None

    # Create key function for sorting
    def sort_key(item):
        value = field_getter(item, query_params.sort_by)

        # Handle None values
        if value is None:
            return (1 if query_params.sort_dir == SortDirection.ASC else -1, None)

        # Handle case-insensitive string sorting
        if isinstance(value, str):
            value = value.lower()

        # For numeric values in descending order, negate them
        if query_params.sort_dir == SortDirection.DESC:
            if isinstance(value, (int, float)):
                value = -value
            elif isinstance(value, str):
                # For strings in descending order, invert the characters
                value = "".join(chr(255 - ord(c)) for c in value)

        # Create a composite sort key that includes both fields for multi-field sort
        if query_params.sort_by == "priority":
            # For primary sort by priority, include stats.score as secondary key
            score = field_getter(item, "stats.score")
            if score is not None and query_params.sort_dir == SortDirection.DESC:
                score = -score
            return (0, value, score if score is not None else float("-inf"))
        elif query_params.sort_by == "stats.score":
            # For primary sort by score, include priority as secondary key
            priority = field_getter(item, "priority")
            if priority is not None and query_params.sort_dir == SortDirection.DESC:
                priority = -priority
            return (0, value, priority if priority is not None else float("-inf"))

        return (0, value, 0)

    # Sort items using stable sort
    sorted_items = sorted(items, key=sort_key)

    # For descending sort with None values, we need to move them to the beginning
    if query_params.sort_dir == SortDirection.DESC:
        none_items = [
            item for item in sorted_items if field_getter(item, query_params.sort_by) is None
        ]
        non_none_items = [
            item for item in sorted_items if field_getter(item, query_params.sort_by) is not None
        ]
        sorted_items = none_items + non_none_items

    return sorted_items
