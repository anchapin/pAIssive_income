"""Tests for the Flask user router."""

import json
import copy
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

    # Simply register the blueprint with a different name
    # This avoids the duplicate route name issue
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


class TestFlaskUserRouter:
    """Tests for the Flask user router."""

    def test_get_users(self, client, app):
        """Test getting all users."""
        # Create test users
        with app.app_context():
            user1 = User(username="testuser1", email="test1@example.com", password_hash="hash1")
            user2 = User(username="testuser2", email="test2@example.com", password_hash="hash2")
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

        # Test the endpoint
        response = client.get('/api/users/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['username'] == 'testuser1'
        assert data[1]['username'] == 'testuser2'

    def test_get_users_error(self, client, app):
        """Test getting all users with an error."""
        with patch('api.routes.flask_user_router.User.query') as mock_query:
            mock_query.all.side_effect = Exception("Database error")

            response = client.get('/api/users/')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'An error occurred while getting users'

    def test_get_user(self, client, app):
        """Test getting a user by ID."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Test the endpoint
        response = client.get(f'/api/users/{user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'

    def test_get_user_not_found(self, client):
        """Test getting a non-existent user."""
        response = client.get('/api/users/00000000-0000-0000-0000-000000000000')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_user_error(self, client, app):
        """Test getting a user with an error."""
        with patch('api.routes.flask_user_router.User.query') as mock_query:
            mock_query.get.side_effect = Exception("Database error")

            response = client.get('/api/users/00000000-0000-0000-0000-000000000000')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'An error occurred while getting the user'

    def test_create_user(self, client):
        """Test creating a user."""
        with patch('api.routes.flask_user_router.user_service') as mock_service:
            mock_service.create_user.return_value = {
                'id': 1,
                'username': 'newuser',
                'email': 'new@example.com',
                'is_active': True
            }

            response = client.post(
                '/api/users/',
                json={
                    'username': 'newuser',
                    'email': 'new@example.com',
                    'password': 'password123'
                }
            )
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['username'] == 'newuser'
            assert data['email'] == 'new@example.com'

            mock_service.create_user.assert_called_once_with(
                'newuser', 'new@example.com', 'password123'
            )

    def test_create_user_no_data(self, client):
        """Test creating a user with no data."""
        response = client.post('/api/users/')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'No data provided'

    def test_create_user_missing_fields(self, client):
        """Test creating a user with missing fields."""
        response = client.post(
            '/api/users/',
            json={
                'username': 'newuser',
                'email': 'new@example.com'
                # Missing password
            }
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Missing required fields'

    def test_create_user_service_error(self, client):
        """Test creating a user with a service error."""
        # Create a custom exception with a message attribute
        class ValidationError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        with patch('api.routes.flask_user_router.user_service') as mock_service:
            # Use a message that contains one of the safe terms
            mock_service.create_user.side_effect = ValidationError("User already exists")

            response = client.post(
                '/api/users/',
                json={
                    'username': 'newuser',
                    'email': 'new@example.com',
                    'password': 'password123'
                }
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert "already exists" in data['error']

    def test_create_user_server_error(self, client):
        """Test creating a user with a server error."""
        # Instead of mocking Flask's request object (which is difficult in tests),
        # we'll test the server error by causing an exception in the service layer
        with patch('api.routes.flask_user_router.user_service.create_user') as mock_create_user:
            # Make the service throw an unexpected exception (not a validation error)
            mock_create_user.side_effect = RuntimeError("Unexpected server error")

            # Send a valid request that will trigger the server error in the service
            response = client.post(
                '/api/users/',
                json={
                    'username': 'newuser',
                    'email': 'new@example.com',
                    'password': 'password123'
                }
            )

            # The route should catch this and return a 500 error
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'An error occurred while creating the user'

    def test_authenticate_user_success(self, client):
        """Test authenticating a user successfully."""
        with patch('api.routes.flask_user_router.user_service') as mock_service:
            mock_service.authenticate_user.return_value = (
                True,
                {
                    'id': 1,
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'is_active': True
                }
            )
            mock_service.generate_token.return_value = "test-token"

            response = client.post(
                '/api/users/authenticate',
                json={
                    'username_or_email': 'testuser',
                    'password': 'password123'
                }
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['token'] == 'test-token'
            assert data['user']['username'] == 'testuser'

            mock_service.authenticate_user.assert_called_once_with(
                'testuser', 'password123'
            )
            mock_service.generate_token.assert_called_once()

    def test_authenticate_user_no_data(self, client):
        """Test authenticating a user with no data."""
        response = client.post('/api/users/authenticate')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'No data provided'

    def test_authenticate_user_missing_fields(self, client):
        """Test authenticating a user with missing fields."""
        response = client.post(
            '/api/users/authenticate',
            json={
                'username_or_email': 'testuser'
                # Missing password
            }
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Missing required fields'

    def test_authenticate_user_invalid_credentials(self, client):
        """Test authenticating a user with invalid credentials."""
        with patch('api.routes.flask_user_router.user_service') as mock_service:
            mock_service.authenticate_user.return_value = (False, None)

            response = client.post(
                '/api/users/authenticate',
                json={
                    'username_or_email': 'testuser',
                    'password': 'wrong-password'
                }
            )
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Invalid credentials'

    def test_authenticate_user_error(self, client):
        """Test authenticating a user with an error."""
        with patch('api.routes.flask_user_router.user_service') as mock_service:
            mock_service.authenticate_user.side_effect = Exception("Database error")

            response = client.post(
                '/api/users/authenticate',
                json={
                    'username_or_email': 'testuser',
                    'password': 'password123'
                }
            )
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'An error occurred while authenticating the user'

    def test_update_user(self, client, app):
        """Test updating a user."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Test the endpoint
        response = client.put(
            f'/api/users/{user_id}',
            json={
                'username': 'updateduser',
                'email': 'updated@example.com',
                'is_active': False
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'updateduser'
        assert data['email'] == 'updated@example.com'
        assert data['is_active'] is False

        # Verify the user was updated in the database
        with app.app_context():
            updated_user = User.query.get(user_id)
            assert updated_user.username == 'updateduser'
            assert updated_user.email == 'updated@example.com'
            assert updated_user.is_active == "false"

    def test_update_user_not_found(self, client):
        """Test updating a non-existent user."""
        response = client.put(
            '/api/users/00000000-0000-0000-0000-000000000000',
            json={
                'username': 'updateduser',
                'email': 'updated@example.com'
            }
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error']

    def test_update_user_no_data(self, client, app):
        """Test updating a user with no data."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        response = client.put(f'/api/users/{user_id}')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'No data provided'

    def test_update_user_error(self, client, app):
        """Test updating a user with an error."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        with patch('api.routes.flask_user_router.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            response = client.put(
                f'/api/users/{user_id}',
                json={
                    'username': 'updateduser',
                    'email': 'updated@example.com'
                }
            )
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'An error occurred while updating the user'

    def test_delete_user(self, client, app):
        """Test deleting a user."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Test the endpoint
        response = client.delete(f'/api/users/{user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'deleted successfully' in data['message']

        # Verify the user was deleted from the database
        with app.app_context():
            deleted_user = User.query.get(user_id)
            assert deleted_user is None

    def test_delete_user_not_found(self, client):
        """Test deleting a non-existent user."""
        response = client.delete('/api/users/00000000-0000-0000-0000-000000000000')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error']

    def test_delete_user_error(self, client, app):
        """Test deleting a user with an error."""
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        with patch('api.routes.flask_user_router.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            response = client.delete(f'/api/users/{user_id}')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'An error occurred while deleting the user'
