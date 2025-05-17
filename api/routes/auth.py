from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
import bcrypt
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime, timedelta
import logging

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Flask-Limiter instance (for demo; in prod, usually set up in main app)
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
limiter.init_app = getattr(limiter, "init_app", lambda app: None)  # for compatibility if already set up

# In-memory user "database" for demonstration (replace with real user DB)
USERS = {
    "e2euser@example.com": {"password": bcrypt.hashpw(b"oldpassword", bcrypt.gensalt()).decode(), "id": 1}
}

RESET_TOKEN_EXPIRY = 1800  # 30 minutes

# SQLAlchemy setup for tokens (using SQLite for demo)
Base = declarative_base()
engine = create_engine(os.environ.get("RESET_TOKEN_DB_URL", "sqlite:///reset_tokens.db"))
SessionLocal = sessionmaker(bind=engine)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True, nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

def send_email(to_addr, subject, body):
    # SMTP config from env vars or defaults
    SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 1025))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASS = os.environ.get("SMTP_PASS", "")
    FROM_ADDR = os.environ.get("SMTP_FROM", "no-reply@example.com")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = FROM_ADDR
    msg['To'] = to_addr
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            if SMTP_USER and SMTP_PASS:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_ADDR, [to_addr], msg.as_string())
        print(f"[Password Reset] Sent email to {to_addr}")
    except Exception as e:
        print(f"[Password Reset] Failed to send email: {e}")

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    # Audit log every request
    logging.info(f"[AUDIT][{datetime.utcnow().isoformat()}] Password reset requested for {email or '<empty>'} from {remote_ip}")

    # Always respond identically for user enumeration protection
    if not email:
        return jsonify({"message": "If the email is registered, a reset link will be sent."}), 200

    # If user exists, create a token and send an email
    if email in USERS:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=RESET_TOKEN_EXPIRY)
        # Store token in DB
        session = SessionLocal()
        session.add(PasswordResetToken(email=email, token=token, expires_at=expires_at))
        session.commit()
        session.close()
        logging.info(f"[AUDIT][{datetime.utcnow().isoformat()}] Password reset token generated for {email} from {remote_ip} token={token}")
        # Compose reset link (assuming frontend at localhost:3000)
        reset_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password/{token}"
        subject = "Password Reset Request"
        body = f"To reset your password, click the following link:\n\n{reset_link}\n\nIf you did not request a password reset, please ignore this email."
        send_email(email, subject, body)
    # Respond identically in either case
    return jsonify({"message": "If the email is registered, a reset link will be sent."}), 200

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if not token or not new_password:
        logging.warning(f"[AUDIT][{datetime.utcnow().isoformat()}] Password reset failed (missing fields) from {remote_ip}")
        return jsonify({"message": "Missing token or new password."}), 400

    session = SessionLocal()
    prt = session.query(PasswordResetToken).filter_by(token=token).first()
    if not prt or prt.expires_at < datetime.utcnow():
        session.close()
        logging.warning(f"[AUDIT][{datetime.utcnow().isoformat()}] Password reset failed (invalid/expired token) from {remote_ip} token={token}")
        return jsonify({"message": "Invalid or expired reset link."}), 400

    email = prt.email
    if email not in USERS:
        session.delete(prt)
        session.commit()
        session.close()
        logging.warning(f"[AUDIT][{datetime.utcnow().isoformat()}] Password reset failed (user not found) for {email} from {remote_ip} token={token}")
        return jsonify({"message": "User not found."}), 400

    # Hash the new password and update the user record
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    USERS[email]['password'] = hashed
    session.delete(prt)
    session.commit()
    session.close()
    logging.info(f"[AUDIT][{datetime.utcnow().isoformat()}] Password reset completed for {email} from {remote_ip}")

    return jsonify({"message": "Password has been reset."}), 200

# To enable: import and register this blueprint with your Flask app, e.g.:
# from api.routes.auth import auth_bp
# app.register_blueprint(auth_bp)