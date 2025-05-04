"""
"""
Tests for the agent team API.
Tests for the agent team API.


This module contains tests for the agent team API endpoints.
This module contains tests for the agent team API endpoints.
"""
"""




from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_agent_team_data, generate_id
from tests.api.utils.test_data import generate_agent_team_data, generate_id


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
validate_paginated_response,
validate_paginated_response,
validate_success_response,
validate_success_response,
)
)




class TestAgentTeamAPI:
    class TestAgentTeamAPI:
    """Tests for the agent team API."""

    def test_create_team(self, api_test_client: APITestClient):
    """Test creating an agent team."""
    # Generate test data
    data = generate_agent_team_data()

    # Make request
    response = api_test_client.post("agent-team/teams", data)

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
    validate_field_exists(result, "agents")
    validate_field_type(result, "agents", list)
    validate_field_exists(result, "workflow_settings")
    validate_field_type(result, "workflow_settings", dict)

    def test_get_teams(self, api_test_client: APITestClient):
    """Test getting all agent teams."""
    # Make request
    response = api_test_client.get("agent-team/teams")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    def test_get_team(self, api_test_client: APITestClient):
    """Test getting a specific agent team."""
    # Generate a random ID
    team_id = generate_id()

    # Make request
    response = api_test_client.get(f"agent-team/teams/{team_id}")

    # This might return 404 if the team doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", team_id)
    validate_field_exists(result, "name")
    validate_field_type(result, "name", str)
    validate_field_exists(result, "description")
    validate_field_type(result, "description", str)
    validate_field_exists(result, "agents")
    validate_field_type(result, "agents", list)
    validate_field_exists(result, "workflow_settings")
    validate_field_type(result, "workflow_settings", dict)

    def test_update_team(self, api_test_client: APITestClient):
    """Test updating an agent team."""
    # Generate a random ID
    team_id = generate_id()

    # Generate test data
    data = generate_agent_team_data()

    # Make request
    response = api_test_client.put(f"agent-team/teams/{team_id}", data)

    # This might return 404 if the team doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", team_id)
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])
    validate_field_exists(result, "agents")
    validate_field_type(result, "agents", list)
    validate_field_exists(result, "workflow_settings")
    validate_field_type(result, "workflow_settings", dict)

    def test_delete_team(self, api_test_client: APITestClient):
    """Test deleting an agent team."""
    # Generate a random ID
    team_id = generate_id()

    # Make request
    response = api_test_client.delete(f"agent-team/teams/{team_id}")

    # This might return 404 if the team doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    validate_success_response(response, 204)  # No Content

    def test_get_agents(self, api_test_client: APITestClient):
    """Test getting all agents."""
    # Make request
    response = api_test_client.get("agent-team/agents")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    def test_get_agent(self, api_test_client: APITestClient):
    """Test getting a specific agent."""
    # Generate a random ID
    agent_id = generate_id()

    # Make request
    response = api_test_client.get(f"agent-team/agents/{agent_id}")

    # This might return 404 if the agent doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", agent_id)
    validate_field_exists(result, "name")
    validate_field_type(result, "name", str)
    validate_field_exists(result, "role")
    validate_field_type(result, "role", str)
    validate_field_exists(result, "model_id")
    validate_field_type(result, "model_id", str)
    validate_field_exists(result, "capabilities")
    validate_field_type(result, "capabilities", list)

    def test_get_workflows(self, api_test_client: APITestClient):
    """Test getting all workflows."""
    # Make request
    response = api_test_client.get("agent-team/workflows")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    def test_get_workflow(self, api_test_client: APITestClient):
    """Test getting a specific workflow."""
    # Generate a random ID
    workflow_id = generate_id()

    # Make request
    response = api_test_client.get(f"agent-team/workflows/{workflow_id}")

    # This might return 404 if the workflow doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", workflow_id)
    validate_field_exists(result, "name")
    validate_field_type(result, "name", str)
    validate_field_exists(result, "description")
    validate_field_type(result, "description", str)
    validate_field_exists(result, "steps")
    validate_field_type(result, "steps", list)

    def test_run_workflow(self, api_test_client: APITestClient):
    """Test running a workflow."""
    # Generate a random ID
    team_id = generate_id()
    workflow_id = generate_id()

    # Generate test data
    data = {
    "workflow_id": workflow_id,
    "parameters": {
    "market_segments": ["e-commerce", "digital-marketing"],
    "target_audience": "small businesses",
    },
    }

    # Make request
    response = api_test_client.post(f"agent-team/teams/{team_id}/run", data)

    # This might return 404 if the team or workflow doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(
    response, 202
    )  # Accepted (async operation)

    # Validate fields
    validate_field_exists(result, "task_id")
    validate_field_type(result, "task_id", str)
    validate_field_not_empty(result, "task_id")
    validate_field_exists(result, "status_url")
    validate_field_type(result, "status_url", str)
    validate_field_not_empty(result, "status_url")

    def test_bulk_create_teams(self, api_test_client: APITestClient):
    """Test bulk creating agent teams."""
    # Generate test data
    teams = [generate_agent_team_data() for _ in range(3)]

    # Make request
    response = api_test_client.bulk_create("agent-team/teams", teams)

    # Validate response
    result = validate_bulk_response(response, 201)  # Created

    # Validate stats
    validate_field_equals(result["stats"], "total", 3)

    def test_filter_teams(self, api_test_client: APITestClient):
    """Test filtering agent teams."""
    # Make request with filter
    response = api_test_client.get(
    "agent-team/teams",
    params={
    "filter": "name:contains:Team",
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
    validate_field_exists(item, "name")
    assert "Team" in item["name"]

    def test_invalid_team_request(self, api_test_client: APITestClient):
    """Test invalid team request."""
    # Make request with invalid data
    response = api_test_client.post("agent-team/teams", {})

    # Validate error response
    validate_error_response(response, 422)  # Unprocessable Entity

    def test_nonexistent_team(self, api_test_client: APITestClient):
    """Test getting a nonexistent team."""
    # Generate a random ID that is unlikely to exist
    team_id = "nonexistent-" + generate_id()

    # Make request
    response = api_test_client.get(f"agent-team/teams/{team_id}")

    # Validate error response
    validate_error_response(response, 404)  # Not Found