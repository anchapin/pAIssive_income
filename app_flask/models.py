"""Application models module."""

from datetime import datetime
import uuid
from typing import TypeVar, Dict, Any, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, backref

# Type alias for db.Model - using Any to avoid mypy errors
# mypy: disable-error-code="name-defined"
ModelType = TypeVar("ModelType", bound="db.Model")  # type: ignore[name-defined]

# Re-export hash_credential for tests
from users.auth import hash_credential as _hash_credential
hash_credential = _hash_credential

class User(db.Model):  # type: ignore[name-defined]
    """User model for authentication and user management."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(String(5), default="true", nullable=False)
    is_admin = Column(String(5), default="false", nullable=False)

    def __init__(self, username: str, email: str, password_hash: str = None, password: str = None,
                 is_active: bool = True, is_admin: bool = False):
        """Initialize user model.

        Args:
            username: User's username
            email: User's email address
            password_hash: Pre-hashed password (for tests)
            password: User's plaintext password (will be hashed)
            is_active: Whether the user is active
            is_admin: Whether the user is an admin
        """
        self.username = username
        self.email = email
        self.is_active = str(is_active).lower()
        self.is_admin = str(is_admin).lower()

        if password_hash is not None:
            self.password_hash = password_hash
        elif password is not None:
            from users.auth import hash_credential
            self.password_hash = hash_credential(password)

        self.created_at = datetime.utcnow()

    def __repr__(self) -> str:
        """
        Return string representation of User.

        Returns:
            str: String representation

        """
        return f"<User {self.username}>"

    def to_dict(self, include_profile=False) -> Dict[str, Any]:
        """Convert user model to dictionary.

        Args:
            include_profile: Whether to include profile data

        Returns:
            Dictionary with user data
        """
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active == "true",
            "is_admin": self.is_admin == "true",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

        if include_profile and hasattr(self, 'profile') and self.profile:
            result["profile"] = self.profile.to_dict()

        return result


class Team(db.Model):  # type: ignore[name-defined]
    """Team model for grouping AI agents."""

    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    agents = db.relationship(
        "Agent", back_populates="team", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        Return string representation of Team.

        Returns:
            str: String representation

        """
        return f"<Team {self.name}>"

class Agent(db.Model):  # type: ignore[name-defined]
    """Agent model for AI agents that belong to teams."""

    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    role = Column(String(100))
    description = Column(String(1000))
    team_id = Column(String(36), ForeignKey('teams.id'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    team = relationship("Team", back_populates="agents")

    def __init__(self, name: str, role: str = None, description: str = None, team_id: str = None, team = None):
        """Initialize agent model.

        Args:
            name: Agent name
            role: Agent role
            description: Optional agent description
            team_id: ID of team
            team: Team object
        """
        self.name = name
        self.role = role
        self.description = description
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        if team_id is not None:
            self.team_id = team_id
        elif team is not None:
            self.team = team

    def __repr__(self) -> str:
        """
        Return string representation of Agent.

        Returns:
            str: String representation

        """
        return f"<Agent {self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent model to dictionary.

        Returns:
            Dictionary with agent data
        """
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "team_id": self.team_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], team=None) -> "Agent":
        """Create agent from dictionary.

        Args:
            data: Dictionary with agent data
            team: Team object

        Returns:
            Agent instance
        """
        # Set team_id from team object if provided
        team_id = data.get("team_id")
        if team is not None:
            team_id = team.id

        agent = cls(
            name=data.get("name"),
            role=data.get("role"),
            description=data.get("description"),
            team_id=team_id,
            team=team
        )

        if "id" in data:
            agent.id = data["id"]

        return agent


# This is a duplicate Team class definition that has been removed
# The Team class is already defined above
