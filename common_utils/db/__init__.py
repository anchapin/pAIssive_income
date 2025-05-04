"""
"""
Database abstraction layer for pAIssive income.
Database abstraction layer for pAIssive income.


This package provides a flexible database abstraction layer with support for
This package provides a flexible database abstraction layer with support for
different database types (SQL and NoSQL), migration tools, and performance monitoring.
different database types (SQL and NoSQL), migration tools, and performance monitoring.


Usage examples:
    Usage examples:
    # Create a SQLite database
    # Create a SQLite database
    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.monitoring import MonitoringDatabaseProxy
    from common_utils.db.monitoring import MonitoringDatabaseProxy


    # Create a SQLite database with monitoring
    # Create a SQLite database with monitoring
    db_config = {'db_path': 'app_data.db'}
    db_config = {'db_path': 'app_data.db'}
    db = DatabaseFactory.create_database('sqlite', db_config)
    db = DatabaseFactory.create_database('sqlite', db_config)
    db_with_monitoring = MonitoringDatabaseProxy(db)
    db_with_monitoring = MonitoringDatabaseProxy(db)


    # Use the database
    # Use the database
    db_with_monitoring.connect()
    db_with_monitoring.connect()
    db_with_monitoring.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    db_with_monitoring.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    db_with_monitoring.insert('users', {'name': 'John Doe'})
    db_with_monitoring.insert('users', {'name': 'John Doe'})
    users = db_with_monitoring.fetch_all('SELECT * FROM users')
    users = db_with_monitoring.fetch_all('SELECT * FROM users')


    # Get performance metrics
    # Get performance metrics
    report = db_with_monitoring.get_performance_report()
    report = db_with_monitoring.get_performance_report()
    """
    """


    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.monitoring import MonitoringDatabaseProxy
    from common_utils.db.monitoring import MonitoringDatabaseProxy


    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.factory import DatabaseFactory
    from common_utils.db.interfaces import (DatabaseInterface, Repository,
    from common_utils.db.interfaces import (DatabaseInterface, Repository,
    UnitOfWork)
    UnitOfWork)
    from common_utils.db.migration import Migration, MigrationManager
    from common_utils.db.migration import Migration, MigrationManager
    from common_utils.db.monitoring import DatabaseMetrics, MonitoringDatabaseProxy
    from common_utils.db.monitoring import DatabaseMetrics, MonitoringDatabaseProxy
    from common_utils.db.nosql_adapter import MongoDBAdapter, MongoDBUnitOfWork
    from common_utils.db.nosql_adapter import MongoDBAdapter, MongoDBUnitOfWork
    from common_utils.db.sql_adapter import SQLiteAdapter, SQLiteUnitOfWork
    from common_utils.db.sql_adapter import SQLiteAdapter, SQLiteUnitOfWork


    __all__
    __all__


    """
    """
    Database abstraction layer for pAIssive income.
    Database abstraction layer for pAIssive income.


    This package provides a flexible database abstraction layer with support for
    This package provides a flexible database abstraction layer with support for
    different database types (SQL and NoSQL), migration tools, and performance monitoring.
    different database types (SQL and NoSQL), migration tools, and performance monitoring.


    Usage examples:
    Usage examples:
    # Create a SQLite database
    # Create a SQLite database
    # Create a SQLite database with monitoring
    # Create a SQLite database with monitoring
    db_config = {'db_path': 'app_data.db'}
    db_config = {'db_path': 'app_data.db'}
    db = DatabaseFactory.create_database('sqlite', db_config)
    db = DatabaseFactory.create_database('sqlite', db_config)
    db_with_monitoring = MonitoringDatabaseProxy(db)
    db_with_monitoring = MonitoringDatabaseProxy(db)


    # Use the database
    # Use the database
    db_with_monitoring.connect()
    db_with_monitoring.connect()
    db_with_monitoring.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    db_with_monitoring.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    db_with_monitoring.insert('users', {'name': 'John Doe'})
    db_with_monitoring.insert('users', {'name': 'John Doe'})
    users = db_with_monitoring.fetch_all('SELECT * FROM users')
    users = db_with_monitoring.fetch_all('SELECT * FROM users')


    # Get performance metrics
    # Get performance metrics
    report = db_with_monitoring.get_performance_report()
    report = db_with_monitoring.get_performance_report()
    """
    """


    # Factory for creating database instances
    # Factory for creating database instances
    # Core interfaces
    # Core interfaces
    # Migration tools
    # Migration tools
    # Performance monitoring
    # Performance monitoring
    # Database implementations
    # Database implementations
    = [
    = [
    # Interfaces
    # Interfaces
    "DatabaseInterface",
    "DatabaseInterface",
    "Repository",
    "Repository",
    "UnitOfWork",
    "UnitOfWork",
    # Implementations
    # Implementations
    "SQLiteAdapter",
    "SQLiteAdapter",
    "SQLiteUnitOfWork",
    "SQLiteUnitOfWork",
    "MongoDBAdapter",
    "MongoDBAdapter",
    "MongoDBUnitOfWork",
    "MongoDBUnitOfWork",
    # Factory
    # Factory
    "DatabaseFactory",
    "DatabaseFactory",
    # Migration
    # Migration
    "Migration",
    "Migration",
    "MigrationManager",
    "MigrationManager",
    # Monitoring
    # Monitoring
    "DatabaseMetrics",
    "DatabaseMetrics",
    "MonitoringDatabaseProxy",
    "MonitoringDatabaseProxy",
    ]
    ]