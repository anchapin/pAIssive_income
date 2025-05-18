"""Tests for the config module."""

import logging
import os
import unittest
from unittest.mock import patch

from config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def test_default_database_url(self):
        """Test that the default database URL is set correctly."""
        # Test with no environment variable set
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            self.assertEqual(
                config.SQLALCHEMY_DATABASE_URI,
                "postgresql://myuser:mypassword@db:5432/mydb",
            )

    def test_custom_database_url(self):
        """Test that a custom database URL from environment is used."""
        # Test with environment variable set
        test_db_url = "postgresql://testuser:testpass@testhost:5432/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": test_db_url}, clear=True):
            config = Config()
            self.assertEqual(config.SQLALCHEMY_DATABASE_URI, test_db_url)

    def test_sqlalchemy_track_modifications(self):
        """Test that SQLALCHEMY_TRACK_MODIFICATIONS is set to False."""
        config = Config()
        self.assertFalse(Config.SQLALCHEMY_TRACK_MODIFICATIONS)


if __name__ == "__main__":
    unittest.main()
