"""Tests for add_logging_import.py module."""

import os
import sys
import tempfile
from unittest.mock import mock_open, patch

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
from add_logging_import import add_logging_import, process_directory


class TestAddLoggingImport:
    """Test suite for add_logging_import functions."""

    def test_add_logging_import_already_imported(self):
        """Test that add_logging_import returns False when logging is already imported."""
        content = "import logging\n\ndef test_function():\n    pass\n"

        with patch("builtins.open", mock_open(read_data=content)):
            with patch("builtins.print") as mock_print:
                result = add_logging_import("dummy_file.py")

                assert result is False
                mock_print.assert_called_once()
                assert "already imported" in mock_print.call_args[0][0]

    def test_add_logging_import_from_logging_already_imported(self):
        """Test that add_logging_import returns False when from logging import is already used."""
        content = "from logging import getLogger\n\ndef test_function():\n    pass\n"

        with patch("builtins.open", mock_open(read_data=content)):
            with patch("builtins.print") as mock_print:
                result = add_logging_import("dummy_file.py")

                assert result is False
                mock_print.assert_called_once()
                assert "already imported" in mock_print.call_args[0][0]

    def test_add_logging_import_before_first_import(self):
        """Test that add_logging_import adds logging import before the first import."""
        content = "import os\nimport sys\n\ndef test_function():\n    pass\n"
        expected = "import logging\nimport os\nimport sys\n\ndef test_function():\n    pass\n"

        mock_file = mock_open(read_data=content)
        with patch("builtins.open", mock_file):
            with patch("builtins.print") as mock_print:
                result = add_logging_import("dummy_file.py")

                assert result is True
                mock_print.assert_called_once()
                assert "Added logging import" in mock_print.call_args[0][0]

                # Check that the file was written with the expected content
                handle = mock_file()
                handle.write.assert_called_once_with(expected)

    def test_add_logging_import_after_docstring(self):
        """Test that add_logging_import adds logging import after the docstring."""
        content = '"""This is a docstring."""\n\ndef test_function():\n    pass\n'

        mock_file = mock_open(read_data=content)
        with patch("builtins.open", mock_file):
            with patch("builtins.print") as mock_print:
                result = add_logging_import("dummy_file.py")

                assert result is True
                mock_print.assert_called_once()
                assert "Added logging import" in mock_print.call_args[0][0]

                # Check that the file was written with some content
                handle = mock_file()
                handle.write.assert_called_once()
                # Check that the written content contains the import logging statement
                assert "import logging" in handle.write.call_args[0][0]
                # Check that the docstring and function are preserved
                assert '"""This is a docstring."""' in handle.write.call_args[0][0]
                assert "def test_function():" in handle.write.call_args[0][0]

    def test_add_logging_import_at_beginning(self):
        """Test that add_logging_import adds logging import at the beginning if no imports or docstring."""
        content = "def test_function():\n    pass\n"
        expected = "import logging\ndef test_function():\n    pass\n"

        mock_file = mock_open(read_data=content)
        with patch("builtins.open", mock_file):
            with patch("builtins.print") as mock_print:
                result = add_logging_import("dummy_file.py")

                assert result is True
                mock_print.assert_called_once()
                assert "Added logging import" in mock_print.call_args[0][0]

                # Check that the file was written with the expected content
                handle = mock_file()
                handle.write.assert_called_once_with(expected)

    @patch("os.walk")
    @patch("add_logging_import.add_logging_import")
    def test_process_directory(self, mock_add_logging_import, mock_walk):
        """Test that process_directory processes all test files in a directory."""
        # Setup mock os.walk to return some test files
        mock_walk.return_value = [
            ("/path/to/tests", [], ["test_file1.py", "test_file2.py", "not_a_test.py"]),
            ("/path/to/tests/subdir", [], ["test_file3.py", "another_file.py"])
        ]

        # Setup mock add_logging_import to return True for some files
        mock_add_logging_import.side_effect = [True, False, True]

        # Call the function
        count = process_directory("/path/to/tests")

        # Check that add_logging_import was called for each test file
        assert mock_add_logging_import.call_count == 3

        # Get the actual calls made to mock_add_logging_import
        actual_calls = [call[0][0] for call in mock_add_logging_import.call_args_list]

        # Check that the expected files were processed
        # Use os.path.normpath to handle path separators consistently
        expected_files = [
            os.path.normpath("/path/to/tests/test_file1.py"),
            os.path.normpath("/path/to/tests/test_file2.py"),
            os.path.normpath("/path/to/tests/subdir/test_file3.py")
        ]

        # Check that each expected file is in the actual calls
        for expected_file in expected_files:
            assert any(os.path.normpath(actual) == expected_file for actual in actual_calls)

        # Check that the count is correct
        assert count == 2
