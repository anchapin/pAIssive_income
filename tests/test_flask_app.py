"""test_flask_app - Test module for Flask app."""

import json
import unittest
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

# Constants
TUPLE_LENGTH = 3
HTTP_OK = 200
HTTP_NOT_FOUND = 404

# Note: MagicMock and patch are not used in this file but are kept
# as they might be needed for future test expansions


# Create a mock Flask class to avoid import issues
class MockFlask:
    def __init__(self, name):
        self.name = name
        self.routes = {}
        self.config = {}
        self.blueprints = {}

    def route(self, path, **_kwargs):
        def decorator(func):
            self.routes[path] = func
            return func

        return decorator

    def test_client(self):
        return MockClient(self)

    def register_blueprint(self, blueprint, **_kwargs):
        self.blueprints[blueprint.name] = blueprint


class MockClient:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        if path in self.app.routes:
            result = self.app.routes[path]()
            if isinstance(result, tuple) and len(result) == TUPLE_LENGTH:
                data, status_code, headers = result
                return MockResponse(data, status_code, headers)
        return MockResponse('{"error": "Not found"}', HTTP_NOT_FOUND, {})

    def post(self, path, json=None):
        if path in self.app.routes:
            result = self.app.routes[path](json)
            if isinstance(result, tuple) and len(result) == 3:
                data, status_code, headers = result
                response = MockResponse(data, status_code, headers)
                return response
        return MockResponse('{"error": "Not found"}', 404, {})


class MockResponse:
    def __init__(self, data, status_code, headers):
        self.data = data.encode("utf-8") if isinstance(data, str) else data
        self.status_code = status_code
        self.headers = headers


@pytest.fixture
def app():
    """
    Create a mock Flask app for testing.

    Returns:
        MockFlask: The configured mock Flask application

    """
    return MockFlask(__name__)


@pytest.fixture
def client(app):
    """
    Create a test client.

    Args:
        mock_app: Mock Flask application

    Returns:
        MockClient: Test client for the mock Flask application

    """
    return mock_app.test_client()


@pytest.fixture
def app():
    """Create a real Flask app for testing with in-memory SQLite."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the real Flask app."""
    return app.test_client()


def test_flask_app_creation(mock_app):
    """Test that the Flask app is created successfully."""
    assert mock_app is not None
    assert isinstance(mock_app, MockFlask)


def test_flask_client_creation(mock_client):
    """Test that the Flask test client is created successfully."""
    assert mock_client is not None
    assert isinstance(mock_client, MockClient)


def test_flask_route(mock_app, mock_client):
    """Test adding a route to the Flask app."""

    # Add a test route
    @mock_app.route("/test")
    def test_route():
        return (
            json.dumps({"success": True}),
            HTTP_OK,
            {"ContentType": "application/json"},
        )

    # Test the route
    response = client.get("/test")
    assert response.status_code == HTTP_OK
    data = json.loads(response.data)
    assert data["success"] is True


def test_create_app_function():
    """Test the create_app function."""
    # Test with custom config only to avoid connecting to real database
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test_key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)
    assert app is not None
    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test_key"


def test_db_initialization(app):
    """Test that the database is properly initialized."""
    from sqlalchemy import text

    with app.app_context():
        # Check that we can execute a simple query
        # Use text() to properly format the SQL query
        result = db.session.execute(text("SELECT 1")).scalar()
        assert result == 1


def test_blueprint_registration(app):
    """Test that blueprints are properly registered."""
    # Check that the user blueprint is registered
    assert "user" in [rule.endpoint.split('.')[0] for rule in app.url_map.iter_rules()
                     if '.' in rule.endpoint]


class TestFlaskApp(unittest.TestCase):
    """Test suite for the Flask application."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
        self.app = create_app(self.test_config)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down test fixtures."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_app_context(self):
        """Test that the app context works properly."""
        from flask import current_app

        with self.app.app_context():
            # Use the imported current_app instead of Flask.current_app
            assert current_app is not None
            # Verify it's the correct app
            assert current_app.name == 'app_flask'

    def test_user_blueprint_routes(self):
        """Test that the user blueprint routes are registered."""
        # Check that the user creation route exists
        with self.app.app_context():
            rules = [rule for rule in self.app.url_map.iter_rules()
                    if rule.endpoint.startswith('user.')]
            assert any(rule.rule == '/api/users/' for rule in rules)
            assert any(rule.rule == '/api/users/authenticate' for rule in rules)

    @patch('users.services.UserService.create_user')
    def test_create_user_endpoint(self, mock_create_user):
        """Test the create user endpoint."""
        # Mock the create_user method
        mock_create_user.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
        }

        # Test the endpoint
        response = self.client.post(
            '/api/users/',
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

        # Verify the mock was called with the right arguments
        mock_create_user.assert_called_once_with(
            "testuser", "test@example.com", "password123"
        )

    @patch('users.services.UserService.authenticate_user')
    def test_authenticate_user_endpoint_success(self, mock_authenticate):
        """Test the authenticate user endpoint with successful authentication."""
        # Mock the authenticate_user method
        mock_authenticate.return_value = (True, {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
        })

        # Test the endpoint
        response = self.client.post(
            '/api/users/authenticate',
            json={
                "username_or_email": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"

        # Verify the mock was called with the right arguments
        mock_authenticate.assert_called_once_with(
            "testuser", "password123"
        )

    @patch('users.services.UserService.authenticate_user')
    def test_authenticate_user_endpoint_failure(self, mock_authenticate):
        """Test the authenticate user endpoint with failed authentication."""
        # Mock the authenticate_user method
        mock_authenticate.return_value = (False, None)

        # Test the endpoint
        response = self.client.post(
            '/api/users/authenticate',
            json={
                "username_or_email": "testuser",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "Invalid credentials"

        # Verify the mock was called with the right arguments
        mock_authenticate.assert_called_once_with(
            "testuser", "wrongpassword"
        )
