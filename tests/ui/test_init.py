"""Test class contains unit tests for the ui.__init__ module."""

import subprocess
import sys
import unittest

import ui


class TestUIInit(unittest.TestCase):
    """Test UI init.

    Test simply calls the main function to ensure it runs without error
    and increases code coverage for ui/__init__.py.
    """

    def test_main_function(self):
        """Test main function.

        Test simply calls the main function to ensure it runs without error
        and increases code coverage for ui/__init__.py.
        """
        try:
            ui.main()
            self.assertTrue(True)  # Assert True if main runs without exception
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running ui/__init__.py directly to cover the
        if __name__ == "__main__": block.
        """
        result = subprocess.run([sys.executable, "ui/__init__.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
