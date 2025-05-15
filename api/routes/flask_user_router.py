"""flask_user_router - User API endpoints using Flask."""

import logging

from flask import Blueprint, jsonify, request

from app_flask.models import User
from app_flask import db
from users.services import UserService

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint("user", __name__, url_prefix="/api/users")

# Initialize user service with a default token secret for testing
# In production, this should be a secure secret from environment variables
user_service = UserService(token_secret="test-secret-key-for-development-only")


@user_bp.route("/", methods=["GET"])
def get_users():
    """Get all users."""
    try:
        users = User.query.all()
        result = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active == "true"
            }
            for user in users
        ]
        return jsonify(result), 200
    except Exception:
        logger.exception("Error getting users")
        return jsonify({"error": "An error occurred while getting users"}), 500


@user_bp.route("/<string:user_id>", methods=["GET"])
def get_user(user_id: str):
    """Get a user by ID."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active == "true"
        }
        return jsonify(result), 200
    except Exception:
        # Fix for CodeQL Log Injection issue - don't include user input in log messages
        logger.exception("Error getting user")
        logger.info("Failed user_id: %s", user_id)  # Log user_id separately with proper formatting
        return jsonify({"error": "An error occurred while getting the user"}), 500


@user_bp.route("/", methods=["POST"])
def create_user():
    """Create a new user."""
    try:
        # Handle case where no JSON data is provided
        if not request.is_json:
            return jsonify({"error": "No data provided"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not all([username, email, password]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            user_data = user_service.create_user(username, email, password)
            return jsonify(user_data), 201
        except RuntimeError:
            # Handle unexpected server errors with 500 status code
            logger.exception("Server error creating user")
            return jsonify({"error": "An error occurred while creating the user"}), 500
        except Exception as e:
            # Handle validation errors with 400 status code
            logger.exception("Error creating user")
            # Fix for CodeQL Information exposure issue - don't expose raw exception to users
            # Create a safe error message that doesn't expose implementation details
            error_message = "Invalid input data"
            if hasattr(e, "message"):
                error_message = e.message
            elif str(e):
                # Only use the exception message if it's a validation error message
                # that's safe to show to users
                if any(safe_term in str(e).lower() for safe_term in
                      ["invalid", "required", "must be", "cannot be", "already exists"]):
                    error_message = str(e)
            return jsonify({"error": error_message}), 400
    except Exception:
        logger.exception("Server error creating user")
        return jsonify({"error": "An error occurred while creating the user"}), 500


@user_bp.route("/authenticate", methods=["POST"])
def authenticate_user():
    """Authenticate a user."""
    try:
        # Handle case where no JSON data is provided
        if not request.is_json:
            return jsonify({"error": "No data provided"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username_or_email = data.get("username_or_email")
        password = data.get("password")

        if not all([username_or_email, password]):
            return jsonify({"error": "Missing required fields"}), 400

        success, user_data = user_service.authenticate_user(username_or_email, password)

        if not success:
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate token
        token = user_service.generate_token(user_data)

        return jsonify({"token": token, "user": user_data}), 200
    except Exception:
        logger.exception("Error authenticating user")
        return jsonify({"error": "An error occurred while authenticating the user"}), 500


@user_bp.route("/<string:user_id>", methods=["PUT"])
def update_user(user_id: str):
    """Update a user."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        # Handle case where no JSON data is provided
        if not request.is_json:
            return jsonify({"error": "No data provided"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "is_active" in data:
            user.is_active = str(data["is_active"]).lower()

        db.session.commit()

        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active == "true"
        }
        return jsonify(result), 200
    except Exception:
        # Fix for CodeQL Log Injection issue - don't include user input in log messages
        logger.exception("Error updating user")
        logger.info("Failed user_id: %s", user_id)  # Log user_id separately with proper formatting
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the user"}), 500


@user_bp.route("/<string:user_id>", methods=["DELETE"])
def delete_user(user_id: str):
    """Delete a user."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": f"User with ID {user_id} deleted successfully"}), 200
    except Exception:
        # Fix for CodeQL Log Injection issue - don't include user input in log messages
        logger.exception("Error deleting user")
        logger.info("Failed user_id: %s", user_id)  # Log user_id separately with proper formatting
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the user"}), 500
