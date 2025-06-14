"""Auth blueprint for Flask application with password reset functionality."""

from __future__ import annotations

import logging
import os
import re
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

import bcrypt
from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Pattern for allowed characters in logs. Anything not matching this will be replaced.
# Allows: a-z, A-Z, 0-9, space, period, underscore, @, :, /, =, -
ALLOWED_CHARS_PATTERN = re.compile(r"[^a-zA-Z0-9\s\._@:/=-]")

# Create a proper logger for this module
logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Flask-Limiter instance (for demo; in prod, usually set up in main app)
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)
# Ensure init_app method exists for compatibility
if not hasattr(limiter, "init_app"):
    limiter.init_app = lambda _: None  # type: ignore[assignment]

# In-memory user "database" for demonstration (replace with real user DB)
# Note: In production, use a proper database with secure password storage
USERS = {
    "e2euser@example.com": {
        "password": bcrypt.hashpw(b"oldpassword", bcrypt.gensalt()).decode(),
        "id": 1,
    }
}

RESET_TOKEN_EXPIRY = 1800  # 30 minutes

# SQLAlchemy setup for tokens (using SQLite for demo)
# In production, use a proper database with secure connection
Base = declarative_base()
db_url = os.environ.get("RESET_TOKEN_DB_URL", "sqlite:///reset_tokens.db")
# Use parameterized connection string to avoid SQL injection
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)


class PasswordResetToken(Base):
    """Model for password reset tokens."""

    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True, nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)


Base.metadata.create_all(bind=engine)


def send_email(to_addr: str, subject: str, body: str) -> None:
    """Send email with proper security measures."""
    # SMTP config from env vars or defaults
    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("SMTP_PORT", "1025"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_addr = os.environ.get("SMTP_FROM", "no-reply@example.com")

    # Create email with proper encoding
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_user and smtp_pass:
                # Always use TLS for security
                server.starttls()
                server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        logger.info("[Password Reset] Sent email to %s", sanitize_log_data(to_addr))
    except Exception:
        logger.exception("[Password Reset] Failed to send email")


def sanitize_log_data(data: str | None) -> str:
    """Sanitize data for logging to prevent log injection attacks."""
    if data is None:
        return "<none>"

    max_log_length = 256

    if isinstance(data, str):
        # Replace newlines first
        sanitized = data.replace("\n", " ").replace("\r", " ")

        # Replace any characters not in the allowed set with an underscore
        sanitized = ALLOWED_CHARS_PATTERN.sub("_", sanitized)

        # Truncate and return
        return sanitized[:max_log_length]
    # For non-strings, convert to string, then apply basic sanitization (length and newlines)
    s_data = str(data).replace("\n", " ").replace("\r", " ")
    # Also apply the strict character filter to the string representation of non-string data
    s_data = ALLOWED_CHARS_PATTERN.sub("_", s_data)
    # Removed html.escape from the return
    return s_data[:max_log_length]


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per minute")
def forgot_password() -> tuple[dict, int]:
    """Handle forgot password requests with proper security measures."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower() if data.get("email") else ""

    # Get client IP with fallback
    remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if remote_ip and "," in remote_ip:
        # If multiple IPs in X-Forwarded-For, take the first one
        remote_ip = remote_ip.split(",")[0].strip()

    # Sanitize data for logging
    safe_email = sanitize_log_data(email)
    safe_ip = sanitize_log_data(remote_ip)

    # Audit log every request
    logger.info(
        "[AUDIT][%s] Password reset requested for %s from %s",
        datetime.now(timezone.utc).isoformat(),
        safe_email or "<empty>",
        safe_ip,
    )

    # Always respond identically for user enumeration protection
    if not email:
        return jsonify(
            {"message": "If the email is registered, a reset link will be sent."}
        ), 200

    # If user exists, create a token and send an email
    if email in USERS:
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=RESET_TOKEN_EXPIRY)

        # Store token in DB with proper session handling
        session = SessionLocal()
        try:
            session.add(
                PasswordResetToken(email=email, token=token, expires_at=expires_at)
            )
            session.commit()

            # Log token generation (without exposing the full token in logs)
            # Use None for empty token so sanitize_log_data handles it as '<none>'
            token_prefix_raw = token[:5] if token else None
            token_prefix_sanitized = sanitize_log_data(token_prefix_raw)
            logger.info(
                "[AUDIT][%s] Password reset token generated for %s from %s token_prefix=%s...",
                datetime.now(timezone.utc).isoformat(),
                safe_email,
                safe_ip,
                token_prefix_sanitized,
            )

            # Compose reset link with proper URL construction
            frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
            reset_link = f"{frontend_url}/reset-password/{token}"

            subject = "Password Reset Request"
            body = f"To reset your password, click the following link:\n\n{reset_link}\n\nIf you did not request a password reset, please ignore this email."
            send_email(email, subject, body)
        except Exception:
            # Log the error but don't expose details to the client
            logger.exception("[ERROR] Failed to process password reset")
            session.rollback()
        finally:
            session.close()

    # Respond identically in either case for security
    return jsonify(
        {"message": "If the email is registered, a reset link will be sent."}
    ), 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password() -> tuple[object, int]:
    """Handle password reset with proper security measures."""
    data = request.get_json() or {}
    token = data.get("token", "")
    new_password = data.get("new_password", "")

    # Get client IP with fallback
    remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if remote_ip and "," in remote_ip:
        remote_ip = remote_ip.split(",")[0].strip()

    # Sanitize data for logging
    safe_ip = sanitize_log_data(remote_ip)
    # Sanitize token_prefix before logging
    # Use None for empty token so sanitize_log_data handles it as '<none>'
    raw_token_prefix = token[:5] if token else None
    safe_token_prefix = sanitize_log_data(raw_token_prefix)

    if not token or not new_password:
        logger.warning(
            "[AUDIT][%s] Password reset failed (missing fields) from %s",
            datetime.now(timezone.utc).isoformat(),
            safe_ip,
        )
        return jsonify({"message": "Missing token or new password."}), 400

    session = SessionLocal()
    try:
        # Use parameterized query to prevent SQL injection
        prt = session.query(PasswordResetToken).filter_by(token=token).first()

        if not prt or prt.expires_at < datetime.now(timezone.utc):
            logger.warning(
                "[AUDIT][%s] Password reset failed (invalid/expired token) from %s token_prefix=%s...",
                datetime.now(timezone.utc).isoformat(),
                safe_ip,
                safe_token_prefix,
            )
            return jsonify({"message": "Invalid or expired reset link."}), 400

        email = str(prt.email)
        safe_email = sanitize_log_data(email)

        if email not in USERS:
            session.delete(prt)
            session.commit()
            logger.warning(
                "[AUDIT][%s] Password reset failed (user not found) for %s from %s",
                datetime.now(timezone.utc).isoformat(),
                safe_email,
                safe_ip,
            )
            return jsonify(
                {"message": "Invalid or expired reset link."}
            ), 400  # Use same message for security

        # Hash the new password with bcrypt (already secure)
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        USERS[email]["password"] = hashed

        # Delete the used token
        session.delete(prt)
        session.commit()
        logger.info(
            "[AUDIT][%s] Password reset completed for %s from %s",
            datetime.now(timezone.utc).isoformat(),
            safe_email,
            safe_ip,
        )

        return jsonify({"message": "Password has been reset."}), 200
    except Exception:
        # Log the error but don't expose details to the client
        logger.exception("[ERROR] Failed to reset password")
        session.rollback()
        return jsonify({"message": "An error occurred. Please try again later."}), 500
    finally:
        session.close()


# To enable: import and register this blueprint with your Flask app, e.g.:
# from api.routes.auth import auth_bp
# app.register_blueprint(auth_bp)
