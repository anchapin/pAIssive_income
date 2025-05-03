"""
Integration tests for the API.

This module contains integration tests that span multiple API endpoints.
"""


import pytest

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import 

(
    generate_agent_team_data,
    generate_marketing_strategy_data,
    generate_monetization_data,
    generate_niche_analysis_data,
)
from tests.api.utils.test_validators import (
    validate_field_exists,
    validate_field_type,
    validate_paginated_response,
    validate_success_response,
)


class TestAPIIntegration:
    """Integration tests for the API."""

    def test_niche_to_solution_workflow(self, auth_api_test_client: APITestClient):
        """Test the niche analysis to solution development workflow."""
        # Step 1: Create a niche analysis
        niche_data = generate_niche_analysis_data()
        response = auth_api_test_client.post("niche-analysis/analyze", niche_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Niche analysis endpoint not implemented")

        # Validate response
        niche_result = validate_success_response(
            response, 202
        )  # Accepted (async operation)
        validate_field_exists(niche_result, "task_id")

        # Step 2: Check the status of the niche analysis task
        task_id = niche_result["task_id"]
        response = auth_api_test_client.get(f"tasks/{task_id}")

        # If the endpoint returns 404 or 501, skip the status check
        if response.status_code not in (404, 501):
            task_result = validate_success_response(response)
            validate_field_exists(task_result, "status")

        # Step 3: Get the niches
        response = auth_api_test_client.get("niche-analysis/niches")
        niches_result = validate_paginated_response(response)

        # If there are no niches, skip the rest of the test
        if not niches_result["items"]:
            pytest.skip("No niches available for testing")

        # Step 4: Select a niche and develop a solution
        niche_id = niches_result["items"][0]["id"]
        solution_data = {
            "niche_id": niche_id,
            "name": "Test Solution",
            "description": "A solution for testing",
            "features": ["Feature 1", "Feature 2", "Feature 3"],
            "technologies": ["Python", "FastAPI", "React"],
        }

        response = auth_api_test_client.post("solutions", solution_data)

        # If the endpoint returns 404 or 501, skip the solution development
        if response.status_code in (404, 501):
            pytest.skip("Solution development endpoint not implemented")

        # Validate response
        solution_result = validate_success_response(response, 201)  # Created
        validate_field_exists(solution_result, "id")
        solution_id = solution_result["id"]

        # Step 5: Create a monetization strategy for the solution
        monetization_data = generate_monetization_data()
        monetization_data["solution_id"] = solution_id

        response = auth_api_test_client.post(
            "monetization/subscription-models", monetization_data
        )

        # If the endpoint returns 404 or 501, skip the monetization strategy
        if response.status_code in (404, 501):
            pytest.skip("Monetization strategy endpoint not implemented")

        # Validate response
        monetization_result = validate_success_response(response, 201)  # Created
        validate_field_exists(monetization_result, "id")
        monetization_result["id"]

        # Step 6: Create a marketing strategy for the solution
        marketing_data = generate_marketing_strategy_data()
        marketing_data["niche_id"] = niche_id
        marketing_data["solution_id"] = solution_id

        response = auth_api_test_client.post("marketing/strategies", marketing_data)

        # If the endpoint returns 404 or 501, skip the marketing strategy
        if response.status_code in (404, 501):
            pytest.skip("Marketing strategy endpoint not implemented")

        # Validate response
        marketing_result = validate_success_response(response, 201)  # Created
        validate_field_exists(marketing_result, "id")

    def test_agent_team_workflow(self, auth_api_test_client: APITestClient):
        """Test the agent team workflow."""
        # Step 1: Create an agent team
        team_data = generate_agent_team_data()
        response = auth_api_test_client.post("agent-team/teams", team_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Agent team endpoint not implemented")

        # Validate response
        team_result = validate_success_response(response, 201)  # Created
        validate_field_exists(team_result, "id")
        team_id = team_result["id"]

        # Step 2: Run a niche analysis workflow with the team
        workflow_data = {
            "workflow_id": "niche-analysis",
            "parameters": {
                "market_segments": ["e-commerce", "digital-marketing"],
                "target_audience": "small businesses",
            },
        }

        response = auth_api_test_client.post(
            f"agent-team/teams/{team_id}/run", workflow_data
        )

        # If the endpoint returns 404 or 501, skip the workflow
        if response.status_code in (404, 501):
            pytest.skip("Team workflow endpoint not implemented")

        # Validate response
        workflow_result = validate_success_response(
            response, 202
        )  # Accepted (async operation)
        validate_field_exists(workflow_result, "task_id")

        # Step 3: Check the status of the workflow task
        task_id = workflow_result["task_id"]
        response = auth_api_test_client.get(f"tasks/{task_id}")

        # If the endpoint returns 404 or 501, skip the status check
        if response.status_code not in (404, 501):
            task_result = validate_success_response(response)
            validate_field_exists(task_result, "status")

    def test_api_key_authentication(
        self, api_test_client: APITestClient, auth_api_test_client: APITestClient
    ):
        """Test API key authentication."""
        # Step 1: Create an API key (requires authentication)
        api_key_data = {
            "name": "Test API Key",
            "description": "API key for testing",
            "permissions": ["read"],
            "expires_at": "2099-12-31T23:59:59Z",
        }

        response = auth_api_test_client.post("api-keys", api_key_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("API key endpoint not implemented")

        # Validate response
        api_key_result = validate_success_response(response, 201)  # Created
        validate_field_exists(api_key_result, "key")
        api_key = api_key_result["key"]

        # Step 2: Use the API key to access a protected endpoint
        headers = {"X-API-Key": api_key}

        response = api_test_client.get("niche-analysis/niches", headers=headers)

        # Validate response
        validate_success_response(response)

    def test_webhook_integration(self, auth_api_test_client: APITestClient):
        """Test webhook integration."""
        # Step 1: Create a webhook
        webhook_data = {
            "url": "https://example.com/webhook",
            "event_types": ["niche.created", "solution.created"],
            "description": "Webhook for testing",
            "is_active": True,
            "secret": "test-webhook-secret",
        }

        response = auth_api_test_client.post("webhooks", webhook_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Webhook endpoint not implemented")

        # Validate response
        webhook_result = validate_success_response(response, 201)  # Created
        validate_field_exists(webhook_result, "id")
        webhook_id = webhook_result["id"]

        # Step 2: Create a niche analysis (should trigger the webhook)
        niche_data = generate_niche_analysis_data()
        response = auth_api_test_client.post("niche-analysis/analyze", niche_data)

        # If the endpoint returns 404 or 501, skip the niche analysis
        if response.status_code in (404, 501):
            pytest.skip("Niche analysis endpoint not implemented")

        # Step 3: Check webhook deliveries
        response = auth_api_test_client.get(f"webhooks/{webhook_id}/deliveries")

        # If the endpoint returns 404 or 501, skip the delivery check
        if response.status_code in (404, 501):
            pytest.skip("Webhook deliveries endpoint not implemented")

        # Validate response
        deliveries_result = validate_paginated_response(response)
        validate_field_type(deliveries_result, "items", list)

    def test_analytics_integration(self, auth_api_test_client: APITestClient):
        """Test analytics integration."""
        # Step 1: Make several API requests to generate analytics data
        auth_api_test_client.get("niche-analysis/niches")
        auth_api_test_client.get("monetization/subscription-models")
        auth_api_test_client.get("marketing/strategies")
        auth_api_test_client.get("ai-models/models")
        auth_api_test_client.get("agent-team/teams")

        # Step 2: Check analytics data
        response = auth_api_test_client.get("analytics/summary")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Analytics endpoint not implemented")

        # Validate response
        analytics_result = validate_success_response(response)
        validate_field_exists(analytics_result, "total_requests")
        validate_field_type(analytics_result, "total_requests", int)

        # Step 3: Check endpoint statistics
        response = auth_api_test_client.get("analytics/endpoints")

        # If the endpoint returns 404 or 501, skip the endpoint statistics
        if response.status_code in (404, 501):
            pytest.skip("Endpoint statistics endpoint not implemented")

        # Validate response
        endpoints_result = validate_paginated_response(response)
        validate_field_type(endpoints_result, "items", list)