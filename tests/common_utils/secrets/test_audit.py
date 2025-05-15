"""Tests for the audit module."""

import os
import re
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

from common_utils.secrets.audit import (
    is_text_file,
    is_example_code,
    should_exclude,
    find_potential_secrets,
    process_file,
    scan_directory,
    handle_file_error,
    PATTERNS,
    DEFAULT_EXCLUDE_DIRS,
    TEXT_FILE_EXTENSIONS,
)


class TestAudit(unittest.TestCase):
    """Test cases for the audit module."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_is_text_file_with_text_extension(self):
        """Test is_text_file with a file having a text extension."""
        for ext in TEXT_FILE_EXTENSIONS:
            file_path = os.path.join(self.test_dir, f"test{ext}")
            with open(file_path, "w") as f:
                f.write("Test content")
            self.assertTrue(is_text_file(file_path))

    def test_is_text_file_with_binary_content(self):
        """Test is_text_file with binary content."""
        file_path = os.path.join(self.test_dir, "binary_file")
        with open(file_path, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        self.assertFalse(is_text_file(file_path))

    def test_is_text_file_with_nonexistent_file(self):
        """Test is_text_file with a nonexistent file."""
        file_path = os.path.join(self.test_dir, "nonexistent_file")
        self.assertFalse(is_text_file(file_path))

    def test_is_example_code_with_example_indicators(self):
        """Test is_example_code with example indicators."""
        content = "Some content"
        for indicator in ["example", "sample", "demo", "test", "mock", "dummy", "placeholder", "todo", "fixme"]:
            line = f"This is an {indicator} line"
            self.assertTrue(is_example_code(content, line))

    def test_is_example_code_with_docstring(self):
        """Test is_example_code with docstring."""
        content = '"""\nThis is a docstring\n"""'
        line = "    This is indented code in a docstring"
        self.assertTrue(is_example_code(content, line))

    def test_is_example_code_with_regular_code(self):
        """Test is_example_code with regular code."""
        content = "def function():\n    pass"
        line = "def function():"
        self.assertFalse(is_example_code(content, line))

    def test_should_exclude_with_default_exclude_dirs(self):
        """Test should_exclude with default exclude directories."""
        for exclude_dir in DEFAULT_EXCLUDE_DIRS:
            file_path = os.path.join(exclude_dir, "test_file.py")
            self.assertTrue(should_exclude(file_path))

    def test_should_exclude_with_custom_exclude_dirs(self):
        """Test should_exclude with custom exclude directories."""
        custom_exclude_dirs = {"custom_dir", "another_dir"}
        file_path = os.path.join("custom_dir", "test_file.py")
        self.assertTrue(should_exclude(file_path, custom_exclude_dirs))
        file_path = os.path.join("not_excluded", "test_file.py")
        self.assertFalse(should_exclude(file_path, custom_exclude_dirs))

    def test_find_potential_secrets_with_no_secrets(self):
        """Test find_potential_secrets with a file containing no secrets."""
        file_path = os.path.join(self.test_dir, "clean_file.py")
        with open(file_path, "w") as f:
            f.write("def function():\n    pass\n")
        results = find_potential_secrets(file_path)
        self.assertEqual(results, [])

    def test_find_potential_secrets_with_secrets(self):
        """Test find_potential_secrets with a file containing secrets."""
        file_path = os.path.join(self.test_dir, "secret_file.py")
        with open(file_path, "w") as f:
            f.write('api_key = "abcdefghijklmnopqrstuvwxyz123456"\n')
            f.write('password = "supersecretpassword"\n')
        results = find_potential_secrets(file_path)
        self.assertGreater(len(results), 0)
        # Check that we found both secrets
        self.assertEqual(len(results), 2)

    @patch("common_utils.secrets.audit.is_example_code")
    def test_find_potential_secrets_with_example_code(self, mock_is_example_code):
        """Test find_potential_secrets with example code containing secrets."""
        # Mock is_example_code to return True for any input
        mock_is_example_code.return_value = True

        file_path = os.path.join(self.test_dir, "example_file.py")
        with open(file_path, "w") as f:
            f.write('# Example code\napi_key = "abcdefghijklmnopqrstuvwxyz123456"\n')

        results = find_potential_secrets(file_path)
        self.assertEqual(results, [])

    def test_process_file_with_excluded_file(self):
        """Test process_file with an excluded file."""
        file_path = os.path.join("node_modules", "test_file.py")
        results = process_file(file_path)
        self.assertEqual(results, [])

    def test_process_file_with_binary_file(self):
        """Test process_file with a binary file."""
        file_path = os.path.join(self.test_dir, "binary_file")
        with open(file_path, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        results = process_file(file_path)
        self.assertEqual(results, [])

    def test_handle_file_error(self):
        """Test handle_file_error function."""
        file_path = "test_file.py"
        error = ValueError("Test error")
        result = handle_file_error(file_path, error)
        self.assertEqual(result["file"], file_path)
        self.assertEqual(result["error_type"], "ValueError")
        self.assertIn("timestamp", result)
        self.assertIn("error_id", result)

    @patch("common_utils.secrets.audit.process_file")
    @patch("os.walk")
    def test_scan_directory(self, mock_walk, mock_process_file):
        """Test scan_directory function."""
        # Setup mock
        mock_walk.return_value = [
            (self.test_dir, [], ["file1.py", "file2.py"]),
        ]
        mock_process_file.side_effect = [
            [("credential_type_1", 1, 'api_key = "abcdefghijklmnopqrstuvwxyz123456"', "abcdefghijklmnopqrstuvwxyz123456")],
            []
        ]

        # Call function
        results = scan_directory(self.test_dir)

        # Verify results
        self.assertEqual(len(results), 1)
        file_path = os.path.join(self.test_dir, "file1.py")
        self.assertIn(file_path, results)
        self.assertEqual(len(results[file_path]), 1)
        self.assertEqual(results[file_path][0][0], "credential_type_1")

    @patch("common_utils.secrets.audit.process_file")
    @patch("os.walk")
    def test_scan_directory_with_errors(self, mock_walk, mock_process_file):
        """Test scan_directory function with errors."""
        # Setup mock
        mock_walk.return_value = [
            (self.test_dir, [], ["file1.py", "file2.py"]),
        ]
        mock_process_file.side_effect = [
            PermissionError("Permission denied"),
            []
        ]

        # Call function
        with patch("common_utils.secrets.audit.logger") as mock_logger:
            results = scan_directory(self.test_dir)

            # Verify results
            self.assertEqual(len(results), 0)
            mock_logger.warning.assert_called()


if __name__ == "__main__":
    unittest.main()
