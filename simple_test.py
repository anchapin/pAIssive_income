"""Simple test module to verify pytest functionality."""
# Ruff S101: Use of assert is expected in test files and is allowed here.

EXPECTED_SUM = 2


def test_simple() -> None:
    """A simple test to verify that pytest works (assert is allowed in test files)."""
    # nosec B101 - This is a test file, assert is expected
    assert EXPECTED_SUM == 1 + 1  # noqa: S101
