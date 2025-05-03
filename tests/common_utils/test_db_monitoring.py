"""
Tests for database monitoring functionality.

This module tests the database performance monitoring, including query timing,
slow query detection, and performance reporting.
"""

import os
import sqlite3
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from common_utils.db.monitoring import DatabaseMetrics, MonitoringDatabaseProxy


@pytest.fixture
def mock_db():
    """Create a mock database interface."""
    db = MagicMock()
    db.execute.return_value = None
    db.fetch_one.return_value = {"id": 1, "name": "Test"}
    db.fetch_all.return_value = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test 2"}]
    db.insert.return_value = 1
    db.update.return_value = 1
    db.delete.return_value = 1
    return db


@pytest.fixture
def db_metrics():
    """Create a database metrics instance."""
    return DatabaseMetrics()


@pytest.fixture
def monitoring_db(mock_db):
    """Create a monitoring database proxy."""
    return MonitoringDatabaseProxy(mock_db)


def test_database_metrics_init(db_metrics):
    """Test DatabaseMetrics initialization."""
    assert db_metrics.query_count == 0
    assert db_metrics.total_query_time == 0.0
    assert db_metrics.queries == []
    assert db_metrics.slow_threshold == 0.5


def test_database_metrics_record_query(db_metrics):
    """Test recording a query in DatabaseMetrics."""
    db_metrics.record_query(
        query="SELECT * FROM users", params=None, duration=0.1, operation="select"
    )

    assert db_metrics.query_count == 1
    assert db_metrics.total_query_time == 0.1
    assert len(db_metrics.queries) == 1

    query_record = db_metrics.queries[0]
    assert query_record["query"] == "SELECT * FROM users"
    assert query_record["params"] is None
    assert query_record["duration"] == 0.1
    assert query_record["operation"] == "select"
    assert "timestamp" in query_record
    assert not query_record["is_slow"]


def test_database_metrics_record_slow_query(db_metrics):
    """Test recording a slow query in DatabaseMetrics."""
    # Set a lower slow threshold for testing
    db_metrics.slow_threshold = 0.1

    db_metrics.record_query(
        query="SELECT * FROM users",
        params=None,
        duration=0.2,  # > slow_threshold
        operation="select",
    )

    assert db_metrics.query_count == 1
    assert db_metrics.total_query_time == 0.2
    assert len(db_metrics.queries) == 1

    query_record = db_metrics.queries[0]
    assert query_record["is_slow"]


def test_database_metrics_reset(db_metrics):
    """Test resetting DatabaseMetrics."""
    # Record some queries
    db_metrics.record_query(
        query="SELECT * FROM users", params=None, duration=0.1, operation="select"
    )

    db_metrics.record_query(
        query="INSERT INTO users (name) VALUES (?)",
        params={"name": "Test"},
        duration=0.2,
        operation="insert",
    )

    # Verify initial state
    assert db_metrics.query_count == 2
    assert db_metrics.total_query_time == 0.3
    assert len(db_metrics.queries) == 2

    # Reset metrics
    db_metrics.reset()

    # Verify reset state
    assert db_metrics.query_count == 0
    assert db_metrics.total_query_time == 0.0
    assert db_metrics.queries == []


def test_database_metrics_get_slow_queries(db_metrics):
    """Test getting slow queries from DatabaseMetrics."""
    # Set a lower slow threshold for testing
    db_metrics.slow_threshold = 0.2

    # Record some queries, some slow and some not
    db_metrics.record_query(
        query="SELECT * FROM users", params=None, duration=0.1, 
            operation="select"  # Not slow
    )

    db_metrics.record_query(
        query="SELECT * FROM users WHERE id = ?",
        params={"id": 1},
        duration=0.3,  # Slow
        operation="select",
    )

    db_metrics.record_query(
        query="INSERT INTO users (name) VALUES (?)",
        params={"name": "Test"},
        duration=0.4,  # Slow
        operation="insert",
    )

    # Get slow queries
    slow_queries = db_metrics.get_slow_queries()

    # Verify slow queries
    assert len(slow_queries) == 2
    assert slow_queries[0]["query"] == "SELECT * FROM users WHERE id = ?"
    assert slow_queries[1]["query"] == "INSERT INTO users (name) VALUES (?)"


def test_database_metrics_get_summary(db_metrics):
    """Test getting a summary from DatabaseMetrics."""
    # Record some queries
    db_metrics.record_query(
        query="SELECT * FROM users", params=None, duration=0.1, operation="select"
    )

    db_metrics.record_query(
        query="SELECT * FROM users WHERE id = ?", params={"id": 1}, duration=0.3, 
            operation="select"
    )

    db_metrics.record_query(
        query="INSERT INTO users (name) VALUES (?)",
        params={"name": "Test"},
        duration=0.2,
        operation="insert",
    )

    # Get summary
    summary = db_metrics.get_summary()

    # Verify summary
    assert summary["query_count"] == 3
    assert summary["total_query_time"] == 0.6
    assert summary["average_query_time"] == 0.2
    assert summary["operation_counts"]["select"] == 2
    assert summary["operation_counts"]["insert"] == 1


def test_monitoring_database_proxy_execute(monitoring_db, mock_db):
    """Test execute method of MonitoringDatabaseProxy."""
    # Execute a query
    monitoring_db.execute("SELECT * FROM users")

    # Verify that the underlying database was called
    mock_db.execute.assert_called_once_with("SELECT * FROM users", None)

    # Verify that metrics were recorded
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 1
    assert len(metrics.queries) == 1
    assert metrics.queries[0]["query"] == "SELECT * FROM users"
    assert metrics.queries[0]["operation"] == "execute"


def test_monitoring_database_proxy_fetch_one(monitoring_db, mock_db):
    """Test fetch_one method of MonitoringDatabaseProxy."""
    # Fetch one record
    result = monitoring_db.fetch_one("SELECT * FROM users WHERE id = ?", {"id": 1})

    # Verify that the underlying database was called
    mock_db.fetch_one.assert_called_once_with("SELECT * FROM users WHERE id = ?", 
        {"id": 1})

    # Verify that the result is correct
    assert result == {"id": 1, "name": "Test"}

    # Verify that metrics were recorded
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 1
    assert len(metrics.queries) == 1
    assert metrics.queries[0]["query"] == "SELECT * FROM users WHERE id = ?"
    assert metrics.queries[0]["operation"] == "fetch_one"


def test_monitoring_database_proxy_fetch_all(monitoring_db, mock_db):
    """Test fetch_all method of MonitoringDatabaseProxy."""
    # Fetch all records
    result = monitoring_db.fetch_all("SELECT * FROM users")

    # Verify that the underlying database was called
    mock_db.fetch_all.assert_called_once_with("SELECT * FROM users", None)

    # Verify that the result is correct
    assert result == [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test 2"}]

    # Verify that metrics were recorded
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 1
    assert len(metrics.queries) == 1
    assert metrics.queries[0]["query"] == "SELECT * FROM users"
    assert metrics.queries[0]["operation"] == "fetch_all"


def test_monitoring_database_proxy_insert(monitoring_db, mock_db):
    """Test insert method of MonitoringDatabaseProxy."""
    # Insert a record
    result = monitoring_db.insert("users", {"name": "Test"})

    # Verify that the underlying database was called
    mock_db.insert.assert_called_once_with("users", {"name": "Test"})

    # Verify that the result is correct
    assert result == 1

    # Verify that metrics were recorded
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 1
    assert len(metrics.queries) == 1
    assert metrics.queries[0]["operation"] == "insert"


def test_monitoring_database_proxy_update(monitoring_db, mock_db):
    """Test update method of MonitoringDatabaseProxy."""
    # Update a record
    result = monitoring_db.update("users", {"name": "Updated"}, "id = ?", {"id": 1})

    # Verify that the underlying database was called
    mock_db.update.assert_called_once_with("users", {"name": "Updated"}, "id = ?", 
        {"id": 1})

    # Verify that the result is correct
    assert result == 1

    # Verify that metrics were recorded
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 1
    assert len(metrics.queries) == 1
    assert metrics.queries[0]["operation"] == "update"


def test_monitoring_database_proxy_delete(monitoring_db, mock_db):
    """Test delete method of MonitoringDatabaseProxy."""
    # Delete a record
    result = monitoring_db.delete("users", "id = ?", {"id": 1})

    # Verify that the underlying database was called
    mock_db.delete.assert_called_once_with("users", "id = ?", {"id": 1})

    # Verify that the result is correct
    assert result == 1

    # Verify that metrics were recorded
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 1
    assert len(metrics.queries) == 1
    assert metrics.queries[0]["operation"] == "delete"


def test_monitoring_database_proxy_get_performance_report(monitoring_db):
    """Test get_performance_report method of MonitoringDatabaseProxy."""
    # Execute some queries
    monitoring_db.execute("SELECT * FROM users")
    monitoring_db.fetch_one("SELECT * FROM users WHERE id = ?", {"id": 1})
    monitoring_db.insert("users", {"name": "Test"})

    # Get performance report
    report = monitoring_db.get_performance_report()

    # Verify report structure
    assert "summary" in report
    assert "slow_queries" in report
    assert "recent_queries" in report

    # Verify summary
    assert report["summary"]["query_count"] == 3
    assert "total_query_time" in report["summary"]
    assert "average_query_time" in report["summary"]
    assert "operation_counts" in report["summary"]

    # Verify recent queries
    assert len(report["recent_queries"]) == 3
    assert report["recent_queries"][0]["query"] == "SELECT * FROM users"
    assert report["recent_queries"][1]["query"] == "SELECT * FROM users WHERE id = ?"
    assert report["recent_queries"][2]["operation"] == "insert"


def test_monitoring_database_proxy_reset_metrics(monitoring_db):
    """Test reset_metrics method of MonitoringDatabaseProxy."""
    # Execute some queries
    monitoring_db.execute("SELECT * FROM users")
    monitoring_db.fetch_one("SELECT * FROM users WHERE id = ?", {"id": 1})

    # Verify initial state
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 2

    # Reset metrics
    monitoring_db.reset_metrics()

    # Verify reset state
    metrics = monitoring_db.get_metrics()
    assert metrics.query_count == 0
    assert metrics.total_query_time == 0.0
    assert metrics.queries == []


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Clean up
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_real_sqlite_database(temp_db_path):
    """Test monitoring with a real SQLite database."""
    # Create a real SQLite database
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Create a test table
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()

    # Create a mock database interface that uses the real SQLite database
    class SQLiteDB:
        def __init__(self, db_path):
            self.db_path = db_path
            self.conn = None

        def connect(self):
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

        def execute(self, query, params=None):
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()

        def fetch_one(self, query, params=None):
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

        def fetch_all(self, query, params=None):
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        def insert(self, table, data):
            cursor = self.conn.cursor()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            self.conn.commit()
            return cursor.lastrowid

    # Create a database with monitoring
    db = SQLiteDB(temp_db_path)
    db.connect()
    db_with_monitoring = MonitoringDatabaseProxy(db)

    # Insert some test data
    db_with_monitoring.insert("users", {"name": "User 1"})
    db_with_monitoring.insert("users", {"name": "User 2"})
    db_with_monitoring.insert("users", {"name": "User 3"})

    # Query the data
    users = db_with_monitoring.fetch_all("SELECT * FROM users")

    # Verify the data
    assert len(users) == 3
    assert users[0]["name"] == "User 1"
    assert users[1]["name"] == "User 2"
    assert users[2]["name"] == "User 3"

    # Get performance metrics
    metrics = db_with_monitoring.get_metrics()
    assert metrics.query_count == 4  # 3 inserts + 1 select

    # Get performance report
    report = db_with_monitoring.get_performance_report()
    assert report["summary"]["query_count"] == 4
    assert len(report["recent_queries"]) == 4

    # Close the connection
    conn.close()


if __name__ == "__main__":
    pytest.main([" - xvs", __file__])
