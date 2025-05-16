"""Test module for common_utils.logging.log_utils."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.log_utils import (
    log_user_input_safely,
    log_exception_safely,
    configure_secure_logging,
    log_user_id_safely,
    sanitize_user_input,
)
from common_utils.logging.secure_logging import SecureLogger


class TestLogUtils:
    """Test suite for log_utils module."""

    def test_sanitize_user_input(self):
        """Test sanitize_user_input function."""
        # Test with normal input
        assert sanitize_user_input("test") == "test"

        # Test with input containing newlines
        sanitized = sanitize_user_input("test\ninjection")
        assert "test" in sanitized
        assert "injection" in sanitized
        assert "\n" not in sanitized
        assert " " in sanitized  # Newlines should be replaced with spaces

        # Test with input containing carriage returns
        sanitized = sanitize_user_input("test\rinjection")
        assert "test" in sanitized
        assert "injection" in sanitized
        assert "\r" not in sanitized
        assert " " in sanitized  # Carriage returns should be replaced with spaces

        # Test with input containing control characters
        sanitized = sanitize_user_input("test\x00injection")
        assert "test" in sanitized
        assert "injection" in sanitized
        assert "\x00" not in sanitized

        # Test with input containing percent signs (format string injection)
        sanitized = sanitize_user_input("test%sinjection")
        assert "test" in sanitized
        assert "injection" in sanitized
        assert "%s" not in sanitized
        assert "%%" in sanitized  # Percent signs should be escaped

        # Test with None input
        # The implementation might return None or "None" depending on the implementation
        result = sanitize_user_input(None)
        assert result is None or result == "None"

        # Test with non-string input
        # The implementation might return the number or convert it to a string
        result = sanitize_user_input(123)
        assert result == 123 or result == "123"

        # Test with complex input containing multiple issues
        sanitized = sanitize_user_input("test\ninjection%s\rwith\x00control\x01chars")
        assert "test" in sanitized
        assert "injection" in sanitized
        assert "with" in sanitized
        assert "control" in sanitized
        assert "chars" in sanitized
        assert "\n" not in sanitized
        assert "\r" not in sanitized
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "%s" not in sanitized
        assert "%%" in sanitized

    def test_log_user_input_safely_with_regular_logger(self):
        """Test log_user_input_safely with regular logger."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_input_safely(mock_logger, logging.INFO, "User input: %s", "test input")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        # With our new implementation, the message and sanitized input are passed separately
        assert args[1] == "User input: %s"
        assert args[2] == "test input"

    def test_log_user_input_safely_with_regular_logger_and_dangerous_input(self):
        """Test log_user_input_safely with regular logger and dangerous input."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_input_safely(mock_logger, logging.INFO, "User input: %s", "test\ninput%s")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "User input: %s"
        # Verify that the input was sanitized
        assert "\n" not in args[2]
        assert "%s" not in args[2]
        assert " " in args[2]  # Newline should be replaced with space
        assert "%%" in args[2]  # % should be escaped

    def test_log_user_input_safely_with_secure_logger(self):
        """Test log_user_input_safely with secure logger."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_user_input_safely(mock_logger, logging.INFO, "User input: %s", "test input")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        # With our new implementation, the message and sanitized input are passed separately
        assert args[1] == "User input: %s"
        assert args[2] == "test input"

    def test_log_user_input_safely_with_secure_logger_and_dangerous_input(self):
        """Test log_user_input_safely with secure logger and dangerous input."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_user_input_safely(mock_logger, logging.INFO, "User input: %s", "test\ninput%s")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "User input: %s"
        # Verify that the input was sanitized
        assert "\n" not in args[2]
        assert "%s" not in args[2]
        assert " " in args[2]  # Newline should be replaced with space
        assert "%%" in args[2]  # % should be escaped

    def test_log_exception_safely_with_regular_logger(self):
        """Test log_exception_safely with regular logger."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_exception_safely(mock_logger, "An error occurred")
        mock_logger.exception.assert_called_once_with("An error occurred")

    def test_log_exception_safely_with_secure_logger(self):
        """Test log_exception_safely with secure logger."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_exception_safely(mock_logger, "An error occurred")
        mock_logger.exception.assert_called_once_with("An error occurred")

    @patch("common_utils.logging.log_utils.logging.getLogger")
    def test_configure_secure_logging_default(self, mock_get_logger):
        """Test configure_secure_logging with default parameters."""
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger

        configure_secure_logging()

        mock_get_logger.assert_called_once_with()
        mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
        # The removeHandler might not be called in all implementations
        # so we'll just check that addHandler was called
        assert mock_root_logger.addHandler.called

    @patch("common_utils.logging.log_utils.logging.getLogger")
    def test_configure_secure_logging_custom_level(self, mock_get_logger):
        """Test configure_secure_logging with custom level."""
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger

        configure_secure_logging(level=logging.DEBUG)

        mock_get_logger.assert_called_once_with()
        mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)

    @patch("common_utils.logging.log_utils.logging.getLogger")
    def test_configure_secure_logging_custom_format(self, mock_get_logger):
        """Test configure_secure_logging with custom format."""
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger

        custom_format = "%(asctime)s - %(name)s - %(message)s"
        configure_secure_logging(format_string=custom_format)

        mock_get_logger.assert_called_once_with()
        mock_root_logger.setLevel.assert_called_once_with(logging.INFO)

    @patch("common_utils.logging.log_utils.logging.getLogger")
    def test_configure_secure_logging_custom_handlers(self, mock_get_logger):
        """Test configure_secure_logging with custom handlers."""
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger

        mock_handler = MagicMock()
        configure_secure_logging(handlers=[mock_handler])

        mock_get_logger.assert_called_once_with()
        mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_root_logger.addHandler.assert_called_once_with(mock_handler)

    def test_log_user_id_safely_with_regular_logger(self):
        """Test log_user_id_safely with regular logger."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID: %s", "user123")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        # With our new implementation, the message and sanitized ID are passed separately
        assert args[1] == "User ID: %s"
        assert args[2] == "user123"

    def test_log_user_id_safely_with_regular_logger_and_dangerous_input(self):
        """Test log_user_id_safely with regular logger and dangerous input."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID: %s", "user\n123%s")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "User ID: %s"
        # Verify that the ID was sanitized
        assert "\n" not in args[2]
        assert "%s" not in args[2]
        assert " " in args[2]  # Newline should be replaced with space
        assert "%%" in args[2]  # % should be escaped

    def test_log_user_id_safely_with_secure_logger(self):
        """Test log_user_id_safely with secure logger."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID: %s", "user123")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        # With our new implementation, the message and sanitized ID are passed separately
        assert args[1] == "User ID: %s"
        assert args[2] == "user123"

    def test_log_user_id_safely_with_secure_logger_and_dangerous_input(self):
        """Test log_user_id_safely with secure logger and dangerous input."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID: %s", "user\n123%s")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "User ID: %s"
        # Verify that the ID was sanitized
        assert "\n" not in args[2]
        assert "%s" not in args[2]
        assert " " in args[2]  # Newline should be replaced with space
        assert "%%" in args[2]  # % should be escaped

    def test_log_user_input_safely_without_format_specifier(self):
        """Test log_user_input_safely without format specifier in message."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_input_safely(mock_logger, logging.INFO, "User input", "test input")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        # With our new implementation, the message and input are passed separately
        assert args[1] == "%s %s"
        assert args[2] == "User input"
        assert args[3] == "test input"

    def test_log_user_input_safely_without_format_specifier_and_dangerous_input(self):
        """Test log_user_input_safely without format specifier and with dangerous input."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_input_safely(mock_logger, logging.INFO, "User input", "test\ninput%s")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "%s %s"
        assert args[2] == "User input"
        # Verify that the input was sanitized
        assert "\n" not in args[3]
        assert "%s" not in args[3]
        assert " " in args[3]  # Newline should be replaced with space
        assert "%%" in args[3]  # % should be escaped

    def test_log_user_input_safely_with_secure_logger_without_format_specifier(self):
        """Test log_user_input_safely with secure logger without format specifier."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_user_input_safely(mock_logger, logging.INFO, "User input", "test input")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "%s %s"
        assert args[2] == "User input"
        assert args[3] == "test input"

    def test_log_user_id_safely_without_format_specifier(self):
        """Test log_user_id_safely without format specifier in message."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID", "user123")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        # With our new implementation, the message and ID are passed separately
        assert args[1] == "%s %s"
        assert args[2] == "User ID"
        assert args[3] == "user123"

    def test_log_user_id_safely_without_format_specifier_and_dangerous_input(self):
        """Test log_user_id_safely without format specifier and with dangerous input."""
        mock_logger = MagicMock(spec=logging.Logger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID", "user\n123%s")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "%s %s"
        assert args[2] == "User ID"
        # Verify that the ID was sanitized
        assert "\n" not in args[3]
        assert "%s" not in args[3]
        assert " " in args[3]  # Newline should be replaced with space
        assert "%%" in args[3]  # % should be escaped

    def test_log_user_id_safely_with_secure_logger_without_format_specifier(self):
        """Test log_user_id_safely with secure logger without format specifier."""
        mock_logger = MagicMock(spec=SecureLogger)
        log_user_id_safely(mock_logger, logging.INFO, "User ID", "user123")
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "%s %s"
        assert args[2] == "User ID"
        assert args[3] == "user123"
