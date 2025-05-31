"""Enhanced test module for common_utils.logging.__init__."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging import (
    SENSITIVE_FIELDS,
    SecureLogger,
    _logger_cache,
    get_logger,
    get_secure_logger,
    mask_sensitive_data,
    secure_logger,
)


class TestLoggingInitEnhanced:
    """Enhanced test suite for logging __init__ module."""

    def setup_method(self):
        """Set up test environment."""
        # Clear the logger cache before each test
        _logger_cache.clear()

    def test_get_logger_secure_exception_fallback(self):
        """Test get_logger falls back to standard logger when SecureLogger raises an exception."""
        # Mock SecureLogger to raise an exception
        with patch("common_utils.logging.SecureLogger", side_effect=Exception("Test exception")):
            # Mock standard logger
            mock_logger = MagicMock()
            with patch("common_utils.logging.logging.getLogger", return_value=mock_logger):
                # Call get_logger
                logger = get_logger("test_fallback_logger")

                # Verify standard logger was used
                assert logger is mock_logger
                mock_logger.setLevel.assert_called_once_with(logging.INFO)

                # Verify logger was cached
                assert "test_fallback_logger" in _logger_cache
                assert _logger_cache["test_fallback_logger"] is mock_logger

    def test_get_logger_with_different_secure_values(self):
        """Test get_logger with different secure parameter values."""
        # Get a secure logger
        secure_logger_instance = get_logger("test_secure_param", secure=True)
        assert isinstance(secure_logger_instance, SecureLogger)

        # Clear cache to test with secure=False
        _logger_cache.clear()

        # Mock standard logger
        mock_std_logger = MagicMock()
        with patch("common_utils.logging.logging.getLogger", return_value=mock_std_logger):
            # Get a non-secure logger
            non_secure_logger = get_logger("test_secure_param", secure=False)
            assert non_secure_logger is mock_std_logger

    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        from common_utils.logging import __all__

        expected_exports = [
            "SENSITIVE_FIELDS",
            "SecureLogger",
            "get_logger",
            "get_secure_logger",
            "mask_sensitive_data",
        ]

        for export in expected_exports:
            assert export in __all__

    def test_secure_logger_global_instance_methods(self):
        """Test methods of the global secure_logger instance."""
        with patch.object(SecureLogger, "info") as mock_info:
            secure_logger.info("Test info message")
            mock_info.assert_called_once_with("Test info message")

        with patch.object(SecureLogger, "warning") as mock_warning:
            secure_logger.warning("Test warning message")
            mock_warning.assert_called_once_with("Test warning message")

        with patch.object(SecureLogger, "error") as mock_error:
            secure_logger.error("Test error message")
            mock_error.assert_called_once_with("Test error message")

        with patch.object(SecureLogger, "debug") as mock_debug:
            secure_logger.debug("Test debug message")
            mock_debug.assert_called_once_with("Test debug message")

    def test_get_logger_same_name_different_secure_param(self):
        """Test get_logger with same name but different secure parameter."""
        # Get a secure logger
        secure_logger_instance = get_logger("test_same_name", secure=True)
        assert isinstance(secure_logger_instance, SecureLogger)

        # Try to get a non-secure logger with the same name
        # It should return the cached secure logger
        logger2 = get_logger("test_same_name", secure=False)

        # Verify the same logger was returned
        assert logger2 is secure_logger_instance

        # Clear cache and try the opposite order
        _logger_cache.clear()

        # Mock standard logger
        mock_std_logger = MagicMock()
        with patch("common_utils.logging.logging.getLogger", return_value=mock_std_logger):
            # Get a non-secure logger first
            non_secure_logger = get_logger("test_same_name2", secure=False)

            # Try to get a secure logger with the same name
            # It should return the cached non-secure logger
            logger2 = get_logger("test_same_name2", secure=True)

            # Verify the same logger was returned
            assert logger2 is non_secure_logger
