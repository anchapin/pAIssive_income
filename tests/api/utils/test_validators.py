"""
"""
Utility functions for validating API responses in tests.
Utility functions for validating API responses in tests.
"""
"""




from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from requests import Response
from requests import Response




def validate_status_code():
    def validate_status_code():
    import uuid
    import uuid


    (response: Response, expected_status_code: int) -> None:
    (response: Response, expected_status_code: int) -> None:
    """
    """
    Validate that a response has the expected status code.
    Validate that a response has the expected status code.


    Args:
    Args:
    response: Response to validate
    response: Response to validate
    expected_status_code: Expected status code
    expected_status_code: Expected status code


    Raises:
    Raises:
    AssertionError: If the status code does not match
    AssertionError: If the status code does not match
    """
    """
    assert (
    assert (
    response.status_code == expected_status_code
    response.status_code == expected_status_code
    ), f"Expected status code {expected_status_code}, got {response.status_code}"
    ), f"Expected status code {expected_status_code}, got {response.status_code}"




    def validate_json_response(response: Response) -> Dict[str, Any]:
    def validate_json_response(response: Response) -> Dict[str, Any]:
    """
    """
    Validate that a response contains valid JSON and return the parsed data.
    Validate that a response contains valid JSON and return the parsed data.


    Args:
    Args:
    response: Response to validate
    response: Response to validate


    Returns:
    Returns:
    Parsed JSON response
    Parsed JSON response


    Raises:
    Raises:
    AssertionError: If the response is not valid JSON
    AssertionError: If the response is not valid JSON
    """
    """
    try:
    try:
    data = response.json()
    data = response.json()
    assert isinstance(
    assert isinstance(
    data, (dict, list)
    data, (dict, list)
    ), f"Response is not a valid JSON object or array: {data}"
    ), f"Response is not a valid JSON object or array: {data}"
    return data
    return data
except Exception as e:
except Exception as e:
    assert False, f"Response is not valid JSON: {response.text}. Error: {str(e)}"
    assert False, f"Response is not valid JSON: {response.text}. Error: {str(e)}"




    def validate_error_response(
    def validate_error_response(
    response: Response,
    response: Response,
    expected_status_code: int,
    expected_status_code: int,
    expected_error_code: Optional[str] = None,
    expected_error_code: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Validate that a response is an error response.
    Validate that a response is an error response.


    Args:
    Args:
    response: Response to validate
    response: Response to validate
    expected_status_code: Expected status code
    expected_status_code: Expected status code
    expected_error_code: Expected error code
    expected_error_code: Expected error code


    Returns:
    Returns:
    Parsed error response
    Parsed error response


    Raises:
    Raises:
    AssertionError: If the response is not a valid error response
    AssertionError: If the response is not a valid error response
    """
    """
    validate_status_code(response, expected_status_code)
    validate_status_code(response, expected_status_code)
    data = validate_json_response(response)
    data = validate_json_response(response)


    # Check for both possible error formats
    # Check for both possible error formats
    if "error" in data:
    if "error" in data:
    error = data["error"]
    error = data["error"]
    assert isinstance(error, dict), f"Error field is not a dictionary: {error}"
    assert isinstance(error, dict), f"Error field is not a dictionary: {error}"
    assert "message" in error, f"Error does not contain 'message' field: {error}"
    assert "message" in error, f"Error does not contain 'message' field: {error}"


    if expected_error_code:
    if expected_error_code:
    assert "code" in error, f"Error does not contain 'code' field: {error}"
    assert "code" in error, f"Error does not contain 'code' field: {error}"
    assert (
    assert (
    error["code"] == expected_error_code
    error["code"] == expected_error_code
    ), f"Expected error code {expected_error_code}, got {error['code']}"
    ), f"Expected error code {expected_error_code}, got {error['code']}"


    elif "detail" in data:
    elif "detail" in data:
    # Convert FastAPI error format to our standard format
    # Convert FastAPI error format to our standard format
    detail = data["detail"]
    detail = data["detail"]
    if isinstance(detail, dict):
    if isinstance(detail, dict):
    assert (
    assert (
    "message" in detail or "msg" in detail
    "message" in detail or "msg" in detail
    ), f"Error detail does not contain 'message' or 'msg' field: {detail}"
    ), f"Error detail does not contain 'message' or 'msg' field: {detail}"


    if expected_error_code:
    if expected_error_code:
    assert (
    assert (
    "code" in detail
    "code" in detail
    ), f"Error detail does not contain 'code' field: {detail}"
    ), f"Error detail does not contain 'code' field: {detail}"
    assert (
    assert (
    detail["code"] == expected_error_code
    detail["code"] == expected_error_code
    ), f"Expected error code {expected_error_code}, got {detail['code']}"
    ), f"Expected error code {expected_error_code}, got {detail['code']}"


    data = {"error": detail}
    data = {"error": detail}
    else:
    else:
    # Simple string error message
    # Simple string error message
    data = {"error": {"message": detail, "code": str(expected_status_code)}}
    data = {"error": {"message": detail, "code": str(expected_status_code)}}
    else:
    else:
    assert (
    assert (
    False
    False
    ), f"Error response does not contain 'error' or 'detail' field: {data}"
    ), f"Error response does not contain 'error' or 'detail' field: {data}"


    return data
    return data




    def validate_success_response(
    def validate_success_response(
    response: Response, expected_status_code: int = 200
    response: Response, expected_status_code: int = 200
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Validate that a response is a success response.
    Validate that a response is a success response.


    Args:
    Args:
    response: Response to validate
    response: Response to validate
    expected_status_code: Expected status code
    expected_status_code: Expected status code


    Returns:
    Returns:
    Parsed success response
    Parsed success response


    Raises:
    Raises:
    AssertionError: If the response is not a valid success response
    AssertionError: If the response is not a valid success response
    """
    """
    validate_status_code(response, expected_status_code)
    validate_status_code(response, expected_status_code)
    return validate_json_response(response)
    return validate_json_response(response)




    def validate_paginated_response(
    def validate_paginated_response(
    response: Response, expected_status_code: int = 200
    response: Response, expected_status_code: int = 200
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Validate that a response is a paginated response.
    Validate that a response is a paginated response.


    Args:
    Args:
    response: Response to validate
    response: Response to validate
    expected_status_code: Expected status code
    expected_status_code: Expected status code


    Returns:
    Returns:
    Parsed paginated response
    Parsed paginated response


    Raises:
    Raises:
    AssertionError: If the response is not a valid paginated response
    AssertionError: If the response is not a valid paginated response
    """
    """
    data = validate_success_response(response, expected_status_code)
    data = validate_success_response(response, expected_status_code)


    # Validate pagination fields
    # Validate pagination fields
    assert "items" in data, f"Paginated response does not contain 'items' field: {data}"
    assert "items" in data, f"Paginated response does not contain 'items' field: {data}"
    assert isinstance(
    assert isinstance(
    data["items"], list
    data["items"], list
    ), f"'items' field is not a list: {data['items']}"
    ), f"'items' field is not a list: {data['items']}"
    assert "total" in data, f"Paginated response does not contain 'total' field: {data}"
    assert "total" in data, f"Paginated response does not contain 'total' field: {data}"
    assert "page" in data, f"Paginated response does not contain 'page' field: {data}"
    assert "page" in data, f"Paginated response does not contain 'page' field: {data}"
    assert (
    assert (
    "page_size" in data
    "page_size" in data
    ), f"Paginated response does not contain 'page_size' field: {data}"
    ), f"Paginated response does not contain 'page_size' field: {data}"
    assert "pages" in data, f"Paginated response does not contain 'pages' field: {data}"
    assert "pages" in data, f"Paginated response does not contain 'pages' field: {data}"


    return data
    return data




    def validate_bulk_response(
    def validate_bulk_response(
    response: Response, expected_status_code: int = 201
    response: Response, expected_status_code: int = 201
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Validate that a response is a bulk operation response.
    Validate that a response is a bulk operation response.


    Args:
    Args:
    response: Response to validate
    response: Response to validate
    expected_status_code: Expected status code
    expected_status_code: Expected status code


    Returns:
    Returns:
    Parsed bulk response
    Parsed bulk response


    Raises:
    Raises:
    AssertionError: If the response is not a valid bulk operation response
    AssertionError: If the response is not a valid bulk operation response
    """
    """
    data = validate_success_response(response, expected_status_code)
    data = validate_success_response(response, expected_status_code)


    # Validate bulk operation fields
    # Validate bulk operation fields
    assert "stats" in data, f"Bulk response does not contain 'stats' field: {data}"
    assert "stats" in data, f"Bulk response does not contain 'stats' field: {data}"
    stats = data["stats"]
    stats = data["stats"]
    assert (
    assert (
    "total" in stats
    "total" in stats
    ), f"Bulk response stats does not contain 'total' field: {stats}"
    ), f"Bulk response stats does not contain 'total' field: {stats}"
    assert (
    assert (
    "success" in stats
    "success" in stats
    ), f"Bulk response stats does not contain 'success' field: {stats}"
    ), f"Bulk response stats does not contain 'success' field: {stats}"
    assert (
    assert (
    "failure" in stats
    "failure" in stats
    ), f"Bulk response stats does not contain 'failure' field: {stats}"
    ), f"Bulk response stats does not contain 'failure' field: {stats}"


    if stats["failure"] > 0:
    if stats["failure"] > 0:
    assert (
    assert (
    "errors" in data
    "errors" in data
    ), f"Bulk response with failures does not contain 'errors' field: {data}"
    ), f"Bulk response with failures does not contain 'errors' field: {data}"
    assert isinstance(
    assert isinstance(
    data["errors"], list
    data["errors"], list
    ), f"'errors' field is not a list: {data['errors']}"
    ), f"'errors' field is not a list: {data['errors']}"


    return data
    return data




    def validate_field_exists(data: Dict[str, Any], field_path: str) -> Any:
    def validate_field_exists(data: Dict[str, Any], field_path: str) -> Any:
    """
    """
    Validate that a field exists in a dictionary, supporting dot notation for nested fields.
    Validate that a field exists in a dictionary, supporting dot notation for nested fields.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation (e.g., "user.profile.name")
    field_path: Field path using dot notation (e.g., "user.profile.name")


    Returns:
    Returns:
    The value of the field
    The value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist
    AssertionError: If the field does not exist
    """
    """
    parts = field_path.split(".")
    parts = field_path.split(".")
    current = data
    current = data


    for part in parts:
    for part in parts:
    assert isinstance(
    assert isinstance(
    current, dict
    current, dict
    ), f"Cannot access '{part}' in non-dictionary: {current}"
    ), f"Cannot access '{part}' in non-dictionary: {current}"
    assert part in current, f"Field '{part}' not found in: {current}"
    assert part in current, f"Field '{part}' not found in: {current}"
    current = current[part]
    current = current[part]


    return current
    return current




    def validate_field_equals(
    def validate_field_equals(
    data: Dict[str, Any], field_path: str, expected_value: Any
    data: Dict[str, Any], field_path: str, expected_value: Any
    ) -> None:
    ) -> None:
    """
    """
    Validate that a field equals an expected value, supporting dot notation for nested fields.
    Validate that a field equals an expected value, supporting dot notation for nested fields.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    expected_value: Expected value
    expected_value: Expected value


    Raises:
    Raises:
    AssertionError: If the field does not exist or does not equal the expected value
    AssertionError: If the field does not exist or does not equal the expected value
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert (
    assert (
    actual_value == expected_value
    actual_value == expected_value
    ), f"Field '{field_path}' expected to be {expected_value}, got {actual_value}"
    ), f"Field '{field_path}' expected to be {expected_value}, got {actual_value}"




    def validate_field_type(
    def validate_field_type(
    data: Dict[str, Any], field_path: str, expected_type: type
    data: Dict[str, Any], field_path: str, expected_type: type
    ) -> Any:
    ) -> Any:
    """
    """
    Validate that a field is of an expected type, supporting dot notation for nested fields.
    Validate that a field is of an expected type, supporting dot notation for nested fields.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    expected_type: Expected type
    expected_type: Expected type


    Returns:
    Returns:
    The value of the field
    The value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist or is not of the expected type
    AssertionError: If the field does not exist or is not of the expected type
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, expected_type
    actual_value, expected_type
    ), f"Field '{field_path}' expected to be of type {expected_type.__name__}, got {type(actual_value).__name__}"
    ), f"Field '{field_path}' expected to be of type {expected_type.__name__}, got {type(actual_value).__name__}"
    return actual_value
    return actual_value




    def validate_field_not_empty(data: Dict[str, Any], field_path: str) -> Any:
    def validate_field_not_empty(data: Dict[str, Any], field_path: str) -> Any:
    """
    """
    Validate that a field is not empty, supporting dot notation for nested fields.
    Validate that a field is not empty, supporting dot notation for nested fields.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation


    Returns:
    Returns:
    The value of the field
    The value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist or is empty
    AssertionError: If the field does not exist or is empty
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)


    if isinstance(actual_value, str):
    if isinstance(actual_value, str):
    assert actual_value.strip(), f"Field '{field_path}' is an empty string"
    assert actual_value.strip(), f"Field '{field_path}' is an empty string"
    elif isinstance(actual_value, (list, dict)):
    elif isinstance(actual_value, (list, dict)):
    assert actual_value, f"Field '{field_path}' is empty"
    assert actual_value, f"Field '{field_path}' is empty"
    elif actual_value is None:
    elif actual_value is None:
    assert False, f"Field '{field_path}' is None"
    assert False, f"Field '{field_path}' is None"
    else:
    else:
    # For numbers, booleans, etc. just check if truthy
    # For numbers, booleans, etc. just check if truthy
    assert actual_value, f"Field '{field_path}' is falsy"
    assert actual_value, f"Field '{field_path}' is falsy"


    return actual_value
    return actual_value




    def validate_list_not_empty(data: Dict[str, Any], field_path: str) -> List[Any]:
    def validate_list_not_empty(data: Dict[str, Any], field_path: str) -> List[Any]:
    """
    """
    Validate that a field is a non-empty list, supporting dot notation for nested fields.
    Validate that a field is a non-empty list, supporting dot notation for nested fields.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation


    Returns:
    Returns:
    The list value of the field
    The list value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist, is not a list, or is empty
    AssertionError: If the field does not exist, is not a list, or is empty
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, list
    actual_value, list
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    assert actual_value, f"Field '{field_path}' is an empty list"
    assert actual_value, f"Field '{field_path}' is an empty list"
    return actual_value
    return actual_value




    def validate_list_length(
    def validate_list_length(
    data: Dict[str, Any], field_path: str, expected_length: int
    data: Dict[str, Any], field_path: str, expected_length: int
    ) -> List[Any]:
    ) -> List[Any]:
    """
    """
    Validate that a field is a list with the expected length, supporting dot notation for nested fields.
    Validate that a field is a list with the expected length, supporting dot notation for nested fields.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    expected_length: Expected length
    expected_length: Expected length


    Returns:
    Returns:
    The list value of the field
    The list value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist, is not a list, or has wrong length
    AssertionError: If the field does not exist, is not a list, or has wrong length
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, list
    actual_value, list
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    assert (
    assert (
    len(actual_value) == expected_length
    len(actual_value) == expected_length
    ), f"Field '{field_path}' expected to have length {expected_length}, got {len(actual_value)}"
    ), f"Field '{field_path}' expected to have length {expected_length}, got {len(actual_value)}"
    return actual_value
    return actual_value




    def validate_list_min_length(
    def validate_list_min_length(
    data: Dict[str, Any], field_path: str, min_length: int
    data: Dict[str, Any], field_path: str, min_length: int
    ) -> List[Any]:
    ) -> List[Any]:
    """
    """
    Validate that a field is a list with at least the minimum length.
    Validate that a field is a list with at least the minimum length.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    min_length: Minimum length
    min_length: Minimum length


    Returns:
    Returns:
    The list value of the field
    The list value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist, is not a list, or is too short
    AssertionError: If the field does not exist, is not a list, or is too short
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, list
    actual_value, list
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    assert (
    assert (
    len(actual_value) >= min_length
    len(actual_value) >= min_length
    ), f"Field '{field_path}' expected to have at least {min_length} items, got {len(actual_value)}"
    ), f"Field '{field_path}' expected to have at least {min_length} items, got {len(actual_value)}"
    return actual_value
    return actual_value




    def validate_list_max_length(
    def validate_list_max_length(
    data: Dict[str, Any], field_path: str, max_length: int
    data: Dict[str, Any], field_path: str, max_length: int
    ) -> List[Any]:
    ) -> List[Any]:
    """
    """
    Validate that a field is a list with at most the maximum length.
    Validate that a field is a list with at most the maximum length.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    max_length: Maximum length
    max_length: Maximum length


    Returns:
    Returns:
    The list value of the field
    The list value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist, is not a list, or is too long
    AssertionError: If the field does not exist, is not a list, or is too long
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, list
    actual_value, list
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    assert (
    assert (
    len(actual_value) <= max_length
    len(actual_value) <= max_length
    ), f"Field '{field_path}' expected to have at most {max_length} items, got {len(actual_value)}"
    ), f"Field '{field_path}' expected to have at most {max_length} items, got {len(actual_value)}"
    return actual_value
    return actual_value




    def validate_list_contains(
    def validate_list_contains(
    data: Dict[str, Any], field_path: str, expected_item: Any
    data: Dict[str, Any], field_path: str, expected_item: Any
    ) -> List[Any]:
    ) -> List[Any]:
    """
    """
    Validate that a list field contains an expected item.
    Validate that a list field contains an expected item.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    expected_item: Item that should be in the list
    expected_item: Item that should be in the list


    Returns:
    Returns:
    The list value of the field
    The list value of the field


    Raises:
    Raises:
    AssertionError: If the field does not exist, is not a list, or doesn't contain the item
    AssertionError: If the field does not exist, is not a list, or doesn't contain the item
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, list
    actual_value, list
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    assert (
    assert (
    expected_item in actual_value
    expected_item in actual_value
    ), f"Field '{field_path}' does not contain item: {expected_item}"
    ), f"Field '{field_path}' does not contain item: {expected_item}"
    return actual_value
    return actual_value




    def validate_list_contains_dict_with_field(
    def validate_list_contains_dict_with_field(
    data: Dict[str, Any], field_path: str, dict_field: str, expected_value: Any
    data: Dict[str, Any], field_path: str, dict_field: str, expected_value: Any
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Validate that a list field contains a dictionary with a specific field value.
    Validate that a list field contains a dictionary with a specific field value.


    Args:
    Args:
    data: Dictionary to check
    data: Dictionary to check
    field_path: Field path using dot notation
    field_path: Field path using dot notation
    dict_field: Field in the dictionaries to check
    dict_field: Field in the dictionaries to check
    expected_value: Expected value of the field
    expected_value: Expected value of the field


    Returns:
    Returns:
    The list value of the field
    The list value of the field


    Raises:
    Raises:
    AssertionError: If validation fails
    AssertionError: If validation fails
    """
    """
    actual_value = validate_field_exists(data, field_path)
    actual_value = validate_field_exists(data, field_path)
    assert isinstance(
    assert isinstance(
    actual_value, list
    actual_value, list
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"
    ), f"Field '{field_path}' is not a list: {type(actual_value).__name__}"


    for item in actual_value:
    for item in actual_value:
    assert isinstance(
    assert isinstance(
    item, dict
    item, dict
    ), f"Item in list '{field_path}' is not a dictionary: {type(item).__name__}"
    ), f"Item in list '{field_path}' is not a dictionary: {type(item).__name__}"
    if dict_field in item and item[dict_field] == expected_value:
    if dict_field in item and item[dict_field] == expected_value:
    return actual_value
    return actual_value


    assert (
    assert (
    False
    False
    ), f"No dictionary in list '{field_path}' has field '{dict_field}' with value: {expected_value}"
    ), f"No dictionary in list '{field_path}' has field '{dict_field}' with value: {expected_value}"
    return actual_value
    return actual_value




    def generate_id() -> str:
    def generate_id() -> str:
    """
    """
    Generate a random ID for testing.
    Generate a random ID for testing.


    Returns:
    Returns:
    Random ID
    Random ID
    """
    """




    return str(uuid.uuid4())
    return str(uuid.uuid4())