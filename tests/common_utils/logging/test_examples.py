"""Tests for common_utils.logging.examples module."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.examples import (
    example_mask_sensitive_data,
    example_secure_logger,
)


class TestExamples:
    """Test suite for examples module."""

    @patch("common_utils.logging.examples.get_secure_logger")
    def test_example_secure_logger(self, mock_get_secure_logger):
        """Test example_secure_logger function."""
        # Create a mock logger
        mock_logger = MagicMock()
        mock_get_secure_logger.return_value = mock_logger

        # Call the function
        example_secure_logger()

        # Verify that the logger was created and used
        mock_get_secure_logger.assert_called_once_with("example")

        # Verify that the logger's info method was called with the expected messages
        assert mock_logger.info.call_count == 3

        # Check that the first call contains the access token
        first_call_args = mock_logger.info.call_args_list[0][0]
        assert first_call_args[0] == "Using access token: %s"
        assert first_call_args[1] == "DEMO_TOKEN_PLACEHOLDER"

        # Check that the second call contains the auth material
        second_call_args = mock_logger.info.call_args_list[1][0]
        assert second_call_args[0] == "Authentication material: %s"
        assert second_call_args[1] == "DEMO_AUTH_PLACEHOLDER"

        # Check that the third call contains the user data
        third_call_args = mock_logger.info.call_args_list[2][0]
        assert third_call_args[0] == "User data: %s"
        # Check that the user_data dictionary is passed as expected
        user_data = third_call_args[1]
        assert user_data["username"] == "john_doe"
        assert user_data["email"] == "john@example.com"
        assert user_data["auth_material"] == "DEMO_AUTH_PLACEHOLDER"
        assert user_data["secure_data"]["service_1"] == "DEMO_TOKEN_PLACEHOLDER"
        assert user_data["secure_data"]["service_2"] == "EXAMPLE_AUTH_PLACEHOLDER_NOT_REAL"

    @patch("common_utils.logging.examples.mask_sensitive_data")
    @patch("common_utils.logging.examples.logging.getLogger")
    def test_example_mask_sensitive_data(self, mock_get_logger, mock_mask_sensitive_data):
        """Test example_mask_sensitive_data function."""
        # Create a mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Mock the mask_sensitive_data function
        mock_mask_sensitive_data.side_effect = lambda x: f"MASKED: {x}" if isinstance(x, str) else {"masked": True}

        # Call the function
        example_mask_sensitive_data()

        # Verify that the logger was created and used
        mock_get_logger.assert_called_once_with("standard_logger")

        # Verify that mask_sensitive_data was called
        assert mock_mask_sensitive_data.call_count == 2

        # Check that the first call contains the access token
        first_call_args = mock_mask_sensitive_data.call_args_list[0][0][0]
        assert "Using access token:" in first_call_args
        assert "DEMO_TOKEN_PLACEHOLDER" in first_call_args

        # Check that the second call contains the config dictionary
        second_call_args = mock_mask_sensitive_data.call_args_list[1][0][0]
        assert isinstance(second_call_args, dict)
        assert "access_token" in second_call_args
        assert second_call_args["access_token"] == "DEMO_TOKEN_PLACEHOLDER"
        assert "endpoint" in second_call_args
        assert "timeout" in second_call_args

        # Verify that the logger's info method was called with the masked values
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call("%s", "MASKED: Using access token: DEMO_TOKEN_PLACEHOLDER")
        mock_logger.info.assert_any_call("Configuration: %s", {"masked": True})

    @patch("common_utils.logging.examples.logging.basicConfig")
    def test_module_logging_setup(self, mock_logging_basicConfig):
        """Test that logging is set up correctly in the module."""
        # Re-import the module to trigger the logging setup
        import importlib

        import common_utils.logging.examples
        importlib.reload(common_utils.logging.examples)

        # Verify that logging.basicConfig was called with the correct arguments
        mock_logging_basicConfig.assert_called_once_with(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
