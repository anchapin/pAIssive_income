"""Integration tests for the secrets CLI module."""

import logging
import os
import tempfile
import unittest
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from common_utils.secrets.cli import (
    ADMIN_TOKEN_DIR,
    ADMIN_TOKEN_FILE,
    LOCKOUT_DURATION,
    MAX_FAILED_ATTEMPTS,
    _check_auth,
    _check_rate_limit,
    _handle_list_due,
    _handle_rotate_all,
    _handle_rotate_secret,
    _handle_schedule_rotation,
    _handle_unknown_rotation_command,
    _validate_secret_value,
    failed_attempts,
    get_secret_value,
    handle_audit,
    handle_delete,
    handle_get,
    handle_list,
    handle_rotation,
    handle_set,
    lockout_times,
    main,
    parse_args,
    require_auth,
)


class TestCliIntegration(unittest.TestCase):
    """Integration test cases for the CLI module."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset failed attempts and lockout times before each test
        failed_attempts.clear()
        lockout_times.clear()

    def test_handle_rotation_schedule(self):
        """Test handle_rotation with schedule command."""
        # Arrange
        args = MagicMock()
        args.backend = "env"
        args.rotation_command = "schedule"
        args.key = "test_key"
        args.interval = 30

        # Act
        with patch("common_utils.secrets.cli._check_auth", return_value=True), \
             patch("common_utils.secrets.cli.SecretRotation") as mock_rotation_class, \
             patch("common_utils.secrets.cli._handle_schedule_rotation") as mock_handle_schedule:
            mock_rotation = MagicMock()
            mock_rotation_class.return_value = mock_rotation

            handle_rotation(args)

        # Assert
        mock_rotation_class.assert_called_once_with(secrets_backend=args.backend)
        mock_handle_schedule.assert_called_once_with(mock_rotation, args, "test_key")

    def test_handle_rotation_rotate(self):
        """Test handle_rotation with rotate command."""
        # Arrange
        args = MagicMock()
        args.backend = "env"
        args.rotation_command = "rotate"
        args.key = "test_key"

        # Act
        with patch("common_utils.secrets.cli._check_auth", return_value=True), \
             patch("common_utils.secrets.cli.SecretRotation") as mock_rotation_class, \
             patch("common_utils.secrets.cli._handle_rotate_secret") as mock_handle_rotate:
            mock_rotation = MagicMock()
            mock_rotation_class.return_value = mock_rotation

            handle_rotation(args)

        # Assert
        mock_rotation_class.assert_called_once_with(secrets_backend=args.backend)
        mock_handle_rotate.assert_called_once_with(mock_rotation, args, "test_key")

    def test_handle_rotation_rotate_all(self):
        """Test handle_rotation with rotate-all command."""
        # Arrange
        args = MagicMock()
        args.backend = "env"
        args.rotation_command = "rotate-all"

        # Act
        with patch("common_utils.secrets.cli._check_auth", return_value=True), \
             patch("common_utils.secrets.cli.SecretRotation") as mock_rotation_class, \
             patch("common_utils.secrets.cli._handle_rotate_all") as mock_handle_rotate_all:
            mock_rotation = MagicMock()
            mock_rotation_class.return_value = mock_rotation

            handle_rotation(args)

        # Assert
        mock_rotation_class.assert_called_once_with(secrets_backend=args.backend)
        mock_handle_rotate_all.assert_called_once_with(mock_rotation)

    def test_handle_rotation_list_due(self):
        """Test handle_rotation with list-due command."""
        # Arrange
        args = MagicMock()
        args.backend = "env"
        args.rotation_command = "list-due"

        # Act
        with patch("common_utils.secrets.cli._check_auth", return_value=True), \
             patch("common_utils.secrets.cli.SecretRotation") as mock_rotation_class, \
             patch("common_utils.secrets.cli._handle_list_due") as mock_handle_list_due:
            mock_rotation = MagicMock()
            mock_rotation_class.return_value = mock_rotation

            handle_rotation(args)

        # Assert
        mock_rotation_class.assert_called_once_with(secrets_backend=args.backend)
        mock_handle_list_due.assert_called_once_with(mock_rotation)

    def test_handle_rotation_unknown_command(self):
        """Test handle_rotation with unknown command."""
        # Arrange
        args = MagicMock()
        args.backend = "env"
        args.rotation_command = "unknown"

        # Act
        with patch("common_utils.secrets.cli._check_auth", return_value=True), \
             patch("common_utils.secrets.cli.SecretRotation") as mock_rotation_class, \
             patch("common_utils.secrets.cli._handle_unknown_rotation_command") as mock_handle_unknown:
            mock_rotation = MagicMock()
            mock_rotation_class.return_value = mock_rotation

            handle_rotation(args)

        # Assert
        mock_rotation_class.assert_called_once_with(secrets_backend=args.backend)
        mock_handle_unknown.assert_called_once_with("unknown")
