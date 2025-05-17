"""Comprehensive test module for common_utils.logging.centralized_logging."""

import datetime
import json
import logging
import os
import socket
import tempfile
import threading
import time
from unittest.mock import MagicMock, patch, call

import pytest

from common_utils.logging.centralized_logging import (
    CentralizedLoggingService,
    LoggingClient,
    RemoteHandler,
    configure_centralized_logging,
    get_centralized_logger,
    _client,
)


class TestCentralizedLoggingService:
    """Test suite for CentralizedLoggingService class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
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
        if hasattr(self, "service") and self.service.running:
            self.service.stop()

        # Clean up the temporary directory
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    @patch("socket.socket")
    def test_start_stop(self, mock_socket):
        """Test starting and stopping the service."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Start the service
        self.service.start()

        # Verify that the socket was created and bound
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_socket_instance.bind.assert_called_once_with(("localhost", 5000))

        # Verify that the service is running
        assert self.service.running
        assert self.service.socket is not None
        assert self.service.thread is not None

        # Stop the service
        self.service.stop()

        # Verify that the service is stopped
        assert not self.service.running
        assert self.service.socket is None
        assert self.service.thread is None
        mock_socket_instance.close.assert_called_once()

    @patch("socket.socket")
    def test_start_already_running(self, mock_socket):
        """Test starting the service when it's already running."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Start the service
        self.service.start()

        # Try to start it again
        with patch("common_utils.logging.centralized_logging.get_secure_logger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance

            self.service.start()

            # Verify that a warning was logged
            mock_logger_instance.warning.assert_called_once_with("Service is already running")

    def test_stop_not_running(self):
        """Test stopping the service when it's not running."""
        # Try to stop the service
        with patch("common_utils.logging.centralized_logging.get_secure_logger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance

            self.service.stop()

            # Verify that a warning was logged
            mock_logger_instance.warning.assert_called_once_with("Service is not running")

    @patch("socket.socket")
    def test_receive_log(self, mock_socket):
        """Test receiving a log entry."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock the recvfrom method
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
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

        # Receive a log entry
        received_entry = self.service.receive_log()

        # Verify the received entry
        assert received_entry == log_entry
        mock_socket_instance.recvfrom.assert_called_once_with(8192)

    @patch("socket.socket")
    def test_receive_log_not_running(self, mock_socket):
        """Test receiving a log entry when the service is not running."""
        # Try to receive a log entry
        with pytest.raises(RuntimeError, match="Service is not running"):
            self.service.receive_log()

    @patch("socket.socket")
    def test_receive_log_json_error(self, mock_socket):
        """Test receiving a log entry with invalid JSON."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock the recvfrom method
        mock_socket_instance.recvfrom.return_value = (
            b"invalid json",
            ("127.0.0.1", 12345),
        )

        # Start the service
        self.service.start()

        # Receive a log entry
        received_entry = self.service.receive_log()

        # Verify the received entry
        assert received_entry["level"] == "ERROR"
        assert "Failed to parse log entry" in received_entry["message"]
        assert received_entry["app"] == "centralized_logging_service"

    @patch("socket.socket")
    def test_process_log(self, mock_socket):
        """Test processing a log entry."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Start the service
        self.service.start()

        # Create a log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Process the log entry
        self.service.process_log(log_entry)

        # Verify that the log file was created
        log_file = os.path.join(self.temp_dir.name, "test_app.log")
        assert os.path.exists(log_file)

        # Verify the log file contents
        with open(log_file, "r") as f:
            log_content = f.read()
            assert "test_app" in log_content
            assert "test_logger" in log_content
            assert "INFO" in log_content
            assert "Test message" in log_content


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

    @patch("socket.socket")
    def test_send_log(self, mock_socket):
        """Test sending a log entry."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Create a log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
        }

        # Send the log entry
        self.client.send_log(log_entry)

        # Verify that the socket was created and used
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_socket_instance.sendto.assert_called_once()
        mock_socket_instance.close.assert_called_once()

        # Verify that the app name was added to the log entry
        call_args = mock_socket_instance.sendto.call_args[0]
        sent_data = json.loads(call_args[0].decode("utf-8"))
        assert sent_data["app"] == "test_app"

    @patch("socket.socket")
    def test_send_log_with_app(self, mock_socket):
        """Test sending a log entry with an app name already set."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Create a log entry with an app name
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "custom_app",
        }

        # Send the log entry
        self.client.send_log(log_entry)

        # Verify that the app name was not changed
        call_args = mock_socket_instance.sendto.call_args[0]
        sent_data = json.loads(call_args[0].decode("utf-8"))
        assert sent_data["app"] == "custom_app"

    @patch("socket.socket")
    def test_send_log_error(self, mock_socket):
        """Test sending a log entry with an error."""
        # Mock the socket to raise an exception
        mock_socket.side_effect = Exception("Test error")

        # Create a log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
        }

        # Mock the logger
        with patch("common_utils.logging.centralized_logging.get_secure_logger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance

            # Send the log entry
            self.client.send_log(log_entry)

            # Verify that the error was logged
            mock_logger_instance.error.assert_called_once_with("Failed to send log entry: Test error")


class TestRemoteHandler:
    """Test suite for RemoteHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock client
        self.mock_client = MagicMock()

        # Create a RemoteHandler instance
        self.handler = RemoteHandler(
            client=self.mock_client,
            level=logging.INFO,
        )

    def test_emit(self):
        """Test emitting a log record."""
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        self.handler.emit(record)

        # Verify that the client's send_log method was called
        self.mock_client.send_log.assert_called_once()

        # Verify the log entry
        log_entry = self.mock_client.send_log.call_args[0][0]
        assert log_entry["level"] == "INFO"
        assert "Test message" in log_entry["message"]
        assert log_entry["logger"] == "test_logger"
        assert log_entry["pathname"] == "test_file.py"
        assert log_entry["lineno"] == 42
        assert log_entry["funcName"] == "?"

    def test_emit_error(self):
        """Test emitting a log record with an error."""
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Make the client's send_log method raise an exception
        self.mock_client.send_log.side_effect = Exception("Test error")

        # Mock the handleError method
        with patch.object(self.handler, "handleError") as mock_handle_error:
            # Emit the record
            self.handler.emit(record)

            # Verify that handleError was called
            mock_handle_error.assert_called_once_with(record)


class TestConfigureCentralizedLogging:
    """Test suite for configure_centralized_logging function."""

    def test_configure_centralized_logging(self):
        """Test configuring centralized logging."""
        # Mock the LoggingClient and RemoteHandler classes
        with patch("common_utils.logging.centralized_logging.LoggingClient") as mock_client_class, \
             patch("common_utils.logging.centralized_logging.RemoteHandler") as mock_handler_class, \
             patch("logging.getLogger") as mock_get_logger:
            # Mock the client and handler instances
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

            # Verify that the client was created
            mock_client_class.assert_called_once_with(
                app_name="test_app",
                host="localhost",
                port=5000,
            )

            # Verify that the handler was created
            mock_handler_class.assert_called_once_with(
                client=mock_client_instance,
                level=logging.INFO,
            )

            # Verify that the handler was added to the root logger
            mock_get_logger.assert_called_once_with()
            mock_logger.addHandler.assert_called_once_with(mock_handler_instance)
            mock_logger.setLevel.assert_called_once_with(logging.INFO)


class TestGetCentralizedLogger:
    """Test suite for get_centralized_logger function."""

    def test_get_centralized_logger_with_client(self):
        """Test getting a centralized logger when a client is configured."""
        # Mock the global client
        global _client
        original_client = _client
        _client = MagicMock()

        # Mock the logging.getLogger function
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Get a centralized logger
            logger = get_centralized_logger("test_logger")

            # Verify that logging.getLogger was called
            mock_get_logger.assert_called_once_with("test_logger")

            # Verify that the logger was returned
            assert logger == mock_logger

        # Restore the original client
        _client = original_client

    def test_get_centralized_logger_without_client(self):
        """Test getting a centralized logger when no client is configured."""
        # Mock the global client
        global _client
        original_client = _client
        _client = None

        # Mock the get_secure_logger function
        with patch("common_utils.logging.centralized_logging.get_secure_logger") as mock_get_secure_logger:
            mock_logger = MagicMock()
            mock_get_secure_logger.return_value = mock_logger

            # Get a centralized logger
            logger = get_centralized_logger("test_logger")

            # Verify that get_secure_logger was called
            mock_get_secure_logger.assert_called_once_with("test_logger")

            # Verify that the logger was returned
            assert logger == mock_logger

        # Restore the original client
        _client = original_client
