"""Database migration environment configuration."""

from __future__ import annotations

import logging
import os
from logging.config import fileConfig
from typing import Any

from alembic import context
from alembic.operations.ops import UpgradeOps
from alembic.script.revision import MigrationScript

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config: Any = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
else:
    msg = "Alembic config_file_name is None. Check your alembic.ini setup."
    raise RuntimeError(msg)
logger = logging.getLogger("alembic.env")

# Get database URL from environment or use default
db_url = os.environ.get("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb")
config.set_main_option("sqlalchemy.url", db_url)
target_metadata = None  # We're not using model metadata for these migrations

# Additional configuration options can be set here if needed


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        msg = "sqlalchemy.url is not set in Alembic config."
        raise RuntimeError(msg)
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # This callback prevents auto-migration when there are no changes
    # See: https://alembic.sqlalchemy.org/en/latest/cookbook.html
    def process_revision_directives(
        _context: object, _revision: object, directives: list[MigrationScript]
    ) -> None:
        """
        Process migration directives to detect empty migrations.

        Args:
            _context: Alembic context (unused)
            _revision: Revision object (unused)
            directives: List of MigrationScript objects (migration scripts)

        """
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]  # type: ignore[index]
            # Only proceed if script is a MigrationScript and has upgrade_ops
            if isinstance(script, MigrationScript) and isinstance(
                script.upgrade_ops, UpgradeOps
            ):
                if script.upgrade_ops.is_empty():
                    directives[:] = []
                logger.info("No changes in schema detected.")

    from sqlalchemy import create_engine

    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        msg = "sqlalchemy.url is not set in Alembic config."
        raise RuntimeError(msg)
    engine = create_engine(url)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,  # type: ignore[arg-type]
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
