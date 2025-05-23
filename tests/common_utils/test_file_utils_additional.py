"""Additional tests for the common_utils.file_utils module to improve coverage."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

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


class TestFileUtilsAdditional:
    """Additional test suite for file utility functions to improve coverage."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up after each test."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.temp_dir)

    def test_ensure_directory_exists_with_path_object(self):
        """Test ensure_directory_exists with a Path object."""
        path_obj = Path(self.temp_dir) / "path_obj_dir"
        result = ensure_directory_exists(path_obj)
        assert path_obj.exists()
        assert path_obj.is_dir()
        assert result == path_obj

    def test_list_files_with_path_object(self):
        """Test list_files with a Path object."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")

        # Use Path object
        path_obj = Path(self.temp_dir)
        files = list_files(path_obj)
        assert len(files) == 1
        assert files[0].name == "test.txt"

    def test_list_files_with_multiple_patterns(self):
        """Test list_files with multiple file patterns."""
        # Create test files with different extensions
        txt_file = os.path.join(self.temp_dir, "test.txt")
        py_file = os.path.join(self.temp_dir, "test.py")
        md_file = os.path.join(self.temp_dir, "test.md")

        for file_path in [txt_file, py_file, md_file]:
            with open(file_path, "w") as f:
                f.write(f"Content for {file_path}")

        # Test with txt files
        txt_files = list_files(self.temp_dir, "*.txt")
        assert len(txt_files) == 1
        assert txt_files[0].name == "test.txt"

        # Test with py files
        py_files = list_files(self.temp_dir, "*.py")
        assert len(py_files) == 1
        assert py_files[0].name == "test.py"

        # Test with md files
        md_files = list_files(self.temp_dir, "*.md")
        assert len(md_files) == 1
        assert md_files[0].name == "test.md"

    def test_read_file_with_different_encodings(self):
        """Test read_file with different encodings."""
        # Create a test file with UTF-8 encoding
        utf8_file = os.path.join(self.temp_dir, "utf8.txt")
        utf8_content = "UTF-8 content with special chars: äöüß"
        with open(utf8_file, "w", encoding="utf-8") as f:
            f.write(utf8_content)

        # Read with UTF-8 encoding
        content = read_file(utf8_file, encoding="utf-8")
        assert content == utf8_content

        # Create a test file with Latin-1 encoding
        latin1_file = os.path.join(self.temp_dir, "latin1.txt")
        latin1_content = "Latin-1 content with special chars: äöüß"
        with open(latin1_file, "w", encoding="latin-1") as f:
            f.write(latin1_content)

        # Read with Latin-1 encoding
        content = read_file(latin1_file, encoding="latin-1")
        assert content == latin1_content

    def test_read_file_with_other_exceptions(self):
        """Test read_file with exceptions other than PermissionError."""
        # Create a test file path
        test_file = os.path.join(self.temp_dir, "test.txt")

        # Create the file so it exists (to pass the existence check)
        with open(test_file, "w") as f:
            f.write("Test content")

        # Test with IOError using a context manager to patch open
        with patch("builtins.open") as mock_open_io:
            # Configure the mock to raise IOError when called
            mock_open_io.side_effect = IOError("IO Error")

            # Test with IOError
            with pytest.raises(IOError):
                read_file(test_file)

        # Test with UnicodeDecodeError using a separate context manager
        with patch("builtins.open") as mock_open_unicode:
            # Configure the mock to raise UnicodeDecodeError when called
            mock_open_unicode.side_effect = UnicodeDecodeError("utf-8", b"test", 0, 1, "Invalid byte")

            # Test with UnicodeDecodeError
            with pytest.raises(UnicodeDecodeError):
                read_file(test_file)

    def test_write_file_without_create_dirs(self):
        """Test write_file with create_dirs=False."""
        # Create a nested path
        nested_file = os.path.join(self.temp_dir, "nested", "test.txt")

        # Try to write without creating directories
        with pytest.raises(FileNotFoundError):
            write_file(nested_file, "Test content", create_dirs=False)

        # Create the directory and try again
        os.makedirs(os.path.join(self.temp_dir, "nested"))
        write_file(nested_file, "Test content", create_dirs=False)

        # Verify the file was created
        assert os.path.isfile(nested_file)
        with open(nested_file, "r") as f:
            assert f.read() == "Test content"

    def test_copy_file_without_create_dirs(self):
        """Test copy_file with create_dirs=False."""
        # Create a source file
        source_file = os.path.join(self.temp_dir, "source.txt")
        with open(source_file, "w") as f:
            f.write("Source content")

        # Try to copy to a nested path without creating directories
        dest_file = os.path.join(self.temp_dir, "nested", "dest.txt")
        with pytest.raises(FileNotFoundError):
            copy_file(source_file, dest_file, create_dirs=False)

        # Create the directory and try again
        os.makedirs(os.path.join(self.temp_dir, "nested"))
        copy_file(source_file, dest_file, create_dirs=False)

        # Verify the file was copied
        assert os.path.isfile(dest_file)
        with open(dest_file, "r") as f:
            assert f.read() == "Source content"

    def test_get_file_extension_with_multiple_dots(self):
        """Test get_file_extension with multiple dots in filename."""
        # Test with multiple dots in filename
        assert get_file_extension("file.name.with.dots.txt") == "txt"
        assert get_file_extension("archive.tar.gz") == "gz"

        # Test with hidden files
        # Note: Path.suffix for ".hidden.file" returns ".file", so lstrip(".") gives "file"
        assert get_file_extension(".hidden.file") == "file"
        # For a file named just ".hidden", Path.suffix returns ".hidden" but the current implementation
        # returns an empty string because it's treated as a hidden file without extension
        assert get_file_extension(".hidden") == ""

        # Test with Path object
        assert get_file_extension(Path("file.txt")) == "txt"
        assert get_file_extension(Path("/path/to/file.txt")) == "txt"

    def test_create_temp_file_with_binary_content(self):
        """Test create_temp_file with binary content."""
        # Create a temp file
        temp_file = create_temp_file("Test content")

        # Verify the file was created with the correct content
        assert os.path.isfile(temp_file)
        with open(temp_file, "r") as f:
            assert f.read() == "Test content"

        # Clean up
        os.unlink(temp_file)

    @patch("tempfile.mkstemp")
    def test_create_temp_file_with_custom_suffix(self, mock_mkstemp):
        """Test create_temp_file with custom suffix."""
        # Set up mock
        mock_fd = 123
        mock_path = "/tmp/mock_temp_file.custom"
        mock_mkstemp.return_value = (mock_fd, mock_path)

        # Mock os.close to avoid closing a non-existent file descriptor
        with patch("os.close") as mock_close:
            # Mock open to avoid writing to a non-existent file
            with patch("builtins.open", mock_open()) as mock_file:
                # Call the function
                result = create_temp_file("Test content", suffix=".custom")

                # Verify the function called mkstemp with the correct suffix
                mock_mkstemp.assert_called_once_with(suffix=".custom")

                # Verify the function closed the file descriptor
                mock_close.assert_called_once_with(mock_fd)

                # Verify the function opened the file for writing
                mock_file.assert_called_once_with(mock_path, "w")

                # Verify the function wrote the content
                mock_file().write.assert_called_once_with("Test content")

                # Verify the function returned the path
                assert result == mock_path
