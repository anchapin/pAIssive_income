"""Additional tests for the common_utils.exceptions module to improve coverage."""

import sys

import pytest

from common_utils.exceptions import (
    DirectoryNotFoundError,
    DirectoryPermissionError,
    FileNotPythonError,
    FilePermissionError,
    InvalidRotationIntervalError,
    MissingFileError,
    ScriptNotFoundError,
)


class TestExceptionsAdditional:
    """Additional test suite for custom exceptions to improve coverage."""

    def test_directory_permission_error_with_none(self):
        """Test DirectoryPermissionError with None as message."""
        # This should use the default message
        error = DirectoryPermissionError(None)
        assert str(error) == "None"

    def test_file_permission_error_with_empty_string(self):
        """Test FilePermissionError with empty string as file_path."""
        error = FilePermissionError("")
        # The implementation doesn't append a colon and space when the file_path is empty
        assert str(error) == "Insufficient permissions to read file"

    def test_directory_not_found_error_with_empty_string(self):
        """Test DirectoryNotFoundError with empty string as directory."""
        error = DirectoryNotFoundError("")
        # The implementation doesn't append a colon and space when the directory is empty
        assert str(error) == "Directory not found"

    def test_file_not_python_error_with_empty_string(self):
        """Test FileNotPythonError with empty string as file_path."""
        error = FileNotPythonError("")
        # The implementation doesn't append a colon and space when the file_path is empty
        assert str(error) == "Not a Python file"

    def test_missing_file_error_with_empty_string(self):
        """Test MissingFileError with empty string as file_path."""
        error = MissingFileError("")
        # The implementation doesn't append a colon and space when the file_path is empty
        assert str(error) == "File not found"

    def test_script_not_found_error_with_empty_string(self):
        """Test ScriptNotFoundError with empty string as script_path."""
        error = ScriptNotFoundError("")
        # The implementation doesn't append a colon and space when the script_path is empty
        assert str(error) == "Script not found"

    def test_invalid_rotation_interval_error_with_empty_string(self):
        """Test InvalidRotationIntervalError with empty string as message."""
        error = InvalidRotationIntervalError("")
        assert str(error) == ""

    def test_exception_pickling_basic(self):
        """Test that exceptions can be pickled and unpickled (basic version)."""
        import pickle

        # Test with a simple exception
        original_error = DirectoryPermissionError("Test message")

        # Pickle and unpickle
        pickled = pickle.dumps(original_error)
        unpickled_error = pickle.loads(pickled)

        # Verify the unpickled error has the same message and type
        assert str(unpickled_error) == str(original_error)
        assert type(unpickled_error) == type(original_error)

    def test_exception_with_cause(self):
        """Test exceptions with a cause."""
        try:
            try:
                # Raise a built-in exception
                raise ValueError("Original error")
            except ValueError as e:
                # Raise our custom exception with the built-in as the cause
                raise DirectoryPermissionError("Custom error") from e
        except DirectoryPermissionError as e:
            # Verify the exception chain
            assert str(e) == "Custom error"
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Original error"

    def test_exception_traceback(self):
        """Test that exceptions preserve traceback information."""
        try:
            # Raise our custom exception
            raise FilePermissionError("test_file.txt")
        except FilePermissionError:
            # Verify traceback information is present
            assert sys.exc_info()[2] is not None

    def test_exception_args(self):
        """Test the args attribute of exceptions."""
        # Test with a single argument
        error = DirectoryPermissionError("Test message")
        assert error.args == ("Test message",)

        # Test with default message
        error = MissingFileError()
        assert error.args == ("File not found",)

        # Test with file path
        error = FileNotPythonError("test_file.txt")
        assert error.args == ("Not a Python file: test_file.txt",)

    def test_directory_permission_error_inheritance(self):
        """Test that DirectoryPermissionError inherits from PermissionError."""
        error = DirectoryPermissionError()
        assert isinstance(error, PermissionError)
        assert issubclass(DirectoryPermissionError, PermissionError)

    def test_directory_permission_error_custom_message(self):
        """Test DirectoryPermissionError with a custom message."""
        custom_message = "Cannot access directory /path/to/dir due to permissions"
        error = DirectoryPermissionError(custom_message)
        assert str(error) == custom_message
        assert error.args[0] == custom_message

    def test_file_permission_error_inheritance(self):
        """Test that FilePermissionError inherits from PermissionError."""
        error = FilePermissionError()
        assert isinstance(error, PermissionError)
        assert issubclass(FilePermissionError, PermissionError)

    def test_file_permission_error_default_message(self):
        """Test FilePermissionError with default message."""
        error = FilePermissionError()
        assert str(error) == "Insufficient permissions to read file"
        assert error.args[0] == "Insufficient permissions to read file"

    def test_file_permission_error_with_file_path(self):
        """Test FilePermissionError with a file path."""
        file_path = "/path/to/file.txt"
        error = FilePermissionError(file_path)
        assert str(error) == f"Insufficient permissions to read file: {file_path}"
        assert error.args[0] == f"Insufficient permissions to read file: {file_path}"

    def test_directory_not_found_error_inheritance(self):
        """Test that DirectoryNotFoundError inherits from FileNotFoundError."""
        error = DirectoryNotFoundError()
        assert isinstance(error, FileNotFoundError)
        assert issubclass(DirectoryNotFoundError, FileNotFoundError)

    def test_directory_not_found_error_default_message(self):
        """Test DirectoryNotFoundError with default message."""
        error = DirectoryNotFoundError()
        assert str(error) == "Directory not found"
        assert error.args[0] == "Directory not found"

    def test_directory_not_found_error_with_directory(self):
        """Test DirectoryNotFoundError with a directory path."""
        directory = "/path/to/dir"
        error = DirectoryNotFoundError(directory)
        assert str(error) == f"Directory not found: {directory}"
        assert error.args[0] == f"Directory not found: {directory}"

    def test_file_not_python_error_inheritance(self):
        """Test that FileNotPythonError inherits from ValueError."""
        error = FileNotPythonError()
        assert isinstance(error, ValueError)
        assert issubclass(FileNotPythonError, ValueError)

    def test_file_not_python_error_default_message(self):
        """Test FileNotPythonError with default message."""
        error = FileNotPythonError()
        assert str(error) == "Not a Python file"
        assert error.args[0] == "Not a Python file"

    def test_file_not_python_error_with_file_path(self):
        """Test FileNotPythonError with a file path."""
        file_path = "/path/to/file.txt"
        error = FileNotPythonError(file_path)
        assert str(error) == f"Not a Python file: {file_path}"
        assert error.args[0] == f"Not a Python file: {file_path}"

    def test_missing_file_error_inheritance(self):
        """Test that MissingFileError inherits from FileNotFoundError."""
        error = MissingFileError()
        assert isinstance(error, FileNotFoundError)
        assert issubclass(MissingFileError, FileNotFoundError)

    def test_missing_file_error_default_message(self):
        """Test MissingFileError with default message."""
        error = MissingFileError()
        assert str(error) == "File not found"
        assert error.args[0] == "File not found"

    def test_missing_file_error_with_file_path(self):
        """Test MissingFileError with a file path."""
        file_path = "/path/to/file.txt"
        error = MissingFileError(file_path)
        assert str(error) == f"File not found: {file_path}"
        assert error.args[0] == f"File not found: {file_path}"

    def test_script_not_found_error_inheritance(self):
        """Test that ScriptNotFoundError inherits from FileNotFoundError."""
        error = ScriptNotFoundError()
        assert isinstance(error, FileNotFoundError)
        assert issubclass(ScriptNotFoundError, FileNotFoundError)

    def test_script_not_found_error_default_message(self):
        """Test ScriptNotFoundError with default message."""
        error = ScriptNotFoundError()
        assert str(error) == "Script not found"
        assert error.args[0] == "Script not found"

    def test_script_not_found_error_with_script_path(self):
        """Test ScriptNotFoundError with a script path."""
        script_path = "/path/to/script.py"
        error = ScriptNotFoundError(script_path)
        assert str(error) == f"Script not found: {script_path}"
        assert error.args[0] == f"Script not found: {script_path}"

    def test_invalid_rotation_interval_error_inheritance(self):
        """Test that InvalidRotationIntervalError inherits from ValueError."""
        error = InvalidRotationIntervalError()
        assert isinstance(error, ValueError)
        assert issubclass(InvalidRotationIntervalError, ValueError)

    def test_invalid_rotation_interval_error_default_message(self):
        """Test InvalidRotationIntervalError with default message."""
        error = InvalidRotationIntervalError()
        assert str(error) == "Invalid rotation interval"
        assert error.args[0] == "Invalid rotation interval"

    def test_invalid_rotation_interval_error_custom_message(self):
        """Test InvalidRotationIntervalError with a custom message."""
        custom_message = "Rotation interval must be a positive integer"
        error = InvalidRotationIntervalError(custom_message)
        assert str(error) == custom_message
        assert error.args[0] == custom_message

    def test_exception_pickling_basic(self):
        """Test that basic exceptions can be pickled and unpickled."""
        import pickle

        # Test basic exception pickling
        error = InvalidRotationIntervalError("Test message")
        pickled = pickle.dumps(error)
        unpickled_error = pickle.loads(pickled)

        # Verify the unpickled exception has the same args
        assert unpickled_error.args == error.args
        assert isinstance(unpickled_error, InvalidRotationIntervalError)

    def test_exception_class_inheritance(self):
        """Test that custom exceptions inherit from the correct base classes."""
        assert issubclass(DirectoryPermissionError, PermissionError)
        assert issubclass(FilePermissionError, PermissionError)
        assert issubclass(DirectoryNotFoundError, FileNotFoundError)
        assert issubclass(FileNotPythonError, ValueError)
        assert issubclass(MissingFileError, FileNotFoundError)
        assert issubclass(ScriptNotFoundError, FileNotFoundError)
        assert issubclass(InvalidRotationIntervalError, ValueError)
