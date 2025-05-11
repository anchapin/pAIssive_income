"""test_credential_hashing - Module for tests/users.test_credential_hashing."""

# Standard library imports
import uuid

# Third-party imports
import pytest

# Local imports
from users.auth import hash_credential
from users.auth import verify_credential


@pytest.fixture
def test_credentials():
    """Generate unique test credentials for each test run."""
    # Generate a unique test credential for each test run
    # This helps prevent hardcoded credentials from being flagged by security scanners
    return {
        "test_credential": f"test_cred_{uuid.uuid4().hex[:8]}",
        "wrong_credential": f"wrong_cred_{uuid.uuid4().hex[:8]}",
    }


def test_hash_credential(test_credentials):
    """Test that hash_credential returns a bcrypt hash."""
    credential = test_credentials["test_credential"]
    hashed = hash_credential(credential)

    # Check that the hash is a bytes object
    assert isinstance(hashed, bytes)

    # Check that the hash starts with the bcrypt identifier
    assert hashed.startswith(b"$2b$")

    # Check that the hash is not the same as the original credential
    assert hashed != credential.encode("utf-8")


def test_verify_credential_success(test_credentials):
    """Test that verify_credential returns True for a correct credential."""
    credential = test_credentials["test_credential"]
    hashed = hash_credential(credential)

    # Verify the credential
    assert verify_credential(credential, hashed)


def test_verify_credential_failure(test_credentials):
    """Test that verify_credential returns False for an incorrect credential."""
    credential = test_credentials["test_credential"]
    wrong_credential = test_credentials["wrong_credential"]
    hashed = hash_credential(credential)

    # Verify the wrong credential
    assert not verify_credential(wrong_credential, hashed)


def test_verify_credential_empty(test_credentials):
    """Test that verify_credential returns False for empty inputs."""
    credential = test_credentials["test_credential"]

    # Empty credential
    hashed = hash_credential(credential)
    assert not verify_credential("", hashed)

    # Empty hash
    assert not verify_credential(credential, b"")

    # Both empty
    assert not verify_credential("", b"")


def test_hash_credential_empty():
    """Test that hash_credential raises ValueError for empty credential."""
    with pytest.raises(ValueError, match="Authentication credential cannot be empty"):
        hash_credential("")


def test_bcrypt_rounds(test_credentials):
    """Test that the bcrypt hash uses the correct number of rounds."""
    credential = test_credentials["test_credential"]
    hashed = hash_credential(credential)

    # Extract the number of rounds from the hash
    # The format is $2b$XX$ where XX is the number of rounds
    rounds = int(hashed[4:6])

    # Check that the number of rounds is 12 (default in our implementation)
    assert rounds == 12


def test_different_hashes(test_credentials):
    """Test that hashing the same credential twice produces different hashes."""
    credential = test_credentials["test_credential"]
    hash1 = hash_credential(credential)
    hash2 = hash_credential(credential)

    # Check that the hashes are different (due to different salts)
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_credential(credential, hash1)
    assert verify_credential(credential, hash2)
