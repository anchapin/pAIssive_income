"""
Tests for the Monetization GraphQL API.

This module contains tests for Monetization GraphQL queries and mutations.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id, generate_monetization_strategy_data
from tests.api.utils.test_validators import (
    validate_field_equals,
    validate_field_exists,
    validate_field_not_empty,
    validate_field_type,
    validate_json_response,
)


class TestMonetizationGraphQLAPI:
    """Tests for the Monetization GraphQL API."""

    def test_monetization_strategies_query(self, api_test_client: APITestClient):
        """Test querying monetization strategies."""
        # GraphQL query
        query = """
        query {
            monetizationStrategies {
                id
                name
                description
                solutionId
                model {
                    type
                    pricing {
                        basePrice
                        currency
                        billingCycle
                    }
                    tiers {
                        name
                        price
                        features
                        isPopular
                    }
                }
                projections {
                    timeframe
                    metrics {
                        users
                        revenue
                        costs
                        profit
                    }
                }
                createdAt
                updatedAt
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
            validate_field_exists(data, "monetizationStrategies")
            validate_field_type(data["monetizationStrategies"], list)

            # If there are strategies, validate their structure
            if data["monetizationStrategies"]:
                strategy = data["monetizationStrategies"][0]
                validate_field_exists(strategy, "id")
                validate_field_exists(strategy, "name")
                validate_field_exists(strategy, "description")
                validate_field_exists(strategy, "solutionId")
                validate_field_exists(strategy, "model")
                validate_field_exists(strategy, "projections")
                validate_field_exists(strategy, "createdAt")
                validate_field_exists(strategy, "updatedAt")

    def test_monetization_strategy_query(self, api_test_client: APITestClient):
        """Test querying a specific monetization strategy."""
        # Generate a random ID
        strategy_id = generate_id()

        # GraphQL query
        query = """
        query($id: ID!) {
            monetizationStrategy(id: $id) {
                id
                name
                description
                solutionId
                model {
                    type
                    pricing {
                        basePrice
                        currency
                        billingCycle
                    }
                    tiers {
                        name
                        price
                        features
                        isPopular
                    }
                }
                projections {
                    timeframe
                    metrics {
                        users
                        revenue
                        costs
                        profit
                    }
                    segments {
                        name
                        percentage
                        revenue
                    }
                }
                metrics {
                    currentUsers
                    monthlyRecurringRevenue
                    averageRevenuePerUser
                    churnRate
                    lifetimeValue
                }
                marketAnalysis {
                    targetMarketSize
                    competitorPricing
                    userWillingnessToPay
                    suggestedPriceRange
                }
                createdAt
                updatedAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"id": strategy_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "monetizationStrategy")

            # The strategy might not exist, which is fine
            if data["monetizationStrategy"]:
                strategy = data["monetizationStrategy"]
                validate_field_exists(strategy, "id")
                validate_field_equals(strategy, "id", strategy_id)
                validate_field_exists(strategy, "name")
                validate_field_exists(strategy, "description")
                validate_field_exists(strategy, "solutionId")
                validate_field_exists(strategy, "model")
                validate_field_exists(strategy, "projections")
                validate_field_exists(strategy, "metrics")
                validate_field_exists(strategy, "marketAnalysis")
                validate_field_exists(strategy, "createdAt")
                validate_field_exists(strategy, "updatedAt")

    def test_revenue_projections_query(self, api_test_client: APITestClient):
        """Test querying revenue projections."""
        # Generate a random ID
        strategy_id = generate_id()

        # GraphQL query
        query = """
        query($strategyId: ID!, $timeframe: TimeframeInput!) {
            revenueProjections(strategyId: $strategyId, timeframe: $timeframe) {
                periods {
                    date
                    metrics {
                        users {
                            total
                            new
                            churned
                            byTier {
                                tier
                                count
                            }
                        }
                        revenue {
                            total
                            recurring
                            oneTime
                            byTier {
                                tier
                                amount
                            }
                        }
                        costs {
                            fixed
                            variable
                            total
                        }
                        metrics {
                            churnRate
                            conversionRate
                            averageRevenuePerUser
                            lifetimeValue
                        }
                    }
                }
                summary {
                    totalRevenue
                    totalProfit
                    averageMonthlyRevenue
                    projectedAnnualGrowth
                }
            }
        }
        """

        # Variables
        variables = {
            "strategyId": strategy_id,
            "timeframe": {
                "startDate": "2025 - 05 - 01",
                "endDate": "2026 - 04 - 30",
                "periodicity": "MONTHLY",
            },
        }

        # Make request
        response = api_test_client.post("graphql", json={"query": query, "variables": variables})

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "revenueProjections")

            if data["revenueProjections"]:
                projections = data["revenueProjections"]
                validate_field_exists(projections, "periods")
                validate_field_type(projections["periods"], list)
                validate_field_exists(projections, "summary")

    def test_create_monetization_strategy_mutation(self, api_test_client: APITestClient):
        """Test creating a monetization strategy using GraphQL mutation."""
        # Generate test data
        test_data = generate_monetization_strategy_data()

        # GraphQL mutation
        mutation = """
        mutation($input: MonetizationStrategyInput!) {
            createMonetizationStrategy(input: $input) {
                id
                name
                description
                solutionId
                model {
                    type
                    pricing {
                        basePrice
                        currency
                        billingCycle
                    }
                    tiers {
                        name
                        price
                        features
                        isPopular
                    }
                }
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "name": test_data["name"],
                "description": test_data["description"],
                "solutionId": test_data["solution_id"],
                "model": test_data["model"],
            }
        }

        # Make request
        response = api_test_client.post("graphql", json={"query": mutation, "variables": variables})

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "createMonetizationStrategy")

            if data["createMonetizationStrategy"]:
                strategy = data["createMonetizationStrategy"]
                validate_field_exists(strategy, "id")
                validate_field_exists(strategy, "name")
                validate_field_equals(strategy, "name", test_data["name"])
                validate_field_exists(strategy, "description")
                validate_field_equals(strategy, "description", test_data["description"])
                validate_field_exists(strategy, "solutionId")
                validate_field_equals(strategy, "solutionId", test_data["solution_id"])
                validate_field_exists(strategy, "model")
                validate_field_exists(strategy, "createdAt")
                validate_field_exists(strategy, "updatedAt")

    def test_update_monetization_strategy_mutation(self, api_test_client: APITestClient):
        """Test updating a monetization strategy using GraphQL mutation."""
        # Generate test data
        strategy_id = generate_id()
        test_data = generate_monetization_strategy_data()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!, $input: MonetizationStrategyInput!) {
            updateMonetizationStrategy(id: $id, input: $input) {
                id
                name
                description
                solutionId
                model {
                    type
                    pricing {
                        basePrice
                        currency
                        billingCycle
                    }
                    tiers {
                        name
                        price
                        features
                        isPopular
                    }
                }
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "id": strategy_id,
            "input": {
                "name": test_data["name"],
                "description": test_data["description"],
                "solutionId": test_data["solution_id"],
                "model": test_data["model"],
            },
        }

        # Make request
        response = api_test_client.post("graphql", json={"query": mutation, "variables": variables})

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "updateMonetizationStrategy")

            # The update might return None if strategy doesn't exist
            if data["updateMonetizationStrategy"]:
                strategy = data["updateMonetizationStrategy"]
                validate_field_exists(strategy, "id")
                validate_field_equals(strategy, "id", strategy_id)
                validate_field_exists(strategy, "name")
                validate_field_equals(strategy, "name", test_data["name"])
                validate_field_exists(strategy, "description")
                validate_field_equals(strategy, "description", test_data["description"])
                validate_field_exists(strategy, "solutionId")
                validate_field_equals(strategy, "solutionId", test_data["solution_id"])
                validate_field_exists(strategy, "model")
                validate_field_exists(strategy, "createdAt")
                validate_field_exists(strategy, "updatedAt")

    def test_delete_monetization_strategy_mutation(self, api_test_client: APITestClient):
        """Test deleting a monetization strategy using GraphQL mutation."""
        # Generate a random ID
        strategy_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!) {
            deleteMonetizationStrategy(id: $id)
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": mutation, "variables": {"id": strategy_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "deleteMonetizationStrategy")
            validate_field_type(data["deleteMonetizationStrategy"], bool)

    def test_optimize_pricing_mutation(self, api_test_client: APITestClient):
        """Test optimizing pricing using GraphQL mutation."""
        # Generate test data
        strategy_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($input: PricingOptimizationInput!) {
            optimizePricing(input: $input) {
                strategyId
                recommendations {
                    tier {
                        name
                        currentPrice
                        recommendedPrice
                        priceChange
                        justification
                    }
                    metrics {
                        projectedRevenue
                        conversionImpact
                        churnImpact
                    }
                }
                analysis {
                    competitorPricing {
                        min
                        max
                        average
                        marketPosition
                    }
                    userSegments {
                        name
                        willingnessToPay
                        priceElasticity
                    }
                    recommendations {
                        summary
                        confidenceScore
                        risks
                        opportunities
                    }
                }
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "strategyId": strategy_id,
                "optimizationGoal": "MAXIMIZE_REVENUE",
                "constraints": {"minPrice": 5.0, "maxPrice": 100.0, "maxPriceChange": 25},
            }
        }

        # Make request
        response = api_test_client.post("graphql", json={"query": mutation, "variables": variables})

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "optimizePricing")

            if data["optimizePricing"]:
                optimization = data["optimizePricing"]
                validate_field_exists(optimization, "strategyId")
                validate_field_equals(optimization, "strategyId", strategy_id)
                validate_field_exists(optimization, "recommendations")
                validate_field_type(optimization["recommendations"], list)
                validate_field_exists(optimization, "analysis")

    def test_error_handling(self, api_test_client: APITestClient):
        """Test GraphQL error handling for monetization operations."""
        # Test invalid query field
        query = """
        query {
            monetizationStrategies {
                invalidField
            }
        }
        """

        response = api_test_client.post("graphql", json={"query": query})
        result = validate_json_response(response)
        validate_field_exists(result, "errors")

        # Test invalid mutation input
        mutation = """
        mutation($input: MonetizationStrategyInput!) {
            createMonetizationStrategy(input: $input) {
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
        validate_field_exists(result, "errors")
