"""
"""
Database migration tools.
Database migration tools.


This module provides tools for managing database migrations, allowing
This module provides tools for managing database migrations, allowing
for schema changes to be applied and tracked for both SQL and NoSQL databases.
for schema changes to be applied and tracked for both SQL and NoSQL databases.
"""
"""


import datetime
import datetime
import glob
import glob
import importlib.util
import importlib.util
import logging
import logging
import os
import os
import re
import re
import sys
import sys
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from common_utils.db.interfaces import DatabaseInterface
from common_utils.db.interfaces import DatabaseInterface
from common_utils.db.nosql_adapter import MongoDBAdapter
from common_utils.db.nosql_adapter import MongoDBAdapter
from common_utils.db.sql_adapter import SQLiteAdapter
from common_utils.db.sql_adapter import SQLiteAdapter


logger
logger


from common_utils.db.migration import Migration
from common_utils.db.migration import Migration




class Migration:
    class Migration:


    pass  # Added missing block
    pass  # Added missing block




    class Migration(ABC):
    class Migration(ABC):
    """Base class for database migrations."""

    @property
    @abstractmethod
    def version(self) -> str:
    """Get the migration version."""
    pass

    @property
    @abstractmethod
    def description(self) -> str:
    """Get the migration description."""
    pass

    @abstractmethod
    def up(self, db: DatabaseInterface) -> None:
    """Apply the migration."""
    pass

    @abstractmethod
    def down(self, db: DatabaseInterface) -> None:
    """Revert the migration."""
    pass


    class MigrationManager:

    # Collection/table name for tracking migrations
    MIGRATIONS_TABLE = "_migrations"

    def __init__(self, db: DatabaseInterface, migrations_dir: str):
    """
    """
    Initialize the migration manager.
    Initialize the migration manager.


    Args:
    Args:
    db: Database interface to use for migrations
    db: Database interface to use for migrations
    migrations_dir: Directory containing migration files
    migrations_dir: Directory containing migration files
    """
    """
    self.db = db
    self.db = db
    self.migrations_dir = os.path.abspath(migrations_dir)
    self.migrations_dir = os.path.abspath(migrations_dir)
    self._ensure_migrations_table()
    self._ensure_migrations_table()


    def _ensure_migrations_table(self) -> None:
    def _ensure_migrations_table(self) -> None:
    """Ensure the migrations tracking table/collection exists."""
    try:
    if isinstance(self.db, SQLiteAdapter):
    # For SQL databases
    self.db.execute(
    """
    """
    CREATE TABLE IF NOT EXISTS {self.MIGRATIONS_TABLE} (
    CREATE TABLE IF NOT EXISTS {self.MIGRATIONS_TABLE} (
    version TEXT PRIMARY KEY,
    version TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    description TEXT
    description TEXT
    )
    )
    """
    """
    )
    )
    logger.info("Ensured migrations table exists (SQL)")
    logger.info("Ensured migrations table exists (SQL)")
    elif isinstance(self.db, MongoDBAdapter):
    elif isinstance(self.db, MongoDBAdapter):
    # For MongoDB
    # For MongoDB
    # Collections are created automatically when documents are inserted
    # Collections are created automatically when documents are inserted
    # But we can create an index on the version field
    # But we can create an index on the version field
    if self.MIGRATIONS_TABLE not in self.db.db.list_collection_names():
    if self.MIGRATIONS_TABLE not in self.db.db.list_collection_names():
    self.db.db[self.MIGRATIONS_TABLE].create_index(
    self.db.db[self.MIGRATIONS_TABLE].create_index(
    "version", unique=True
    "version", unique=True
    )
    )
    logger.info("Ensured migrations collection exists (MongoDB)")
    logger.info("Ensured migrations collection exists (MongoDB)")
    else:
    else:
    # For other database types
    # For other database types
    logger.warning(
    logger.warning(
    f"Unknown database type: {type(self.db)}. Migration tracking may not work correctly."
    f"Unknown database type: {type(self.db)}. Migration tracking may not work correctly."
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating migrations table/collection: {e}")
    logger.error(f"Error creating migrations table/collection: {e}")
    raise
    raise


    def get_applied_migrations(self) -> List[Dict[str, Any]]:
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
    """
    """
    Get a list of migrations that have been applied.
    Get a list of migrations that have been applied.


    Returns:
    Returns:
    List of applied migrations with version, name, and applied_at
    List of applied migrations with version, name, and applied_at
    """
    """
    try:
    try:
    if isinstance(self.db, SQLiteAdapter):
    if isinstance(self.db, SQLiteAdapter):
    # For SQL databases
    # For SQL databases
    result = self.db.fetch_all(
    result = self.db.fetch_all(
    f"SELECT version, name, applied_at, description FROM {self.MIGRATIONS_TABLE} ORDER BY version"
    f"SELECT version, name, applied_at, description FROM {self.MIGRATIONS_TABLE} ORDER BY version"
    )
    )
    return result
    return result
    elif isinstance(self.db, MongoDBAdapter):
    elif isinstance(self.db, MongoDBAdapter):
    # For MongoDB
    # For MongoDB
    result = list(
    result = list(
    self.db.db[self.MIGRATIONS_TABLE]
    self.db.db[self.MIGRATIONS_TABLE]
    .find(
    .find(
    {},
    {},
    {
    {
    "version": 1,
    "version": 1,
    "name": 1,
    "name": 1,
    "applied_at": 1,
    "applied_at": 1,
    "description": 1,
    "description": 1,
    "_id": 0,
    "_id": 0,
    },
    },
    )
    )
    .sort("version", 1)
    .sort("version", 1)
    )
    )
    return result
    return result
    else:
    else:
    # For other database types
    # For other database types
    logger.warning(
    logger.warning(
    f"Unknown database type: {type(self.db)}. Cannot get applied migrations."
    f"Unknown database type: {type(self.db)}. Cannot get applied migrations."
    )
    )
    return []
    return []
except Exception as e:
except Exception as e:
    logger.error(f"Error fetching applied migrations: {e}")
    logger.error(f"Error fetching applied migrations: {e}")
    return []
    return []


    def _load_migration(self, filename: str) -> Optional[Migration]:
    def _load_migration(self, filename: str) -> Optional[Migration]:
    """
    """
    Load a migration class from a file.
    Load a migration class from a file.


    Args:
    Args:
    filename: The filename of the migration file
    filename: The filename of the migration file


    Returns:
    Returns:
    An instance of the Migration class or None if not found
    An instance of the Migration class or None if not found
    """
    """
    try:
    try:
    # Extract the module name from the filename (without .py extension)
    # Extract the module name from the filename (without .py extension)
    module_name = os.path.splitext(os.path.basename(filename))[0]
    module_name = os.path.splitext(os.path.basename(filename))[0]
    module_path = os.path.join(self.migrations_dir, filename)
    module_path = os.path.join(self.migrations_dir, filename)


    # Import the module dynamically
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
    if not spec or not spec.loader:
    logger.error(f"Could not load spec for {filename}")
    logger.error(f"Could not load spec for {filename}")
    return None
    return None


    module = importlib.util.module_from_spec(spec)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    spec.loader.exec_module(module)


    # Find the Migration class in the module
    # Find the Migration class in the module
    for attr_name in dir(module):
    for attr_name in dir(module):
    attr = getattr(module, attr_name)
    attr = getattr(module, attr_name)
    if (
    if (
    isinstance(attr, type)
    isinstance(attr, type)
    and issubclass(attr, Migration)
    and issubclass(attr, Migration)
    and attr != Migration
    and attr != Migration
    ):
    ):
    return attr()
    return attr()


    logger.warning(f"No Migration class found in {filename}")
    logger.warning(f"No Migration class found in {filename}")
    return None
    return None
except Exception as e:
except Exception as e:
    logger.error(f"Error loading migration from {filename}: {e}")
    logger.error(f"Error loading migration from {filename}: {e}")
    return None
    return None


    def _get_migration_files(self) -> List[str]:
    def _get_migration_files(self) -> List[str]:
    """
    """
    Get all migration files.
    Get all migration files.


    Returns:
    Returns:
    A sorted list of migration filenames
    A sorted list of migration filenames
    """
    """
    # Get all Python files in the migrations directory
    # Get all Python files in the migrations directory
    migration_files = []
    migration_files = []
    pattern = os.path.join(self.migrations_dir, "*.py")
    pattern = os.path.join(self.migrations_dir, "*.py")
    for filename in glob.glob(pattern):
    for filename in glob.glob(pattern):
    basename = os.path.basename(filename)
    basename = os.path.basename(filename)
    if not basename.startswith("__"):  # Skip __init__.py and similar
    if not basename.startswith("__"):  # Skip __init__.py and similar
    migration_files.append(basename)
    migration_files.append(basename)


    # Sort migration files by version (assuming version is at the start of the filename)
    # Sort migration files by version (assuming version is at the start of the filename)
    def get_version(filename):
    def get_version(filename):
    # Extract version from filename pattern like "001_initial_schema.py"
    # Extract version from filename pattern like "001_initial_schema.py"
    match = re.match(r"^(\d+)_", filename)
    match = re.match(r"^(\d+)_", filename)
    if match:
    if match:
    return int(match.group(1))
    return int(match.group(1))
    return 0
    return 0


    migration_files.sort(key=get_version)
    migration_files.sort(key=get_version)
    return migration_files
    return migration_files


    def create_migration(self, name: str) -> str:
    def create_migration(self, name: str) -> str:
    """
    """
    Create a new migration file.
    Create a new migration file.


    Args:
    Args:
    name: Name of the migration
    name: Name of the migration


    Returns:
    Returns:
    Path to the created migration file
    Path to the created migration file
    """
    """
    # Get the next version number
    # Get the next version number
    migration_files = self._get_migration_files()
    migration_files = self._get_migration_files()
    if migration_files:
    if migration_files:
    latest_version = max(
    latest_version = max(
    int(re.match(r"^(\d+)_", f).group(1))
    int(re.match(r"^(\d+)_", f).group(1))
    for f in migration_files
    for f in migration_files
    if re.match(r"^(\d+)_", f)
    if re.match(r"^(\d+)_", f)
    )
    )
    version = latest_version + 1
    version = latest_version + 1
    else:
    else:
    version = 1
    version = 1


    # Format version as padded string (e.g., 001)
    # Format version as padded string (e.g., 001)
    version_str = f"{version:03d}"
    version_str = f"{version:03d}"


    # Format name as snake_case
    # Format name as snake_case
    name_snake = re.sub(r"[^a-zA-Z0-9]", "_", name.lower())
    name_snake = re.sub(r"[^a-zA-Z0-9]", "_", name.lower())
    name_snake = re.sub(r"_+", "_", name_snake).strip("_")
    name_snake = re.sub(r"_+", "_", name_snake).strip("_")


    # Create the filename
    # Create the filename
    filename = f"{version_str}_{name_snake}.py"
    filename = f"{version_str}_{name_snake}.py"
    filepath = os.path.join(self.migrations_dir, filename)
    filepath = os.path.join(self.migrations_dir, filename)


    # Create the migration file content
    # Create the migration file content
    content = f'''"""
    content = f'''"""
    Migration {version_str}: {name}
    Migration {version_str}: {name}


    Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    """
    {version_str}(Migration):
    {version_str}(Migration):
    """Migration {version_str}: {name}"""

    @property
    def version(self) -> str:
    return "{version_str}"

    @property
    def description(self) -> str:
    return "{name}"

    def up(self, db):
    """Apply the migration."""
    # TODO: Implement migration
    pass

    def down(self, db):
    """Revert the migration."""
    # TODO: Implement rollback
    pass
    '''

    # Write the migration file
    with open(filepath, "w") as f:
    f.write(content)

    logger.info(f"Created migration file: {filepath}")
    return filepath

    def migrate(self, target_version: Optional[str] = None) -> None:
    """
    """
    Apply pending migrations up to the target version.
    Apply pending migrations up to the target version.


    Args:
    Args:
    target_version: Optional version to migrate to. If None, all pending migrations will be applied.
    target_version: Optional version to migrate to. If None, all pending migrations will be applied.
    """
    """
    applied_migrations = self.get_applied_migrations()
    applied_migrations = self.get_applied_migrations()
    applied_versions = {m["version"] for m in applied_migrations}
    applied_versions = {m["version"] for m in applied_migrations}


    # Get all migration files
    # Get all migration files
    migration_files = self._get_migration_files()
    migration_files = self._get_migration_files()


    # Track if we need to stop at a specific version
    # Track if we need to stop at a specific version
    reached_target = False
    reached_target = False


    # Apply pending migrations
    # Apply pending migrations
    for filename in migration_files:
    for filename in migration_files:
    # Skip if we've reached the target version
    # Skip if we've reached the target version
    if reached_target:
    if reached_target:
    break
    break


    migration = self._load_migration(filename)
    migration = self._load_migration(filename)
    if not migration:
    if not migration:
    continue
    continue


    version = migration.version
    version = migration.version


    # Check if we've reached the target version
    # Check if we've reached the target version
    if target_version and version > target_version:
    if target_version and version > target_version:
    reached_target = True
    reached_target = True
    continue
    continue


    if version not in applied_versions:
    if version not in applied_versions:
    logger.info(f"Applying migration {version}: {migration.description}")
    logger.info(f"Applying migration {version}: {migration.description}")


    try:
    try:
    # Start transaction if supported
    # Start transaction if supported
    migration.up(self.db)
    migration.up(self.db)


    # Record the migration
    # Record the migration
    migration_record = {
    migration_record = {
    "version": version,
    "version": version,
    "name": filename,
    "name": filename,
    "applied_at": datetime.datetime.now().isoformat(),
    "applied_at": datetime.datetime.now().isoformat(),
    "description": migration.description,
    "description": migration.description,
    }
    }


    # Insert the migration record based on database type
    # Insert the migration record based on database type
    if isinstance(self.db, SQLiteAdapter) or not isinstance(
    if isinstance(self.db, SQLiteAdapter) or not isinstance(
    self.db, MongoDBAdapter
    self.db, MongoDBAdapter
    ):
    ):
    self.db.insert(self.MIGRATIONS_TABLE, migration_record)
    self.db.insert(self.MIGRATIONS_TABLE, migration_record)
    else:
    else:
    # For MongoDB
    # For MongoDB
    self.db.db[self.MIGRATIONS_TABLE].insert_one(migration_record)
    self.db.db[self.MIGRATIONS_TABLE].insert_one(migration_record)


    logger.info(f"Successfully applied migration {version}")
    logger.info(f"Successfully applied migration {version}")
except Exception as e:
except Exception as e:
    logger.error(f"Error applying migration {version}: {e}")
    logger.error(f"Error applying migration {version}: {e}")
    raise
    raise


    def rollback(self, steps: int = 1) -> None:
    def rollback(self, steps: int = 1) -> None:
    """
    """
    Rollback the last N migrations.
    Rollback the last N migrations.


    Args:
    Args:
    steps: Number of migrations to roll back
    steps: Number of migrations to roll back
    """
    """
    applied_migrations = self.get_applied_migrations()
    applied_migrations = self.get_applied_migrations()


    # Nothing to rollback
    # Nothing to rollback
    if not applied_migrations:
    if not applied_migrations:
    logger.info("No migrations to roll back")
    logger.info("No migrations to roll back")
    return # Limit steps to the number of applied migrations
    return # Limit steps to the number of applied migrations
    steps = min(steps, len(applied_migrations))
    steps = min(steps, len(applied_migrations))


    # Get the migrations to roll back (in reverse order)
    # Get the migrations to roll back (in reverse order)
    to_rollback = applied_migrations[-steps:]
    to_rollback = applied_migrations[-steps:]
    to_rollback.reverse()
    to_rollback.reverse()


    for migration_record in to_rollback:
    for migration_record in to_rollback:
    version = migration_record["version"]
    version = migration_record["version"]
    filename = migration_record["name"]
    filename = migration_record["name"]


    logger.info(
    logger.info(
    f"Rolling back migration {version}: {migration_record.get('description', 'Unknown')}"
    f"Rolling back migration {version}: {migration_record.get('description', 'Unknown')}"
    )
    )


    # Load the migration class
    # Load the migration class
    migration = self._load_migration(filename)
    migration = self._load_migration(filename)
    if not migration:
    if not migration:
    logger.error(f"Could not load migration {filename} for rollback")
    logger.error(f"Could not load migration {filename} for rollback")
    continue
    continue


    try:
    try:
    # Roll back the migration
    # Roll back the migration
    migration.down(self.db)
    migration.down(self.db)


    # Remove the migration record based on database type
    # Remove the migration record based on database type
    if isinstance(self.db, SQLiteAdapter):
    if isinstance(self.db, SQLiteAdapter):
    # For SQL databases
    # For SQL databases
    self.db.delete(
    self.db.delete(
    self.MIGRATIONS_TABLE,
    self.MIGRATIONS_TABLE,
    "version = :version",
    "version = :version",
    {"version": version},
    {"version": version},
    )
    )
    elif isinstance(self.db, MongoDBAdapter):
    elif isinstance(self.db, MongoDBAdapter):
    # For MongoDB
    # For MongoDB
    self.db.db[self.MIGRATIONS_TABLE].delete_one({"version": version})
    self.db.db[self.MIGRATIONS_TABLE].delete_one({"version": version})
    else:
    else:
    # For other database types
    # For other database types
    logger.warning(
    logger.warning(
    f"Unknown database type: {type(self.db)}. Migration record may not be removed."
    f"Unknown database type: {type(self.db)}. Migration record may not be removed."
    )
    )


    logger.info(f"Successfully rolled back migration {version}")
    logger.info(f"Successfully rolled back migration {version}")
except Exception as e:
except Exception as e:
    logger.error(f"Error rolling back migration {version}: {e}")
    logger.error(f"Error rolling back migration {version}: {e}")
    raise
    raise