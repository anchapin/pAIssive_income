"""Custom exception classes for the project.

This module contains custom exception classes that provide more descriptive
error messages and better error handling throughout the project.
"""

from typing import Optional


class DirectoryPermissionError(PermissionError):
    """Exception raised when there are insufficient permissions to read a directory."""

    def __init__(self, message: str = "Insufficient permissions to read directory"):
        """Initialize the exception.

        Args:
            message: The error message
        """
        super().__init__(message)


class FilePermissionError(PermissionError):
    """Exception raised when there are insufficient permissions to read a file."""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize the exception.

        Args:
            file_path: The path to the file
        """
        message = "Insufficient permissions to read file"
        if file_path:
            message = f"{message}: {file_path}"
        super().__init__(message)


class DirectoryNotFoundError(FileNotFoundError):
    """Exception raised when a directory is not found."""

    def __init__(self, directory: Optional[str] = None):
        """Initialize the exception.

        Args:
            directory: The directory path
        """
        message = "Directory not found"
        if directory:
            message = f"{message}: {directory}"
        super().__init__(message)


class FileNotPythonError(ValueError):
    """Exception raised when a file is not a Python file."""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize the exception.

        Args:
            file_path: The path to the file
        """
        message = "Not a Python file"
        if file_path:
            message = f"{message}: {file_path}"
        super().__init__(message)


class MissingFileError(FileNotFoundError):
    """Exception raised when a file is not found."""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize the exception.

        Args:
            file_path: The path to the file
        """
        message = "File not found"
        if file_path:
            message = f"{message}: {file_path}"
        super().__init__(message)


class ScriptNotFoundError(FileNotFoundError):
    """Exception raised when a script is not found."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Script not found")


class InvalidRotationIntervalError(ValueError):
    """Exception raised when an invalid rotation interval is provided."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Invalid rotation interval")
