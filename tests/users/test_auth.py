"""test_auth - Test module for users.auth."""

# Standard library imports
import unittest
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest
import bcrypt

# Local imports
from users.auth import hash_credential, verify_credential


class TestHashCredential(unittest.TestCase):
    """Test suite for hash_credential function."""

    def test_hash_credential_valid(self):
        """Test hashing a valid credential."""
        # Arrange
        credential = "test_password123"
        
        # Act
        hashed = hash_credential(credential)
        
        # Assert
        self.assertIsInstance(hashed, str)
        self.assertTrue(hashed.startswith("$2b$"))  # bcrypt hash format
        self.assertNotEqual(hashed, credential)
    
    def test_hash_credential_empty(self):
        """Test hashing an empty credential raises an error."""
        # Arrange
        credential = ""
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            hash_credential(credential)
        
        self.assertIn("Authentication credential cannot be empty", str(context.exception))
    
    def test_hash_credential_none(self):
        """Test hashing None raises an error."""
        # Arrange
        credential = None
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            hash_credential(credential)
        
        self.assertIn("Authentication credential cannot be empty", str(context.exception))
    
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
        self.assertEqual(result, mock_hash.decode('utf-8'))


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
        self.assertTrue(result)
    
    def test_verify_credential_valid_no_match(self):
        """Test verifying a valid credential that doesn't match the hash."""
        # Arrange
        credential = "test_password123"
        wrong_credential = "wrong_password"
        hashed = bcrypt.hashpw(credential.encode('utf-8'), bcrypt.gensalt())
        
        # Act
        result = verify_credential(wrong_credential, hashed)
        
        # Assert
        self.assertFalse(result)
    
    def test_verify_credential_empty_credential(self):
        """Test verifying an empty credential."""
        # Arrange
        credential = ""
        hashed = bcrypt.hashpw(b"test", bcrypt.gensalt())
        
        # Act
        result = verify_credential(credential, hashed)
        
        # Assert
        self.assertFalse(result)
    
    def test_verify_credential_empty_hash(self):
        """Test verifying against an empty hash."""
        # Arrange
        credential = "test_password123"
        hashed = ""
        
        # Act
        result = verify_credential(credential, hashed)
        
        # Assert
        self.assertFalse(result)
    
    def test_verify_credential_none_values(self):
        """Test verifying with None values."""
        # Arrange & Act
        result1 = verify_credential(None, "hash")
        result2 = verify_credential("credential", None)
        result3 = verify_credential(None, None)
        
        # Assert
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
    
    def test_verify_credential_string_hash(self):
        """Test verifying with a string hash."""
        # Arrange
        credential = "test_password123"
        hashed_bytes = bcrypt.hashpw(credential.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed_bytes.decode('utf-8')
        
        # Act
        result = verify_credential(credential, hashed_str)
        
        # Assert
        self.assertTrue(result)
    
    def test_verify_credential_invalid_hash_format(self):
        """Test verifying with an invalid hash format."""
        # Arrange
        credential = "test_password123"
        invalid_hash = "not_a_valid_hash"
        
        # Act
        result = verify_credential(credential, invalid_hash)
        
        # Assert
        self.assertFalse(result)
    
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
        self.assertFalse(result)
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
