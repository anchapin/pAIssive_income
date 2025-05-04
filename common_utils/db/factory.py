"""
"""
Database factory for creating database instances.
Database factory for creating database instances.


This module provides a factory for creating different types of database connections
This module provides a factory for creating different types of database connections
based on configuration.
based on configuration.
"""
"""




import logging
import logging
from typing import Any, Dict
from typing import Any, Dict


from common_utils.db.interfaces import DatabaseInterface, UnitOfWork
from common_utils.db.interfaces import DatabaseInterface, UnitOfWork
from common_utils.db.nosql_adapter import MongoDBAdapter, MongoDBUnitOfWork
from common_utils.db.nosql_adapter import MongoDBAdapter, MongoDBUnitOfWork
from common_utils.db.sql_adapter import SQLiteAdapter, SQLiteUnitOfWork
from common_utils.db.sql_adapter import SQLiteAdapter, SQLiteUnitOfWork


logger
logger


= logging.getLogger(__name__)
= logging.getLogger(__name__)




class DatabaseFactory:
    class DatabaseFactory:
    """Factory for creating database connections."""

    @staticmethod
    def create_database(db_type: str, config: Dict[str, Any]) -> DatabaseInterface:
    """
    """
    Create and return a database instance based on the provided type and configuration.
    Create and return a database instance based on the provided type and configuration.


    Args:
    Args:
    db_type: The type of database ('sqlite', 'mongodb', etc.)
    db_type: The type of database ('sqlite', 'mongodb', etc.)
    config: Configuration parameters for the database
    config: Configuration parameters for the database


    Returns:
    Returns:
    An instance of a class implementing DatabaseInterface
    An instance of a class implementing DatabaseInterface


    Raises:
    Raises:
    ValueError: If the db_type is not supported
    ValueError: If the db_type is not supported
    """
    """
    db_type = db_type.lower()
    db_type = db_type.lower()


    if db_type == "sqlite":
    if db_type == "sqlite":
    db_path = config.get("db_path", ":memory:")
    db_path = config.get("db_path", ":memory:")
    logger.info(f"Creating SQLite database connection to {db_path}")
    logger.info(f"Creating SQLite database connection to {db_path}")
    return SQLiteAdapter(db_path)
    return SQLiteAdapter(db_path)


    elif db_type == "mongodb":
    elif db_type == "mongodb":
    connection_string = config.get(
    connection_string = config.get(
    "connection_string", "mongodb://localhost:27017"
    "connection_string", "mongodb://localhost:27017"
    )
    )
    db_name = config.get("db_name", "default")
    db_name = config.get("db_name", "default")
    logger.info(
    logger.info(
    f"Creating MongoDB connection to {connection_string}, database: {db_name}"
    f"Creating MongoDB connection to {connection_string}, database: {db_name}"
    )
    )
    return MongoDBAdapter(connection_string, db_name)
    return MongoDBAdapter(connection_string, db_name)


    else:
    else:
    logger.error(f"Unsupported database type: {db_type}")
    logger.error(f"Unsupported database type: {db_type}")
    raise ValueError(f"Unsupported database type: {db_type}")
    raise ValueError(f"Unsupported database type: {db_type}")


    @staticmethod
    @staticmethod
    def create_unit_of_work(db: DatabaseInterface) -> UnitOfWork:
    def create_unit_of_work(db: DatabaseInterface) -> UnitOfWork:
    """
    """
    Create and return a unit of work instance for the provided database.
    Create and return a unit of work instance for the provided database.


    Args:
    Args:
    db: The database interface instance
    db: The database interface instance


    Returns:
    Returns:
    An instance of a class implementing UnitOfWork
    An instance of a class implementing UnitOfWork


    Raises:
    Raises:
    ValueError: If the database type is not supported
    ValueError: If the database type is not supported
    """
    """
    if isinstance(db, SQLiteAdapter):
    if isinstance(db, SQLiteAdapter):
    return SQLiteUnitOfWork(db)
    return SQLiteUnitOfWork(db)
    elif isinstance(db, MongoDBAdapter):
    elif isinstance(db, MongoDBAdapter):
    return MongoDBUnitOfWork(db)
    return MongoDBUnitOfWork(db)
    else:
    else:
    logger.error(f"Unsupported database type for UnitOfWork: {type(db)}")
    logger.error(f"Unsupported database type for UnitOfWork: {type(db)}")
    raise ValueError(f"Unsupported database type for UnitOfWork: {type(db)}")
    raise ValueError(f"Unsupported database type for UnitOfWork: {type(db)}")