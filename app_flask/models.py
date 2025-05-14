"""Application models module."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UserModel(Base):
    """User model class."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __init__(self, username: str, email: str, password: str):
        """Initialize user model.
        
        Args:
            username: User's username
            email: User's email address
            password: User's plaintext password (will be hashed)
        """
        from users.auth import hash_credential

        self.username = username
        self.email = email
        self.password_hash = hash_credential(password)
        self.created_at = datetime.utcnow()

    def __repr__(self) -> str:
        """Get string representation.
        
        Returns:
            String representation of user
        """
        return f"<User {self.username}>"

# Alias for compatibility
User = UserModel

class Agent(Base):
    """Agent model class."""

    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    team_id = Column(String(36), ForeignKey('teams.id'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    team = relationship("Team", back_populates="agents")

    def __init__(self, name: str, description: str = None):
        """Initialize agent model.
        
        Args:
            name: Agent name
            description: Optional agent description
        """
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<Agent {self.name}>"

class Team(Base):
    """Team model class."""

    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("UserModel")
    agents = relationship("Agent", back_populates="team")

    def __init__(self, name: str, owner_id: str, description: str = None):
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

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<Team {self.name}>"
