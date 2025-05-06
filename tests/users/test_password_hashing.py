"""test_password_hashing - Module for tests/users.test_password_hashing."""

# Standard library imports
import unittest

# Third-party imports
# Local imports
from users.auth import hash_password, verify_password


class TestPasswordHashing(unittest.TestCase):
    """Test cases for password hashing functions."""

    def test_hash_password(self):
        """Test that hash_password returns a bcrypt hash."""
        password = "test_password"
        hashed = hash_password(password)

        # Check that the hash is a bytes object
        self.assertIsInstance(hashed, bytes)

        # Check that the hash starts with the bcrypt identifier
        self.assertTrue(hashed.startswith(b"$2b$"))

        # Check that the hash is not the same as the original password
        self.assertNotEqual(hashed, password.encode("utf-8"))

    def test_verify_password_success(self):
        """Test that verify_password returns True for a correct password."""
        password = "test_password"
        hashed = hash_password(password)

        # Verify the password
        self.assertTrue(verify_password(password, hashed))

    def test_verify_password_failure(self):
        """Test that verify_password returns False for an incorrect password."""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        # Verify the wrong password
        self.assertFalse(verify_password(wrong_password, hashed))

    def test_verify_password_empty(self):
        """Test that verify_password returns False for empty inputs."""
        # Empty password
        hashed = hash_password("test_password")
        self.assertFalse(verify_password("", hashed))

        # Empty hash
        self.assertFalse(verify_password("test_password", b""))

        # Both empty
        self.assertFalse(verify_password("", b""))

    def test_hash_password_empty(self):
        """Test that hash_password raises ValueError for empty password."""
        with self.assertRaises(ValueError):
            hash_password("")

    def test_bcrypt_rounds(self):
        """Test that the bcrypt hash uses the correct number of rounds."""
        password = "test_password"
        hashed = hash_password(password)

        # Extract the number of rounds from the hash
        # The format is $2b$XX$ where XX is the number of rounds
        rounds = int(hashed[4:6])

        # Check that the number of rounds is 12 (default in our implementation)
        self.assertEqual(rounds, 12)

    def test_different_hashes(self):
        """Test that hashing the same password twice produces different hashes."""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Check that the hashes are different (due to different salts)
        self.assertNotEqual(hash1, hash2)

        # But both should verify correctly
        self.assertTrue(verify_password(password, hash1))
        self.assertTrue(verify_password(password, hash2))


if __name__ == "__main__":
    unittest.main()
