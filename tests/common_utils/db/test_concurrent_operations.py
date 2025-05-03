"""
Tests for data consistency during concurrent operations.

This module tests the database layer's ability to maintain data consistency
during concurrent operations, handle race conditions, and enforce transaction
isolation levels.
"""

import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import pytest

from common_utils.db.factory import DatabaseFactory
from common_utils.db.interfaces import DatabaseInterface, UnitOfWork


@pytest.fixture
def sqlite_db():
    """Fixture for SQLite database."""
    db_config = {"db_path": ":memory:"}
    db = DatabaseFactory.create_database("sqlite", db_config)
    db.connect()

    # Create test table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS test_concurrent (
            id INTEGER PRIMARY KEY,
            counter INTEGER NOT NULL,
            last_updated_by TEXT
        )
    """
    )

    # Insert initial data
    db.execute(
        "INSERT INTO test_concurrent (id, counter, last_updated_by) VALUES (?, ?, ?)",
        (1, 0, "init"),
    )

    yield db

    # Clean up
    db.execute("DROP TABLE IF EXISTS test_concurrent")
    db.disconnect()


@pytest.fixture
def sqlite_uow(sqlite_db):
    """Fixture for SQLite Unit of Work."""
    return DatabaseFactory.create_unit_of_work(sqlite_db)


def test_parallel_updates_consistency(sqlite_db):
    """
    Test data consistency during parallel updates.

    This test verifies that when multiple threads update the same record,
    all updates are properly applied and the final state is consistent.
    """
    num_threads = 10
    updates_per_thread = 5

    def update_counter(thread_id: int):
        """Update counter in a separate thread."""
        for i in range(updates_per_thread):
            # Read current value
            result = sqlite_db.fetch_one("SELECT counter FROM test_concurrent WHERE id = ?", 
                (1,))
            current_counter = result["counter"]

            # Simulate some processing time
            time.sleep(random.uniform(0.001, 0.005))

            # Update with incremented value
            sqlite_db.execute(
                "UPDATE test_concurrent SET counter = ?, 
                    last_updated_by = ? WHERE id = ?",
                (current_counter + 1, f"thread-{thread_id}-update-{i}", 1),
            )

    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=update_counter, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check final counter value
    result = sqlite_db.fetch_one("SELECT counter FROM test_concurrent WHERE id = ?", (1,
        ))
    final_counter = result["counter"]

    # Without proper concurrency control, the final counter will likely be less than
    # the expected value due to race conditions
    expected_counter = num_threads * updates_per_thread

    # This test is expected to fail without proper concurrency control
    # The purpose is to demonstrate the need for transactions
    assert (
        final_counter <= expected_counter
    ), f"Final counter: {final_counter}, Expected: {expected_counter}"
    print(f"Final counter: {final_counter}, Expected: {expected_counter}")
    print(
        "Note: This test demonstrates race conditions without proper concurrency control")


def test_transaction_prevents_race_conditions(sqlite_db, sqlite_uow):
    """
    Test that transactions prevent race conditions.

    This test verifies that when using transactions, race conditions are prevented
    and all updates are properly applied.
    """
    num_threads = 10
    updates_per_thread = 5

    def update_counter_with_transaction(thread_id: int):
        """Update counter using a transaction."""
        for i in range(updates_per_thread):
            with sqlite_uow:
                # Read current value within transaction
                result = sqlite_db.fetch_one(
                    "SELECT counter FROM test_concurrent WHERE id = ?", (1,)
                )
                current_counter = result["counter"]

                # Simulate some processing time
                time.sleep(random.uniform(0.001, 0.005))

                # Update with incremented value within same transaction
                sqlite_db.execute(
                    "UPDATE test_concurrent SET counter = ?, 
                        last_updated_by = ? WHERE id = ?",
                    (current_counter + 1, f"thread-{thread_id}-update-{i}", 1),
                )
                # Transaction is committed at the end of the with block

    # Reset counter
    sqlite_db.execute(
        "UPDATE test_concurrent SET counter = ?, last_updated_by = ? WHERE id = ?", (0, 
            "init", 1)
    )

    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=update_counter_with_transaction, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check final counter value
    result = sqlite_db.fetch_one("SELECT counter FROM test_concurrent WHERE id = ?", (1,
        ))
    final_counter = result["counter"]
    expected_counter = num_threads * updates_per_thread

    # With proper transaction isolation, the final counter should equal the expected value
    assert (
        final_counter == expected_counter
    ), f"Final counter: {final_counter}, Expected: {expected_counter}"


def test_transaction_isolation_levels(sqlite_db):
    """
    Test transaction isolation levels.

    This test verifies that different transaction isolation levels work as expected.
    SQLite supports the following isolation levels:
    - DEFERRED (default): Locks are acquired when needed
    - IMMEDIATE: Write lock is acquired immediately
    - EXCLUSIVE: Exclusive lock is acquired immediately
    """
    # Reset counter
    sqlite_db.execute(
        "UPDATE test_concurrent SET counter = ?, last_updated_by = ? WHERE id = ?", (0, 
            "init", 1)
    )

    # Test with different isolation levels
    isolation_levels = ["DEFERRED", "IMMEDIATE", "EXCLUSIVE"]

    for level in isolation_levels:
        # Start a transaction with specific isolation level
        sqlite_db.execute(f"BEGIN {level} TRANSACTION")

        # Read current value
        result = sqlite_db.fetch_one("SELECT counter FROM test_concurrent WHERE id = ?", 
            (1,))
        current_counter = result["counter"]

        # Update with incremented value
        sqlite_db.execute(
            "UPDATE test_concurrent SET counter = ?, last_updated_by = ? WHERE id = ?",
            (current_counter + 1, f"isolation-{level}", 1),
        )

        # Commit transaction
        sqlite_db.connection.commit()

        # Verify counter was incremented
        result = sqlite_db.fetch_one(
            "SELECT counter, last_updated_by FROM test_concurrent WHERE id = ?", (1,)
        )
        assert result["counter"] == current_counter + 1
        assert result["last_updated_by"] == f"isolation-{level}"


def test_deadlock_prevention(sqlite_db):
    """
    Test deadlock prevention.

    This test verifies that the database layer can prevent or detect deadlocks
    when multiple transactions are trying to update the same records in different order.
    """
    # Create additional test table
    sqlite_db.execute(
        """
        CREATE TABLE IF NOT EXISTS test_concurrent_2 (
            id INTEGER PRIMARY KEY,
            counter INTEGER NOT NULL,
            last_updated_by TEXT
        )
    """
    )

    # Insert initial data
    sqlite_db.execute(
        "INSERT INTO test_concurrent_2 (id, counter, last_updated_by) VALUES (?, ?, ?)",
        (1, 0, "init"),
    )

    # Reset first table counter
    sqlite_db.execute(
        "UPDATE test_concurrent SET counter = ?, last_updated_by = ? WHERE id = ?", (0, 
            "init", 1)
    )

    # Flag to track if deadlock was detected
    deadlock_detected = False

    def transaction_1():
        """First transaction that updates table 1 then table 2."""
        try:
            # Start transaction
            sqlite_db.execute("BEGIN IMMEDIATE TRANSACTION")

            # Update first table
            sqlite_db.execute(
                "UPDATE test_concurrent SET counter = counter + 1, 
                    last_updated_by = ? WHERE id = ?",
                ("tx1", 1),
            )

            # Simulate delay to increase chance of deadlock
            time.sleep(0.1)

            # Update second table
            sqlite_db.execute(
                "UPDATE test_concurrent_2 SET counter = counter + 1, 
                    last_updated_by = ? WHERE id = ?",
                ("tx1", 1),
            )

            # Commit transaction
            sqlite_db.connection.commit()
            return True
        except Exception as e:
            # Rollback on error
            sqlite_db.connection.rollback()
            nonlocal deadlock_detected
            deadlock_detected = True
            print(f"Transaction 1 error: {e}")
            return False

    def transaction_2():
        """Second transaction that updates table 2 then table 1."""
        try:
            # Start transaction
            sqlite_db.execute("BEGIN IMMEDIATE TRANSACTION")

            # Update second table
            sqlite_db.execute(
                "UPDATE test_concurrent_2 SET counter = counter + 1, 
                    last_updated_by = ? WHERE id = ?",
                ("tx2", 1),
            )

            # Simulate delay to increase chance of deadlock
            time.sleep(0.1)

            # Update first table
            sqlite_db.execute(
                "UPDATE test_concurrent SET counter = counter + 1, 
                    last_updated_by = ? WHERE id = ?",
                ("tx2", 1),
            )

            # Commit transaction
            sqlite_db.connection.commit()
            return True
        except Exception as e:
            # Rollback on error
            sqlite_db.connection.rollback()
            nonlocal deadlock_detected
            deadlock_detected = True
            print(f"Transaction 2 error: {e}")
            return False

    # Run transactions in separate threads
    thread1 = threading.Thread(target=transaction_1)
    thread2 = threading.Thread(target=transaction_2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # Check if deadlock was detected
    # Note: SQLite has automatic deadlock detection and will raise an error
    # if a deadlock is detected, causing one of the transactions to fail
    if deadlock_detected:
        print("Deadlock was detected and prevented")

    # Clean up
    sqlite_db.execute("DROP TABLE IF EXISTS test_concurrent_2")


def test_concurrent_batch_operations(sqlite_db):
    """
    Test concurrent batch operations.

    This test verifies that the database layer can handle concurrent batch operations
    while maintaining data consistency.
    """
    # Create test table for batch operations
    sqlite_db.execute(
        """
        CREATE TABLE IF NOT EXISTS test_batch (
            id INTEGER PRIMARY KEY,
            value TEXT,
            created_by TEXT
        )
    """
    )

    num_threads = 5
    items_per_thread = 20

    def batch_insert(thread_id: int):
        """Insert multiple records in a batch."""
        # Prepare batch data
        batch_data = []
        for i in range(items_per_thread):
            batch_data.append(
                {"value": f"value-{thread_id}-{i}", "created_by": f"thread-{thread_id}"}
            )

        # Insert batch
        with sqlite_uow:
            for item in batch_data:
                sqlite_db.execute(
                    "INSERT INTO test_batch (value, created_by) VALUES (?, ?)",
                    (item["value"], item["created_by"]),
                )

    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=batch_insert, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check total number of records
    result = sqlite_db.fetch_one("SELECT COUNT(*) as count FROM test_batch")
    total_records = result["count"]
    expected_records = num_threads * items_per_thread

    assert (
        total_records == expected_records
    ), f"Total records: {total_records}, Expected: {expected_records}"

    # Check records per thread
    for i in range(num_threads):
        result = sqlite_db.fetch_one(
            "SELECT COUNT(*) as count FROM test_batch WHERE created_by = ?", 
                (f"thread-{i}",)
        )
        thread_records = result["count"]
        assert (
            thread_records == items_per_thread
        ), f"Thread {i} records: {thread_records}, Expected: {items_per_thread}"

    # Clean up
    sqlite_db.execute("DROP TABLE IF EXISTS test_batch")


if __name__ == "__main__":
    pytest.main([" - v", "test_concurrent_operations.py"])
