"""Tests for the common_utils/exceptions.py module."""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common_utils.exceptions import (
    DirectoryNotFoundError,
    DirectoryPermissionError,
    FileNotPythonError,
    FilePermissionError,
    InvalidRotationIntervalError,
    MissingFileError,
    ScriptNotFoundError,
)


class TestExceptions(unittest.TestCase):
    """Test cases for the common_utils/exceptions.py module."""

    def test_directory_permission_error_default(self):
        """Test DirectoryPermissionError with default message."""
        error = DirectoryPermissionError()
        self.assertEqual(str(error), "Insufficient permissions to read directory")

    def test_directory_permission_error_custom(self):
        """Test DirectoryPermissionError with custom message."""
        custom_message = "Cannot access directory due to permissions"
        error = DirectoryPermissionError(custom_message)
        self.assertEqual(str(error), custom_message)

    def test_file_permission_error_default(self):
        """Test FilePermissionError with default message."""
        error = FilePermissionError()
        self.assertEqual(str(error), "Insufficient permissions to read file")

    def test_file_permission_error_with_path(self):
        """Test FilePermissionError with file path."""
        file_path = "/path/to/file.py"
        error = FilePermissionError(file_path)
        self.assertEqual(str(error), f"Insufficient permissions to read file: {file_path}")

    def test_directory_not_found_error_default(self):
        """Test DirectoryNotFoundError with default message."""
        error = DirectoryNotFoundError()
        self.assertEqual(str(error), "Directory not found")

    def test_directory_not_found_error_with_path(self):
        """Test DirectoryNotFoundError with directory path."""
        directory = "/path/to/directory"
        error = DirectoryNotFoundError(directory)
        self.assertEqual(str(error), f"Directory not found: {directory}")

    def test_file_not_python_error_default(self):
        """Test FileNotPythonError with default message."""
        error = FileNotPythonError()
        self.assertEqual(str(error), "Not a Python file")

    def test_file_not_python_error_with_path(self):
        """Test FileNotPythonError with file path."""
        file_path = "/path/to/file.txt"
        error = FileNotPythonError(file_path)
        self.assertEqual(str(error), f"Not a Python file: {file_path}")

    def test_missing_file_error_default(self):
        """Test MissingFileError with default message."""
        error = MissingFileError()
        self.assertEqual(str(error), "File not found")

    def test_missing_file_error_with_path(self):
        """Test MissingFileError with file path."""
        file_path = "/path/to/missing_file.py"
        error = MissingFileError(file_path)
        self.assertEqual(str(error), f"File not found: {file_path}")

    def test_script_not_found_error(self):
        """Test ScriptNotFoundError."""
        error = ScriptNotFoundError()
        self.assertEqual(str(error), "Script not found")

    def test_invalid_rotation_interval_error(self):
        """Test InvalidRotationIntervalError."""
        error = InvalidRotationIntervalError()
        self.assertEqual(str(error), "Invalid rotation interval")


if __name__ == "__main__":
    unittest.main()
