"""Test module for common_utils.logging.dashboard_auth."""

import datetime
import time
from unittest.mock import MagicMock, patch

import dash
import pytest
from dash import html
from dash.exceptions import PreventUpdate

from common_utils.logging.dashboard_auth import (
    DashboardAuth,
    Permission,
    Role,
    User,
    require_auth,
    require_permission,
)


class TestUser:
    """Test suite for User class."""

    def test_init(self):
        """Test initialization."""
        user = User(
            username="test",
            password_hash="hash",
            roles=["admin", "viewer"],
        )
        assert user.username == "test"
        assert user.password_hash == "hash"
        assert user.roles == ["admin", "viewer"]
        assert user.is_active is True
        assert user.last_login is None
        assert isinstance(user.created_at, datetime.datetime)


class TestRole:
    """Test suite for Role class."""

    def test_init(self):
        """Test initialization."""
        role = Role(
            name="admin",
            permissions=["view_logs", "manage_alerts"],
            description="Administrator role",
        )
        assert role.name == "admin"
        assert role.permissions == ["view_logs", "manage_alerts"]
        assert role.description == "Administrator role"


class TestPermission:
    """Test suite for Permission class."""

    def test_init(self):
        """Test initialization."""
        permission = Permission(
            name="view_logs",
            description="View logs",
        )
        assert permission.name == "view_logs"
        assert permission.description == "View logs"


class TestDashboardAuth:
    """Test suite for DashboardAuth class."""

    def test_init(self):
        """Test initialization."""
        auth = DashboardAuth(
            secret_key="test_key",
            session_expiry=3600,
            pepper="test_pepper",
        )
        assert auth.secret_key == "test_key"
        assert auth.session_expiry == 3600
        assert auth.pepper == "test_pepper"
        assert isinstance(auth.users, dict)
        assert isinstance(auth.roles, dict)
        assert isinstance(auth.permissions, dict)
        assert len(auth.permissions) > 0  # Default permissions

        # Check security features initialization
        assert auth.rate_limiting_enabled is False
        assert auth.csrf_protection_enabled is False
        assert auth.audit_logging_enabled is False
        assert isinstance(auth.failed_attempts, dict)
        assert isinstance(auth.lockout_until, dict)
        assert isinstance(auth.csrf_tokens, dict)
        assert isinstance(auth.audit_logs, list)

    def test_add_user(self):
        """Test adding a user."""
        auth = DashboardAuth()
        user = User(
            username="test",
            password_hash="hash",
        )

        auth.add_user(user)
        assert "test" in auth.users
        assert auth.users["test"] == user

    def test_remove_user(self):
        """Test removing a user."""
        auth = DashboardAuth()
        user = User(
            username="test",
            password_hash="hash",
        )

        auth.add_user(user)
        assert "test" in auth.users

        result = auth.remove_user("test")
        assert result is True
        assert "test" not in auth.users

        result = auth.remove_user("nonexistent")
        assert result is False

    def test_add_role(self):
        """Test adding a role."""
        auth = DashboardAuth()
        role = Role(
            name="admin",
            permissions=["view_logs"],
        )

        auth.add_role(role)
        assert "admin" in auth.roles
        assert auth.roles["admin"] == role

    def test_remove_role(self):
        """Test removing a role."""
        auth = DashboardAuth()
        role = Role(
            name="admin",
            permissions=["view_logs"],
        )

        auth.add_role(role)
        assert "admin" in auth.roles

        result = auth.remove_role("admin")
        assert result is True
        assert "admin" not in auth.roles

        result = auth.remove_role("nonexistent")
        assert result is False

    def test_add_permission(self):
        """Test adding a permission."""
        auth = DashboardAuth()
        permission = Permission(
            name="custom_permission",
            description="Custom permission",
        )

        auth.add_permission(permission)
        assert "custom_permission" in auth.permissions
        assert auth.permissions["custom_permission"] == permission

    def test_remove_permission(self):
        """Test removing a permission."""
        auth = DashboardAuth()
        permission = Permission(
            name="custom_permission",
            description="Custom permission",
        )

        auth.add_permission(permission)
        assert "custom_permission" in auth.permissions

        result = auth.remove_permission("custom_permission")
        assert result is True
        assert "custom_permission" not in auth.permissions

        result = auth.remove_permission("nonexistent")
        assert result is False

    def test_hash_password(self):
        """Test password hashing."""
        auth = DashboardAuth(pepper="test_pepper")
        password_hash = auth.hash_password("password")

        # Check format
        assert "$" in password_hash
        salt, hash_hex = password_hash.split("$")
        assert len(salt) == 32  # 16 bytes as hex
        assert len(hash_hex) == 64  # 32 bytes as hex

    def test_verify_password(self):
        """Test password verification."""
        auth = DashboardAuth(pepper="test_pepper")
        password_hash = auth.hash_password("password")

        # Correct password
        assert auth.verify_password("password", password_hash) is True

        # Incorrect password
        assert auth.verify_password("wrong", password_hash) is False

    def test_authenticate(self):
        """Test user authentication."""
        auth = DashboardAuth()
        password_hash = auth.hash_password("password")

        user = User(
            username="test",
            password_hash=password_hash,
        )
        auth.add_user(user)

        # Correct credentials
        assert auth.authenticate("test", "password") is True
        assert user.last_login is not None

        # Incorrect password
        assert auth.authenticate("test", "wrong") is False

        # Nonexistent user
        assert auth.authenticate("nonexistent", "password") is False

        # Inactive user
        user.is_active = False
        assert auth.authenticate("test", "password") is False

    def test_authenticate_with_rate_limiting(self):
        """Test user authentication with rate limiting."""
        auth = DashboardAuth()
        auth.enable_rate_limiting(max_attempts=3, lockout_time=300)
        auth.enable_audit_logging()

        password_hash = auth.hash_password("password")

        user = User(
            username="test",
            password_hash=password_hash,
        )
        auth.add_user(user)

        # Correct credentials
        assert auth.authenticate("test", "password") is True

        # Incorrect password (first attempt)
        assert auth.authenticate("test", "wrong") is False
        assert auth.failed_attempts.get("test") == 1

        # Incorrect password (second attempt)
        assert auth.authenticate("test", "wrong") is False
        assert auth.failed_attempts.get("test") == 2

        # Incorrect password (third attempt - should trigger lockout)
        assert auth.authenticate("test", "wrong") is False
        assert auth.failed_attempts.get("test") == 3
        assert "test" in auth.lockout_until

        # Try to authenticate while locked out
        assert auth.authenticate("test", "password") is False

        # Check audit logs
        assert len(auth.audit_logs) > 0
        assert any(log["event_type"] == "authentication_rate_limited" for log in auth.audit_logs)

        # Reset lockout
        auth.reset_failed_attempts("test")

        # Should be able to authenticate again
        assert auth.authenticate("test", "password") is True

    def test_get_user_permissions(self):
        """Test getting user permissions."""
        auth = DashboardAuth()

        # Add roles
        admin_role = Role(
            name="admin",
            permissions=["view_logs", "manage_alerts"],
        )
        viewer_role = Role(
            name="viewer",
            permissions=["view_logs"],
        )
        auth.add_role(admin_role)
        auth.add_role(viewer_role)

        # Add user with multiple roles
        user = User(
            username="test",
            password_hash="hash",
            roles=["admin", "viewer"],
        )
        auth.add_user(user)

        # Get permissions
        permissions = auth.get_user_permissions("test")
        assert permissions == {"view_logs", "manage_alerts"}

        # Nonexistent user
        permissions = auth.get_user_permissions("nonexistent")
        assert permissions == set()

    def test_has_permission(self):
        """Test checking if a user has a permission."""
        auth = DashboardAuth()

        # Add role
        role = Role(
            name="admin",
            permissions=["view_logs", "manage_alerts"],
        )
        auth.add_role(role)

        # Add user
        user = User(
            username="test",
            password_hash="hash",
            roles=["admin"],
        )
        auth.add_user(user)

        # Check permissions
        assert auth.has_permission("test", "view_logs") is True
        assert auth.has_permission("test", "manage_alerts") is True
        assert auth.has_permission("test", "nonexistent") is False

        # Nonexistent user
        assert auth.has_permission("nonexistent", "view_logs") is False

    def test_create_session(self):
        """Test creating a session."""
        auth = DashboardAuth(session_expiry=3600)

        # Create session
        session_data = auth.create_session("test")

        # Check session data
        assert session_data["username"] == "test"
        assert isinstance(session_data["created_at"], int)
        assert isinstance(session_data["expires_at"], int)
        assert session_data["expires_at"] - session_data["created_at"] == 3600

    def test_validate_session(self):
        """Test validating a session."""
        auth = DashboardAuth()

        # Add user
        user = User(
            username="test",
            password_hash="hash",
        )
        auth.add_user(user)

        # Create valid session
        now = int(time.time())
        session_data = {
            "username": "test",
            "created_at": now,
            "expires_at": now + 3600,
        }

        # Valid session
        assert auth.validate_session(session_data) is True

        # Expired session
        expired_session = {
            "username": "test",
            "created_at": now - 7200,
            "expires_at": now - 3600,
        }
        assert auth.validate_session(expired_session) is False

        # Nonexistent user
        nonexistent_session = {
            "username": "nonexistent",
            "created_at": now,
            "expires_at": now + 3600,
        }
        assert auth.validate_session(nonexistent_session) is False

        # Inactive user
        user.is_active = False
        assert auth.validate_session(session_data) is False

        # Invalid session data
        assert auth.validate_session(None) is False
        assert auth.validate_session({}) is False
        assert auth.validate_session({"username": "test"}) is False

    def test_enable_rate_limiting(self):
        """Test enabling rate limiting."""
        auth = DashboardAuth()

        # Enable rate limiting
        auth.enable_rate_limiting(max_attempts=5, lockout_time=300)

        # Check if rate limiting is enabled
        assert auth.rate_limiting_enabled is True
        assert auth.max_auth_attempts == 5
        assert auth.lockout_time == 300

    def test_enable_csrf_protection(self):
        """Test enabling CSRF protection."""
        auth = DashboardAuth()

        # Enable CSRF protection
        auth.enable_csrf_protection()

        # Check if CSRF protection is enabled
        assert auth.csrf_protection_enabled is True

    def test_enable_audit_logging(self):
        """Test enabling audit logging."""
        auth = DashboardAuth()

        # Enable audit logging
        auth.enable_audit_logging()

        # Check if audit logging is enabled
        assert auth.audit_logging_enabled is True

    def test_check_rate_limit(self):
        """Test checking rate limit."""
        auth = DashboardAuth()

        # Without rate limiting
        assert auth.check_rate_limit("test") is True

        # Enable rate limiting
        auth.enable_rate_limiting(max_attempts=3, lockout_time=300)

        # Check rate limit for user with no failed attempts
        assert auth.check_rate_limit("test") is True

        # Add failed attempts
        auth.failed_attempts["test"] = 2
        assert auth.check_rate_limit("test") is True

        # Lock out user
        auth.lockout_until["test"] = time.time() + 300
        assert auth.check_rate_limit("test") is False

    def test_record_failed_attempt(self):
        """Test recording failed attempts."""
        auth = DashboardAuth()

        # Enable rate limiting
        auth.enable_rate_limiting(max_attempts=3, lockout_time=300)

        # Record failed attempts
        auth.record_failed_attempt("test")
        assert auth.failed_attempts.get("test") == 1

        auth.record_failed_attempt("test")
        assert auth.failed_attempts.get("test") == 2

        # Record one more to trigger lockout
        auth.record_failed_attempt("test")
        assert auth.failed_attempts.get("test") == 3
        assert "test" in auth.lockout_until
        assert auth.lockout_until["test"] > time.time()

    def test_reset_failed_attempts(self):
        """Test resetting failed attempts."""
        auth = DashboardAuth()

        # Enable rate limiting
        auth.enable_rate_limiting(max_attempts=3, lockout_time=300)

        # Add failed attempts and lockout
        auth.failed_attempts["test"] = 3
        auth.lockout_until["test"] = time.time() + 300

        # Reset failed attempts
        auth.reset_failed_attempts("test")
        assert "test" not in auth.failed_attempts
        assert "test" not in auth.lockout_until

    def test_generate_csrf_token(self):
        """Test generating CSRF token."""
        auth = DashboardAuth()

        # Without CSRF protection
        token = auth.generate_csrf_token("session_id")
        assert token == ""

        # Enable CSRF protection
        auth.enable_csrf_protection()

        # Generate token
        token = auth.generate_csrf_token("session_id")
        assert token != ""
        assert len(token) == 64  # 32 bytes as hex
        assert "session_id" in auth.csrf_tokens
        assert auth.csrf_tokens["session_id"] == token

    def test_validate_csrf_token(self):
        """Test validating CSRF token."""
        auth = DashboardAuth()

        # Without CSRF protection
        assert auth.validate_csrf_token("session_id", "token") is True

        # Enable CSRF protection
        auth.enable_csrf_protection()

        # Generate token
        token = auth.generate_csrf_token("session_id")

        # Validate token
        assert auth.validate_csrf_token("session_id", token) is True
        assert auth.validate_csrf_token("session_id", "invalid") is False
        assert auth.validate_csrf_token("invalid", token) is False

    def test_log_audit_event(self):
        """Test logging audit events."""
        auth = DashboardAuth()

        # Without audit logging
        auth.log_audit_event("test_event", "test_user", {"test": "data"})
        assert len(auth.audit_logs) == 0

        # Enable audit logging
        auth.enable_audit_logging()

        # Log event
        auth.log_audit_event("test_event", "test_user", {"test": "data"})
        assert len(auth.audit_logs) == 1
        assert auth.audit_logs[0]["event_type"] == "test_event"
        assert auth.audit_logs[0]["username"] == "test_user"
        assert auth.audit_logs[0]["details"] == {"test": "data"}

    def test_get_audit_logs(self):
        """Test getting audit logs."""
        auth = DashboardAuth()

        # Enable audit logging
        auth.enable_audit_logging()

        # Log events
        auth.log_audit_event("event1", "user1", {})
        auth.log_audit_event("event2", "user2", {})
        auth.log_audit_event("event1", "user2", {})

        # Get all logs
        logs = auth.get_audit_logs()
        assert len(logs) == 3

        # Filter by event type
        logs = auth.get_audit_logs(event_type="event1")
        assert len(logs) == 2
        assert all(log["event_type"] == "event1" for log in logs)

        # Filter by username
        logs = auth.get_audit_logs(username="user2")
        assert len(logs) == 2
        assert all(log["username"] == "user2" for log in logs)

        # Filter by both
        logs = auth.get_audit_logs(event_type="event1", username="user2")
        assert len(logs) == 1
        assert logs[0]["event_type"] == "event1"
        assert logs[0]["username"] == "user2"


class TestDecorators:
    """Test suite for decorator functions."""

    def test_require_auth(self):
        """Test require_auth decorator."""
        # Create mock function
        mock_func = MagicMock(return_value="result")

        # Apply decorator
        decorated_func = require_auth(mock_func)

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.outputs = [{"id": MagicMock()}]
        mock_ctx.outputs[0]["id"].split.return_value = [MagicMock()]
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app = MagicMock()
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth = MagicMock()

        # Mock session
        mock_session = {"auth": {"username": "test"}}

        # Test authenticated
        with patch("dash.callback_context", mock_ctx), \
             patch("common_utils.logging.dashboard_auth.session", mock_session):
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.validate_session.return_value = True
            result = decorated_func("arg1", "arg2", kwarg1="value1")
            assert result == "result"
            mock_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")

        # Test not authenticated
        mock_func.reset_mock()
        with patch("dash.callback_context", mock_ctx), \
             patch("common_utils.logging.dashboard_auth.session", mock_session):
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.validate_session.return_value = False
            with pytest.raises(PreventUpdate):
                decorated_func("arg1", "arg2", kwarg1="value1")
            mock_func.assert_not_called()

    def test_require_permission(self):
        """Test require_permission decorator."""
        # Create mock function
        mock_func = MagicMock(return_value="result")
        mock_func.__name__ = "mock_func"

        # Apply decorator
        decorated_func = require_permission("view_logs")(mock_func)

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.outputs = [{"id": MagicMock()}]
        mock_ctx.outputs[0]["id"].split.return_value = [MagicMock()]
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app = MagicMock()
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth = MagicMock()
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.audit_logging_enabled = True

        # Mock session
        mock_session = {"auth": {"username": "test"}}

        # Test authenticated with permission
        with patch("dash.callback_context", mock_ctx), \
             patch("common_utils.logging.dashboard_auth.session", mock_session):
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.validate_session.return_value = True
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.has_permission.return_value = True
            result = decorated_func("arg1", "arg2", kwarg1="value1")
            assert result == "result"
            mock_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.has_permission.assert_called_once_with("test", "view_logs")
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.log_audit_event.assert_called_with(
                "permission_granted", "test", {"permission": "view_logs", "callback": "mock_func"}
            )

        # Test authenticated without permission
        mock_func.reset_mock()
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.log_audit_event.reset_mock()
        with patch("dash.callback_context", mock_ctx), \
             patch("common_utils.logging.dashboard_auth.session", mock_session):
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.validate_session.return_value = True
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.has_permission.return_value = False
            with pytest.raises(PreventUpdate):
                decorated_func("arg1", "arg2", kwarg1="value1")
            mock_func.assert_not_called()
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.log_audit_event.assert_called_with(
                "permission_denied", "test", {"permission": "view_logs", "callback": "mock_func"}
            )

        # Test not authenticated
        mock_func.reset_mock()
        mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.log_audit_event.reset_mock()
        with patch("dash.callback_context", mock_ctx), \
             patch("common_utils.logging.dashboard_auth.session", mock_session):
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.validate_session.return_value = False
            with pytest.raises(PreventUpdate):
                decorated_func("arg1", "arg2", kwarg1="value1")
            mock_func.assert_not_called()
            mock_ctx.outputs[0]["id"].split.return_value[0]._dash_app.auth.log_audit_event.assert_called_with(
                "permission_check_failed", "test", {"permission": "view_logs", "reason": "not_authenticated", "callback": "mock_func"}
            )
