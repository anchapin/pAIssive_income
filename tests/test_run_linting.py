import pytest
"""Test class contains unit tests for run_linting.py."""

import subprocess
import sys
import unittest
from unittest.mock import patch

import run_linting


class TestRunLinting(unittest.TestCase):
    """Test the run_linting module functionality."""

    def test_main_function_no_arguments(self):
        """Test main function when called directly with no arguments."""
        # Patch sys.argv to simulate no command line arguments
        with patch("sys.argv", ["run_linting.py"]):
            result = run_linting.main()
            self.assertEqual(result, 0)

    def test_main_function_with_arguments(self):
        """Test main function when called directly with dummy arguments."""
        # Patch sys.argv to simulate command line arguments
        with patch("sys.argv", ["run_linting.py", "--some-arg", "value"]):
            result = run_linting.main()
            self.assertEqual(result, 0)

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running run_linting.py directly to cover the
        if __name__ == "__main__": block and sys.exit().
        """
        result = subprocess.run([sys.executable, "run_linting.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
