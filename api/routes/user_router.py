"""user_router - User API endpoints using SQLAlchemy ORM."""

import logging
import os
from typing import Any, Dict, Tuple

from flask import Blueprint, jsonify, request
from users.services import AuthenticationError, UserExistsError, UserService

# Set up logger
logger = logging.getLogger(__name__)
# Example: provide your secret through environment variable in production
TOKEN_SECRET = os.environ.get("USER_TOKEN_SECRET", "super-secret")

user_bp = Blueprint("user", __name__, url_prefix="/api/users")

user_service = UserService(token_secret=TOKEN_SECRET)


@user_bp.route("/", methods=["POST"])
def create_user() -> Tuple[Dict[str, Any], int]:
    """Create a new user.

    Returns:
        Tuple[Dict[str, Any], int]: JSON response with user data or error and HTTP status code
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    try:
        user = user_service.create_user(username, email, password)
        return jsonify(user), 201
    except UserExistsError:
        # Handle specific known exceptions with appropriate error messages
        return jsonify({"error": "User already exists"}), 400
    except AuthenticationError:
        return jsonify({"error": "Invalid credentials"}), 400
    except Exception:
        # Log the exception but don't expose details to the client
        logger.exception("Error creating user")
        # Return a generic error message to avoid information exposure
        return jsonify({"error": "An error occurred while creating the user"}), 500


@user_bp.route("/authenticate", methods=["POST"])
def authenticate_user() -> Tuple[Dict[str, Any], int]:
    """Authenticate a user.

    Returns:
        Tuple[Dict[str, Any], int]: JSON response with user data or error and HTTP status code
    """
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")
    success, user = user_service.authenticate_user(username_or_email, password)
    if success:
        return jsonify(user), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
