"""user_router - User API endpoints using SQLAlchemy ORM."""

import os
from typing import Any, Dict, Tuple

from flask import Blueprint, jsonify, request

from common_utils.logging import get_logger
from users.services import AuthenticationError, UserExistsError, UserService

# Set up secure logger that masks sensitive info
logger = get_logger(__name__)

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
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        logger.info("Creating new user")
        user = user_service.create_user(username, email, password)
        logger.info("User created successfully")
        return jsonify(user), 201

    except UserExistsError:
        logger.warning("Attempt to create duplicate user")
        return jsonify({"error": "User already exists"}), 400

    except AuthenticationError:
        logger.warning("Invalid credentials provided during user creation")
        return jsonify({"error": "Invalid credentials"}), 400

    except Exception:
        logger.exception("Failed to create user")
        return jsonify({"error": "An error occurred while creating the user"}), 500


@user_bp.route("/authenticate", methods=["POST"])
def authenticate_user() -> Tuple[Dict[str, Any], int]:
    """Authenticate a user.

    Returns:
        Tuple[Dict[str, Any], int]: JSON response with user data or error and HTTP status code
    """
    try:
        data = request.get_json()
        username_or_email = data.get("username_or_email")
        password = data.get("password")

        logger.info("Authenticating user")
        success, user = user_service.authenticate_user(username_or_email, password)

        if success:
            logger.info("User authentication successful")
            return jsonify(user), 200

        logger.warning("Invalid credentials provided")
        return jsonify({"error": "Invalid credentials"}), 401

    except Exception:
        logger.exception("Failed to authenticate user")
        return jsonify({"error": "An error occurred during authentication"}), 500
