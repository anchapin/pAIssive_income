"""Tests for the app_flask/mcp_servers.py module."""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app_flask.mcp_servers import (
    MCP_SERVERS_KEY,
    InvalidDataTypeError,
    load_settings,
    save_settings,
    validate_server_data,
)


class TestMcpServers(unittest.TestCase):
    """Test cases for the app_flask/mcp_servers.py module."""

    def test_validate_server_data_valid(self):
        """Test validation with valid server data."""
        server_data = {
            "name": "test-server",
            "host": "localhost",
            "port": 8080,
            "description": "Test server"
        }
        result = validate_server_data(server_data)
        self.assertIsNone(result)

    def test_validate_server_data_invalid_json(self):
        """Test validation with invalid JSON data."""
        server_data = None
        result = validate_server_data(server_data)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "Invalid JSON data")
        self.assertEqual(result[1], 400)

    def test_validate_server_data_missing_fields(self):
        """Test validation with missing required fields."""
        server_data = {
            "name": "test-server",
            "host": "localhost"
            # Missing port
        }
        result = validate_server_data(server_data)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "Missing required field: port")
        self.assertEqual(result[1], 400)

    def test_validate_server_data_invalid_name(self):
        """Test validation with invalid server name."""
        server_data = {
            "name": "test server!",  # Invalid characters
            "host": "localhost",
            "port": 8080
        }
        result = validate_server_data(server_data)
        self.assertIsNotNone(result)
        self.assertTrue("Server name must contain only" in result[0])
        self.assertEqual(result[1], 400)

    def test_validate_server_data_invalid_host(self):
        """Test validation with invalid host."""
        server_data = {
            "name": "test-server",
            "host": "localhost!",  # Invalid characters
            "port": 8080
        }
        result = validate_server_data(server_data)
        self.assertIsNotNone(result)
        self.assertTrue("Host must contain only" in result[0])
        self.assertEqual(result[1], 400)

    def test_validate_server_data_invalid_port_type(self):
        """Test validation with invalid port type."""
        server_data = {
            "name": "test-server",
            "host": "localhost",
            "port": "invalid"  # Not an integer
        }
        result = validate_server_data(server_data)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "Port must be a valid integer")
        self.assertEqual(result[1], 400)

    def test_validate_server_data_invalid_port_range(self):
        """Test validation with port out of range."""
        server_data = {
            "name": "test-server",
            "host": "localhost",
            "port": 70000  # Out of range
        }
        result = validate_server_data(server_data)
        self.assertIsNotNone(result)
        self.assertTrue("Port must be between" in result[0])
        self.assertEqual(result[1], 400)

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_load_settings_file_not_exists(self, mock_settings_file):
        """Test loading settings when file doesn't exist."""
        mock_settings_file.exists.return_value = False
        result = load_settings()
        self.assertEqual(result, {MCP_SERVERS_KEY: []})

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_load_settings_file_too_large(self, mock_settings_file):
        """Test loading settings when file is too large."""
        mock_settings_file.exists.return_value = True
        mock_stat = MagicMock()
        mock_stat.st_size = 2 * 1024 * 1024  # 2MB (too large)
        mock_settings_file.stat.return_value = mock_stat

        result = load_settings()
        self.assertEqual(result, {MCP_SERVERS_KEY: []})

    @patch("app_flask.mcp_servers.MCP_SETTINGS_FILE")
    def test_save_settings_invalid_data_type(self, mock_settings_file):
        """Test saving settings with invalid data type."""
        data = {MCP_SERVERS_KEY: "not a list"}  # Invalid type

        with self.assertRaises(InvalidDataTypeError):
            save_settings(data)


if __name__ == "__main__":
    unittest.main()
