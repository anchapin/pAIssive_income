# Database Utilities for pAIssive Income

This package provides a flexible database abstraction layer with support for different database types (SQL and NoSQL), migration tools, and performance monitoring.

## Overview

The database utilities include:

- **Database Interface**: Common interface for all database operations
- **SQL Adapter**: Implementation for SQLite databases
- **NoSQL Adapter**: Implementation for MongoDB databases
- **Migration Tools**: Tools for managing database schema changes
- **Performance Monitoring**: Utilities for monitoring database performance
- **Factory**: Factory for creating database instances

## Getting Started

### Creating a Database Connection

```python
from common_utils.db.factory import DatabaseFactory

# Create a SQLite database
db_config = {'db_path': 'app_data.db'}
db = DatabaseFactory.create_database('sqlite', db_config)

# Create a MongoDB database
db_config = {
    'connection_string': 'mongodb://localhost:27017',
    'db_name': 'paissive_income'
}
db = DatabaseFactory.create_database('mongodb', db_config)

# Connect to the database
db.connect()
```

### Basic Database Operations

```python
# SQL operations
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
db.insert('users', {'name': 'John Doe'})
users = db.fetch_all('SELECT * FROM users')

# MongoDB operations
db.insert('users', {'name': 'John Doe'})
users = db.fetch_all('users', {'name': 'John Doe'})
```

## Database Migrations

The migration tools support both SQL and NoSQL databases, allowing you to manage schema changes in a consistent way.

### Creating Migrations

```python
from common_utils.db.migration import MigrationManager

# Create a migration manager
migration_manager = MigrationManager(db, 'migrations')

# Create a new migration
migration_file = migration_manager.create_migration('add_users_table')
```

This will create a migration file with the following structure:

```python
from common_utils.db.migration import Migration

class Migration001(Migration):
    """Migration 001: add_users_table"""

    @property
    def version(self) -> str:
        return "001"

    @property
    def description(self) -> str:
        return "add_users_table"

    def up(self, db):
        """Apply the migration."""
        # For SQL databases
        if hasattr(db, 'execute'):
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at TEXT
                )
            """)
        # For MongoDB
        elif hasattr(db, 'db'):
            db.db.create_collection('users')
            db.db.users.create_index('email', unique=True)

    def down(self, db):
        """Revert the migration."""
        # For SQL databases
        if hasattr(db, 'execute'):
            db.execute("DROP TABLE IF EXISTS users")
        # For MongoDB
        elif hasattr(db, 'db'):
            db.db.users.drop()
```

### Applying Migrations

```python
# Apply all pending migrations
migration_manager.migrate()

# Apply migrations up to a specific version
migration_manager.migrate(target_version="003")

# Rollback the last migration
migration_manager.rollback()

# Rollback multiple migrations
migration_manager.rollback(steps=3)
```

## Database Types Support

The migration tools support both SQL and NoSQL databases:

### SQL Databases (e.g., SQLite)

- Migrations are tracked in a `_migrations` table
- SQL statements are used for schema changes
- Transactions are used for atomic migrations

### NoSQL Databases (e.g., MongoDB)

- Migrations are tracked in a `_migrations` collection
- Collection and index operations are used for schema changes
- Document operations are used for data migrations

## Performance Monitoring

```python
from common_utils.db.monitoring import MonitoringDatabaseProxy

# Create a database with monitoring
db = DatabaseFactory.create_database('sqlite', {'db_path': 'app_data.db'})
db_with_monitoring = MonitoringDatabaseProxy(db)

# Use the database
db_with_monitoring.connect()
db_with_monitoring.execute('SELECT * FROM users')

# Get performance metrics
report = db_with_monitoring.get_performance_report()
print(f"Total queries: {report['summary']['query_count']}")
print(f"Average query time: {report['summary']['average_query_time']}ms")
```

## Unit of Work Pattern

```python
from common_utils.db.factory import DatabaseFactory

# Create a database
db = DatabaseFactory.create_database('sqlite', {'db_path': 'app_data.db'})

# Create a unit of work
uow = DatabaseFactory.create_unit_of_work(db)

# Use the unit of work
with uow:
    uow.users.add({'name': 'John Doe'})
    uow.orders.add({'user_id': 1, 'product': 'Widget'})
    # Changes are committed when the context exits
```

## Best Practices

1. **Use the Factory**: Always use the `DatabaseFactory` to create database instances
2. **Abstract Database Type**: Write code that works with both SQL and NoSQL databases
3. **Use Migrations**: Manage schema changes with migrations
4. **Monitor Performance**: Use the monitoring proxy to track database performance
5. **Handle Errors**: Always handle database errors gracefully
6. **Use Transactions**: Use the unit of work pattern for transactional operations
7. **Parameterize Queries**: Always use parameterized queries to prevent SQL injection
