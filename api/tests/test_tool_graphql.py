"""Tests for GraphQL math tool endpoints."""

import os

import pytest
from fastapi.testclient import TestClient
import requests

from api.app import app

client = TestClient(app)

API_KEY_HEADER = {"x-api-key": os.getenv("TOOL_API_KEY", "test-api-key-for-ci")}

@pytest.fixture(autouse=True)
def set_tool_api_key(monkeypatch):
    """Fixture to set TOOL_API_KEY environment variable for tests."""
    monkeypatch.setenv("TOOL_API_KEY", "test-api-key-for-ci")

def graphql_query(query: str, variables: dict | None = None) -> requests.Response:
    """
    Helper to POST a GraphQL query and return the Response object.

    Args:
        query (str): The GraphQL query string.
        variables (dict | None): Optional variables for the query.

    Returns:
        requests.Response: The HTTP response from the server.
    """
    resp = client.post(
        "/graphql",
        headers=API_KEY_HEADER,
        json={"query": query, "variables": variables or {}},
    )
    return resp


def test_graphql_add() -> None:
    """Test GraphQL add query."""
    query = """
    query {
        add(a: 1, b: 2)
    }
    """
    resp = graphql_query(query)
    assert resp.status_code == 200
    assert resp.json()["data"]["add"] == 3


def test_graphql_divide_by_zero() -> None:
    """Test GraphQL divide by zero error."""
    query = """
    query {
        divide(a: 10, b: 0)
    }
    """
    resp = graphql_query(query)
    # Strawberry returns error in "errors", not data
    body = resp.json()
    assert "errors" in body
    # Assert exact error message
    assert body["errors"][0]["message"] == "Cannot divide by zero"


def test_graphql_average_empty_list() -> None:
    """Test GraphQL average with empty list raises error."""
    query = """
    query {
        average(numbers: [])
    }
    """
    resp = graphql_query(query)
    body = resp.json()
    assert "errors" in body
    # Assert exact error message
    assert body["errors"][0]["message"] == "Cannot calculate average of empty list"


@pytest.mark.parametrize(
    "headers,expected_code",
    [
        ({}, 401),
        ({"x-api-key": "wrong"}, 401),
    ],
)
def test_graphql_auth_failure(headers, expected_code) -> None:
    """Test GraphQL authentication failure."""
    query = """
    query {
        add(a: 1, b: 2)
    }
    """
    resp = client.post("/graphql", headers=headers, json={"query": query})
    assert resp.status_code == expected_code
    assert resp.json()["message"] == "Invalid or missing API key"
    assert resp.json()["code"] == 401