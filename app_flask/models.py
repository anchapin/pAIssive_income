"""Application models module."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, backref

from app_flask import db
from users.auth import hash_credential as _hash_credential

# Re-export hash_credential for tests
hash_credential = _hash_credential

class UserModel(db.Model):
    """User model class."""

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
        """Get string representation.

        Returns:
            String representation of user
        """
        return f"<User {self.username}>"

    def to_dict(self, include_profile=False) -> dict:
        """Convert user model to dictionary.

        Args:
            include_profile: Whether to include the user's profile

        Returns:
            Dictionary representation of user
        """
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active == "true",
            "is_admin": self.is_admin == "true",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

        if include_profile and hasattr(self, 'profile') and self.profile:
            result["profile"] = self.profile.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "UserModel":
        """Create user model from dictionary.

        Args:
            data: Dictionary with user data

        Returns:
            UserModel instance
        """
        user = cls(
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            is_active=data.get("is_active", True),
            is_admin=data.get("is_admin", False)
        )

        if "id" in data:
            user.id = data["id"]

        if "created_at" in data and data["created_at"]:
            if isinstance(data["created_at"], str):
                user.created_at = datetime.fromisoformat(data["created_at"])
            else:
                user.created_at = data["created_at"]

        if "last_login" in data and data["last_login"]:
            if isinstance(data["last_login"], str):
                user.last_login = datetime.fromisoformat(data["last_login"])
            else:
                user.last_login = data["last_login"]

        return user

    def update_last_login(self) -> None:
        """Update the last login timestamp to current time.

        Raises:
            SQLAlchemyError: If there's a database error
        """
        from sqlalchemy.exc import SQLAlchemyError

        self.last_login = datetime.utcnow()
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

# Alias for compatibility
User = UserModel

class Agent(db.Model):
    """Agent model class."""

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
        """Get string representation."""
        if self.role:
            return f"<Agent {self.name} ({self.role})>"
        return f"<Agent {self.name}>"

class UserProfile(db.Model):
    """User profile model class."""

    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    bio = Column(String(1000))
    avatar_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("UserModel", backref=backref("profile", uselist=False))

    def __init__(self, user=None, user_id=None, first_name=None, last_name=None, bio=None, avatar_url=None):
        """Initialize user profile model.

        Args:
            user: User object
            user_id: ID of user
            first_name: User's first name
            last_name: User's last name
            bio: User's biography
            avatar_url: URL to user's avatar
        """
        if user is not None:
            self.user = user
            self.user_id = user.id
        elif user_id is not None:
            self.user_id = user_id

        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio
        self.avatar_url = avatar_url
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<UserProfile {self.first_name} {self.last_name}>"

    def to_dict(self) -> dict:
        """Convert profile to dictionary.

        Returns:
            Dictionary representation of profile
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict, user=None) -> "UserProfile":
        """Create profile from dictionary.

        Args:
            data: Dictionary with profile data
            user: User object

        Returns:
            UserProfile instance
        """
        # Set user_id from user object if provided
        user_id = data.get("user_id")
        if user is not None:
            user_id = user.id

        profile = cls(
            user=user,
            user_id=user_id,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            bio=data.get("bio"),
            avatar_url=data.get("avatar_url")
        )

        if "id" in data:
            profile.id = data["id"]

        return profile


class Team(db.Model):
    """Team model class."""

    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(1000))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("UserModel")
    agents = relationship("Agent", back_populates="team", cascade="all, delete-orphan")

    def __init__(self, name: str, owner_id: str = None, description: str = None):
        """Initialize team model.

        Args:
            name: Team name
            owner_id: ID of team owner (User)
            description: Optional team description
        """
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<Team {self.name}>"
