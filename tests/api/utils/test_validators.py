"""
Test validators for API tests.

This module provides utilities for validating API responses in tests.
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi.testclient import TestClient
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
    Validate that a response is JSON and return the parsed JSON.

    Args:
        response: Response to validate

    Returns:
        Parsed JSON response

    Raises:
        AssertionError: If the response is not valid JSON
    """
    try:
        return response.json()
    except json.JSONDecodeError:
        assert False, f"Response is not valid JSON: {response.text}"


def validate_error_response(
    response: Response, expected_status_code: int, expected_error_code: Optional[str] = None
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

    # Check for both possible error formats
    if "error" in data:
        assert (
            "message" in data["error"]
        ), f"Error response does not contain 'message' field: {data}"

        if expected_error_code:
            assert "code" in data["error"], f"Error response does not contain 'code' field: {data}"
            assert (
                data["error"]["code"] == expected_error_code
            ), f"Expected error code {expected_error_code}, got {data['error']['code']}"
    elif "detail" in data:
        # Alternative error format
        if isinstance(data["detail"], dict):
            assert (
                "message" in data["detail"]
            ), f"Error response does not contain 'message' field: {data}"

            if expected_error_code:
                assert (
                    "code" in data["detail"]
                ), f"Error response does not contain 'code' field: {data}"
                assert (
                    data["detail"]["code"] == expected_error_code
                ), f"Expected error code {expected_error_code}, got {data['detail']['code']}"
    else:
        assert False, f"Error response does not contain 'error' or 'detail' field: {data}"

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

    # Special case for 204 No Content responses
    if expected_status_code == 204:
        return {}

    return validate_json_response(response)


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

    assert "items" in data, f"Paginated response does not contain 'items' field: {data}"
    assert "total" in data, f"Paginated response does not contain 'total' field: {data}"
    assert "page" in data, f"Paginated response does not contain 'page' field: {data}"
    assert "page_size" in data, f"Paginated response does not contain 'page_size' field: {data}"

    return data


def validate_bulk_response(response: Response, expected_status_code: int = 200) -> Dict[str, Any]:
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

    assert "stats" in data, f"Bulk response does not contain 'stats' field: {data}"
    assert "total" in data["stats"], f"Bulk response stats does not contain 'total' field: {data}"
    assert (
        "success" in data["stats"]
    ), f"Bulk response stats does not contain 'success' field: {data}"
    assert (
        "failure" in data["stats"]
    ), f"Bulk response stats does not contain 'failure' field: {data}"

    if data["stats"]["failure"] > 0:
        assert (
            "errors" in data
        ), f"Bulk response with failures does not contain 'errors' field: {data}"

    return data


def validate_field_exists(data: Dict[str, Any], field: str) -> None:
    """
    Validate that a field exists in a dictionary.

    Args:
        data: Dictionary to validate
        field: Field to check

    Raises:
        AssertionError: If the field does not exist
    """
    assert field in data, f"Field '{field}' does not exist in data: {data}"


def validate_field_equals(data: Dict[str, Any], field: str, expected_value: Any) -> None:
    """
    Validate that a field equals an expected value.

    Args:
        data: Dictionary to validate
        field: Field to check
        expected_value: Expected value

    Raises:
        AssertionError: If the field does not equal the expected value
    """
    validate_field_exists(data, field)
    assert (
        data[field] == expected_value
    ), f"Field '{field}' expected to be {expected_value}, got {data[field]}"


def validate_field_type(data: Dict[str, Any], field: str, expected_type: type) -> None:
    """
    Validate that a field is of an expected type.

    Args:
        data: Dictionary to validate
        field: Field to check
        expected_type: Expected type

    Raises:
        AssertionError: If the field is not of the expected type
    """
    validate_field_exists(data, field)
    assert isinstance(
        data[field], expected_type
    ), f"Field '{field}' expected to be of type {expected_type}, got {type(data[field])}"


def validate_field_not_empty(data: Dict[str, Any], field: str) -> None:
    """
    Validate that a field is not empty.

    Args:
        data: Dictionary to validate
        field: Field to check

    Raises:
        AssertionError: If the field is empty
    """
    validate_field_exists(data, field)
    assert data[field], f"Field '{field}' is empty"


def validate_list_not_empty(data: List[Any]) -> None:
    """
    Validate that a list is not empty.

    Args:
        data: List to validate

    Raises:
        AssertionError: If the list is empty
    """
    assert data, "List is empty"


def validate_list_length(data: List[Any], expected_length: int) -> None:
    """
    Validate that a list has an expected length.

    Args:
        data: List to validate
        expected_length: Expected length

    Raises:
        AssertionError: If the list does not have the expected length
    """
    assert (
        len(data) == expected_length
    ), f"List expected to have length {expected_length}, got {len(data)}"


def validate_list_min_length(data: List[Any], min_length: int) -> None:
    """
    Validate that a list has at least a minimum length.

    Args:
        data: List to validate
        min_length: Minimum length

    Raises:
        AssertionError: If the list does not have at least the minimum length
    """
    assert (
        len(data) >= min_length
    ), f"List expected to have at least length {min_length}, got {len(data)}"


def validate_list_max_length(data: List[Any], max_length: int) -> None:
    """
    Validate that a list has at most a maximum length.

    Args:
        data: List to validate
        max_length: Maximum length

    Raises:
        AssertionError: If the list does not have at most the maximum length
    """
    assert (
        len(data) <= max_length
    ), f"List expected to have at most length {max_length}, got {len(data)}"


def validate_list_contains(data: List[Any], item: Any) -> None:
    """
    Validate that a list contains an item.

    Args:
        data: List to validate
        item: Item to check

    Raises:
        AssertionError: If the list does not contain the item
    """
    assert item in data, f"List does not contain item {item}"


def validate_list_contains_dict_with_field(
    data: List[Dict[str, Any]], field: str, value: Any
) -> None:
    """
    Validate that a list contains a dictionary with a field equal to a value.

    Args:
        data: List to validate
        field: Field to check
        value: Expected value

    Raises:
        AssertionError: If the list does not contain a dictionary with the field equal to the value
    """
    for item in data:
        if field in item and item[field] == value:
            return
    assert False, f"List does not contain a dictionary with field '{field}' equal to {value}"
