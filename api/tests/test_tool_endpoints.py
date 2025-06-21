"""Tests for REST math tool endpoints."""

import os

import pytest
from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)

API_KEY_HEADER = {"x-api-key": os.getenv("TOOL_API_KEY", "test-api-key-for-ci")}


@pytest.fixture(autouse=True)
def set_tool_api_key(monkeypatch):
    """Fixture to set TOOL_API_KEY environment variable for tests."""
    monkeypatch.setenv("TOOL_API_KEY", "test-api-key-for-ci")

def test_add_success() -> None:
    """Test /tools/add happy path."""
    resp = client.post("/tools/add", headers=API_KEY_HEADER, json={"a": 1, "b": 2})
    assert resp.status_code == 200
    assert resp.json() == {"result": 3}


def test_divide_by_zero() -> None:
    """Test /tools/divide error on divide by zero."""
    resp = client.post("/tools/divide", headers=API_KEY_HEADER, json={"a": 1, "b": 0})
    assert resp.status_code == 400
    assert resp.json()["message"] == "Cannot divide by zero"
    assert resp.json()["code"] == 400


def test_average_empty_list() -> None:
    """Test /tools/average error on empty list."""
    resp = client.post("/tools/average", headers=API_KEY_HEADER, json={"numbers": []})
    assert resp.status_code == 400
    assert resp.json()["message"] == "Cannot calculate average of empty list"
    assert resp.json()["code"] == 400


@pytest.mark.parametrize(
    "headers,expected_code",
    [
        ({}, 401),
        ({"x-api-key": "wrong"}, 401),
    ],
)
def test_api_key_auth_failure(headers, expected_code) -> None:
    """Test /tools/add authentication failure (missing/invalid key)."""
    resp = client.post("/tools/add", headers=headers, json={"a": 1, "b": 2})
    assert resp.status_code == expected_code
    assert resp.json()["message"] == "Invalid or missing API key"
    assert resp.json()["code"] == 401
