"""
Tests for the Agent Team GraphQL API.

This module contains tests for Agent Team GraphQL queries and mutations.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_agent_team_data, generate_id
from tests.api.utils.test_validators import (
    validate_field_equals,
    validate_field_exists,
    validate_field_not_empty,
    validate_field_type,
    validate_json_response,
)


class TestAgentTeamGraphQLAPI:
    """Tests for the Agent Team GraphQL API."""

    def test_agent_teams_query(self, api_test_client: APITestClient):
        """Test querying agent teams."""
        # GraphQL query
        query = """
        query {
            agentTeams {
                id
                name
                description
                agents {
                    id
                    name
                    role
                    modelId
                    capabilities
                }
                workflowSettings {
                    parallelExecution
                    reviewSteps
                    autoCorrection
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
            validate_field_exists(data, "agentTeams")
            validate_field_type(data["agentTeams"], list)

            # If there are teams, validate their structure
            if data["agentTeams"]:
                team = data["agentTeams"][0]
                validate_field_exists(team, "id")
                validate_field_exists(team, "name")
                validate_field_exists(team, "description")
                validate_field_exists(team, "agents")
                validate_field_type(team["agents"], list)
                validate_field_exists(team, "workflowSettings")
                validate_field_exists(team, "createdAt")
                validate_field_exists(team, "updatedAt")

    def test_agent_team_query(self, api_test_client: APITestClient):
        """Test querying a specific agent team."""
        # Generate a random ID
        team_id = generate_id()

        # GraphQL query
        query = """
        query($id: ID!) {
            agentTeam(id: $id) {
                id
                name
                description
                agents {
                    id
                    name
                    role
                    modelId
                    capabilities
                }
                workflowSettings {
                    parallelExecution
                    reviewSteps
                    autoCorrection
                }
                metrics {
                    completedTasks
                    successRate
                    averageResponseTime
                    activeAgents
                }
                createdAt
                updatedAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"id": team_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "agentTeam")

            # The team might not exist, which is fine
            if data["agentTeam"]:
                team = data["agentTeam"]
                validate_field_exists(team, "id")
                validate_field_equals(team, "id", team_id)
                validate_field_exists(team, "name")
                validate_field_exists(team, "description")
                validate_field_exists(team, "agents")
                validate_field_type(team["agents"], list)
                validate_field_exists(team, "workflowSettings")
                validate_field_exists(team, "metrics")
                validate_field_exists(team, "createdAt")
                validate_field_exists(team, "updatedAt")

    def test_agent_conversations_query(self, api_test_client: APITestClient):
        """Test querying agent conversations."""
        # Generate a random ID
        team_id = generate_id()

        # GraphQL query
        query = """
        query($teamId: ID!) {
            agentConversations(teamId: $teamId) {
                id
                teamId
                agents {
                    id
                    name
                    role
                }
                messages {
                    id
                    agentId
                    content
                    type
                    timestamp
                }
                status
                startedAt
                completedAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": query, "variables": {"teamId": team_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "agentConversations")
            validate_field_type(data["agentConversations"], list)

            # If there are conversations, validate their structure
            if data["agentConversations"]:
                conversation = data["agentConversations"][0]
                validate_field_exists(conversation, "id")
                validate_field_exists(conversation, "teamId")
                validate_field_exists(conversation, "agents")
                validate_field_type(conversation["agents"], list)
                validate_field_exists(conversation, "messages")
                validate_field_type(conversation["messages"], list)
                validate_field_exists(conversation, "status")
                validate_field_exists(conversation, "startedAt")
                validate_field_exists(conversation, "completedAt")

    def test_create_agent_team_mutation(self, api_test_client: APITestClient):
        """Test creating an agent team using GraphQL mutation."""
        # Generate test data
        test_data = generate_agent_team_data()

        # GraphQL mutation
        mutation = """
        mutation($input: AgentTeamInput!) {
            createAgentTeam(input: $input) {
                id
                name
                description
                agents {
                    id
                    name
                    role
                    modelId
                    capabilities
                }
                workflowSettings {
                    parallelExecution
                    reviewSteps
                    autoCorrection
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
                "agents": test_data["agents"],
                "workflowSettings": test_data["workflow_settings"],
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
            validate_field_exists(data, "createAgentTeam")

            if data["createAgentTeam"]:
                team = data["createAgentTeam"]
                validate_field_exists(team, "id")
                validate_field_exists(team, "name")
                validate_field_equals(team, "name", test_data["name"])
                validate_field_exists(team, "description")
                validate_field_equals(team, "description", test_data["description"])
                validate_field_exists(team, "agents")
                validate_field_type(team["agents"], list)
                validate_field_exists(team, "workflowSettings")
                validate_field_exists(team, "createdAt")
                validate_field_exists(team, "updatedAt")

    def test_update_agent_team_mutation(self, api_test_client: APITestClient):
        """Test updating an agent team using GraphQL mutation."""
        # Generate test data
        team_id = generate_id()
        test_data = generate_agent_team_data()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!, $input: AgentTeamInput!) {
            updateAgentTeam(id: $id, input: $input) {
                id
                name
                description
                agents {
                    id
                    name
                    role
                    modelId
                    capabilities
                }
                workflowSettings {
                    parallelExecution
                    reviewSteps
                    autoCorrection
                }
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "id": team_id,
            "input": {
                "name": test_data["name"],
                "description": test_data["description"],
                "agents": test_data["agents"],
                "workflowSettings": test_data["workflow_settings"],
            },
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
            validate_field_exists(data, "updateAgentTeam")

            # The update might return None if team doesn't exist
            if data["updateAgentTeam"]:
                team = data["updateAgentTeam"]
                validate_field_exists(team, "id")
                validate_field_equals(team, "id", team_id)
                validate_field_exists(team, "name")
                validate_field_equals(team, "name", test_data["name"])
                validate_field_exists(team, "description")
                validate_field_equals(team, "description", test_data["description"])
                validate_field_exists(team, "agents")
                validate_field_type(team["agents"], list)
                validate_field_exists(team, "workflowSettings")
                validate_field_exists(team, "createdAt")
                validate_field_exists(team, "updatedAt")

    def test_delete_agent_team_mutation(self, api_test_client: APITestClient):
        """Test deleting an agent team using GraphQL mutation."""
        # Generate a random ID
        team_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!) {
            deleteAgentTeam(id: $id)
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql", json={"query": mutation, "variables": {"id": team_id}}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "deleteAgentTeam")
            validate_field_type(data["deleteAgentTeam"], bool)

    def test_agent_task_mutation(self, api_test_client: APITestClient):
        """Test running an agent task using GraphQL mutation."""
        # Generate test data
        team_id = generate_id()
        agent_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($input: AgentTaskInput!) {
            runAgentTask(input: $input) {
                taskId
                agentId
                teamId
                status
                result {
                    output
                    metadata
                    timestamp
                }
                metrics {
                    startTime
                    completionTime
                    processingTime
                    tokens {
                        input
                        output
                        total
                    }
                }
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "teamId": team_id,
                "agentId": agent_id,
                "task": {
                    "type": "analyze_niche",
                    "parameters": {
                        "marketSegment": "e - commerce",
                        "targetAudience": "small businesses",
                    },
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
            validate_field_exists(data, "runAgentTask")

            if data["runAgentTask"]:
                task = data["runAgentTask"]
                validate_field_exists(task, "taskId")
                validate_field_exists(task, "agentId")
                validate_field_equals(task, "agentId", agent_id)
                validate_field_exists(task, "teamId")
                validate_field_equals(task, "teamId", team_id)
                validate_field_exists(task, "status")
                validate_field_exists(task, "result")
                validate_field_exists(task, "metrics")

    def test_error_handling(self, api_test_client: APITestClient):
        """Test GraphQL error handling for agent team operations."""
        # Test invalid query field
        query = """
        query {
            agentTeams {
                invalidField
            }
        }
        """

        response = api_test_client.post("graphql", json={"query": query})
        result = validate_json_response(response)
        validate_field_exists(result, "errors")

        # Test invalid mutation input
        mutation = """
        mutation($input: AgentTeamInput!) {
            createAgentTeam(input: $input) {
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
                        "description": "Invalid team"
                    }
                },
            },
        )
        result = validate_json_response(response)
        validate_field_exists(result, "errors")
