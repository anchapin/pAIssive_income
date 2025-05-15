"""test_webhook_security - Module for tests/api.test_webhook_security."""

# Standard library imports
import unittest
from unittest.mock import MagicMock, patch
from ipaddress import AddressValueError

# Local imports
from api.services.webhook_security import WebhookSignatureVerifier, WebhookIPAllowlist

class TestWebhookSignatureVerifier(unittest.TestCase):
    """Test suite for WebhookSignatureVerifier."""

    def setUp(self):
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

    def test_verify_signature_valid(self):
        """Test verifying a valid signature."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.secret)

        # Act
        result = self.verifier.verify_signature(self.payload, signature, self.secret)

        # Assert
        assert result

    def test_verify_signature_invalid(self):
        """Test verifying an invalid signature."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.secret)
        wrong_signature = signature[:-1] + ("1" if signature[-1] == "0" else "0")

        # Act
        result = self.verifier.verify_signature(self.payload, wrong_signature, self.secret)

        # Assert
        assert not result

    def test_verify_signature_different_payload(self):
        """Test verifying a signature with a different payload."""
        # Arrange
        signature = self.verifier.create_signature(self.payload, self.secret)
        different_payload = '{"event": "different", "data": {"id": 456}}'

        # Act
        result = self.verifier.verify_signature(different_payload, signature, self.secret)

        # Assert
        assert not result

    def test_verify_signature_exception(self):
        """Test signature verification with invalid input causing exception."""
        # Act
        result = self.verifier.verify_signature(self.payload, None, self.secret)

        # Assert
        assert not result

    def test_verify_signature_encoding_error(self):
        """Test signature verification with encoding error."""
        # Act
        result = self.verifier.verify_signature(self.payload, "invalid-base64!", self.secret)

        # Assert
        assert not result

    @patch("hmac.new")
    def test_verify_signature_hmac_error(self, mock_hmac_new):
        """Test signature verification with HMAC error."""
        # Arrange
        mock_hmac_new.side_effect = Exception("HMAC error")

        # Act
        result = self.verifier.verify_signature(self.payload, "signature", self.secret)

        # Assert
        assert not result
        mock_hmac_new.assert_called_once()

    @patch("base64.b64encode")
    def test_verify_signature_base64_error(self, mock_b64encode):
        """Test signature verification with base64 encoding error."""
        # Arrange
        mock_b64encode.side_effect = Exception("Base64 encoding error")

        # Act
        result = self.verifier.verify_signature(self.payload, "signature", self.secret)

        # Assert
        assert not result

class TestWebhookIPAllowlist(unittest.TestCase):
    """Test suite for WebhookIPAllowlist."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.allowlist = WebhookIPAllowlist(self.mock_db)
        self.webhook_id = "webhook-123"
        self.ip = "192.168.1.1"
        self.network = "192.168.1.0/24"

    def test_add_ip(self):
        """Test adding an IP address."""
        # Arrange
        self.mock_db.add_ip_to_allowlist.return_value = True

        # Act
        result = self.allowlist.add_ip(self.webhook_id, self.ip)

        # Assert
        assert result
        self.mock_db.add_ip_to_allowlist.assert_called_once_with(self.webhook_id, self.ip)

    def test_add_ip_without_db(self):
        """Test adding an IP without a database connection."""
        # Arrange
        allowlist = WebhookIPAllowlist(db=None)

        # Act
        result = allowlist.add_ip(self.webhook_id, self.ip)

        # Assert
        assert not result

    def test_add_network_valid(self):
        """Test adding a valid network."""
        # Arrange
        self.mock_db.add_ip_to_allowlist.return_value = True

        # Act
        result = self.allowlist.add_network(self.webhook_id, self.network)

        # Assert
        assert result
        self.mock_db.add_ip_to_allowlist.assert_called_once_with(self.webhook_id, self.network)

    def test_add_network_invalid(self):
        """Test adding an invalid network."""
        # Act
        result = self.allowlist.add_network(self.webhook_id, "invalid_network")

        # Assert
        assert not result
        self.mock_db.add_ip_to_allowlist.assert_not_called()

    def test_add_network_validation_error(self):
        """Test adding a network with validation error."""
        # Act
        with patch('ipaddress.ip_network', side_effect=AddressValueError):
            result = self.allowlist.add_network(self.webhook_id, "192.168.1.256/24")

        # Assert
        assert not result
        self.mock_db.add_ip_to_allowlist.assert_not_called()

    def test_remove_ip(self):
        """Test removing an IP address."""
        # Arrange
        self.mock_db.remove_ip_from_allowlist.return_value = True

        # Act
        result = self.allowlist.remove_ip(self.webhook_id, self.ip)

        # Assert
        assert result
        self.mock_db.remove_ip_from_allowlist.assert_called_once_with(self.webhook_id, self.ip)

    def test_remove_ip_without_db(self):
        """Test removing an IP without database."""
        # Create a new instance with no db
        allowlist = WebhookIPAllowlist(db=None)

        # Act
        result = allowlist.remove_ip(self.webhook_id, self.ip)

        # Assert
        assert not result

    def test_remove_network(self):
        """Test removing a network."""
        # Arrange
        self.mock_db.remove_ip_from_allowlist.return_value = True

        # Act
        result = self.allowlist.remove_network(self.webhook_id, self.network)

        # Assert
        assert result
        self.mock_db.remove_ip_from_allowlist.assert_called_once_with(self.webhook_id, self.network)

    def test_is_allowed_empty_allowlist(self):
        """Test IP check with empty allowlist."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = []

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert result
        self.mock_db.get_ip_allowlist.assert_called_once_with(self.webhook_id)

    def test_is_allowed_ip_match(self):
        """Test IP check with direct IP match."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.ip]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert result

    def test_is_allowed_network_match(self):
        """Test IP check with network match."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.network]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, "192.168.1.100")

        # Assert
        assert result

    def test_is_allowed_no_match(self):
        """Test IP check with no match."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.network]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, "10.0.0.1")

        # Assert
        assert not result

    def test_is_allowed_without_db(self):
        """Test IP check without a database connection."""
        # Arrange
        allowlist_without_db = WebhookIPAllowlist(db=None)

        # Act
        result = allowlist_without_db.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert result

    def test_is_allowed_invalid_ip(self):
        """Test IP check with invalid IP address."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = [self.network]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, "invalid-ip")

        # Assert
        assert not result

    def test_is_allowed_invalid_network(self):
        """Test IP check with invalid network in allowlist."""
        # Arrange
        self.mock_db.get_ip_allowlist.return_value = ["invalid/network"]

        # Act
        result = self.allowlist.is_allowed(self.webhook_id, self.ip)

        # Assert
        assert not result
