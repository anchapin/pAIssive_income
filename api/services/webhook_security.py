"""webhook_security - Module for api/services.webhook_security."""

# Standard library imports
import base64
import hashlib
import hmac
import ipaddress

# Third-party imports
# Local imports
from common_utils.logging import get_logger

logger = get_logger(__name__)


class WebhookSignatureVerifier:
    """Utility for creating and verifying webhook signatures."""

    def create_signature(self, payload: str, secret: str) -> str:
        """
        Create a signature for a webhook payload.

        Args:
            payload: The webhook payload as a string
            secret: The webhook secret

        Returns:
            Base64-encoded HMAC-SHA256 signature

        """
        # Create an HMAC with the secret and payload
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()

        # Return base64 encoded signature
        return base64.b64encode(signature).decode()

    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """
        Verify a webhook signature.

        Args:
            payload: The webhook payload as a string
            signature: The signature to verify
            secret: The webhook secret

        Returns:
            True if the signature is valid, False otherwise

        """
        try:
            # Calculate the expected signature
            expected_signature = self.create_signature(payload, secret)

            # Compare signatures using constant-time comparison
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            logger.exception("Signature verification failed")
            return False


class WebhookIPAllowlist:
    """Utility for managing IP allowlists for webhooks."""

    def __init__(self, db=None):
        """
        Initialize the IP allowlist.

        Args:
            db: Database connection object. If None, a default connection will be used.

        """
        self.db = db

    def add_ip(self, webhook_id: str, ip: str) -> bool:
        """
        Add an IP address to the allowlist.

        Args:
            webhook_id: The ID of the webhook
            ip: The IP address to add

        Returns:
            True if added successfully, False otherwise

        """
        if self.db:
            return self.db.add_ip_to_allowlist(webhook_id, ip)
        return False

    def add_network(self, webhook_id: str, network: str) -> bool:
        """
        Add a network (CIDR notation) to the allowlist.

        Args:
            webhook_id: The ID of the webhook
            network: The network in CIDR notation (e.g., "192.168.1.0/24")

        Returns:
            True if added successfully, False otherwise

        """
        try:
            # Validate the network
            ipaddress.ip_network(network)

            # Add to the allowlist
            if self.db:
                return self.db.add_ip_to_allowlist(webhook_id, network)
            return False
        except ValueError:
            logger.exception("Invalid network format")
            return False

    def remove_ip(self, webhook_id: str, ip: str) -> bool:
        """
        Remove an IP address from the allowlist.

        Args:
            webhook_id: The ID of the webhook
            ip: The IP address to remove

        Returns:
            True if removed successfully, False otherwise

        """
        if self.db:
            return self.db.remove_ip_from_allowlist(webhook_id, ip)
        return False

    def remove_network(self, webhook_id: str, network: str) -> bool:
        """
        Remove a network from the allowlist.

        Args:
            webhook_id: The ID of the webhook
            network: The network to remove

        Returns:
            True if removed successfully, False otherwise

        """
        if self.db:
            return self.db.remove_ip_from_allowlist(webhook_id, network)
        return False

    def is_allowed(self, webhook_id: str, ip: str) -> bool:
        """
        Check if an IP address is allowed.

        Args:
            webhook_id: The ID of the webhook
            ip: The IP address to check

        Returns:
            True if the IP is allowed, False otherwise

        """
        if not self.db:
            return True  # If no DB, allow all

        # Get the allowlist for this webhook
        allowlist = self.db.get_ip_allowlist(webhook_id)

        # If the allowlist is empty, allow all
        if not allowlist:
            return True

        # Check if the IP is in the allowlist
        if ip in allowlist:
            return True

        # Check if the IP is in any of the networks in the allowlist
        try:
            ip_obj = ipaddress.ip_address(ip)
            for item in allowlist:
                try:
                    # Check if the item is a network
                    if "/" in item:
                        network = ipaddress.ip_network(item)
                        if ip_obj in network:
                            return True
                except ValueError:
                    continue
        except ValueError:
            logger.exception("Invalid IP address format")
            return False

        return False
