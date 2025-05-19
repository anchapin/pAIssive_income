"""File utility functions for the pAIssive_income project.

This module provides common file handling functions used across the project.
"""

# Standard library imports
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Union, BinaryIO, TextIO, Iterator, Any, Dict

# Third-party imports

# Local imports
from common_utils.exceptions import (
    DirectoryPermissionError,
    FilePermissionError,
    DirectoryNotFoundError,
    FileNotPythonError,
    MissingFileError,
)


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: The path to the directory

    Returns:
        The Path object for the directory

    Raises:
        DirectoryPermissionError: If the directory cannot be created due to permissions

    Examples:
        >>> import tempfile
        >>> temp_dir = tempfile.gettempdir()
        >>> test_dir = os.path.join(temp_dir, "test_dir")
        >>> path = ensure_directory_exists(test_dir)
        >>> os.path.isdir(test_dir)
        True
        >>> os.rmdir(test_dir)  # Clean up
    """
    path = Path(directory_path)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise DirectoryPermissionError(f"Cannot create directory {directory_path}: {e}") from e
    return path


def list_files(
    directory_path: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False,
) -> List[Path]:
    """
    List files in a directory, optionally matching a pattern.

    Args:
        directory_path: The path to the directory
        pattern: A glob pattern to match files (default: "*")
        recursive: Whether to search recursively (default: False)

    Returns:
        A list of Path objects for the matching files

    Raises:
        DirectoryNotFoundError: If the directory does not exist

    Examples:
        >>> import tempfile
        >>> temp_dir = tempfile.gettempdir()
        >>> test_dir = os.path.join(temp_dir, "test_dir")
        >>> os.makedirs(test_dir, exist_ok=True)
        >>> with open(os.path.join(test_dir, "test.txt"), "w") as f:
        ...     f.write("test")
        4
        >>> with open(os.path.join(test_dir, "test.py"), "w") as f:
        ...     f.write("print('test')")
        13
        >>> files = list_files(test_dir, "*.txt")
        >>> len(files)
        1
        >>> str(files[0]).endswith("test.txt")
        True
        >>> shutil.rmtree(test_dir)  # Clean up
    """
    path = Path(directory_path)
    if not path.exists():
        raise DirectoryNotFoundError(f"Directory {directory_path} does not exist")

    if recursive:
        return list(path.glob(f"**/{pattern}"))
    return list(path.glob(pattern))


def list_python_files(directory_path: Union[str, Path], recursive: bool = True) -> List[Path]:
    """
    List Python files in a directory.

    Args:
        directory_path: The path to the directory
        recursive: Whether to search recursively (default: True)

    Returns:
        A list of Path objects for the Python files

    Examples:
        >>> import tempfile
        >>> temp_dir = tempfile.gettempdir()
        >>> test_dir = os.path.join(temp_dir, "test_dir")
        >>> os.makedirs(test_dir, exist_ok=True)
        >>> with open(os.path.join(test_dir, "test.txt"), "w") as f:
        ...     f.write("test")
        4
        >>> with open(os.path.join(test_dir, "test.py"), "w") as f:
        ...     f.write("print('test')")
        13
        >>> files = list_python_files(test_dir)
        >>> len(files)
        1
        >>> str(files[0]).endswith("test.py")
        True
        >>> shutil.rmtree(test_dir)  # Clean up
    """
    return list_files(directory_path, "*.py", recursive)


def read_file(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """
    Read the contents of a text file.

    Args:
        file_path: The path to the file
        encoding: The encoding to use (default: "utf-8")

    Returns:
        The contents of the file as a string

    Raises:
        MissingFileError: If the file does not exist
        FilePermissionError: If the file cannot be read due to permissions

    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        ...     f.write("test content")
        ...     temp_file = f.name
        12
        >>> content = read_file(temp_file)
        >>> content
        'test content'
        >>> os.unlink(temp_file)  # Clean up
    """
    path = Path(file_path)
    if not path.exists():
        raise MissingFileError(f"File {file_path} does not exist")

    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except PermissionError as e:
        raise FilePermissionError(f"Cannot read file {file_path}: {e}") from e


def write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> None:
    """
    Write content to a text file.

    Args:
        file_path: The path to the file
        content: The content to write
        encoding: The encoding to use (default: "utf-8")
        create_dirs: Whether to create parent directories if they don't exist (default: True)

    Raises:
        FilePermissionError: If the file cannot be written due to permissions

    Examples:
        >>> import tempfile
        >>> temp_dir = tempfile.gettempdir()
        >>> test_file = os.path.join(temp_dir, "test_write.txt")
        >>> write_file(test_file, "test content")
        >>> with open(test_file, "r") as f:
        ...     content = f.read()
        >>> content
        'test content'
        >>> os.unlink(test_file)  # Clean up
    """
    path = Path(file_path)

    if create_dirs:
        ensure_directory_exists(path.parent)

    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
    except PermissionError as e:
        raise FilePermissionError(f"Cannot write to file {file_path}: {e}") from e


def copy_file(
    source_path: Union[str, Path],
    destination_path: Union[str, Path],
    create_dirs: bool = True,
) -> None:
    """
    Copy a file from source to destination.

    Args:
        source_path: The path to the source file
        destination_path: The path to the destination file
        create_dirs: Whether to create parent directories if they don't exist (default: True)

    Raises:
        MissingFileError: If the source file does not exist
        FilePermissionError: If the file cannot be copied due to permissions

    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        ...     f.write("test content")
        ...     source_file = f.name
        12
        >>> temp_dir = tempfile.gettempdir()
        >>> dest_file = os.path.join(temp_dir, "test_copy.txt")
        >>> copy_file(source_file, dest_file)
        >>> with open(dest_file, "r") as f:
        ...     content = f.read()
        >>> content
        'test content'
        >>> os.unlink(source_file)  # Clean up
        >>> os.unlink(dest_file)  # Clean up
    """
    source = Path(source_path)
    destination = Path(destination_path)

    if not source.exists():
        raise MissingFileError(f"Source file {source_path} does not exist")

    if create_dirs:
        ensure_directory_exists(destination.parent)

    try:
        shutil.copy2(source, destination)
    except PermissionError as e:
        raise FilePermissionError(f"Cannot copy file {source_path} to {destination_path}: {e}") from e


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: The path to the file

    Returns:
        The size of the file in bytes

    Raises:
        MissingFileError: If the file does not exist

    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        ...     f.write("test content")
        ...     temp_file = f.name
        12
        >>> size = get_file_size(temp_file)
        >>> size
        12
        >>> os.unlink(temp_file)  # Clean up
    """
    path = Path(file_path)
    if not path.exists():
        raise MissingFileError(f"File {file_path} does not exist")

    return path.stat().st_size


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the extension of a file.

    Args:
        file_path: The path to the file

    Returns:
        The extension of the file (without the dot)

    Examples:
        >>> get_file_extension("test.txt")
        'txt'
        >>> get_file_extension("test.tar.gz")
        'gz'
        >>> get_file_extension("test")
        ''
    """
    path = Path(file_path)
    return path.suffix.lstrip(".")


def create_temp_file(content: str = "", suffix: str = ".txt") -> str:
    """
    Create a temporary file with optional content.

    Args:
        content: The content to write to the file (default: "")
        suffix: The suffix for the temporary file (default: ".txt")

    Returns:
        The path to the temporary file

    Examples:
        >>> temp_file = create_temp_file("test content", ".txt")
        >>> with open(temp_file, "r") as f:
        ...     content = f.read()
        >>> content
        'test content'
        >>> os.unlink(temp_file)  # Clean up
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    if content:
        with open(path, "w") as f:
            f.write(content)

    return path


def create_temp_directory() -> str:
    """
    Create a temporary directory.

    Returns:
        The path to the temporary directory

    Examples:
        >>> temp_dir = create_temp_directory()
        >>> os.path.isdir(temp_dir)
        True
        >>> os.rmdir(temp_dir)  # Clean up
    """
    return tempfile.mkdtemp()
