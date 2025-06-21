"""Tests for ui.app Flask application."""

import pytest
import os
from ui.app import create_app

import pytest
import os
from ui.app import create_app

@pytest.fixture
def client():
    # Reset per-test action store
    app = create_app()
    if hasattr(app, "_action_store"):
        app._action_store.reset()  # type: ignore
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json == {"status": "ok"}

import pytest

@pytest.mark.parametrize("origin_list", [
    "http://localhost:3000",
    "http://localhost:3000,https://foo.com",
    "https://mydomain.com,http://localhost:3000",
])
def test_cors_headers(client, monkeypatch, origin_list):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", origin_list)
    # Recreate app with new CORS origins
    app = create_app()
    app.config['TESTING'] = True
    test_client = app.test_client()
    for origin in [o.strip() for o in origin_list.split(",") if o.strip()]:
        resp = test_client.options("/api/agent/action", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        })
        assert resp.status_code == 200
        assert resp.headers.get("Access-Control-Allow-Origin") == origin

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