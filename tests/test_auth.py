"""test_auth - Test module for users.auth."""

import logging
import unittest
from unittest.mock import MagicMock, patch

import bcrypt
import pytest

from users.auth import hash_credential, verify_credential, hash_auth, verify_auth


class TestAuthFunctions(unittest.TestCase):
    """Test suite for authentication functions."""

    def test_hash_credential(self):
        """Test hashing a credential."""
        # Test with a valid credential
        credential = "password123"
        hashed = hash_credential(credential)

        # Verify the result is a string
        self.assertIsInstance(hashed, str)

        # Verify the hash is not the original credential
        self.assertNotEqual(hashed, credential)

        # Verify the hash can be verified with bcrypt
        self.assertTrue(
            bcrypt.checkpw(
                credential.encode('utf-8'),
                hashed.encode('utf-8')
            )
        )

    def test_hash_credential_empty(self):
        """Test hashing an empty credential raises an error."""
        with self.assertRaises(ValueError) as context:
            hash_credential("")

        self.assertEqual(
            str(context.exception),
            "Authentication credential cannot be empty"
        )

    def test_hash_credential_none(self):
        """Test hashing a None credential raises an error."""
        with self.assertRaises(ValueError) as context:
            hash_credential(None)

        self.assertEqual(
            str(context.exception),
            "Authentication credential cannot be empty"
        )

    def test_verify_credential_valid(self):
        """Test verifying a valid credential."""
        # Create a hashed credential
        plain_credential = "password123"
        hashed_credential = bcrypt.hashpw(
            plain_credential.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Verify the credential
        result = verify_credential(plain_credential, hashed_credential)
        self.assertTrue(result)

    def test_verify_credential_invalid(self):
        """Test verifying an invalid credential."""
        # Create a hashed credential
        plain_credential = "password123"
        wrong_credential = "wrong_password"
        hashed_credential = bcrypt.hashpw(
            plain_credential.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Verify with wrong credential
        result = verify_credential(wrong_credential, hashed_credential)
        self.assertFalse(result)

    def test_verify_credential_empty_plain(self):
        """Test verifying with an empty plain credential."""
        hashed_credential = bcrypt.hashpw(
            b"password123",
            bcrypt.gensalt()
        ).decode('utf-8')

        result = verify_credential("", hashed_credential)
        self.assertFalse(result)

    def test_verify_credential_empty_hashed(self):
        """Test verifying with an empty hashed credential."""
        result = verify_credential("password123", "")
        self.assertFalse(result)

    def test_verify_credential_none_plain(self):
        """Test verifying with a None plain credential."""
        hashed_credential = bcrypt.hashpw(
            b"password123",
            bcrypt.gensalt()
        ).decode('utf-8')

        result = verify_credential(None, hashed_credential)
        self.assertFalse(result)

    def test_verify_credential_none_hashed(self):
        """Test verifying with a None hashed credential."""
        result = verify_credential("password123", None)
        self.assertFalse(result)

    def test_verify_credential_bytes_hashed(self):
        """Test verifying with bytes hashed credential."""
        plain_credential = "password123"
        hashed_credential = bcrypt.hashpw(
            plain_credential.encode('utf-8'),
            bcrypt.gensalt()
        )  # Keep as bytes

        # Verify the credential
        result = verify_credential(plain_credential, hashed_credential)
        self.assertTrue(result)

    def test_verify_credential_invalid_format(self):
        """Test verifying with an invalid hashed credential format."""
        with patch('users.auth.logger') as mock_logger:
            result = verify_credential("password123", "invalid_hash_format")
            self.assertFalse(result)
            mock_logger.error.assert_called_once()

    def test_verify_credential_exception(self):
        """Test handling of unexpected exceptions during verification."""
        with patch('bcrypt.checkpw') as mock_checkpw, patch('users.auth.logger') as mock_logger:
            mock_checkpw.side_effect = Exception("Unexpected error")

            result = verify_credential("password123", "hashed_password")

            self.assertFalse(result)
            mock_logger.error.assert_called_once()

    def test_hash_auth_alias(self):
        """Test hash_auth alias function."""
        credential = "password123"

        # Hash using both functions
        hashed1 = hash_credential(credential)
        hashed2 = hash_auth(credential)

        # Verify both can be verified with the original credential
        self.assertTrue(
            bcrypt.checkpw(
                credential.encode('utf-8'),
                hashed1.encode('utf-8')
            )
        )
        self.assertTrue(
            bcrypt.checkpw(
                credential.encode('utf-8'),
                hashed2.encode('utf-8')
            )
        )

    def test_verify_auth_alias(self):
        """Test verify_auth alias function."""
        plain_credential = "password123"
        hashed_credential = bcrypt.hashpw(
            plain_credential.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Verify using both functions
        result1 = verify_credential(plain_credential, hashed_credential)
        result2 = verify_auth(plain_credential, hashed_credential)

        self.assertTrue(result1)
        self.assertTrue(result2)


if __name__ == "__main__":
    unittest.main()
