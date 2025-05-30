"""Tests for the MCP adapter."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from ai_models.adapters.exceptions import ModelContextProtocolError
from ai_models.adapters.mcp_adapter import MCPAdapter


@pytest.fixture
def mock_mcp():
    """Mock the modelcontextprotocol module."""
    with patch("ai_models.adapters.mcp_adapter.mcp") as mock_mcp:
        mock_client = MagicMock()
        mock_mcp.Client.return_value = mock_client
        yield mock_mcp


class TestMCPAdapter:
    """Tests for the MCPAdapter class."""

    def test_init_with_valid_params(self, mock_mcp):  # noqa: ARG002
        """Test initialization with valid parameters."""
        # Define test values
        test_host = "localhost"
        test_port = 9000

        adapter = MCPAdapter(host=test_host, port=test_port)
        assert adapter.host == test_host
        assert adapter.port == test_port
        assert adapter.client is None

    def test_init_with_invalid_host(self, mock_mcp):  # noqa: ARG002
        """Test initialization with invalid host."""
        with pytest.raises(
            ValueError, match="Host must contain only alphanumeric characters"
        ):
            MCPAdapter(host="local;host", port=9000)

    def test_init_with_invalid_port_type(self, mock_mcp):  # noqa: ARG002
        """Test initialization with invalid port type."""
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535"
        ):
            MCPAdapter(host="localhost", port="9000")

    def test_init_with_invalid_port_range(self, mock_mcp):  # noqa: ARG002
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

    def test_send_message_with_mcp_none(self):
        """Test send_message raises ModelContextProtocolError if mcp is None."""
        with patch("ai_models.adapters.mcp_adapter.mcp", None), pytest.raises(ModelContextProtocolError):
            adapter = MCPAdapter(host="localhost", port=9000)
            adapter.send_message("Hello")

    def test_send_message_handle_client_error(self, mock_mcp):
        """Test send_message triggers _handle_client_error when self.client is None after connect."""
        adapter = MCPAdapter(host="localhost", port=9000)
        # Patch connect to not set self.client
        with patch.object(adapter, "connect", return_value=None):
            adapter.client = None
            with pytest.raises(ConnectionError, match="Error communicating with MCP server"):
                adapter.send_message("Hello")

    def test_close_always_sets_client_none(self, mock_mcp, caplog):
        """Test close always sets self.client = None and logs, even if disconnect raises."""
        adapter = MCPAdapter(host="localhost", port=9000)
        adapter.client = mock_mcp.Client.return_value
        mock_mcp.Client.return_value.disconnect.side_effect = Exception("Disconnect error")
        with caplog.at_level(logging.INFO):
            adapter.close()
        assert adapter.client is None
        # Should log 'Reset client to None'
        assert any("Reset client to None" in m for m in caplog.messages)

    def test_extra_kwargs_passed_to_client(self, mock_mcp):
        """Test extra kwargs are passed to mcp.Client."""
        adapter = MCPAdapter(host="localhost", port=9000, foo="bar", baz=123)
        adapter.connect()
        mock_mcp.Client.assert_called_once_with("http://localhost:9000", foo="bar", baz=123)

    def test_custom_exceptions(self):
        """Test custom exception classes for correct message and attributes."""
        from ai_models.adapters.mcp_adapter import (
            HostFormatError,
            MCPCommunicationError,
            MCPConnectionError,
            PortRangeError,
        )
        # HostFormatError
        err = HostFormatError()
        assert "Host must contain only alphanumeric characters" in str(err)
        # PortRangeError
        err = PortRangeError()
        assert "Port must be an integer between" in str(err)
        # MCPConnectionError
        orig = Exception("fail")
        err = MCPConnectionError("http://localhost:9000", orig)
        assert "Failed to connect to MCP server" in str(err)
        assert err.original_error is orig
        # MCPCommunicationError
        orig = Exception("fail2")
        err = MCPCommunicationError(orig)
        assert "Error communicating with MCP server" in str(err)
        assert err.original_error is orig

    def test_handle_client_error_function(self):
        """Test the private _handle_client_error function raises MCPCommunicationError."""
        from ai_models.adapters.mcp_adapter import (
            MCPCommunicationError,
            _handle_client_error,
        )
        with pytest.raises(MCPCommunicationError) as exc_info:
            _handle_client_error()
        assert "Error communicating with MCP server" in str(exc_info.value)
