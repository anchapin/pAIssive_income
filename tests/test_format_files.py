"""Test class contains unit tests for format_files.py."""

import os
import subprocess
import sys
import unittest
from unittest.mock import patch

import format_files


class TestFormatFiles(unittest.TestCase):
    """Test cases for format_files module."""

    @patch("builtins.print")
    def test_main_no_files(self, mock_print):
        """Test main function when called with no files."""
        with patch("sys.argv", ["format_files.py"]):
            result = format_files.main()
            self.assertEqual(result, 0)
            mock_print.assert_any_call("No files provided for formatting.")

    @patch("format_files.format_file", return_value=True)
    @patch("builtins.print")
    def test_main_with_files_success(self, mock_print, mock_format_file):
        """Test main function when called with files and formatting succeeds."""
        with patch("sys.argv", ["format_files.py", "file1.py", "file2.py"]):
            result = format_files.main()
            self.assertEqual(result, 0)
            self.assertEqual(mock_format_file.call_count, 2)
            mock_format_file.assert_any_call("file1.py")
            mock_format_file.assert_any_call("file2.py")

    @patch("format_files.format_file", return_value=False)
    @patch("builtins.print")
    def test_main_with_files_failure(self, mock_print, mock_format_file):
        """Test main function when called with files and formatting fails for one."""
        with patch("sys.argv", ["format_files.py", "file1.py", "file2.py"]):
            result = format_files.main()
            self.assertEqual(result, 1)
            self.assertEqual(mock_format_file.call_count, 2)
            mock_format_file.assert_any_call("file1.py")
            mock_format_file.assert_any_call("file2.py")

    def test_main_block_execution_success(self):
        """Test the __main__ block when main returns 0."""
        script_path = os.path.join(os.path.dirname(__file__), "../format_files.py")
        assert os.path.exists(script_path), f"Script not found: {script_path}"

        # Set environment variable to force success mode
        env = os.environ.copy()
        env["FORMAT_FILES_TEST_MODE"] = "success"

        result = subprocess.run([sys.executable, script_path], env=env, check=True)
        self.assertEqual(result.returncode, 0)

    def test_main_block_execution_failure(self):
        """Test the __main__ block when main returns 1."""
        script_path = os.path.join(os.path.dirname(__file__), "../format_files.py")
        assert os.path.exists(script_path), f"Script not found: {script_path}"

        # Set environment variable to force failure mode
        env = os.environ.copy()
        env["FORMAT_FILES_TEST_MODE"] = "failure"

        # check=True is removed because we expect a non-zero exit code
        result = subprocess.run([sys.executable, script_path], env=env)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
