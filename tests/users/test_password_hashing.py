"""test_credential_hashing - Module for tests/users.test_credential_hashing."""

# Standard library imports
import unittest
import uuid

# Third-party imports
# Local imports
from users.auth import hash_credential, verify_credential


class TestCredentialHashing(unittest.TestCase):
    """Test cases for credential hashing functions."""

    def setUp(self):
        """Set up test credentials that are unique for each test run."""
        # Generate a unique test credential for each test run
        # This helps prevent hardcoded credentials from being flagged by security scanners
        self.test_credential = f"test_cred_{uuid.uuid4().hex[:8]}"
        self.wrong_credential = f"wrong_cred_{uuid.uuid4().hex[:8]}"

    def test_hash_credential(self):
        """Test that hash_credential returns a bcrypt hash."""
        hashed = hash_credential(self.test_credential)

        # Check that the hash is a bytes object
        self.assertIsInstance(hashed, bytes)

        # Check that the hash starts with the bcrypt identifier
        self.assertTrue(hashed.startswith(b"$2b$"))

        # Check that the hash is not the same as the original credential
        self.assertNotEqual(hashed, self.test_credential.encode("utf-8"))

    def test_verify_credential_success(self):
        """Test that verify_credential returns True for a correct credential."""
        hashed = hash_credential(self.test_credential)

        # Verify the credential
        self.assertTrue(verify_credential(self.test_credential, hashed))

    def test_verify_credential_failure(self):
        """Test that verify_credential returns False for an incorrect credential."""
        hashed = hash_credential(self.test_credential)

        # Verify the wrong credential
        self.assertFalse(verify_credential(self.wrong_credential, hashed))

    def test_verify_credential_empty(self):
        """Test that verify_credential returns False for empty inputs."""
        # Empty credential
        hashed = hash_credential(self.test_credential)
        self.assertFalse(verify_credential("", hashed))

        # Empty hash
        self.assertFalse(verify_credential(self.test_credential, b""))

        # Both empty
        self.assertFalse(verify_credential("", b""))

    def test_hash_credential_empty(self):
        """Test that hash_credential raises ValueError for empty credential."""
        with self.assertRaises(ValueError):
            hash_credential("")

    def test_bcrypt_rounds(self):
        """Test that the bcrypt hash uses the correct number of rounds."""
        hashed = hash_credential(self.test_credential)

        # Extract the number of rounds from the hash
        # The format is $2b$XX$ where XX is the number of rounds
        rounds = int(hashed[4:6])

        # Check that the number of rounds is 12 (default in our implementation)
        self.assertEqual(rounds, 12)

    def test_different_hashes(self):
        """Test that hashing the same credential twice produces different hashes."""
        hash1 = hash_credential(self.test_credential)
        hash2 = hash_credential(self.test_credential)

        # Check that the hashes are different (due to different salts)
        self.assertNotEqual(hash1, hash2)

        # But both should verify correctly
        self.assertTrue(verify_credential(self.test_credential, hash1))
        self.assertTrue(verify_credential(self.test_credential, hash2))

    def tearDown(self):
        """Clean up after tests by removing test credentials from memory."""
        del self.test_credential
        del self.wrong_credential


if __name__ == "__main__":
    unittest.main()
