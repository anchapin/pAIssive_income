"""api_server - Module for ui.api_server.

This module provides a simple HTTP server for the UI module.
It includes a health check endpoint for monitoring.
"""

# Standard library imports
import http.server
import json
import logging
import os
import socketserver
from typing import Any
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class APIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the API server."""

    def _send_response(self, status_code: int, data: dict[str, Any]) -> None:
        """Send a JSON response.

        Args:
            status_code (int): The HTTP status code.
            data (Dict[str, Any]): The data to send as JSON.

        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow CORS
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == "/health":
                logger.info("Health check request received")
                self._send_response(200, {"status": "ok"})
            else:
                logger.warning(f"404 error: {path}")
                self._send_response(404, {"error": "Not found", "path": path})
        except Exception:
            logger.exception("Error handling request")
            self._send_response(500, {"error": "Internal server error"})

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format: str, *args: tuple) -> None:
        """Log messages to the logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded HTTP server to handle concurrent requests."""

    allow_reuse_address = True
    daemon_threads = True


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the API server.

    Args:
        host (str, optional): The host to bind to. Defaults to '0.0.0.0'.
        port (int, optional): The port to bind to. Defaults to 8000.

    """
    server_address = (host, port)

    # Try to create the server, retrying with different ports if needed
    max_retries = 5
    for retry in range(max_retries):
        try:
            httpd = ThreadedHTTPServer(server_address, APIHandler)
            break
        except OSError:
            if retry < max_retries - 1:
                logger.warning(f"Port {port} is in use, trying port {port + 1}")
                port += 1
                server_address = (host, port)
            else:
                logger.exception(
                    "Failed to start server after %d attempts", max_retries
                )
                raise

    logger.info(f"Starting API server on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        httpd.server_close()
        logger.info("Server stopped")


if __name__ == "__main__":
    # Get port from environment variable or use default
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        logger.warning(
            f"Invalid PORT environment variable: {port_str}, using default 8000"
        )
        port = 8000

    # Run the server
    run_server(port=port)
