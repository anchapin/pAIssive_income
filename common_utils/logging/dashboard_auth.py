"""
Authentication and authorization for the logging dashboard.

This module provides functionality for securing the logging dashboard with
authentication and authorization.

Usage:
    from common_utils.logging.dashboard_auth import (
        DashboardAuth,
        User,
        Role,
        Permission,
        require_auth,
        require_permission,
    )

    # Create dashboard auth
    auth = DashboardAuth()

    # Add users
    auth.add_user(
        User(
            username="admin",
            password_hash=auth.hash_password("admin_password"),
            roles=["admin"],
        )
    )
    auth.add_user(
        User(
            username="user",
            password_hash=auth.hash_password("user_password"),
            roles=["viewer"],
        )
    )

    # Add roles
    auth.add_role(
        Role(
            name="admin",
            permissions=["view_logs", "view_analytics", "view_alerts", "manage_alerts", "view_ml_analysis"],
        )
    )
    auth.add_role(
        Role(
            name="viewer",
            permissions=["view_logs", "view_analytics"],
        )
    )

    # Protect routes
    @app.callback(...)
    @require_auth
    def protected_callback(...):
        ...

    @app.callback(...)
    @require_permission("manage_alerts")
    def permission_protected_callback(...):
        ...
"""

import datetime
import hashlib
import hmac
import os
import secrets
import sys  # Added sys import
import time
import uuid
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional

try:
    import dash
    import flask
    from dash import dcc, html
    from dash.dependencies import Input, Output, State
    from dash.exceptions import PreventUpdate
    from flask import g, request, session
except ImportError:
    sys.exit(1)


try:
    from common_utils.logging.secure_logging import get_secure_logger
except ImportError:
    sys.exit(1)


# Set up logging for this module
logger = get_secure_logger(__name__)


@dataclass
class User:
    """User for dashboard authentication."""

    username: str
    password_hash: str
    roles: list[str] = field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime.datetime] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class Role:
    """Role for dashboard authorization."""

    name: str
    permissions: list[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class Permission:
    """Permission for dashboard authorization."""

    name: str
    description: Optional[str] = None


class DashboardAuth:
    """Authentication and authorization for the dashboard."""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        session_expiry: int = 3600,  # 1 hour
        pepper: Optional[str] = None,
    ) -> None:
        """
        Initialize the dashboard auth.

        Args:
            secret_key: Secret key for session signing
            session_expiry: Session expiry time in seconds
            pepper: Pepper for password hashing

        """
        self.secret_key = secret_key or os.environ.get("DASHBOARD_SECRET_KEY") or secrets.token_hex(32)
        self.session_expiry = session_expiry
        self.pepper = pepper or os.environ.get("DASHBOARD_PEPPER") or secrets.token_hex(16)

        self.users: dict[str, User] = {}
        self.roles: dict[str, Role] = {}
        self.permissions: dict[str, Permission] = {}

        # Security features
        self.rate_limiting_enabled = False
        self.max_auth_attempts = 5
        self.lockout_time = 300  # 5 minutes
        self.failed_attempts: dict[str, int] = {}
        self.lockout_until: dict[str, float] = {}

        self.csrf_protection_enabled = False
        self.csrf_tokens: dict[str, str] = {}

        self.audit_logging_enabled = False
        self.audit_logs: list[dict[str, Any]] = []

        # Add default permissions
        self._add_default_permissions()

    def _add_default_permissions(self) -> None:
        """Add default permissions."""
        default_permissions = [
            Permission(name="view_logs", description="View logs"),
            Permission(name="view_analytics", description="View analytics"),
            Permission(name="view_alerts", description="View alerts"),
            Permission(name="manage_alerts", description="Manage alerts"),
            Permission(name="view_ml_analysis", description="View machine learning analysis"),
            Permission(name="run_ml_analysis", description="Run machine learning analysis"),
            Permission(name="view_settings", description="View settings"),
            Permission(name="manage_settings", description="Manage settings"),
            Permission(name="manage_users", description="Manage users"),
            Permission(name="manage_roles", description="Manage roles"),
        ]

        for permission in default_permissions:
            self.add_permission(permission)

    def enable_rate_limiting(self, max_attempts: int = 5, lockout_time: int = 300) -> None:
        """
        Enable rate limiting for authentication attempts.

        Args:
            max_attempts: Maximum number of failed authentication attempts before lockout
            lockout_time: Lockout time in seconds after max failed attempts

        """
        self.rate_limiting_enabled = True
        self.max_auth_attempts = max_attempts
        self.lockout_time = lockout_time
        logger.info(f"Enabled rate limiting: max_attempts={max_attempts}, lockout_time={lockout_time}")

    def enable_csrf_protection(self) -> None:
        """Enable CSRF protection."""
        self.csrf_protection_enabled = True
        logger.info("Enabled CSRF protection")

    def enable_audit_logging(self) -> None:
        """Enable audit logging for security events."""
        self.audit_logging_enabled = True
        logger.info("Enabled audit logging")

    def log_audit_event(self, event_type: str, username: Optional[str] = None, details: Optional[dict[str, Any]] = None) -> None:
        """
        Log an audit event.

        Args:
            event_type: Type of event (e.g., "login", "logout", "permission_denied")
            username: Username associated with the event
            details: Additional details about the event

        """
        if not self.audit_logging_enabled:
            return

        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "username": username,
            "ip_address": request.remote_addr if request else None,
            "user_agent": request.user_agent.string if request and request.user_agent else None,
            "details": details or {},
        }

        self.audit_logs.append(event)
        logger.info(f"Audit: {event_type}", extra={"audit": event})

    def get_audit_logs(self, limit: int = 100, event_type: Optional[str] = None, username: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get audit logs.

        Args:
            limit: Maximum number of logs to return
            event_type: Filter by event type
            username: Filter by username

        Returns:
            List of audit logs

        """
        filtered_logs = self.audit_logs

        if event_type:
            filtered_logs = [log for log in filtered_logs if log["event_type"] == event_type]

        if username:
            filtered_logs = [log for log in filtered_logs if log["username"] == username]

        # Sort by timestamp (newest first)
        filtered_logs = sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True)

        return filtered_logs[:limit]

    def generate_csrf_token(self, session_id: str) -> str:
        """
        Generate a CSRF token for a session.

        Args:
            session_id: Session ID

        Returns:
            str: CSRF token

        """
        if not self.csrf_protection_enabled:
            return ""

        token = secrets.token_hex(32)
        self.csrf_tokens[session_id] = token
        return token

    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """
        Validate a CSRF token.

        Args:
            session_id: Session ID
            token: CSRF token

        Returns:
            bool: True if the token is valid, False otherwise

        """
        if not self.csrf_protection_enabled:
            return True

        expected_token = self.csrf_tokens.get(session_id)
        if not expected_token:
            return False

        return hmac.compare_digest(expected_token, token)

    def check_rate_limit(self, username: str) -> bool:
        """
        Check if a user is rate limited.

        Args:
            username: Username

        Returns:
            bool: True if the user is allowed to authenticate, False if rate limited

        """
        if not self.rate_limiting_enabled:
            return True

        # Check if user is locked out
        lockout_until = self.lockout_until.get(username, 0)
        if lockout_until > time.time():
            # User is locked out
            remaining = int(lockout_until - time.time())
            logger.warning(f"Rate limit: User {username} is locked out for {remaining} seconds")
            return False

        return True

    def record_failed_attempt(self, username: str) -> None:
        """
        Record a failed authentication attempt.

        Args:
            username: Username

        """
        if not self.rate_limiting_enabled:
            return

        # Increment failed attempts
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1

        # Check if user should be locked out
        if self.failed_attempts[username] >= self.max_auth_attempts:
            # Lock out user
            self.lockout_until[username] = time.time() + self.lockout_time
            logger.warning(f"Rate limit: User {username} locked out for {self.lockout_time} seconds after {self.failed_attempts[username]} failed attempts")

            # Log audit event
            self.log_audit_event("user_lockout", username, {
                "failed_attempts": self.failed_attempts[username],
                "lockout_time": self.lockout_time,
            })

    def reset_failed_attempts(self, username: str) -> None:
        """
        Reset failed authentication attempts for a user.

        Args:
            username: Username

        """
        if not self.rate_limiting_enabled:
            return

        # Reset failed attempts
        if username in self.failed_attempts:
            del self.failed_attempts[username]

        # Reset lockout
        if username in self.lockout_until:
            del self.lockout_until[username]

    def add_user(self, user: User) -> None:
        """
        Add a user.

        Args:
            user: User to add

        """
        self.users[user.username] = user
        logger.info(f"Added user: {user.username}")

    def remove_user(self, username: str) -> bool:
        """
        Remove a user.

        Args:
            username: Username of the user to remove

        Returns:
            bool: True if the user was removed, False if not found

        """
        if username in self.users:
            del self.users[username]
            logger.info(f"Removed user: {username}")
            return True
        return False

    def add_role(self, role: Role) -> None:
        """
        Add a role.

        Args:
            role: Role to add

        """
        self.roles[role.name] = role
        logger.info(f"Added role: {role.name}")

    def remove_role(self, name: str) -> bool:
        """
        Remove a role.

        Args:
            name: Name of the role to remove

        Returns:
            bool: True if the role was removed, False if not found

        """
        if name in self.roles:
            del self.roles[name]
            logger.info(f"Removed role: {name}")
            return True
        return False

    def add_permission(self, permission: Permission) -> None:
        """
        Add a permission.

        Args:
            permission: Permission to add

        """
        self.permissions[permission.name] = permission
        logger.info(f"Added permission: {permission.name}")

    def remove_permission(self, name: str) -> bool:
        """
        Remove a permission.

        Args:
            name: Name of the permission to remove

        Returns:
            bool: True if the permission was removed, False if not found

        """
        if name in self.permissions:
            del self.permissions[name]
            logger.info(f"Removed permission: {name}")
            return True
        return False

    def hash_password(self, password: str) -> str:
        """
        Hash a password.

        Args:
            password: Password to hash

        Returns:
            str: Hashed password

        """
        # Add pepper to password
        peppered = password + self.pepper

        # Generate salt
        salt = secrets.token_hex(16)

        # Hash password with salt
        hash_obj = hashlib.pbkdf2_hmac(
            "sha256",
            peppered.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # 100,000 iterations
        )
        hash_hex = hash_obj.hex()

        # Return salt and hash
        return f"{salt}${hash_hex}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password.

        Args:
            password: Password to verify
            password_hash: Hashed password

        Returns:
            bool: True if the password is correct, False otherwise

        """
        # Add pepper to password
        peppered = password + self.pepper

        # Split salt and hash
        salt, hash_hex = password_hash.split("$")

        # Hash password with salt
        hash_obj = hashlib.pbkdf2_hmac(
            "sha256",
            peppered.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # 100,000 iterations
        )
        new_hash_hex = hash_obj.hex()

        # Compare hashes
        return hmac.compare_digest(hash_hex, new_hash_hex)

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Password

        Returns:
            bool: True if authentication is successful, False otherwise

        """
        # Check rate limiting
        if not self.check_rate_limit(username):
            self.log_audit_event("authentication_rate_limited", username)
            return False

        user = self.users.get(username)
        if not user:
            logger.warning(f"Authentication failed: User not found: {username}")
            self.log_audit_event("authentication_failed", username, {"reason": "user_not_found"})
            self.record_failed_attempt(username)
            return False

        if not user.is_active:
            logger.warning(f"Authentication failed: User is inactive: {username}")
            self.log_audit_event("authentication_failed", username, {"reason": "user_inactive"})
            self.record_failed_attempt(username)
            return False

        if not self.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: Incorrect password for user: {username}")
            self.log_audit_event("authentication_failed", username, {"reason": "incorrect_password"})
            self.record_failed_attempt(username)
            return False

        # Authentication successful
        # Reset failed attempts
        self.reset_failed_attempts(username)

        # Update last login
        user.last_login = datetime.datetime.now()

        # Log audit event
        self.log_audit_event("authentication_successful", username)

        logger.info(f"Authentication successful: {username}")
        return True

    def get_user_permissions(self, username: str) -> set[str]:
        """
        Get permissions for a user.

        Args:
            username: Username

        Returns:
            Set[str]: Set of permission names

        """
        user = self.users.get(username)
        if not user:
            return set()

        permissions = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)

        return permissions

    def has_permission(self, username: str, permission: str) -> bool:
        """
        Check if a user has a permission.

        Args:
            username: Username
            permission: Permission name

        Returns:
            bool: True if the user has the permission, False otherwise

        """
        return permission in self.get_user_permissions(username)

    def create_session(self, username: str) -> dict[str, Any]:
        """
        Create a session for a user.

        Args:
            username: Username

        Returns:
            Dict[str, Any]: Session data

        """
        now = int(time.time())
        expiry = now + self.session_expiry

        return {
            "username": username,
            "created_at": now,
            "expires_at": expiry,
        }


    def validate_session(self, session_data: dict[str, Any]) -> bool:
        """
        Validate a session.

        Args:
            session_data: Session data

        Returns:
            bool: True if the session is valid, False otherwise

        """
        if not session_data:
            return False

        username = session_data.get("username")
        expires_at = session_data.get("expires_at")

        if not username or not expires_at:
            return False

        # Check if user exists and is active
        user = self.users.get(username)
        if not user or not user.is_active:
            return False

        # Check if session has expired
        now = int(time.time())
        return not now > expires_at

    def init_app(self, app: dash.Dash) -> None:
        """
        Initialize the app with authentication.

        Args:
            app: Dash app

        """
        # Set secret key for Flask session
        app.server.secret_key = self.secret_key

        # Store auth in app
        app.auth = self

        # Add login layout
        app.login_layout = html.Div(
            [
                html.H2("Login", className="text-center mb-4"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Username", className="form-label"),
                                html.Input(
                                    id="username-input",
                                    type="text",
                                    className="form-control",
                                    placeholder="Enter username",
                                ),
                            ],
                            className="mb-3",
                        ),
                        html.Div(
                            [
                                html.Label("Password", className="form-label"),
                                html.Input(
                                    id="password-input",
                                    type="password",
                                    className="form-control",
                                    placeholder="Enter password",
                                ),
                            ],
                            className="mb-3",
                        ),
                        # Add CSRF token (hidden)
                        dcc.Store(id="csrf-token"),
                        html.Button(
                            "Login",
                            id="login-button",
                            className="btn btn-primary w-100",
                        ),
                        html.Div(id="login-error", className="text-danger mt-2"),
                    ],
                    className="card p-4",
                    style={"maxWidth": "400px", "margin": "0 auto"},
                ),
            ],
            className="container mt-5",
        )

        # Add CSRF token generation callback
        @app.callback(
            Output("csrf-token", "data"),
            [Input("_auth-location", "pathname")],
        )
        def generate_csrf(pathname):
            if self.csrf_protection_enabled:
                # Generate a unique session ID if not already in session
                if "session_id" not in session:
                    session["session_id"] = str(uuid.uuid4())

                # Generate CSRF token
                return self.generate_csrf_token(session["session_id"])
            return ""

        # Add login callback
        @app.callback(
            [
                Output("login-error", "children"),
                Output("_auth-store", "data"),
            ],
            [Input("login-button", "n_clicks")],
            [
                State("username-input", "value"),
                State("password-input", "value"),
                State("csrf-token", "data"),
            ],
        )
        def login(n_clicks, username, password, csrf_token):
            if not n_clicks:
                raise PreventUpdate

            if not username or not password:
                return "Please enter username and password", None

            # Validate CSRF token
            if self.csrf_protection_enabled:
                if "session_id" not in session:
                    self.log_audit_event("csrf_validation_failed", username, {"reason": "missing_session_id"})
                    return "Session expired. Please refresh the page and try again.", None

                if not self.validate_csrf_token(session["session_id"], csrf_token):
                    self.log_audit_event("csrf_validation_failed", username, {"reason": "invalid_token"})
                    return "Invalid request. Please refresh the page and try again.", None

            if self.authenticate(username, password):
                # Create session
                session_data = self.create_session(username)

                # Store in Flask session
                session["auth"] = session_data

                # Log audit event
                self.log_audit_event("login_successful", username)

                return "", {"authenticated": True}
            return "Invalid username or password", None

        # Add logout callback
        @app.callback(
            [
                Output("_auth-store", "clear_data"),
                Output("_auth-location", "pathname"),
            ],
            [Input("logout-button", "n_clicks")],
            [State("csrf-token", "data")],
        )
        def logout(n_clicks, csrf_token):
            if not n_clicks:
                raise PreventUpdate

            # Validate CSRF token
            if self.csrf_protection_enabled:
                if "session_id" not in session:
                    return True, "/"

                if not self.validate_csrf_token(session["session_id"], csrf_token):
                    return True, "/"

            # Get username before clearing session
            username = None
            if "auth" in session:
                username = session["auth"].get("username")

            # Clear session
            session.clear()

            # Log audit event
            if username:
                self.log_audit_event("logout", username)

            return True, "/"

        # Add auth store
        app.layout = html.Div(
            [
                dcc.Store(id="_auth-store"),
                dcc.Location(id="_auth-location"),
                html.Div(id="_auth-content"),
            ]
        )

        # Add auth content callback
        @app.callback(
            Output("_auth-content", "children"),
            [Input("_auth-store", "data"), Input("_auth-location", "pathname")],
        )
        def update_auth_content(auth_data, pathname):
            # Check if authenticated
            is_authenticated = False
            username = None

            # Check Flask session
            if "auth" in session:
                session_data = session["auth"]
                is_authenticated = self.validate_session(session_data)
                username = session_data.get("username")

            # Check auth data
            if auth_data and auth_data.get("authenticated"):
                is_authenticated = True

            if is_authenticated:
                # Log page access
                if username and pathname:
                    self.log_audit_event("page_access", username, {"pathname": pathname})

                # Show app content
                return app._original_layout
            # Show login layout
            return app.login_layout

        # Store original layout
        app._original_layout = app.layout

        # Add middleware for audit logging
        @app.server.before_request
        def before_request() -> None:
            # Set request start time for performance logging
            g.start_time = time.time()

        @app.server.after_request
        def after_request(response):
            # Log request performance
            if hasattr(g, "start_time") and self.audit_logging_enabled:
                duration = time.time() - g.start_time

                # Log slow requests (> 1 second)
                if duration > 1.0:
                    username = None
                    if "auth" in session:
                        username = session["auth"].get("username")

                    self.log_audit_event("slow_request", username, {
                        "path": request.path,
                        "method": request.method,
                        "duration": duration,
                    })

            return response

        logger.info("Initialized app with authentication")


def require_auth(f=None, *, context_getter=None):
    """
    Decorator to require authentication for a callback.

    Args:
        f: Callback function
        context_getter: Optional callable to get the callback context (for testing)

    Returns:
        Wrapped callback function

    """
    if context_getter is None:
        import dash
        def context_getter():
            return dash.callback_context

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get current app
            ctx = context_getter()
            if not ctx.outputs:
                raise PreventUpdate

            app = ctx.outputs[0]["id"].split(".")[0]._dash_app

            # Check if authenticated
            is_authenticated = False

            # Check Flask session
            if "auth" in session:
                session_data = session["auth"]
                is_authenticated = app.auth.validate_session(session_data)

            if not is_authenticated:
                raise PreventUpdate

            return func(*args, **kwargs)
        return wrapper
    if f is not None:
        return decorator(f)
    return decorator


def require_permission(permission, *, context_getter=None):
    """
    Decorator to require a permission for a callback.

    Args:
        permission: Permission name
        context_getter: Optional callable to get the callback context (for testing)

    Returns:
        Decorator function

    """
    if context_getter is None:
        import dash
        def context_getter():
            return dash.callback_context

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get current app
            ctx = context_getter()
            if not ctx.outputs:
                raise PreventUpdate

            app = ctx.outputs[0]["id"].split(".")[0]._dash_app

            # Check if authenticated
            is_authenticated = False
            username = None

            # Check Flask session
            if "auth" in session:
                session_data = session["auth"]
                is_authenticated = app.auth.validate_session(session_data)
                username = session_data.get("username")

            if not is_authenticated:
                # Log audit event
                if app.auth.audit_logging_enabled:
                    app.auth.log_audit_event("permission_check_failed", username, {
                        "permission": permission,
                        "reason": "not_authenticated",
                        "callback": f.__name__,
                    })
                raise PreventUpdate

            # Check permission
            if not app.auth.has_permission(username, permission):
                # Log audit event
                if app.auth.audit_logging_enabled:
                    app.auth.log_audit_event("permission_denied", username, {
                        "permission": permission,
                        "callback": f.__name__,
                    })
                raise PreventUpdate

            # Log successful permission check
            if app.auth.audit_logging_enabled:
                app.auth.log_audit_event("permission_granted", username, {
                    "permission": permission,
                    "callback": f.__name__,
                })

            return f(*args, **kwargs)
        return wrapper
    return decorator
