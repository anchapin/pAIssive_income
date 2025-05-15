#!/usr/bin/env python3
"""init_db.py - Initialize the database with tables and initial data."""

import logging
import string
import sys
from secrets import randbelow
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app_flask import create_app, db
from app_flask.models import Agent, Team, User
from users.auth import hash_credential

# Set up logger with more detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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


def init_db() -> bool:
    """Initialize the database with required tables and initial data.

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    app = create_app()
    success = False

    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("Tables created")

            # Check if admin user exists
            admin = User.query.filter_by(username="admin").first()
            if admin:
                logger.info("Database already initialized")
                success = True
            else:
                success = _initialize_database_data()

    except Exception:
        logger.exception("Critical error during database initialization")
        success = False

    return success


def _initialize_database_data() -> bool:
    """Initialize database with initial data.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Generate a random password
        password = generate_secure_password()

        # Create admin user
        admin = User(
            username="admin",
            password_hash=hash_credential(password),
        )
        db.session.add(admin)
        logger.info("Admin user created")

        # Create default team
        default_team = Team(
            name="Default Team", description="Default team for AI agents"
        )
        db.session.add(default_team)
        logger.info("Default team created")

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
        logger.info("Sample agents created")

        # Commit all changes
        try:
            db.session.commit()
            logger.info("Database initialized successfully")
            # Security: Don't log passwords, only indicate that a password was generated
            logger.info(
                "Admin user created with generated password (not logged for security reasons)"
            )

            # Verify the initialization
            return _verify_initialization(agents)

        except IntegrityError:
            db.session.rollback()
            logger.exception("Database integrity error")
            return False
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Database error")
            return False

    except Exception:
        logger.exception("Error during database data initialization")
        return False


def _verify_initialization(agents) -> bool:
    """Verify that database initialization was successful.

    Args:
        agents: List of agents that should have been created

    Returns:
        bool: True if verification passed, False otherwise
    """
    try:
        agent_count = db.session.query(Agent).count()
        if agent_count != len(agents):
            logger.warning(
                f"Agent count mismatch: expected {len(agents)}, found {agent_count}"
            )
            return False
    except SQLAlchemyError:
        logger.exception("Error verifying agent count")
        return False
    else:
        return True


if __name__ == "__main__":
    success = init_db()
    if not success:
        logger.error("Database initialization failed")
        sys.exit(1)
    else:
        logger.info("Database initialization completed successfully")
