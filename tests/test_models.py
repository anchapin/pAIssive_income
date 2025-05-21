"""test_models - Test module for database models."""

import logging
from typing import Generator

import pytest
from flask.app import Flask  # Import actual Flask class
from flask.testing import FlaskClient

from app_flask import db
from app_flask.models import Agent, Team, User

# Constants
EXPECTED_AGENT_COUNT = 2


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config.update(
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()


def test_user_model(app: Flask) -> None:
    """Test the User model."""
    with app.app_context():
        # Create a user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",  # noqa: S106 - Test data only
        )
        db.session.add(user)
        db.session.commit()

        # Query the user
        queried_user = User.query.filter_by(username="testuser").first()
        assert queried_user is not None
        assert queried_user.username == "testuser"
        assert queried_user.email == "test@example.com"
        assert queried_user.password_hash == "hashed_password"  # noqa: S105 - Test data only

        # Test to_dict method
        user_dict = user.to_dict()
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert "password_hash" not in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict

        # Test from_dict method
        new_user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password_hash": "new_hash",
            "is_admin": True,
            "is_active": False
        }
        new_user = User.from_dict(new_user_data)
        assert new_user.username == "newuser"
        assert new_user.email == "new@example.com"
        assert new_user.password_hash == "new_hash"
        assert new_user.is_admin == "true"  # String-based boolean
        assert new_user.is_active == "false"  # String-based boolean

        # Test update_last_login method
        user.update_last_login()
        assert user.last_login is not None


def test_team_model(app: Flask) -> None:
    """Test the Team model."""
    with app.app_context():
        # Create a team
        team = Team(name="Test Team", description="A test team")
        db.session.add(team)
        db.session.commit()

        # Query the team
        queried_team = Team.query.filter_by(name="Test Team").first()
        assert queried_team is not None
        assert queried_team.name == "Test Team"
        assert queried_team.description == "A test team"


def test_agent_model(app: Flask) -> None:
    """Test the Agent model."""
    with app.app_context():
        # Create a team
        team = Team(name="Test Team", description="A test team")
        db.session.add(team)
        db.session.commit()

        # Create an agent
        agent = Agent(
            name="Test Agent",
            role="tester",
            description="A test agent",
            team_id=team.id,
        )
        db.session.add(agent)
        db.session.commit()

        # Query the agent
        queried_agent = Agent.query.filter_by(name="Test Agent").first()
        assert queried_agent is not None
        assert queried_agent.name == "Test Agent"
        assert queried_agent.role == "tester"
        assert queried_agent.description == "A test agent"
        assert queried_agent.team_id == team.id


def test_team_agent_relationship(app: Flask) -> None:
    """Test the relationship between Team and Agent models."""
    with app.app_context():
        # Create a team
        team = Team(name="Test Team", description="A test team")
        db.session.add(team)
        db.session.commit()

        # Create agents
        agent1 = Agent(
            name="Agent 1", role="role1", description="Agent 1 description", team=team
        )
        agent2 = Agent(
            name="Agent 2", role="role2", description="Agent 2 description", team=team
        )
        db.session.add_all([agent1, agent2])
        db.session.commit()

        # Query the team and check its agents
        queried_team = Team.query.filter_by(name="Test Team").first()
        assert len(queried_team.agents) == EXPECTED_AGENT_COUNT
        assert queried_team.agents[0].name in ["Agent 1", "Agent 2"]
        assert queried_team.agents[1].name in ["Agent 1", "Agent 2"]

        # Query an agent and check its team
        agent = Agent.query.filter_by(name="Agent 1").first()
        assert agent.team.name == "Test Team"


def test_user_update_last_login_error(app):
    """Test the update_last_login method with a database error."""
    with app.app_context():
        # Create a user
        user = User(
            username="loginuser",
            email="login@example.com",
            password_hash="hashed_password",
        )
        db.session.add(user)
        db.session.commit()

        # Import SQLAlchemyError
        from sqlalchemy.exc import SQLAlchemyError

        # Mock the db.session.commit method to raise an exception
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError("Database error")), \
             patch.object(db.session, 'rollback') as mock_rollback:

            # Call the method and check that it handles the exception
            with pytest.raises(SQLAlchemyError):
                user.update_last_login()

            # Check that db.session.rollback was called
            mock_rollback.assert_called_once()
