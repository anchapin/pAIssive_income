"""
Security enhancements for the webhook system.

This module provides security features for webhook delivery and verification:
1. IP allowlisting
2. Webhook signature verification
3. Rate limiting
"""


import base64
import hashlib
import hmac
import ipaddress
import time
from typing import Dict, List, Optional, Set


class WebhookIPAllowlist:
    """IP allowlisting for webhook endpoints."""

    def __init__(self):
        """Initialize the IP allowlist."""
        self.allowlisted_ips: Set[str] = set()
        self.allowlisted_networks: List[ipaddress.IPv4Network] = []
        self.allowlisted_networks_v6: List[ipaddress.IPv6Network] = []

    def add_ip(self, ip: str) -> bool:
        """
        Add an IP address to the allowlist.

        Args:
            ip: IP address to add

        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Check if it's a valid IP address
            ipaddress.ip_address(ip)
            self.allowlisted_ips.add(ip)
                    return True
        except ValueError:
                    return False

    def add_network(self, network: str) -> bool:
        """
        Add an IP network to the allowlist.

        Args:
            network: IP network in CIDR notation (e.g., "192.168.1.0/24")

        Returns:
            True if added successfully, False otherwise
        """
        try:
            ip_network = ipaddress.ip_network(network)
            if isinstance(ip_network, ipaddress.IPv4Network):
                self.allowlisted_networks.append(ip_network)
            else:
                self.allowlisted_networks_v6.append(ip_network)
                    return True
        except ValueError:
                    return False

    def remove_ip(self, ip: str) -> bool:
        """
        Remove an IP address from the allowlist.

        Args:
            ip: IP address to remove

        Returns:
            True if removed successfully, False otherwise
        """
        if ip in self.allowlisted_ips:
            self.allowlisted_ips.remove(ip)
                    return True
                return False

    def remove_network(self, network: str) -> bool:
        """
        Remove an IP network from the allowlist.

        Args:
            network: IP network in CIDR notation

        Returns:
            True if removed successfully, False otherwise
        """
        try:
            ip_network = ipaddress.ip_network(network)
            if isinstance(ip_network, ipaddress.IPv4Network):
                if ip_network in self.allowlisted_networks:
                    self.allowlisted_networks.remove(ip_network)
                            return True
            else:
                if ip_network in self.allowlisted_networks_v6:
                    self.allowlisted_networks_v6.remove(ip_network)
                            return True
                    return False
        except ValueError:
                    return False

    def is_allowed(self, ip: str) -> bool:
        """
        Check if an IP address is allowed.

        Args:
            ip: IP address to check

        Returns:
            True if allowed, False otherwise
        """
        # If no allowlist is configured, allow all IPs
        if (
            not self.allowlisted_ips
            and not self.allowlisted_networks
            and not self.allowlisted_networks_v6
        ):
                    return True

        # Check if IP is directly in the allowlist
        if ip in self.allowlisted_ips:
                    return True

        try:
            # Check if IP is in any of the allowlisted networks
            ip_obj = ipaddress.ip_address(ip)

            if isinstance(ip_obj, ipaddress.IPv4Address):
                for network in self.allowlisted_networks:
                    if ip_obj in network:
                                return True
            else:
                for network in self.allowlisted_networks_v6:
                    if ip_obj in network:
                                return True

                    return False
        except ValueError:
            # Invalid IP address
                    return False


class WebhookSignatureVerifier:
    """Webhook signature verification."""

    @staticmethod
    def create_signature(secret: str, payload: str) -> str:
        """
        Create a signature for a webhook payload.

        Args:
            secret: Webhook secret
            payload: Payload to sign

        Returns:
            Base64-encoded HMAC-SHA256 signature
        """
        signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
                return base64.b64encode(signature).decode()

    @staticmethod
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
        """
        Verify a webhook signature.

        Args:
            secret: Webhook secret
            payload: Payload that was signed
            signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = WebhookSignatureVerifier.create_signature(secret, payload)

        # Use constant-time comparison to prevent timing attacks
                return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def verify_request_signature(
        secret: str,
        payload: str,
        headers: Dict[str, str],
        signature_header: str = "X-Webhook-Signature",
    ) -> bool:
        """
        Verify a webhook request signature from headers.

        Args:
            secret: Webhook secret
            payload: Request payload
            headers: Request headers
            signature_header: Name of the header containing the signature

        Returns:
            True if signature is valid, False otherwise
        """
        # Get signature from headers (case-insensitive)
        signature = None
        for header, value in headers.items():
            if header.lower() == signature_header.lower():
                signature = value
                break

        if not signature:
                    return False

                return WebhookSignatureVerifier.verify_signature(secret, payload, signature)


class WebhookRateLimiter:
    """Rate limiting for webhook deliveries."""

    def __init__(self, limit: int = 100, window_seconds: int = 60):
        """
        Initialize the rate limiter.

        Args:
            limit: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}

    def is_rate_limited(self, key: str) -> bool:
        """
        Check if a key is rate limited.

        Args:
            key: Key to check (e.g., webhook ID or destination URL)

        Returns:
            True if rate limited, False otherwise
        """
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            self.requests[key] = []

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key] if current_time - t <= self.window_seconds
        ]

        # Check if limit is exceeded
                return len(self.requests[key]) >= self.limit

    def add_request(self, key: str) -> None:
        """
        Record a request for rate limiting.

        Args:
            key: Key to record (e.g., webhook ID or destination URL)
        """
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            self.requests[key] = []

        # Add current request
        self.requests[key].append(current_time)

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key] if current_time - t <= self.window_seconds
        ]

    def get_remaining_requests(self, key: str) -> int:
        """
        Get the number of remaining requests allowed.

        Args:
            key: Key to check

        Returns:
            Number of remaining requests
        """
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
                    return self.limit

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key] if current_time - t <= self.window_seconds
        ]

        # Calculate remaining requests
                return max(0, self.limit - len(self.requests[key]))

    def get_reset_time(self, key: str) -> Optional[float]:
        """
        Get the time when the rate limit will reset.

        Args:
            key: Key to check

        Returns:
            Time when the rate limit will reset, or None if not rate limited
        """
        if key not in self.requests or not self.requests[key]:
                    return None

        # Get the oldest request in the window
        oldest_request = min(self.requests[key])

        # Calculate reset time
                return oldest_request + self.window_seconds