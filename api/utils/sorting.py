"""
"""
Sorting utilities for API endpoints.
Sorting utilities for API endpoints.


This module provides utilities for sorting data in API endpoints.
This module provides utilities for sorting data in API endpoints.
"""
"""




from enum import Enum
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from typing import Any, Callable, Dict, List, Optional




class SortDirection:
    class SortDirection:


    pass  # Added missing block
    pass  # Added missing block
    """Sort direction for query parameters."""

    ASC = "asc"
    DESC = "desc"


    def sort_items(
    items: List[Dict[str, Any]],
    sort_by: str,
    sort_dir: SortDirection = SortDirection.ASC,
    key_func: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> List[Dict[str, Any]]:
    """
    """
    Sort a list of items by a field.
    Sort a list of items by a field.


    Args:
    Args:
    items: List of items to sort
    items: List of items to sort
    sort_by: Field to sort by
    sort_by: Field to sort by
    sort_dir: Sort direction
    sort_dir: Sort direction
    key_func: Optional key function to extract the sort value
    key_func: Optional key function to extract the sort value


    Returns:
    Returns:
    Sorted list of items
    Sorted list of items
    """
    """
    if not items:
    if not items:
    return []
    return []


    # Define a key function that handles None values
    # Define a key function that handles None values
    def default_key_func(item: Dict[str, Any]) -> Any:
    def default_key_func(item: Dict[str, Any]) -> Any:
    value = item.get(sort_by)
    value = item.get(sort_by)
    # None values should be sorted last in ascending order
    # None values should be sorted last in ascending order
    # and first in descending order
    # and first in descending order
    if value is None:
    if value is None:
    return (1, None) if sort_dir == SortDirection.ASC else (0, None)
    return (1, None) if sort_dir == SortDirection.ASC else (0, None)
    return (0, value) if sort_dir == SortDirection.ASC else (1, value)
    return (0, value) if sort_dir == SortDirection.ASC else (1, value)


    # Use the provided key function or the default one
    # Use the provided key function or the default one
    key = key_func or default_key_func
    key = key_func or default_key_func


    return sorted(items, key=key)
    return sorted(items, key=key)




    def multi_sort_items(
    def multi_sort_items(
    items: List[Dict[str, Any]],
    items: List[Dict[str, Any]],
    sort_fields: List[str],
    sort_fields: List[str],
    sort_dirs: Optional[List[SortDirection]] = None,
    sort_dirs: Optional[List[SortDirection]] = None,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Sort a list of items by multiple fields.
    Sort a list of items by multiple fields.


    Args:
    Args:
    items: List of items to sort
    items: List of items to sort
    sort_fields: Fields to sort by
    sort_fields: Fields to sort by
    sort_dirs: Sort directions for each field
    sort_dirs: Sort directions for each field


    Returns:
    Returns:
    Sorted list of items
    Sorted list of items
    """
    """
    if not items or not sort_fields:
    if not items or not sort_fields:
    return items
    return items


    # Use ASC as default direction if not provided
    # Use ASC as default direction if not provided
    if not sort_dirs:
    if not sort_dirs:
    sort_dirs = [SortDirection.ASC] * len(sort_fields)
    sort_dirs = [SortDirection.ASC] * len(sort_fields)
    # If fewer directions than fields, use ASC for the rest
    # If fewer directions than fields, use ASC for the rest
    elif len(sort_dirs) < len(sort_fields):
    elif len(sort_dirs) < len(sort_fields):
    sort_dirs = sort_dirs + [SortDirection.ASC] * (
    sort_dirs = sort_dirs + [SortDirection.ASC] * (
    len(sort_fields) - len(sort_dirs)
    len(sort_fields) - len(sort_dirs)
    )
    )


    # Sort by each field in reverse order to get the correct multi-field sort
    # Sort by each field in reverse order to get the correct multi-field sort
    for i in range(len(sort_fields) - 1, -1, -1):
    for i in range(len(sort_fields) - 1, -1, -1):
    field = sort_fields[i]
    field = sort_fields[i]
    direction = sort_dirs[i]
    direction = sort_dirs[i]
    items = sort_items(items, field, direction)
    items = sort_items(items, field, direction)


    return items
    return items