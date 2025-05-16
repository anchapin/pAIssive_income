"""Tests for coverage of flask_user_router.py."""

import json
import logging
from unittest.mock import patch, MagicMock

import pytest
from flask import Blueprint

from api.routes.flask_user_router import user_bp, user_service
from app_flask import create_app, db
from app_flask.models import User


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    app = create_app(test_config)

    # Register the blueprint with a different name to avoid duplicate route name issue
    app.register_blueprint(user_bp, name="test_user_bp_coverage")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


class TestFlaskUserRouterCoverage:
    """Tests for coverage of flask_user_router.py."""

    def test_get_users_error(self, client, app, caplog):
        """Test error handling in get_users endpoint."""
        # Set up logging capture
        caplog.set_level(logging.ERROR)

        # Mock User.query.all to raise an exception
        with patch('api.routes.flask_user_router.User.query') as mock_query:
            mock_query.all.side_effect = Exception("Database error")

            # Test the endpoint
            response = client.get('/api/users/')

            # Verify response
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "An error occurred" in data["error"]

            # Verify logging
            assert "Error getting users" in caplog.text

    def test_create_user_missing_json(self, client):
        """Test create_user with missing JSON data."""
        # Test with no JSON content
        response = client.post('/api/users/')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No data provided" in data["error"]

    def test_create_user_empty_json(self, client):
        """Test create_user with empty JSON data."""
        # Test with empty JSON
        response = client.post('/api/users/', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No data provided" in data["error"]

    def test_create_user_missing_fields(self, client):
        """Test create_user with missing fields."""
        # Test with partial data
        response = client.post('/api/users/', json={"username": "testuser"})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Missing required fields" in data["error"]

    def test_create_user_runtime_error(self, client):
        """Test create_user with RuntimeError."""
        with patch('api.routes.flask_user_router.user_service.create_user') as mock_create:
            mock_create.side_effect = RuntimeError("Server error")

            response = client.post(
                '/api/users/',
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "An error occurred" in data["error"]

    def test_create_user_validation_error(self, client):
        """Test create_user with validation error."""
        with patch('api.routes.flask_user_router.user_service.create_user') as mock_create:
            mock_create.side_effect = ValueError("Invalid input")

            response = client.post(
                '/api/users/',
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "Invalid input" in data["error"]

    def test_create_user_validation_error_with_message(self, client):
        """Test validation error handling in create_user endpoint with custom message."""
        # Create a custom exception with a message attribute
        class ValidationError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        # Mock the user service to raise the custom exception
        with patch('api.routes.flask_user_router.user_service.create_user') as mock_create_user:
            # Use a message that contains one of the safe terms
            mock_create_user.side_effect = ValidationError("Custom validation must be valid")

            # Test the endpoint
            response = client.post(
                '/api/users/',
                json={
                    'username': 'newuser',
                    'email': 'new@example.com',
                    'password': 'password123'
                }
            )

            # Verify response
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "must be" in data["error"]

    def test_create_user_validation_error_with_safe_terms(self, client):
        """Test validation error handling with safe terms in the error message."""
        # Create a custom exception with a message attribute
        class ValidationError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        # Mock the user service to raise an exception with safe terms
        with patch('api.routes.flask_user_router.user_service.create_user') as mock_create_user:
            # Use a message that contains one of the safe terms
            mock_create_user.side_effect = ValidationError("Email already exists")

            # Test the endpoint
            response = client.post(
                '/api/users/',
                json={
                    'username': 'newuser',
                    'email': 'new@example.com',
                    'password': 'password123'
                }
            )

            # Verify response
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "already exists" in data["error"]

    def test_authenticate_user_missing_json(self, client):
        """Test authenticate_user with missing JSON data."""
        # Test with no JSON content
        response = client.post('/api/users/authenticate')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No data provided" in data["error"]

    def test_authenticate_user_empty_json(self, client):
        """Test authenticate_user with empty JSON data."""
        # Test with empty JSON
        response = client.post('/api/users/authenticate', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No data provided" in data["error"]

    def test_authenticate_user_missing_fields(self, client):
        """Test authenticate_user with missing fields."""
        # Test with partial data
        response = client.post('/api/users/authenticate', json={"username_or_email": "testuser"})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Missing required fields" in data["error"]

    def test_authenticate_user_server_error(self, client, caplog):
        """Test authenticate_user with server error."""
        caplog.set_level(logging.ERROR)

        with patch('api.routes.flask_user_router.user_service.authenticate_user') as mock_auth:
            mock_auth.side_effect = Exception("Server error")

            response = client.post(
                '/api/users/authenticate',
                json={
                    "username_or_email": "testuser",
                    "password": "password123"
                }
            )
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "An error occurred" in data["error"]

            # Verify logging
            assert "Error authenticating user" in caplog.text

    def test_update_user_missing_json(self, client, app):
        """Test update_user with missing JSON data."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Test with no JSON content
        response = client.put(f'/api/users/{user_id}')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No data provided" in data["error"]

    def test_update_user_empty_json(self, client, app):
        """Test update_user with empty JSON data."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Test with empty JSON
        response = client.put(f'/api/users/{user_id}', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No data provided" in data["error"]

    def test_update_user_server_error(self, client, app, caplog):
        """Test update_user with server error."""
        caplog.set_level(logging.ERROR)

        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Mock db.session.commit to raise an exception
        with patch('api.routes.flask_user_router.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            response = client.put(
                f'/api/users/{user_id}',
                json={"username": "updateduser"}
            )
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "An error occurred" in data["error"]

            # Verify logging
            assert "Error updating user" in caplog.text
