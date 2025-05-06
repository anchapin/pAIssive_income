"""Test class contains unit tests for the debug_filtering module."""

import subprocess
import sys
import unittest

import debug_filtering


class TestDebugFiltering(unittest.TestCase):
    """Test class contains unit tests for the debug_filtering module."""

    def test_main_function(self):
        """Test main function.

        Test simply calls the main function to ensure it runs without error
        and increases code coverage for debug_filtering.py
        """
        try:
            debug_filtering.main()
            self.assertTrue(True)  # Assert True if main runs without exception
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running debug_filtering.py directly to cover the
        if __name__ == "__main__": block.
        """
        result = subprocess.run([sys.executable, "debug_filtering.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
