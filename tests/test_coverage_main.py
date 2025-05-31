"""
Test file to ensure we have at least 80% test coverage.
This file imports and tests the main modules of the application.
"""
import importlib
import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the root directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the main modules
from common_utils.logging import get_logger
from users.auth import hash_credential, verify_credential


def test_hash_and_verify_credential():
    """Test the hash_credential and verify_credential functions."""
    # Test with a valid credential
    credential = "test_password123"
    hashed = hash_credential(credential)

    # Verify the result is a string
    assert isinstance(hashed, str)

    # Verify the hash is not the original credential
    assert hashed != credential

    # Verify the credential
    assert verify_credential(credential, hashed) is True

    # Verify with wrong credential
    assert verify_credential("wrong_password", hashed) is False


def test_get_logger():
    """Test the get_logger function."""
    logger = get_logger("test_module")
    assert logger is not None
    assert logger.name == "test_module"


# Create a test for each module to ensure they are imported and covered
@pytest.mark.parametrize(
    "module_name",
    [
        "users.auth",
        "common_utils.logging",
    ]
)
def test_module_imports(module_name):
    """Test that modules can be imported."""
    module = importlib.import_module(module_name)
    assert module is not None


# Test the hash_credential function with various inputs
@pytest.mark.parametrize(
    ("credential", "expected_exception"),
    [
        ("password123", None),
        ("", ValueError),
        (None, ValueError),
    ]
)
def test_hash_credential_parametrized(credential, expected_exception):
    """Test hash_credential with various inputs."""
    if expected_exception:
        with pytest.raises(expected_exception):
            hash_credential(credential)
    else:
        result = hash_credential(credential)
        assert isinstance(result, str)
        assert result.startswith("$2b$")


# Test the verify_credential function with various inputs
@pytest.mark.parametrize(
    ("plain_credential", "hashed_credential", "expected_result"),
    [
        ("password123", "$2b$12$abcdefghijklmnopqrstuvwxyz123456789", False),  # Invalid hash
        ("", "$2b$12$abcdefghijklmnopqrstuvwxyz123456789", False),  # Empty credential
        ("password123", "", False),  # Empty hash
        (None, "$2b$12$abcdefghijklmnopqrstuvwxyz123456789", False),  # None credential
        ("password123", None, False),  # None hash
    ]
)
def test_verify_credential_parametrized(plain_credential, hashed_credential, expected_result):
    """Test verify_credential with various inputs."""
    result = verify_credential(plain_credential, hashed_credential)
    assert result is expected_result


# Test exception handling in verify_credential
def test_verify_credential_exceptions():
    """Test exception handling in verify_credential."""
    with patch("bcrypt.checkpw") as mock_checkpw:
        mock_checkpw.side_effect = Exception("Test exception")
        result = verify_credential("password123", "$2b$12$abcdefghijklmnopqrstuvwxyz123456789")
        assert result is False


# Test the backward compatibility aliases
def test_backward_compatibility_aliases():
    """Test the backward compatibility aliases."""
    from users.auth import hash_auth, verify_auth

    # Test that hash_auth is an alias for hash_credential
    assert hash_auth is hash_credential

    # Test that verify_auth is an alias for verify_credential
    assert verify_auth is verify_credential
