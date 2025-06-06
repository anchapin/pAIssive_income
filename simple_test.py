"""Simple test module to verify pytest functionality."""

EXPECTED_SUM = 2


def test_simple() -> None:
    """A simple test to verify that pytest works."""
    # nosec B101 - This is a test file, assert is expected
    assert EXPECTED_SUM == 1 + 1  # nosec # noqa: S101
