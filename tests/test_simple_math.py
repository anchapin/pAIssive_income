"""Simple test file to verify that pytest is working."""


class TestSimpleMath:
    """Simple test cases for basic math operations."""

    def test_addition(self):
        """Test that addition works."""
        assert 1 + 1 == 2

    def test_subtraction(self):
        """Test that subtraction works."""
        assert 3 - 1 == 2

    def test_multiplication(self):
        """Test that multiplication works."""
        assert 2 * 3 == 6

    def test_division(self):
        """Test that division works."""
        assert 6 / 3 == 2
