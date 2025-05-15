"""Tests for main.py."""

import logging
from unittest.mock import patch

import pytest

import main


class TestMain:
    """Test suite for main.py."""

    def test_module_import(self):
        """Test that the main module can be imported."""
        assert main is not None

    @patch("main.logging.basicConfig")
    def test_logging_setup(self, mock_logging_basicConfig):
        """Test that logging is set up correctly."""
        # Re-import the module to trigger the logging setup
        import importlib
        importlib.reload(main)
        
        # Verify that logging.basicConfig was called with the correct arguments
        mock_logging_basicConfig.assert_called_once_with(
            level=logging.INFO, format="%(levelname)s: %(message)s"
        )
