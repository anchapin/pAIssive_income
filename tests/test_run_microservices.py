import pytest
"""Test class contains unit tests for run_microservices.py."""

import subprocess
import sys
import unittest

import run_microservices


class TestRunMicroservices(unittest.TestCase):
    """Test class contains unit tests for the run_microservices module."""

    def test_main_function(self):
        """Test main function.

        Test simply calls the main function to ensure it runs without error
        and increases code coverage for run_microservices.py.
        """
        try:
            run_microservices.main()
            self.assertTrue(True)  # Assert True if main runs without exception
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running run_microservices.py directly to cover the
        if __name__ == "__main__": block.
        """
        result = subprocess.run([sys.executable, "run_microservices.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
