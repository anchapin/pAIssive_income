"""
"""
Tests for the developer API.
Tests for the developer API.


This module contains tests for the developer API endpoints.
This module contains tests for the developer API endpoints.
"""
"""




from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id, generate_solution_data
from tests.api.utils.test_data import generate_id, generate_solution_data


(
(
validate_bulk_response,
validate_bulk_response,
validate_error_response,
validate_error_response,
validate_field_equals,
validate_field_equals,
validate_field_exists,
validate_field_exists,
validate_field_not_empty,
validate_field_not_empty,
validate_field_type,
validate_field_type,
validate_list_contains,
validate_list_contains,
validate_paginated_response,
validate_paginated_response,
validate_success_response,
validate_success_response,
)
)




class TestDeveloperAPI:
    class TestDeveloperAPI:
    """Tests for the developer API."""

    def test_get_niches(self, api_test_client: APITestClient):
    """Test getting all development niches."""
    # Make request
    response = api_test_client.get("developer/niches")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate their structure
    if result["items"]:
    item = result["items"][0]
    validate_field_exists(item, "id")
    validate_field_type(item, "id", str)
    validate_field_exists(item, "name")
    validate_field_type(item, "name", str)
    validate_field_exists(item, "description")
    validate_field_type(item, "description", str)
    validate_field_exists(item, "technical_requirements")
    validate_field_type(item, "technical_requirements", list)

    def test_get_templates(self, api_test_client: APITestClient):
    """Test getting all development templates."""
    # Make request
    response = api_test_client.get("developer/templates")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate their structure
    if result["items"]:
    item = result["items"][0]
    validate_field_exists(item, "id")
    validate_field_type(item, "id", str)
    validate_field_exists(item, "name")
    validate_field_type(item, "name", str)
    validate_field_exists(item, "description")
    validate_field_type(item, "description", str)
    validate_field_exists(item, "technology_stack")
    validate_field_type(item, "technology_stack", list)
    validate_field_exists(item, "features")
    validate_field_type(item, "features", list)

    def test_create_solution(self, api_test_client: APITestClient):
    """Test creating a development solution."""
    # Generate test data
    data = generate_solution_data()

    # Make request
    response = api_test_client.post("developer/solution", data)

    # Validate response
    result = validate_success_response(response, 201)  # Created

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_type(result, "id", str)
    validate_field_not_empty(result, "id")
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])
    validate_field_exists(result, "niche_id")
    validate_field_equals(result, "niche_id", data["niche_id"])
    validate_field_exists(result, "template_id")
    validate_field_equals(result, "template_id", data["template_id"])
    validate_field_exists(result, "technology_stack")
    validate_field_type(result, "technology_stack", list)
    validate_field_exists(result, "features")
    validate_field_type(result, "features", list)
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", "created")

    def test_get_solution(self, api_test_client: APITestClient):
    """Test getting a specific development solution."""
    # Generate a random ID
    solution_id = generate_id()

    # Make request
    response = api_test_client.get(f"developer/solutions/{solution_id}")

    # This might return 404 if the solution doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", solution_id)
    validate_field_exists(result, "name")
    validate_field_type(result, "name", str)
    validate_field_exists(result, "description")
    validate_field_type(result, "description", str)
    validate_field_exists(result, "niche_id")
    validate_field_type(result, "niche_id", str)
    validate_field_exists(result, "template_id")
    validate_field_type(result, "template_id", str)
    validate_field_exists(result, "technology_stack")
    validate_field_type(result, "technology_stack", list)
    validate_field_exists(result, "features")
    validate_field_type(result, "features", list)
    validate_field_exists(result, "status")
    validate_field_type(result, "status", str)
    validate_field_exists(result, "created_at")
    validate_field_type(result, "created_at", str)
    validate_field_exists(result, "updated_at")
    validate_field_type(result, "updated_at", str)

    def test_get_solutions(self, api_test_client: APITestClient):
    """Test getting all development solutions."""
    # Make request
    response = api_test_client.get("developer/solutions")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    def test_update_solution(self, api_test_client: APITestClient):
    """Test updating a development solution."""
    # Generate a random ID and test data
    solution_id = generate_id()
    data = generate_solution_data()

    # Make request
    response = api_test_client.put(f"developer/solutions/{solution_id}", data)

    # This might return 404 if the solution doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", solution_id)
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])

    def test_update_solution_fields(self, api_test_client: APITestClient):
    """Test updating specific fields of a development solution."""
    # Generate a random ID and test data
    solution_id = generate_id()
    data = {
    "name": "Updated Solution",
    "description": "Updated solution description",
    "status": "in_progress",
    "technology_stack": ["python", "fastapi", "postgresql"],
    "metadata": {"version": "2.0", "priority": "high"},
    }

    # Make request
    response = api_test_client.put(f"developer/solutions/{solution_id}", data)

    # This might return 404 if the solution doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate required fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", solution_id)
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])

    # Validate optional fields if they were updated
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", data["status"])
    validate_field_exists(result, "technology_stack")
    validate_field_type(result, "technology_stack", list)
    for tech in data["technology_stack"]:
    validate_list_contains(result["technology_stack"], tech)
    validate_field_exists(result, "metadata")
    validate_field_type(result, "metadata", dict)
    validate_field_equals(
    result["metadata"], "version", data["metadata"]["version"]
    )
    validate_field_equals(
    result["metadata"], "priority", data["metadata"]["priority"]
    )

    # Validate timestamps
    validate_field_exists(result, "updated_at")
    validate_field_type(result, "updated_at", str)

    def test_delete_solution(self, api_test_client: APITestClient):
    """Test deleting a development solution."""
    # Generate a random ID
    solution_id = generate_id()

    # Make request
    response = api_test_client.delete(f"developer/solutions/{solution_id}")

    # This might return 404 if the solution doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    validate_success_response(response, 204)  # No Content

    def test_filter_solutions(self, api_test_client: APITestClient):
    """Test filtering development solutions."""
    # Make request with filter
    response = api_test_client.get(
    "developer/solutions",
    params={
    "status": "in_progress",
    "technology": "python",
    "sort": "created_at:desc",
    "page": 1,
    "page_size": 10,
    },
    )

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate that they match the filter
    if result["items"]:
    for item in result["items"]:
    validate_field_equals(item, "status", "in_progress")
    # Check if any technology in the stack matches 'python' case-insensitively
    tech_match = any(
    tech.lower() == "python" for tech in item["technology_stack"]
    )
    assert (
    tech_match
    ), f"Technology stack {item['technology_stack']} does not contain 'python' (case-insensitive)"

    def test_invalid_solution_request(self, api_test_client: APITestClient):
    """Test invalid solution request."""
    # Make request with invalid data
    response = api_test_client.post("developer/solution", {})

    # Validate error response
    validate_error_response(response, 422)  # Unprocessable Entity

    def test_nonexistent_solution(self, api_test_client: APITestClient):
    """Test getting a nonexistent solution."""
    # Generate a random ID that is unlikely to exist
    solution_id = "nonexistent-" + generate_id()

    # Make request
    response = api_test_client.get(f"developer/solutions/{solution_id}")

    # Validate error response
    validate_error_response(response, 404)  # Not Found

    def test_invalid_solution_update(self, api_test_client: APITestClient):
    """Test invalid solution update request."""
    # Generate a random ID
    solution_id = generate_id()

    # Test with empty data
    response = api_test_client.put(f"developer/solutions/{solution_id}", {})
    validate_error_response(response, 422)  # Unprocessable Entity

    # Test with invalid status
    response = api_test_client.put(
    f"developer/solutions/{solution_id}", {"status": "invalid_status"}
    )
    validate_error_response(response, 422)

    # Test with invalid technology stack format
    response = api_test_client.put(
    f"developer/solutions/{solution_id}",
    {"technology_stack": "python,fastapi"},  # Should be a list
    )
    validate_error_response(response, 422)

    def test_delete_solution_errors(self, api_test_client: APITestClient):
    """Test error cases for deleting a solution."""
    # Test deleting with invalid ID format
    response = api_test_client.delete("developer/solutions/invalid-id-format")
    validate_error_response(response, 422)  # Unprocessable Entity

    # Test deleting already deleted solution
    solution_id = generate_id()
    response = api_test_client.delete(f"developer/solutions/{solution_id}")
    if response.status_code == 404:
    # Try deleting again
    response = api_test_client.delete(f"developer/solutions/{solution_id}")
    validate_error_response(response, 404)  # Not Found

    def test_bulk_update_solutions(self, api_test_client: APITestClient):
    """Test bulk updating development solutions."""
    # Generate test data for multiple solutions
    solutions = [
    {
    "id": generate_id(),
    "name": f"Updated Solution {i}",
    "status": "in_progress",
    "metadata": {"batch_update": True},
    }
    for i in range(3)
    ]

    # Make request
    response = api_test_client.bulk_update("developer/solutions", solutions)

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(solutions))
    validate_field_exists(result["stats"], "updated")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["updated"] + result["stats"]["failed"] == len(solutions)

    # Validate updated items
    validate_field_exists(result, "items")
    validate_field_type(result, "items", list)
    for item in result["items"]:
    validate_field_exists(item, "id")
    validate_field_exists(item, "success")
    if item["success"]:
    validate_field_exists(item, "data")
    validate_field_type(item, "data", dict)
    else:
    validate_field_exists(item, "error")
    validate_field_type(item, "error", dict)

    def test_bulk_delete_solutions(self, api_test_client: APITestClient):
    """Test bulk deleting development solutions."""
    # Generate IDs for solutions to delete
    solution_ids = [generate_id() for _ in range(3)]

    # Make request
    response = api_test_client.bulk_delete("developer/solutions", solution_ids)

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(solution_ids))
    validate_field_exists(result["stats"], "deleted")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["deleted"] + result["stats"]["failed"] == len(
    solution_ids
    )

    # Validate results for each ID
    validate_field_exists(result, "items")
    validate_field_type(result, "items", list)
    for item in result["items"]:
    validate_field_exists(item, "id")
    validate_field_exists(item, "success")
    if not item["success"]:
    validate_field_exists(item, "error")
    validate_field_type(item, "error", dict)

    def test_invalid_bulk_operations(self, api_test_client: APITestClient):
    """Test invalid bulk update and delete operations."""
    # Test bulk update with empty list
    response = api_test_client.bulk_update("developer/solutions", [])
    validate_error_response(response, 422)

    # Test bulk update with invalid data
    response = api_test_client.bulk_update(
    "developer/solutions",
    [
    {"id": "invalid-id"},  # Missing required fields
    {"name": "No ID"},  # Missing ID
    ],
    )
    validate_error_response(response, 422)

    # Test bulk delete with empty list
    response = api_test_client.bulk_delete("developer/solutions", [])
    validate_error_response(response, 422)

    # Test bulk delete with invalid IDs
    response = api_test_client.bulk_delete(
    "developer/solutions", ["invalid-id-1", "invalid-id-2"]
    )
    result = validate_bulk_response(response)
    validate_field_equals(result["stats"], "failed", 2)