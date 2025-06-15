"""Security middleware for Flask application."""

from __future__ import annotations

import functools
import re
from collections.abc import Callable
from typing import Any, TypeVar, cast

from flask import Response, request
from werkzeug.datastructures import Headers

# Define type variables for better type annotations
F = TypeVar("F", bound=Callable[..., Any])
R = TypeVar("R")


def require_https() -> Callable[[F], F]:
    """
    Enforce HTTPS.

    Returns:
        Callable: The decorated function

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if not request.is_secure:
                return Response(
                    "HTTPS Required",
                    status=400,
                    headers={"Location": request.url.replace("http://", "https://", 1)},
                )
            return f(*args, **kwargs)

        return cast("F", decorated_function)

        return decorated_function

    return decorator


def set_security_headers() -> Callable[[F], F]:
    """
    Set security headers.

    Returns:
        Callable: The decorated function

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Response:
            response = f(*args, **kwargs)
            if not isinstance(response, Response):
                response = Response(response)

            headers = Headers()
            # Prevent clickjacking
            headers.add("X-Frame-Options", "DENY")
            # Enable XSS protection
            headers.add("X-XSS-Protection", "1; mode=block")
            # Prevent MIME type sniffing
            headers.add("X-Content-Type-Options", "nosniff")
            # Content Security Policy
            headers.add(
                "Content-Security-Policy",
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "frame-ancestors 'none'; "
                "form-action 'self'",
            )
            # HTTP Strict Transport Security (max age: 1 year)
            headers.add(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
            # Referrer Policy
            headers.add("Referrer-Policy", "strict-origin-when-cross-origin")
            # Permissions Policy
            headers.add(
                "Permissions-Policy",
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()",
            )
            response.headers.extend(headers)
            return response

        return cast("F", decorated_function)

    return decorator


def sanitize_response() -> Callable[[F], F]:
    """
    Sanitize response content.

    Returns:
        Callable: The decorated function

    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Response:
            response = f(*args, **kwargs)
            if not isinstance(response, Response):
                response = Response(response)

            # Remove potentially sensitive headers
            sensitive_headers = {
                "Server",
                "X-Powered-By",
                "X-AspNet-Version",
                "X-AspNetMvc-Version",
            }
            for header in sensitive_headers:
                response.headers.pop(header, None)
            return response

        return cast("F", decorated_function)

    return decorator


def setup_security_middleware(app: object) -> None:
    """
    Set up security middleware for the Flask app.

    Args:
        app: The Flask application instance

    """
    # Register security middleware
    app.before_request(validate_request)

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response: Response) -> Response:
        # Add security headers using the existing decorator
        return set_security_headers()(lambda: response)()


def validate_request() -> Response | None:
    """
    Validate incoming requests for security.

    Returns:
        Optional[Response]: Error response if validation fails, None if successful

    """
    # Block potentially dangerous HTTP methods
    if request.method not in {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"}:
        return Response("Method not allowed", status=405)

    # Validate Content-Type for POST/PUT requests
    if (
        request.method in {"POST", "PUT"}
        and request.content_type
        and not re.match(
            r"^application/json(;\s*charset=UTF-8)?$",
            request.content_type,
            re.IGNORECASE,
        )
    ):
        return Response("Invalid Content-Type", status=400)

    # Check request size (16MB limit)
    content_length = request.content_length or 0
    if content_length > 16 * 1024 * 1024:
        return Response("Request too large", status=413)

    return None
