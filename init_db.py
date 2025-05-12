"""init_db.py - Initialize the database with tables and initial data."""

import logging
from typing import List, Optional

from flask import create_app
from flask.models import Agent, Team, User, db

# Set up logger
logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize the database with tables and initial data."""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if admin user exists
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            # Create admin user
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash="$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnpY0o58unSvIPxddLxGystU.O",  # placeholder hash
            )
            db.session.add(admin)

            # Create default team
            default_team = Team(
                name="Default Team", description="Default team for AI agents"
            )
            db.session.add(default_team)

            # Create sample agents
            agents = [
                Agent(
                    name="Research Agent",
                    role="researcher",
                    description="Conducts research on topics",
                    team=default_team,
                ),
                Agent(
                    name="Content Agent",
                    role="writer",
                    description="Creates content based on research",
                    team=default_team,
                ),
                Agent(
                    name="Marketing Agent",
                    role="marketer",
                    description="Develops marketing strategies",
                    team=default_team,
                ),
            ]
            db.session.add_all(agents)

            # Commit changes
            db.session.commit()
            logger.info("Database initialized with default data")
        else:
            logger.info("Database already contains data")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    init_db()
