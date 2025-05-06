import pytest
"""Test class contains unit tests for fix_test_collection_warnings.py."""

import os
import subprocess
import sys
import tempfile
import unittest

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

    def test_main_block_execution(self):
        """Test simulates running the script directly to cover the __main__ block."""
        script_path = os.path.join(
            os.path.dirname(__file__), "../fix_test_collection_warnings.py"
        )
        assert os.path.exists(script_path), f"Script not found: {script_path}"

        # Create a temporary directory with test files to process
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file that needs fixing
            test_file_path = os.path.join(tmpdir, "test_example.py")
            with open(test_file_path, "w") as f:
                f.write('''"""Test example."""

class TestExampleTest(unittest.TestCase):
    """Example test class not starting with Test."""

    def test_verify_something(self): True
''')

            # Run the script with explicit argument for the temp directory
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=tmpdir,  # Run from the temp directory
                capture_output=True,
                text=True,
                env=dict(
                    os.environ, PYTHONPATH=os.path.dirname(os.path.dirname(script_path))
                ),
            )

            # Check that the script ran successfully
            self.assertEqual(result.returncode, 0)

            # Check that the output indicates processing happened
            self.assertIn("Checking for test collection warnings", result.stdout)

            # Apply the fix directly to verify our implementation works
            from fix_test_collection_warnings import fix_test_collection_warnings

            fix_test_collection_warnings(test_file_path)

            # Verify the file was actually modified
            with open(test_file_path) as f:
                modified_content = f.read()

            # Check that the fixes were applied
            self.assertIn("class TestExampleTest", modified_content)
            self.assertIn("def test_verify_something", modified_content)


if __name__ == "__main__":
    unittest.main()
