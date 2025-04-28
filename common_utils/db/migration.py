"""
Database migration tools.

This module provides tools for managing database migrations, allowing
for schema changes to be applied and tracked.
"""

import os
import sys
import glob
import importlib.util
import logging
import datetime
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type

from common_utils.db.interfaces import DatabaseInterface

logger = logging.getLogger(__name__)

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
    """Manages database migrations."""
    
    def __init__(self, db: DatabaseInterface, migrations_dir: str):
        """
        Initialize the migration manager.
        
        Args:
            db: Database interface to use for migrations
            migrations_dir: Directory containing migration files
        """
        self.db = db
        self.migrations_dir = os.path.abspath(migrations_dir)
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self) -> None:
        """Ensure the migrations tracking table exists."""
        try:
            # For SQL databases
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    version TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL,
                    description TEXT
                )
            """)
            logger.info("Ensured migrations table exists")
        except Exception as e:
            logger.error(f"Error creating migrations table: {e}")
            raise
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """
        Get a list of migrations that have been applied.
        
        Returns:
            List of applied migrations with version, name, and applied_at
        """
        try:
            result = self.db.fetch_all("SELECT version, name, applied_at, description FROM _migrations ORDER BY version")
            return result
        except Exception as e:
            logger.error(f"Error fetching applied migrations: {e}")
            return []
    
    def _load_migration(self, filename: str) -> Optional[Migration]:
        """
        Load a migration class from a file.
        
        Args:
            filename: The filename of the migration file
            
        Returns:
            An instance of the Migration class or None if not found
        """
        try:
            # Extract the module name from the filename (without .py extension)
            module_name = os.path.splitext(os.path.basename(filename))[0]
            module_path = os.path.join(self.migrations_dir, filename)
            
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                logger.error(f"Could not load spec for {filename}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find the Migration class in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Migration) and attr != Migration:
                    return attr()
            
            logger.warning(f"No Migration class found in {filename}")
            return None
        except Exception as e:
            logger.error(f"Error loading migration from {filename}: {e}")
            return None
    
    def _get_migration_files(self) -> List[str]:
        """
        Get all migration files.
        
        Returns:
            A sorted list of migration filenames
        """
        # Get all Python files in the migrations directory
        migration_files = []
        pattern = os.path.join(self.migrations_dir, "*.py")
        for filename in glob.glob(pattern):
            basename = os.path.basename(filename)
            if not basename.startswith("__"):  # Skip __init__.py and similar
                migration_files.append(basename)
        
        # Sort migration files by version (assuming version is at the start of the filename)
        def get_version(filename):
            # Extract version from filename pattern like "001_initial_schema.py"
            match = re.match(r"^(\d+)_", filename)
            if match:
                return int(match.group(1))
            return 0
        
        migration_files.sort(key=get_version)
        return migration_files
    
    def create_migration(self, name: str) -> str:
        """
        Create a new migration file.
        
        Args:
            name: Name of the migration
            
        Returns:
            Path to the created migration file
        """
        # Get the next version number
        migration_files = self._get_migration_files()
        if migration_files:
            latest_version = max(int(re.match(r"^(\d+)_", f).group(1)) 
                               for f in migration_files 
                               if re.match(r"^(\d+)_", f))
            version = latest_version + 1
        else:
            version = 1
        
        # Format version as padded string (e.g., 001)
        version_str = f"{version:03d}"
        
        # Format name as snake_case
        name_snake = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        name_snake = re.sub(r'_+', '_', name_snake).strip('_')
        
        # Create the filename
        filename = f"{version_str}_{name_snake}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # Create the migration file content
        content = f'''"""
Migration {version_str}: {name}

Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from common_utils.db.migration import Migration

class Migration{version_str}(Migration):
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
        with open(filepath, 'w') as f:
            f.write(content)
        
        logger.info(f"Created migration file: {filepath}")
        return filepath
    
    def migrate(self, target_version: Optional[str] = None) -> None:
        """
        Apply pending migrations up to the target version.
        
        Args:
            target_version: Optional version to migrate to. If None, all pending migrations will be applied.
        """
        applied_migrations = self.get_applied_migrations()
        applied_versions = {m['version'] for m in applied_migrations}
        
        # Get all migration files
        migration_files = self._get_migration_files()
        
        # Track if we need to stop at a specific version
        reached_target = False
        
        # Apply pending migrations
        for filename in migration_files:
            # Skip if we've reached the target version
            if reached_target:
                break
                
            migration = self._load_migration(filename)
            if not migration:
                continue
                
            version = migration.version
            
            # Check if we've reached the target version
            if target_version and version > target_version:
                reached_target = True
                continue
                
            if version not in applied_versions:
                logger.info(f"Applying migration {version}: {migration.description}")
                
                try:
                    # Start transaction if supported
                    migration.up(self.db)
                    
                    # Record the migration
                    self.db.insert('_migrations', {
                        'version': version,
                        'name': filename,
                        'applied_at': datetime.datetime.now().isoformat(),
                        'description': migration.description
                    })
                    
                    logger.info(f"Successfully applied migration {version}")
                except Exception as e:
                    logger.error(f"Error applying migration {version}: {e}")
                    raise
    
    def rollback(self, steps: int = 1) -> None:
        """
        Rollback the last N migrations.
        
        Args:
            steps: Number of migrations to roll back
        """
        applied_migrations = self.get_applied_migrations()
        
        # Nothing to rollback
        if not applied_migrations:
            logger.info("No migrations to roll back")
            return
        
        # Limit steps to the number of applied migrations
        steps = min(steps, len(applied_migrations))
        
        # Get the migrations to roll back (in reverse order)
        to_rollback = applied_migrations[-steps:]
        to_rollback.reverse()
        
        for migration_record in to_rollback:
            version = migration_record['version']
            filename = migration_record['name']
            
            logger.info(f"Rolling back migration {version}: {migration_record.get('description', 'Unknown')}")
            
            # Load the migration class
            migration = self._load_migration(filename)
            if not migration:
                logger.error(f"Could not load migration {filename} for rollback")
                continue
                
            try:
                # Roll back the migration
                migration.down(self.db)
                
                # Remove the migration record
                self.db.delete('_migrations', "version = ?", (version,))
                
                logger.info(f"Successfully rolled back migration {version}")
            except Exception as e:
                logger.error(f"Error rolling back migration {version}: {e}")
                raise