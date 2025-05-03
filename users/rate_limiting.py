"""
Rate limiting functionality for the pAIssive_income project.

This module provides functions for rate limiting authentication attempts
and other security - sensitive operations.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Tuple

from flask import g, jsonify, request

# Configure logger
logger = logging.getLogger(__name__)

# In - memory storage for rate limiting
# In a production environment, this would be stored in a distributed cache like Redis
LOGIN_ATTEMPTS = defaultdict(list)  # username / ip -> list of timestamps
BLOCKED_IPS = {}  # ip -> unblock_time


def get_client_ip() -> str:
    """
    Get the client IP address from the request.

    Returns:
        Client IP address
    """
    # Check for X - Forwarded - For header (for clients behind proxies)
    if request.headers.get("X - Forwarded - For"):
        ip = request.headers.get("X - Forwarded - For").split(",")[0].strip()
    else:
        ip = request.remote_addr or "unknown"
    return ip


def is_ip_blocked(ip: str) -> bool:
    """
    Check if an IP address is currently blocked.

    Args:
        ip: IP address to check

    Returns:
        True if IP is blocked, False otherwise
    """
    # Check if IP is in blocked list
    if ip in BLOCKED_IPS:
        unblock_time = BLOCKED_IPS[ip]

        # Check if block has expired
        if datetime.utcnow() >= unblock_time:
            # Remove from blocked list
            del BLOCKED_IPS[ip]
            return False

        return True

    return False


def block_ip(ip: str, duration_minutes: int = 15) -> None:
    """
    Block an IP address for a specified duration.

    Args:
        ip: IP address to block
        duration_minutes: Duration to block the IP in minutes
    """
    unblock_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
    BLOCKED_IPS[ip] = unblock_time
    logger.warning(f"Blocked IP {ip} until {unblock_time}")


def record_login_attempt(identifier: str, success: bool) -> Tuple[bool, Optional[int]]:
    """
    Record a login attempt and check if rate limit is exceeded.

    Args:
        identifier: Username or IP address
        success: Whether the login attempt was successful

    Returns:
        Tuple of (is_rate_limited, remaining_attempts)
    """
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=15)

    # Remove attempts older than the window
    LOGIN_ATTEMPTS[identifier] = [
        timestamp for timestamp in LOGIN_ATTEMPTS[identifier] if timestamp > window_start
    ]

    # Add current attempt
    LOGIN_ATTEMPTS[identifier].append(now)

    # Count recent failed attempts
    recent_attempts = len(LOGIN_ATTEMPTS[identifier])

    # If successful login, clear the attempts
    if success:
        LOGIN_ATTEMPTS[identifier] = []
        return False, None

    # Check if rate limit is exceeded
    max_attempts = 5  # Maximum failed attempts in 15 minutes
    if recent_attempts >= max_attempts:
        # Rate limit exceeded
        remaining_attempts = 0
        return True, remaining_attempts

    # Not rate limited
    remaining_attempts = max_attempts - recent_attempts
    return False, remaining_attempts


def rate_limit_login(f):
    """
    Decorator to apply rate limiting to login routes.

    Args:
        f: Flask route function to wrap

    Returns:
        Wrapped function that enforces rate limiting
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP
        ip = get_client_ip()

        # Check if IP is blocked
        if is_ip_blocked(ip):
            logger.warning(f"Blocked IP attempted to access login: {ip}")
            return (
                jsonify(
                    {
                        "error": "Too Many Requests",
                        "message": "Too many failed login attempts. Please try again later.",
                            
                    }
                ),
                429,
            )

        # Get username from request
        data = request.json or {}
        username = data.get("username", "")

        # Create identifiers for rate limiting
        # We track both by username and IP to prevent username enumeration
        username_identifier = f"username:{username}"
        ip_identifier = f"ip:{ip}"

        # Check rate limits
        username_limited, username_remaining = record_login_attempt(username_identifier, 
            False)
        ip_limited, ip_remaining = record_login_attempt(ip_identifier, False)

        if username_limited or ip_limited:
            # If either limit is exceeded, block the IP
            block_ip(ip)

            logger.warning(f"Rate limit exceeded for login: {username} from {ip}")
            return (
                jsonify(
                    {
                        "error": "Too Many Requests",
                        "message": "Too many failed login attempts. Please try again later.",
                            
                    }
                ),
                429,
            )

        # Store identifiers in Flask's g object for the route handler
        g.rate_limit_identifiers = {
            "username": username_identifier,
            "ip": ip_identifier,
        }

        # Continue to the route handler
        return f(*args, **kwargs)

    return decorated_function


def cleanup_rate_limiting_data() -> Tuple[int, int]:
    """
    Clean up expired rate limiting data.

    Returns:
        Tuple of (removed_attempts, removed_blocks)
    """
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=15)

    # Clean up login attempts
    removed_attempts = 0
    for identifier in list(LOGIN_ATTEMPTS.keys()):
        # Remove attempts older than the window
        original_count = len(LOGIN_ATTEMPTS[identifier])
        LOGIN_ATTEMPTS[identifier] = [
            timestamp for timestamp in LOGIN_ATTEMPTS[identifier] if timestamp > window_start
        ]

        # If no attempts remain, remove the identifier
        if not LOGIN_ATTEMPTS[identifier]:
            del LOGIN_ATTEMPTS[identifier]

        removed_attempts += original_count - len(LOGIN_ATTEMPTS.get(identifier, []))

    # Clean up blocked IPs
    blocked_ips = list(BLOCKED_IPS.keys())
    removed_blocks = 0

    for ip in blocked_ips:
        unblock_time = BLOCKED_IPS[ip]
        if now >= unblock_time:
            del BLOCKED_IPS[ip]
            removed_blocks += 1

    logger.info(
        f"Cleaned up rate limiting data: {removed_attempts} attempts, 
            {removed_blocks} blocks"
    )
    return removed_attempts, removed_blocks
