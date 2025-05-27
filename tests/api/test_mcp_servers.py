import logging
import json
import os
import sys
import shutil
import tempfile
from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the blueprint
from app_flask.mcp_servers import mcp_servers_api


@pytest.fixture
def isolated_settings_file(monkeypatch):
    # Create a temporary directory for test files
    tmp_dir = tempfile.mkdtemp()
    test_file = Path(tmp_dir) / "test_cline_mcp_settings.json"

    # Create an empty settings file
    test_file.write_text("{}")

    # Patch the settings file path
    monkeypatch.setattr("app_flask.mcp_servers.MCP_SETTINGS_FILE", test_file)

    # Yield the test file path
    yield test_file

    # Clean up after the test
    shutil.rmtree(tmp_dir)


@pytest.fixture
def app(isolated_settings_file):
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


@patch('app_flask.mcp_servers.Path.exists')
@patch('app_flask.mcp_servers.Path.read_text')
@patch('app_flask.mcp_servers.Path.write_text')
def test_mcp_server_lifecycle(mock_write_text, mock_read_text, mock_exists, client):
    """Test the complete lifecycle of MCP server operations."""
    # Mock the settings file operations
    mock_exists.return_value = True

    # Initially empty settings
    mock_read_text.return_value = '{}'

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

    # Mock the settings file after adding a server
    mock_read_text.return_value = json.dumps({
        "test-server": {
            "name": "test-server",
            "host": "localhost",
            "port": 9876,
            "description": "test desc",
        }
    })

    rv = client.post("/api/mcp_servers/", json=data)
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json["status"] == "added"
    assert rv.json["server"]["name"] == "test-server"

    # List should show the server
    rv = client.get("/api/mcp_servers/")
    assert rv.status_code == HTTPStatus.OK
    servers = rv.json
    assert len(servers) == 1
    assert servers[0]["name"] == "test-server"

    # Add duplicate should fail
    mock_read_text.return_value = json.dumps({
        "test-server": {
            "name": "test-server",
            "host": "localhost",
            "port": 9876,
            "description": "test desc",
        }
    })

    rv = client.post("/api/mcp_servers/", json=data)
    assert rv.status_code == HTTPStatus.CONFLICT

    # Remove the server
    mock_read_text.return_value = '{}'

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


@patch('app_flask.mcp_servers.Path.exists')
@patch('app_flask.mcp_servers.Path.read_text')
def test_invalid_server_data(mock_read_text, mock_exists, client):
    """Test validation of server data."""
    # Mock the settings file operations
    mock_exists.return_value = True
    mock_read_text.return_value = '{}'

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


@patch('app_flask.mcp_servers.Path.exists')
@patch('app_flask.mcp_servers.Path.read_text')
def test_invalid_server_name_in_delete(mock_read_text, mock_exists, client):
    """Test validation of server name in delete operation."""
    # Mock the settings file operations
    mock_exists.return_value = True
    mock_read_text.return_value = '{}'

    # Test invalid server name format
    rv = client.delete("/api/mcp_servers/invalid;name")
    assert rv.status_code == HTTPStatus.BAD_REQUEST
