"""
Flask blueprint for authentication endpoints.

Provides password reset and token management functionality with security measures.
"""

from __future__ import annotations

import logging
import os
import re
import secrets
import smtplib
import time
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from typing import TYPE_CHECKING, Annotated, Optional, TypeVar, Union, cast

import bcrypt
from flask import Blueprint, Response, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

if TYPE_CHECKING:
    from flask import Flask

# Error messages
INVALID_EMAIL_ERROR = "Invalid email address"
DATABASE_URL_ERROR = "DATABASE_URL environment variable must be set in production"

# Constants
RESET_TOKEN_EXPIRY = 1800  # 30 minutes
MAX_IPV4_VALUE = 255  # Maximum value for an IPv4 octet

# Custom types for clarity
Email = Annotated[str, "Email"]
Token = Annotated[str, "Token"]
LoggableData = TypeVar("LoggableData", str, int, float, bool, None)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# Flask-Limiter instance (for demo; in prod, usually set up in main app)
class NoopLimiter(Limiter):
    """Limiter subclass that does nothing on init_app."""

    def init_app(self, _: Flask) -> None:
        """No-op initialization for blueprint usage."""


limiter = NoopLimiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    headers_enabled=True,
    strategy="fixed-window",
)

# In-memory user "database" for demonstration (replace with real user DB)
# Note: In production, use a proper database with secure password storage
USERS: dict[str, dict[str, Union[str, int]]] = {
    "e2euser@example.com": {
        "password": bcrypt.hashpw(b"oldpassword", bcrypt.gensalt()).decode(),
        "id": 1,
    }
}


# SQLAlchemy setup for tokens (using SQLite for demo)
# In production, use a proper database with secure connection
class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


db_url = os.environ.get("RESET_TOKEN_DB_URL", "sqlite:///reset_tokens.db")
# Use parameterized connection string to avoid SQL injection
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)


class PasswordResetToken(Base):
    """
    Database model for password reset tokens.

    Stores the token, associated email, and expiration time.
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, index=True, nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, email: str, token: str, expires_at: datetime) -> None:
        """
        Initialize a password reset token.

        Args:
            email: The user's email address
            token: The reset token
            expires_at: When the token expires

        """
        self.email = email
        self.token = token
        self.expires_at = expires_at


Base.metadata.create_all(bind=engine)

# Set up a dedicated logger for the auth module
logger = logging.getLogger(__name__)


def sanitize_email_content(content: str) -> str:
    """
    Sanitize email content to prevent injection attacks.

    Args:
        content: The content to sanitize

    Returns:
        str: The sanitized content

    """
    # Remove potential email injection characters
    content = re.sub(r"[\r\n]+", " ", content)
    # Basic HTML escaping
    content = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def send_email(to_addr: str, subject: str, body: str) -> None:
    """
    Send an email with security measures.

    Args:
        to_addr: The recipient email address
        subject: The email subject
        body: The email body

    Raises:
        ValueError: If the email address is invalid
        SMTPException: If there is an error sending the email

    """  # Validate email format
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", to_addr):
        raise ValueError(INVALID_EMAIL_ERROR)

    # Sanitize inputs
    subject = sanitize_email_content(subject)
    body = sanitize_email_content(body)

    # Create message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.environ.get("SMTP_FROM", "noreply@example.com")
    msg["To"] = to_addr

    # Get SMTP settings from environment with defaults
    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")

    # Send email with proper error handling
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_user and smtp_pass:
                server.starttls()
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError):
        logger.exception("Failed to send email")
        raise


def sanitize_log_data(data: LoggableData) -> str:
    """
    Sanitize data for logging to prevent log injection.

    Args:
        data: The data to sanitize

    Returns:
        str: The sanitized string

    """
    if data is None:
        return "<none>"
    if isinstance(data, str):
        # Remove any non-printable characters including newlines, carriage returns, tabs
        # Replace any remaining potentially problematic characters with safe alternatives
        return (
            "".join(ch for ch in data if ch.isprintable())
            .replace("%", "%%")  # Escape % to prevent format string issues
            .replace("{", "{{")
            .replace("}", "}}")
        )  # Escape curly braces for format strings
    return str(data).replace("%", "%%")


def validate_ipv4(ip_str: str) -> bool:
    """Validate an IPv4 address."""
    ipv4_segments = 4
    try:
        parts = [int(part) for part in ip_str.split(".")]
        return len(parts) == ipv4_segments and all(
            0 <= part <= MAX_IPV4_VALUE for part in parts
        )
    except (ValueError, AttributeError):
        return False


def validate_ipv6(ip_str: str) -> bool:
    """Validate an IPv6 address."""
    try:  # Remove IPv6 zone index if present
        if "%" in ip_str:
            ip_str = ip_str.split("%")[0]
        parts = ip_str.split(":")

        max_ipv6_segments = 8
        if len(parts) > max_ipv6_segments:
            return False

        # Handle :: compression
        if "" in parts:
            # More than one :: is invalid
            if parts.count("") > 1:
                return False
            # :: can only be at start or end
            if "" in parts[1:-1]:
                return False  # Validate each hextet
        max_hextet_length = 4
        return all(
            len(part) <= max_hextet_length
            and all(c in "0123456789abcdefABCDEF" for c in part)
            for part in parts
            if part
        )
    except (ValueError, AttributeError):
        return False


def validate_ip_address(ip_str: Optional[str]) -> bool:
    """
    Validate an IP address string.

    Args:
        ip_str: The IP address string to validate

    Returns:
        bool: True if the IP address is valid, False otherwise

    """
    if not ip_str:
        return False

    # IPv4 validation
    if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", ip_str):
        return validate_ipv4(ip_str)

    # IPv6 validation
    if ":" in ip_str:
        return validate_ipv6(ip_str)

    return False


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per minute")
def forgot_password() -> tuple[Response, int]:
    """
    Handle forgot password requests with proper security measures.

    Returns:
        tuple: A tuple containing (response, status_code)

    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower() if data.get("email") else ""

    # Get client IP with fallback and validation
    remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if remote_ip and "," in remote_ip:
        remote_ip = remote_ip.split(",")[0].strip()

    # Validate IP address
    if not validate_ip_address(remote_ip):
        remote_ip = "<invalid-ip>"

    # Sanitize data for logging
    safe_ip = sanitize_log_data(cast("str", remote_ip))
    safe_email = sanitize_log_data(cast("str", email))

    # Audit log every request
    logger.info(
        "[AUDIT][%s] Password reset requested for %s from %s",
        datetime.now(timezone.utc).isoformat(),
        safe_email or "<empty>",
        safe_ip,
    )

    # Input validation with timing attack protection
    if not email:
        time.sleep(secrets.randbelow(100) / 1000)  # Random delay 0-100ms
        response = jsonify(
            {"message": "If the email is registered, a reset link will be sent."}
        )
        return add_security_headers(response), 200

    # Validate email format
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        time.sleep(secrets.randbelow(100) / 1000)  # Random delay 0-100ms
        response = jsonify(
            {"message": "If the email is registered, a reset link will be sent."}
        )
        return add_security_headers(response), 200

    # If user exists, create a token and send an email
    if email in USERS:
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=30
        )  # 30 minute expiry

        # Store token in DB with proper session handling
        session = SessionLocal()
        try:
            # Delete any existing tokens for this email
            session.query(PasswordResetToken).filter_by(email=email).delete()

            # Add new token
            session.add(
                PasswordResetToken(email=email, token=token, expires_at=expires_at)
            )
            session.commit()

            # Log token generation with safe token prefix handling
            safe_token_prefix = (
                "<none>" if not token else sanitize_log_data(token[:5]) + "..."
            )
            logger.info(
                "[AUDIT][%s] Password reset token generated for %s from %s token_prefix=%s",
                datetime.now(timezone.utc).isoformat(),
                safe_email,
                safe_ip,
                safe_token_prefix,
            )

            # Compose reset link with proper URL construction
            frontend_url = os.environ.get(
                "FRONTEND_URL", "http://localhost:3000"
            ).rstrip("/")
            reset_link = f"{frontend_url}/reset-password?token={token}"

            # Send email
            try:
                subject = "Password Reset Request"
                body = (
                    f"To reset your password, click the following link:\n\n"
                    f"{reset_link}\n\n"
                    f"This link will expire in 30 minutes.\n\n"
                    f"If you did not request a password reset, please ignore this email "
                    f"and contact support if you have concerns.\n"
                )
                send_email(email, subject, body)
            except Exception:
                # Log email sending failure but don't expose to client
                logger.exception("[ERROR] Failed to send password reset email")
                session.rollback()

        except Exception:
            # Log the error but don't expose details to the client
            logger.exception("[ERROR] Failed to process password reset")
            session.rollback()
        finally:
            session.close()

    # Add random delay to prevent user enumeration timing attacks
    time.sleep(secrets.randbelow(100) / 1000)  # Random delay 0-100ms

    # Respond identically whether user exists or not for security
    response = jsonify(
        {"message": "If the email is registered, a reset link will be sent."}
    )
    return add_security_headers(response), 200


def validate_password(password: str) -> tuple[bool, str, int]:
    """
    Validate password strength against security requirements.

    Args:
        password: The password to validate

    Returns:
        tuple: (is_valid, error_message, status_code)

    """
    min_password_length = 12

    if len(password) < min_password_length:
        return (
            False,
            f"Password must be at least {min_password_length} characters long.",
            400,
        )

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter.", 400

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter.", 400

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number.", 400

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character.", 400

    return True, "", 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password() -> tuple[Response, int]:
    """
    Handle password reset with proper security measures.

    Returns:
        tuple: A tuple containing (response, status_code)

    """
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    new_password = data.get("new_password", "").strip()

    # Get client IP with fallback and validation
    remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if remote_ip and "," in remote_ip:
        remote_ip = remote_ip.split(",")[0].strip()

    # Validate IP address
    if not validate_ip_address(remote_ip):
        remote_ip = "<invalid-ip>"

    # Sanitize data for logging
    safe_ip = sanitize_log_data(cast("str", remote_ip))
    safe_token_prefix = "<none>" if not token else sanitize_log_data(token[:5]) + "..."

    # Validate input data
    if not token or not new_password:
        logger.warning(
            "[AUDIT][%s] Password reset failed (missing fields) from %s",
            datetime.now(timezone.utc).isoformat(),
            safe_ip,
        )
        return jsonify(
            {"message": "Missing token or new password."}
        ), 400  # Validate password strength
    is_valid, error_message, status_code = validate_password(new_password)
    if not is_valid:
        return jsonify({"message": error_message}), status_code

    return process_reset_token(token, new_password, safe_ip, safe_token_prefix)


def process_reset_token(
    token: str, new_password: str, safe_ip: str, safe_token_prefix: str
) -> tuple[Response, int]:
    """
    Process a password reset token and update the password if valid.

    Args:
        token: The reset token
        new_password: The new password
        safe_ip: Sanitized IP for logging
        safe_token_prefix: Sanitized token prefix for logging

    Returns:
        tuple: (response, status_code)

    """
    session = SessionLocal()
    try:
        # Use parameterized query to prevent SQL injection
        prt = session.query(PasswordResetToken).filter_by(token=token).first()

        if not prt or (prt.expires_at and prt.expires_at < datetime.now(timezone.utc)):
            logger.warning(
                "[AUDIT][%s] Password reset failed (invalid/expired token) from %s token_prefix=%s",
                datetime.now(timezone.utc).isoformat(),
                safe_ip,
                safe_token_prefix,
            )
            session.rollback()
            return jsonify({"message": "Invalid or expired reset link."}), 400

        email = prt.email
        safe_email = sanitize_log_data(cast("str", email))

        if email not in USERS:
            session.delete(prt)
            session.commit()
            logger.warning(
                "[AUDIT][%s] Password reset failed (user not found) for %s from %s",
                datetime.now(timezone.utc).isoformat(),
                safe_email,
                safe_ip,
            )
            return jsonify({"message": "Invalid or expired reset link."}), 400

        # Hash the new password with bcrypt using high work factor
        hashed = bcrypt.hashpw(
            new_password.encode(),
            bcrypt.gensalt(rounds=12),  # Higher work factor for better security
        ).decode()

        # Update password and invalidate all reset tokens
        USERS[cast("str", email)]["password"] = hashed
        session.query(PasswordResetToken).filter_by(email=email).delete()
        session.commit()

        logger.info(
            "[AUDIT][%s] Password reset completed for %s from %s",
            datetime.now(timezone.utc).isoformat(),
            safe_email,
            safe_ip,
        )

        response = jsonify({"message": "Password has been reset."})
        return add_security_headers(response), 200

    except Exception:
        # Log the error but don't expose details to the client
        logger.exception("[ERROR] Failed to reset password")
        session.rollback()
        return jsonify({"message": "An error occurred. Please try again later."}), 500
    finally:
        session.close()


def add_security_headers(response: Union[Response, str]) -> Response:
    """
    Add security headers to the response.

    Args:
        response: The response object or string to add headers to

    Returns:
        Response: The response with added security headers

    """
    if isinstance(response, str):
        response = Response(response)

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )

    # HTTP Strict Transport Security (max age: 1 year)
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy
    response.headers["Permissions-Policy"] = (
        "accelerometer=(), "
        "camera=(), "
        "geolocation=(), "
        "gyroscope=(), "
        "magnetometer=(), "
        "microphone=(), "
        "payment=(), "
        "usb=()"
    )

    return response
