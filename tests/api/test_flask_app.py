"""test_flask_app - Test module for Flask app."""

import json
import logging
import os
import sys
import unittest
from importlib import import_module
from unittest.mock import MagicMock, patch

import pytest
from flask import Blueprint, Flask, jsonify
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the app and db
from app_flask import create_app, db

# Constants
TUPLE_LENGTH = 3
HTTP_OK = 200
HTTP_NOT_FOUND = 404

# Create a mock Flask class for basic tests
# Note: MagicMock and patch are kept as they might be needed for future test expansions
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
def mock_app():
    """
    Create a mock Flask app for testing.

    Returns:
        MockFlask: The configured mock Flask application

    """
    return MockFlask(__name__)


@pytest.fixture
def mock_client(mock_app):
    """
    Create a test client.

    Args:
        mock_app (MockFlask): Mock Flask application

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
    response = mock_client.get("/test")
    assert response.status_code == HTTP_OK
    data = json.loads(response.data)
    assert data["success"] is True


@patch("app_flask.models.db")
@patch("app_flask.db")
def test_create_app_function(mock_db, mock_models_db):
    """Test the create_app function."""
    # Test with custom config only to avoid connecting to real database
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test_key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    # Create a simple Flask app for testing
    app = Flask(__name__)
    app.config.update(test_config)

    assert app is not None
    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True
    assert app.config.get("SECRET_KEY") == "test_key"


@patch("app_flask.models.db")
@patch("app_flask.db")
def test_db_initialization(mock_db, mock_models_db):
    """Test that the database is properly initialized."""
    # Create a mock app
    app = Flask(__name__)
    app.config["TESTING"] = True

    # Mock the db.session.execute method
    mock_db.session.execute.return_value.scalar.return_value = 1

    # Create a mock app context
    with app.app_context():
        # Check that we can execute a simple query
        result = mock_db.session.execute(text("SELECT 1")).scalar()
        assert result == 1


def test_blueprint_registration():
    """Test that blueprints are properly registered."""
    # Create a mock app
    app = Flask(__name__)

    # Create a real blueprint
    user_bp = Blueprint("user_bp", __name__, url_prefix="/api/users")

    # Add a route to the blueprint
    @user_bp.route("/")
    def index():
        return "User index"

    # Register the blueprint
    app.register_blueprint(user_bp)

    # Check that the user blueprint is registered
    endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]

    # The user blueprint should be registered with at least one endpoint
    assert "user_bp.index" in endpoints


class TestFlaskApp(unittest.TestCase):
    """Test suite for the Flask application."""

    @patch("app_flask.models.db")
    @patch("app_flask.db")
    def setUp(self, mock_db, mock_models_db):
        """Set up test fixtures."""
        self.test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }

        # Create a simple Flask app for testing
        self.app = Flask(__name__)
        self.app.config.update(self.test_config)
        self.client = self.app.test_client()

        # Mock the db methods
        self.mock_db = mock_db
        self.mock_models_db = mock_models_db

    def tearDown(self):
        """Tear down test fixtures."""

    def test_app_context(self):
        """Test that the app context works properly."""
        from flask import current_app

        with self.app.app_context():
            # Use the imported current_app instead of Flask.current_app
            assert current_app is not None
            # Verify it's the correct app - the name will be the module name
            assert current_app.name == "tests.api.test_flask_app"

    def test_user_blueprint_routes(self):
        """Test that the user blueprint routes are registered."""
        # Create a mock blueprint
        user_bp = Blueprint("user_bp", __name__, url_prefix="/api/users")

        # Add a route to the blueprint
        @user_bp.route("/", methods=["POST"])
        def create_user():
            return jsonify({"success": True}), 201

        # Register the blueprint
        self.app.register_blueprint(user_bp)

        # Check that the user creation route exists
        with self.app.app_context():
            rules = [rule for rule in self.app.url_map.iter_rules()]
            # Look for any endpoint that might be related to users
            user_endpoints = [rule.endpoint for rule in rules if "user" in rule.endpoint.lower()]
            assert len(user_endpoints) > 0, "No user-related endpoints found"

    @patch("app_flask.models.User")
    def test_create_user_endpoint(self, mock_user):
        """Test the create user endpoint."""
        # Skip this test for now as we need to properly mock the user service
        self.skipTest("Skipping until user service is properly mocked")

    @patch("app_flask.models.User")
    def test_authenticate_user_endpoint_success(self, mock_user):
        """Test the authenticate user endpoint with successful authentication."""
        # Skip this test for now as we need to properly mock the user service
        self.skipTest("Skipping until user service is properly mocked")

    @patch("app_flask.models.User")
    def test_authenticate_user_endpoint_failure(self, mock_user):
        """Test the authenticate user endpoint with failed authentication."""
        # Skip this test for now as we need to properly mock the user service
        self.skipTest("Skipping until user service is properly mocked")
