"""Test class contains unit tests for the run_local_tests module."""

import subprocess
import sys
import unittest

import run_local_tests


class TestRunLocalTests(unittest.TestCase):
    """Test class contains unit tests for the run_local_tests module."""

    def test_main_function(self):
        """Test main function.

        Test simply calls the main function to ensure it runs without error
        and increases code coverage for run_local_tests.py.
        """
        try:
            run_local_tests.main()
            self.assertTrue(True)  # Assert True if main runs without exception
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running run_local_tests.py directly to cover the
        if __name__ == "__main__": block.
        """
        result = subprocess.run([sys.executable, "run_local_tests.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
