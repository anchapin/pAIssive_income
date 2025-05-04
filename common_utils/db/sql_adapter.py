"""
"""
SQLite adapter implementation of the database interface.
SQLite adapter implementation of the database interface.


This module provides a concrete implementation of DatabaseInterface for SQLite databases.
This module provides a concrete implementation of DatabaseInterface for SQLite databases.
"""
"""




import logging
import logging
import sqlite3
import sqlite3
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from common_utils.db.interfaces import DatabaseInterface, UnitOfWork
from common_utils.db.interfaces import DatabaseInterface, UnitOfWork


logger
logger


= logging.getLogger(__name__)
= logging.getLogger(__name__)




class SQLiteAdapter(DatabaseInterface):
    class SQLiteAdapter(DatabaseInterface):
    """Implementation of DatabaseInterface for SQLite."""

    def __init__(self, db_path: str):
    """
    """
    Initialize the SQLite adapter.
    Initialize the SQLite adapter.


    Args:
    Args:
    db_path: Path to the SQLite database file
    db_path: Path to the SQLite database file
    """
    """
    self.db_path = db_path
    self.db_path = db_path
    self.connection = None
    self.connection = None
    self.cursor = None
    self.cursor = None


    def connect(self) -> None:
    def connect(self) -> None:
    """Establish a connection to the SQLite database."""
    try:
    self.connection = sqlite3.connect(self.db_path)
    self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
    self.cursor = self.connection.cursor()
    logger.info(f"Connected to SQLite database at {self.db_path}")
except sqlite3.Error as e:
    logger.error(f"Error connecting to SQLite database: {e}")
    raise

    def disconnect(self) -> None:
    """Close the SQLite database connection."""
    if self.connection:
    self.connection.close()
    self.connection = None
    self.cursor = None
    logger.info("Disconnected from SQLite database")

    def _ensure_connection(self) -> None:
    """Ensure database connection is established."""
    if not self.connection:
    self.connect()

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    """
    Execute a query with parameters.
    Execute a query with parameters.


    Args:
    Args:
    query: SQL query to execute
    query: SQL query to execute
    params: Parameters for the query
    params: Parameters for the query


    Returns:
    Returns:
    Query result
    Query result


    Raises:
    Raises:
    sqlite3.Error: If there's an issue with the database operation
    sqlite3.Error: If there's an issue with the database operation
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    if params:
    if params:
    result = self.cursor.execute(query, params)
    result = self.cursor.execute(query, params)
    else:
    else:
    result = self.cursor.execute(query)
    result = self.cursor.execute(query)


    return result
    return result
except sqlite3.Error as e:
except sqlite3.Error as e:
    logger.error(f"Error executing query: {e}")
    logger.error(f"Error executing query: {e}")
    if self.connection:
    if self.connection:
    self.connection.rollback()
    self.connection.rollback()
    raise
    raise


    def fetch_one(
    def fetch_one(
    self, query: str, params: Optional[Dict[str, Any]] = None
    self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
    ) -> Optional[Dict[str, Any]]:
    """
    """
    Fetch a single record from the SQLite database.
    Fetch a single record from the SQLite database.


    Args:
    Args:
    query: SQL query to execute
    query: SQL query to execute
    params: Parameters for the query
    params: Parameters for the query


    Returns:
    Returns:
    A single record as a dictionary or None if no records found
    A single record as a dictionary or None if no records found


    Raises:
    Raises:
    sqlite3.Error: If there's an issue with the database operation
    sqlite3.Error: If there's an issue with the database operation
    """
    """
    try:
    try:
    self.execute(query, params)
    self.execute(query, params)
    row = self.cursor.fetchone()
    row = self.cursor.fetchone()
    return dict(row) if row else None
    return dict(row) if row else None
except sqlite3.Error as e:
except sqlite3.Error as e:
    logger.error(f"Error fetching data: {e}")
    logger.error(f"Error fetching data: {e}")
    raise
    raise


    def fetch_all(
    def fetch_all(
    self, query: str, params: Optional[Dict[str, Any]] = None
    self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Fetch multiple records from the SQLite database.
    Fetch multiple records from the SQLite database.


    Args:
    Args:
    query: SQL query to execute
    query: SQL query to execute
    params: Parameters for the query
    params: Parameters for the query


    Returns:
    Returns:
    A list of records as dictionaries
    A list of records as dictionaries


    Raises:
    Raises:
    sqlite3.Error: If there's an issue with the database operation
    sqlite3.Error: If there's an issue with the database operation
    """
    """
    try:
    try:
    self.execute(query, params)
    self.execute(query, params)
    rows = self.cursor.fetchall()
    rows = self.cursor.fetchall()
    return [dict(row) for row in rows]
    return [dict(row) for row in rows]
except sqlite3.Error as e:
except sqlite3.Error as e:
    logger.error(f"Error fetching data: {e}")
    logger.error(f"Error fetching data: {e}")
    raise
    raise


    def insert(self, table: str, data: Dict[str, Any]) -> Any:
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
    """
    """
    Insert a record into the SQLite database.
    Insert a record into the SQLite database.


    Args:
    Args:
    table: Table name
    table: Table name
    data: Column-value pairs to insert
    data: Column-value pairs to insert


    Returns:
    Returns:
    The ID of the inserted row
    The ID of the inserted row


    Raises:
    Raises:
    sqlite3.Error: If there's an issue with the database operation
    sqlite3.Error: If there's an issue with the database operation
    """
    """
    placeholders = ", ".join([f":{key}" for key in data.keys()])
    placeholders = ", ".join([f":{key}" for key in data.keys()])
    columns = ", ".join(data.keys())
    columns = ", ".join(data.keys())


    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"


    try:
    try:
    self.execute(query, data)
    self.execute(query, data)
    return self.cursor.lastrowid
    return self.cursor.lastrowid
except sqlite3.Error as e:
except sqlite3.Error as e:
    logger.error(f"Error inserting data: {e}")
    logger.error(f"Error inserting data: {e}")
    raise
    raise


    def update(
    def update(
    self,
    self,
    table: str,
    table: str,
    data: Dict[str, Any],
    data: Dict[str, Any],
    condition: str,
    condition: str,
    params: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    ) -> int:
    ) -> int:
    """
    """
    Update records in the SQLite database.
    Update records in the SQLite database.


    Args:
    Args:
    table: Table name
    table: Table name
    data: Column-value pairs to update
    data: Column-value pairs to update
    condition: WHERE clause condition
    condition: WHERE clause condition
    params: Parameters for the condition
    params: Parameters for the condition


    Returns:
    Returns:
    Number of rows affected
    Number of rows affected


    Raises:
    Raises:
    sqlite3.Error: If there's an issue with the database operation
    sqlite3.Error: If there's an issue with the database operation
    """
    """
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    combined_params = {**data}
    combined_params = {**data}


    if params:
    if params:
    combined_params.update(params)
    combined_params.update(params)


    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"


    try:
    try:
    self.execute(query, combined_params)
    self.execute(query, combined_params)
    return self.cursor.rowcount
    return self.cursor.rowcount
except sqlite3.Error as e:
except sqlite3.Error as e:
    logger.error(f"Error updating data: {e}")
    logger.error(f"Error updating data: {e}")
    raise
    raise


    def delete(
    def delete(
    self, table: str, condition: str, params: Optional[Dict[str, Any]] = None
    self, table: str, condition: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
    ) -> int:
    """
    """
    Delete records from the SQLite database.
    Delete records from the SQLite database.


    Args:
    Args:
    table: Table name
    table: Table name
    condition: WHERE clause condition
    condition: WHERE clause condition
    params: Parameters for the condition
    params: Parameters for the condition


    Returns:
    Returns:
    Number of rows affected
    Number of rows affected


    Raises:
    Raises:
    sqlite3.Error: If there's an issue with the database operation
    sqlite3.Error: If there's an issue with the database operation
    """
    """
    query = f"DELETE FROM {table} WHERE {condition}"
    query = f"DELETE FROM {table} WHERE {condition}"


    try:
    try:
    self.execute(query, params)
    self.execute(query, params)
    return self.cursor.rowcount
    return self.cursor.rowcount
except sqlite3.Error as e:
except sqlite3.Error as e:
    logger.error(f"Error deleting data: {e}")
    logger.error(f"Error deleting data: {e}")
    raise
    raise




    class SQLiteUnitOfWork(UnitOfWork):
    class SQLiteUnitOfWork(UnitOfWork):
    """SQLite implementation of the Unit of Work pattern."""

    def __init__(self, adapter: SQLiteAdapter):
    """
    """
    Initialize the SQLite unit of work.
    Initialize the SQLite unit of work.


    Args:
    Args:
    adapter: SQLite adapter instance
    adapter: SQLite adapter instance
    """
    """
    self.adapter = adapter
    self.adapter = adapter


    def __enter__(self):
    def __enter__(self):
    """Start a transaction."""
    self.adapter._ensure_connection()
    self.adapter.execute("BEGIN TRANSACTION")
    return self

    def __exit__(self, exc_type, exc_val, exc_tb):
    """End a transaction."""
    if exc_type is not None:  # An exception occurred
    self.rollback()
    else:
    self.commit()

    def commit(self):
    """Commit the transaction."""
    if self.adapter.connection:
    self.adapter.connection.commit()
    logger.debug("Transaction committed")

    def rollback(self):
    """Rollback the transaction."""
    if self.adapter.connection:
    self.adapter.connection.rollback()
    logger.debug("Transaction rolled back")