"""
Database abstraction layer interfaces.

This module provides abstract base classes and interfaces for the database abstraction
layer. These interfaces define the contract that all database implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class DatabaseInterface(ABC):
    """Base interface for database operations."""

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query with parameters."""
        pass

    @abstractmethod
    def fetch_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single record from the database."""
        pass

    @abstractmethod
    def fetch_all(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch multiple records from the database."""
        pass

    @abstractmethod
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert a record into the database."""
        pass

    @abstractmethod
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Update records in the database."""
        pass

    @abstractmethod
    def delete(self, table: str, condition: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Delete records from the database."""
        pass


class Repository(Generic[T], ABC):
    """Generic repository interface for entity operations."""

    @abstractmethod
    def find_by_id(self, id: Any) -> Optional[T]:
        """Find an entity by its ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity (create or update)."""
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity."""
        pass


class UnitOfWork(ABC):
    """Interface for the Unit of Work pattern."""

    @abstractmethod
    def __enter__(self):
        """Start a transaction."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End a transaction."""
        pass

    @abstractmethod
    def commit(self):
        """Commit the transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback the transaction."""
        pass
