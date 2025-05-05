"""Test class contains unit tests for run_tests.py."""

import subprocess
import sys
import unittest
from unittest.mock import patch

import run_tests


class TestRunTests(unittest.TestCase):
    """Test suite for run_tests.py."""

    def test_main_function_no_arguments(self):
        """Test main function when called directly with no arguments."""
        # Patch sys.argv to simulate no command line arguments
        with patch("sys.argv", ["run_tests.py"]):
            result = run_tests.main()
            self.assertEqual(result, 0)

    def test_main_function_with_arguments(self):
        """Test main function when called directly with dummy arguments."""
        # Patch sys.argv to simulate command line arguments
        with patch("sys.argv", ["run_tests.py", "--some-arg", "value"]):
            result = run_tests.main()
            self.assertEqual(result, 0)

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running run_tests.py directly to cover the
        if __name__ == "__main__": block and sys.exit().
        """
        result = subprocess.run([sys.executable, "run_tests.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
