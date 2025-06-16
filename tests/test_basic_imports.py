"""Test basic imports and module initialization."""

import pytest


def test_ai_models_import():
    """Test that ai_models module can be imported."""
    import ai_models
    assert ai_models is not None


def test_ai_models_version():
    """Test that ai_models version is accessible."""
    from ai_models.version import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_config_import():
    """Test that config module can be imported."""
    import config
    assert config is not None


def test_utils_import():
    """Test that utils module can be imported."""
    import utils
    assert utils is not None


def test_utils_math_utils():
    """Test basic math utils functions."""
    from utils.math_utils import add, average, divide, multiply, subtract

    # Test add
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

    # Test multiply
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 5) == 0

    # Test subtract
    assert subtract(5, 3) == 2
    assert subtract(0, 0) == 0

    # Test divide
    assert divide(6, 2) == 3
    assert divide(5, 2) == 2.5

    # Test average
    assert average([1, 2, 3, 4, 5]) == 3.0
    assert average([10, 20]) == 15.0


def test_users_models_import():
    """Test that users models can be imported."""
    from users.models import User
    assert User is not None


def test_users_models_user_creation():
    """Test basic User model functionality."""
    from users.models import User

    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_app_flask_database():
    """Test app_flask database module."""
    from app_flask.database import db
    assert db is not None


def test_app_flask_database():
    """Test app_flask database module."""
    from app_flask.database import db
    assert db is not None


def test_common_utils_validation():
    """Test common_utils validation."""
    from common_utils.validation import ValidationError
    assert ValidationError is not None


def test_crewai_import():
    """Test crewai module import."""
    import crewai
    assert crewai is not None


def test_config_basic():
    """Test config module basic functionality."""
    import config
    assert config is not None
