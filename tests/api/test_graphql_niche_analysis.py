"""
Tests for the Niche Analysis GraphQL API.

This module contains tests for Niche Analysis GraphQL queries and mutations.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id, generate_niche_analysis_data, generate_niche_data
from tests.api.utils.test_validators import (
    validate_field_equals,
    validate_field_exists,
    validate_field_not_empty,
    validate_field_type,
    validate_json_response,
)


class TestNicheAnalysisGraphQLAPI:
    """Tests for the Niche Analysis GraphQL API."""

    def test_market_segments_query(self, api_test_client: APITestClient):
        """Test querying market segments."""
        # GraphQL query
        query = """
        query {
            marketSegments {
                id
                name
                description
                potentialMarketSize
                growthRate
                competitionLevel
                technologicalAdoption
                targetUsers
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
            validate_field_exists(data, "marketSegments")
            validate_field_type(data["marketSegments"], list)

            # If there are segments, validate their structure
            if data["marketSegments"]:
                segment = data["marketSegments"][0]
                validate_field_exists(segment, "id")
                validate_field_exists(segment, "name")
                validate_field_exists(segment, "description")
                validate_field_exists(segment, "potentialMarketSize")
                validate_field_exists(segment, "growthRate")
                validate_field_exists(segment, "competitionLevel")
                validate_field_exists(segment, "technologicalAdoption")
                validate_field_exists(segment, "targetUsers")
                validate_field_type(segment["targetUsers"], list)

    def test_analyze_niches_mutation(self, api_test_client: APITestClient):
        """Test analyzing niches using GraphQL mutation."""
        # GraphQL mutation
        mutation = """
        mutation($input: AnalyzeNichesInput!) {
            analyzeNiches(input: $input) {
                id
                dateCreated
                segments {
                    id
                    name
                    description
                    opportunityScore
                }
                opportunities {
                    id
                    name
                    segmentId
                    segmentName
                    description
                    opportunityScore
                    competitionLevel
                    growthPotential
                }
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "segmentIds": [generate_id(), generate_id()],
                "analysisParameters": {
                    "minOpportunityScore": 0.7,
                    "considerTechnologicalTrends": True,
                    "focusOnAiApplications": True,
                },
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
            validate_field_exists(data, "analyzeNiches")

            if data["analyzeNiches"]:
                analysis = data["analyzeNiches"]
                validate_field_exists(analysis, "id")
                validate_field_exists(analysis, "dateCreated")
                validate_field_exists(analysis, "segments")
                validate_field_type(analysis["segments"], list)
                validate_field_exists(analysis, "opportunities")
                validate_field_type(analysis["opportunities"], list)

                # Validate segments if any
                if analysis["segments"]:
                    segment = analysis["segments"][0]
                    validate_field_exists(segment, "id")
                    validate_field_exists(segment, "name")
                    validate_field_exists(segment, "description")
                    validate_field_exists(segment, "opportunityScore")

                # Validate opportunities if any
                if analysis["opportunities"]:
                    opportunity = analysis["opportunities"][0]
                    validate_field_exists(opportunity, "id")
                    validate_field_exists(opportunity, "name")
                    validate_field_exists(opportunity, "segmentId")
                    validate_field_exists(opportunity, "segmentName")
                    validate_field_exists(opportunity, "description")
                    validate_field_exists(opportunity, "opportunityScore")
                    validate_field_exists(opportunity, "competitionLevel")
                    validate_field_exists(opportunity, "growthPotential")

    def test_niche_problems_query(self, api_test_client: APITestClient):
        """Test querying problems for a specific niche."""
        # Generate a random ID
        niche_id = generate_id()

        # GraphQL query
        query = """
        query($nicheId: ID!) {
            nicheProblems(nicheId: $nicheId) {
                id
                title
                description
                severity
                prevalence
                currentSolutions
                painPoints
                userImpact
                businessImpact
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"nicheId": niche_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "nicheProblems")
            validate_field_type(data["nicheProblems"], list)

            # If there are problems, validate their structure
            if data["nicheProblems"]:
                problem = data["nicheProblems"][0]
                validate_field_exists(problem, "id")
                validate_field_exists(problem, "title")
                validate_field_exists(problem, "description")
                validate_field_exists(problem, "severity")
                validate_field_exists(problem, "prevalence")
                validate_field_exists(problem, "currentSolutions")
                validate_field_exists(problem, "painPoints")
                validate_field_exists(problem, "userImpact")
                validate_field_exists(problem, "businessImpact")

    def test_opportunity_metrics_query(self, api_test_client: APITestClient):
        """Test querying opportunity metrics."""
        # Generate a random ID
        opportunity_id = generate_id()

        # GraphQL query
        query = """
        query($id: ID!) {
            opportunityMetrics(id: $id) {
                marketSize {
                    value
                    unit
                    source
                }
                growthRate {
                    value
                    timeframe
                }
                competition {
                    level
                    majorCompetitors {
                        name
                        marketShare
                        strengths
                    }
                }
                trends {
                    name
                    direction
                    impact
                }
                targetAudience {
                    demographics
                    size
                    growth
                }
                monetizationPotential {
                    models
                    estimatedRevenue {
                        min
                        max
                        unit
                        timeframe
                    }
                }
                resourceRequirements {
                    time {
                        value
                        unit
                    }
                    skills
                    initialInvestment {
                        value
                        currency
                    }
                }
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"id": opportunity_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "opportunityMetrics")

            # The metrics might be None if opportunity doesn't exist
            if data["opportunityMetrics"]:
                metrics = data["opportunityMetrics"]
                validate_field_exists(metrics, "marketSize")
                validate_field_exists(metrics, "growthRate")
                validate_field_exists(metrics, "competition")
                validate_field_exists(metrics, "trends")
                validate_field_exists(metrics, "targetAudience")
                validate_field_exists(metrics, "monetizationPotential")
                validate_field_exists(metrics, "resourceRequirements")

    def test_create_niche_analysis_mutation(self, api_test_client: APITestClient):
        """Test creating a niche analysis using GraphQL mutation."""
        # Generate test data
        test_data = generate_niche_analysis_data()

        # GraphQL mutation
        mutation = """
        mutation($input: NicheAnalysisInput!) {
            createNicheAnalysis(input: $input) {
                id
                name
                description
                marketSize
                growthRate
                competitionLevel
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
                "marketSize": test_data["market_size"],
                "growthRate": test_data["growth_rate"],
                "competitionLevel": test_data["competition_level"],
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
            validate_field_exists(data, "createNicheAnalysis")

            if data["createNicheAnalysis"]:
                niche = data["createNicheAnalysis"]
                validate_field_exists(niche, "id")
                validate_field_exists(niche, "name")
                validate_field_equals(niche, "name", test_data["name"])
                validate_field_exists(niche, "description")
                validate_field_equals(niche, "description", test_data["description"])
                validate_field_exists(niche, "marketSize")
                validate_field_equals(niche, "marketSize", test_data["market_size"])
                validate_field_exists(niche, "growthRate")
                validate_field_equals(niche, "growthRate", test_data["growth_rate"])
                validate_field_exists(niche, "competitionLevel")
                validate_field_equals(niche, "competitionLevel", test_data["competition_level"])
                validate_field_exists(niche, "createdAt")
                validate_field_exists(niche, "updatedAt")

    def test_update_niche_analysis_mutation(self, api_test_client: APITestClient):
        """Test updating a niche analysis using GraphQL mutation."""
        # Generate test data
        niche_id = generate_id()
        test_data = generate_niche_analysis_data()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!, $input: NicheInput!) {
            updateNiche(id: $id, input: $input) {
                id
                name
                description
                marketSize
                growthRate
                competitionLevel
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "id": niche_id,
            "input": {
                "name": test_data["name"],
                "description": test_data["description"],
                "marketSize": test_data["market_size"],
                "growthRate": test_data["growth_rate"],
                "competitionLevel": test_data["competition_level"],
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
            validate_field_exists(data, "updateNiche")

            # The update might return None if niche doesn't exist
            if data["updateNiche"]:
                niche = data["updateNiche"]
                validate_field_exists(niche, "id")
                validate_field_equals(niche, "id", niche_id)
                validate_field_exists(niche, "name")
                validate_field_equals(niche, "name", test_data["name"])
                validate_field_exists(niche, "description")
                validate_field_equals(niche, "description", test_data["description"])
                validate_field_exists(niche, "marketSize")
                validate_field_equals(niche, "marketSize", test_data["market_size"])
                validate_field_exists(niche, "growthRate")
                validate_field_equals(niche, "growthRate", test_data["growth_rate"])
                validate_field_exists(niche, "competitionLevel")
                validate_field_equals(niche, "competitionLevel", test_data["competition_level"])
                validate_field_exists(niche, "createdAt")
                validate_field_exists(niche, "updatedAt")

    def test_delete_niche_mutation(self, api_test_client: APITestClient):
        """Test deleting a niche using GraphQL mutation."""
        # Generate a random ID
        niche_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!) {
            deleteNiche(id: $id)
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": mutation, "variables": {"id": niche_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "deleteNiche")
            validate_field_type(data["deleteNiche"], bool)

    def test_compare_opportunities_query(self, api_test_client: APITestClient):
        """Test comparing opportunities using GraphQL."""
        # Generate random IDs
        opportunity_ids = [generate_id(), generate_id()]

        # GraphQL query
        query = """
        query($ids: [ID!]!) {
            compareOpportunities(ids: $ids) {
                opportunities {
                    id
                    name
                    score
                    metrics {
                        marketSize {
                            value
                            unit
                        }
                        growthRate {
                            value
                            timeframe
                        }
                        competition {
                            level
                        }
                    }
                }
                comparison {
                    scoreDifference
                    marketSizeDifference
                    growthRateDifference
                    recommendation
                }
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"ids": opportunity_ids}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "compareOpportunities")

            if data["compareOpportunities"]:
                comparison = data["compareOpportunities"]
                validate_field_exists(comparison, "opportunities")
                validate_field_type(comparison["opportunities"], list)
                validate_field_exists(comparison, "comparison")

    def test_error_handling(self, api_test_client: APITestClient):
        """Test GraphQL error handling for niche analysis."""
        # Test invalid query field
        query = """
        query {
            marketSegments {
                invalidField
            }
        }
        """

        response = api_test_client.post("graphql", json={"query": query})
        result = validate_json_response(response)
        validate_field_exists(result, "errors")

        # Test invalid mutation input
        mutation = """
        mutation($input: NicheAnalysisInput!) {
            createNicheAnalysis(input: $input) {
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
                        "description": "Invalid analysis"
                    }
                },
            },
        )
        result = validate_json_response(response)
        validate_field_exists(result, "errors")
