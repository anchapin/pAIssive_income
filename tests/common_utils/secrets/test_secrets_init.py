"""Tests for the secrets package __init__ module. Renamed to avoid conflicts."""

import logging
import os
from unittest.mock import patch

import pytest

from common_utils.secrets import (
    SecretsBackend,
    SecretsManager,
    delete_secret,
    get_secret,
    list_secrets,
    set_secret,
)


class TestSecretsInit:
    """Tests for the secrets __init__ module."""

    def test_imports(self):
        """Test that all expected symbols are imported."""
        assert SecretsBackend is not None
        assert SecretsManager is not None
        assert delete_secret is not None
        assert get_secret is not None
        assert list_secrets is not None
        assert set_secret is not None

    def test_get_secret_direct(self):
        """Test get_secret directly."""
        os.environ["TEST_KEY"] = "test_value"
        result = get_secret("TEST_KEY")
        assert result == "test_value"
        del os.environ["TEST_KEY"]

    def test_set_secret_direct(self):
        """Test set_secret directly."""
        result = set_secret("TEST_KEY", "test_value")
        assert result is True
        assert os.environ["TEST_KEY"] == "test_value"
        del os.environ["TEST_KEY"]

    def test_delete_secret_direct(self):
        """Test delete_secret directly."""
        os.environ["TEST_KEY"] = "test_value"
        result = delete_secret("TEST_KEY")
        assert result is True
        assert "TEST_KEY" not in os.environ

    def test_list_secrets_direct(self):
        """Test list_secrets directly."""
        os.environ["TEST_KEY"] = "test_value"
        result = list_secrets()

        # The key might be masked with a hash-based identifier
        # Look for any key that contains our test value
        found = False
        for key, value in result.items():
            if key == "TEST_KEY" or "SENSITIVE_KEY" in key:
                if value == "****" or value == "********":
                    found = True
                    break

        assert found, "TEST_KEY or masked version not found in secrets list"
        del os.environ["TEST_KEY"]
