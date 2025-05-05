"""Tests for the UI application module."""

import os
import sys
import unittest
from unittest.mock import patch

# Add the parent directory to the Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.ui_service.ui_app import main


class TestUIApp(unittest.TestCase):
    """Test cases for the UI application module."""

    @patch("builtins.print")
    def test_main_function_returns_true(self, mock_print):
        """Test that the main function returns True."""
        result = main()
        self.assertTrue(result)
        mock_print.assert_called_once_with("UI Application initialized")

    def test_main_function_exists(self):
        """Test that the main function exists and can be called without exceptions."""
        try:
            result = main()
            success = True
        except Exception as e:
            success = False
            self.fail(f"main() raised exception: {e}")

        self.assertTrue(success)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
