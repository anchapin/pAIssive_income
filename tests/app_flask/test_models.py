"""test_models - Module for tests/app_flask.test_models."""

# Standard library imports
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest

# Local imports
from app_flask.models import UserModel, User, Agent, Team


class TestUserModel:
    """Test suite for the UserModel class."""

    def test_init_with_password_hash(self):
        """Test initializing a user with a pre-hashed password."""
        # Arrange
        username = "testuser"
        email = "test@example.com"
        password_hash = "hashed_password"

        # Act
        user = UserModel(username=username, email=email, password_hash=password_hash)

        # Assert
        assert user.username == username
        assert user.email == email
        assert user.password_hash == password_hash
        assert isinstance(user.created_at, datetime)
        assert user.last_login is None

    @patch("users.auth.hash_credential")
    def test_init_with_password(self, mock_hash_credential):
        """Test initializing a user with a plaintext password."""
        # Arrange
        username = "testuser"
        email = "test@example.com"
        password = "plaintext_password"
        mock_hash_credential.return_value = "hashed_password"

        # Act
        user = UserModel(username=username, email=email, password=password)

        # Assert
        assert user.username == username
        assert user.email == email
        assert user.password_hash == "hashed_password"
        mock_hash_credential.assert_called_once_with(password)
        assert isinstance(user.created_at, datetime)
        assert user.last_login is None

    def test_repr(self):
        """Test the string representation of a user."""
        # Arrange
        user = UserModel(username="testuser", email="test@example.com", password_hash="hash")

        # Act
        result = repr(user)

        # Assert
        assert result == "<User testuser>"

    def test_user_alias(self):
        """Test that User is an alias for UserModel."""
        assert User is UserModel


class TestAgentModel:
    """Test suite for the Agent class."""

    def test_init_basic(self):
        """Test initializing an agent with basic information."""
        # Arrange
        name = "Test Agent"
        role = "Assistant"
        description = "A test agent"

        # Act
        agent = Agent(name=name, role=role, description=description)

        # Assert
        assert agent.name == name
        assert agent.role == role
        assert agent.description == description
        assert agent.team_id is None
        assert agent.team is None
        assert isinstance(agent.created_at, datetime)
        assert isinstance(agent.updated_at, datetime)

    def test_init_with_team_id(self):
        """Test initializing an agent with a team ID."""
        # Arrange
        name = "Test Agent"
        team_id = "team-uuid"

        # Act
        agent = Agent(name=name, team_id=team_id)

        # Assert
        assert agent.name == name
        assert agent.team_id == team_id
        assert agent.team is None

    def test_init_with_team_object(self):
        """Test initializing an agent with a team object."""
        # Arrange
        name = "Test Agent"
        team = MagicMock()
        team.id = "team-uuid"

        # Act
        agent = Agent(name=name, team=team)

        # Assert
        assert agent.name == name
        assert agent.team is team

    def test_repr_with_role(self):
        """Test the string representation of an agent with a role."""
        # Arrange
        agent = Agent(name="Test Agent", role="Assistant")

        # Act
        result = repr(agent)

        # Assert
        assert result == "<Agent Test Agent (Assistant)>"

    def test_repr_without_role(self):
        """Test the string representation of an agent without a role."""
        # Arrange
        agent = Agent(name="Test Agent")

        # Act
        result = repr(agent)

        # Assert
        assert result == "<Agent Test Agent>"


class TestTeamModel:
    """Test suite for the Team class."""

    def test_init_basic(self):
        """Test initializing a team with basic information."""
        # Arrange
        name = "Test Team"
        description = "A test team"

        # Act
        team = Team(name=name, description=description)

        # Assert
        assert team.name == name
        assert team.description == description
        assert team.owner_id is None
        assert isinstance(team.created_at, datetime)
        assert isinstance(team.updated_at, datetime)
        assert team.agents == []

    def test_init_with_owner(self):
        """Test initializing a team with an owner ID."""
        # Arrange
        name = "Test Team"
        owner_id = "owner-uuid"

        # Act
        team = Team(name=name, owner_id=owner_id)

        # Assert
        assert team.name == name
        assert team.owner_id == owner_id

    def test_repr(self):
        """Test the string representation of a team."""
        # Arrange
        team = Team(name="Test Team")

        # Act
        result = repr(team)

        # Assert
        assert result == "<Team Test Team>"

    def test_relationship_with_agents(self):
        """Test the relationship between teams and agents."""
        # This is a more conceptual test since we can't easily test SQLAlchemy relationships
        # without a database, but we can verify the relationship is defined correctly
        team = Team(name="Test Team")
        agent1 = Agent(name="Agent 1", team=team)
        agent2 = Agent(name="Agent 2", team=team)

        # The team should have these agents in its collection
        assert agent1 in team.agents
        assert agent2 in team.agents

        # And the agents should reference back to the team
        assert agent1.team is team
        assert agent2.team is team
