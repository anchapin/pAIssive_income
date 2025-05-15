"""Test module for common_utils.logging.__init__."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging import (
    SecureLogger,
    get_logger,
    secure_logger,
)


class TestLoggingInit:
    """Test suite for logging __init__ module."""

    def test_secure_logger_error_with_secure_context(self):
        """Test SecureLogger.error with secure_context."""
        logger = SecureLogger("test_secure_logger")
        
        # Mock the parent class's error method
        with patch.object(logging.Logger, 'error') as mock_error:
            logger.error("Test message", secure_context=True)
            mock_error.assert_called_once_with("[SECURE] Test message", secure_context=True)

    def test_secure_logger_warning_with_secure_context(self):
        """Test SecureLogger.warning with secure_context."""
        logger = SecureLogger("test_secure_logger")
        
        # Mock the parent class's warning method
        with patch.object(logging.Logger, 'warning') as mock_warning:
            logger.warning("Test message", secure_context=True)
            mock_warning.assert_called_once_with("[SECURE] Test message", secure_context=True)

    def test_secure_logger_info_with_secure_context(self):
        """Test SecureLogger.info with secure_context."""
        logger = SecureLogger("test_secure_logger")
        
        # Mock the parent class's info method
        with patch.object(logging.Logger, 'info') as mock_info:
            logger.info("Test message", secure_context=True)
            mock_info.assert_called_once_with("[SECURE] Test message", secure_context=True)

    def test_get_logger_from_cache(self):
        """Test get_logger returns cached logger."""
        # First call to get_logger will create a new logger
        logger1 = get_logger("test_cached_logger")
        
        # Mock the SecureLogger constructor to verify it's not called again
        with patch('common_utils.logging.SecureLogger') as mock_secure_logger:
            # Second call should return the cached logger
            logger2 = get_logger("test_cached_logger")
            
            # Verify the constructor wasn't called
            mock_secure_logger.assert_not_called()
            
            # Verify the same logger was returned
            assert logger1 is logger2

    def test_get_logger_non_secure(self):
        """Test get_logger with secure=False."""
        with patch('common_utils.logging.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            logger = get_logger("test_non_secure_logger", secure=False)
            
            mock_get_logger.assert_called_once_with("test_non_secure_logger")
            mock_logger.setLevel.assert_called_once_with(logging.INFO)

    def test_secure_logger_global_instance(self):
        """Test the global secure_logger instance."""
        assert isinstance(secure_logger, SecureLogger)
        assert secure_logger.name == "secure_logger"
