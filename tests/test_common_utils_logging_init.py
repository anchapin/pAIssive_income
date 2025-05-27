"""Tests for common_utils/logging/__init__.py module."""

import logging
import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
from common_utils.logging import (
    SENSITIVE_FIELDS,
    SecureLogger,
    get_logger,
    get_secure_logger,
    mask_sensitive_data,
)


class TestLoggingInit:
    """Test suite for common_utils/logging/__init__.py."""

    def test_get_logger_secure(self):
        """Test get_logger with secure=True."""
        # Clear the logger cache
        from common_utils.logging import _logger_cache
        _logger_cache.clear()

        # Test getting a secure logger
        logger = get_logger("test_secure_logger", secure=True)

        # Verify that the logger is a SecureLogger
        assert isinstance(logger, SecureLogger)

        # Verify that the logger is cached
        assert "test_secure_logger" in _logger_cache
        assert _logger_cache["test_secure_logger"] is logger

    def test_get_logger_standard(self):
        """Test get_logger with secure=False."""
        # Clear the logger cache
        from common_utils.logging import _logger_cache
        _logger_cache.clear()

        # Test getting a standard logger
        logger = get_logger("test_standard_logger", secure=False)

        # Verify that the logger is a standard Logger
        assert isinstance(logger, logging.Logger)
        assert not isinstance(logger, SecureLogger)

        # Verify that the logger is cached
        assert "test_standard_logger" in _logger_cache
        assert _logger_cache["test_standard_logger"] is logger

    def test_get_logger_cached(self):
        """Test that get_logger returns cached loggers."""
        # Clear the logger cache
        from common_utils.logging import _logger_cache
        _logger_cache.clear()

        # Create a logger
        logger1 = get_logger("test_cached_logger")

        # Get the same logger again
        logger2 = get_logger("test_cached_logger")

        # Verify that the same logger instance is returned
        assert logger1 is logger2

    @patch("common_utils.logging.SecureLogger")
    def test_get_logger_secure_fallback(self, mock_secure_logger):
        """Test that get_logger falls back to standard logger if SecureLogger fails."""
        # Clear the logger cache
        from common_utils.logging import _logger_cache
        _logger_cache.clear()

        # Make SecureLogger raise an exception
        mock_secure_logger.side_effect = Exception("SecureLogger failed")

        # Test getting a secure logger
        logger = get_logger("test_fallback_logger", secure=True)

        # Verify that a standard logger is returned
        assert isinstance(logger, logging.Logger)
        assert not isinstance(logger, SecureLogger)

        # Verify that the logger is cached
        assert "test_fallback_logger" in _logger_cache
        assert _logger_cache["test_fallback_logger"] is logger

    def test_module_exports(self):
        """Test that the module exports the expected symbols."""
        from common_utils.logging import __all__

        expected_exports = [
            "SENSITIVE_FIELDS",
            "SecureLogger",
            "get_logger",
            "get_secure_logger",
            "mask_sensitive_data",
        ]

        assert set(__all__) == set(expected_exports)
