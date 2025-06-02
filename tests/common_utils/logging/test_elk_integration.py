"""Test module for ELK stack integration in centralized_logging."""

import datetime
import json
import logging
import os
import socket
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, call, patch

import pytest

from common_utils.logging.centralized_logging import (
    CentralizedLoggingService,
    ElasticsearchOutput,
    LoggingClient,
    LogstashOutput,
)


@pytest.mark.skipif(
    not hasattr(pytest, "ELASTICSEARCH_AVAILABLE") or not pytest.ELASTICSEARCH_AVAILABLE,
    reason="Elasticsearch package not installed",
)
class TestElasticsearchOutput:
    """Test suite for ElasticsearchOutput class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock Elasticsearch
        self.es_patcher = patch("common_utils.logging.centralized_logging.Elasticsearch")
        self.mock_es_class = self.es_patcher.start()
        self.mock_es = MagicMock()
        self.mock_es_class.return_value = self.mock_es

        # Create an ElasticsearchOutput instance
        self.output = ElasticsearchOutput(
            hosts=["localhost:9200"],
            index_prefix="logs",
            batch_size=2,
            flush_interval=0.1,
        )

    def teardown_method(self):
        """Tear down test fixtures."""
        # Stop the output
        self.output.close()

        # Stop the patcher
        self.es_patcher.stop()

    def test_output(self):
        """Test outputting a log entry."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Output the log entry
        self.output.output(log_entry)

        # Verify that the log entry was added to the batch
        assert len(self.output.batch) == 1
        assert self.output.batch[0] == log_entry

        # Output another log entry to trigger a flush
        self.output.output(log_entry)

        # Wait for the flush to complete
        time.sleep(0.2)

        # Verify that the batch was flushed
        assert len(self.output.batch) == 0

        # Verify that the bulk method was called
        self.mock_es.bulk.assert_called_once()

        # Verify the bulk request
        bulk_data = self.mock_es.bulk.call_args[1]["body"]
        assert len(bulk_data) == 4  # 2 index actions + 2 log entries
        assert bulk_data[0]["index"]["_index"].startswith("logs-")
        assert bulk_data[1] == log_entry
        assert bulk_data[2]["index"]["_index"].startswith("logs-")
        assert bulk_data[3] == log_entry

    def test_flush_thread(self):
        """Test the flush thread."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Output the log entry
        self.output.output(log_entry)

        # Wait for the flush thread to flush the batch
        time.sleep(0.2)

        # Verify that the batch was flushed
        assert len(self.output.batch) == 0

        # Verify that the bulk method was called
        self.mock_es.bulk.assert_called_once()

    def test_close(self):
        """Test closing the output."""
        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Output the log entry
        self.output.output(log_entry)

        # Close the output
        self.output.close()

        # Verify that the running flag is set to False
        assert not self.output.running

        # Verify that the bulk method was called
        self.mock_es.bulk.assert_called_once()


@pytest.mark.skipif(
    not hasattr(pytest, "LOGSTASH_AVAILABLE") or not pytest.LOGSTASH_AVAILABLE,
    reason="Logstash package not installed",
)
class TestLogstashOutput:
    """Test suite for LogstashOutput class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock logstash handlers
        self.udp_patcher = patch("common_utils.logging.centralized_logging.logstash.UDPLogstashHandler")
        self.tcp_patcher = patch("common_utils.logging.centralized_logging.logstash.TCPLogstashHandler")
        self.mock_udp_handler_class = self.udp_patcher.start()
        self.mock_tcp_handler_class = self.tcp_patcher.start()
        self.mock_udp_handler = MagicMock()
        self.mock_tcp_handler = MagicMock()
        self.mock_udp_handler_class.return_value = self.mock_udp_handler
        self.mock_tcp_handler_class.return_value = self.mock_tcp_handler

    def teardown_method(self):
        """Tear down test fixtures."""
        # Stop the patchers
        self.udp_patcher.stop()
        self.tcp_patcher.stop()

    def test_init_udp(self):
        """Test initializing with UDP protocol."""
        # Create a LogstashOutput instance with UDP protocol
        output = LogstashOutput(
            host="localhost",
            port=5000,
            protocol="udp",
        )

        # Verify that the UDP handler was created
        self.mock_udp_handler_class.assert_called_once_with("localhost", 5000)
        assert output.handler == self.mock_udp_handler

    def test_init_tcp(self):
        """Test initializing with TCP protocol."""
        # Create a LogstashOutput instance with TCP protocol
        output = LogstashOutput(
            host="localhost",
            port=5000,
            protocol="tcp",
        )

        # Verify that the TCP handler was created
        self.mock_tcp_handler_class.assert_called_once_with("localhost", 5000)
        assert output.handler == self.mock_tcp_handler

    def test_output(self):
        """Test outputting a log entry."""
        # Create a LogstashOutput instance
        output = LogstashOutput(
            host="localhost",
            port=5000,
            protocol="udp",
        )

        # Create a log entry
        log_entry = {
            "timestamp": "2023-01-01T12:00:00",
            "level": "INFO",
            "message": "Test message",
            "logger": "test_logger",
            "app": "test_app",
        }

        # Output the log entry
        output.output(log_entry)

        # Verify that the emit method was called
        self.mock_udp_handler.emit.assert_called_once()

        # Verify the log record
        record = self.mock_udp_handler.emit.call_args[0][0]
        assert record.name == "test_logger"
        assert record.levelno == logging.INFO
        assert record.msg == "Test message"
        assert hasattr(record, "app")
        assert record.app == "test_app"

    def test_close(self):
        """Test closing the output."""
        # Create a LogstashOutput instance
        output = LogstashOutput(
            host="localhost",
            port=5000,
            protocol="udp",
        )

        # Close the output
        output.close()

        # Verify that the close method was called
        self.mock_udp_handler.close.assert_called_once()
