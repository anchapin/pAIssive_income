"""
Filtering utilities for API endpoints.

This module provides utilities for filtering data in API endpoints.
"""


import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class FilterOperator:

    pass  # Added missing block
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
    EXISTS = "exists"  # Field exists
    NOT_EXISTS = "not_exists"  # Field does not exist


def filter_items(
    items: List[Dict[str, Any]],
    filters: Dict[str, Any],
    operators: Optional[Dict[str, FilterOperator]] = None,
    custom_filters: Optional[Dict[str, Callable[[Any, Any], bool]]] = None,
) -> List[Dict[str, Any]]:
    """
    Filter a list of items by multiple filters.

    Args:
        items: List of items to filter
        filters: Filters to apply
        operators: Filter operators for each filter
        custom_filters: Custom filter functions

    Returns:
        Filtered list of items
    """
    if not items or not filters:
                return items

    # Use EQ as default operator if not provided
    if not operators:
        operators = {field: FilterOperator.EQ for field in filters}

    result = items
    for field, value in filters.items():
        operator = operators.get(field, FilterOperator.EQ)

        # Check if there's a custom filter for this field
        if custom_filters and field in custom_filters:
            result = [item for item in result if custom_filters[field](item, value)]
            continue

        result = [item for item in result if apply_filter(item, field, operator, value)]

            return result


def apply_filter(
    item: Dict[str, Any], field: str, operator: FilterOperator, value: Any
) -> bool:
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
    # Handle field existence operators
    if operator == FilterOperator.EXISTS:
                return field in item and item[field] is not None
    elif operator == FilterOperator.NOT_EXISTS:
                return field not in item or item[field] is None

    # For other operators, the field must exist
    if field not in item:
                return False

    item_value = item[field]

    # Handle None values
    if item_value is None:
        # None values only match equality operators
                return (operator == FilterOperator.EQ and value is None) or (
            operator == FilterOperator.NE and value is not None
        )

    # Apply the operator
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
        # Handle different types for contains
        if isinstance(item_value, str) and isinstance(value, str):
                    return value.lower() in item_value.lower()
        elif isinstance(item_value, (list, tuple, set)):
                    return value in item_value
        else:
                    return False
    elif operator == FilterOperator.STARTS_WITH:
        if isinstance(item_value, str) and isinstance(value, str):
                    return item_value.lower().startswith(value.lower())
        else:
                    return False
    elif operator == FilterOperator.ENDS_WITH:
        if isinstance(item_value, str) and isinstance(value, str):
                    return item_value.lower().endswith(value.lower())
        else:
                    return False
    elif operator == FilterOperator.REGEX:
        if isinstance(item_value, str) and isinstance(value, str):
            try:
                        return bool(re.search(value, item_value, re.IGNORECASE))
            except re.error:
                        return False
        else:
                    return False
    else:
                return False