"""Tests for the enhanced secure logging functionality."""

import logging
import unittest
from unittest.mock import patch, MagicMock

import pytest

from common_utils.logging.secure_logging import (
    SecureLogger,
    get_secure_logger,
    mask_sensitive_data,
    prevent_log_injection,
)


class TestSecureLoggingEnhancements(unittest.TestCase):
    """Test cases for the enhanced secure logging functionality."""

    def test_prevent_log_injection_with_newlines(self):
        """Test that prevent_log_injection removes newlines."""
        # Test with a string containing newlines
        test_string = "This is a test\nwith newlines\r\nand carriage returns"
        expected = "This is a test [FILTERED] with newlines [FILTERED] and carriage returns"

        result = prevent_log_injection(test_string)

        assert result == expected

    def test_prevent_log_injection_with_control_chars(self):
        """Test that prevent_log_injection removes control characters."""
        # Test with a string containing control characters
        test_string = "This is a test\x00with\x01control\x02characters"
        expected = "This is a test [FILTERED] with [FILTERED] control [FILTERED] characters"

        result = prevent_log_injection(test_string)

        assert result == expected

    def test_prevent_log_injection_with_dict(self):
        """Test that prevent_log_injection works with dictionaries."""
        # Test with a dictionary containing strings with newlines
        test_dict = {
            "key1": "value1\nwith newline",
            "key2": "value2\r\nwith carriage return",
            "key3": "normal value"
        }

        expected = {
            "key1": "value1 [FILTERED] with newline",
            "key2": "value2 [FILTERED] with carriage return",
            "key3": "normal value"
        }

        result = prevent_log_injection(test_dict)

        assert result == expected

    def test_prevent_log_injection_with_list(self):
        """Test that prevent_log_injection works with lists."""
        # Test with a list containing strings with newlines
        test_list = [
            "value1\nwith newline",
            "value2\r\nwith carriage return",
            "normal value"
        ]

        expected = [
            "value1 [FILTERED] with newline",
            "value2 [FILTERED] with carriage return",
            "normal value"
        ]

        result = prevent_log_injection(test_list)

        assert result == expected

    def test_mask_sensitive_data_calls_prevent_log_injection(self):
        """Test that mask_sensitive_data calls prevent_log_injection."""
        # Create a test string with both sensitive data and log injection patterns
        test_string = "password=secret123\napi_key=abcdef"

        # The expected result should have both the sensitive data masked and the newline removed
        expected = "password=****secret123 [FILTERED] api_key=****abcdef"

        # Call mask_sensitive_data
        result = mask_sensitive_data(test_string)

        # Check that the result has both the sensitive data masked and the newline removed
        assert "****" in result
        assert "\n" not in result
        assert " [FILTERED] " in result

    def test_secure_logger_prevents_log_injection(self):
        """Test that SecureLogger prevents log injection."""
        # Create a mock logger
        mock_logger = MagicMock()

        # Create a SecureLogger with the mock logger
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Log a message with a newline
        test_message = "This is a test\nwith a newline"
        secure_logger.info(test_message)

        # Check that the mock logger was called with the sanitized message
        mock_logger.info.assert_called_once()
        args, _ = mock_logger.info.call_args
        assert "\n" not in args[0]
        assert " [FILTERED] " in args[0]

    def test_secure_logger_masks_sensitive_data(self):
        """Test that SecureLogger masks sensitive data."""
        # Create a mock logger
        mock_logger = MagicMock()

        # Create a SecureLogger with the mock logger
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Log a message with sensitive data
        test_message = "password=secret123"
        secure_logger.info(test_message)

        # Check that the mock logger was called with the masked message
        mock_logger.info.assert_called_once()
        args, _ = mock_logger.info.call_args
        # The actual masking pattern shows first 4 chars and masks the rest
        assert "password=secr" in args[0]
        assert "*" in args[0]  # Some masking is applied
        assert "secret123" not in args[0]  # Full password is not visible

    def test_get_secure_logger_returns_secure_logger(self):
        """Test that get_secure_logger returns a SecureLogger instance."""
        logger = get_secure_logger("test_logger")
        assert isinstance(logger, SecureLogger)

    def test_secure_logger_with_real_logging(self):
        """Test SecureLogger with real logging."""
        # Create a StringIO to capture log output
        import io
        log_stream = io.StringIO()

        # Create a handler that writes to the StringIO
        handler = logging.StreamHandler(log_stream)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        # Create a SecureLogger and add the handler
        logger = get_secure_logger("test_logger")
        logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.INFO)

        # Log a message with both sensitive data and log injection patterns
        logger.info("password=secret123\napi_key=abcdef")

        # Get the log output
        log_output = log_stream.getvalue()

        # Check that the sensitive data is masked and the newline is removed
        assert "password=secr" in log_output
        assert "*" in log_output  # Some masking is applied
        assert "secret123" not in log_output  # Full password is not visible
        assert "\n" not in log_output or " [FILTERED] " in log_output  # Either newlines are removed or replaced


if __name__ == "__main__":
    unittest.main()
