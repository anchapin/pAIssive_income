import os
import os
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Fetch the API key from the environment, using the dummy test value as a fallback
# This makes local/dev testing easier, but CI should set the real value.
api_key = os.environ.get("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")


def test_tool_endpoint():
    response = client.post(
        "/tools/some_tool",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"input": "test"}
    )
    assert response.status_code == 200
    assert response.json()["result"] == "expected_result"
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

# Use TOOL_API_KEY from environment for consistency and security.
TOOL_API_KEY = os.getenv("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")
HEADERS = {"x-api-key": TOOL_API_KEY}

def test_add_success():
    resp = client.post("/tools/add", json={"a": 2, "b": 3}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"result": 5}

def test_subtract_success():
    resp = client.post("/tools/subtract", json={"a": 8, "b": 2}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"result": 6}

def test_multiply_success():
    resp = client.post("/tools/multiply", json={"a": 1.5, "b": 4}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"result": 6.0}

def test_divide_success():
    resp = client.post("/tools/divide", json={"a": 9, "b": 3}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"result": 3.0}

def test_divide_by_zero():
    resp = client.post("/tools/divide", json={"a": 1, "b": 0}, headers=HEADERS)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot divide by zero"

def test_average_success():
    resp = client.post("/tools/average", json={"numbers": [1, 2, 3]}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"result": 2.0}

def test_average_empty_list():
    resp = client.post("/tools/average", json={"numbers": []}, headers=HEADERS)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot calculate average of empty list"

@pytest.mark.parametrize("endpoint,payload", [
    ("/tools/add", {"a": 2}),  # missing b
    ("/tools/subtract", {"a": 2}),
    ("/tools/multiply", {"b": 2}),
    ("/tools/divide", {}),
    ("/tools/average", {}),
])
def test_invalid_input(endpoint, payload):
    resp = client.post(endpoint, json=payload, headers=HEADERS)
    assert resp.status_code == 422  # Unprocessable Entity

@pytest.mark.parametrize("headers", [
    {},  # missing API key
    {"x-api-key": "wrongkey"},
    {"x-api-key": ""},
])
def test_authentication_required(headers):
    resp = client.post("/tools/add", json={"a": 1, "b": 2}, headers=headers)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or missing API key"

def test_audit_logging_and_auth_failures(caplog):
    # Successful call
    with caplog.at_level("INFO"):
        client.post("/tools/add", json={"a": 2, "b": 3}, headers=HEADERS)
        assert any("tool=add" in msg for msg in caplog.text.splitlines())
    # Auth failure
    with caplog.at_level("INFO"):
        client.post("/tools/add", json={"a": 2, "b": 3}, headers={"x-api-key": "bad"})
        assert any("[AUTH FAIL]" in msg for msg in caplog.text.splitlines())