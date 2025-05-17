from flask import Blueprint, request, jsonify
import secrets
import time
import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# In-memory user "database" and reset tokens (for demonstration only)
USERS = {
    "e2euser@example.com": {"password": bcrypt.hashpw(b"oldpassword", bcrypt.gensalt()).decode(), "id": 1}
}
RESET_TOKENS = {}  # token: {email, expires_at}

RESET_TOKEN_EXPIRY = 1800  # 30 minutes

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    # Always respond identically for user enumeration protection
    if not email:
        return jsonify({"message": "If the email is registered, a reset link will be sent."}), 200

    # If user exists, create a token and "send" an email (here: just log)
    if email in USERS:
        token = secrets.token_urlsafe(32)
        RESET_TOKENS[token] = {
            "email": email,
            "expires_at": time.time() + RESET_TOKEN_EXPIRY
        }
        print(f"[Password Reset] Generated reset token for {email}: {token}")
        # In real app: send email with link containing token
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