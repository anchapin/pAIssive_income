"""Comprehensive tests for the common_utils.file_utils module."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from common_utils.exceptions import (
    DirectoryNotFoundError,
    DirectoryPermissionError,
    FilePermissionError,
    MissingFileError,
)
from common_utils.file_utils import (
    copy_file,
    create_temp_directory,
    create_temp_file,
    ensure_directory_exists,
    get_file_extension,
    get_file_size,
    list_files,
    list_python_files,
    read_file,
    write_file,
)


class TestFileUtilsComprehensive:
    """Comprehensive test suite for file utility functions."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create a test file
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test file.")

        # Create a Python file
        self.test_py_file = os.path.join(self.temp_dir, "test.py")
        with open(self.test_py_file, "w") as f:
            f.write("print('This is a Python file.')")

        # Create a subdirectory
        self.sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(self.sub_dir, exist_ok=True)

        # Create a file in the subdirectory
        self.sub_file = os.path.join(self.sub_dir, "subfile.txt")
        with open(self.sub_file, "w") as f:
            f.write("This is a file in a subdirectory.")

    def teardown_method(self):
        """Clean up after each test."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.temp_dir)

    def test_ensure_directory_exists_new_dir(self):
        """Test ensure_directory_exists with a new directory."""
        new_dir = os.path.join(self.temp_dir, "new_dir")
        result = ensure_directory_exists(new_dir)
        assert os.path.isdir(new_dir)
        assert isinstance(result, Path)
        assert str(result) == new_dir

    def test_ensure_directory_exists_existing_dir(self):
        """Test ensure_directory_exists with an existing directory."""
        result = ensure_directory_exists(self.temp_dir)
        assert os.path.isdir(self.temp_dir)
        assert isinstance(result, Path)
        assert str(result) == self.temp_dir

    def test_ensure_directory_exists_nested_dir(self):
        """Test ensure_directory_exists with a nested directory structure."""
        nested_dir = os.path.join(self.temp_dir, "nested1", "nested2", "nested3")
        result = ensure_directory_exists(nested_dir)
        assert os.path.isdir(nested_dir)
        assert isinstance(result, Path)
        assert str(result) == nested_dir

    @patch("pathlib.Path.mkdir")
    def test_ensure_directory_exists_permission_error(self, mock_mkdir):
        """Test ensure_directory_exists with permission error."""
        mock_mkdir.side_effect = PermissionError("Permission denied")

        with pytest.raises(DirectoryPermissionError) as excinfo:
            ensure_directory_exists("/root/test_dir")

        assert "Cannot create directory" in str(excinfo.value)

    def test_list_files_basic(self):
        """Test basic functionality of list_files."""
        files = list_files(self.temp_dir)
        # The directory itself might be included in the results
        assert len(files) >= 2  # At least test.txt and test.py
        assert any(str(f).endswith("test.txt") for f in files)
        assert any(str(f).endswith("test.py") for f in files)

    def test_list_files_with_pattern(self):
        """Test list_files with a pattern."""
        files = list_files(self.temp_dir, "*.txt")
        assert len(files) == 1
        assert str(files[0]).endswith("test.txt")

    def test_list_files_recursive(self):
        """Test list_files with recursive option."""
        files = list_files(self.temp_dir, recursive=True)
        # The directory itself might be included in the results
        assert len(files) >= 3  # At least test.txt, test.py, and subdir/subfile.txt
        assert any(str(f).endswith("test.txt") for f in files)
        assert any(str(f).endswith("test.py") for f in files)
        assert any(str(f).endswith("subfile.txt") for f in files)

    def test_list_files_nonexistent_dir(self):
        """Test list_files with a non-existent directory."""
        with pytest.raises(DirectoryNotFoundError):
            list_files(os.path.join(self.temp_dir, "nonexistent"))

    def test_list_python_files_basic(self):
        """Test basic functionality of list_python_files."""
        # Create a Python file in the subdirectory
        sub_py_file = os.path.join(self.sub_dir, "subfile.py")
        with open(sub_py_file, "w") as f:
            f.write("print('This is a Python file in a subdirectory.')")

        # Test with recursive=True (default)
        py_files = list_python_files(self.temp_dir)
        assert len(py_files) == 2  # test.py and subdir/subfile.py
        assert any(str(f).endswith("test.py") for f in py_files)
        assert any(str(f).endswith("subfile.py") for f in py_files)

        # Test with recursive=False
        py_files = list_python_files(self.temp_dir, recursive=False)
        assert len(py_files) == 1  # Only test.py
        assert str(py_files[0]).endswith("test.py")

    def test_list_python_files_empty_dir(self):
        """Test list_python_files with an empty directory."""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)

        py_files = list_python_files(empty_dir)
        assert len(py_files) == 0

    def test_list_python_files_nonexistent_dir(self):
        """Test list_python_files with a non-existent directory."""
        with pytest.raises(DirectoryNotFoundError):
            list_python_files(os.path.join(self.temp_dir, "nonexistent"))

    def test_read_file_basic(self):
        """Test basic functionality of read_file."""
        content = read_file(self.test_file)
        assert content == "This is a test file."

    def test_read_file_nonexistent(self):
        """Test read_file with a non-existent file."""
        with pytest.raises(MissingFileError):
            read_file(os.path.join(self.temp_dir, "nonexistent.txt"))

    @patch("builtins.open", new_callable=mock_open)
    def test_read_file_permission_error(self, mock_file):
        """Test read_file with permission error."""
        mock_file.side_effect = PermissionError("Permission denied")

        with pytest.raises(FilePermissionError) as excinfo:
            read_file(self.test_file)

        assert "Cannot read file" in str(excinfo.value)

    def test_write_file_basic(self):
        """Test basic functionality of write_file."""
        new_file = os.path.join(self.temp_dir, "new_file.txt")
        write_file(new_file, "New content")

        with open(new_file) as f:
            content = f.read()

        assert content == "New content"

    def test_write_file_create_dirs(self):
        """Test write_file with create_dirs option."""
        new_file = os.path.join(self.temp_dir, "new_dir", "new_file.txt")
        write_file(new_file, "New content", create_dirs=True)

        assert os.path.isdir(os.path.join(self.temp_dir, "new_dir"))
        assert os.path.isfile(new_file)

        with open(new_file) as f:
            content = f.read()

        assert content == "New content"

    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_permission_error(self, mock_file):
        """Test write_file with permission error."""
        mock_file.side_effect = PermissionError("Permission denied")

        with pytest.raises(FilePermissionError) as excinfo:
            write_file(self.test_file, "New content")

        assert "Cannot write to file" in str(excinfo.value)

    def test_copy_file_basic(self):
        """Test basic functionality of copy_file."""
        dest_file = os.path.join(self.temp_dir, "dest_file.txt")
        copy_file(self.test_file, dest_file)

        assert os.path.isfile(dest_file)

        with open(dest_file) as f:
            content = f.read()

        assert content == "This is a test file."

    def test_copy_file_create_dirs(self):
        """Test copy_file with create_dirs option."""
        dest_file = os.path.join(self.temp_dir, "new_dir", "dest_file.txt")
        copy_file(self.test_file, dest_file, create_dirs=True)

        assert os.path.isdir(os.path.join(self.temp_dir, "new_dir"))
        assert os.path.isfile(dest_file)

        with open(dest_file) as f:
            content = f.read()

        assert content == "This is a test file."

    def test_copy_file_nonexistent_source(self):
        """Test copy_file with a non-existent source file."""
        with pytest.raises(MissingFileError):
            copy_file(
                os.path.join(self.temp_dir, "nonexistent.txt"),
                os.path.join(self.temp_dir, "dest.txt")
            )

    @patch("shutil.copy2")
    def test_copy_file_permission_error(self, mock_copy2):
        """Test copy_file with permission error."""
        mock_copy2.side_effect = PermissionError("Permission denied")

        with pytest.raises(FilePermissionError) as excinfo:
            copy_file(self.test_file, os.path.join(self.temp_dir, "dest.txt"))

        assert "Cannot copy file" in str(excinfo.value)

    def test_get_file_size(self):
        """Test get_file_size function."""
        size = get_file_size(self.test_file)
        assert size == len("This is a test file.")

    def test_get_file_size_nonexistent(self):
        """Test get_file_size with a non-existent file."""
        with pytest.raises(MissingFileError):
            get_file_size(os.path.join(self.temp_dir, "nonexistent.txt"))

    def test_get_file_extension(self):
        """Test get_file_extension function."""
        # Test with simple extension
        assert get_file_extension(self.test_file) == "txt"
        assert get_file_extension(self.test_py_file) == "py"

        # Test with no extension
        no_ext_file = os.path.join(self.temp_dir, "noextension")
        with open(no_ext_file, "w") as f:
            f.write("No extension")
        assert get_file_extension(no_ext_file) == ""

        # Test with compound extension
        compound_ext_file = os.path.join(self.temp_dir, "file.tar.gz")
        with open(compound_ext_file, "w") as f:
            f.write("Compound extension")
        assert get_file_extension(compound_ext_file) == "gz"

    def test_create_temp_file(self):
        """Test create_temp_file function."""
        # Test with content
        temp_file = create_temp_file("Test content", ".txt")
        assert os.path.isfile(temp_file)

        with open(temp_file) as f:
            content = f.read()
        assert content == "Test content"

        # Clean up
        os.unlink(temp_file)

        # Test without content
        temp_file = create_temp_file(suffix=".log")
        assert os.path.isfile(temp_file)
        assert temp_file.endswith(".log")

        # Clean up
        os.unlink(temp_file)

    def test_create_temp_directory(self):
        """Test create_temp_directory function."""
        temp_dir = create_temp_directory()
        assert os.path.isdir(temp_dir)

        # Clean up
        shutil.rmtree(temp_dir)
