"""Comprehensive test module for common_utils.logging.log_utils."""

import logging
import re
from unittest.mock import MagicMock, patch, call

import pytest

from common_utils.logging.log_utils import (
    get_logger,
    log_user_input_safely,
    log_exception_safely,
    configure_secure_logging,
    log_user_id_safely,
    sanitize_user_input,
)
from common_utils.logging.secure_logging import SecureLogger


class TestLogUtilsComprehensive:
    """Comprehensive test suite for log_utils module."""

    def setup_method(self):
        """Set up test environment."""
        # Create a mock logger for testing
        self.mock_logger = MagicMock(spec=SecureLogger)

        # Reset the root logger to avoid affecting other tests
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.WARNING)

    def test_get_logger(self):
        """Test get_logger function."""
        with patch("common_utils.logging.log_utils.get_secure_logger") as mock_get_secure_logger:
            mock_instance = MagicMock()
            mock_get_secure_logger.return_value = mock_instance

            # Call the function
            logger = get_logger("test_module")

            # Verify the result
            assert logger == mock_instance
            mock_get_secure_logger.assert_called_once_with("test_module")

    def test_sanitize_user_input_string(self):
        """Test sanitize_user_input with string input."""
        # Test with a string containing potentially harmful characters
        input_str = "User input with \nnewlines\r and [brackets] and {braces} and % percent signs"
        expected = "User input with  newlines  and \\[brackets\\] and \\{braces\\} and %% percent signs"

        with patch("common_utils.logging.log_utils.prevent_log_injection") as mock_prevent:
            mock_prevent.return_value = expected

            # Call the function
            result = sanitize_user_input(input_str)

            # Verify the result
            mock_prevent.assert_called_once()
            assert result == expected

    def test_sanitize_user_input_non_string(self):
        """Test sanitize_user_input with non-string input."""
        # Test with a non-string input
        input_value = 123

        with patch("common_utils.logging.log_utils.prevent_log_injection") as mock_prevent:
            mock_prevent.return_value = input_value

            # Call the function
            result = sanitize_user_input(input_value)

            # Verify the result
            mock_prevent.assert_called_once_with(input_value)
            assert result == input_value

    def test_log_user_input_safely_with_format_specifier(self):
        """Test log_user_input_safely with format specifier in message."""
        # Setup
        user_input = "malicious\ninput"
        sanitized_input = "sanitized_input"

        with patch("common_utils.logging.log_utils.sanitize_user_input") as mock_sanitize:
            mock_sanitize.return_value = sanitized_input

            # Call the function
            log_user_input_safely(self.mock_logger, logging.INFO, "User input: %s", user_input)

            # Verify the result
            mock_sanitize.assert_called_once_with(user_input)
            self.mock_logger.log.assert_called_once_with(logging.INFO, "User input: %s", sanitized_input)

    def test_log_user_input_safely_without_format_specifier(self):
        """Test log_user_input_safely without format specifier in message."""
        # Setup
        user_input = "malicious\ninput"
        sanitized_input = "sanitized_input"

        with patch("common_utils.logging.log_utils.sanitize_user_input") as mock_sanitize:
            mock_sanitize.return_value = sanitized_input

            # Call the function
            log_user_input_safely(self.mock_logger, logging.INFO, "User input:", user_input)

            # Verify the result
            mock_sanitize.assert_called_once_with(user_input)
            self.mock_logger.log.assert_called_once_with(logging.INFO, "User input: sanitized_input")

    def test_log_exception_safely(self):
        """Test log_exception_safely function."""
        # Call the function
        log_exception_safely(self.mock_logger, logging.ERROR, "An error occurred")

        # Verify the result
        self.mock_logger.exception.assert_called_once_with("An error occurred")

    def test_configure_secure_logging_default(self):
        """Test configure_secure_logging with default parameters."""
        # Setup
        mock_root_logger = MagicMock()
        mock_handler = MagicMock()
        mock_formatter = MagicMock()

        with patch("common_utils.logging.log_utils.logging.getLogger", return_value=mock_root_logger), \
             patch("common_utils.logging.log_utils.logging.StreamHandler", return_value=mock_handler), \
             patch("common_utils.logging.log_utils.logging.Formatter", return_value=mock_formatter):

            # Call the function
            configure_secure_logging()

            # Verify the result
            mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
            mock_root_logger.removeHandler.assert_not_called()  # No handlers to remove
            mock_handler.setFormatter.assert_called_once_with(mock_formatter)
            mock_root_logger.addHandler.assert_called_once_with(mock_handler)

    def test_configure_secure_logging_custom(self):
        """Test configure_secure_logging with custom parameters."""
        # Setup
        mock_root_logger = MagicMock()
        mock_handler = MagicMock()
        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        with patch("common_utils.logging.log_utils.logging.getLogger", return_value=mock_root_logger), \
             patch("common_utils.logging.log_utils.logging.StreamHandler", return_value=mock_handler), \
             patch("common_utils.logging.log_utils.logging.Formatter") as mock_formatter_class:

            # Call the function
            configure_secure_logging(level=logging.DEBUG, format_string=custom_format)

            # Verify the result
            mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)
            mock_formatter_class.assert_called_once_with(custom_format)
            mock_handler.setFormatter.assert_called_once()
            mock_root_logger.addHandler.assert_called_once_with(mock_handler)

    def test_configure_secure_logging_with_handlers(self):
        """Test configure_secure_logging with custom handlers."""
        # Setup
        mock_root_logger = MagicMock()
        mock_handler1 = MagicMock()
        mock_handler2 = MagicMock()

        with patch("common_utils.logging.log_utils.logging.getLogger", return_value=mock_root_logger):

            # Call the function
            configure_secure_logging(handlers=[mock_handler1, mock_handler2])

            # Verify the result
            mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
            assert mock_root_logger.addHandler.call_count == 2
            mock_root_logger.addHandler.assert_any_call(mock_handler1)
            mock_root_logger.addHandler.assert_any_call(mock_handler2)

    def test_log_user_id_safely_with_format_specifier(self):
        """Test log_user_id_safely with format specifier in message."""
        # Setup
        user_id = "user123"
        sanitized_id = "sanitized_id"

        with patch("common_utils.logging.log_utils.sanitize_user_input") as mock_sanitize:
            mock_sanitize.return_value = sanitized_id

            # Call the function
            log_user_id_safely(self.mock_logger, logging.INFO, "User ID: %s", user_id)

            # Verify the result
            mock_sanitize.assert_called_once_with(user_id)
            self.mock_logger.log.assert_called_once_with(logging.INFO, "User ID: %s", sanitized_id)

    def test_log_user_id_safely_without_format_specifier(self):
        """Test log_user_id_safely without format specifier in message."""
        # Setup
        user_id = "user123"
        sanitized_id = "sanitized_id"

        with patch("common_utils.logging.log_utils.sanitize_user_input") as mock_sanitize:
            mock_sanitize.return_value = sanitized_id

            # Call the function
            log_user_id_safely(self.mock_logger, logging.INFO, "User ID:", user_id)

            # Verify the result
            mock_sanitize.assert_called_once_with(user_id)
            self.mock_logger.log.assert_called_once_with(logging.INFO, "User ID: sanitized_id")
















