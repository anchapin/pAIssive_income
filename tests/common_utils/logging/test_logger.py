"""Test module for common_utils.logging.logger."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.logger import (
    get_logger,
    setup_logger,
)


class TestLogger:
    """Test suite for logger module."""

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
