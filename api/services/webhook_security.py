"""
"""
Security enhancements for the webhook system.
Security enhancements for the webhook system.


This module provides security features for webhook delivery and verification:
    This module provides security features for webhook delivery and verification:
    1. IP allowlisting
    1. IP allowlisting
    2. Webhook signature verification
    2. Webhook signature verification
    3. Rate limiting
    3. Rate limiting
    """
    """




    import base64
    import base64
    import hashlib
    import hashlib
    import hmac
    import hmac
    import ipaddress
    import ipaddress
    import time
    import time
    from typing import Dict, List, Optional, Set
    from typing import Dict, List, Optional, Set




    class WebhookIPAllowlist:
    class WebhookIPAllowlist:
    """IP allowlisting for webhook endpoints."""

    def __init__(self):
    """Initialize the IP allowlist."""
    self.allowlisted_ips: Set[str] = set()
    self.allowlisted_networks: List[ipaddress.IPv4Network] = []
    self.allowlisted_networks_v6: List[ipaddress.IPv6Network] = []

    def add_ip(self, ip: str) -> bool:
    """
    """
    Add an IP address to the allowlist.
    Add an IP address to the allowlist.


    Args:
    Args:
    ip: IP address to add
    ip: IP address to add


    Returns:
    Returns:
    True if added successfully, False otherwise
    True if added successfully, False otherwise
    """
    """
    try:
    try:
    # Check if it's a valid IP address
    # Check if it's a valid IP address
    ipaddress.ip_address(ip)
    ipaddress.ip_address(ip)
    self.allowlisted_ips.add(ip)
    self.allowlisted_ips.add(ip)
    return True
    return True
except ValueError:
except ValueError:
    return False
    return False


    def add_network(self, network: str) -> bool:
    def add_network(self, network: str) -> bool:
    """
    """
    Add an IP network to the allowlist.
    Add an IP network to the allowlist.


    Args:
    Args:
    network: IP network in CIDR notation (e.g., "192.168.1.0/24")
    network: IP network in CIDR notation (e.g., "192.168.1.0/24")


    Returns:
    Returns:
    True if added successfully, False otherwise
    True if added successfully, False otherwise
    """
    """
    try:
    try:
    ip_network = ipaddress.ip_network(network)
    ip_network = ipaddress.ip_network(network)
    if isinstance(ip_network, ipaddress.IPv4Network):
    if isinstance(ip_network, ipaddress.IPv4Network):
    self.allowlisted_networks.append(ip_network)
    self.allowlisted_networks.append(ip_network)
    else:
    else:
    self.allowlisted_networks_v6.append(ip_network)
    self.allowlisted_networks_v6.append(ip_network)
    return True
    return True
except ValueError:
except ValueError:
    return False
    return False


    def remove_ip(self, ip: str) -> bool:
    def remove_ip(self, ip: str) -> bool:
    """
    """
    Remove an IP address from the allowlist.
    Remove an IP address from the allowlist.


    Args:
    Args:
    ip: IP address to remove
    ip: IP address to remove


    Returns:
    Returns:
    True if removed successfully, False otherwise
    True if removed successfully, False otherwise
    """
    """
    if ip in self.allowlisted_ips:
    if ip in self.allowlisted_ips:
    self.allowlisted_ips.remove(ip)
    self.allowlisted_ips.remove(ip)
    return True
    return True
    return False
    return False


    def remove_network(self, network: str) -> bool:
    def remove_network(self, network: str) -> bool:
    """
    """
    Remove an IP network from the allowlist.
    Remove an IP network from the allowlist.


    Args:
    Args:
    network: IP network in CIDR notation
    network: IP network in CIDR notation


    Returns:
    Returns:
    True if removed successfully, False otherwise
    True if removed successfully, False otherwise
    """
    """
    try:
    try:
    ip_network = ipaddress.ip_network(network)
    ip_network = ipaddress.ip_network(network)
    if isinstance(ip_network, ipaddress.IPv4Network):
    if isinstance(ip_network, ipaddress.IPv4Network):
    if ip_network in self.allowlisted_networks:
    if ip_network in self.allowlisted_networks:
    self.allowlisted_networks.remove(ip_network)
    self.allowlisted_networks.remove(ip_network)
    return True
    return True
    else:
    else:
    if ip_network in self.allowlisted_networks_v6:
    if ip_network in self.allowlisted_networks_v6:
    self.allowlisted_networks_v6.remove(ip_network)
    self.allowlisted_networks_v6.remove(ip_network)
    return True
    return True
    return False
    return False
except ValueError:
except ValueError:
    return False
    return False


    def is_allowed(self, ip: str) -> bool:
    def is_allowed(self, ip: str) -> bool:
    """
    """
    Check if an IP address is allowed.
    Check if an IP address is allowed.


    Args:
    Args:
    ip: IP address to check
    ip: IP address to check


    Returns:
    Returns:
    True if allowed, False otherwise
    True if allowed, False otherwise
    """
    """
    # If no allowlist is configured, allow all IPs
    # If no allowlist is configured, allow all IPs
    if (
    if (
    not self.allowlisted_ips
    not self.allowlisted_ips
    and not self.allowlisted_networks
    and not self.allowlisted_networks
    and not self.allowlisted_networks_v6
    and not self.allowlisted_networks_v6
    ):
    ):
    return True
    return True


    # Check if IP is directly in the allowlist
    # Check if IP is directly in the allowlist
    if ip in self.allowlisted_ips:
    if ip in self.allowlisted_ips:
    return True
    return True


    try:
    try:
    # Check if IP is in any of the allowlisted networks
    # Check if IP is in any of the allowlisted networks
    ip_obj = ipaddress.ip_address(ip)
    ip_obj = ipaddress.ip_address(ip)


    if isinstance(ip_obj, ipaddress.IPv4Address):
    if isinstance(ip_obj, ipaddress.IPv4Address):
    for network in self.allowlisted_networks:
    for network in self.allowlisted_networks:
    if ip_obj in network:
    if ip_obj in network:
    return True
    return True
    else:
    else:
    for network in self.allowlisted_networks_v6:
    for network in self.allowlisted_networks_v6:
    if ip_obj in network:
    if ip_obj in network:
    return True
    return True


    return False
    return False
except ValueError:
except ValueError:
    # Invalid IP address
    # Invalid IP address
    return False
    return False




    class WebhookSignatureVerifier:
    class WebhookSignatureVerifier:
    """Webhook signature verification."""

    @staticmethod
    def create_signature(secret: str, payload: str) -> str:
    """
    """
    Create a signature for a webhook payload.
    Create a signature for a webhook payload.


    Args:
    Args:
    secret: Webhook secret
    secret: Webhook secret
    payload: Payload to sign
    payload: Payload to sign


    Returns:
    Returns:
    Base64-encoded HMAC-SHA256 signature
    Base64-encoded HMAC-SHA256 signature
    """
    """
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()
    return base64.b64encode(signature).decode()


    @staticmethod
    @staticmethod
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
    """
    """
    Verify a webhook signature.
    Verify a webhook signature.


    Args:
    Args:
    secret: Webhook secret
    secret: Webhook secret
    payload: Payload that was signed
    payload: Payload that was signed
    signature: Signature to verify
    signature: Signature to verify


    Returns:
    Returns:
    True if signature is valid, False otherwise
    True if signature is valid, False otherwise
    """
    """
    expected_signature = WebhookSignatureVerifier.create_signature(secret, payload)
    expected_signature = WebhookSignatureVerifier.create_signature(secret, payload)


    # Use constant-time comparison to prevent timing attacks
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)
    return hmac.compare_digest(expected_signature, signature)


    @staticmethod
    @staticmethod
    def verify_request_signature(
    def verify_request_signature(
    secret: str,
    secret: str,
    payload: str,
    payload: str,
    headers: Dict[str, str],
    headers: Dict[str, str],
    signature_header: str = "X-Webhook-Signature",
    signature_header: str = "X-Webhook-Signature",
    ) -> bool:
    ) -> bool:
    """
    """
    Verify a webhook request signature from headers.
    Verify a webhook request signature from headers.


    Args:
    Args:
    secret: Webhook secret
    secret: Webhook secret
    payload: Request payload
    payload: Request payload
    headers: Request headers
    headers: Request headers
    signature_header: Name of the header containing the signature
    signature_header: Name of the header containing the signature


    Returns:
    Returns:
    True if signature is valid, False otherwise
    True if signature is valid, False otherwise
    """
    """
    # Get signature from headers (case-insensitive)
    # Get signature from headers (case-insensitive)
    signature = None
    signature = None
    for header, value in headers.items():
    for header, value in headers.items():
    if header.lower() == signature_header.lower():
    if header.lower() == signature_header.lower():
    signature = value
    signature = value
    break
    break


    if not signature:
    if not signature:
    return False
    return False


    return WebhookSignatureVerifier.verify_signature(secret, payload, signature)
    return WebhookSignatureVerifier.verify_signature(secret, payload, signature)




    class WebhookRateLimiter:
    class WebhookRateLimiter:
    """Rate limiting for webhook deliveries."""

    def __init__(self, limit: int = 100, window_seconds: int = 60):
    """
    """
    Initialize the rate limiter.
    Initialize the rate limiter.


    Args:
    Args:
    limit: Maximum number of requests allowed in the time window
    limit: Maximum number of requests allowed in the time window
    window_seconds: Time window in seconds
    window_seconds: Time window in seconds
    """
    """
    self.limit = limit
    self.limit = limit
    self.window_seconds = window_seconds
    self.window_seconds = window_seconds
    self.requests: Dict[str, List[float]] = {}
    self.requests: Dict[str, List[float]] = {}


    def is_rate_limited(self, key: str) -> bool:
    def is_rate_limited(self, key: str) -> bool:
    """
    """
    Check if a key is rate limited.
    Check if a key is rate limited.


    Args:
    Args:
    key: Key to check (e.g., webhook ID or destination URL)
    key: Key to check (e.g., webhook ID or destination URL)


    Returns:
    Returns:
    True if rate limited, False otherwise
    True if rate limited, False otherwise
    """
    """
    current_time = time.time()
    current_time = time.time()


    # Initialize if key doesn't exist
    # Initialize if key doesn't exist
    if key not in self.requests:
    if key not in self.requests:
    self.requests[key] = []
    self.requests[key] = []


    # Remove requests outside the time window
    # Remove requests outside the time window
    self.requests[key] = [
    self.requests[key] = [
    t for t in self.requests[key] if current_time - t <= self.window_seconds
    t for t in self.requests[key] if current_time - t <= self.window_seconds
    ]
    ]


    # Check if limit is exceeded
    # Check if limit is exceeded
    return len(self.requests[key]) >= self.limit
    return len(self.requests[key]) >= self.limit


    def add_request(self, key: str) -> None:
    def add_request(self, key: str) -> None:
    """
    """
    Record a request for rate limiting.
    Record a request for rate limiting.


    Args:
    Args:
    key: Key to record (e.g., webhook ID or destination URL)
    key: Key to record (e.g., webhook ID or destination URL)
    """
    """
    current_time = time.time()
    current_time = time.time()


    # Initialize if key doesn't exist
    # Initialize if key doesn't exist
    if key not in self.requests:
    if key not in self.requests:
    self.requests[key] = []
    self.requests[key] = []


    # Add current request
    # Add current request
    self.requests[key].append(current_time)
    self.requests[key].append(current_time)


    # Remove requests outside the time window
    # Remove requests outside the time window
    self.requests[key] = [
    self.requests[key] = [
    t for t in self.requests[key] if current_time - t <= self.window_seconds
    t for t in self.requests[key] if current_time - t <= self.window_seconds
    ]
    ]


    def get_remaining_requests(self, key: str) -> int:
    def get_remaining_requests(self, key: str) -> int:
    """
    """
    Get the number of remaining requests allowed.
    Get the number of remaining requests allowed.


    Args:
    Args:
    key: Key to check
    key: Key to check


    Returns:
    Returns:
    Number of remaining requests
    Number of remaining requests
    """
    """
    current_time = time.time()
    current_time = time.time()


    # Initialize if key doesn't exist
    # Initialize if key doesn't exist
    if key not in self.requests:
    if key not in self.requests:
    return self.limit
    return self.limit


    # Remove requests outside the time window
    # Remove requests outside the time window
    self.requests[key] = [
    self.requests[key] = [
    t for t in self.requests[key] if current_time - t <= self.window_seconds
    t for t in self.requests[key] if current_time - t <= self.window_seconds
    ]
    ]


    # Calculate remaining requests
    # Calculate remaining requests
    return max(0, self.limit - len(self.requests[key]))
    return max(0, self.limit - len(self.requests[key]))


    def get_reset_time(self, key: str) -> Optional[float]:
    def get_reset_time(self, key: str) -> Optional[float]:
    """
    """
    Get the time when the rate limit will reset.
    Get the time when the rate limit will reset.


    Args:
    Args:
    key: Key to check
    key: Key to check


    Returns:
    Returns:
    Time when the rate limit will reset, or None if not rate limited
    Time when the rate limit will reset, or None if not rate limited
    """
    """
    if key not in self.requests or not self.requests[key]:
    if key not in self.requests or not self.requests[key]:
    return None
    return None


    # Get the oldest request in the window
    # Get the oldest request in the window
    oldest_request = min(self.requests[key])
    oldest_request = min(self.requests[key])


    # Calculate reset time
    # Calculate reset time
    return oldest_request + self.window_seconds
    return oldest_request + self.window_seconds