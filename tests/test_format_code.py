"""Test class contains unit tests for format_code.py."""

import subprocess
import sys
import unittest
from unittest.mock import patch

import format_code


class TestFormatCode(unittest.TestCase):
    """Test class contains unit tests for format_code.py."""

    def test_main_function_no_arguments(self):
        """Test main function when called directly with no arguments."""
        # Patch sys.argv to simulate no command line arguments
        with patch("sys.argv", ["format_code.py"]):
            result = format_code.main()
            self.assertEqual(result, 0)

    def test_main_function_with_arguments(self):
        """Test main function when called directly with dummy arguments."""
        # Patch sys.argv to simulate command line arguments
        with patch("sys.argv", ["format_code.py", "arg1", "arg2"]):
            result = format_code.main()
            self.assertEqual(result, 0)

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running format_code.py directly to cover the
        if __name__ == "__main__": block and sys.exit().
        """
        result = subprocess.run([sys.executable, "format_code.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
