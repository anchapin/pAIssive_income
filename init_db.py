"""init_db.py - Initialize the database with tables and initial data."""

import logging
import os
import string
from secrets import randbelow

from app_flask import create_app, db
from app_flask.models import Agent, Team, User
from users.auth import hash_credential

# Set up logger
logger = logging.getLogger(__name__)


def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password.

    Args:
        length: Length of the password to generate

    Returns:
        A secure random password string
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Use a more secure method for random selection
    password = ""
    for _ in range(length):
        password += alphabet[randbelow(len(alphabet))]
    return password


def init_db() -> None:
    """Initialize the database with tables and initial data."""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if admin user exists
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            # Generate a secure password for admin
            admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD")
            if not admin_password:
                admin_password = generate_secure_password()
                # Log a message but don't include the password in logs
                logger.info("Generated secure admin password - use it to log in")
                # Log the generated password during interactive setup
                if hasattr(os, "isatty") and os.isatty(0):
                    logger.info(f"Generated admin password: {admin_password}")
                    logger.info("Admin password was logged to console")

            # Hash the password
            password_hash = hash_credential(admin_password)

            # Create admin user
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=password_hash,
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
