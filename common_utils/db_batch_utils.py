"""
"""
Database batch operations utility.
Database batch operations utility.


This module provides utilities for performing database operations in batches,
This module provides utilities for performing database operations in batches,
including inserting, updating, and querying large sets of data efficiently.
including inserting, updating, and querying large sets of data efficiently.
"""
"""




import logging
import logging
import sqlite3
import sqlite3
import time
import time
import uuid
import uuid
from dataclasses import dataclass
from dataclasses import dataclass
from datetime import datetime
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union


from .batch_utils import BatchProcessingStats
from .batch_utils import BatchProcessingStats


# Type variables for generic functions
# Type variables for generic functions
T = TypeVar("T")  # Input item type
T = TypeVar("T")  # Input item type
R = TypeVar("R")  # Result item type
R = TypeVar("R")  # Result item type


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




@dataclass
@dataclass
class DBBatchResult:
    class DBBatchResult:
    """Results from a batch database operation."""

    batch_id: str
    operation_type: str  # 'insert', 'update', 'delete', 'query'
    affected_rows: int
    errors: List[Tuple[int, Exception]]
    stats: BatchProcessingStats

    @property
    def success_rate(self) -> float:
    """Calculate the success rate as a percentage."""
    if self.stats.total_items == 0:
    return 100.0
    return 100.0 - (len(self.errors) / self.stats.total_items * 100.0)

    def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
    return {
    "batch_id": self.batch_id,
    "operation_type": self.operation_type,
    "affected_rows": self.affected_rows,
    "total_items": self.stats.total_items,
    "error_count": len(self.errors),
    "success_rate": self.success_rate,
    "processing_time_ms": self.stats.processing_time_ms,
    "items_per_second": self.stats.items_per_second,
    }


    class DBBatchProcessor:
    """
    """
    Class for performing database operations in batches.
    Class for performing database operations in batches.
    """
    """


    def __init__(
    def __init__(
    self, connection: Union[sqlite3.Connection, Any], default_batch_size: int = 100
    self, connection: Union[sqlite3.Connection, Any], default_batch_size: int = 100
    ):
    ):
    """
    """
    Initialize the batch processor.
    Initialize the batch processor.


    Args:
    Args:
    connection: Database connection (SQLite or other DB-API 2.0 compliant connection)
    connection: Database connection (SQLite or other DB-API 2.0 compliant connection)
    default_batch_size: Default size for each batch
    default_batch_size: Default size for each batch
    """
    """
    self.connection = connection
    self.connection = connection
    self.default_batch_size = default_batch_size
    self.default_batch_size = default_batch_size
    self.batch_history = {}
    self.batch_history = {}


    # Detect if we're using SQLite
    # Detect if we're using SQLite
    self.is_sqlite = isinstance(connection, sqlite3.Connection)
    self.is_sqlite = isinstance(connection, sqlite3.Connection)


    def _execute_batch(
    def _execute_batch(
    self, cursor: Any, query: str, params_list: List[Tuple], operation_type: str
    self, cursor: Any, query: str, params_list: List[Tuple], operation_type: str
    ) -> Tuple[int, List[Tuple[int, Exception]]]:
    ) -> Tuple[int, List[Tuple[int, Exception]]]:
    """
    """
    Execute a batch of the same query with different parameters.
    Execute a batch of the same query with different parameters.


    Args:
    Args:
    cursor: Database cursor
    cursor: Database cursor
    query: SQL query to execute
    query: SQL query to execute
    params_list: List of parameter tuples
    params_list: List of parameter tuples
    operation_type: Type of operation ('insert', 'update', 'delete', 'query')
    operation_type: Type of operation ('insert', 'update', 'delete', 'query')


    Returns:
    Returns:
    Tuple of (affected_rows, list of errors)
    Tuple of (affected_rows, list of errors)
    """
    """
    affected_rows = 0
    affected_rows = 0
    errors = []
    errors = []


    if not params_list:
    if not params_list:
    return 0, []
    return 0, []


    # Execute batch based on database type
    # Execute batch based on database type
    if self.is_sqlite:
    if self.is_sqlite:
    # SQLite doesn't have native batch support, so execute individually
    # SQLite doesn't have native batch support, so execute individually
    for i, params in enumerate(params_list):
    for i, params in enumerate(params_list):
    try:
    try:
    cursor.execute(query, params)
    cursor.execute(query, params)
    if operation_type in ("insert", "update", "delete"):
    if operation_type in ("insert", "update", "delete"):
    affected_rows += cursor.rowcount
    affected_rows += cursor.rowcount
except Exception as e:
except Exception as e:
    errors.append((i, e))
    errors.append((i, e))
    logger.error(f"Error executing {operation_type} operation: {e}")
    logger.error(f"Error executing {operation_type} operation: {e}")
    else:
    else:
    # For other databases, try to use execute_batch if available
    # For other databases, try to use execute_batch if available
    # This is available in some database adapters like psycopg2
    # This is available in some database adapters like psycopg2
    try:
    try:
    if hasattr(cursor, "executemany"):
    if hasattr(cursor, "executemany"):
    cursor.executemany(query, params_list)
    cursor.executemany(query, params_list)
    affected_rows = cursor.rowcount
    affected_rows = cursor.rowcount
    else:
    else:
    # Fall back to individual execution
    # Fall back to individual execution
    for i, params in enumerate(params_list):
    for i, params in enumerate(params_list):
    try:
    try:
    cursor.execute(query, params)
    cursor.execute(query, params)
    affected_rows += cursor.rowcount
    affected_rows += cursor.rowcount
except Exception as e:
except Exception as e:
    errors.append((i, e))
    errors.append((i, e))
    logger.error(
    logger.error(
    f"Error executing {operation_type} operation: {e}"
    f"Error executing {operation_type} operation: {e}"
    )
    )
except Exception as e:
except Exception as e:
    for i in range(len(params_list)):
    for i in range(len(params_list)):
    errors.append((i, e))
    errors.append((i, e))
    logger.error(f"Error executing batch {operation_type} operation: {e}")
    logger.error(f"Error executing batch {operation_type} operation: {e}")


    return affected_rows, errors
    return affected_rows, errors


    def execute_batch_operation(
    def execute_batch_operation(
    self,
    self,
    query: str,
    query: str,
    params_list: List[Tuple],
    params_list: List[Tuple],
    operation_type: str,
    operation_type: str,
    batch_size: int = None,
    batch_size: int = None,
    auto_commit: bool = True,
    auto_commit: bool = True,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Execute a batch database operation.
    Execute a batch database operation.


    Args:
    Args:
    query: SQL query to execute
    query: SQL query to execute
    params_list: List of parameter tuples for the query
    params_list: List of parameter tuples for the query
    operation_type: Type of operation ('insert', 'update', 'delete', 'query')
    operation_type: Type of operation ('insert', 'update', 'delete', 'query')
    batch_size: Size of each batch (defaults to default_batch_size)
    batch_size: Size of each batch (defaults to default_batch_size)
    auto_commit: Whether to automatically commit after each batch
    auto_commit: Whether to automatically commit after each batch


    Returns:
    Returns:
    DBBatchResult with operation results and statistics
    DBBatchResult with operation results and statistics
    """
    """
    effective_batch_size = batch_size or self.default_batch_size
    effective_batch_size = batch_size or self.default_batch_size
    batch_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())


    stats = BatchProcessingStats(
    stats = BatchProcessingStats(
    batch_id=batch_id, total_items=len(params_list), start_time=datetime.now()
    batch_id=batch_id, total_items=len(params_list), start_time=datetime.now()
    )
    )


    start_time = time.time()
    start_time = time.time()
    affected_rows = 0
    affected_rows = 0
    all_errors = []
    all_errors = []


    # Process in batches
    # Process in batches
    cursor = self.connection.cursor()
    cursor = self.connection.cursor()


    for i in range(0, len(params_list), effective_batch_size):
    for i in range(0, len(params_list), effective_batch_size):
    batch_params = params_list[i : i + effective_batch_size]
    batch_params = params_list[i : i + effective_batch_size]
    batch_affected_rows, batch_errors = self._execute_batch(
    batch_affected_rows, batch_errors = self._execute_batch(
    cursor=cursor,
    cursor=cursor,
    query=query,
    query=query,
    params_list=batch_params,
    params_list=batch_params,
    operation_type=operation_type,
    operation_type=operation_type,
    )
    )


    affected_rows += batch_affected_rows
    affected_rows += batch_affected_rows


    # Adjust error indices to match the original params_list
    # Adjust error indices to match the original params_list
    offset = i
    offset = i
    for idx, error in batch_errors:
    for idx, error in batch_errors:
    all_errors.append((offset + idx, error))
    all_errors.append((offset + idx, error))


    stats.processed_items += len(batch_params)
    stats.processed_items += len(batch_params)
    stats.successful_items += len(batch_params) - len(batch_errors)
    stats.successful_items += len(batch_params) - len(batch_errors)
    stats.failed_items += len(batch_errors)
    stats.failed_items += len(batch_errors)


    if auto_commit:
    if auto_commit:
    self.connection.commit()
    self.connection.commit()


    # Final commit if needed
    # Final commit if needed
    if not auto_commit:
    if not auto_commit:
    self.connection.commit()
    self.connection.commit()


    # Update stats
    # Update stats
    stats.end_time = datetime.now()
    stats.end_time = datetime.now()
    stats.processing_time_ms = (time.time() - start_time) * 1000
    stats.processing_time_ms = (time.time() - start_time) * 1000


    result = DBBatchResult(
    result = DBBatchResult(
    batch_id=batch_id,
    batch_id=batch_id,
    operation_type=operation_type,
    operation_type=operation_type,
    affected_rows=affected_rows,
    affected_rows=affected_rows,
    errors=all_errors,
    errors=all_errors,
    stats=stats,
    stats=stats,
    )
    )


    # Store in history
    # Store in history
    self.batch_history[batch_id] = result
    self.batch_history[batch_id] = result


    return result
    return result


    def batch_insert(
    def batch_insert(
    self,
    self,
    table_name: str,
    table_name: str,
    columns: List[str],
    columns: List[str],
    values_list: List[List[Any]],
    values_list: List[List[Any]],
    batch_size: int = None,
    batch_size: int = None,
    auto_commit: bool = True,
    auto_commit: bool = True,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Insert multiple rows into a table in batches.
    Insert multiple rows into a table in batches.


    Args:
    Args:
    table_name: Name of the table
    table_name: Name of the table
    columns: List of column names
    columns: List of column names
    values_list: List of value lists to insert
    values_list: List of value lists to insert
    batch_size: Size of each batch (defaults to default_batch_size)
    batch_size: Size of each batch (defaults to default_batch_size)
    auto_commit: Whether to automatically commit after each batch
    auto_commit: Whether to automatically commit after each batch


    Returns:
    Returns:
    DBBatchResult with insertion results and statistics
    DBBatchResult with insertion results and statistics
    """
    """
    # Create the INSERT query
    # Create the INSERT query
    placeholders = ", ".join(["?"] * len(columns))
    placeholders = ", ".join(["?"] * len(columns))
    columns_str = ", ".join(columns)
    columns_str = ", ".join(columns)
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"


    # Execute the batch operation
    # Execute the batch operation
    return self.execute_batch_operation(
    return self.execute_batch_operation(
    query=query,
    query=query,
    params_list=values_list,
    params_list=values_list,
    operation_type="insert",
    operation_type="insert",
    batch_size=batch_size,
    batch_size=batch_size,
    auto_commit=auto_commit,
    auto_commit=auto_commit,
    )
    )


    def batch_update(
    def batch_update(
    self,
    self,
    table_name: str,
    table_name: str,
    set_columns: List[str],
    set_columns: List[str],
    where_column: str,
    where_column: str,
    data_list: List[Tuple[List[Any], Any]],
    data_list: List[Tuple[List[Any], Any]],
    batch_size: int = None,
    batch_size: int = None,
    auto_commit: bool = True,
    auto_commit: bool = True,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Update multiple rows in a table in batches.
    Update multiple rows in a table in batches.


    Args:
    Args:
    table_name: Name of the table
    table_name: Name of the table
    set_columns: List of column names to update
    set_columns: List of column names to update
    where_column: Column name for the WHERE clause
    where_column: Column name for the WHERE clause
    data_list: List of tuples (set_values, where_value)
    data_list: List of tuples (set_values, where_value)
    batch_size: Size of each batch (defaults to default_batch_size)
    batch_size: Size of each batch (defaults to default_batch_size)
    auto_commit: Whether to automatically commit after each batch
    auto_commit: Whether to automatically commit after each batch


    Returns:
    Returns:
    DBBatchResult with update results and statistics
    DBBatchResult with update results and statistics
    """
    """
    # Create the UPDATE query
    # Create the UPDATE query
    set_clause = ", ".join([f"{col} = ?" for col in set_columns])
    set_clause = ", ".join([f"{col} = ?" for col in set_columns])
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = ?"
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = ?"


    # Prepare parameters for the query
    # Prepare parameters for the query
    params_list = [
    params_list = [
    tuple(set_values + [where_value]) for set_values, where_value in data_list
    tuple(set_values + [where_value]) for set_values, where_value in data_list
    ]
    ]


    # Execute the batch operation
    # Execute the batch operation
    return self.execute_batch_operation(
    return self.execute_batch_operation(
    query=query,
    query=query,
    params_list=params_list,
    params_list=params_list,
    operation_type="update",
    operation_type="update",
    batch_size=batch_size,
    batch_size=batch_size,
    auto_commit=auto_commit,
    auto_commit=auto_commit,
    )
    )


    def batch_delete(
    def batch_delete(
    self,
    self,
    table_name: str,
    table_name: str,
    where_column: str,
    where_column: str,
    key_list: List[Any],
    key_list: List[Any],
    batch_size: int = None,
    batch_size: int = None,
    auto_commit: bool = True,
    auto_commit: bool = True,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Delete multiple rows from a table in batches.
    Delete multiple rows from a table in batches.


    Args:
    Args:
    table_name: Name of the table
    table_name: Name of the table
    where_column: Column name for the WHERE clause
    where_column: Column name for the WHERE clause
    key_list: List of values to match in the WHERE clause
    key_list: List of values to match in the WHERE clause
    batch_size: Size of each batch (defaults to default_batch_size)
    batch_size: Size of each batch (defaults to default_batch_size)
    auto_commit: Whether to automatically commit after each batch
    auto_commit: Whether to automatically commit after each batch


    Returns:
    Returns:
    DBBatchResult with deletion results and statistics
    DBBatchResult with deletion results and statistics
    """
    """
    # Create the DELETE query
    # Create the DELETE query
    query = f"DELETE FROM {table_name} WHERE {where_column} = ?"
    query = f"DELETE FROM {table_name} WHERE {where_column} = ?"


    # Convert key_list to a list of single-element tuples
    # Convert key_list to a list of single-element tuples
    params_list = [(key,) for key in key_list]
    params_list = [(key,) for key in key_list]


    # Execute the batch operation
    # Execute the batch operation
    return self.execute_batch_operation(
    return self.execute_batch_operation(
    query=query,
    query=query,
    params_list=params_list,
    params_list=params_list,
    operation_type="delete",
    operation_type="delete",
    batch_size=batch_size,
    batch_size=batch_size,
    auto_commit=auto_commit,
    auto_commit=auto_commit,
    )
    )


    def batch_query(
    def batch_query(
    self,
    self,
    query: str,
    query: str,
    param_sets: List[Tuple],
    param_sets: List[Tuple],
    processor_func: Callable[[Any], R] = None,
    processor_func: Callable[[Any], R] = None,
    batch_size: int = None,
    batch_size: int = None,
    ) -> Dict[int, Union[List[Tuple], R, Exception]]:
    ) -> Dict[int, Union[List[Tuple], R, Exception]]:
    """
    """
    Execute multiple queries in batches and optionally process results.
    Execute multiple queries in batches and optionally process results.


    Args:
    Args:
    query: SQL query to execute
    query: SQL query to execute
    param_sets: List of parameter tuples for the query
    param_sets: List of parameter tuples for the query
    processor_func: Optional function to process each result set
    processor_func: Optional function to process each result set
    batch_size: Size of each batch (defaults to default_batch_size)
    batch_size: Size of each batch (defaults to default_batch_size)


    Returns:
    Returns:
    Dictionary mapping indices to results or exceptions
    Dictionary mapping indices to results or exceptions
    """
    """
    effective_batch_size = batch_size or self.default_batch_size
    effective_batch_size = batch_size or self.default_batch_size
    results = {}
    results = {}
    batch_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())


    stats = BatchProcessingStats(
    stats = BatchProcessingStats(
    batch_id=batch_id, total_items=len(param_sets), start_time=datetime.now()
    batch_id=batch_id, total_items=len(param_sets), start_time=datetime.now()
    )
    )


    start_time = time.time()
    start_time = time.time()
    cursor = self.connection.cursor()
    cursor = self.connection.cursor()


    for i, params in enumerate(param_sets):
    for i, params in enumerate(param_sets):
    try:
    try:
    cursor.execute(query, params)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    rows = cursor.fetchall()


    if processor_func:
    if processor_func:
    try:
    try:
    processed = processor_func(rows)
    processed = processor_func(rows)
    results[i] = processed
    results[i] = processed
except Exception as e:
except Exception as e:
    # Processing error
    # Processing error
    results[i] = e
    results[i] = e
    stats.failed_items += 1
    stats.failed_items += 1
    logger.error(
    logger.error(
    f"Error processing query result for index {i}: {e}"
    f"Error processing query result for index {i}: {e}"
    )
    )
    else:
    else:
    results[i] = rows
    results[i] = rows


    stats.successful_items += 1
    stats.successful_items += 1
except Exception as e:
except Exception as e:
    # Query execution error
    # Query execution error
    results[i] = e
    results[i] = e
    stats.failed_items += 1
    stats.failed_items += 1
    logger.error(f"Error executing query for index {i}: {e}")
    logger.error(f"Error executing query for index {i}: {e}")


    stats.processed_items += 1
    stats.processed_items += 1


    # Commit after each batch if we're using autocommit mode
    # Commit after each batch if we're using autocommit mode
    if i % effective_batch_size == effective_batch_size - 1:
    if i % effective_batch_size == effective_batch_size - 1:
    self.connection.commit()
    self.connection.commit()


    # Update stats
    # Update stats
    stats.end_time = datetime.now()
    stats.end_time = datetime.now()
    stats.processing_time_ms = (time.time() - start_time) * 1000
    stats.processing_time_ms = (time.time() - start_time) * 1000


    # Store batch operation information
    # Store batch operation information
    errors = [(i, e) for i, e in results.items() if isinstance(e, Exception)]
    errors = [(i, e) for i, e in results.items() if isinstance(e, Exception)]
    result = DBBatchResult(
    result = DBBatchResult(
    batch_id=batch_id,
    batch_id=batch_id,
    operation_type="query",
    operation_type="query",
    affected_rows=stats.successful_items,
    affected_rows=stats.successful_items,
    errors=errors,
    errors=errors,
    stats=stats,
    stats=stats,
    )
    )


    self.batch_history[batch_id] = result
    self.batch_history[batch_id] = result


    return results
    return results


    def get_batch_result(self, batch_id: str) -> Optional[DBBatchResult]:
    def get_batch_result(self, batch_id: str) -> Optional[DBBatchResult]:
    """
    """
    Get a batch result by its ID.
    Get a batch result by its ID.


    Args:
    Args:
    batch_id: ID of the batch operation
    batch_id: ID of the batch operation


    Returns:
    Returns:
    DBBatchResult if found, None otherwise
    DBBatchResult if found, None otherwise
    """
    """
    return self.batch_history.get(batch_id)
    return self.batch_history.get(batch_id)


    def get_recent_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
    def get_recent_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
    """
    """
    Get information about recent batch operations.
    Get information about recent batch operations.


    Args:
    Args:
    limit: Maximum number of batches to return
    limit: Maximum number of batches to return


    Returns:
    Returns:
    List of batch result dictionaries
    List of batch result dictionaries
    """
    """
    # Sort by end time (most recent first)
    # Sort by end time (most recent first)
    sorted_batches = sorted(
    sorted_batches = sorted(
    self.batch_history.values(),
    self.batch_history.values(),
    key=lambda r: r.stats.end_time if r.stats.end_time else datetime.min,
    key=lambda r: r.stats.end_time if r.stats.end_time else datetime.min,
    reverse=True,
    reverse=True,
    )
    )


    # Return limited number of batch summaries
    # Return limited number of batch summaries
    return [batch.to_dict() for batch in sorted_batches[:limit]]
    return [batch.to_dict() for batch in sorted_batches[:limit]]




    # Convenience functions for database batch operations
    # Convenience functions for database batch operations
    def batch_insert(
    def batch_insert(
    connection: Union[sqlite3.Connection, Any],
    connection: Union[sqlite3.Connection, Any],
    table_name: str,
    table_name: str,
    columns: List[str],
    columns: List[str],
    values_list: List[List[Any]],
    values_list: List[List[Any]],
    batch_size: int = 100,
    batch_size: int = 100,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Insert multiple rows into a table in batches.
    Insert multiple rows into a table in batches.


    Args:
    Args:
    connection: Database connection
    connection: Database connection
    table_name: Name of the table
    table_name: Name of the table
    columns: List of column names
    columns: List of column names
    values_list: List of value lists to insert
    values_list: List of value lists to insert
    batch_size: Size of each batch
    batch_size: Size of each batch


    Returns:
    Returns:
    DBBatchResult with insertion results and statistics
    DBBatchResult with insertion results and statistics
    """
    """
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    return processor.batch_insert(table_name, columns, values_list, batch_size)
    return processor.batch_insert(table_name, columns, values_list, batch_size)




    def batch_update(
    def batch_update(
    connection: Union[sqlite3.Connection, Any],
    connection: Union[sqlite3.Connection, Any],
    table_name: str,
    table_name: str,
    set_columns: List[str],
    set_columns: List[str],
    where_column: str,
    where_column: str,
    data_list: List[Tuple[List[Any], Any]],
    data_list: List[Tuple[List[Any], Any]],
    batch_size: int = 100,
    batch_size: int = 100,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Update multiple rows in a table in batches.
    Update multiple rows in a table in batches.


    Args:
    Args:
    connection: Database connection
    connection: Database connection
    table_name: Name of the table
    table_name: Name of the table
    set_columns: List of column names to update
    set_columns: List of column names to update
    where_column: Column name for the WHERE clause
    where_column: Column name for the WHERE clause
    data_list: List of tuples (set_values, where_value)
    data_list: List of tuples (set_values, where_value)
    batch_size: Size of each batch
    batch_size: Size of each batch


    Returns:
    Returns:
    DBBatchResult with update results and statistics
    DBBatchResult with update results and statistics
    """
    """
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    return processor.batch_update(
    return processor.batch_update(
    table_name, set_columns, where_column, data_list, batch_size
    table_name, set_columns, where_column, data_list, batch_size
    )
    )




    def batch_delete(
    def batch_delete(
    connection: Union[sqlite3.Connection, Any],
    connection: Union[sqlite3.Connection, Any],
    table_name: str,
    table_name: str,
    where_column: str,
    where_column: str,
    key_list: List[Any],
    key_list: List[Any],
    batch_size: int = 100,
    batch_size: int = 100,
    ) -> DBBatchResult:
    ) -> DBBatchResult:
    """
    """
    Delete multiple rows from a table in batches.
    Delete multiple rows from a table in batches.


    Args:
    Args:
    connection: Database connection
    connection: Database connection
    table_name: Name of the table
    table_name: Name of the table
    where_column: Column name for the WHERE clause
    where_column: Column name for the WHERE clause
    key_list: List of values to match in the WHERE clause
    key_list: List of values to match in the WHERE clause
    batch_size: Size of each batch
    batch_size: Size of each batch


    Returns:
    Returns:
    DBBatchResult with deletion results and statistics
    DBBatchResult with deletion results and statistics
    """
    """
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    return processor.batch_delete(table_name, where_column, key_list, batch_size)
    return processor.batch_delete(table_name, where_column, key_list, batch_size)