"""Test module for common_utils.logging.centralized_logging."""

import json
import logging
import os
import socket
import tempfile
from unittest.mock import MagicMock, patch

import pytest

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

        # Reset the mock to clear the call history
        mock_socket_instance.recvfrom.reset_mock()

        # Receive a log
        received_log = self.service.receive_log()

        # Verify that recvfrom was called
        mock_socket_instance.recvfrom.assert_called_once_with(8192)

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


class TestRemoteHandler:
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


class TestCentralizedLoggingFunctions:
    """Test suite for centralized logging functions."""

    @patch("common_utils.logging.centralized_logging.LoggingClient")
    @patch("common_utils.logging.centralized_logging.RemoteHandler")
    @patch("logging.getLogger")
    def test_configure_centralized_logging(self, mock_get_logger, mock_handler_class, mock_client_class):
        """Test configure_centralized_logging function."""
        # Mock the client and handler
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_handler_instance = MagicMock()
        mock_handler_class.return_value = mock_handler_instance

        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Configure centralized logging
        configure_centralized_logging(
            app_name="test_app",
            host="localhost",
            port=5000,
            level=logging.INFO,
        )

        # Verify that a client was created
        mock_client_class.assert_called_once_with(
            app_name="test_app",
            host="localhost",
            port=5000,
        )

        # Verify that a handler was created
        mock_handler_class.assert_called_once_with(
            client=mock_client_instance,
            level=logging.INFO,
        )

        # Verify that the handler was added to the root logger
        mock_logger.addHandler.assert_called_once_with(mock_handler_instance)

        # Verify that the logging level was set
        mock_logger.setLevel.assert_called_once_with(logging.INFO)

    @patch("common_utils.logging.centralized_logging._client", None)
    @patch("common_utils.logging.centralized_logging.get_secure_logger")
    def test_get_centralized_logger_without_client(self, mock_get_secure_logger):
        """Test get_centralized_logger function without a client."""
        # Mock the secure logger
        mock_secure_logger = MagicMock()
        mock_get_secure_logger.return_value = mock_secure_logger

        # Get a centralized logger
        logger = get_centralized_logger("test_logger")

        # Verify that get_secure_logger was called
        mock_get_secure_logger.assert_called_once_with("test_logger")

        # Verify that the secure logger was returned
        assert logger == mock_secure_logger

    @patch("common_utils.logging.centralized_logging._client", MagicMock())
    @patch("logging.getLogger")
    def test_get_centralized_logger_with_client(self, mock_get_logger):
        """Test get_centralized_logger function with a client."""
        # Mock the logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Get a centralized logger
        logger = get_centralized_logger("test_logger")

        # Verify that getLogger was called
        mock_get_logger.assert_called_once_with("test_logger")

        # Verify that the logger was returned
        assert logger == mock_logger
