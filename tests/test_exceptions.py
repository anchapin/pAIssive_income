"""Tests for the common_utils/exceptions.py module."""

import os
import sys

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


class TestExceptions:
    """Test cases for the common_utils/exceptions.py module."""

    def test_directory_permission_error_default(self):
        """Test DirectoryPermissionError with default message."""
        error = DirectoryPermissionError()
        assert str(error) == "Insufficient permissions to read directory"

    def test_directory_permission_error_custom(self):
        """Test DirectoryPermissionError with custom message."""
        custom_message = "Cannot access directory due to permissions"
        error = DirectoryPermissionError(custom_message)
        assert str(error) == custom_message

    def test_file_permission_error_default(self):
        """Test FilePermissionError with default message."""
        error = FilePermissionError()
        assert str(error) == "Insufficient permissions to read file"

    def test_file_permission_error_with_path(self):
        """Test FilePermissionError with file path."""
        file_path = "/path/to/file.py"
        error = FilePermissionError(file_path)
        assert str(error) == f"Insufficient permissions to read file: {file_path}"

    def test_directory_not_found_error_default(self):
        """Test DirectoryNotFoundError with default message."""
        error = DirectoryNotFoundError()
        assert str(error) == "Directory not found"

    def test_directory_not_found_error_with_path(self):
        """Test DirectoryNotFoundError with directory path."""
        directory = "/path/to/directory"
        error = DirectoryNotFoundError(directory)
        assert str(error) == f"Directory not found: {directory}"

    def test_file_not_python_error_default(self):
        """Test FileNotPythonError with default message."""
        error = FileNotPythonError()
        assert str(error) == "Not a Python file"

    def test_file_not_python_error_with_path(self):
        """Test FileNotPythonError with file path."""
        file_path = "/path/to/file.txt"
        error = FileNotPythonError(file_path)
        assert str(error) == f"Not a Python file: {file_path}"

    def test_missing_file_error_default(self):
        """Test MissingFileError with default message."""
        error = MissingFileError()
        assert str(error) == "File not found"

    def test_missing_file_error_with_path(self):
        """Test MissingFileError with file path."""
        file_path = "/path/to/missing_file.py"
        error = MissingFileError(file_path)
        assert str(error) == f"File not found: {file_path}"

    def test_script_not_found_error(self):
        """Test ScriptNotFoundError."""
        error = ScriptNotFoundError()
        assert str(error) == "Script not found"

    def test_invalid_rotation_interval_error(self):
        """Test InvalidRotationIntervalError."""
        error = InvalidRotationIntervalError()
        assert str(error) == "Invalid rotation interval"
