"""Test module for common_utils.logging.logger."""

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.logger import (
    _loggers,
    get_logger,
    setup_logger,
)


class TestLogger:
    """Test suite for logger module."""

    def setup_method(self):
        """Set up test environment."""
        # Clear the logger cache before each test
        _loggers.clear()

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_same_instance(self):
        """Test get_logger returns the same instance for the same name."""
        logger1 = get_logger("test_logger_same")
        logger2 = get_logger("test_logger_same")
        assert logger1 is logger2

    def test_get_logger_different_instances(self):
        """Test get_logger returns different instances for different names."""
        logger1 = get_logger("test_logger_1")
        logger2 = get_logger("test_logger_2")
        assert logger1 is not logger2

    @patch("common_utils.logging.logger.logging.getLogger")
    def test_setup_logger_default_level(self, mock_get_logger):
        """Test setup_logger with default level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        setup_logger("test_setup_logger")

        mock_get_logger.assert_called_once_with("test_setup_logger")
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        assert mock_logger.addHandler.called

    @patch("common_utils.logging.logger.logging.getLogger")
    def test_setup_logger_custom_level(self, mock_get_logger):
        """Test setup_logger with custom level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        setup_logger("test_setup_logger_custom", level=logging.DEBUG)

        mock_get_logger.assert_called_once_with("test_setup_logger_custom")
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
        assert mock_logger.addHandler.called

    @patch("common_utils.logging.logger.logging.getLogger")
    def test_setup_logger_with_format(self, mock_get_logger):
        """Test setup_logger with custom format."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        setup_logger("test_setup_logger_format", format_str=custom_format)

        mock_get_logger.assert_called_once_with("test_setup_logger_format")
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        assert mock_logger.addHandler.called

    @patch("common_utils.logging.logger.logging.getLogger")
    def test_setup_logger_with_handlers(self, mock_get_logger):
        """Test setup_logger with custom handlers."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        mock_handler = MagicMock()
        setup_logger("test_setup_logger_handlers", handlers=[mock_handler])

        mock_get_logger.assert_called_once_with("test_setup_logger_handlers")
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_setup_logger_remove_existing_handlers(self):
        """Test setup_logger removes existing handlers."""
        # Create a logger with an existing handler
        logger_name = "test_remove_handlers"
        logger = logging.getLogger(logger_name)

        # Add a handler to the logger
        handler = logging.StreamHandler()
        logger.addHandler(handler)

        # Store the logger in the cache
        _loggers[logger_name] = logger

        # Call setup_logger
        with patch.object(logger, "removeHandler") as mock_remove_handler:
            setup_logger(logger_name)
            mock_remove_handler.assert_called_once_with(handler)

    def test_setup_logger_propagate(self):
        """Test setup_logger sets propagate flag."""
        # Test with propagate=True (default)
        logger_name = "test_propagate_true"
        result = setup_logger(logger_name)
        assert result.propagate is True

        # Test with propagate=False
        logger_name = "test_propagate_false"
        result = setup_logger(logger_name, propagate=False)
        assert result.propagate is False

    def test_setup_logger_formatter(self):
        """Test setup_logger sets formatter on handlers."""
        logger_name = "test_formatter"
        custom_format = "%(levelname)s: %(message)s"

        # Create a mock handler
        mock_handler = MagicMock(spec=logging.Handler)

        # Call setup_logger with the mock handler
        setup_logger(logger_name, format_str=custom_format, handlers=[mock_handler])

        # Verify the formatter was set on the handler
        mock_handler.setFormatter.assert_called_once()
        formatter = mock_handler.setFormatter.call_args[0][0]
        assert isinstance(formatter, logging.Formatter)
        assert formatter._fmt == custom_format

    def test_setup_logger_default_handler(self):
        """Test setup_logger creates default handler when none provided."""
        logger_name = "test_default_handler"

        # Call setup_logger without handlers
        with patch("logging.StreamHandler") as mock_stream_handler:
            mock_handler = MagicMock()
            mock_stream_handler.return_value = mock_handler

            result = setup_logger(logger_name)

            # Verify a StreamHandler was created
            mock_stream_handler.assert_called_once()

            # Verify the handler was added to the logger
            assert mock_handler in result.handlers
