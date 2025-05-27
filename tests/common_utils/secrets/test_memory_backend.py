"""Tests for the memory backend module."""

import logging
from unittest.mock import patch

import pytest

from common_utils.secrets.memory_backend import MemoryBackend


class TestMemoryBackend:
    """Tests for the MemoryBackend class."""

    def test_init(self):
        """Test initializing the memory backend."""
        backend = MemoryBackend()
        assert backend.secrets == {}

    def test_get_secret_not_implemented(self):
        """Test that get_secret raises NotImplementedError."""
        backend = MemoryBackend()
        with pytest.raises(NotImplementedError):
            backend.get_secret()

    def test_set_secret_not_implemented(self):
        """Test that set_secret raises NotImplementedError."""
        backend = MemoryBackend()
        with pytest.raises(NotImplementedError):
            backend.set_secret()

    def test_delete_secret_not_implemented(self):
        """Test that delete_secret raises NotImplementedError."""
        backend = MemoryBackend()
        with pytest.raises(NotImplementedError):
            backend.delete_secret()

    def test_list_secrets_not_implemented(self):
        """Test that list_secrets raises NotImplementedError."""
        backend = MemoryBackend()
        with pytest.raises(NotImplementedError):
            backend.list_secrets()
