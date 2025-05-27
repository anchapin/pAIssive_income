"""Tests for the webhook security service."""

import logging
import unittest
from unittest.mock import MagicMock, patch
import base64
import hashlib
import hmac
import ipaddress

import pytest

from api.services.webhook_security import WebhookSignatureVerifier, WebhookIPAllowlist


class TestWebhookSignatureVerifier:
    """Test suite for WebhookSignatureVerifier."""

    def setup_method(self):
        """Set up test fixtures."""
        self.verifier = WebhookSignatureVerifier()
        self.payload = '{"event": "test", "data": {"id": 123}}'
        self.secret = "whsec_test_secret"

    def test_create_signature(self):
        """Test creating a webhook signature."""
        # Act
        signature = self.verifier.create_signature(self.payload, self.secret)

        # Assert
        assert isinstance(signature, str)
        assert len(signature) > 0

        # Verify the signature manually
        expected_signature = base64.b64encode(
            hmac.new(
                self.secret.encode(),
                self.payload.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        assert signature == expected_signature

    def test_verify_signature_valid(self):
        """Test verifying a valid signature."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.secret)

        # Act
        result = self.verifier.verify_signature(self.payload, signature, self.secret)

        # Assert
        assert result is True

    def test_verify_signature_invalid(self):
        """Test verifying an invalid signature."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.secret)
        tampered_payload = self.payload.replace("123", "456")

        # Act
        result = self.verifier.verify_signature(tampered_payload, signature, self.secret)

        # Assert
        assert result is False

    def test_verify_signature_exception(self):
        """Test signature verification with an exception."""
        # Arrange
        with patch.object(self.verifier, 'create_signature', side_effect=Exception("Test error")):
            # Act
            result = self.verifier.verify_signature(self.payload, "invalid-signature", self.secret)

            # Assert
            assert result is False


class TestWebhookIPAllowlist:
    """Test suite for WebhookIPAllowlist."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.allowlist = WebhookIPAllowlist(db=self.mock_db)
        self.webhook_id = "webhook-123"
        self.ip = "192.168.1.1"
        self.network = "192.168.1.0/24"

    def test_add_ip(self):
        """Test adding an IP to the allowlist."""
        # Arrange
        self.mock_db.add_ip_to_allowlist.return_value = True

        # Act
        result = self.allowlist.add_ip(self.webhook_id, self.ip)

        # Assert
        assert result is True
        self.mock_db.add_ip_to_allowlist.assert_called_once_with(self.webhook_id, self.ip)

    def test_add_network_valid(self):
        """Test adding a valid network to the allowlist."""
        # Arrange
        self.mock_db.add_ip_to_allowlist.return_value = True

        # Act
        result = self.allowlist.add_network(self.webhook_id, self.network)

        # Assert
        assert result is True
        self.mock_db.add_ip_to_allowlist.assert_called_once_with(self.webhook_id, self.network)

    def test_add_network_invalid(self):
        """Test adding an invalid network to the allowlist."""
        # Act
        result = self.allowlist.add_network(self.webhook_id, "invalid-network")

        # Assert
        assert result is False
        self.mock_db.add_ip_to_allowlist.assert_not_called()

    def test_remove_ip(self):
        """Test removing an IP from the allowlist."""
        # Arrange
        self.mock_db.remove_ip_from_allowlist.return_value = True

        # Act
        result = self.allowlist.remove_ip(self.webhook_id, self.ip)

        # Assert
        assert result is True
        self.mock_db.remove_ip_from_allowlist.assert_called_once_with(self.webhook_id, self.ip)

    def test_remove_network(self):
        """Test removing a network from the allowlist."""
        # Arrange
        self.mock_db.remove_ip_from_allowlist.return_value = True

        # Act
        result = self.allowlist.remove_network(self.webhook_id, self.network)

        # Assert
        assert result is True
        self.mock_db.remove_ip_from_allowlist.assert_called_once_with(self.webhook_id, self.network)

    def test_is_allowed_direct_match(self):
        """Test IP check with direct match."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.ip]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert result is True

    def test_is_allowed_network_match(self):
        """Test IP check with network match."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.network]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, "192.168.1.100")

        # Assert
        assert result is True

    def test_is_allowed_no_match(self):
        """Test IP check with no match."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.ip, self.network]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, "10.0.0.1")

        # Assert
        assert result is False

    def test_is_allowed_empty_allowlist(self):
        """Test IP check with empty allowlist."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = []

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert result is True

    def test_is_allowed_without_db(self):
        """Test IP check without a database connection."""
        # Arrange
        allowlist_without_db = WebhookIPAllowlist(db=None)

        # Act
        result = allowlist_without_db.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert result is True

    def test_is_allowed_invalid_ip(self):
        """Test IP check with invalid IP address."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.network]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, "invalid-ip")

        # Assert
        assert result is False
