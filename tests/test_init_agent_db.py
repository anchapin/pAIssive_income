"""Tests for the init_agent_db module."""

import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from init_agent_db import init_agent_db


class TestInitAgentDB(unittest.TestCase):
    """Test cases for the init_agent_db function."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variable
        self.db_url_patcher = patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/testdb"})
        self.db_url_patcher.start()

        # Mock logger
        self.logger_patcher = patch("init_agent_db.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.db_url_patcher.stop()
        self.logger_patcher.stop()

    @patch("init_agent_db.psycopg2.connect")
    def test_init_agent_db_success(self, mock_connect):
        """Test successful database initialization."""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock cursor.fetchone() to return different values for different queries
        mock_cursor.fetchone.side_effect = [
            {"exists": False},  # First call: agent table doesn't exist
            {"exists": False},  # Second call: agent_action table doesn't exist
            {"count": 0}        # Third call: no agent records
        ]

        # Call the function
        result = init_agent_db()

        # Verify result
        self.assertTrue(result)

        # Verify connection was established
        mock_connect.assert_called_once_with(
            "postgresql://user:pass@localhost/testdb",
            cursor_factory=unittest.mock.ANY
        )

        # Verify tables were created
        self.assertEqual(mock_cursor.execute.call_count, 6)

        # Verify connection was closed
        mock_conn.close.assert_called_once()

        # Verify success was logged
        self.mock_logger.info.assert_any_call("Agent database initialization completed successfully")

    @patch("init_agent_db.psycopg2.connect")
    def test_init_agent_db_tables_exist(self, mock_connect):
        """Test when tables already exist."""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock cursor.fetchone() to return different values for different queries
        mock_cursor.fetchone.side_effect = [
            {"exists": True},   # First call: agent table exists
            {"exists": True},   # Second call: agent_action table exists
            {"count": 5}        # Third call: 5 agent records
        ]

        # Call the function
        result = init_agent_db()

        # Verify result
        self.assertTrue(result)

        # Verify tables were not created
        self.assertEqual(mock_cursor.execute.call_count, 3)

        # Verify agent data was not inserted
        # Check that no INSERT INTO agent was called
        insert_calls = [call for call in mock_cursor.execute.call_args_list if "INSERT INTO agent" in str(call)]
        self.assertEqual(len(insert_calls), 0)

        # Verify existing records were logged
        self.mock_logger.info.assert_any_call("Agent table already has %d records", 5)

    @patch("init_agent_db.psycopg2.connect")
    def test_init_agent_db_no_records(self, mock_connect):
        """Test when tables exist but no records."""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock cursor.fetchone() to return different values for different queries
        mock_cursor.fetchone.side_effect = [
            {"exists": True},   # First call: agent table exists
            {"exists": True},   # Second call: agent_action table exists
            {"count": 0}        # Third call: no agent records
        ]

        # Call the function
        result = init_agent_db()

        # Verify result
        self.assertTrue(result)

        # Verify agent data was inserted
        self.mock_logger.info.assert_any_call("Inserting test agent data...")
        self.mock_logger.info.assert_any_call("Test agent data inserted successfully")

    def test_init_agent_db_no_db_url(self):
        """Test when DATABASE_URL is not set."""
        # Remove DATABASE_URL from environment
        with patch.dict(os.environ, {}, clear=True):
            # Call the function
            result = init_agent_db()

            # Verify result
            self.assertFalse(result)

            # Verify error was logged
            self.mock_logger.error.assert_called_once_with("DATABASE_URL environment variable not set")

    @patch("init_agent_db.psycopg2.connect")
    def test_init_agent_db_exception(self, mock_connect):
        """Test when an exception occurs."""
        # Setup mock to raise an exception
        mock_connect.side_effect = Exception("Test error")

        # Call the function
        result = init_agent_db()

        # Verify result
        self.assertFalse(result)

        # Verify error was logged
        self.mock_logger.exception.assert_called_once_with("Error initializing agent database")


if __name__ == "__main__":
    unittest.main()
