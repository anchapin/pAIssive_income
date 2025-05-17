"""Test module for common_utils.logging.log_aggregation."""

import json
import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.log_aggregation import (
    LogAggregator,
    ElasticsearchHandler,
    LogstashHandler,
    FileRotatingHandler,
    aggregate_logs,
    configure_log_aggregation,
    parse_log_file,
    get_log_files,
    get_log_statistics,
)


class TestLogAggregator:
    """Test suite for LogAggregator class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a LogAggregator instance
        self.aggregator = LogAggregator(
            app_name="test_app",
            log_dir=self.temp_dir.name,
        )

    def teardown_method(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_init(self):
        """Test LogAggregator initialization."""
        assert self.aggregator.app_name == "test_app"
        assert self.aggregator.log_dir == self.temp_dir.name
        assert isinstance(self.aggregator.handlers, list)
        assert len(self.aggregator.handlers) == 0  # No handlers by default

    def test_add_handler(self):
        """Test add_handler method."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Verify that the handler was added
        assert mock_handler in self.aggregator.handlers
        assert len(self.aggregator.handlers) == 1

    def test_remove_handler(self):
        """Test remove_handler method."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Verify that the handler was added
        assert mock_handler in self.aggregator.handlers

        # Remove the handler
        self.aggregator.remove_handler(mock_handler)

        # Verify that the handler was removed
        assert mock_handler not in self.aggregator.handlers
        assert len(self.aggregator.handlers) == 0

    def test_aggregate_log_entry(self):
        """Test aggregate_log_entry method."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Aggregate the log entry
        self.aggregator.aggregate_log_entry(log_entry)

        # Verify that the handler was called with the log entry
        mock_handler.handle.assert_called_once_with(log_entry)

    def test_aggregate_log_file(self):
        """Test aggregate_log_file method."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Create a sample log file
        log_file_path = os.path.join(self.temp_dir.name, "test.log")
        with open(log_file_path, "w") as f:
            f.write("2023-01-01 12:00:00 - app - INFO - Test message 1\n")
            f.write("2023-01-01 12:01:00 - app.auth - WARNING - Test message 2\n")

        # Aggregate the log file
        with patch("common_utils.logging.log_aggregation.parse_log_file") as mock_parse:
            # Mock the parse_log_file function to return some log entries
            mock_parse.return_value = [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "level": "INFO",
                    "message": "Test message 1",
                    "logger": "app",
                    "app": "test_app",
                },
                {
                    "timestamp": "2023-01-01T12:01:00Z",
                    "level": "WARNING",
                    "message": "Test message 2",
                    "logger": "app.auth",
                    "app": "test_app",
                },
            ]

            # Call the method under test
            self.aggregator.aggregate_log_file(log_file_path)

            # Verify that parse_log_file was called with the log file path
            mock_parse.assert_called_once_with(log_file_path)

            # Verify that the handler was called for each log entry
            assert mock_handler.handle.call_count == 2


class TestElasticsearchHandler:
    """Test suite for ElasticsearchHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create an ElasticsearchHandler instance with a mock Elasticsearch client
        self.mock_es_client = MagicMock()
        self.handler = ElasticsearchHandler(
            es_client=self.mock_es_client,
            index_name="test_logs",
        )

    def test_init(self):
        """Test ElasticsearchHandler initialization."""
        assert self.handler.es_client == self.mock_es_client
        assert self.handler.index_name == "test_logs"

    def test_handle(self):
        """Test handle method."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Handle the log entry
        self.handler.handle(log_entry)

        # Verify that the Elasticsearch client was called to index the document
        self.mock_es_client.index.assert_called_once_with(
            index="test_logs",
            document=log_entry,
        )


class TestLogstashHandler:
    """Test suite for LogstashHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a LogstashHandler instance with mock socket
        self.mock_socket = MagicMock()
        self.handler = LogstashHandler(
            host="localhost",
            port=5000,
            socket=self.mock_socket,
        )

    def test_init(self):
        """Test LogstashHandler initialization."""
        assert self.handler.host == "localhost"
        assert self.handler.port == 5000
        assert self.handler.socket == self.mock_socket

    def test_handle(self):
        """Test handle method."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Handle the log entry
        self.handler.handle(log_entry)

        # Verify that the socket was called to send the log entry
        self.mock_socket.sendto.assert_called_once()

        # The first argument should be the JSON-encoded log entry
        args, _ = self.mock_socket.sendto.call_args
        sent_data = args[0]

        # Decode the sent data and verify it matches the log entry
        decoded_data = json.loads(sent_data.decode("utf-8"))
        assert decoded_data == log_entry


class TestFileRotatingHandler:
    """Test suite for FileRotatingHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a FileRotatingHandler instance
        self.handler = FileRotatingHandler(
            filename=os.path.join(self.temp_dir.name, "test.log"),
            max_bytes=1024,
            backup_count=3,
        )

    def teardown_method(self):
        """Tear down test fixtures."""
        # Close the handler to release the file
        if hasattr(self, 'handler') and hasattr(self.handler, 'handler'):
            self.handler.handler.close()

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_init(self):
        """Test FileRotatingHandler initialization."""
        assert self.handler.filename == os.path.join(self.temp_dir.name, "test.log")
        assert self.handler.max_bytes == 1024
        assert self.handler.backup_count == 3
        assert isinstance(self.handler.handler, logging.handlers.RotatingFileHandler)

    @patch("logging.handlers.RotatingFileHandler.emit")
    def test_handle(self, mock_emit):
        """Test handle method."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Handle the log entry
        self.handler.handle(log_entry)

        # Verify that emit was called
        mock_emit.assert_called_once()

        # Verify that the log record contains the expected fields
        record = mock_emit.call_args[0][0]
        assert record.name == "test_logger"
        assert record.levelname == "INFO"
        assert record.msg == "Test message"


class TestAggregateLogsFunctions:
    """Test suite for aggregate_logs and related functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test log files
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown_method(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("common_utils.logging.log_aggregation.LogAggregator")
    @patch("common_utils.logging.log_aggregation.ElasticsearchHandler")
    @patch("common_utils.logging.log_aggregation.LogstashHandler")
    @patch("common_utils.logging.log_aggregation.FileRotatingHandler")
    def test_aggregate_logs(self, mock_file_handler, mock_logstash_handler, mock_es_handler, mock_aggregator):
        """Test aggregate_logs function."""
        # Mock the aggregator and handlers
        mock_aggregator_instance = MagicMock()
        mock_aggregator.return_value = mock_aggregator_instance

        mock_es_handler_instance = MagicMock()
        mock_es_handler.return_value = mock_es_handler_instance

        mock_logstash_handler_instance = MagicMock()
        mock_logstash_handler.return_value = mock_logstash_handler_instance

        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance

        # Mock the elasticsearch module
        mock_elasticsearch = MagicMock()
        mock_es_client = MagicMock()
        mock_elasticsearch.Elasticsearch.return_value = mock_es_client

        # Mock the import
        with patch.dict('sys.modules', {'elasticsearch': mock_elasticsearch}):
            # Call the function under test
            aggregate_logs(
                app_name="test_app",
                log_dir=self.temp_dir.name,
                es_host="elasticsearch",
                es_port=9200,
                es_index="logs",
                logstash_host="logstash",
                logstash_port=5000,
                output_file="aggregated.log",
            )

            # Verify that the aggregator was created
            mock_aggregator.assert_called_once_with(
                app_name="test_app",
                log_dir=self.temp_dir.name,
            )

            # Verify that the handlers were created and added
            mock_es_handler.assert_called_once_with(
                es_client=mock_es_client,
                index_name="logs",
            )
            mock_logstash_handler.assert_called_once_with(
                host="logstash",
                port=5000,
            )
            mock_file_handler.assert_called_once_with(
                filename="aggregated.log",
            )

            # Verify that the handlers were added to the aggregator
            mock_aggregator_instance.add_handler.assert_any_call(mock_es_handler_instance)
            mock_aggregator_instance.add_handler.assert_any_call(mock_logstash_handler_instance)
            mock_aggregator_instance.add_handler.assert_any_call(mock_file_handler_instance)

            # Verify that the log directory was aggregated
            mock_aggregator_instance.aggregate_log_directory.assert_called_once_with(self.temp_dir.name)

    @patch("common_utils.logging.log_aggregation.aggregate_logs")
    @patch("threading.Thread")
    def test_configure_log_aggregation(self, mock_thread, mock_aggregate_logs):
        """Test configure_log_aggregation function."""
        # Mock the thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Call the function under test
        configure_log_aggregation(
            app_name="test_app",
            log_dir=self.temp_dir.name,
            es_host="elasticsearch",
            es_port=9200,
            es_index="logs",
            logstash_host="logstash",
            logstash_port=5000,
            output_file="aggregated.log",
        )

        # Verify that a thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

        # Verify that the thread was created with daemon=True
        _, kwargs = mock_thread.call_args
        assert kwargs["daemon"] is True
