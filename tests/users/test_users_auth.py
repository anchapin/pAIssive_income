"""test_users_auth - Test module for users.auth."""

# Standard library imports
import unittest
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest
import bcrypt

# Local imports
from users.auth import hash_credential, verify_credential, hash_auth, verify_auth


class TestHashCredential(unittest.TestCase):
    """Test suite for hash_credential function."""

    def test_hash_credential_valid(self):
        """Test hashing a valid credential."""
        # Arrange
        credential = "test_password123"

        # Act
        hashed = hash_credential(credential)

        # Assert
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")  # bcrypt hash format
        assert hashed != credential

    def test_hash_credential_empty(self):
        """Test hashing an empty credential raises an error."""
        # Arrange
        credential = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Authentication credential cannot be empty"):
            hash_credential(credential)

    def test_hash_credential_none(self):
        """Test hashing None raises an error."""
        # Arrange
        credential = None

        # Act & Assert
        with pytest.raises(ValueError, match="Authentication credential cannot be empty"):
            hash_credential(credential)

    @patch('bcrypt.gensalt')
    @patch('bcrypt.hashpw')
    def test_hash_credential_implementation(self, mock_hashpw, mock_gensalt):
        """Test the implementation details of hash_credential."""
        # Arrange
        credential = "test_password123"
        mock_salt = b'mock_salt'
        mock_hash = b'mock_hash'
        mock_gensalt.return_value = mock_salt
        mock_hashpw.return_value = mock_hash

        # Act
        result = hash_credential(credential)

        # Assert
        mock_gensalt.assert_called_once_with(rounds=12)
        mock_hashpw.assert_called_once_with(credential.encode('utf-8'), mock_salt)
        assert result == mock_hash.decode('utf-8')


class TestVerifyCredential(unittest.TestCase):
    """Test suite for verify_credential function."""

    def test_verify_credential_valid_match(self):
        """Test verifying a valid credential that matches the hash."""
        # Arrange
        credential = "test_password123"
        hashed = bcrypt.hashpw(credential.encode('utf-8'), bcrypt.gensalt())

        # Act
        result = verify_credential(credential, hashed)

        # Assert
        assert result

    def test_verify_credential_valid_no_match(self):
        """Test verifying a valid credential that doesn't match the hash."""
        # Arrange
        credential = "test_password123"
        wrong_credential = "wrong_password"
        hashed = bcrypt.hashpw(credential.encode('utf-8'), bcrypt.gensalt())

        # Act
        result = verify_credential(wrong_credential, hashed)

        # Assert
        assert not result

    def test_verify_credential_empty_credential(self):
        """Test verifying an empty credential."""
        # Arrange
        credential = ""
        hashed = bcrypt.hashpw(b"test", bcrypt.gensalt())

        # Act
        result = verify_credential(credential, hashed)

        # Assert
        assert not result

    def test_verify_credential_empty_hash(self):
        """Test verifying against an empty hash."""
        # Arrange
        credential = "test_password123"
        hashed = ""

        # Act
        result = verify_credential(credential, hashed)

        # Assert
        assert not result

    def test_verify_credential_none_values(self):
        """Test verifying with None values."""
        # Arrange & Act
        result1 = verify_credential(None, "hash")
        result2 = verify_credential("credential", None)
        result3 = verify_credential(None, None)

        # Assert
        assert not result1
        assert not result2
        assert not result3

    def test_verify_credential_string_hash(self):
        """Test verifying with a string hash."""
        # Arrange
        credential = "test_password123"
        hashed_bytes = bcrypt.hashpw(credential.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed_bytes.decode('utf-8')

        # Act
        result = verify_credential(credential, hashed_str)

        # Assert
        assert result

    def test_verify_credential_invalid_hash_format(self):
        """Test verifying with an invalid hash format."""
        # Arrange
        credential = "test_password123"
        invalid_hash = "not_a_valid_hash"

        # Act
        result = verify_credential(credential, invalid_hash)

        # Assert
        assert not result

    def test_verify_credential_encoding_error(self):
        """Test verifying with a hash that raises an encoding error."""
        # Arrange
        credential = "test_password123"

        # Use a different approach to simulate an encoding error
        with patch("users.auth.logger") as mock_logger:
            with patch("users.auth.bcrypt.checkpw", side_effect=Exception("Encoding error")):
                # Act
                result = verify_credential(credential, "hashed_password")

        # Assert
        assert result is False
        # Check that logger.exception was called with any arguments
        assert mock_logger.exception.called

    def test_verify_credential_attribute_error(self):
        """Test verifying with a hash that raises AttributeError."""
        # Arrange
        credential = "test_password123"
        mock_hash = MagicMock()
        mock_hash.encode.side_effect = AttributeError("'int' object has no attribute 'encode'")

        # Act
        with patch("users.auth.logger") as mock_logger:
            result = verify_credential(credential, mock_hash)

        # Assert
        assert not result
        # Check that logger.exception was called with any arguments
        assert mock_logger.exception.called

    @patch('bcrypt.checkpw')
    def test_verify_credential_exception_handling(self, mock_checkpw):
        """Test exception handling in verify_credential."""
        # Arrange
        credential = "test_password123"
        hashed = "hashed_credential"
        mock_checkpw.side_effect = Exception("Test exception")

        # Act
        result = verify_credential(credential, hashed)

        # Assert
        assert not result
        mock_checkpw.assert_called_once()


# Add pytest-style tests for compatibility
def test_hash_and_verify_credential_integration():
    """Test the integration of hash_credential and verify_credential."""
    # Arrange
    credential = "test_integration_password"

    # Act
    hashed = hash_credential(credential)
    verify_result = verify_credential(credential, hashed)

    # Assert
    assert verify_result is True

    # Also verify that a wrong credential doesn't match
    wrong_verify_result = verify_credential("wrong_password", hashed)
    assert wrong_verify_result is False


def test_backward_compatibility_aliases():
    """Test that the backward compatibility aliases work correctly."""
    # Test that hash_auth is an alias for hash_credential
    assert hash_auth is hash_credential

    # Test that verify_auth is an alias for verify_credential
    assert verify_auth is verify_credential

    # Test the aliases in action
    credential = "test_password"

    # Hash using the alias
    hashed = hash_auth(credential)

    # Verify using the alias
    assert verify_auth(credential, hashed) is True
    assert verify_auth("wrong_password", hashed) is False


@patch("users.auth.logger")
def test_hash_credential_logging(mock_logger):
    """Test that hash_credential logs appropriately."""
    # Call the function
    hash_credential("test_password")

    # Verify logging
    mock_logger.debug.assert_called_with("Authentication material processing completed")


@patch("users.auth.logger")
def test_verify_credential_logging(mock_logger):
    """Test that verify_credential logs appropriately."""
    # Hash a credential
    credential = "password123"
    hashed = hash_credential(credential)

    # Verify the credential
    verify_credential(credential, hashed)

    # Verify logging
    mock_logger.debug.assert_called_with("Authentication verification completed")
