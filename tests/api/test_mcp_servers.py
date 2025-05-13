import os
import json
import tempfile
import shutil

import pytest
from flask import Flask

from app_flask.mcp_servers import mcp_servers_api, MCP_SETTINGS_FILE, MCP_SERVERS_KEY

@pytest.fixture
def isolated_settings_file(monkeypatch):
    # Backup original settings file if present
    orig = MCP_SETTINGS_FILE
    tmp_dir = tempfile.mkdtemp()
    test_file = os.path.join(tmp_dir, "test_cline_mcp_settings.json")
    monkeypatch.setattr("app_flask.mcp_servers.MCP_SETTINGS_FILE", test_file)
    yield test_file
    shutil.rmtree(tmp_dir)
    # Do not restore original so test is isolated

@pytest.fixture
def app(isolated_settings_file):
    app = Flask(__name__)
    app.register_blueprint(mcp_servers_api)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_mcp_server_lifecycle(client):
    # List should be empty
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == 200
    assert rv.json == []

    # Add a new MCP server
    data = {
        "name": "test-server",
        "host": "localhost",
        "port": 9876,
        "description": "test desc"
    }
    rv = client.post("/api/mcp_servers/", json=data)
    assert rv.status_code == 201
    assert rv.json["status"] == "added"
    assert rv.json["server"]["name"] == "test-server"

    # List should show the server
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == 200
    servers = rv.json
    assert any(s["name"] == "test-server" for s in servers)

    # Add duplicate should fail
    rv = client.post("/api/mcp_servers/", json=data)
    assert rv.status_code == 409

    # Remove the server
    rv = client.delete("/api/mcp_servers/test-server")
    assert rv.status_code == 200
    assert rv.json["status"] == "deleted"

    # Remove non-existent server
    rv = client.delete("/api/mcp_servers/nonexistent")
    assert rv.status_code == 404

    # List should be empty again
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == 200
    assert rv.json == []