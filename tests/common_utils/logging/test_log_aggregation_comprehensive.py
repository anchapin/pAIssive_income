"""Comprehensive test module for common_utils.logging.log_aggregation."""

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


class TestLogAggregationFunctions:
    """Test suite for log aggregation utility functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a sample log file
        self.log_file = os.path.join(self.temp_dir.name, "test.log")
        with open(self.log_file, "w") as f:
            f.write("2023-01-01 12:00:00 - test_module - INFO - Test message 1\n")
            f.write("2023-01-01 12:01:00 - test_module - ERROR - Test message 2\n")
            f.write("2023-01-01 12:02:00 - other_module - WARNING - Test message 3\n")
            f.write("Invalid log line\n")
            f.write("2023-01-01 12:03:00 - test_module - INFO - Test message 4\n")
            f.write("    Continuation of previous message\n")

    def teardown_method(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def test_parse_log_file(self):
        """Test parsing a log file."""
        # Parse the log file
        log_entries = parse_log_file(self.log_file)

        # Verify the parsed entries
        assert len(log_entries) == 4

        # Check the first entry
        assert log_entries[0]["timestamp"] == "2023-01-01T12:00:00"
        assert log_entries[0]["level"] == "INFO"
        assert log_entries[0]["message"] == "Test message 1"
        assert log_entries[0]["n"] == "test_module"

        # Check the last entry
        assert log_entries[3]["timestamp"] == "2023-01-01T12:03:00"
        assert log_entries[3]["level"] == "INFO"
        assert log_entries[3]["message"] == "Test message 4\n    Continuation of previous message"
        assert log_entries[3]["n"] == "test_module"

    def test_parse_log_file_error(self):
        """Test parsing a log file with an error."""
        # Create a non-existent file path
        non_existent_file = os.path.join(self.temp_dir.name, "non_existent.log")

        # Mock the logger
        with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Parse the non-existent file
            log_entries = parse_log_file(non_existent_file)

            # Verify that an error was logged
            mock_logger.error.assert_called_once()
            assert "Error parsing log file" in mock_logger.error.call_args[0][0]

            # Verify that an empty list was returned
            assert log_entries == []

    def test_get_log_files(self):
        """Test getting log files from a directory."""
        # Create additional log files
        with open(os.path.join(self.temp_dir.name, "test2.log"), "w") as f:
            f.write("2023-01-01 12:00:00 - test_module - INFO - Test message\n")

        with open(os.path.join(self.temp_dir.name, "test3.log"), "w") as f:
            f.write("2023-01-01 12:00:00 - test_module - INFO - Test message\n")

        # Create a non-log file
        with open(os.path.join(self.temp_dir.name, "test.txt"), "w") as f:
            f.write("Not a log file\n")

        # Get the log files
        log_files = get_log_files(self.temp_dir.name)

        # Verify the log files
        assert len(log_files) == 3
        assert os.path.join(self.temp_dir.name, "test.log") in log_files
        assert os.path.join(self.temp_dir.name, "test2.log") in log_files
        assert os.path.join(self.temp_dir.name, "test3.log") in log_files
        assert os.path.join(self.temp_dir.name, "test.txt") not in log_files

    def test_get_log_statistics(self):
        """Test getting statistics for log entries."""
        # Create log entries
        log_entries = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "level": "INFO",
                "message": "Test message 1",
                "name": "test_module",
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "level": "ERROR",
                "message": "Test message 2",
                "name": "test_module",
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "level": "WARNING",
                "message": "Test message 3",
                "name": "other_module",
            },
            {
                "timestamp": "2023-01-02T13:00:00",
                "level": "INFO",
                "message": "Test message 4",
                "name": "test_module",
            },
        ]

        # Get the statistics
        stats = get_log_statistics(log_entries)

        # Verify the statistics
        assert stats["total"] == 4

        # Check level counts
        assert stats["by_level"]["INFO"] == 2
        assert stats["by_level"]["ERROR"] == 1
        assert stats["by_level"]["WARNING"] == 1

        # Check module counts
        assert stats["by_module"]["test_module"] == 3
        assert stats["by_module"]["other_module"] == 1

        # Check hour counts
        assert stats["by_hour"][12] == 2
        assert stats["by_hour"][13] == 2

        # Check date counts
        assert stats["by_date"]["2023-01-01"] == 2
        assert stats["by_date"]["2023-01-02"] == 2

    def test_get_log_statistics_empty(self):
        """Test getting statistics for an empty list of log entries."""
        # Get the statistics for an empty list
        stats = get_log_statistics([])

        # Verify the statistics
        assert stats["total"] == 0
        assert stats["by_level"] == {}
        assert stats["by_module"] == {}
        assert stats["by_hour"] == {}
        assert stats["by_date"] == {}


class TestLogAggregator:
    """Test suite for LogAggregator class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a LogAggregator instance
        self.aggregator = LogAggregator(
            app_name="test_app",
            log_dir=self.temp_dir.name,
        )

        # Create a sample log file
        self.log_file = os.path.join(self.temp_dir.name, "test.log")
        with open(self.log_file, "w") as f:
            f.write("2023-01-01 12:00:00 - test_module - INFO - Test message 1\n")
            f.write("2023-01-01 12:01:00 - test_module - ERROR - Test message 2\n")

    def teardown_method(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def test_add_remove_handler(self):
        """Test adding and removing handlers."""
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

        # Try to remove a non-existent handler
        self.aggregator.remove_handler(MagicMock())

    def test_aggregate_log_entry(self):
        """Test aggregating a log entry."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
        }

        # Aggregate the log entry
        self.aggregator.aggregate_log_entry(log_entry)

        # Verify that the handler's handle method was called
        mock_handler.handle.assert_called_once_with(log_entry)

        # Verify that the app name was added to the log entry
        assert log_entry["app"] == "test_app"

    def test_aggregate_log_entry_with_app(self):
        """Test aggregating a log entry with an app name already set."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Create a log entry with an app name
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "custom_app",
        }

        # Aggregate the log entry
        self.aggregator.aggregate_log_entry(log_entry)

        # Verify that the app name was not changed
        assert log_entry["app"] == "custom_app"

    def test_aggregate_log_entry_handler_error(self):
        """Test aggregating a log entry with a handler error."""
        # Create a mock handler that raises an exception
        mock_handler = MagicMock()
        mock_handler.handle.side_effect = Exception("Test error")

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
        }

        # Mock the logger
        with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Aggregate the log entry
            self.aggregator.aggregate_log_entry(log_entry)

            # Verify that an error was logged
            mock_logger.error.assert_called_once()
            assert "Error handling log entry" in mock_logger.error.call_args[0][0]

    @patch("common_utils.logging.log_aggregation.parse_log_file")
    def test_aggregate_log_file(self, mock_parse_log_file):
        """Test aggregating a log file."""
        # Mock the parse_log_file function
        mock_parse_log_file.return_value = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "level": "INFO",
                "message": "Test message 1",
                "logger": "test_logger",
            },
            {
                "timestamp": "2023-01-01T12:01:00",
                "level": "ERROR",
                "message": "Test message 2",
                "logger": "test_logger",
            },
        ]

        # Create a mock handler
        mock_handler = MagicMock()

        # Add the handler
        self.aggregator.add_handler(mock_handler)

        # Aggregate the log file
        self.aggregator.aggregate_log_file(self.log_file)

        # Verify that parse_log_file was called
        mock_parse_log_file.assert_called_once_with(self.log_file)

        # Verify that the handler's handle method was called for each log entry
        assert mock_handler.handle.call_count == 2

        # Mock the logger
        with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Aggregate the log file
            self.aggregator.aggregate_log_file(self.log_file)

            # Verify that a message was logged
            mock_logger.info.assert_called_once()
            assert f"Aggregated 2 log entries from {self.log_file}" in mock_logger.info.call_args[0][0]

    @patch("common_utils.logging.log_aggregation.glob.glob")
    def test_aggregate_log_directory(self, mock_glob):
        """Test aggregating a log directory."""
        # Mock the glob function
        mock_glob.return_value = [
            os.path.join(self.temp_dir.name, "test1.log"),
            os.path.join(self.temp_dir.name, "test2.log"),
        ]

        # Mock the aggregate_log_file method
        with patch.object(self.aggregator, "aggregate_log_file") as mock_aggregate_log_file:
            # Aggregate the log directory
            self.aggregator.aggregate_log_directory(self.temp_dir.name)

            # Verify that glob was called
            mock_glob.assert_called_once_with(os.path.join(self.temp_dir.name, "*.log"))

            # Verify that aggregate_log_file was called for each log file
            assert mock_aggregate_log_file.call_count == 2
            mock_aggregate_log_file.assert_has_calls([
                call(os.path.join(self.temp_dir.name, "test1.log")),
                call(os.path.join(self.temp_dir.name, "test2.log")),
            ])

            # Mock the logger
            with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
                # Aggregate the log directory
                self.aggregator.aggregate_log_directory(self.temp_dir.name)

                # Verify that a message was logged
                mock_logger.info.assert_called_once()
                assert f"Aggregated logs from 2 files in {self.temp_dir.name}" in mock_logger.info.call_args[0][0]


class TestElasticsearchHandler:
    """Test suite for ElasticsearchHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock Elasticsearch client
        self.mock_es_client = MagicMock()

        # Create an ElasticsearchHandler instance
        self.handler = ElasticsearchHandler(
            es_client=self.mock_es_client,
            index_name="logs",
        )

    def test_handle(self):
        """Test handling a log entry."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Handle the log entry
        self.handler.handle(log_entry)

        # Verify that the Elasticsearch client's index method was called
        self.mock_es_client.index.assert_called_once_with(
            index="logs",
            document=log_entry,
        )

    def test_handle_error(self):
        """Test handling a log entry with an error."""
        # Make the Elasticsearch client's index method raise an exception
        self.mock_es_client.index.side_effect = Exception("Test error")

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Mock the logger
        with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Handle the log entry
            self.handler.handle(log_entry)

            # Verify that an error was logged
            mock_logger.error.assert_called_once()
            assert "Error indexing log entry in Elasticsearch" in mock_logger.error.call_args[0][0]


class TestLogstashHandler:
    """Test suite for LogstashHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a LogstashHandler instance
        self.handler = LogstashHandler(
            host="localhost",
            port=5000,
        )

    @patch("socket.socket")
    def test_handle(self, mock_socket):
        """Test handling a log entry."""
        # Mock the socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Handle the log entry
        self.handler.handle(log_entry)

        # Verify that the socket was created and used
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_socket_instance.sendto.assert_called_once()
        mock_socket_instance.close.assert_called_once()

        # Verify the data sent
        call_args = mock_socket_instance.sendto.call_args[0]
        sent_data = json.loads(call_args[0].decode("utf-8"))
        assert sent_data == log_entry
        assert call_args[1] == ("localhost", 5000)

    def test_handle_with_socket(self):
        """Test handling a log entry with a provided socket."""
        # Create a mock socket
        mock_socket = MagicMock()

        # Create a LogstashHandler instance with a socket
        handler = LogstashHandler(
            host="localhost",
            port=5000,
            socket=mock_socket,
        )

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Handle the log entry
        handler.handle(log_entry)

        # Verify that the socket was used
        mock_socket.sendto.assert_called_once()

        # Verify that the socket was not closed
        mock_socket.close.assert_not_called()

    @patch("socket.socket")
    def test_handle_error(self, mock_socket):
        """Test handling a log entry with an error."""
        # Mock the socket to raise an exception
        mock_socket.side_effect = Exception("Test error")

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Mock the logger
        with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Handle the log entry
            self.handler.handle(log_entry)

            # Verify that an error was logged
            mock_logger.error.assert_called_once()
            assert "Error sending log entry to Logstash" in mock_logger.error.call_args[0][0]


class TestFileRotatingHandler:
    """Test suite for FileRotatingHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a FileRotatingHandler instance
        self.handler = FileRotatingHandler(
            filename=os.path.join(self.temp_dir.name, "aggregated.log"),
            max_bytes=1024,
            backup_count=3,
        )

    def teardown_method(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def test_handle(self):
        """Test handling a log entry."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "pathname": "test_file.py",
            "lineno": 42,
            "app": "test_app",
        }

        # Handle the log entry
        self.handler.handle(log_entry)

        # Verify that the log file was created
        log_file = os.path.join(self.temp_dir.name, "aggregated.log")
        assert os.path.exists(log_file)

        # Verify the log file contents
        with open(log_file, "r") as f:
            log_content = f.read()
            assert "test_logger" in log_content
            assert "INFO" in log_content
            assert "Test message" in log_content

    def test_handle_error(self):
        """Test handling a log entry with an error."""
        # Mock the handler's emit method to raise an exception
        with patch.object(self.handler.handler, "emit") as mock_emit:
            mock_emit.side_effect = Exception("Test error")

            # Create a log entry
            log_entry = {
                "timestamp": "2023-01-01T12:00:00",
                "level": "INFO",
                "message": "Test message",
                "logger": "test_logger",
                "app": "test_app",
            }

            # Mock the logger
            with patch("common_utils.logging.log_aggregation.logger") as mock_logger:
                # Handle the log entry
                self.handler.handle(log_entry)

                # Verify that an error was logged
                mock_logger.error.assert_called_once()
                assert "Error writing log entry to file" in mock_logger.error.call_args[0][0]


class TestAggregateLogs:
    """Test suite for aggregate_logs function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a sample log file
        self.log_file = os.path.join(self.temp_dir.name, "test.log")
        with open(self.log_file, "w") as f:
            f.write("2023-01-01 12:00:00 - test_module - INFO - Test message\n")

    def teardown_method(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    @patch("common_utils.logging.log_aggregation.LogAggregator")
    @patch("common_utils.logging.log_aggregation.ElasticsearchHandler")
    @patch("common_utils.logging.log_aggregation.LogstashHandler")
    @patch("common_utils.logging.log_aggregation.FileRotatingHandler")
    def test_aggregate_logs_with_all_handlers(
        self,
        mock_file_handler,
        mock_logstash_handler,
        mock_es_handler,
        mock_aggregator,
    ):
        """Test aggregating logs with all handlers."""
        # Mock the Elasticsearch client
        mock_es_client = MagicMock()

        # Mock the Elasticsearch module
        mock_elasticsearch = MagicMock()
        mock_elasticsearch.Elasticsearch.return_value = mock_es_client

        # Mock the aggregator instance
        mock_aggregator_instance = MagicMock()
        mock_aggregator.return_value = mock_aggregator_instance

        # Mock the handler instances
        mock_es_handler_instance = MagicMock()
        mock_es_handler.return_value = mock_es_handler_instance

        mock_logstash_handler_instance = MagicMock()
        mock_logstash_handler.return_value = mock_logstash_handler_instance

        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance

        # Mock the import
        with patch.dict("sys.modules", {"elasticsearch": mock_elasticsearch}):
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

            # Verify that the Elasticsearch client was created
            mock_elasticsearch.Elasticsearch.assert_called_once_with(
                ["http://elasticsearch:9200"]
            )

            # Verify that the handlers were created
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
            mock_aggregator_instance.add_handler.assert_has_calls([
                call(mock_es_handler_instance),
                call(mock_logstash_handler_instance),
                call(mock_file_handler_instance),
            ])

            # Verify that the aggregator's aggregate_log_directory method was called
            mock_aggregator_instance.aggregate_log_directory.assert_called_once_with(
                self.temp_dir.name
            )

    @patch("common_utils.logging.log_aggregation.LogAggregator")
    @patch("common_utils.logging.log_aggregation.LogstashHandler")
    @patch("common_utils.logging.log_aggregation.FileRotatingHandler")
    def test_aggregate_logs_without_elasticsearch(
        self,
        mock_file_handler,
        mock_logstash_handler,
        mock_aggregator,
    ):
        """Test aggregating logs without Elasticsearch."""
        # Mock the aggregator instance
        mock_aggregator_instance = MagicMock()
        mock_aggregator.return_value = mock_aggregator_instance

        # Mock the handler instances
        mock_logstash_handler_instance = MagicMock()
        mock_logstash_handler.return_value = mock_logstash_handler_instance

        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance

        # Call the function under test
        aggregate_logs(
            app_name="test_app",
            log_dir=self.temp_dir.name,
            es_host=None,
            logstash_host="logstash",
            logstash_port=5000,
            output_file="aggregated.log",
        )

        # Verify that the aggregator was created
        mock_aggregator.assert_called_once_with(
            app_name="test_app",
            log_dir=self.temp_dir.name,
        )

        # Verify that the handlers were created
        mock_logstash_handler.assert_called_once_with(
            host="logstash",
            port=5000,
        )

        mock_file_handler.assert_called_once_with(
            filename="aggregated.log",
        )

        # Verify that the handlers were added to the aggregator
        mock_aggregator_instance.add_handler.assert_has_calls([
            call(mock_logstash_handler_instance),
            call(mock_file_handler_instance),
        ])

        # Verify that the aggregator's aggregate_log_directory method was called
        mock_aggregator_instance.aggregate_log_directory.assert_called_once_with(
            self.temp_dir.name
        )

    @patch("common_utils.logging.log_aggregation.LogAggregator")
    @patch("common_utils.logging.log_aggregation.ElasticsearchHandler")
    def test_aggregate_logs_elasticsearch_import_error(
        self,
        mock_es_handler,
        mock_aggregator,
    ):
        """Test aggregating logs with an Elasticsearch import error."""
        # Mock the aggregator instance
        mock_aggregator_instance = MagicMock()
        mock_aggregator.return_value = mock_aggregator_instance

        # Mock the import to raise an ImportError
        with patch.dict("sys.modules", {"elasticsearch": None}), \
             patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Call the function under test
            aggregate_logs(
                app_name="test_app",
                log_dir=self.temp_dir.name,
                es_host="elasticsearch",
                es_port=9200,
                es_index="logs",
            )

            # Verify that an error was logged
            mock_logger.error.assert_called_once()
            assert "Elasticsearch module not found" in mock_logger.error.call_args[0][0]

            # Verify that the ElasticsearchHandler was not created
            mock_es_handler.assert_not_called()


class TestConfigureLogAggregation:
    """Test suite for configure_log_aggregation function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown_method(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    @patch("common_utils.logging.log_aggregation.aggregate_logs")
    @patch("common_utils.logging.log_aggregation.threading.Thread")
    def test_configure_log_aggregation(self, mock_thread, mock_aggregate_logs):
        """Test configuring log aggregation."""
        # Mock the thread instance
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

        # Verify that a thread was created
        mock_thread.assert_called_once()
        assert mock_thread.call_args[1]["daemon"] is True

        # Verify that the thread was started
        mock_thread_instance.start.assert_called_once()

        # Call the thread target function
        thread_target = mock_thread.call_args[1]["target"]

        # Mock time.sleep to avoid waiting
        with patch("time.sleep"):
            # Call the thread target function
            thread_target()

            # Verify that aggregate_logs was called
            mock_aggregate_logs.assert_called_once_with(
                app_name="test_app",
                log_dir=self.temp_dir.name,
                es_host="elasticsearch",
                es_port=9200,
                es_index="logs",
                logstash_host="logstash",
                logstash_port=5000,
                output_file="aggregated.log",
            )

    @patch("common_utils.logging.log_aggregation.aggregate_logs")
    @patch("common_utils.logging.log_aggregation.threading.Thread")
    def test_configure_log_aggregation_error(self, mock_thread, mock_aggregate_logs):
        """Test configuring log aggregation with an error."""
        # Mock the thread instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Make aggregate_logs raise an exception
        mock_aggregate_logs.side_effect = Exception("Test error")

        # Call the function under test
        configure_log_aggregation(
            app_name="test_app",
            log_dir=self.temp_dir.name,
        )

        # Verify that a thread was created
        mock_thread.assert_called_once()

        # Call the thread target function
        thread_target = mock_thread.call_args[1]["target"]

        # Mock time.sleep to avoid waiting
        with patch("time.sleep"), \
             patch("common_utils.logging.log_aggregation.logger") as mock_logger:
            # Call the thread target function
            thread_target()

            # Verify that an error was logged
            mock_logger.error.assert_called_once()
            assert "Error aggregating logs" in mock_logger.error.call_args[0][0]
