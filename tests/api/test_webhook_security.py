"""test_webhook_security - Module for tests/api.test_webhook_security."""

# Standard library imports
import hmac
import hashlib
import base64
import unittest
from unittest.mock import MagicMock, patch
import ipaddress

# Third-party imports
import pytest

# Local imports
from api.services.webhook_security import WebhookSignatureVerifier, WebhookIPAllowlist


class TestWebhookSignatureVerifier(unittest.TestCase):
    """Test suite for the WebhookSignatureVerifier class."""

    def setUp(self):
        """Set up test fixtures."""
        self.verifier = WebhookSignatureVerifier()
        self.webhook_secret = "whsec_test_secret"
        self.payload = '{"event":"test","data":{"id":"123"}}'

    def test_create_signature(self):
        """Test creating a webhook signature."""
        # Act
        signature = self.verifier.create_signature(self.payload, self.webhook_secret)

        # Assert
        # Manually calculate the expected signature
        expected_signature = base64.b64encode(
            hmac.new(
                self.webhook_secret.encode(),
                self.payload.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        self.assertEqual(signature, expected_signature)

    def test_verify_signature_valid(self):
        """Test verifying a valid webhook signature."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.webhook_secret)

        # Act
        result = self.verifier.verify_signature(self.payload, signature, self.webhook_secret)

        # Assert
        self.assertTrue(result)

    def test_verify_signature_invalid(self):
        """Test verifying an invalid webhook signature."""
        # Arrange
        invalid_signature = "invalid_signature"

        # Act
        result = self.verifier.verify_signature(self.payload, invalid_signature, self.webhook_secret)

        # Assert
        self.assertFalse(result)

    def test_verify_signature_tampered_payload(self):
        """Test verifying a signature with a tampered payload."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.webhook_secret)
        tampered_payload = '{"event":"test","data":{"id":"456"}}'

        # Act
        result = self.verifier.verify_signature(tampered_payload, signature, self.webhook_secret)

        # Assert
        self.assertFalse(result)


class TestWebhookIPAllowlist(unittest.TestCase):
    """Test suite for the WebhookIPAllowlist class."""

    def setUp(self):
        """Set up test fixtures."""
        self.allowlist = WebhookIPAllowlist()
        self.db = MagicMock()
        self.allowlist.db = self.db
        self.webhook_id = "webhook-123"

    def test_add_ip(self):
        """Test adding an IP to the allowlist."""
        # Arrange
        ip = "192.168.1.1"
        self.db.add_ip_to_allowlist.return_value = True

        # Act
        result = self.allowlist.add_ip(self.webhook_id, ip)

        # Assert
        self.assertTrue(result)
        self.db.add_ip_to_allowlist.assert_called_once_with(self.webhook_id, ip)

    def test_add_network(self):
        """Test adding a network to the allowlist."""
        # Arrange
        network = "192.168.1.0/24"
        self.db.add_ip_to_allowlist.return_value = True

        # Act
        result = self.allowlist.add_network(self.webhook_id, network)

        # Assert
        self.assertTrue(result)
        self.db.add_ip_to_allowlist.assert_called_once_with(self.webhook_id, network)

    def test_remove_ip(self):
        """Test removing an IP from the allowlist."""
        # Arrange
        ip = "192.168.1.1"
        self.db.remove_ip_from_allowlist.return_value = True

        # Act
        result = self.allowlist.remove_ip(self.webhook_id, ip)

        # Assert
        self.assertTrue(result)
        self.db.remove_ip_from_allowlist.assert_called_once_with(self.webhook_id, ip)

    def test_remove_network(self):
        """Test removing a network from the allowlist."""
        # Arrange
        network = "192.168.1.0/24"
        self.db.remove_ip_from_allowlist.return_value = True

        # Act
        result = self.allowlist.remove_network(self.webhook_id, network)

        # Assert
        self.assertTrue(result)
        self.db.remove_ip_from_allowlist.assert_called_once_with(self.webhook_id, network)

    def test_is_allowed_single_ip(self):
        """Test checking if a single IP is allowed."""
        # Arrange
        ip = "192.168.1.1"
        self.db.get_ip_allowlist.return_value = ["192.168.1.1"]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, ip)

        # Assert
        self.assertTrue(result)
        self.db.get_ip_allowlist.assert_called_once_with(self.webhook_id)

    def test_is_allowed_network(self):
        """Test checking if an IP in a network is allowed."""
        # Arrange
        ip = "192.168.1.5"
        self.db.get_ip_allowlist.return_value = ["192.168.1.0/24"]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, ip)

        # Assert
        self.assertTrue(result)
        self.db.get_ip_allowlist.assert_called_once_with(self.webhook_id)

    def test_is_allowed_not_in_list(self):
        """Test checking if an IP not in the allowlist is allowed."""
        # Arrange
        ip = "192.168.2.1"
        self.db.get_ip_allowlist.return_value = ["192.168.1.0/24", "10.0.0.1"]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, ip)

        # Assert
        self.assertFalse(result)
        self.db.get_ip_allowlist.assert_called_once_with(self.webhook_id)

    def test_is_allowed_empty_allowlist(self):
        """Test checking if any IP is allowed when the allowlist is empty."""
        # Arrange
        ip = "192.168.1.1"
        self.db.get_ip_allowlist.return_value = []

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, ip)

        # Assert
        self.assertTrue(result)  # Empty allowlist should allow all IPs
        self.db.get_ip_allowlist.assert_called_once_with(self.webhook_id)
