"""models.py - SQLAlchemy models for Flask app."""

from __future__ import annotations

# Import db from the database module
from .database import db


class User(db.Model):  # type: ignore[name-defined]
    """User model for authentication and user management."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self) -> str:
        """
        Return string representation of User.

        Returns:
            str: String representation

        """
        return f"<User {self.username}>"

    def __init__(
        self, username: str, email: str, password_hash: str, **kwargs: object
    ) -> None:
        """
        Initialize a User instance.

        Args:
            username: The username of the user
            email: The email address of the user
            password_hash: The hashed password
            **kwargs: Additional keyword arguments for SQLAlchemy

        """
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.password_hash = password_hash


class Team(db.Model):  # type: ignore[name-defined]
    """Team model for grouping AI agents."""

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # Relationships
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

    def __init__(self, name: str, description: str = "", **kwargs: object) -> None:
        """
        Initialize a Team instance.

        Args:
            name: The name of the team
            description: The description of the team
            **kwargs: Additional keyword arguments for SQLAlchemy

        """
        super().__init__(**kwargs)
        self.name = name
        self.description = description


class Agent(db.Model):  # type: ignore[name-defined]
    """Agent model for AI agents that belong to teams."""

    __tablename__ = "agents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80))
    description = db.Column(db.String(255))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # Relationships
    team = db.relationship("Team", backref=db.backref("agents", lazy=True))

    def __repr__(self) -> str:
        """
        Return string representation of Agent.

        Returns:
            str: String representation

        """
        return f"<Agent {self.name} ({self.role})>"

    def __init__(
        self,
        name: str,
        role: str = "",
        description: str = "",
        team_id: int | None = None,
        team: Team | None = None,
        **kwargs: object,
    ) -> None:
        """
        Initialize an Agent instance.

        Args:
            name: The name of the agent
            role: The role of the agent
            description: The description of the agent
            team_id: The ID of the team the agent belongs to
            team: The Team instance the agent belongs to
            **kwargs: Additional keyword arguments for SQLAlchemy

        """
        super().__init__(**kwargs)
        self.name = name
        self.role = role
        self.description = description
        if team_id is not None:
            self.team_id = team_id
        if team is not None:
            self.team = team
