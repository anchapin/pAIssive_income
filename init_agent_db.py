#!/usr/bin/env python3
"""init_agent_db.py - Initialize the agent database with test data."""

import logging
import os
import sys

# Configure logging
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    logger.warning("psycopg2 is not available. Database initialization will be skipped.")
    psycopg2 = None
    RealDictCursor = None
    HAS_PSYCOPG2 = False



def init_agent_db() -> bool:
    """
    Initialize the agent database with test data.

    Returns:
        bool: True if initialization was successful, False otherwise

    """
    if not HAS_PSYCOPG2:
        logger.warning("psycopg2 not available. Skipping database initialization.")
        return False

    # Get database URL from environment variable
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        return False

    try:
        # Connect to the database
        logger.info("Connecting to database...")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        # Check if agent table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'agent'
            );
        """)
        table_exists = cursor.fetchone()["exists"]

        if not table_exists:
            logger.info("Creating agent table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    avatar_url TEXT,
                    description TEXT
                );
            """)
            conn.commit()

        # Check if agent_action table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'agent_action'
            );
        """)
        action_table_exists = cursor.fetchone()["exists"]

        if not action_table_exists:
            logger.info("Creating agent_action table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_action (
                    id SERIAL PRIMARY KEY,
                    agent_id INTEGER REFERENCES agent(id),
                    action_type TEXT,
                    action_payload JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

        # Check if agent data exists
        cursor.execute("SELECT COUNT(*) FROM agent;")
        agent_count = cursor.fetchone()["count"]

        if agent_count == 0:
            logger.info("Inserting test agent data...")
            cursor.execute("""
                INSERT INTO agent (name, avatar_url, description)
                VALUES (
                    'Test Agent',
                    'https://example.com/avatar.png',
                    'This is a test agent for integration testing'
                );
            """)
            conn.commit()
            logger.info("Test agent data inserted successfully")
        else:
            logger.info("Agent table already has %d records", agent_count)

        conn.close()
        logger.info("Agent database initialization completed successfully")

    except Exception:
        logger.exception("Error initializing agent database")
        return False
    else:
        return True


if __name__ == "__main__":
    # Set up logger with more detailed formatting
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    success = init_agent_db()
    if not success:
        sys.exit(1)
