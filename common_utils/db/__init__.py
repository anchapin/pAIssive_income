"""
Database abstraction layer for pAIssive income.

This package provides a flexible database abstraction layer with support for
different database types (SQL and NoSQL), migration tools, and performance monitoring.

Usage examples:
    # Create a SQLite database
    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.monitoring import MonitoringDatabaseProxy

    # Create a SQLite database with monitoring
    db_config = {'db_path': 'app_data.db'}
    db = DatabaseFactory.create_database('sqlite', db_config)
    db_with_monitoring = MonitoringDatabaseProxy(db)

    # Use the database
    db_with_monitoring.connect()
    db_with_monitoring.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    db_with_monitoring.insert('users', {'name': 'John Doe'})
    users = db_with_monitoring.fetch_all('SELECT * FROM users')

    # Get performance metrics
    report = db_with_monitoring.get_performance_report()
"""

# Core interfaces
from common_utils.db.interfaces import DatabaseInterface, Repository, UnitOfWork

# Database implementations
from common_utils.db.sql_adapter import SQLiteAdapter, SQLiteUnitOfWork
from common_utils.db.nosql_adapter import MongoDBAdapter, MongoDBUnitOfWork

# Factory for creating database instances
from common_utils.db.factory import DatabaseFactory

# Migration tools
from common_utils.db.migration import Migration, MigrationManager

# Performance monitoring
from common_utils.db.monitoring import DatabaseMetrics, MonitoringDatabaseProxy

__all__ = [
    # Interfaces
    "DatabaseInterface",
    "Repository",
    "UnitOfWork",
    # Implementations
    "SQLiteAdapter",
    "SQLiteUnitOfWork",
    "MongoDBAdapter",
    "MongoDBUnitOfWork",
    # Factory
    "DatabaseFactory",
    # Migration
    "Migration",
    "MigrationManager",
    # Monitoring
    "DatabaseMetrics",
    "MonitoringDatabaseProxy",
]
