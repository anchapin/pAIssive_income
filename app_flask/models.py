"""models.py - SQLAlchemy models for Flask app."""

from typing import TypeVar

from . import db

# Type alias for db.Model - using Any to avoid mypy errors
# mypy: disable-error-code="name-defined"
ModelType = TypeVar("ModelType", bound="db.Model")  # type: ignore[name-defined]


class User(db.Model):  # type: ignore[name-defined]
    """User model for authentication and user management."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self) -> str:
        """
        Return string representation of User.

        Returns:
            str: String representation

        """
        return f"<User {self.username}>"


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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    team = db.relationship("Team", back_populates="agents")

    def __repr__(self) -> str:
        """
        Return string representation of Agent.

        Returns:
            str: String representation

        """
        return f"<Agent {self.name} ({self.role})>"
