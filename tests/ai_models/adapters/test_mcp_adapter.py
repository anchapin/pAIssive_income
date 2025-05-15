"""Tests for the MCP adapter."""

import pytest
import re
from unittest.mock import MagicMock, patch

from ai_models.adapters.mcp_adapter import MCPAdapter
from ai_models.adapters.exceptions import ModelContextProtocolError


@pytest.fixture
def mock_mcp():
    """Mock the modelcontextprotocol module."""
    with patch("ai_models.adapters.mcp_adapter.mcp") as mock_mcp:
        mock_client = MagicMock()
        mock_mcp.Client.return_value = mock_client
        yield mock_mcp


class TestMCPAdapter:
    """Tests for the MCPAdapter class."""

    def test_init_with_valid_params(self):
        """Test initialization with valid parameters."""
        adapter = MCPAdapter(host="localhost", port=9000)
        assert adapter.host == "localhost"
        assert adapter.port == 9000
        assert adapter.client is None

    def test_init_with_invalid_host(self):
        """Test initialization with invalid host."""
        with pytest.raises(
            ValueError, match="Host must contain only alphanumeric characters"
        ):
            MCPAdapter(host="local;host", port=9000)

    def test_init_with_invalid_port_type(self):
        """Test initialization with invalid port type."""
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535"
        ):
            MCPAdapter(host="localhost", port="9000")

    def test_init_with_invalid_port_range(self):
        """Test initialization with invalid port range."""
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535"
        ):
            MCPAdapter(host="localhost", port=0)

        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535"
        ):
            MCPAdapter(host="localhost", port=65536)

    def test_init_with_missing_mcp(self):
        """Test initialization with missing MCP module."""
        with patch("ai_models.adapters.mcp_adapter.mcp", None), pytest.raises(
            ModelContextProtocolError
        ):
            MCPAdapter(host="localhost", port=9000)

    def test_connect(self, mock_mcp):
        """Test connect method."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.connect()

        mock_mcp.Client.assert_called_once_with("http://localhost:9000")
        mock_mcp.Client.return_value.connect.assert_called_once()
        assert adapter.client == mock_mcp.Client.return_value

    def test_connect_with_error(self, mock_mcp):
        """Test connect method with error."""
        mock_mcp.Client.return_value.connect.side_effect = Exception("Connection error")

        adapter = MCPAdapter(host="localhost", port=9000)
        with pytest.raises(ConnectionError, match="Failed to connect to MCP server"):
            adapter.connect()

    def test_send_message(self, mock_mcp):
        """Test send_message method."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = mock_mcp.Client.return_value

        mock_mcp.Client.return_value.send_message.return_value = "Response"

        response = adapter.send_message("Hello")

        mock_mcp.Client.return_value.send_message.assert_called_once_with("Hello")
        assert response == "Response"

    def test_send_message_with_no_client(self, mock_mcp):
        """Test send_message method with no client."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = None

        mock_mcp.Client.return_value.send_message.return_value = "Response"

        response = adapter.send_message("Hello")

        mock_mcp.Client.assert_called_once_with("http://localhost:9000")
        mock_mcp.Client.return_value.connect.assert_called_once()
        mock_mcp.Client.return_value.send_message.assert_called_once_with("Hello")
        assert response == "Response"

    def test_send_message_with_error(self, mock_mcp):
        """Test send_message method with error."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = mock_mcp.Client.return_value

        mock_mcp.Client.return_value.send_message.side_effect = Exception("Send error")

        with pytest.raises(
            ConnectionError, match="Error communicating with MCP server"
        ):
            adapter.send_message("Hello")

        assert adapter.client is None  # Client should be reset on error

    def test_close(self, mock_mcp):
        """Test close method."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = mock_mcp.Client.return_value

        adapter.close()

        mock_mcp.Client.return_value.disconnect.assert_called_once()
        assert adapter.client is None

    def test_close_with_no_client(self, mock_mcp):
        """Test close method with no client."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = None

        adapter.close()  # Should not raise an exception

        mock_mcp.Client.return_value.disconnect.assert_not_called()
        assert adapter.client is None

    def test_close_with_error(self, mock_mcp):
        """Test close method with error."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = mock_mcp.Client.return_value

        mock_mcp.Client.return_value.disconnect.side_effect = Exception(
            "Disconnect error"
        )

        adapter.close()  # Should not raise an exception

        mock_mcp.Client.return_value.disconnect.assert_called_once()
        assert adapter.client is None
