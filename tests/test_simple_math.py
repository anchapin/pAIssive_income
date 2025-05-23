"""Simple test file to verify that pytest is working."""

import unittest


class TestSimpleMath(unittest.TestCase):
    """Simple test cases for basic math operations."""

    def test_addition(self):
        """Test that addition works."""
        self.assertEqual(1 + 1, 2)

    def test_subtraction(self):
        """Test that subtraction works."""
        self.assertEqual(3 - 1, 2)

    def test_multiplication(self):
        """Test that multiplication works."""
        self.assertEqual(2 * 3, 6)

    def test_division(self):
        """Test that division works."""
        self.assertEqual(6 / 3, 2)


if __name__ == "__main__":
    unittest.main()
