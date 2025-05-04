"""
Tests for the GraphQL API.

This module contains tests for GraphQL queries, mutations, and subscriptions.
"""

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id
    validate_bulk_response,
    validate_error_response,
    validate_field_equals,
    validate_field_exists,
    validate_field_not_empty,
    validate_field_type,
    validate_json_response,
    validate_list_contains,
    validate_list_contains_dict_with_field,
    validate_list_length,
    validate_list_max_length,
    validate_list_min_length,
    validate_list_not_empty,
    validate_paginated_response,
    validate_status_code,
    validate_success_response,
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
        variables = {"id": generate_id()}

        # Make request
        response = api_test_client.post("graphql", json={"query": query, 
            "variables": variables})

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
        variables = {"id": generate_id()}

        # Make request
        response = api_test_client.post("graphql", json={"query": query, 
            "variables": variables})

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
                "startDate": "2025 - 05 - 01",
                "endDate": "2025 - 05 - 31",
                "channels": ["SOCIAL_MEDIA", "EMAIL"],
                "targetAudience": {
                    "demographics": {"ageRanges": ["25_34", "35_44"], "locations": ["US", 
                        "UK"]}
                },
            }
        }

        # Make request
        response = api_test_client.post("graphql", json={"query": mutation, 
            "variables": variables})

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
        """Test subscription resolver for real - time updates."""
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
        variables = {"campaignId": generate_id()}

        # Make request to set up subscription
        response = api_test_client.post(
            "graphql", json={"query": subscription, "variables": variables}
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
        response = api_test_client.post("graphql", json={"query": query})

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
        response = api_test_client.post("graphql", json={"query": query})

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "__schema")
            validate_field_exists(data["__schema"], "types")
            assert len(data["__schema"]["types"]) > 0

    def test_marketing_queries(self, api_test_client: APITestClient):
        """Test marketing query operations."""
        # Test getting all marketing strategies
        query = """
        query {
            marketingStrategies(limit: 5) {
                id
                name
                description
                targetAudience {
                    demographics
                    interests
                    painPoints
                }
                channels {
                    name
                    priority
                    contentTypes
                }
                goals {
                    metric
                    targetValue
                    timeframe
                }
                createdAt
                updatedAt
            }
        }
        """

        response = api_test_client.post("graphql", json={"query": query})
        result = validate_json_response(response)

        # Validate response structure
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "marketingStrategies")
        validate_field_type(result["data"]["marketingStrategies"], list)

        # Test getting specific marketing strategy
        strategy_id = "test - strategy - id"
        query = """
        query($id: ID!) {
            marketingStrategy(id: $id) {
                id
                name
                description
                channels {
                    name
                    effectivenessScore
                    costPerLead
                }
            }
        }
        """

        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"id": strategy_id}}
        )
        result = validate_json_response(response)

        # Validate response structure
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "marketingStrategy")

        # Test getting marketing channels
        query = """
        query {
            marketingChannels {
                id
                name
                description
                platforms
                effectivenessScore
                costPerLead
            }
        }
        """

        response = api_test_client.post("graphql", json={"query": query})
        result = validate_json_response(response)

        # Validate response structure
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "marketingChannels")
        validate_field_type(result["data"]["marketingChannels"], list)

    def test_marketing_mutations(self, api_test_client: APITestClient):
        """Test marketing mutation operations."""
        # Test creating marketing strategy
        mutation = """
        mutation($input: MarketingStrategyInput!) {
            createMarketingStrategy(input: $input) {
                id
                name
                description
                targetAudience {
                    demographics
                    interests
                    painPoints
                }
                channels {
                    name
                    priority
                    contentTypes
                }
                goals {
                    metric
                    targetValue
                    timeframe
                }
            }
        }
        """

        variables = {
            "input": {
                "name": "Test Strategy",
                "description": "A test marketing strategy",
                "targetAudience": {
                    "demographics": {"ageRange": ["25 - 34"], "location": ["US"]},
                    "interests": ["technology", "marketing"],
                    "painPoints": ["time - consuming content creation"],
                },
                "channels": [
                    {
                        "name": "social_media",
                        "priority": "high",
                        "contentTypes": ["posts", "stories"],
                    }
                ],
                "goals": [
                    {"metric": "engagement_rate", "targetValue": 0.05, 
                        "timeframe": "monthly"}
                ],
            }
        }

        response = api_test_client.post("graphql", json={"query": mutation, 
            "variables": variables})
        result = validate_json_response(response)

        # Validate response structure
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "createMarketingStrategy")
        strategy = result["data"]["createMarketingStrategy"]
        if strategy:
            validate_field_exists(strategy, "id")
            validate_field_equals(strategy, "name", variables["input"]["name"])
            validate_field_exists(strategy, "channels")
            validate_field_type(strategy, "channels", list)

        # Test updating marketing strategy
        strategy_id = strategy["id"] if strategy else "test - strategy - id"
        mutation = """
        mutation($id: ID!, $input: MarketingStrategyInput!) {
            updateMarketingStrategy(id: $id, input: $input) {
                id
                name
                description
                channels {
                    name
                    priority
                    contentTypes
                }
            }
        }
        """

        update_variables = {
            "id": strategy_id,
            "input": {
                "name": "Updated Strategy",
                "description": "An updated test strategy",
                "channels": [
                    {
                        "name": "email",
                        "priority": "medium",
                        "contentTypes": ["newsletter", "drip_campaign"],
                    }
                ],
            },
        }

        response = api_test_client.post(
            "graphql", json={"query": mutation, "variables": update_variables}
        )
        result = validate_json_response(response)

        # Validate response structure
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "updateMarketingStrategy")
        updated = result["data"]["updateMarketingStrategy"]
        if updated:
            validate_field_equals(updated, "name", update_variables["input"]["name"])

        # Test deleting marketing strategy
        mutation = """
        mutation($id: ID!) {
            deleteMarketingStrategy(id: $id)
        }
        """

        response = api_test_client.post(
            "graphql", json={"query": mutation, "variables": {"id": strategy_id}}
        )
        result = validate_json_response(response)

        # Validate response structure
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "deleteMarketingStrategy")
        validate_field_type(result["data"]["deleteMarketingStrategy"], bool)

    def test_marketing_error_scenarios(self, api_test_client: APITestClient):
        """Test error scenarios for marketing operations."""
        # Test querying non - existent strategy
        query = """
        query($id: ID!) {
            marketingStrategy(id: $id) {
                id
                name
            }
        }
        """

        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"id": "non - existent - id"}}
        )
        result = validate_json_response(response)

        # Should return null data without error
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "marketingStrategy")
        assert result["data"]["marketingStrategy"] is None

        # Test creating strategy with invalid input
        mutation = """
        mutation($input: MarketingStrategyInput!) {
            createMarketingStrategy(input: $input) {
                id
                name
            }
        }
        """

        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": {
                    "input": {
                        # Missing required fields
                        "description": "Invalid strategy"
                    }
                },
            },
        )
        result = validate_json_response(response)

        # Should return validation error
        validate_field_exists(result, "errors")
        validate_field_type(result["errors"], list)
        assert len(result["errors"]) > 0

        # Test updating non - existent strategy
        mutation = """
        mutation($id: ID!, $input: MarketingStrategyInput!) {
            updateMarketingStrategy(id: $id, input: $input) {
                id
                name
            }
        }
        """

        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": {
                    "id": "non - existent - id",
                    "input": {"name": "Test Strategy", 
                        "description": "Test description"},
                },
            },
        )
        result = validate_json_response(response)

        # Should return null data without error
        validate_field_exists(result, "data")
        validate_field_exists(result["data"], "updateMarketingStrategy")
        assert result["data"]["updateMarketingStrategy"] is None
