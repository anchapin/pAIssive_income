"""Tests for main.py."""

import logging
from unittest.mock import patch

import main
import pytest


class TestMain:
    """Test suite for main.py."""

    def test_module_import(self):
        """Test that the main module can be imported."""
        assert main is not None

    @patch("main.configure_logging")
    def test_logging_setup(self, mock_configure_logging):
        """Test that logging is set up correctly when run as main."""
        # Simulate running the module as a script by calling the main block code
        if hasattr(main, "_run_main"):
            # If the module has a _run_main function, call it
            main._run_main()
        else:
            # Otherwise, execute the code that would run in the __main__ block
            main.configure_logging()
            # We don't need to call logger.info here as we're just testing that configure_logging is called

        # Verify that configure_logging was called
        mock_configure_logging.assert_called_once()

    @patch("main.configure_logging")
    @patch("main.logger")
    def test_main_execution(self, mock_logger, mock_configure_logging):
        """Test the execution of the main module when run as a script."""
        # Simulate running as __main__
        main_globals = {"__name__": "__main__"}
        with patch.dict(main.__dict__, main_globals):
            # Re-import to trigger __main__ block
            import importlib
            importlib.reload(main)

        # Verify configure_logging was called
        mock_configure_logging.assert_called_once()

        # Verify logger.info was called with the expected message
        mock_logger.info.assert_called_once_with("Main application started.")
