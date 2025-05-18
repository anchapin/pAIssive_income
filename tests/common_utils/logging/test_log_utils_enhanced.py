"""Enhanced test module for common_utils.logging.log_utils."""

import logging
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


class TestLogUtilsEnhanced:
    """Enhanced test suite for log_utils module."""

    def test_get_logger(self):
        """Test get_logger function."""
        with patch('common_utils.logging.secure_logging.get_secure_logger') as mock_get_secure_logger:
            mock_logger = MagicMock(spec=SecureLogger)
            mock_get_secure_logger.return_value = mock_logger
            
            # Call get_logger
            logger = get_logger("test_module")
            
            # Verify get_secure_logger was called
            mock_get_secure_logger.assert_called_once_with("test_module")
            
            # Verify the returned logger is the mock
            assert logger is mock_logger

    def test_log_user_input_safely_with_format_specifier(self):
        """Test log_user_input_safely with format specifier in message."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Mock sanitize_user_input
        user_input = "user<script>alert('xss')</script>"
        sanitized_input = "user&lt;script&gt;alert('xss')&lt;/script&gt;"
        
        with patch('common_utils.logging.log_utils.sanitize_user_input', return_value=sanitized_input) as mock_sanitize:
            # Call log_user_input_safely with format specifier
            log_user_input_safely(mock_logger, logging.INFO, "User input: %s", user_input)
            
            # Verify sanitize_user_input was called
            mock_sanitize.assert_called_once_with(user_input)
            
            # Verify logger.log was called with sanitized input
            mock_logger.log.assert_called_once_with(logging.INFO, "User input: %s", sanitized_input)

    def test_log_user_input_safely_without_format_specifier(self):
        """Test log_user_input_safely without format specifier in message."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Mock sanitize_user_input
        user_input = "user<script>alert('xss')</script>"
        sanitized_input = "user&lt;script&gt;alert('xss')&lt;/script&gt;"
        
        with patch('common_utils.logging.log_utils.sanitize_user_input', return_value=sanitized_input) as mock_sanitize:
            # Call log_user_input_safely without format specifier
            log_user_input_safely(mock_logger, logging.INFO, "User input:", user_input)
            
            # Verify sanitize_user_input was called
            mock_sanitize.assert_called_once_with(user_input)
            
            # Verify logger.log was called with formatted message
            mock_logger.log.assert_called_once_with(logging.INFO, "User input: user&lt;script&gt;alert('xss')&lt;/script&gt;")

    def test_log_user_input_safely_with_extra_args(self):
        """Test log_user_input_safely with extra args."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Mock sanitize_user_input
        user_input = "user input"
        sanitized_input = "sanitized input"
        
        with patch('common_utils.logging.log_utils.sanitize_user_input', return_value=sanitized_input):
            # Call log_user_input_safely with extra args
            extra = {"key": "value"}
            log_user_input_safely(mock_logger, logging.INFO, "User input: %s", user_input, extra=extra)
            
            # Verify logger.log was called with extra args
            mock_logger.log.assert_called_once_with(logging.INFO, "User input: %s", sanitized_input, extra=extra)

    def test_log_exception_safely(self):
        """Test log_exception_safely function."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Call log_exception_safely
        log_exception_safely(mock_logger, "An error occurred")
        
        # Verify logger.exception was called
        mock_logger.exception.assert_called_once_with("An error occurred")
        
    def test_log_exception_safely_with_extra_args(self):
        """Test log_exception_safely with extra args."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Call log_exception_safely with extra args
        extra = {"key": "value"}
        log_exception_safely(mock_logger, "An error occurred", extra=extra)
        
        # Verify logger.exception was called with extra args
        mock_logger.exception.assert_called_once_with("An error occurred", extra=extra)

    def test_configure_secure_logging_default(self):
        """Test configure_secure_logging with default parameters."""
        # Mock root logger
        mock_root_logger = MagicMock()
        
        with patch('common_utils.logging.log_utils.logging.getLogger', return_value=mock_root_logger) as mock_get_logger:
            # Call configure_secure_logging
            configure_secure_logging()
            
            # Verify getLogger was called with empty string (root logger)
            mock_get_logger.assert_called_once_with()
            
            # Verify root logger was configured
            mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
            
            # Verify existing handlers were removed
            mock_root_logger.removeHandler.assert_not_called()  # No handlers to remove

    def test_configure_secure_logging_with_handlers(self):
        """Test configure_secure_logging with custom handlers."""
        # Create mock handlers
        mock_existing_handler = MagicMock(spec=logging.Handler)
        mock_new_handler = MagicMock(spec=logging.Handler)
        
        # Mock root logger with existing handler
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = [mock_existing_handler]
        
        with patch('common_utils.logging.log_utils.logging.getLogger', return_value=mock_root_logger):
            # Call configure_secure_logging with custom handler
            configure_secure_logging(handlers=[mock_new_handler])
            
            # Verify existing handlers were removed
            mock_root_logger.removeHandler.assert_called_once_with(mock_existing_handler)
            
            # Verify new handler was added
            mock_root_logger.addHandler.assert_called_once_with(mock_new_handler)

    def test_log_user_id_safely_with_format_specifier(self):
        """Test log_user_id_safely with format specifier in message."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Mock sanitize_user_input
        user_id = "user-123<script>alert('xss')</script>"
        sanitized_id = "user-123&lt;script&gt;alert('xss')&lt;/script&gt;"
        
        with patch('common_utils.logging.log_utils.sanitize_user_input', return_value=sanitized_id) as mock_sanitize:
            # Call log_user_id_safely with format specifier
            log_user_id_safely(mock_logger, logging.INFO, "User ID: %s", user_id)
            
            # Verify sanitize_user_input was called
            mock_sanitize.assert_called_once_with(user_id)
            
            # Verify logger.log was called with sanitized input
            mock_logger.log.assert_called_once_with(logging.INFO, "User ID: %s", sanitized_id)

    def test_log_user_id_safely_without_format_specifier(self):
        """Test log_user_id_safely without format specifier in message."""
        # Create mock logger
        mock_logger = MagicMock(spec=SecureLogger)
        
        # Mock sanitize_user_input
        user_id = "user-123<script>alert('xss')</script>"
        sanitized_id = "user-123&lt;script&gt;alert('xss')&lt;/script&gt;"
        
        with patch('common_utils.logging.log_utils.sanitize_user_input', return_value=sanitized_id) as mock_sanitize:
            # Call log_user_id_safely without format specifier
            log_user_id_safely(mock_logger, logging.INFO, "User ID:", user_id)
            
            # Verify sanitize_user_input was called
            mock_sanitize.assert_called_once_with(user_id)
            
            # Verify logger.log was called with formatted message
            mock_logger.log.assert_called_once_with(logging.INFO, "User ID: user-123&lt;script&gt;alert('xss')&lt;/script&gt;")
