"""
Tests for the GraphQL API.

This module contains tests for GraphQL queries, mutations, and subscriptions.
"""

import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id
)
from tests.api.utils.test_validators import (
    validate_status_code, validate_json_response, validate_error_response,
    validate_success_response, validate_paginated_response, validate_bulk_response,
    validate_field_exists, validate_field_equals, validate_field_type,
    validate_field_not_empty, validate_list_not_empty, validate_list_length,
    validate_list_min_length, validate_list_max_length, validate_list_contains,
    validate_list_contains_dict_with_field
)


class TestGraphQLAPI:
    """Tests for the GraphQL API."""

    def test_query_resolver(self, api_test_client: APITestClient):
        """Test basic query resolver with field selection."""
        # GraphQL query
        query = """
        query GetNicheAnalysis($id: ID!) {
            nicheAnalysis(id: $id) {
                id
                status
                marketAnalysis {
                    size
                    growth
                    competition
                }
                results {
                    opportunityScore
                    recommendations {
                        title
                        description
                        priority
                    }
                }
            }
        }
        """
        
        # Variables
        variables = {
            "id": generate_id()
        }
        
        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": query,
                "variables": variables
            }
        )
        
        # Validate response structure
        result = validate_json_response(response)
        
        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:  # If no errors, validate data
            data = result["data"]
            validate_field_exists(data, "nicheAnalysis")
            if data["nicheAnalysis"]:
                niche = data["nicheAnalysis"]
                validate_field_exists(niche, "id")
                validate_field_exists(niche, "status")
                validate_field_exists(niche, "marketAnalysis")
                validate_field_exists(niche, "results")

    def test_nested_query_resolver(self, api_test_client: APITestClient):
        """Test nested query resolution."""
        # GraphQL query
        query = """
        query GetMarketingStrategy($id: ID!) {
            marketingStrategy(id: $id) {
                id
                name
                campaigns {
                    id
                    name
                    status
                    metrics {
                        impressions
                        clicks
                        conversions
                        roi
                    }
                    content {
                        id
                        type
                        title
                        performance {
                            views
                            engagement
                        }
                    }
                }
            }
        }
        """
        
        # Variables
        variables = {
            "id": generate_id()
        }
        
        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": query,
                "variables": variables
            }
        )
        
        # Validate response structure
        result = validate_json_response(response)
        
        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "marketingStrategy")
            if data["marketingStrategy"]:
                strategy = data["marketingStrategy"]
                validate_field_exists(strategy, "id")
                validate_field_exists(strategy, "name")
                validate_field_exists(strategy, "campaigns")
                if strategy["campaigns"]:
                    campaign = strategy["campaigns"][0]
                    validate_field_exists(campaign, "metrics")
                    validate_field_exists(campaign, "content")

    def test_mutation_resolver(self, api_test_client: APITestClient):
        """Test mutation resolver with input validation."""
        # GraphQL mutation
        mutation = """
        mutation CreateCampaign($input: CreateCampaignInput!) {
            createCampaign(input: $input) {
                campaign {
                    id
                    name
                    status
                    budget
                    startDate
                    endDate
                }
                errors {
                    field
                    message
                }
            }
        }
        """
        
        # Variables
        variables = {
            "input": {
                "name": "Test Campaign",
                "budget": 1000.00,
                "startDate": "2025-05-01",
                "endDate": "2025-05-31",
                "channels": ["SOCIAL_MEDIA", "EMAIL"],
                "targetAudience": {
                    "demographics": {
                        "ageRanges": ["25_34", "35_44"],
                        "locations": ["US", "UK"]
                    }
                }
            }
        }
        
        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": variables
            }
        )
        
        # Validate response structure
        result = validate_json_response(response)
        
        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "createCampaign")
            validate_field_exists(data["createCampaign"], "campaign")
            validate_field_exists(data["createCampaign"], "errors")
            
            campaign = data["createCampaign"]["campaign"]
            if campaign:
                validate_field_exists(campaign, "id")
                validate_field_exists(campaign, "name")
                validate_field_equals(campaign, "name", variables["input"]["name"])
                validate_field_exists(campaign, "status")
                validate_field_exists(campaign, "budget")
                validate_field_equals(campaign, "budget", variables["input"]["budget"])

    def test_subscription_resolver(self, api_test_client: APITestClient):
        """Test subscription resolver for real-time updates."""
        # GraphQL subscription
        subscription = """
        subscription OnCampaignMetricsUpdate($campaignId: ID!) {
            campaignMetricsUpdate(campaignId: $campaignId) {
                timestamp
                metrics {
                    impressions
                    clicks
                    conversions
                    currentSpend
                }
            }
        }
        """
        
        # Variables
        variables = {
            "campaignId": generate_id()
        }
        
        # Make request to set up subscription
        response = api_test_client.post(
            "graphql",
            json={
                "query": subscription,
                "variables": variables
            }
        )
        
        # Validate initial response structure
        result = validate_json_response(response)
        
        # GraphQL specific validation for subscription setup
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "campaignMetricsUpdate")

    def test_error_handling(self, api_test_client: APITestClient):
        """Test GraphQL error handling."""
        # Invalid query
        query = """
        query GetInvalid {
            nonexistentField {
                id
            }
        }
        """
        
        # Make request
        response = api_test_client.post(
            "graphql",
            json={"query": query}
        )
        
        # Validate response structure
        result = validate_json_response(response)
        
        # GraphQL specific validation
        validate_field_exists(result, "errors")
        errors = result["errors"]
        assert len(errors) > 0
        error = errors[0]
        validate_field_exists(error, "message")
        validate_field_exists(error, "locations")

    def test_schema_validation(self, api_test_client: APITestClient):
        """Test GraphQL schema validation."""
        # Query introspection
        query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        
        # Make request
        response = api_test_client.post(
            "graphql",
            json={"query": query}
        )
        
        # Validate response structure
        result = validate_json_response(response)
        
        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "__schema")
            validate_field_exists(data["__schema"], "types")
            assert len(data["__schema"]["types"]) > 0