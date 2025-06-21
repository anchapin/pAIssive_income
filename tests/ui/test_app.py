"""Tests for ui.app Flask application."""

import pytest
from flask import Flask
from ui.app import create_app

@pytest.fixture(name="app")
def fixture_app() -> Flask:
    """Flask app fixture."""
    return create_app()

@pytest.fixture(name="client")
def fixture_client(app: Flask):
    """Flask client fixture."""
    return app.test_client()

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"status": "ok"}
    # CORS header present
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"

def test_get_agent(client):
    resp = client.get("/api/agent")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "id" in body and "name" in body

def test_agent_action_success(client):
    sample = {
        "type": "do-something",
        "agentId": "test-agent",
        "payload": {"foo": "bar"},
    }
    resp = client.post("/api/agent/action", json=sample)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert isinstance(body["action_id"], int)

def test_agent_action_id_increments(client):
    # Post two actions, ids should increment
    resp1 = client.post("/api/agent/action", json={"type": "a"})
    resp2 = client.post("/api/agent/action", json={"type": "b"})
    id1 = resp1.get_json()["action_id"]
    id2 = resp2.get_json()["action_id"]
    assert id2 == id1 + 1

def test_agent_action_invalid_json(client):
    # Send text/plain, which should not parse as JSON
    resp = client.post(
        "/api/agent/action", data="not json", content_type="text/plain"
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"] == "Invalid JSON"

def test_agent_action_missing_type(client):
    # JSON but missing 'type'
    resp = client.post("/api/agent/action", json={"foo": "bar"})
    assert resp.status_code == 400
    body = resp.get_json()
    assert "type" in body["error"]
