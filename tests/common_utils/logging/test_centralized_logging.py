"""Test module for common_utils.logging.centralized_logging."""

import json
import logging
import os
import socket
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test - we'll create this module next
from common_utils.logging.centralized_logging import (
    CentralizedLoggingService,
    LoggingClient,
    RemoteHandler,
    configure_centralized_logging,
    get_centralized_logger,
)


class TestCentralizedLoggingService:
    """Test suite for CentralizedLoggingService class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a CentralizedLoggingService instance
        self.service = CentralizedLoggingService(
            host="localhost",
            port=5000,
            log_dir=self.temp_dir.name,
        )

    def teardown_method(self):
        """Tear down test fixtures."""
        # Stop the service if it's running
        if hasattr(self, 'service') and self.service.running:
            self.service.stop()

        # Sleep briefly to allow file handles to be released
        import time
        time.sleep(0.1)

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_init(self):
        """Test CentralizedLoggingService initialization."""
        assert self.service.host == "localhost"
        assert self.service.port == 5000
        assert self.service.log_dir == self.temp_dir.name
        assert self.service.running is False

    @patch("socket.socket")
    def test_start(self, mock_socket):
        """Test start method."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Start the service
        self.service.start()

        # Verify that the socket was created and bound
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_socket_instance.bind.assert_called_once_with(("localhost", 5000))

        # Verify that the service is running
        assert self.service.running is True

        # Verify that the socket was stored
        assert self.service.socket == mock_socket_instance

    @patch("socket.socket")
    def test_stop(self, mock_socket):
        """Test stop method."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Start the service
        self.service.start()

        # Verify that the service is running
        assert self.service.running is True

        # Stop the service
        self.service.stop()

        # Verify that the socket was closed
        mock_socket_instance.close.assert_called_once()

        # Verify that the service is not running
        assert self.service.running is False

    @patch("socket.socket")
    def test_receive_log(self, mock_socket):
        """Test receive_log method."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock the recvfrom method to return a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }
        mock_socket_instance.recvfrom.return_value = (
            json.dumps(log_entry).encode("utf-8"),
            ("127.0.0.1", 12345),
        )

        # Start the service
        self.service.start()

        # Receive a log
        received_log = self.service.receive_log()

        # Verify that recvfrom was called with the correct buffer size
        mock_socket_instance.recvfrom.assert_called_with(8192)

        # Verify that the received log matches the expected log entry
        assert received_log == log_entry

    @patch("socket.socket")
    def test_process_log(self, mock_socket):
        """Test process_log method."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Mock the log file
        log_file_path = os.path.join(self.temp_dir.name, "test_app.log")

        # Start the service
        self.service.start()

        # Process the log
        with patch("builtins.open", MagicMock()) as mock_open:
            self.service.process_log(log_entry)

            # Verify that the log file was opened for appending
            mock_open.assert_called_once_with(log_file_path, "a")

            # Verify that the log entry was written to the file
            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.write.assert_called_once()

            # Verify that the written log entry contains the expected fields
            written_log = mock_file.write.call_args[0][0]
            assert "2023-01-01T12:00:00Z" in written_log
            assert "INFO" in written_log
            assert "Test message" in written_log
            assert "test_logger" in written_log
            assert "test_app" in written_log


class TestLoggingClient:
    """Test suite for LoggingClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a LoggingClient instance
        self.client = LoggingClient(
            app_name="test_app",
            host="localhost",
            port=5000,
        )

    def test_init(self):
        """Test LoggingClient initialization."""
        assert self.client.app_name == "test_app"
        assert self.client.host == "localhost"
        assert self.client.port == 5000

    @patch("socket.socket")
    def test_send_log(self, mock_socket):
        """Test send_log method."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Send the log
        self.client.send_log(log_entry)

        # Verify that the socket was created
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)

        # Verify that the log entry was sent
        mock_socket_instance.sendto.assert_called_once()

        # Verify that the socket was closed
        mock_socket_instance.close.assert_called_once()

        # The first argument to sendto should be the JSON-encoded log entry
        args, _ = mock_socket_instance.sendto.call_args
        sent_data = args[0]

        # Decode the sent data and verify it matches the log entry
        decoded_data = json.loads(sent_data.decode("utf-8"))
        assert decoded_data == log_entry

        # The second argument to sendto should be the host and port
        args, _ = mock_socket_instance.sendto.call_args
        assert args[1] == ("localhost", 5000)


class TestRemoteHandler(logging.Handler):
    """Test suite for RemoteHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a RemoteHandler instance with a mock client
        self.mock_client = MagicMock()
        self.handler = RemoteHandler(client=self.mock_client)

    def test_init(self):
        """Test RemoteHandler initialization."""
        assert self.handler.client == self.mock_client

    def test_emit(self):
        """Test emit method."""
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        self.handler.emit(record)

        # Verify that the client's send_log method was called
        self.mock_client.send_log.assert_called_once()

        # Verify that the log entry contains the expected fields
        log_entry = self.mock_client.send_log.call_args[0][0]
        assert log_entry["logger"] == "test_logger"
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Test message"
        assert "timestamp" in log_entry
