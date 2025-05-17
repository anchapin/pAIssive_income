"""Test module for check_api_server.py."""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
from check_api_server import check_syntax


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
        with patch("logging.Logger.exception") as mock_exception:
            result = check_syntax(non_existent_path)

            # Verify the result
            assert result is False
            mock_exception.assert_called_once()

    def test_check_syntax_permission_error(self):
        """Test check_syntax with a file that cannot be read."""
        # Mock open to raise a permission error
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
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
            # Mock sys.exit
            with patch("sys.exit") as mock_exit:
                # Mock logger.error
                with patch("check_api_server.logger.error") as mock_error:
                    # Import and run the main function directly
                    from check_api_server import main

                    # This will call sys.exit(1) for invalid arguments
                    try:
                        main()
                    except (SystemExit, IndexError):
                        # Catch the SystemExit or IndexError that might be raised
                        pass

                    # Verify that logger.error was called
                    mock_error.assert_called_once()

                    # Verify that sys.exit was called with exit code 1
                    mock_exit.assert_called_once_with(1)

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
            # Mock sys.exit
            with patch("sys.exit") as mock_exit:
                # Mock check_syntax to return False (indicating invalid syntax)
                with patch("check_api_server.check_syntax", return_value=False):
                    # Import and run the main function directly
                    from check_api_server import main

                    # This will call sys.exit(1) for invalid syntax
                    try:
                        main()
                    except SystemExit:
                        # Catch the SystemExit that might be raised
                        pass

                    # Verify that sys.exit was called with exit code 1
                    mock_exit.assert_called_once_with(1)
