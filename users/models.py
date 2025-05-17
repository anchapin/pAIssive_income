"""models - Module for users.models."""

# Standard library imports
from __future__ import annotations

from typing import Any

# Third-party imports
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Local imports

# Create a mock database session for testing
Base = declarative_base()
db = sessionmaker()()


class User(Base):  # type: ignore[misc, valid-type]
    """User model for database."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        """
        Convert user model to dictionary.

        Returns:
            dict[str, Any]: User data as dictionary

        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
