"""Test module for common_utils.logging.centralized_logging with improved coverage."""

import json
import logging
import os
import socket
import tempfile
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.centralized_logging import (
    CentralizedLoggingService,
    LoggingClient,
    RemoteHandler,
    configure_centralized_logging,
    get_centralized_logger,
)


class TestCentralizedLoggingServiceImproved:
    """Test suite for CentralizedLoggingService class with improved coverage."""

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

    def test_start_when_already_running(self):
        """Test start method when the service is already running."""
        # Start the service
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            self.service.start()

        # Verify that the service is running
        assert self.service.running is True

        # Mock the logger
        with patch.object(self.service.logger, "warning") as mock_warning:
            # Start the service again
            self.service.start()

            # Verify that the warning was logged
            mock_warning.assert_called_once_with("Service is already running")

    def test_start_with_exception(self):
        """Test start method with an exception."""
        # Mock the socket to raise an exception
        with patch("socket.socket", side_effect=Exception("Test exception")):
            # Mock the logger
            with patch.object(self.service.logger, "error") as mock_error:
                # Start the service
                with pytest.raises(Exception, match="Test exception"):
                    self.service.start()

                # Verify that the error was logged
                mock_error.assert_called_once()

                # Verify that the service is not running
                assert self.service.running is False
                assert self.service.socket is None

    def test_stop_when_not_running(self):
        """Test stop method when the service is not running."""
        # Verify that the service is not running
        assert self.service.running is False

        # Mock the logger
        with patch.object(self.service.logger, "warning") as mock_warning:
            # Stop the service
            self.service.stop()

            # Verify that the warning was logged
            mock_warning.assert_called_once_with("Service is not running")

    def test_receive_log_when_not_running(self):
        """Test receive_log method when the service is not running."""
        # Verify that the service is not running
        assert self.service.running is False

        # Call receive_log
        with pytest.raises(RuntimeError, match="Service is not running"):
            self.service.receive_log()

    def test_receive_log_with_json_decode_error(self):
        """Test receive_log method with a JSON decode error."""
        # Start the service
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            self.service.start()

        # Mock the socket to return invalid JSON
        self.service.socket.recvfrom.return_value = (b"invalid json", ("localhost", 5000))

        # Mock the logger
        with patch.object(self.service.logger, "error") as mock_error:
            # Call receive_log
            log_entry = self.service.receive_log()

            # Verify that the error was logged
            mock_error.assert_called_once()

            # Verify that a default log entry was returned
            assert log_entry["level"] == "ERROR"
            assert "Failed to parse log entry" in log_entry["message"]
            assert log_entry["logger"] == "centralized_logging_service"
            assert log_entry["app"] == "centralized_logging_service"

    def test_process_log_with_exception(self):
        """Test process_log method with an exception."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=Exception("Test exception")):
            # Mock the logger
            with patch.object(self.service.logger, "error") as mock_error:
                # Process the log entry
                self.service.process_log(log_entry)

                # Verify that the error was logged
                mock_error.assert_called_once()

    def test_process_logs_with_exception(self):
        """Test _process_logs method with an exception."""
        # Start the service
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            self.service.start()

        # Mock receive_log to raise an exception
        with patch.object(self.service, "receive_log", side_effect=Exception("Test exception")):
            # Mock the logger
            with patch.object(self.service.logger, "error") as mock_error:
                # Mock time.sleep to avoid waiting
                with patch("time.sleep"):
                    # Call _process_logs
                    self.service._process_logs()

                    # Verify that the error was logged
                    mock_error.assert_called_once()


class TestLoggingClientImproved:
    """Test suite for LoggingClient class with improved coverage."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a LoggingClient instance
        self.client = LoggingClient(
            app_name="test_app",
            host="localhost",
            port=5000,
        )

    def test_send_log_with_exception(self):
        """Test send_log method with an exception."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
        }

        # Mock socket.socket to raise an exception
        with patch("socket.socket", side_effect=Exception("Test exception")):
            # Mock the logger
            with patch.object(self.client.logger, "error") as mock_error:
                # Send the log entry
                self.client.send_log(log_entry)

                # Verify that the error was logged
                mock_error.assert_called_once()


class TestRemoteHandlerImproved:
    """Test suite for RemoteHandler class with improved coverage."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock client
        self.mock_client = MagicMock()

        # Create a RemoteHandler instance
        self.handler = RemoteHandler(
            client=self.mock_client,
            level=logging.INFO,
        )

    def test_emit_with_exception(self):
        """Test emit method with an exception."""
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

        # Mock the client's send_log method to raise an exception
        self.mock_client.send_log.side_effect = Exception("Test exception")

        # Mock handleError
        with patch.object(self.handler, "handleError") as mock_handle_error:
            # Emit the record
            self.handler.emit(record)

            # Verify that handleError was called
            mock_handle_error.assert_called_once_with(record)


class TestCentralizedLoggingFunctionsImproved:
    """Test suite for centralized logging functions with improved coverage."""

    def test_get_centralized_logger_without_client(self):
        """Test get_centralized_logger function when the client is not configured."""
        # Ensure the global client is None
        from common_utils.logging.centralized_logging import _client
        _client = None

        # Mock get_secure_logger
        with patch("common_utils.logging.centralized_logging.get_secure_logger") as mock_get_secure_logger:
            mock_logger = MagicMock()
            mock_get_secure_logger.return_value = mock_logger

            # Get a centralized logger
            logger = get_centralized_logger("test_logger")

            # Verify that get_secure_logger was called
            mock_get_secure_logger.assert_called_once_with("test_logger")

            # Verify that the secure logger was returned
            assert logger == mock_logger
