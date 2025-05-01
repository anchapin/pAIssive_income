"""
Utility functions for validating API responses in tests.
"""

from typing import Dict, Any, Optional, List, Union
from requests import Response


def validate_status_code(response: Response, expected_status_code: int) -> None:
    """
    Validate the status code of a response.

    Args:
        response: Response to validate
        expected_status_code: Expected status code

    Raises:
        AssertionError: If the status code is not as expected
    """
    assert (
        response.status_code == expected_status_code
    ), f"Expected status code {expected_status_code}, got {response.status_code}. Response: {response.text}"


def validate_json_response(response: Response) -> Dict[str, Any]:
    """
    Validate that a response contains valid JSON.

    Args:
        response: Response to validate

    Returns:
        Parsed JSON response

    Raises:
        AssertionError: If the response is not valid JSON
    """
    try:
        data = response.json()
        assert isinstance(data, (dict, list)), f"Response is not a valid JSON object or array: {data}"
        return data
    except Exception as e:
        assert False, f"Response is not valid JSON: {response.text}. Error: {str(e)}"


def validate_error_response(
    response: Response,
    expected_status_code: int,
    expected_error_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate an error response.

    Args:
        response: Response to validate
        expected_status_code: Expected status code
        expected_error_code: Expected error code

    Returns:
        Parsed JSON response

    Raises:
        AssertionError: If the response is not a valid error response
    """
    validate_status_code(response, expected_status_code)
    data = validate_json_response(response)

    # Handle FastAPI default error format
    if "detail" in data and not "error" in data:
        # Convert to our standard error format
        data = {"error": {"code": response.status_code, "message": data["detail"]}}
        return data

    assert "error" in data, f"Error response does not contain 'error' field: {data}"
    error = data["error"]
    assert isinstance(error, dict), f"Error field is not a dictionary: {error}"
    assert "message" in error, f"Error does not contain 'message' field: {error}"

    if expected_error_code:
        assert "code" in error, f"Error does not contain 'code' field: {error}"
        assert (
            error["code"] == expected_error_code
        ), f"Expected error code {expected_error_code}, got {error['code']}"

    return data


def validate_success_response(
    response: Response, expected_status_code: int = 200
) -> Dict[str, Any]:
    """
    Validate a success response.

    Args:
        response: Response to validate
        expected_status_code: Expected status code

    Returns:
        Parsed JSON response

    Raises:
        AssertionError: If the response is not a valid success response
    """
    validate_status_code(response, expected_status_code)
    return validate_json_response(response)


def validate_pagination(data: Dict[str, Any]) -> None:
    """
    Validate that a response contains pagination information.

    Args:
        data: Response data to validate

    Raises:
        AssertionError: If the response does not contain pagination information
    """
    assert "items" in data, f"Response does not contain 'items' field: {data}"
    assert isinstance(data["items"], list), f"'items' field is not a list: {data['items']}"
    assert "total" in data, f"Response does not contain 'total' field: {data}"
    assert isinstance(data["total"], int), f"'total' field is not an integer: {data['total']}"
    assert data["total"] >= len(data["items"]), f"'total' is less than the number of items: {data}"


def validate_paginated_response(
    response: Response, expected_status_code: int = 200
) -> Dict[str, Any]:
    """
    Validate a paginated response.

    Args:
        response: Response to validate
        expected_status_code: Expected status code

    Returns:
        Parsed JSON response

    Raises:
        AssertionError: If the response is not a valid paginated response
    """
    data = validate_success_response(response, expected_status_code)
    validate_pagination(data)
    return data


def validate_bulk_response(
    response: Response, expected_status_code: int = 200
) -> Dict[str, Any]:
    """
    Validate a bulk operation response.

    Args:
        response: Response to validate
        expected_status_code: Expected status code

    Returns:
        Parsed JSON response

    Raises:
        AssertionError: If the response is not a valid bulk operation response
    """
    data = validate_success_response(response, expected_status_code)
    
    assert "success" in data, f"Bulk response does not contain 'success' field: {data}"
    assert isinstance(data["success"], bool), f"'success' field is not a boolean: {data['success']}"
    
    if "results" in data:
        assert isinstance(data["results"], list), f"'results' field is not a list: {data['results']}"
    
    if "errors" in data:
        assert isinstance(data["errors"], list), f"'errors' field is not a list: {data['errors']}"
    
    return data


def validate_field_exists(data: Dict[str, Any], field_path: str) -> Any:
    """
    Validate that a field exists in a dictionary, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.profile.name")
        
    Returns:
        The value of the field
        
    Raises:
        AssertionError: If the field does not exist
    """
    parts = field_path.split('.')
    current = data
    
    for part in parts:
        assert isinstance(current, dict), f"Cannot access '{part}' in non-dictionary: {current}"
        assert part in current, f"Field '{part}' not found in: {current}"
        current = current[part]
        
    return current


def validate_field_equals(data: Dict[str, Any], field_path: str, expected_value: Any) -> None:
    """
    Validate that a field in a dictionary equals an expected value, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.profile.name")
        expected_value: Expected value of the field
        
    Raises:
        AssertionError: If the field does not exist or does not equal the expected value
    """
    actual_value = validate_field_exists(data, field_path)
    assert actual_value == expected_value, f"Field '{field_path}' has value '{actual_value}', expected '{expected_value}'"
def validate_field_type(data: Dict[str, Any], field_path: str, expected_type: type) -> Any:
    """
    Validate that a field in a dictionary is of the expected type, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.profile.name")
        expected_type: Expected type of the field
        
    Returns:
        The value of the field
        
    Raises:
        AssertionError: If the field does not exist or is not of the expected type
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, expected_type), f"Field '{field_path}' has type '{type(actual_value).__name__}', expected '{expected_type.__name__}'"
    return actual_value
def validate_field_not_empty(data: Dict[str, Any], field_path: str) -> Any:
    """
    Validate that a field in a dictionary is not empty, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.profile.name")
        
    Returns:
        The value of the field
        
    Raises:
        AssertionError: If the field does not exist or is empty
    """
    actual_value = validate_field_exists(data, field_path)
    
    if isinstance(actual_value, str):
        assert actual_value.strip() != "", f"Field '{field_path}' is empty"
    elif isinstance(actual_value, (list, dict)):
        assert len(actual_value) > 0, f"Field '{field_path}' is empty"
    elif actual_value is None:
        assert False, f"Field '{field_path}' is None"
        
    return actual_value
def validate_list_not_empty(data: Dict[str, Any], field_path: str) -> List[Any]:
    """
    Validate that a field in a dictionary is a non-empty list, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.items")
        
    Returns:
        The list value of the field
        
    Raises:
        AssertionError: If the field does not exist, is not a list, or is an empty list
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, list), f"Field '{field_path}' is not a list, got {type(actual_value).__name__}"
    assert len(actual_value) > 0, f"Field '{field_path}' is an empty list"
    return actual_value
def validate_list_length(data: Dict[str, Any], field_path: str, expected_length: int) -> List[Any]:
    """
    Validate that a field in a dictionary is a list with the expected length, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.items")
        expected_length: Expected length of the list
        
    Returns:
        The list value of the field
        
    Raises:
        AssertionError: If the field does not exist, is not a list, or does not have the expected length
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, list), f"Field '{field_path}' is not a list, got {type(actual_value).__name__}"
    assert len(actual_value) == expected_length, f"Field '{field_path}' has length {len(actual_value)}, expected {expected_length}"
    return actual_value
def validate_list_min_length(data: Dict[str, Any], field_path: str, min_length: int) -> List[Any]:
    """
    Validate that a field in a dictionary is a list with at least the minimum length, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.items")
        min_length: Minimum length of the list
        
    Returns:
        The list value of the field
        
    Raises:
        AssertionError: If the field does not exist, is not a list, or has fewer items than the minimum length
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, list), f"Field '{field_path}' is not a list, got {type(actual_value).__name__}"
    assert len(actual_value) >= min_length, f"Field '{field_path}' has length {len(actual_value)}, expected at least {min_length}"
    return actual_value
def validate_list_max_length(data: Dict[str, Any], field_path: str, max_length: int) -> List[Any]:
    """
    Validate that a field in a dictionary is a list with at most the maximum length, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.items")
        max_length: Maximum length of the list
        
    Returns:
        The list value of the field
        
    Raises:
        AssertionError: If the field does not exist, is not a list, or has more items than the maximum length
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, list), f"Field '{field_path}' is not a list, got {type(actual_value).__name__}"
    assert len(actual_value) <= max_length, f"Field '{field_path}' has length {len(actual_value)}, expected at most {max_length}"
    return actual_value


def validate_list_contains(data: Dict[str, Any], field_path: str, expected_item: Any) -> List[Any]:
    """
    Validate that a list field in a dictionary contains the expected item, supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.items")
        expected_item: Item that should be in the list
        
    Returns:
        The list value of the field
        
    Raises:
        AssertionError: If the field does not exist, is not a list, or does not contain the expected item
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, list), f"Field '{field_path}' is not a list, got {type(actual_value).__name__}"
    assert expected_item in actual_value, f"Field '{field_path}' does not contain item '{expected_item}'"
    return actual_value


def validate_list_contains_dict_with_field(
    data: Dict[str, Any], 
    field_path: str, 
    dict_field: str, 
    expected_value: Any
) -> List[Dict[str, Any]]:
    """
    Validate that a list field in a dictionary contains a dictionary with a specific field value,
    supporting dot notation for nested fields.
    
    Args:
        data: Dictionary to check
        field_path: Field path using dot notation (e.g., "user.items")
        dict_field: Field in the dictionaries within the list to check
        expected_value: Expected value of the field in at least one dictionary
        
    Returns:
        The list value of the field
        
    Raises:
        AssertionError: If the field does not exist, is not a list of dictionaries,
                       or none of the dictionaries contain the expected field value
    """
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(actual_value, list), f"Field '{field_path}' is not a list, got {type(actual_value).__name__}"
    
    for item in actual_value:
        assert isinstance(item, dict), f"Item in list '{field_path}' is not a dictionary, got {type(item).__name__}"
        
        if dict_field in item and item[dict_field] == expected_value:
            return actual_value
    
    assert False, f"No dictionary in list '{field_path}' has field '{dict_field}' with value '{expected_value}'"
    return actual_value
def generate_id() -> str:
    """
    Generate a random ID for testing.

    Returns:
        Random ID
    """
    import uuid
    return str(uuid.uuid4())
