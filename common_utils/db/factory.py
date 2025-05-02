"""
Database factory for creating database instances.

This module provides a factory for creating different types of database connections
based on configuration.
"""

import logging
from typing import Any, Dict

from common_utils.db.interfaces import DatabaseInterface, UnitOfWork
from common_utils.db.nosql_adapter import MongoDBAdapter, MongoDBUnitOfWork
from common_utils.db.sql_adapter import SQLiteAdapter, SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class DatabaseFactory:
    """Factory for creating database connections."""

    @staticmethod
    def create_database(db_type: str, config: Dict[str, Any]) -> DatabaseInterface:
        """
        Create and return a database instance based on the provided type and configuration.

        Args:
            db_type: The type of database ('sqlite', 'mongodb', etc.)
            config: Configuration parameters for the database

        Returns:
            An instance of a class implementing DatabaseInterface

        Raises:
            ValueError: If the db_type is not supported
        """
        db_type = db_type.lower()

        if db_type == "sqlite":
            db_path = config.get("db_path", ":memory:")
            logger.info(f"Creating SQLite database connection to {db_path}")
            return SQLiteAdapter(db_path)

        elif db_type == "mongodb":
            connection_string = config.get(
                "connection_string", "mongodb://localhost:27017"
            )
            db_name = config.get("db_name", "default")
            logger.info(
                f"Creating MongoDB connection to {connection_string}, database: {db_name}"
            )
            return MongoDBAdapter(connection_string, db_name)

        else:
            logger.error(f"Unsupported database type: {db_type}")
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def create_unit_of_work(db: DatabaseInterface) -> UnitOfWork:
        """
        Create and return a unit of work instance for the provided database.

        Args:
            db: The database interface instance

        Returns:
            An instance of a class implementing UnitOfWork

        Raises:
            ValueError: If the database type is not supported
        """
        if isinstance(db, SQLiteAdapter):
            return SQLiteUnitOfWork(db)
        elif isinstance(db, MongoDBAdapter):
            return MongoDBUnitOfWork(db)
        else:
            logger.error(f"Unsupported database type for UnitOfWork: {type(db)}")
            raise ValueError(f"Unsupported database type for UnitOfWork: {type(db)}")
