"""Tests for security fixes in flask_user_router.py."""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from flask import Blueprint

from api.routes.flask_user_router import user_bp
from app_flask import create_app, db
from app_flask.models import User


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    }
    app = create_app(test_config)

    # Register the blueprint with a different name to avoid duplicate route name issue
    app.register_blueprint(user_bp, name="test_user_bp")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


class TestFlaskUserRouterSecurity:
    """Tests for security fixes in flask_user_router.py."""

    def test_get_user_no_log_injection(self, client, app, caplog):
        """Test that user_id is not directly included in log messages."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Set up logging capture
        caplog.set_level(logging.INFO)

        # Create a malicious user_id that could be used for log injection
        malicious_id = f"{user_id}\n\nERROR: Injected log message"

        # Test the endpoint with the malicious ID
        with patch("api.routes.flask_user_router.User.query") as mock_query:
            mock_query.get.side_effect = Exception("Test exception")

            response = client.get(f"/api/users/{malicious_id}")
            assert response.status_code == 500

            # Check that the malicious ID is not directly included in any log messages
            for record in caplog.records:
                assert malicious_id not in record.getMessage()
                # But we should see the sanitized log message
                if "Error getting user" in record.getMessage():
                    assert "Injected log message" not in record.getMessage()

            # Check for the INFO level log message with the user_id
            found_log = False
            for record in caplog.records:
                if record.levelno == logging.INFO and "Failed user_id" in record.getMessage():
                    found_log = True
                    break
            assert found_log, "Expected INFO log with 'Failed user_id' not found"

    def test_update_user_no_log_injection(self, client, app, caplog):
        """Test that user_id is not directly included in log messages for update_user."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Set up logging capture
        caplog.set_level(logging.INFO)

        # Test the endpoint with a valid ID but force an exception
        with patch("api.routes.flask_user_router.User.query.get") as mock_get:
            # Mock the user query to return a valid user
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_get.return_value = mock_user

            # Mock the commit to raise an exception
            with patch("api.routes.flask_user_router.db.session.commit") as mock_commit:
                mock_commit.side_effect = Exception("Test exception")

                response = client.put(
                    f"/api/users/{user_id}",
                    json={"username": "updateduser"}
                )
                assert response.status_code == 500

                # Check that the log messages don't contain any injection patterns
                for record in caplog.records:
                    if "Error updating user" in record.getMessage():
                        # Verify we're not using f-strings with user input
                        assert f"Error updating user {user_id}" not in record.getMessage()

                # Check for the INFO level log message with the user_id
                found_log = False
                for record in caplog.records:
                    if record.levelno == logging.INFO and "Failed user_id" in record.getMessage():
                        found_log = True
                        break
                assert found_log, "Expected INFO log with 'Failed user_id' not found"

    def test_delete_user_no_log_injection(self, client, app, caplog):
        """Test that user_id is not directly included in log messages for delete_user."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Set up logging capture
        caplog.set_level(logging.INFO)

        # Test the endpoint with a valid ID but force an exception
        with patch("api.routes.flask_user_router.User.query.get") as mock_get:
            # Mock the user query to return a valid user
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_get.return_value = mock_user

            # Mock the commit to raise an exception
            with patch("api.routes.flask_user_router.db.session.commit") as mock_commit:
                mock_commit.side_effect = Exception("Test exception")

                response = client.delete(f"/api/users/{user_id}")
                assert response.status_code == 500

                # Check that the log messages don't contain any injection patterns
                for record in caplog.records:
                    if "Error deleting user" in record.getMessage():
                        # Verify we're not using f-strings with user input
                        assert f"Error deleting user {user_id}" not in record.getMessage()

                # Check for the INFO level log message with the user_id
                found_log = False
                for record in caplog.records:
                    if record.levelno == logging.INFO and "Failed user_id" in record.getMessage():
                        found_log = True
                        break
                assert found_log, "Expected INFO log with 'Failed user_id' not found"

    def test_create_user_no_exception_exposure(self, client, app):
        """Test that exception details are not exposed to users."""
        # Test the endpoint with valid data but force an exception
        with patch("api.routes.flask_user_router.user_service.create_user") as mock_create_user:
            # Create a sensitive exception message that should not be exposed
            sensitive_message = "Database connection failed: password=secret123"
            mock_create_user.side_effect = Exception(sensitive_message)

            response = client.post(
                "/api/users/",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "password123"
                }
            )
            assert response.status_code == 400

            # Check that the response does not contain the sensitive exception message
            data = json.loads(response.data)
            assert "error" in data
            assert sensitive_message not in data["error"]
            assert "secret123" not in data["error"]
            # Should use a safe error message instead
            assert data["error"] == "Invalid input data"
