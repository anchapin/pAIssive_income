"""Tests for the fixes in common_utils/secrets/secrets_manager.py."""

import unittest
from unittest.mock import patch, MagicMock

import pytest

from common_utils.secrets.secrets_manager import SecretsManager


class TestSecretsManagerFixes(unittest.TestCase):
    """Test cases for the fixes in secrets_manager.py."""

    def test_sanitize_secrets_dict_not_duplicated(self):
        """Test that _sanitize_secrets_dict is not duplicated in the SecretsManager class."""
        # Get all methods in the SecretsManager class
        methods = [method for method in dir(SecretsManager) if callable(getattr(SecretsManager, method))]
        
        # Count occurrences of _sanitize_secrets_dict
        sanitize_method_count = methods.count('_sanitize_secrets_dict')
        
        # There should be exactly one implementation of _sanitize_secrets_dict
        assert sanitize_method_count == 1, f"Expected 1 implementation of _sanitize_secrets_dict, found {sanitize_method_count}"

    def test_sanitize_secrets_dict_functionality(self):
        """Test that the _sanitize_secrets_dict method correctly masks sensitive values."""
        # Create a SecretsManager instance
        manager = SecretsManager()
        
        # Test with a dictionary containing sensitive keys
        test_secrets = {
            "api_key": "sensitive-api-key-12345",
            "password": "sensitive-password-67890",
            "token": "sensitive-token-abcdef",
            "normal_key": "normal-value-12345",
            "nested": {
                "secret": "nested-secret-value",
                "normal": "nested-normal-value"
            }
        }
        
        # Sanitize the secrets
        sanitized = manager._sanitize_secrets_dict(test_secrets)
        
        # Check that sensitive values are masked
        assert sanitized["api_key"] == "********"
        assert sanitized["password"] == "********"
        assert sanitized["token"] == "********"
        
        # Check that non-sensitive values are not masked
        assert sanitized["normal_key"] != "********"
        
        # Check that nested dictionaries are also sanitized
        assert isinstance(sanitized["nested"], dict)
        assert sanitized["nested"]["secret"] == "********"
        assert sanitized["nested"]["normal"] != "********"

    def test_list_backend_secrets_uses_sanitize(self):
        """Test that _list_backend_secrets uses _sanitize_secrets_dict."""
        # Create a SecretsManager instance
        manager = SecretsManager()
        
        # Create a mock for _sanitize_secrets_dict
        original_sanitize = manager._sanitize_secrets_dict
        manager._sanitize_secrets_dict = MagicMock(return_value={"masked": "value"})
        
        # Create mocks for the backend classes
        with patch('common_utils.secrets.secrets_manager.FileBackend') as mock_file_backend:
            # Set up the mock to return a dictionary of secrets
            mock_backend_instance = MagicMock()
            mock_backend_instance.list_secrets.return_value = {"secret": "value"}
            mock_file_backend.return_value = mock_backend_instance
            
            # Call _list_backend_secrets
            from common_utils.secrets.secrets_manager import SecretsBackend
            result = manager._list_backend_secrets(SecretsBackend.FILE)
            
            # Verify that _sanitize_secrets_dict was called with the correct arguments
            manager._sanitize_secrets_dict.assert_called_once_with({"secret": "value"})
            
            # Verify that the result is the sanitized dictionary
            assert result == {"masked": "value"}
        
        # Restore the original method
        manager._sanitize_secrets_dict = original_sanitize

    def test_list_secrets_uses_list_backend_secrets(self):
        """Test that list_secrets uses _list_backend_secrets for non-ENV backends."""
        # Create a SecretsManager instance
        manager = SecretsManager()
        
        # Create a mock for _list_backend_secrets
        manager._list_backend_secrets = MagicMock(return_value={"masked": "value"})
        
        # Call list_secrets with a non-ENV backend
        from common_utils.secrets.secrets_manager import SecretsBackend
        result = manager.list_secrets(SecretsBackend.FILE)
        
        # Verify that _list_backend_secrets was called with the correct arguments
        manager._list_backend_secrets.assert_called_once_with(SecretsBackend.FILE)
        
        # Verify that the result is the value returned by _list_backend_secrets
        assert result == {"masked": "value"}


if __name__ == "__main__":
    unittest.main()
