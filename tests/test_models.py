"""test_models - Test module for database models."""

from typing import Generator

import pytest

from app_flask import db
from app_flask.models import Agent, Team, User
from flask import Flask
from flask.testing import FlaskClient

# Constants
EXPECTED_AGENT_COUNT = 2


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

        # Test string representation
        assert str(queried_user) == "<User testuser>"


def test_team_model(app: Flask) -> None:
    """Test the Team model."""
    with app.app_context():
        # Create a team
        team = Team(name="Team Model Test", description="A test team for team model")
        db.session.add(team)
        db.session.commit()

        # Query the team
        queried_team = Team.query.filter_by(name="Team Model Test").first()
        assert queried_team is not None
        assert queried_team.name == "Team Model Test"
        assert queried_team.description == "A test team for team model"
        assert queried_team.created_at is not None
        assert queried_team.updated_at is not None

        # Test string representation
        assert str(queried_team) == "<Team Team Model Test>"


def test_agent_model(app: Flask) -> None:
    """Test the Agent model."""
    with app.app_context():
        # Create a team
        team = Team(
            name="Agent Model Test Team", description="A test team for agent model"
        )
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
        assert queried_agent.created_at is not None
        assert queried_agent.updated_at is not None

        # Test string representation
        assert str(queried_agent) == "<Agent Test Agent (tester)>"


def test_team_agent_relationship(app: Flask) -> None:
    """Test the relationship between Team and Agent models."""
    with app.app_context():
        # Create a team
        team = Team(
            name="Relationship Test Team", description="A test team for relationships"
        )
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
        queried_team = Team.query.filter_by(name="Relationship Test Team").first()
        assert queried_team is not None
        assert len(queried_team.agents) == EXPECTED_AGENT_COUNT
        agent_names = [agent.name for agent in queried_team.agents]
        assert "Agent 1" in agent_names
        assert "Agent 2" in agent_names

        # Query an agent and check its team
        agent = Agent.query.filter_by(name="Agent 1").first()
        assert agent is not None
        assert agent.team is not None
        assert agent.team.name == "Relationship Test Team"


def test_cascade_delete(app: Flask) -> None:
    """Test that deleting a team cascades to delete its agents."""
    with app.app_context():
        # Create a team with agents
        team = Team(name="Cascade Delete Team", description="Team to be deleted")
        db.session.add(team)
        db.session.commit()

        agent1 = Agent(name="Agent 1", role="role1", team=team)
        agent2 = Agent(name="Agent 2", role="role2", team=team)
        db.session.add_all([agent1, agent2])
        db.session.commit()

        team_id = team.id

        # Verify agents exist
        assert Agent.query.filter_by(team_id=team_id).count() == 2

        # Delete the team
        db.session.delete(team)
        db.session.commit()

        # Verify agents are also deleted (cascade)
        assert Agent.query.filter_by(team_id=team_id).count() == 0


def test_user_unique_constraints(app: Flask) -> None:
    """Test that unique constraints work for User model."""
    with app.app_context():
        # Create first user
        user1 = User(
            username="unique_user",
            email="unique@example.com",
            password_hash="password1",
        )
        db.session.add(user1)
        db.session.commit()

        # Try to create user with same username
        user2 = User(
            username="unique_user",  # Same username
            email="different@example.com",
            password_hash="password2",
        )
        db.session.add(user2)

        with pytest.raises(
            Exception, match="UNIQUE constraint failed"
        ):  # Should raise IntegrityError
            db.session.commit()

        db.session.rollback()

        # Try to create user with same email
        user3 = User(
            username="different_user",
            email="unique@example.com",  # Same email
            password_hash="password3",
        )
        db.session.add(user3)

        with pytest.raises(
            Exception, match="UNIQUE constraint failed"
        ):  # Should raise IntegrityError
            db.session.commit()


def test_team_unique_name(app: Flask) -> None:
    """Test that team names must be unique."""
    with app.app_context():
        # Create first team
        team1 = Team(name="Unique Team Name", description="First team")
        db.session.add(team1)
        db.session.commit()

        # Try to create team with same name
        team2 = Team(name="Unique Team Name", description="Second team")
        db.session.add(team2)

        with pytest.raises(
            Exception, match="UNIQUE constraint failed"
        ):  # Should raise IntegrityError
            db.session.commit()
