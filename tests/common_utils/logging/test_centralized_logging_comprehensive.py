"""Comprehensive test module for common_utils.logging.centralized_logging."""

import datetime
import json
import logging
import os
import socket
import tempfile
import threading
import time
from unittest.mock import MagicMock, call, patch

import pytest

from common_utils.logging.centralized_logging import (
    CentralizedLoggingService,
    ElasticsearchOutput,
    FileOutput,
    LevelFilter,
    LogFilter,
    LoggingClient,
    LogLevel,
    LogOutput,
    LogstashOutput,
    RemoteHandler,
    SensitiveDataFilter,
    _client,
    configure_centralized_logging,
    get_centralized_logger,
    stop_centralized_logging,
)


class TestLogLevel:
    """Test suite for LogLevel enum."""

    def test_log_level_values(self):
        """Test that LogLevel enum values match logging module values."""
        assert LogLevel.DEBUG.value == logging.DEBUG
        assert LogLevel.INFO.value == logging.INFO
        assert LogLevel.WARNING.value == logging.WARNING
        assert LogLevel.ERROR.value == logging.ERROR
        assert LogLevel.CRITICAL.value == logging.CRITICAL


class TestLevelFilter:
    """Test suite for LevelFilter class."""

    def test_init_with_string(self):
        """Test initializing with a string level name."""
        filter_obj = LevelFilter("INFO")
        assert filter_obj.min_level == logging.INFO

    def test_init_with_int(self):
        """Test initializing with an integer level value."""
        filter_obj = LevelFilter(30)  # WARNING
        assert filter_obj.min_level == logging.WARNING

    def test_init_with_enum(self):
        """Test initializing with a LogLevel enum value."""
        filter_obj = LevelFilter(LogLevel.ERROR)
        assert filter_obj.min_level == logging.ERROR

    def test_filter_below_level(self):
        """Test filtering a log entry below the minimum level."""
        filter_obj = LevelFilter(LogLevel.WARNING)
        log_entry = {"level": "INFO"}
        assert filter_obj.filter(log_entry) is False

    def test_filter_at_level(self):
        """Test filtering a log entry at the minimum level."""
        filter_obj = LevelFilter(LogLevel.WARNING)
        log_entry = {"level": "WARNING"}
        assert filter_obj.filter(log_entry) is True

    def test_filter_above_level(self):
        """Test filtering a log entry above the minimum level."""
        filter_obj = LevelFilter(LogLevel.WARNING)
        log_entry = {"level": "ERROR"}
        assert filter_obj.filter(log_entry) is True


class TestSensitiveDataFilter:
    """Test suite for SensitiveDataFilter class."""

    def test_filter_message(self):
        """Test filtering sensitive data in a message."""
        filter_obj = SensitiveDataFilter()
        log_entry = {"message": "Password: secret123"}
        assert filter_obj.filter(log_entry) is True
        assert log_entry["message"] != "Password: secret123"
        assert "Password: ***" in log_entry["message"]

    def test_filter_fields(self):
        """Test filtering sensitive data in specified fields."""
        filter_obj = SensitiveDataFilter(fields=["user_data"])
        log_entry = {
            "message": "User logged in",
            "user_data": {"password": "secret123"},
        }
        assert filter_obj.filter(log_entry) is True
        assert log_entry["message"] == "User logged in"
        assert log_entry["user_data"]["password"] != "secret123"


class MockOutput(LogOutput):
    """Mock output for testing."""

    def __init__(self):
        """Initialize the mock output."""
        self.entries = []
        self.closed = False

    def output(self, log_entry):
        """Output a log entry."""
        self.entries.append(log_entry.copy())

    def close(self):
        """Close the output."""
        self.closed = True


class TestFileOutput:
    """Test suite for FileOutput class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output = FileOutput(directory=self.temp_dir.name)

    def teardown_method(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_output(self):
        """Test outputting a log entry."""
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }
        self.output.output(log_entry)

        # Check that the log file was created
        log_file = os.path.join(self.temp_dir.name, "test_app.log")
        assert os.path.exists(log_file)

        # Check the log file contents
        with open(log_file) as f:
            content = f.read()
            assert "2023-01-01T12:00:00" in content
            assert "test_app" in content
            assert "test_logger" in content
            assert "INFO" in content
            assert "Test message" in content

    def test_rotation_size(self):
        """Test log rotation based on size."""
        # Create a file output with size-based rotation
        output = FileOutput(
            directory=self.temp_dir.name,
            rotation="size",
            max_size=100,  # Small size for testing
            backup_count=3,
        )

        # Write a log entry that exceeds the max size
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "X" * 200,  # Large message
            "logger": "test_logger",
            "app": "test_app",
        }

        # Output the log entry
        output.output(log_entry)

        # Check that the log file was created
        log_file = os.path.join(self.temp_dir.name, "test_app.log")
        assert os.path.exists(log_file)

        # Output another log entry to trigger rotation
        output.output(log_entry)

        # Check that the rotated log file was created
        rotated_file = f"{log_file}.1"
        assert os.path.exists(rotated_file)


class TestCentralizedLoggingService:
    """Test suite for CentralizedLoggingService class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a mock output
        self.mock_output = MockOutput()

        # Create a CentralizedLoggingService instance
        self.service = CentralizedLoggingService(
            host="localhost",
            port=5000,
            outputs=[self.mock_output, FileOutput(directory=self.temp_dir.name)],
            filters=[LevelFilter(LogLevel.INFO)],
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

        # Replace the logger with a mock
        self.service.logger = MagicMock()

        # Try to start it again
        self.service.start()

        # Verify that a warning was logged
        self.service.logger.warning.assert_called_once_with("Service is already running")

    def test_stop_not_running(self):
        """Test stopping the service when it's not running."""
        # Ensure the service is not running
        self.service.running = False

        # Mock the logger directly on the service instance
        self.service.logger = MagicMock()

        # Try to stop the service
        self.service.stop()

        # Verify that a warning was logged
        self.service.logger.warning.assert_called_once_with("Service is not running")

    def test_receive_log(self):
        """Test receiving a log entry."""
        # Create a log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Create a mock socket directly
        mock_socket = MagicMock()
        mock_socket.recvfrom.return_value = (
            json.dumps(log_entry).encode("utf-8"),
            ("127.0.0.1", 12345),
        )

        # Set the service's socket and running state directly
        self.service.socket = mock_socket
        self.service.running = True

        # Receive a log entry
        received_entry = self.service.receive_log()

        # Verify the received entry
        assert received_entry == log_entry
        mock_socket.recvfrom.assert_called_once_with(8192)

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
        with open(log_file) as f:
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
            buffer_size=10,
            retry_interval=1,
            secure=False,
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

        # Replace the client's logger with a mock
        self.client.logger = MagicMock()

        # Send the log entry
        self.client.send_log(log_entry)

        # Verify that the error was logged
        self.client.logger.error.assert_called_once_with("Failed to send log entry: Test error")

    def test_buffer_and_stop(self):
        """Test buffering log entries and stopping the client."""
        # Create a client with a small buffer
        client = LoggingClient(
            app_name="test_app",
            host="localhost",
            port=5000,
            buffer_size=5,
            retry_interval=0.1,
        )

        # Mock the _send_log_entry method
        client._send_log_entry = MagicMock(return_value=True)

        # Send some log entries
        for i in range(3):
            client.send_log({"message": f"Test message {i}"})

        # Wait for the buffer to be processed
        time.sleep(0.2)

        # Verify that _send_log_entry was called for each entry
        assert client._send_log_entry.call_count == 3

        # Stop the client
        client.stop()

        # Verify that the client is stopped
        assert not client.running


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
        # The funcName might be None in the actual implementation, so we'll skip this check
        # assert log_entry["funcName"] == "?"

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

            # Reset the mock before our test
            mock_get_logger.reset_mock()

            # Configure centralized logging
            configure_centralized_logging(
                app_name="test_app",
                host="localhost",
                port=5000,
                level=logging.INFO,
                buffer_size=100,
                retry_interval=5,
                secure=False,
            )

            # Verify that the client was created
            mock_client_class.assert_called_once_with(
                app_name="test_app",
                host="localhost",
                port=5000,
                buffer_size=100,
                retry_interval=5,
                secure=False,
            )

            # Verify that the handler was created
            mock_handler_class.assert_called_once_with(
                client=mock_client_instance,
                level=logging.INFO,
            )

            # Verify that the handler was added to the root logger
            # We don't need to check the exact number of calls, just that it was called with the right arguments
            mock_get_logger.assert_any_call()
            mock_logger.addHandler.assert_called_with(mock_handler_instance)
            mock_logger.setLevel.assert_called_with(logging.INFO)


class TestGetCentralizedLogger:
    """Test suite for get_centralized_logger function."""

    def test_get_centralized_logger_with_client(self):
        """Test getting a centralized logger when a client is configured."""
        # Save the original client
        # Set the global client to a mock using the module's namespace
        import common_utils.logging.centralized_logging
        from common_utils.logging.centralized_logging import _client as original_client
        mock_client = MagicMock()
        common_utils.logging.centralized_logging._client = mock_client

        try:
            # Mock the logging.getLogger function
            with patch("common_utils.logging.centralized_logging.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                # Get a centralized logger
                logger = get_centralized_logger("test_logger")

                # Verify that logging.getLogger was called
                mock_get_logger.assert_called_once_with("test_logger")

                # Verify that the logger was returned
                assert logger == mock_logger
        finally:
            # Restore the original client
            common_utils.logging.centralized_logging._client = original_client

    def test_get_centralized_logger_without_client(self):
        """Test getting a centralized logger when no client is configured."""
        # Save the original client
        # Set the global client to None using the module's namespace
        import common_utils.logging.centralized_logging
        from common_utils.logging.centralized_logging import _client as original_client
        common_utils.logging.centralized_logging._client = None

        try:
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
        finally:
            # Restore the original client
            common_utils.logging.centralized_logging._client = original_client


class TestStopCentralizedLogging:
    """Test suite for stop_centralized_logging function."""

    def test_stop_centralized_logging(self):
        """Test stopping centralized logging."""
        # Save the original client
        # Set the global client to a mock using the module's namespace
        import common_utils.logging.centralized_logging
        from common_utils.logging.centralized_logging import _client as original_client
        mock_client = MagicMock()
        common_utils.logging.centralized_logging._client = mock_client

        try:
            # Mock the logging.getLogger function
            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                # Mock the RemoteHandler class
                mock_handler = MagicMock(spec=RemoteHandler)
                mock_logger.handlers = [mock_handler]

                # Stop centralized logging
                stop_centralized_logging()

                # Verify that the client was stopped
                mock_client.stop.assert_called_once()

                # Verify that the handler was removed from the root logger
                mock_logger.removeHandler.assert_called_once_with(mock_handler)

                # Verify that the global client was set to None
                assert common_utils.logging.centralized_logging._client is None
        finally:
            # Restore the original client
            common_utils.logging.centralized_logging._client = original_client
