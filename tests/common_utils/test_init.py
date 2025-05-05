"""Test common utils."""

import subprocess
import sys
import unittest

import common_utils


class TestCommonUtilsInit(unittest.TestCase):
    """Test common utils init."""

    def test_main_function(self):
        """Test main function.

        Test simply calls the main function to ensure it runs without error
        and increases code coverage for common_utils/__init__.py
        """
        try:
            common_utils.main()
            self.assertTrue(True)  # Assert True if main runs without exception
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running common_utils/__init__.py directly to cover the
        # if __name__ == "__main__": block.
        """
        result = subprocess.run(
            [sys.executable, "common_utils/__init__.py"], check=True
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
