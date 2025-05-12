"""test_models - Test module for database models."""

import pytest
from flask import Flask
from flask.models import db, User, Team, Agent


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_user_model(app):
    """Test the User model."""
    with app.app_context():
        # Create a user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )
        db.session.add(user)
        db.session.commit()

        # Query the user
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"


def test_team_model(app):
    """Test the Team model."""
    with app.app_context():
        # Create a team
        team = Team(name="Test Team", description="A test team")
        db.session.add(team)
        db.session.commit()

        # Query the team
        team = Team.query.filter_by(name="Test Team").first()
        assert team is not None
        assert team.name == "Test Team"
        assert team.description == "A test team"


def test_agent_model(app):
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
        agent = Agent.query.filter_by(name="Test Agent").first()
        assert agent is not None
        assert agent.name == "Test Agent"
        assert agent.role == "tester"
        assert agent.description == "A test agent"
        assert agent.team_id == team.id


def test_team_agent_relationship(app):
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
        team = Team.query.filter_by(name="Test Team").first()
        assert len(team.agents) == 2
        assert team.agents[0].name in ["Agent 1", "Agent 2"]
        assert team.agents[1].name in ["Agent 1", "Agent 2"]

        # Query an agent and check its team
        agent = Agent.query.filter_by(name="Agent 1").first()
        assert agent.team.name == "Test Team"
