import shutil
import tempfile
from http import HTTPStatus
from pathlib import Path

import pytest
from flask import Flask

from app_flask.mcp_servers import mcp_servers_api


@pytest.fixture
def isolated_settings_file(monkeypatch):
    # Create a temporary directory for test files
    tmp_dir = tempfile.mkdtemp()
    test_file = Path(tmp_dir) / "test_cline_mcp_settings.json"

    # Patch the settings file path
    monkeypatch.setattr("app_flask.mcp_servers.MCP_SETTINGS_FILE", test_file)

    # Yield the test file path
    yield test_file

    # Clean up after the test
    shutil.rmtree(tmp_dir)


@pytest.fixture
def app(_: Path):  # Renamed from isolated_settings_file to _ to indicate unused
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    app.register_blueprint(mcp_servers_api)

    # Create a test context
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_mcp_server_lifecycle(client):
    """Test the complete lifecycle of MCP server operations."""
    # List should be empty initially
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == HTTPStatus.OK
    assert rv.json == []

    # Add a new MCP server
    data = {
        "name": "test-server",
        "host": "localhost",
        "port": 9876,
        "description": "test desc",
    }
    rv = client.post("/api/mcp_servers/", json=data)
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json["status"] == "added"
    assert rv.json["server"]["name"] == "test-server"

    # List should show the server
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == HTTPStatus.OK
    servers = rv.json
    assert any(s["name"] == "test-server" for s in servers)

    # Add duplicate should fail
    rv = client.post("/api/mcp_servers/", json=data)
    assert rv.status_code == HTTPStatus.CONFLICT

    # Remove the server
    rv = client.delete("/api/mcp_servers/test-server")
    assert rv.status_code == HTTPStatus.OK
    assert rv.json["status"] == "deleted"

    # Remove non-existent server
    rv = client.delete("/api/mcp_servers/nonexistent")
    assert rv.status_code == HTTPStatus.NOT_FOUND

    # List should be empty again
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == HTTPStatus.OK
    assert rv.json == []


def test_invalid_server_data(client):
    """Test validation of server data."""
    # Test missing required fields
    rv = client.post("/api/mcp_servers/", json={"name": "test-server"})
    assert rv.status_code == HTTPStatus.BAD_REQUEST

    # Test invalid server name
    rv = client.post(
        "/api/mcp_servers/",
        json={
            "name": "test server!",  # Contains space and special char
            "host": "localhost",
            "port": 9876,
        },
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST

    # Test invalid host
    rv = client.post(
        "/api/mcp_servers/",
        json={
            "name": "test-server",
            "host": "local;host",  # Contains semicolon
            "port": 9876,
        },
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST

    # Test invalid port (string)
    rv = client.post(
        "/api/mcp_servers/",
        json={"name": "test-server", "host": "localhost", "port": "not-a-number"},
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST

    # Test invalid port (out of range)
    rv = client.post(
        "/api/mcp_servers/",
        json={"name": "test-server", "host": "localhost", "port": 70000},
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_invalid_server_name_in_delete(client):
    """Test validation of server name in delete operation."""
    # Test invalid server name format
    rv = client.delete("/api/mcp_servers/invalid;name")
    assert rv.status_code == HTTPStatus.BAD_REQUEST
