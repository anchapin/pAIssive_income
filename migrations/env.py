# type: ignore
import logging
from logging.config import fileConfig
from typing import Any, List

from alembic import context

# Import current_app directly to avoid mypy errors
try:
    from flask import current_app
except ImportError:
    # This is a fallback for mypy
    current_app = Any  # type: ignore

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Get metadata from Flask-SQLAlchemy models
# This enables Alembic to detect model changes automatically
config.set_main_option(
    "sqlalchemy.url",
    str(current_app.extensions["migrate"].db.get_engine().url).replace("%", "%%"),
)
target_metadata = current_app.extensions["migrate"].db.metadata

# Additional configuration options can be set here if needed


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # This callback prevents auto-migration when there are no changes
    # See: https://alembic.sqlalchemy.org/en/latest/cookbook.html
    def process_revision_directives(
        _context: Any, _revision: Any, directives: List[Any]
    ) -> None:
        """Process migration directives to detect empty migrations.

        Args:
            _context: Alembic context (unused)
            _revision: Revision object (unused)
            directives: List of revision directives
        """
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    connectable = current_app.extensions["migrate"].db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions["migrate"].configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
