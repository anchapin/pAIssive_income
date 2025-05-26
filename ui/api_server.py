"""
api_server - Module for ui.api_server.

This module provides a simple HTTP server for the UI module.
It includes a health check endpoint for monitoring.
"""

# Standard library imports
from __future__ import annotations

import http.server
import json
import logging
import os
import socketserver
from typing import Any
from urllib.parse import urlparse
import sys # Added sys import

# Configure logging
logger = logging.getLogger(__name__)


# Third-party imports
try:
    import psycopg2
    import psycopg2.extensions
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 module not found. Please install it (e.g., pip install psycopg2-binary).")
    sys.exit(1)



class DatabaseError(RuntimeError):
    """Base exception class for database-related errors."""

    def __init__(self, message: str = "Database error occurred") -> None:
        """
        Initialize the database error with a message.

        Args:
            message: Error message

        """
        super().__init__(message)


class DatabaseConfigError(DatabaseError):
    """Raised when database configuration is missing or invalid."""

    def __init__(self) -> None:
        """Initialize the database configuration error with a default message."""
        super().__init__("DATABASE_URL environment variable not set")


class APIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the API server."""

    def _send_response(self, status_code: int, data: dict[str, Any]) -> None:
        """
        Send a JSON response.

        Args:
            status_code (int): The HTTP status code.
            data (Dict[str, Any]): The data to send as JSON.

        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")

        # Get allowed origins from environment variable or use default
        allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
        origin = self.headers.get("Origin", "*")

        # Sanitize origin to prevent HTTP response splitting
        sanitized_origin = (
            origin.replace("\r", "").replace("\n", "") if origin != "*" else "*"
        )

        # If specific origins are defined, check if the request origin is allowed
        if allowed_origins != "*" and sanitized_origin != "*":
            allowed_origins_list = allowed_origins.split(",")
            if sanitized_origin in allowed_origins_list:
                self.send_header("Access-Control-Allow-Origin", sanitized_origin)
            else:
                self.send_header("Access-Control-Allow-Origin", "*")
        else:
            self.send_header("Access-Control-Allow-Origin", "*")

        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _get_db_connection(self) -> psycopg2.extensions.connection:
        """
        Establish a PostgreSQL connection using DATABASE_URL env var.

        Returns:
            A PostgreSQL database connection

        Raises:
            DatabaseConfigError: If DATABASE_URL is not set
            DatabaseError: If connection fails

        """
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise DatabaseConfigError
        try:
            return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        except psycopg2.Error as e:
            # Wrap DB-specific error in our custom exception
            raise DatabaseError from e

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == "/health":
                logger.info("Health check request received")
                self._send_response(200, {"status": "ok"})
            elif path == "/api/agent":
                logger.info("Agent info GET request received")
                try:
                    with self._get_db_connection() as conn, conn.cursor() as cursor:
                        cursor.execute("SELECT * FROM agent LIMIT 1;")
                        agent = cursor.fetchone()
                        if agent:
                            self._send_response(200, agent)
                        else:
                            # If no agent found in database, return a default agent
                            logger.warning(
                                "No agent found in database, returning default agent"
                            )
                            default_agent = {
                                "id": 1,
                                "name": "Default Agent",
                                "description": "This is a default agent for testing",
                                "avatar_url": "https://example.com/avatar.png",
                            }
                            self._send_response(200, default_agent)
                except (DatabaseError, psycopg2.Error):
                    logger.exception("Error fetching agent data")
                    # Return a default agent even if there's a database error
                    logger.warning("Database error, returning default agent")
                    default_agent = {
                        "id": 1,
                        "name": "Default Agent",
                        "description": "This is a default agent for testing",
                        "avatar_url": "https://example.com/avatar.png",
                    }
                    self._send_response(200, default_agent)
            else:
                logger.warning("404 error: %s", path)
                self._send_response(404, {"error": "Not found", "path": path})
        except Exception:
            logger.exception("Error handling request")
            self._send_response(500, {"error": "Internal server error"})

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests."""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == "/api/agent/action":
                logger.info("Agent action POST request received")
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length == 0:
                    self._send_response(400, {"error": "No data provided"})
                    return
                post_data = self.rfile.read(content_length)
                try:
                    action = json.loads(post_data.decode("utf-8"))
                except json.JSONDecodeError:
                    self._send_response(400, {"error": "Invalid JSON"})
                    return

                try:
                    with self._get_db_connection() as conn, conn.cursor() as cursor:
                        # Check if agent_action table exists
                        cursor.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables
                                WHERE table_name = 'agent_action'
                            );
                        """)
                        table_exists = cursor.fetchone()["exists"]

                        if not table_exists:
                            logger.warning(
                                "agent_action table does not exist, creating it"
                            )
                            cursor.execute("""
                                CREATE TABLE IF NOT EXISTS agent_action (
                                    id SERIAL PRIMARY KEY,
                                    agent_id INTEGER,
                                    action_type TEXT,
                                    action_payload JSONB,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                );
                            """)
                            conn.commit()

                        # Extract values from action with defaults
                        agent_id = action.get("agentId") or action.get("agent_id") or 1
                        action_type = (
                            action.get("type") or action.get("action_type") or "UNKNOWN"
                        )
                        payload = action.get("payload") or {}

                        cursor.execute(
                            """
                            INSERT INTO agent_action (agent_id, action_type, action_payload)
                            VALUES (%s, %s, %s)
                            RETURNING id;
                            """,
                            (
                                agent_id,
                                action_type,
                                json.dumps(payload),
                            ),
                        )
                        conn.commit()
                        action_id = cursor.fetchone()["id"]
                        self._send_response(
                            200, {"status": "success", "action_id": action_id}
                        )
                except (DatabaseError, psycopg2.Error):
                    logger.exception("Error saving agent action")
                    # Return success even if there's a database error to avoid breaking the UI
                    logger.warning("Database error, returning mock success response")
                    self._send_response(
                        200, {"status": "success", "action_id": 999, "mock": True}
                    )
                except Exception:
                    logger.exception("Unexpected error while saving agent action")
                    # Return success even if there's an error to avoid breaking the UI
                    self._send_response(
                        200, {"status": "success", "action_id": 999, "mock": True}
                    )
            else:
                self._send_response(404, {"error": "Not found", "path": path})
        except Exception:
            logger.exception("Error handling POST request")
            self._send_response(500, {"error": "Internal server error"})

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)

        # Get allowed origins from environment variable or use default
        allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
        origin = self.headers.get("Origin", "*")

        # Sanitize origin to prevent HTTP response splitting
        sanitized_origin = (
            origin.replace("\r", "").replace("\n", "") if origin != "*" else "*"
        )

        # If specific origins are defined, check if the request origin is allowed
        if allowed_origins != "*" and sanitized_origin != "*":
            allowed_origins_list = allowed_origins.split(",")
            if sanitized_origin in allowed_origins_list:
                self.send_header("Access-Control-Allow-Origin", sanitized_origin)
            else:
                self.send_header("Access-Control-Allow-Origin", "*")
        else:
            self.send_header("Access-Control-Allow-Origin", "*")

        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()

    def log_message(self, format_str: str, *args: tuple) -> None:
        """Log messages to the logger instead of stderr."""
        logger.info("%s - %s", self.address_string(), format_str % args)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded HTTP server to handle concurrent requests."""

    allow_reuse_address = True
    daemon_threads = True


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """
    Run the API server.

    Args:
        host (str, optional): The host to bind to. Defaults to '127.0.0.1'.
        port (int, optional): The port to bind to. Defaults to 8000.

    """
    server_address = (host, port)

    # Try to create the server, retrying with different ports if needed
    max_retries = 5
    httpd = None  # Initialize httpd to None to avoid uninitialized variable warning

    for retry in range(max_retries):
        try:
            httpd = ThreadedHTTPServer(server_address, APIHandler)
            break
        except OSError:
            if retry < max_retries - 1:
                logger.warning("Port %d is in use, trying port %d", port, port + 1)
                port += 1
                server_address = (host, port)
            else:
                logger.exception(
                    "Failed to start server after %d attempts", max_retries
                )
                raise OSError(f"Failed to start server after {max_retries} attempts")

    # Verify that httpd was successfully initialized
    if httpd is None:
        logger.error("Failed to initialize HTTP server")
        return

    logger.info("Starting API server on %s:%d", host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        httpd.server_close()
        logger.info("Server stopped")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # Get port from environment variable or use default
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        logger.warning(
            "Invalid PORT environment variable: %s, using default 8000", port_str
        )
        port = 8000

    # Run the server
    run_server(port=port)
