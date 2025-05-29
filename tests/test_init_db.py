"""Tests for init_db.py."""

import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from init_db import generate_secure_password, init_db


class TestInitDb:
    """Test suite for init_db.py."""

    def test_generate_secure_password(self):
        """Test generate_secure_password function."""
        # Test with default length
        password = generate_secure_password()
        assert len(password) == 16

        # Test with custom length
        password = generate_secure_password(length=10)
        assert len(password) == 10

        # Test that the password contains characters from all required sets
        password = generate_secure_password(length=100)  # Long password to ensure all character types
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        assert has_lowercase and has_uppercase and has_digit and has_special

    @patch("init_db.create_app")
    @patch("init_db.User")
    @patch("init_db.Team")
    @patch("init_db.Agent")
    @patch("init_db.hash_credential")
    @patch("init_db.logger.info")  # Changed from logging.info to logger.info
    @patch("init_db.db")
    def test_init_db_with_existing_admin(self, mock_db, mock_logging, mock_hash, mock_agent,
                                         mock_team, mock_user, mock_create_app):
        """Test init_db function when admin user already exists."""
        # Mock app and db
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Set up app_context to properly handle context manager
        mock_context = MagicMock()
        mock_app.app_context.return_value = mock_context

        # Mock User.query to return an existing admin
        mock_user_instance = MagicMock()
        mock_user.query.filter_by.return_value.first.return_value = mock_user_instance

        # Call the function
        init_db()

        # Verify that no new user was created
        mock_user.assert_not_called()
        mock_team.assert_not_called()
        mock_agent.assert_not_called()
        mock_hash.assert_not_called()
        mock_logging.assert_called_with("Database already initialized")

    @patch("init_db.create_app")
    @patch("init_db.User")
    @patch("init_db.Team")
    @patch("init_db.Agent")
    @patch("init_db.db")
    @patch("init_db.hash_credential")
    @patch("init_db.logger.info")  # Changed from logging.info to logger.info
    @patch.dict(os.environ, {"ADMIN_INITIAL_PASSWORD": "test-password"})
    def test_init_db_with_env_password(self, mock_logging, mock_hash, mock_db,
                                      mock_agent, mock_team, mock_user, mock_create_app):
        """Test init_db function with password from environment variable."""
        # Mock app
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Set up app_context to properly handle context manager
        mock_context = MagicMock()
        mock_app.app_context.return_value = mock_context

        # Mock User.query to return no existing admin
        mock_user.query.filter_by.return_value.first.return_value = None

        # Mock hash_credential
        mock_hash.return_value = "hashed-password"

        # Call the function
        init_db()

        # Verify that a new user was created with the password from env var
        mock_user.assert_called_once()
        mock_hash.assert_called_once_with("test-password")
        mock_team.assert_called_once()
        assert mock_agent.call_count == 3
        mock_db.session.add.assert_called()
        mock_db.session.add_all.assert_called_once()
        mock_db.session.commit.assert_called_once()
        # Check for the expected log messages
        expected_log_calls = [
            "Admin user created",
            "Default team created",
            "Sample agents created",
            "Database initialized successfully",
            "Admin user created with generated password (not logged for security reasons)"
        ]

        for expected_call in expected_log_calls:
            mock_logging.assert_any_call(expected_call)

    @patch("init_db.create_app")
    @patch("init_db.User")
    @patch("init_db.Team")
    @patch("init_db.Agent")
    @patch("init_db.db")
    @patch("init_db.hash_credential")
    @patch("init_db.generate_secure_password")
    @patch("init_db.logger.info")  # Changed from logging.info to logger.info
    @patch("os.isatty")
    @patch.dict(os.environ, {}, clear=True)
    def test_init_db_with_generated_password(self, mock_isatty, mock_logging, mock_gen_pwd,
                                           mock_hash, mock_db, mock_agent, mock_team,
                                           mock_user, mock_create_app):
        """Test init_db function with generated password."""
        # Mock app
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Set up app_context to properly handle context manager
        mock_context = MagicMock()
        mock_app.app_context.return_value = mock_context

        # Mock User.query to return no existing admin
        mock_user.query.filter_by.return_value.first.return_value = None

        # Mock generate_secure_password and hash_credential
        mock_gen_pwd.return_value = "generated-password"
        mock_hash.return_value = "hashed-password"

        # Mock os.isatty to return True (interactive session)
        mock_isatty.return_value = True

        # Call the function
        init_db()

        # Verify that a new user was created with a generated password
        mock_user.assert_called_once()
        mock_gen_pwd.assert_called_once()
        mock_hash.assert_called_once_with("generated-password")
        mock_team.assert_called_once()
        assert mock_agent.call_count == 3
        mock_db.session.add.assert_called()
        mock_db.session.add_all.assert_called_once()
        mock_db.session.commit.assert_called_once()

        # Check for the expected log messages
        expected_log_calls = [
            "Admin user created",
            "Default team created",
            "Sample agents created",
            "Database initialized successfully",
            "Admin user created with generated password (not logged for security reasons)"
        ]

        for expected_call in expected_log_calls:
            mock_logging.assert_any_call(expected_call)
