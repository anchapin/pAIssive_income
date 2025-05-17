"""Tests for the users.models module."""

import logging
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from users.models import UserModel


class TestUserModel(unittest.TestCase):
    """Test cases for the UserModel class."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserModel()
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
        self.assertEqual(UserModel.__tablename__, "users")

    def test_columns(self):
        """Test column definitions."""
        self.assertTrue(hasattr(UserModel, "id"))
        self.assertTrue(hasattr(UserModel, "username"))
        self.assertTrue(hasattr(UserModel, "email"))
        self.assertTrue(hasattr(UserModel, "password_hash"))
        self.assertTrue(hasattr(UserModel, "created_at"))
        self.assertTrue(hasattr(UserModel, "updated_at"))


if __name__ == "__main__":
    unittest.main()
