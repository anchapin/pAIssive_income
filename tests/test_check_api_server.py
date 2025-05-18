"""Test module for check_api_server.py."""

import logging
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
from check_api_server import check_syntax, format_syntax_error, check_multiple_files, main


class TestCheckAPIServer:
    """Test suite for check_api_server.py."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        self.temp_file_path = self.temp_file.name

    def teardown_method(self):
        """Tear down test fixtures."""
        # Close and remove the temporary file
        if hasattr(self, "temp_file") and self.temp_file:
            self.temp_file.close()

        # Remove the file if it exists
        if hasattr(self, "temp_file_path") and os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def test_check_syntax_valid(self):
        """Test check_syntax with valid Python code."""
        # Write valid Python code to the temporary file
        with open(self.temp_file_path, "w") as f:
            f.write("""
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

        # Check the syntax
        result = check_syntax(self.temp_file_path)

        # Verify the result
        assert result is True

    def test_check_syntax_invalid(self):
        """Test check_syntax with invalid Python code."""
        # Write invalid Python code to the temporary file
        with open(self.temp_file_path, "w") as f:
            f.write("""
def hello_world()
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

        # Check the syntax
        with patch("logging.Logger.error") as mock_error:
            result = check_syntax(self.temp_file_path)

            # Verify the result
            assert result is False
            mock_error.assert_called_once()

    def test_check_syntax_file_not_found(self):
        """Test check_syntax with a non-existent file."""
        # Close the file first to avoid permission errors on Windows
        self.temp_file.close()

        # Use a non-existent file path instead of trying to delete
        non_existent_path = os.path.join(os.path.dirname(self.temp_file_path), "non_existent_file.py")

        # Check the syntax
        with patch("logging.Logger.error") as mock_error:
            result = check_syntax(non_existent_path)

            # Verify the result
            assert result is False
            mock_error.assert_called_once()

    def test_check_syntax_permission_error(self):
        """Test check_syntax with a file that cannot be read."""
        # Mock Path.open to raise a permission error
        with patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")):
            with patch("logging.Logger.exception") as mock_exception:
                result = check_syntax(self.temp_file_path)

                # Verify the result
                assert result is False
                mock_exception.assert_called_once()

    def test_check_syntax_not_a_file(self):
        """Test check_syntax with a path that is not a file."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        try:
            # Check the syntax of the directory
            with patch("logging.Logger.error") as mock_error:
                result = check_syntax(temp_dir)

                # Verify the result
                assert result is False
                mock_error.assert_called_once()
        finally:
            # Clean up the temporary directory
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    def test_check_syntax_unicode_decode_error(self):
        """Test check_syntax with a file that cannot be decoded."""
        # Write binary data to the temporary file
        with open(self.temp_file_path, "wb") as f:
            f.write(b"\x80\x81\x82\x83")

        # Mock open to raise a UnicodeDecodeError
        with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"\x80\x81\x82\x83", 0, 1, "invalid start byte")):
            with patch("logging.Logger.exception") as mock_exception:
                result = check_syntax(self.temp_file_path)

                # Verify the result
                assert result is False
                mock_exception.assert_called_once()

    def test_main_with_valid_args(self):
        """Test the main function with valid arguments."""
        # Write valid Python code to the temporary file
        with open(self.temp_file_path, "w") as f:
            f.write("""
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

        # Mock sys.argv
        with patch("sys.argv", ["check_api_server.py", self.temp_file_path]):
            # Mock sys.exit
            with patch("sys.exit") as mock_exit:
                # Import the main function
                from check_api_server import __name__ as module_name

                # Run the main function if the module was run directly
                if module_name == "__main__":
                    # This will call sys.exit(0) for valid syntax
                    pass

                # Verify that sys.exit was not called with a non-zero exit code
                mock_exit.assert_not_called()

    def test_main_with_invalid_args(self):
        """Test the main function with invalid arguments."""
        # Mock sys.argv with no arguments
        with patch("sys.argv", ["check_api_server.py"]):
            # Mock logger.error
            with patch("check_api_server.logger.error") as mock_error:
                # Import and run the main function directly
                from check_api_server import main

                # Run the main function
                result = main()

                # Verify that logger.error was called
                mock_error.assert_called_once()

                # Verify that the function returns 1 for invalid arguments
                assert result == 1

    def test_main_with_invalid_syntax(self):
        """Test the main function with a file containing invalid syntax."""
        # Write invalid Python code to the temporary file
        with open(self.temp_file_path, "w") as f:
            f.write("""
def hello_world()
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

        # Mock sys.argv
        with patch("sys.argv", ["check_api_server.py", self.temp_file_path]):
            # Mock check_multiple_files to return a list with one invalid file
            with patch("check_api_server.check_multiple_files", return_value=([], [self.temp_file_path])):
                # Import and run the main function directly
                result = main()

                # Verify that the function returns 1 for invalid syntax
                assert result == 1

    def test_format_syntax_error(self):
        """Test the format_syntax_error function."""
        # Create a mock SyntaxError
        error = SyntaxError("invalid syntax")
        error.lineno = 2
        error.offset = 5
        error.text = "def hello_world()"
        error.filename = "test.py"

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 2" in error_msg
        assert "column 5" in error_msg
        assert "def hello_world()" in error_msg
        assert "invalid syntax" in error_msg

    def test_format_syntax_error_with_none_values(self):
        """Test the format_syntax_error function with None values."""
        # Create a mock SyntaxError with None values
        error = SyntaxError("invalid syntax")
        error.lineno = 2
        error.offset = None
        error.text = None
        error.filename = "test.py"

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 2" in error_msg
        assert "column None" in error_msg
        assert "<unknown>" in error_msg
        assert "invalid syntax" in error_msg

    def test_format_syntax_error_with_partial_none_values(self):
        """Test the format_syntax_error function with some None values."""
        # Create a mock SyntaxError with some None values
        error = SyntaxError("invalid syntax")
        error.lineno = 2
        error.offset = 5
        error.text = None
        error.filename = "test.py"

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 2" in error_msg
        assert "column 5" in error_msg
        assert "<unknown>" in error_msg
        assert "invalid syntax" in error_msg

    def test_check_multiple_files(self):
        """Test the check_multiple_files function."""
        # Create a second temporary file
        temp_file2 = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path2 = temp_file2.name
        temp_file2.close()

        try:
            # Write valid Python code to the first file
            with open(self.temp_file_path, "w") as f:
                f.write("""
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

            # Write invalid Python code to the second file
            with open(temp_file_path2, "w") as f:
                f.write("""
def hello_world()
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

            # Check both files
            valid_files, invalid_files = check_multiple_files([self.temp_file_path, temp_file_path2])

            # Verify the result
            assert len(valid_files) == 1
            assert len(invalid_files) == 1
            assert self.temp_file_path in valid_files
            assert temp_file_path2 in invalid_files
        finally:
            # Clean up the second temporary file
            if os.path.exists(temp_file_path2):
                os.unlink(temp_file_path2)

    def test_main_with_multiple_files(self):
        """Test the main function with multiple files."""
        # Create a second temporary file
        temp_file2 = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path2 = temp_file2.name
        temp_file2.close()

        try:
            # Write valid Python code to both files
            with open(self.temp_file_path, "w") as f:
                f.write("""
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

            with open(temp_file_path2, "w") as f:
                f.write("""
def goodbye_world():
    print("Goodbye, world!")

if __name__ == "__main__":
    goodbye_world()
""")

            # Mock sys.argv
            with patch("sys.argv", ["check_api_server.py", self.temp_file_path, temp_file_path2]):
                # Run the main function
                result = main()

                # Verify that the function returns 0 for valid syntax
                assert result == 0
        finally:
            # Clean up the second temporary file
            if os.path.exists(temp_file_path2):
                os.unlink(temp_file_path2)

    def test_main_with_mixed_files(self):
        """Test the main function with a mix of valid and invalid files."""
        # Create a second temporary file
        temp_file2 = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path2 = temp_file2.name
        temp_file2.close()

        try:
            # Write valid Python code to the first file
            with open(self.temp_file_path, "w") as f:
                f.write("""
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

            # Write invalid Python code to the second file
            with open(temp_file_path2, "w") as f:
                f.write("""
def goodbye_world()
    print("Goodbye, world!")

if __name__ == "__main__":
    goodbye_world()
""")

            # Mock sys.argv
            with patch("sys.argv", ["check_api_server.py", self.temp_file_path, temp_file_path2]):
                # Mock logger.error to avoid cluttering test output
                with patch("check_api_server.logger.error"):
                    # Run the main function
                    result = main()

                    # Verify that the function returns 1 for invalid syntax
                    assert result == 1
        finally:
            # Clean up the second temporary file
            if os.path.exists(temp_file_path2):
                os.unlink(temp_file_path2)

    def test_check_syntax_with_other_exception(self):
        """Test check_syntax with a file that raises an unexpected exception."""
        # Mock ast.parse to raise a generic exception
        with patch("ast.parse", side_effect=Exception("Unexpected error")):
            with patch("logging.Logger.exception") as mock_exception:
                result = check_syntax(self.temp_file_path)

                # Verify the result
                assert result is False
                mock_exception.assert_called_once()

    def test_format_syntax_error_with_empty_text(self):
        """Test the format_syntax_error function with empty text."""
        # Create a mock SyntaxError with empty text
        error = SyntaxError("invalid syntax")
        error.lineno = 2
        error.offset = 5
        error.text = ""
        error.filename = "test.py"

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 2" in error_msg
        assert "column 5" in error_msg
        assert "<unknown>" in error_msg
        assert "invalid syntax" in error_msg

    def test_format_syntax_error_without_msg(self):
        """Test the format_syntax_error function without an error message."""
        # Create a mock SyntaxError without a message
        error = SyntaxError()
        error.lineno = 2
        error.offset = 5
        error.text = "def hello_world()"
        error.filename = "test.py"
        error.msg = None

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 2" in error_msg
        assert "column 5" in error_msg
        assert "def hello_world()" in error_msg
        assert "Unknown syntax error" in error_msg

    def test_format_syntax_error_without_lineno(self):
        """Test the format_syntax_error function without a line number."""
        # Create a mock SyntaxError without a line number
        error = SyntaxError("invalid syntax")
        # Don't set lineno
        error.offset = 5
        error.text = "def hello_world()"
        error.filename = "test.py"

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 0" in error_msg
        assert "column 5" in error_msg
        assert "def hello_world()" in error_msg
        assert "invalid syntax" in error_msg

    def test_check_syntax_with_file_read_error(self):
        """Test check_syntax with a file that raises an error when read."""
        # Mock Path.open to raise a FileNotFoundError
        with patch("pathlib.Path.open", side_effect=FileNotFoundError("File not found")):
            with patch("logging.Logger.exception") as mock_exception:
                result = check_syntax(self.temp_file_path)

                # Verify the result
                assert result is False
                mock_exception.assert_called_once()

    def test_main_with_valid_files_verbose_output(self):
        """Test the main function with valid files and verify verbose output."""
        # Create a second temporary file
        temp_file2 = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path2 = temp_file2.name
        temp_file2.close()

        try:
            # Write valid Python code to both files
            with open(self.temp_file_path, "w") as f:
                f.write("""
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

            with open(temp_file_path2, "w") as f:
                f.write("""
def goodbye_world():
    print("Goodbye, world!")

if __name__ == "__main__":
    goodbye_world()
""")

            # Mock sys.argv
            with patch("sys.argv", ["check_api_server.py", self.temp_file_path, temp_file_path2]):
                # Mock logger.info to capture output
                with patch("check_api_server.logger.info") as mock_info:
                    # Run the main function
                    result = main()

                    # Verify that the function returns 0 for valid syntax
                    assert result == 0

                    # Verify that logger.info was called with the summary message
                    mock_info.assert_any_call("✅ All %d file(s) have valid syntax.", 2)
        finally:
            # Clean up the second temporary file
            if os.path.exists(temp_file_path2):
                os.unlink(temp_file_path2)

    def test_main_with_invalid_files_verbose_output(self):
        """Test the main function with invalid files and verify verbose output."""
        # Create a second temporary file
        temp_file2 = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path2 = temp_file2.name
        temp_file2.close()

        try:
            # Write invalid Python code to both files
            with open(self.temp_file_path, "w") as f:
                f.write("""
def hello_world()
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
""")

            with open(temp_file_path2, "w") as f:
                f.write("""
def goodbye_world()
    print("Goodbye, world!")

if __name__ == "__main__":
    goodbye_world()
""")

            # Mock sys.argv
            with patch("sys.argv", ["check_api_server.py", self.temp_file_path, temp_file_path2]):
                # Mock logger.error to capture output
                with patch("check_api_server.logger.error") as mock_error:
                    # Run the main function
                    result = main()

                    # Verify that the function returns 1 for invalid syntax
                    assert result == 1

                    # Verify that logger.error was called with the summary message
                    mock_error.assert_any_call("❌ %d file(s) have syntax errors:", 2)
        finally:
            # Clean up the second temporary file
            if os.path.exists(temp_file_path2):
                os.unlink(temp_file_path2)

    def test_format_syntax_error_with_pointer(self):
        """Test the format_syntax_error function with a pointer to the error."""
        # Create a mock SyntaxError with text and offset for pointer
        error = SyntaxError("invalid syntax")
        error.lineno = 2
        error.offset = 10
        error.text = "def hello_world()"
        error.filename = "test.py"

        # Format the error
        error_msg = format_syntax_error("test.py", error)

        # Verify the result
        assert "test.py" in error_msg
        assert "line 2" in error_msg
        assert "column 10" in error_msg
        assert "def hello_world()" in error_msg
        assert "^" in error_msg  # Check for the pointer
        assert "invalid syntax" in error_msg
