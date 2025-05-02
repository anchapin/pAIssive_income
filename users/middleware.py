"""
Authentication and authorization middleware for Flask API.

This module provides decorators and middleware for authentication and authorization.
"""

import functools
import logging
from typing import Callable, Optional

from flask import g, jsonify, request

from .auth import verify_auth_token
from .permissions import PERMISSION_LEVELS, has_permission
from .services import get_user_by_id

# Configure logger
logger = logging.getLogger(__name__)


def authenticate(f: Callable) -> Callable:
    """
    Decorator to enforce authentication for API routes.

    This decorator checks for a valid JWT token in the Authorization header,
    and attaches user information to Flask's g object if the token is valid.

    Args:
        f: Flask route function to wrap

    Returns:
        Wrapped function that enforces authentication
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            return (
                jsonify(
                    {
                        "error": "Authentication Error",
                        "message": "Authentication required",
                    }
                ),
                401,
            )

        # Extract token
        token = auth_header.split("Bearer ")[1]

        # Verify token
        payload = verify_auth_token(token)
        if not payload:
            logger.warning("Invalid or expired token")
            return (
                jsonify(
                    {
                        "error": "Authentication Error",
                        "message": "Invalid or expired token",
                    }
                ),
                401,
            )

        # Store user ID in Flask's g object
        g.user_id = payload.get("sub")
        g.user_roles = payload.get("roles", [])

        # Get full user object (optional)
        user = get_user_by_id(g.user_id)
        if user:
            g.user = user
        else:
            logger.warning(f"Token has valid user ID {g.user_id}, but user not found")
            return (
                jsonify({"error": "Authentication Error", "message": "User not found"}),
                401,
            )

        # Continue to the route handler
        return f(*args, **kwargs)

    return decorated_function


def require_permission(permission: str, level: Optional[PERMISSION_LEVELS] = None) -> Callable:
    """
    Decorator to enforce permissions for API routes.

    This decorator must be used after the authenticate decorator,
    as it relies on user information being available in Flask's g object.

    Args:
        permission: Required permission ID
        level: Optional minimum permission level

    Returns:
        Decorator function that enforces permissions
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Ensure user is authenticated
            if not hasattr(g, "user_roles"):
                logger.error("require_permission used without authenticate decorator")
                return (
                    jsonify({"error": "Server Error", "message": "Internal server error"}),
                    500,
                )

            # Check permission
            if not has_permission(g.user_roles, permission, level):
                logger.warning(
                    f"Permission denied: {permission} (level {level}) for user roles {g.user_roles}"
                )
                return (
                    jsonify(
                        {
                            "error": "Permission Denied",
                            "message": "You don't have permission to access this resource",
                        }
                    ),
                    403,
                )

            # Continue to the route handler
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def audit_log(action: str, resource_type: str) -> Callable:
    """
    Decorator to add audit logging for security events.

    Args:
        action: The action being performed (e.g., "create", "update", "delete")
        resource_type: The type of resource being acted upon

    Returns:
        Decorator function that adds audit logging
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user information if available
            user_id = getattr(g, "user_id", "anonymous")

            # Log before attempting the action
            logger.info(f"AUDIT: User {user_id} attempting {action} on {resource_type}")

            # Call the original function
            result = f(*args, **kwargs)

            # Log after the action is completed
            status_code = 200
            if isinstance(result, tuple) and len(result) > 1:
                status_code = result[1]

            if 200 <= status_code < 300:
                outcome = "success"
            else:
                outcome = "failure"

            logger.info(f"AUDIT: User {user_id} {action} on {resource_type} - {outcome}")

            return result

        return decorated_function

    return decorator
