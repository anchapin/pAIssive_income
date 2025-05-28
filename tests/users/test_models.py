"""Tests for the users.models module."""

import logging
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from users.models import User


class TestUser(unittest.TestCase):
    """Test cases for the User class."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User()
        self.user.id = 1
        self.user.username = "testuser"
        self.user.email = "test@example.com"
        self.user.password_hash = "hashed_password"
        self.user.created_at = datetime(2023, 1, 1, 12, 0, 0)
        self.user.updated_at = datetime(2023, 1, 2, 12, 0, 0)

    def test_to_dict(self):
        """Test to_dict method."""
        expected = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 2, 12, 0, 0),
        }
        self.assertEqual(self.user.to_dict(), expected)

    def test_tablename(self):
        """Test __tablename__ attribute."""
        self.assertEqual(User.__tablename__, "users")

    def test_columns(self):
        """Test column definitions."""
        self.assertTrue(hasattr(User, "id"))
        self.assertTrue(hasattr(User, "username"))
        self.assertTrue(hasattr(User, "email"))
        self.assertTrue(hasattr(User, "password_hash"))
        self.assertTrue(hasattr(User, "created_at"))
        self.assertTrue(hasattr(User, "updated_at"))


if __name__ == "__main__":
    unittest.main()
