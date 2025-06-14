"""Simple test module to verify pytest functionality."""

EXPECTED_SUM = 2


def test_simple() -> None:
    """A simple test to verify that pytest works."""
    # nosec B101 - This is a test file, assert is expected
    if EXPECTED_SUM != 1 + 1:
        raise AssertionError("Expected " + str(EXPECTED_SUM) + ", but got " + str(1 + 1))
