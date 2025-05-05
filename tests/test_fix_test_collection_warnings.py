"""Test class contains unit tests for fix_test_collection_warnings.py."""

import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

# Import the functions from the script
from fix_test_collection_warnings import find_test_files


class TestFixTestCollectionWarnings(unittest.TestCase):
    """Test class contains unit tests for fix_test_collection_warnings.py."""

    def test_find_test_files(self):
        """Create a temporary directory structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some dummy files
            os.makedirs(os.path.join(tmpdir, "subdir1"))
            os.makedirs(os.path.join(tmpdir, "subdir2"))
            with open(os.path.join(tmpdir, "test_file1.py"), "w") as f:
                f.write("test content")
            with open(os.path.join(tmpdir, "file_not_test.py"), "w") as f:
                f.write("test content")
            with open(os.path.join(tmpdir, "subdir1", "test_file2.py"), "w") as f:
                f.write("test content")
            with open(os.path.join(tmpdir, "subdir2", "another_file.txt"), "w") as f:
                f.write("test content")

            # Call the function and check the results
            found_files = find_test_files(root_dir=tmpdir)

            # Assert that the correct files were found
            expected_files = [
                os.path.join(tmpdir, "test_file1.py"),
                os.path.join(tmpdir, "subdir1", "test_file2.py"),
            ]
            self.assertCountEqual(found_files, expected_files)

    @patch("fix_test_collection_warnings.find_test_files")
    @patch("fix_test_collection_warnings.main")
    @patch("builtins.print")
    def test_main_block_execution(self, mock_print, mock_main, mock_find_files):
        """Test simulates running the script directly to cover the __main__ block."""
        mock_find_files.return_value = ["fake_file1.py", "fake_file2.py"]
        mock_main.return_value = True

        script_path = os.path.join(
            os.path.dirname(__file__), "../fix_test_collection_warnings.py"
        )
        assert os.path.exists(script_path), f"Script not found: {script_path}"

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
        )

        # Assert that the main function was executed and its dependencies were called
        mock_find_files.assert_called_once()
        mock_main.assert_called_once()
        mock_print.assert_any_call("Checking for test collection warnings...")
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
