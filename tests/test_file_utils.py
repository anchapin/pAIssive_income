"""Tests for the common_utils.file_utils module."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from common_utils.file_utils import (
    ensure_directory_exists,
    list_files,
    list_python_files,
    read_file,
    write_file,
    copy_file,
    get_file_size,
    get_file_extension,
    create_temp_file,
    create_temp_directory,
)
from common_utils.exceptions import (
    DirectoryPermissionError,
    FilePermissionError,
    DirectoryNotFoundError,
    MissingFileError,
)


class TestFileUtils:
    """Test suite for file utility functions."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create some test files
        self.test_txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_txt_file, "w") as f:
            f.write("This is a test file.")

        self.test_py_file = os.path.join(self.temp_dir, "test.py")
        with open(self.test_py_file, "w") as f:
            f.write("print('This is a Python test file.')")

        # Create a subdirectory
        self.sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(self.sub_dir)

        # Create a file in the subdirectory
        self.sub_file = os.path.join(self.sub_dir, "subfile.txt")
        with open(self.sub_file, "w") as f:
            f.write("This is a file in a subdirectory.")

        self.sub_py_file = os.path.join(self.sub_dir, "subfile.py")
        with open(self.sub_py_file, "w") as f:
            f.write("print('This is a Python file in a subdirectory.')")

    def teardown_method(self):
        """Clean up after each test."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.temp_dir)

    def test_ensure_directory_exists(self):
        """Test the ensure_directory_exists function."""
        # Test creating a new directory
        new_dir = os.path.join(self.temp_dir, "new_dir")
        path = ensure_directory_exists(new_dir)
        assert os.path.isdir(new_dir)
        assert isinstance(path, Path)

        # Test with an existing directory
        path = ensure_directory_exists(self.temp_dir)
        assert os.path.isdir(self.temp_dir)

        # Test creating nested directories
        nested_dir = os.path.join(self.temp_dir, "nested", "dir")
        path = ensure_directory_exists(nested_dir)
        assert os.path.isdir(nested_dir)

    def test_list_files(self):
        """Test the list_files function."""
        # Test listing all files
        files = list_files(self.temp_dir)
        # The directory itself is included in the results
        assert len(files) == 3  # test.txt, test.py, and subdir

        # Test with pattern
        txt_files = list_files(self.temp_dir, "*.txt")
        assert len(txt_files) == 1
        assert str(txt_files[0]).endswith("test.txt")

        py_files = list_files(self.temp_dir, "*.py")
        assert len(py_files) == 1
        assert str(py_files[0]).endswith("test.py")

        # Test with non-existent directory
        with pytest.raises(DirectoryNotFoundError):
            list_files(os.path.join(self.temp_dir, "non_existent"))

        # Test recursive listing
        all_files = list_files(self.temp_dir, "*", recursive=True)
        assert len(all_files) == 5  # test.txt, test.py, subdir, subdir/subfile.txt, subdir/subfile.py

    def test_list_python_files(self):
        """Test the list_python_files function."""
        # Create a Python file in the subdirectory
        sub_py_file = os.path.join(self.sub_dir, "subfile.py")
        with open(sub_py_file, "w") as f:
            f.write("print('This is a Python file in a subdirectory.')")

        # Test listing Python files
        py_files = list_python_files(self.temp_dir)
        assert len(py_files) == 2  # test.py and subdir/subfile.py

        # Test with non-recursive
        py_files = list_python_files(self.temp_dir, recursive=False)
        assert len(py_files) == 1  # Only test.py
        assert str(py_files[0]).endswith("test.py")

    def test_read_file(self):
        """Test the read_file function."""
        # Test reading an existing file
        content = read_file(self.test_txt_file)
        assert content == "This is a test file."

        # Test with non-existent file
        with pytest.raises(MissingFileError):
            read_file(os.path.join(self.temp_dir, "non_existent.txt"))

    def test_write_file(self):
        """Test the write_file function."""
        # Test writing to a new file
        new_file = os.path.join(self.temp_dir, "new_file.txt")
        write_file(new_file, "This is a new file.")
        assert os.path.exists(new_file)
        with open(new_file, "r") as f:
            assert f.read() == "This is a new file."

        # Test overwriting an existing file
        write_file(new_file, "This is updated content.")
        with open(new_file, "r") as f:
            assert f.read() == "This is updated content."

        # Test creating directories if they don't exist
        nested_file = os.path.join(self.temp_dir, "nested", "dir", "file.txt")
        write_file(nested_file, "This is a nested file.")
        assert os.path.exists(nested_file)
        with open(nested_file, "r") as f:
            assert f.read() == "This is a nested file."

    def test_copy_file(self):
        """Test the copy_file function."""
        # Test copying a file
        dest_file = os.path.join(self.temp_dir, "copy.txt")
        copy_file(self.test_txt_file, dest_file)
        assert os.path.exists(dest_file)
        with open(dest_file, "r") as f:
            assert f.read() == "This is a test file."

        # Test with non-existent source file
        with pytest.raises(MissingFileError):
            copy_file(os.path.join(self.temp_dir, "non_existent.txt"), dest_file)

        # Test copying to a nested directory
        nested_dest = os.path.join(self.temp_dir, "nested", "dir", "copy.txt")
        copy_file(self.test_txt_file, nested_dest)
        assert os.path.exists(nested_dest)
        with open(nested_dest, "r") as f:
            assert f.read() == "This is a test file."

    def test_get_file_size(self):
        """Test the get_file_size function."""
        # Test getting the size of an existing file
        size = get_file_size(self.test_txt_file)
        assert size == len("This is a test file.")

        # Test with non-existent file
        with pytest.raises(MissingFileError):
            get_file_size(os.path.join(self.temp_dir, "non_existent.txt"))

    def test_get_file_extension(self):
        """Test the get_file_extension function."""
        # Test with .txt file
        assert get_file_extension(self.test_txt_file) == "txt"

        # Test with .py file
        assert get_file_extension(self.test_py_file) == "py"

        # Test with no extension
        no_ext_file = os.path.join(self.temp_dir, "no_extension")
        with open(no_ext_file, "w") as f:
            f.write("This file has no extension.")
        assert get_file_extension(no_ext_file) == ""

        # Test with multiple dots
        multi_dot_file = os.path.join(self.temp_dir, "archive.tar.gz")
        with open(multi_dot_file, "w") as f:
            f.write("This is a fake archive file.")
        assert get_file_extension(multi_dot_file) == "gz"

    def test_create_temp_file(self):
        """Test the create_temp_file function."""
        # Test creating an empty temporary file
        temp_file = create_temp_file()
        assert os.path.exists(temp_file)
        assert os.path.getsize(temp_file) == 0

        # Test creating a temporary file with content
        temp_file_with_content = create_temp_file("This is content.", ".log")
        assert os.path.exists(temp_file_with_content)
        assert temp_file_with_content.endswith(".log")
        with open(temp_file_with_content, "r") as f:
            assert f.read() == "This is content."

        # Clean up
        os.unlink(temp_file)
        os.unlink(temp_file_with_content)

    def test_create_temp_directory(self):
        """Test the create_temp_directory function."""
        # Test creating a temporary directory
        temp_dir = create_temp_directory()
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)

        # Clean up
        os.rmdir(temp_dir)
