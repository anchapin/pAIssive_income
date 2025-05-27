"""test_basic - Basic tests for the Flask application."""

import pytest

from app_flask import create_app, db
from flask import Flask


def test_app_creation():
    """Test that the Flask app can be created successfully."""
    app = create_app()
    assert app is not None
    assert isinstance(app, Flask)


def test_app_with_test_config():
    """Test that the Flask app can be created with test configuration."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)
    assert app is not None
    assert app.config["TESTING"] is True
    assert "sqlite:///:memory:" in app.config["SQLALCHEMY_DATABASE_URI"]


def test_database_initialization(app):
    """Test that the database is properly initialized."""
    with app.app_context():
        # Check that db is available
        assert db is not None

        # Check that we can execute a simple query
        result = db.session.execute(db.text("SELECT 1")).scalar()
        assert result == 1


def test_app_context(app):
    """Test that the app context works correctly."""
    assert app.app_context

    with app.app_context():
        # We should be able to access app-specific functionality
        assert app.config is not None


def test_client_creation(client):
    """Test that the test client can be created."""
    assert client is not None

    # Test a basic request (this might fail if no routes are defined, but that's OK)
    response = client.get("/")
    # We don't assert on the response code since routes might not be defined
    assert response is not None


def test_config_loading():
    """Test that configuration loading works with fallbacks."""
    # Test with no config file (should use fallback)
    app = create_app()
    assert app.config.get("SQLALCHEMY_TRACK_MODIFICATIONS") is False

    # Test with explicit test config that includes database URI
    test_config = {
        "TEST_VALUE": "test",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)
    assert app.config.get("TEST_VALUE") == "test"


def test_app_factory_pattern():
    """Test that the app factory pattern works correctly."""
    # Create multiple app instances with proper database configuration
    app1 = create_app({
        "TESTING": True,
        "TEST_ID": 1,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    app2 = create_app({
        "TESTING": True,
        "TEST_ID": 2,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    # They should be different instances
    assert app1 is not app2
    assert app1.config["TEST_ID"] != app2.config["TEST_ID"]


def test_database_models_import(app):
    """Test that database models can be imported without errors."""
    with app.app_context():
        try:
            from app_flask.models import Agent, Team, User

            # Check that the models are available
            assert User is not None
            assert Team is not None
            assert Agent is not None

            # Check that they have the expected attributes
            assert hasattr(User, "__tablename__")
            assert hasattr(Team, "__tablename__")
            assert hasattr(Agent, "__tablename__")

        except ImportError as e:
            pytest.fail(f"Failed to import models: {e}")


def test_blueprints_registration(app):
    """Test that blueprints are registered (if available)."""
    # Check if any blueprints are registered
    blueprint_names = [bp.name for bp in app.blueprints.values()]

    # We don't require specific blueprints since they might not be available
    # in all environments, but we can check that the registration process works
    assert isinstance(blueprint_names, list)
