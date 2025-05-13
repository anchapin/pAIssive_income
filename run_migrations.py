"""run_migrations.py - Run database migrations."""

import logging

from flask_migrate import upgrade

from flask import create_app

# Set up logger
logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Run database migrations."""
    app = create_app()
    with app.app_context():
        # Run migrations
        upgrade()
        logger.info("Migrations completed successfully")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    run_migrations()
