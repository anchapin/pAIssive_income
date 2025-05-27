"""Comprehensive tests for the common_utils.exceptions module."""

# Standard library imports
import logging
import unittest
import pytest

# Local imports
from common_utils.exceptions import (
    DirectoryPermissionError,
    FilePermissionError,
    DirectoryNotFoundError,
    FileNotPythonError,
    MissingFileError,
    ScriptNotFoundError,
    InvalidRotationIntervalError,
)


class TestExceptions(unittest.TestCase):
    """Test suite for custom exceptions."""

    def test_directory_permission_error_default_message(self):
        """Test DirectoryPermissionError with default message."""
        # Act
        error = DirectoryPermissionError()

        # Assert
        self.assertEqual(str(error), "Insufficient permissions to read directory")
        self.assertIsInstance(error, PermissionError)

    def test_directory_permission_error_custom_message(self):
        """Test DirectoryPermissionError with custom message."""
        # Act
        custom_message = "Cannot access directory due to permissions"
        error = DirectoryPermissionError(custom_message)

        # Assert
        self.assertEqual(str(error), custom_message)
        self.assertIsInstance(error, PermissionError)

    def test_file_permission_error_default_message(self):
        """Test FilePermissionError with default message."""
        # Act
        error = FilePermissionError()

        # Assert
        self.assertEqual(str(error), "Insufficient permissions to read file")
        self.assertIsInstance(error, PermissionError)

    def test_file_permission_error_with_path(self):
        """Test FilePermissionError with file path."""
        # Act
        file_path = "/path/to/file.txt"
        error = FilePermissionError(file_path)

        # Assert
        self.assertEqual(str(error), f"Insufficient permissions to read file: {file_path}")
        self.assertIsInstance(error, PermissionError)

    def test_directory_not_found_error_default_message(self):
        """Test DirectoryNotFoundError with default message."""
        # Act
        error = DirectoryNotFoundError()

        # Assert
        self.assertEqual(str(error), "Directory not found")
        self.assertIsInstance(error, FileNotFoundError)

    def test_directory_not_found_error_with_path(self):
        """Test DirectoryNotFoundError with directory path."""
        # Act
        directory = "/path/to/directory"
        error = DirectoryNotFoundError(directory)

        # Assert
        self.assertEqual(str(error), f"Directory not found: {directory}")
        self.assertIsInstance(error, FileNotFoundError)

    def test_file_not_python_error_default_message(self):
        """Test FileNotPythonError with default message."""
        # Act
        error = FileNotPythonError()

        # Assert
        self.assertEqual(str(error), "Not a Python file")
        self.assertIsInstance(error, ValueError)

    def test_file_not_python_error_with_path(self):
        """Test FileNotPythonError with file path."""
        # Act
        file_path = "/path/to/file.txt"
        error = FileNotPythonError(file_path)

        # Assert
        self.assertEqual(str(error), f"Not a Python file: {file_path}")
        self.assertIsInstance(error, ValueError)

    def test_missing_file_error_default_message(self):
        """Test MissingFileError with default message."""
        # Act
        error = MissingFileError()

        # Assert
        self.assertEqual(str(error), "File not found")
        self.assertIsInstance(error, FileNotFoundError)

    def test_missing_file_error_with_path(self):
        """Test MissingFileError with file path."""
        # Act
        file_path = "/path/to/file.txt"
        error = MissingFileError(file_path)

        # Assert
        self.assertEqual(str(error), f"File not found: {file_path}")
        self.assertIsInstance(error, FileNotFoundError)

    def test_script_not_found_error(self):
        """Test ScriptNotFoundError."""
        # Act
        error = ScriptNotFoundError()

        # Assert
        self.assertEqual(str(error), "Script not found")
        self.assertIsInstance(error, FileNotFoundError)

    def test_invalid_rotation_interval_error(self):
        """Test InvalidRotationIntervalError."""
        # Act
        error = InvalidRotationIntervalError()

        # Assert
        self.assertEqual(str(error), "Invalid rotation interval")
        self.assertIsInstance(error, ValueError)


class TestExceptionsPytest:
    """Test suite for custom exceptions using pytest."""

    def test_directory_permission_error_inheritance(self):
        """Test DirectoryPermissionError inheritance chain."""
        error = DirectoryPermissionError()
        assert isinstance(error, PermissionError)
        assert isinstance(error, OSError)
        assert isinstance(error, Exception)

    def test_file_permission_error_inheritance(self):
        """Test FilePermissionError inheritance chain."""
        error = FilePermissionError()
        assert isinstance(error, PermissionError)
        assert isinstance(error, OSError)
        assert isinstance(error, Exception)

    def test_directory_not_found_error_inheritance(self):
        """Test DirectoryNotFoundError inheritance chain."""
        error = DirectoryNotFoundError()
        assert isinstance(error, FileNotFoundError)
        assert isinstance(error, OSError)
        assert isinstance(error, Exception)

    def test_file_not_python_error_inheritance(self):
        """Test FileNotPythonError inheritance chain."""
        error = FileNotPythonError()
        assert isinstance(error, ValueError)
        assert isinstance(error, Exception)

    def test_missing_file_error_inheritance(self):
        """Test MissingFileError inheritance chain."""
        error = MissingFileError()
        assert isinstance(error, FileNotFoundError)
        assert isinstance(error, OSError)
        assert isinstance(error, Exception)

    def test_script_not_found_error_inheritance(self):
        """Test ScriptNotFoundError inheritance chain."""
        error = ScriptNotFoundError()
        assert isinstance(error, FileNotFoundError)
        assert isinstance(error, OSError)
        assert isinstance(error, Exception)

    def test_invalid_rotation_interval_error_inheritance(self):
        """Test InvalidRotationIntervalError inheritance chain."""
        error = InvalidRotationIntervalError()
        assert isinstance(error, ValueError)
        assert isinstance(error, Exception)

    def test_script_not_found_error_with_path(self):
        """Test ScriptNotFoundError with a path."""
        script_path = "/path/to/script.py"
        error = ScriptNotFoundError(script_path)
        assert str(error) == f"Script not found: {script_path}"
        assert isinstance(error, FileNotFoundError)

    def test_invalid_rotation_interval_error_with_message(self):
        """Test InvalidRotationIntervalError with a custom message."""
        custom_message = "Rotation interval must be a positive integer"
        error = InvalidRotationIntervalError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, ValueError)
