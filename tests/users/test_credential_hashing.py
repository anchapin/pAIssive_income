"""test_credential_hashing - Module for tests/users.test_credential_hashing."""

# Standard library imports

# Third-party imports
import logging

import pytest

# Local imports
from users.auth import hash_credential, verify_credential


def test_hash_credential():
    """Test that hash_credential returns a bcrypt hash."""
    credential = "test_credential"
    hashed = hash_credential(credential)

    # Check that the hash is a string object (as per updated implementation)
    assert isinstance(hashed, str)

    # Check that the hash starts with the bcrypt identifier
    assert hashed.startswith("$2b$")

    # Check that the hash is not the same as the original credential
    assert hashed != credential.encode("utf-8")


def test_verify_credential_success():
    """Test that verify_credential returns True for a correct credential."""
    credential = "test_credential"
    hashed = hash_credential(credential)

    # Verify the credential
    assert verify_credential(credential, hashed)


def test_verify_credential_failure():
    """Test that verify_credential returns False for an incorrect credential."""
    credential = "test_credential"
    wrong_credential = "wrong_credential"
    hashed = hash_credential(credential)

    # Verify the wrong credential
    assert not verify_credential(wrong_credential, hashed)


def test_verify_credential_empty():
    """Test that verify_credential returns False for empty inputs."""
    # Empty credential
    hashed = hash_credential("test_credential")
    assert not verify_credential("", hashed)

    # Empty hash
    assert not verify_credential("test_credential", "")

    # Both empty
    assert not verify_credential("", "")


def test_hash_credential_empty():
    """Test that hash_credential raises ValueError for empty credential."""
    with pytest.raises(ValueError, match="Authentication credential cannot be empty"):
        hash_credential("")


def test_bcrypt_rounds():
    """Test that the bcrypt hash uses the correct number of rounds."""
    credential = "test_credential"
    hashed = hash_credential(credential)

    # Extract the number of rounds from the hash
    # The format is $2b$XX$ where XX is the number of rounds
    rounds = int(hashed[4:6])

    # Check that the number of rounds matches our default implementation
    default_rounds = 12  # Default bcrypt rounds in our implementation
    assert rounds == default_rounds


def test_different_hashes():
    """Test that hashing the same credential twice produces different hashes."""
    credential = "test_credential"
    hash1 = hash_credential(credential)
    hash2 = hash_credential(credential)

    # Check that the hashes are different (due to different salts)
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_credential(credential, hash1)
    assert verify_credential(credential, hash2)
