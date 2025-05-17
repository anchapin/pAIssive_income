from flask import Blueprint, request, jsonify
import secrets
import time
import bcrypt
import smtplib
from email.mime.text import MIMEText
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# In-memory user "database" and reset tokens (for demonstration only)
USERS = {
    "e2euser@example.com": {"password": bcrypt.hashpw(b"oldpassword", bcrypt.gensalt()).decode(), "id": 1}
}
RESET_TOKENS = {}  # token: {email, expires_at}

RESET_TOKEN_EXPIRY = 1800  # 30 minutes

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
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    # Always respond identically for user enumeration protection
    if not email:
        return jsonify({"message": "If the email is registered, a reset link will be sent."}), 200

    # If user exists, create a token and send an email
    if email in USERS:
        token = secrets.token_urlsafe(32)
        RESET_TOKENS[token] = {
            "email": email,
            "expires_at": time.time() + RESET_TOKEN_EXPIRY
        }
        print(f"[Password Reset] Generated reset token for {email}: {token}")
        # Compose reset link (assuming frontend at localhost:3000)
        reset_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password/{token}"
        subject = "Password Reset Request"
        body = f"To reset your password, click the following link:\n\n{reset_link}\n\nIf you did not request a password reset, please ignore this email."
        send_email(email, subject, body)
    # Respond identically in either case
    return jsonify({"message": "If the email is registered, a reset link will be sent."}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    if not token or not new_password:
        return jsonify({"message": "Missing token or new password."}), 400

    token_info = RESET_TOKENS.get(token)
    if not token_info or token_info['expires_at'] < time.time():
        return jsonify({"message": "Invalid or expired reset link."}), 400

    email = token_info['email']
    if email not in USERS:
        return jsonify({"message": "User not found."}), 400

    # Hash the new password and update the user record
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    USERS[email]['password'] = hashed
    del RESET_TOKENS[token]
    print(f"[Password Reset] Password hash set for {email}")

    return jsonify({"message": "Password has been reset."}), 200

# To enable: import and register this blueprint with your Flask app, e.g.:
# from api.routes.auth import auth_bp
# app.register_blueprint(auth_bp)