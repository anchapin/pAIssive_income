"""
Database batch operations utility.

This module provides utilities for performing database operations in batches,
including inserting, updating, and querying large sets of data efficiently.
"""

import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from .batch_utils import BatchProcessingStats

# Type variables for generic functions
T = TypeVar("T")  # Input item type
R = TypeVar("R")  # Result item type

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
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
    Class for performing database operations in batches.
    """

    def __init__(self, connection: Union[sqlite3.Connection, Any], 
        default_batch_size: int = 100):
        """
        Initialize the batch processor.

        Args:
            connection: Database connection (SQLite or other DB - \
                API 2.0 compliant connection)
            default_batch_size: Default size for each batch
        """
        self.connection = connection
        self.default_batch_size = default_batch_size
        self.batch_history = {}

        # Detect if we're using SQLite
        self.is_sqlite = isinstance(connection, sqlite3.Connection)

    def _execute_batch(
        self, cursor: Any, query: str, params_list: List[Tuple], operation_type: str
    ) -> Tuple[int, List[Tuple[int, Exception]]]:
        """
        Execute a batch of the same query with different parameters.

        Args:
            cursor: Database cursor
            query: SQL query to execute
            params_list: List of parameter tuples
            operation_type: Type of operation ('insert', 'update', 'delete', 'query')

        Returns:
            Tuple of (affected_rows, list of errors)
        """
        affected_rows = 0
        errors = []

        if not params_list:
            return 0, []

        # Execute batch based on database type
        if self.is_sqlite:
            # SQLite doesn't have native batch support, so execute individually
            for i, params in enumerate(params_list):
                try:
                    cursor.execute(query, params)
                    if operation_type in ("insert", "update", "delete"):
                        affected_rows += cursor.rowcount
                except Exception as e:
                    errors.append((i, e))
                    logger.error(f"Error executing {operation_type} operation: {e}")
        else:
            # For other databases, try to use execute_batch if available
            # This is available in some database adapters like psycopg2
            try:
                if hasattr(cursor, "executemany"):
                    cursor.executemany(query, params_list)
                    affected_rows = cursor.rowcount
                else:
                    # Fall back to individual execution
                    for i, params in enumerate(params_list):
                        try:
                            cursor.execute(query, params)
                            affected_rows += cursor.rowcount
                        except Exception as e:
                            errors.append((i, e))
                            logger.error(
                                f"Error executing {operation_type} operation: {e}")
            except Exception as e:
                for i in range(len(params_list)):
                    errors.append((i, e))
                logger.error(f"Error executing batch {operation_type} operation: {e}")

        return affected_rows, errors

    def execute_batch_operation(
        self,
        query: str,
        params_list: List[Tuple],
        operation_type: str,
        batch_size: int = None,
        auto_commit: bool = True,
    ) -> DBBatchResult:
        """
        Execute a batch database operation.

        Args:
            query: SQL query to execute
            params_list: List of parameter tuples for the query
            operation_type: Type of operation ('insert', 'update', 'delete', 'query')
            batch_size: Size of each batch (defaults to default_batch_size)
            auto_commit: Whether to automatically commit after each batch

        Returns:
            DBBatchResult with operation results and statistics
        """
        effective_batch_size = batch_size or self.default_batch_size
        batch_id = str(uuid.uuid4())

        stats = BatchProcessingStats(
            batch_id=batch_id, total_items=len(params_list), start_time=datetime.now()
        )

        start_time = time.time()
        affected_rows = 0
        all_errors = []

        # Process in batches
        cursor = self.connection.cursor()

        for i in range(0, len(params_list), effective_batch_size):
            batch_params = params_list[i : i + effective_batch_size]
            batch_affected_rows, batch_errors = self._execute_batch(
                cursor=cursor,
                query=query,
                params_list=batch_params,
                operation_type=operation_type,
            )

            affected_rows += batch_affected_rows

            # Adjust error indices to match the original params_list
            offset = i
            for idx, error in batch_errors:
                all_errors.append((offset + idx, error))

            stats.processed_items += len(batch_params)
            stats.successful_items += len(batch_params) - len(batch_errors)
            stats.failed_items += len(batch_errors)

            if auto_commit:
                self.connection.commit()

        # Final commit if needed
        if not auto_commit:
            self.connection.commit()

        # Update stats
        stats.end_time = datetime.now()
        stats.processing_time_ms = (time.time() - start_time) * 1000

        result = DBBatchResult(
            batch_id=batch_id,
            operation_type=operation_type,
            affected_rows=affected_rows,
            errors=all_errors,
            stats=stats,
        )

        # Store in history
        self.batch_history[batch_id] = result

        return result

    def batch_insert(
        self,
        table_name: str,
        columns: List[str],
        values_list: List[List[Any]],
        batch_size: int = None,
        auto_commit: bool = True,
    ) -> DBBatchResult:
        """
        Insert multiple rows into a table in batches.

        Args:
            table_name: Name of the table
            columns: List of column names
            values_list: List of value lists to insert
            batch_size: Size of each batch (defaults to default_batch_size)
            auto_commit: Whether to automatically commit after each batch

        Returns:
            DBBatchResult with insertion results and statistics
        """
        # Create the INSERT query
        placeholders = ", ".join(["?"] * len(columns))
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        # Execute the batch operation
        return self.execute_batch_operation(
            query=query,
            params_list=values_list,
            operation_type="insert",
            batch_size=batch_size,
            auto_commit=auto_commit,
        )

    def batch_update(
        self,
        table_name: str,
        set_columns: List[str],
        where_column: str,
        data_list: List[Tuple[List[Any], Any]],
        batch_size: int = None,
        auto_commit: bool = True,
    ) -> DBBatchResult:
        """
        Update multiple rows in a table in batches.

        Args:
            table_name: Name of the table
            set_columns: List of column names to update
            where_column: Column name for the WHERE clause
            data_list: List of tuples (set_values, where_value)
            batch_size: Size of each batch (defaults to default_batch_size)
            auto_commit: Whether to automatically commit after each batch

        Returns:
            DBBatchResult with update results and statistics
        """
        # Create the UPDATE query
        set_clause = ", ".join([f"{col} = ?" for col in set_columns])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = ?"

        # Prepare parameters for the query
        params_list = [tuple(set_values + [where_value]) for set_values, 
            where_value in data_list]

        # Execute the batch operation
        return self.execute_batch_operation(
            query=query,
            params_list=params_list,
            operation_type="update",
            batch_size=batch_size,
            auto_commit=auto_commit,
        )

    def batch_delete(
        self,
        table_name: str,
        where_column: str,
        key_list: List[Any],
        batch_size: int = None,
        auto_commit: bool = True,
    ) -> DBBatchResult:
        """
        Delete multiple rows from a table in batches.

        Args:
            table_name: Name of the table
            where_column: Column name for the WHERE clause
            key_list: List of values to match in the WHERE clause
            batch_size: Size of each batch (defaults to default_batch_size)
            auto_commit: Whether to automatically commit after each batch

        Returns:
            DBBatchResult with deletion results and statistics
        """
        # Create the DELETE query
        query = f"DELETE FROM {table_name} WHERE {where_column} = ?"

        # Convert key_list to a list of single - element tuples
        params_list = [(key,) for key in key_list]

        # Execute the batch operation
        return self.execute_batch_operation(
            query=query,
            params_list=params_list,
            operation_type="delete",
            batch_size=batch_size,
            auto_commit=auto_commit,
        )

    def batch_query(
        self,
        query: str,
        param_sets: List[Tuple],
        processor_func: Callable[[Any], R] = None,
        batch_size: int = None,
    ) -> Dict[int, Union[List[Tuple], R, Exception]]:
        """
        Execute multiple queries in batches and optionally process results.

        Args:
            query: SQL query to execute
            param_sets: List of parameter tuples for the query
            processor_func: Optional function to process each result set
            batch_size: Size of each batch (defaults to default_batch_size)

        Returns:
            Dictionary mapping indices to results or exceptions
        """
        effective_batch_size = batch_size or self.default_batch_size
        results = {}
        batch_id = str(uuid.uuid4())

        stats = BatchProcessingStats(
            batch_id=batch_id, total_items=len(param_sets), start_time=datetime.now()
        )

        start_time = time.time()
        cursor = self.connection.cursor()

        for i, params in enumerate(param_sets):
            try:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                if processor_func:
                    try:
                        processed = processor_func(rows)
                        results[i] = processed
                    except Exception as e:
                        # Processing error
                        results[i] = e
                        stats.failed_items += 1
                        logger.error(
                            f"Error processing query result for index {i}: {e}")
                else:
                    results[i] = rows

                stats.successful_items += 1
            except Exception as e:
                # Query execution error
                results[i] = e
                stats.failed_items += 1
                logger.error(f"Error executing query for index {i}: {e}")

            stats.processed_items += 1

            # Commit after each batch if we're using autocommit mode
            if i % effective_batch_size == effective_batch_size - 1:
                self.connection.commit()

        # Update stats
        stats.end_time = datetime.now()
        stats.processing_time_ms = (time.time() - start_time) * 1000

        # Store batch operation information
        errors = [(i, e) for i, e in results.items() if isinstance(e, Exception)]
        result = DBBatchResult(
            batch_id=batch_id,
            operation_type="query",
            affected_rows=stats.successful_items,
            errors=errors,
            stats=stats,
        )

        self.batch_history[batch_id] = result

        return results

    def get_batch_result(self, batch_id: str) -> Optional[DBBatchResult]:
        """
        Get a batch result by its ID.

        Args:
            batch_id: ID of the batch operation

        Returns:
            DBBatchResult if found, None otherwise
        """
        return self.batch_history.get(batch_id)

    def get_recent_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get information about recent batch operations.

        Args:
            limit: Maximum number of batches to return

        Returns:
            List of batch result dictionaries
        """
        # Sort by end time (most recent first)
        sorted_batches = sorted(
            self.batch_history.values(),
            key=lambda r: r.stats.end_time if r.stats.end_time else datetime.min,
            reverse=True,
        )

        # Return limited number of batch summaries
        return [batch.to_dict() for batch in sorted_batches[:limit]]


# Convenience functions for database batch operations
def batch_insert(
    connection: Union[sqlite3.Connection, Any],
    table_name: str,
    columns: List[str],
    values_list: List[List[Any]],
    batch_size: int = 100,
) -> DBBatchResult:
    """
    Insert multiple rows into a table in batches.

    Args:
        connection: Database connection
        table_name: Name of the table
        columns: List of column names
        values_list: List of value lists to insert
        batch_size: Size of each batch

    Returns:
        DBBatchResult with insertion results and statistics
    """
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    return processor.batch_insert(table_name, columns, values_list, batch_size)


def batch_update(
    connection: Union[sqlite3.Connection, Any],
    table_name: str,
    set_columns: List[str],
    where_column: str,
    data_list: List[Tuple[List[Any], Any]],
    batch_size: int = 100,
) -> DBBatchResult:
    """
    Update multiple rows in a table in batches.

    Args:
        connection: Database connection
        table_name: Name of the table
        set_columns: List of column names to update
        where_column: Column name for the WHERE clause
        data_list: List of tuples (set_values, where_value)
        batch_size: Size of each batch

    Returns:
        DBBatchResult with update results and statistics
    """
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    return processor.batch_update(table_name, set_columns, where_column, data_list, 
        batch_size)


def batch_delete(
    connection: Union[sqlite3.Connection, Any],
    table_name: str,
    where_column: str,
    key_list: List[Any],
    batch_size: int = 100,
) -> DBBatchResult:
    """
    Delete multiple rows from a table in batches.

    Args:
        connection: Database connection
        table_name: Name of the table
        where_column: Column name for the WHERE clause
        key_list: List of values to match in the WHERE clause
        batch_size: Size of each batch

    Returns:
        DBBatchResult with deletion results and statistics
    """
    processor = DBBatchProcessor(connection, default_batch_size=batch_size)
    return processor.batch_delete(table_name, where_column, key_list, batch_size)
