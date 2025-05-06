"""Test class contains unit tests for dependency_container.py."""

import subprocess
import sys
import unittest

import dependency_container


class TestDependencyContainer(unittest.TestCase):
    """Test dependency container."""

    def test_main_function(self):
        """Test main function.

        Test simply calls the main function to ensure it runs without error
        and increases code coverage for dependency_container.py
        """
        try:
            dependency_container.main()
            self.assertTrue(True)  # Assert True if main runs without exception
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_block_execution(self):
        """Test main block execution.

        Test simulates running dependency_container.py directly to cover the
        if __name__ == "__main__": block.
        """
        result = subprocess.run([sys.executable, "dependency_container.py"], check=True)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
