"""user_router - User API endpoints using SQLAlchemy ORM."""

from flask import Blueprint, request, jsonify, current_app
from flask.models import db, User
from users.services import UserService
import os

user_bp = Blueprint("user", __name__, url_prefix="/api/users")

# Example: provide your secret through environment variable in production
TOKEN_SECRET = os.environ.get("USER_TOKEN_SECRET", "super-secret")

user_service = UserService(token_secret=TOKEN_SECRET)

@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    try:
        user = user_service.create_user(username, email, password)
        return jsonify(user), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route("/authenticate", methods=["POST"])
def authenticate_user():
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")
    success, user = user_service.authenticate_user(username_or_email, password)
    if success:
        return jsonify(user), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
