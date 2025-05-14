"""test_models - Test module for database models."""

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

from app_flask import db
from app_flask.models import Agent, Team, User


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestUserModel:
    """Test suite for the User model."""

    def test_user_creation(self, app):
        """Test creating a user."""
        with app.app_context():
            # Create a user
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password"
            )
            db.session.add(user)
            db.session.commit()

            # Retrieve the user
            retrieved_user = User.query.filter_by(username="testuser").first()

            # Assert
            assert retrieved_user is not None
            assert retrieved_user.username == "testuser"
            assert retrieved_user.email == "test@example.com"
            assert retrieved_user.password_hash == "hashed_password"

    def test_user_representation(self, app):
        """Test the string representation of a user."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password"
            )

            # Assert
            assert str(user) == "<User testuser>"

    def test_unique_username_constraint(self, app):
        """Test that usernames must be unique."""
        with app.app_context():
            # Create a user
            user1 = User(
                username="testuser",
                email="test1@example.com",
                password_hash="hashed_password1"
            )
            db.session.add(user1)
            db.session.commit()

            # Try to create another user with the same username
            user2 = User(
                username="testuser",
                email="test2@example.com",
                password_hash="hashed_password2"
            )
            db.session.add(user2)

            # Assert that an integrity error is raised
            with pytest.raises(IntegrityError):
                db.session.commit()

            # Rollback the session
            db.session.rollback()

    def test_unique_email_constraint(self, app):
        """Test that emails must be unique."""
        with app.app_context():
            # Create a user
            user1 = User(
                username="testuser1",
                email="test@example.com",
                password_hash="hashed_password1"
            )
            db.session.add(user1)
            db.session.commit()

            # Try to create another user with the same email
            user2 = User(
                username="testuser2",
                email="test@example.com",
                password_hash="hashed_password2"
            )
            db.session.add(user2)

            # Assert that an integrity error is raised
            with pytest.raises(IntegrityError):
                db.session.commit()

            # Rollback the session
            db.session.rollback()


class TestTeamModel:
    """Test suite for the Team model."""

    def test_team_creation(self, app):
        """Test creating a team."""
        with app.app_context():
            # Create a team
            team = Team(
                name="Test Team",
                description="A team for testing"
            )
            db.session.add(team)
            db.session.commit()

            # Retrieve the team
            retrieved_team = Team.query.filter_by(name="Test Team").first()

            # Assert
            assert retrieved_team is not None
            assert retrieved_team.name == "Test Team"
            assert retrieved_team.description == "A team for testing"
            assert retrieved_team.created_at is not None
            assert retrieved_team.updated_at is not None

    def test_team_representation(self, app):
        """Test the string representation of a team."""
        with app.app_context():
            team = Team(
                name="Test Team",
                description="A team for testing"
            )

            # Assert
            assert str(team) == "<Team Test Team>"

    def test_unique_team_name_constraint(self, app):
        """Test that team names must be unique."""
        with app.app_context():
            # Create a team
            team1 = Team(
                name="Test Team",
                description="A team for testing"
            )
            db.session.add(team1)
            db.session.commit()

            # Try to create another team with the same name
            team2 = Team(
                name="Test Team",
                description="Another team for testing"
            )
            db.session.add(team2)

            # Assert that an integrity error is raised
            with pytest.raises(IntegrityError):
                db.session.commit()

            # Rollback the session
            db.session.rollback()

    def test_team_agents_relationship(self, app):
        """Test the relationship between teams and agents."""
        with app.app_context():
            # Create a team
            team = Team(
                name="Test Team",
                description="A team for testing"
            )
            db.session.add(team)
            db.session.commit()

            # Create agents for the team
            agent1 = Agent(
                name="Agent 1",
                role="Developer",
                description="A developer agent",
                team_id=team.id
            )
            agent2 = Agent(
                name="Agent 2",
                role="Designer",
                description="A designer agent",
                team_id=team.id
            )
            db.session.add(agent1)
            db.session.add(agent2)
            db.session.commit()

            # Retrieve the team with its agents
            retrieved_team = Team.query.filter_by(name="Test Team").first()

            # Assert
            assert len(retrieved_team.agents) == 2
            assert retrieved_team.agents[0].name == "Agent 1"
            assert retrieved_team.agents[1].name == "Agent 2"

    def test_cascade_delete(self, app):
        """Test that deleting a team cascades to its agents."""
        with app.app_context():
            # Create a team
            team = Team(
                name="Test Team",
                description="A team for testing"
            )
            db.session.add(team)
            db.session.commit()

            # Create agents for the team
            agent1 = Agent(
                name="Agent 1",
                role="Developer",
                description="A developer agent",
                team_id=team.id
            )
            agent2 = Agent(
                name="Agent 2",
                role="Designer",
                description="A designer agent",
                team_id=team.id
            )
            db.session.add(agent1)
            db.session.add(agent2)
            db.session.commit()

            # Delete the team
            db.session.delete(team)
            db.session.commit()

            # Assert that the agents are also deleted
            assert Agent.query.count() == 0


class TestAgentModel:
    """Test suite for the Agent model."""

    def test_agent_creation(self, app):
        """Test creating an agent."""
        with app.app_context():
            # Create a team
            team = Team(
                name="Test Team",
                description="A team for testing"
            )
            db.session.add(team)
            db.session.commit()

            # Create an agent
            agent = Agent(
                name="Test Agent",
                role="Developer",
                description="An agent for testing",
                team_id=team.id
            )
            db.session.add(agent)
            db.session.commit()

            # Retrieve the agent
            retrieved_agent = Agent.query.filter_by(name="Test Agent").first()

            # Assert
            assert retrieved_agent is not None
            assert retrieved_agent.name == "Test Agent"
            assert retrieved_agent.role == "Developer"
            assert retrieved_agent.description == "An agent for testing"
            assert retrieved_agent.team_id == team.id
            assert retrieved_agent.created_at is not None
            assert retrieved_agent.updated_at is not None

    def test_agent_representation(self, app):
        """Test the string representation of an agent."""
        with app.app_context():
            agent = Agent(
                name="Test Agent",
                role="Developer",
                description="An agent for testing"
            )

            # Assert
            assert str(agent) == "<Agent Test Agent (Developer)>"

    def test_agent_team_relationship(self, app):
        """Test the relationship between agents and teams."""
        with app.app_context():
            # Create a team
            team = Team(
                name="Test Team",
                description="A team for testing"
            )
            db.session.add(team)
            db.session.commit()

            # Create an agent
            agent = Agent(
                name="Test Agent",
                role="Developer",
                description="An agent for testing",
                team_id=team.id
            )
            db.session.add(agent)
            db.session.commit()

            # Retrieve the agent with its team
            retrieved_agent = Agent.query.filter_by(name="Test Agent").first()

            # Assert
            assert retrieved_agent.team is not None
            assert retrieved_agent.team.name == "Test Team"


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
