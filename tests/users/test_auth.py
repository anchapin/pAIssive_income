"""Tests for the users.auth module."""

import logging
import unittest
from unittest.mock import MagicMock, patch

import bcrypt
import pytest

from users.auth import hash_auth, hash_credential, verify_auth, verify_credential


class TestAuth(unittest.TestCase):
    """Test cases for the auth module."""

    @patch("bcrypt.gensalt")
    @patch("bcrypt.hashpw")
    def test_hash_credential(self, mock_hashpw, mock_gensalt):
        """Test hash_credential function."""
        # Setup mocks
        mock_salt = b"mock_salt"
        mock_gensalt.return_value = mock_salt
        mock_hashed = b"hashed_credential"
        mock_hashpw.return_value = mock_hashed

        # Test with valid credential
        result = hash_credential("password")

        # Verify mocks were called correctly
        mock_gensalt.assert_called_once_with(rounds=12)
        mock_hashpw.assert_called_once_with(b"password", mock_salt)
        assert result == "hashed_credential"

    def test_hash_credential_empty(self):
        """Test hash_credential with empty credential."""
        with pytest.raises(ValueError):
            hash_credential("")

    @patch("bcrypt.checkpw")
    def test_verify_credential(self, mock_checkpw):
        """Test verify_credential function."""
        # Setup mock
        mock_checkpw.return_value = True

        # Test with valid credentials
        result = verify_credential("password", "hashed_password")

        # Verify mock was called correctly
        mock_checkpw.assert_called_once_with(b"password", b"hashed_password")
        assert result

    @patch("bcrypt.checkpw")
    def test_verify_credential_bytes(self, mock_checkpw):
        """Test verify_credential with bytes hashed credential."""
        # Setup mock
        mock_checkpw.return_value = True

        # Test with valid credentials
        result = verify_credential("password", b"hashed_password")

        # Verify mock was called correctly
        mock_checkpw.assert_called_once_with(b"password", b"hashed_password")
        assert result

    def test_verify_credential_empty(self):
        """Test verify_credential with empty credentials."""
        assert not verify_credential("", "hashed_password")
        assert not verify_credential("password", "")
        assert not verify_credential("", "")

    @patch("bcrypt.checkpw")
    def test_verify_credential_exception(self, mock_checkpw):
        """Test verify_credential with exception."""
        # Setup mock to raise exception
        mock_checkpw.side_effect = Exception("Test error")

        # Test with exception
        result = verify_credential("password", "hashed_password")

        # Verify result
        assert not result

    def test_verify_credential_invalid_format(self):
        """Test verify_credential with invalid hashed credential format."""
        # Test with invalid format that raises UnicodeEncodeError
        with patch("users.auth.logger") as mock_logger:
            result = verify_credential("password", object())
            assert not result
            # Check that error was logged, but don't be strict about the exact message
            assert mock_logger.error.called

    def test_hash_auth_alias(self):
        """Test hash_auth alias."""
        # Direct test of the alias without mocking
        with patch("bcrypt.gensalt") as mock_gensalt:
            with patch("bcrypt.hashpw") as mock_hashpw:
                mock_salt = b"mock_salt"
                mock_gensalt.return_value = mock_salt
                mock_hashed = b"hashed_credential"
                mock_hashpw.return_value = mock_hashed

                # Test the alias directly
                result = hash_auth("password")
                assert result == "hashed_credential"

    def test_verify_auth_alias(self):
        """Test verify_auth alias."""
        # Direct test of the alias without mocking
        with patch("bcrypt.checkpw") as mock_checkpw:
            mock_checkpw.return_value = True

            # Test the alias directly
            result = verify_auth("password", "hashed_password")
            assert result
            mock_checkpw.assert_called_once_with(b"password", b"hashed_password")


if __name__ == "__main__":
    unittest.main()
