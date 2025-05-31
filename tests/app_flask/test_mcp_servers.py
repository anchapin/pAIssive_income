"""Tests for the app_flask/mcp_servers.py module."""

import json
import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from flask import Flask

from app_flask import create_app
from app_flask.mcp_servers import (
    MCP_SERVERS_KEY,
    MCP_SETTINGS_FILE,
    InvalidDataTypeError,
    load_settings,
    mcp_servers_api,
    save_settings,
    validate_server_data,
)


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(mcp_servers_api, url_prefix="/api/mcp-servers")
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def mock_settings_file():
    """Create a temporary settings file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        json.dump({MCP_SERVERS_KEY: []}, f)
        temp_file = f.name

    yield temp_file

    # Clean up
    os.unlink(temp_file)


class TestMCPServersAPI:
    """Test cases for the MCP Servers API."""

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_load_settings_success(self, mock_path):
        """Test loading settings successfully."""
        # Create mock data
        mock_data = {MCP_SERVERS_KEY: [{"name": "test", "host": "localhost", "port": 8000}]}

        # Set up the mock
        mock_path.open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        mock_path.stat.return_value.st_size = 100  # Small file size

        # Call the function
        result = load_settings()

        # Verify the result
        assert result == mock_data
        assert MCP_SERVERS_KEY in result
        assert len(result[MCP_SERVERS_KEY]) == 1
        assert result[MCP_SERVERS_KEY][0]["name"] == "test"

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_load_settings_file_too_large(self, mock_path):
        """Test loading settings when the file is too large."""
        # Set up the mock
        mock_path.stat.return_value.st_size = 2 * 1024 * 1024  # 2MB (too large)

        # Call the function
        result = load_settings()

        # Verify the result
        assert result == {MCP_SERVERS_KEY: []}
        assert mock_path.open.call_count == 0  # File should not be opened

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_load_settings_invalid_json(self, mock_path):
        """Test loading settings with invalid JSON."""
        # Set up the mock
        mock_path.stat.return_value.st_size = 100  # Small file size
        mock_path.open.return_value.__enter__.return_value.read.return_value = "invalid json"

        # Call the function
        result = load_settings()

        # Verify the result
        assert result == {MCP_SERVERS_KEY: []}

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_load_settings_missing_key(self, mock_path):
        """Test loading settings with missing MCP_SERVERS_KEY."""
        # Create mock data without the key
        mock_data = {"other_key": "value"}

        # Set up the mock
        mock_path.stat.return_value.st_size = 100  # Small file size
        mock_path.open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)

        # Call the function
        result = load_settings()

        # Verify the result
        assert result[MCP_SERVERS_KEY] == []
        assert "other_key" in result
        assert result["other_key"] == "value"

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_save_settings_success(self, mock_path):
        """Test saving settings successfully."""
        # Create mock data
        mock_data = {MCP_SERVERS_KEY: [{"name": "test", "host": "localhost", "port": 8000}]}

        # Set up the mock for the temp file
        mock_temp_file = MagicMock()
        mock_path.with_suffix.return_value = mock_temp_file

        # Mock the open context manager
        mock_file = MagicMock()
        mock_open_context = MagicMock()
        mock_open_context.__enter__.return_value = mock_file
        mock_temp_file.open.return_value = mock_open_context

        # Use a more comprehensive approach by patching all necessary components
        with patch("app_flask.mcp_servers.os.fsync") as mock_fsync:
            with patch("json.dump") as mock_json_dump:
                # Call the function
                save_settings(mock_data)

                # Verify the result
                mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
                mock_temp_file.open.assert_called_once_with("w", encoding="utf-8")
                mock_json_dump.assert_called_once_with(mock_data, mock_file, indent=2)
                mock_file.flush.assert_called_once()
                mock_fsync.assert_called_once()
                mock_temp_file.chmod.assert_called_once_with(stat.S_IRUSR | stat.S_IWUSR)
                mock_temp_file.replace.assert_called_once_with(mock_path)

    def test_validate_server_valid(self):
        """Test validating a valid server configuration."""
        # Create a valid server configuration
        server = {
            "name": "test-server",
            "host": "localhost",
            "port": 8000,
            "description": "A test server"
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is None  # No error message

    def test_validate_server_missing_name(self):
        """Test validating a server configuration with missing name."""
        # Create an invalid server configuration
        server = {
            "host": "localhost",
            "port": 8000
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "name" in result[0]
        assert result[1] == 400

    def test_validate_server_missing_host(self):
        """Test validating a server configuration with missing host."""
        # Create an invalid server configuration
        server = {
            "name": "test-server",
            "port": 8000
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "host" in result[0]  # The error message contains "Missing required field: host"
        assert result[1] == 400

    def test_validate_server_missing_port(self):
        """Test validating a server configuration with missing port."""
        # Create an invalid server configuration
        server = {
            "name": "test-server",
            "host": "localhost"
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "port" in result[0]
        assert result[1] == 400

    def test_validate_server_invalid_name(self):
        """Test validating a server configuration with invalid name."""
        # Create an invalid server configuration
        server = {
            "name": "test server with spaces",
            "host": "localhost",
            "port": 8000
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "name" in result[0]
        assert result[1] == 400

    def test_validate_server_invalid_host(self):
        """Test validating a server configuration with invalid host."""
        # Create an invalid server configuration
        server = {
            "name": "test-server",
            "host": "localhost;rm -rf /",  # Injection attempt
            "port": 8000
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "Host" in result[0]  # Changed from "host" to "Host" to match the actual error message
        assert result[1] == 400

    def test_validate_server_invalid_port_range(self):
        """Test validating a server configuration with invalid port range."""
        # Create an invalid server configuration
        server = {
            "name": "test-server",
            "host": "localhost",
            "port": 70000  # Port out of range
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "Port" in result[0]
        assert result[1] == 400

    def test_validate_server_invalid_port_type(self):
        """Test validating a server configuration with invalid port type."""
        # Create an invalid server configuration
        server = {
            "name": "test-server",
            "host": "localhost",
            "port": "not-a-number"
        }

        # Call the function
        result = validate_server_data(server)

        # Verify the result
        assert result is not None
        assert "Port" in result[0]
        assert result[1] == 400

    @patch("app_flask.mcp_servers.load_settings")
    def test_list_mcp_servers(self, mock_load_settings, client):
        """Test listing MCP servers."""
        # Create mock data
        mock_servers = [
            {"name": "server1", "host": "localhost", "port": 8000},
            {"name": "server2", "host": "example.com", "port": 9000}
        ]
        mock_load_settings.return_value = {MCP_SERVERS_KEY: mock_servers}

        # Make the request
        response = client.get("/api/mcp-servers/")

        # Verify the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]["name"] == "server1"
        assert data[1]["name"] == "server2"

    @patch("app_flask.mcp_servers.load_settings")
    @patch("app_flask.mcp_servers.save_settings")
    def test_add_mcp_server_success(self, mock_save_settings, mock_load_settings, client):
        """Test adding a new MCP server successfully."""
        # Create mock data
        mock_load_settings.return_value = {MCP_SERVERS_KEY: []}

        # Create server data to add
        server_data = {
            "name": "test-server",
            "host": "localhost",
            "port": 8000,
            "description": "Test server"
        }

        # Make the request
        response = client.post(
            "/api/mcp-servers/",
            data=json.dumps(server_data),
            content_type="application/json"
        )

        # Verify the response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "added"
        assert data["server"]["name"] == "test-server"
        assert data["server"]["host"] == "localhost"
        assert data["server"]["port"] == 8000
        assert data["server"]["description"] == "Test server"

        # Verify save_settings was called with the correct data
        mock_save_settings.assert_called_once()
        # Extract the first positional argument from the call
        actual_data = mock_save_settings.call_args[0][0]
        assert MCP_SERVERS_KEY in actual_data
        assert len(actual_data[MCP_SERVERS_KEY]) == 1
        assert actual_data[MCP_SERVERS_KEY][0]["name"] == server_data["name"]
        assert actual_data[MCP_SERVERS_KEY][0]["host"] == server_data["host"]
        assert actual_data[MCP_SERVERS_KEY][0]["port"] == server_data["port"]

    @patch("app_flask.mcp_servers.load_settings")
    @patch("app_flask.mcp_servers.save_settings")
    def test_add_mcp_server_duplicate(self, mock_save_settings, mock_load_settings, client):
        """Test adding a duplicate MCP server."""
        # Create mock data with an existing server
        existing_server = {"name": "test-server", "host": "localhost", "port": 8000}
        mock_load_settings.return_value = {MCP_SERVERS_KEY: [existing_server]}

        # Create server data with the same name
        server_data = {
            "name": "test-server",  # Same name as existing server
            "host": "example.com",
            "port": 9000
        }

        # Make the request
        response = client.post(
            "/api/mcp-servers/",
            data=json.dumps(server_data),
            content_type="application/json"
        )

        # Verify the response
        assert response.status_code == 409
        data = json.loads(response.data)
        assert "error" in data
        assert "already exists" in data["error"]

        # Verify save_settings was not called
        mock_save_settings.assert_not_called()

    @patch("app_flask.mcp_servers.load_settings")
    def test_add_mcp_server_invalid_data(self, mock_load_settings, client):
        """Test adding an MCP server with invalid data."""
        # Create mock data
        mock_load_settings.return_value = {MCP_SERVERS_KEY: []}

        # Create invalid server data (missing required fields)
        server_data = {
            "name": "test-server",
            # Missing host and port
        }

        # Make the request
        response = client.post(
            "/api/mcp-servers/",
            data=json.dumps(server_data),
            content_type="application/json"
        )

        # Verify the response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "host" in data["error"]  # Error message should mention missing host

    @patch("app_flask.mcp_servers.load_settings")
    @patch("app_flask.mcp_servers.save_settings")
    def test_delete_mcp_server_success(self, mock_save_settings, mock_load_settings, client):
        """Test deleting an MCP server successfully."""
        # Create mock data with an existing server
        existing_server = {"name": "test-server", "host": "localhost", "port": 8000}
        mock_load_settings.return_value = {MCP_SERVERS_KEY: [existing_server]}

        # Make the request to delete the server
        response = client.delete("/api/mcp-servers/test-server")

        # Verify the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "deleted"
        assert data["name"] == "test-server"

        # Verify save_settings was called with the correct data
        mock_save_settings.assert_called_once()
        # Extract the first positional argument from the call
        actual_data = mock_save_settings.call_args[0][0]
        assert MCP_SERVERS_KEY in actual_data
        assert len(actual_data[MCP_SERVERS_KEY]) == 0  # Server should be removed

    @patch("app_flask.mcp_servers.load_settings")
    @patch("app_flask.mcp_servers.save_settings")
    def test_delete_mcp_server_not_found(self, mock_save_settings, mock_load_settings, client):
        """Test deleting a non-existent MCP server."""
        # Create mock data with a different server
        existing_server = {"name": "existing-server", "host": "localhost", "port": 8000}
        mock_load_settings.return_value = {MCP_SERVERS_KEY: [existing_server]}

        # Make the request to delete a non-existent server
        response = client.delete("/api/mcp-servers/non-existent-server")

        # Verify the response
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "No server found" in data["error"]

        # Verify save_settings was not called
        mock_save_settings.assert_not_called()

    @patch("app_flask.mcp_servers.load_settings")
    def test_delete_mcp_server_invalid_name(self, mock_load_settings, client):
        """Test deleting an MCP server with an invalid name format."""
        # Create mock data
        mock_load_settings.return_value = {MCP_SERVERS_KEY: []}

        # Make the request with an invalid server name
        response = client.delete("/api/mcp-servers/invalid server name")

        # Verify the response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid server name format" in data["error"]

    @patch("app_flask.mcp_servers.load_settings")
    def test_blueprint_error_handler(self, mock_load_settings, client):
        """Test the blueprint's error handler."""
        # Make load_settings raise an unexpected exception
        mock_load_settings.side_effect = Exception("Unexpected error")

        # Make a request that will trigger the error handler
        response = client.get("/api/mcp-servers/")

        # Verify the response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Internal server error" in data["error"]
        assert "Unexpected error" in data["message"]

    def test_invalid_data_type_error(self):
        """Test the InvalidDataTypeError exception."""
        from app_flask.mcp_servers import InvalidDataTypeError

        # Create an instance of the exception
        error = InvalidDataTypeError("test_field", "string")

        # Verify the error message
        assert str(error) == "test_field must be a string"
        assert error.message == "test_field must be a string"

    @patch("app_flask.mcp_servers.save_settings")
    def test_save_settings_invalid_data_type(self, mock_save_settings):
        """Test save_settings with invalid data type."""
        # Create invalid data (MCP_SERVERS_KEY is not a list)
        invalid_data = {MCP_SERVERS_KEY: "not a list"}

        # Call the function and verify it raises the expected exception
        with pytest.raises(InvalidDataTypeError) as excinfo:
            save_settings(invalid_data)

        # Verify the error message
        assert "must be a list" in str(excinfo.value)
