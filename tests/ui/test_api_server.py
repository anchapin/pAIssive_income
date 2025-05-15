"""test_api_server - Module for tests/ui.test_api_server."""

# Standard library imports
import http.client
import json
import sys
import threading
import time
import unittest

# Constants
HTTP_OK = 200
HTTP_NOT_FOUND = 404

# Add the project root to the Python path
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

# Local imports - this import must be after sys.path modification
# flake8: noqa: E402
from ui.api_server import run_server


class TestAPIServer(unittest.TestCase):
    """Test suite for the API server."""

    # Declare server_thread as a class attribute
    server_thread: threading.Thread

    @classmethod
    def setUpClass(cls):
        """Start the server in a separate thread."""
        cls.server_thread = threading.Thread(
            target=run_server, kwargs={"host": "localhost", "port": 8000}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Wait for the server to start
        time.sleep(1)

    def test_health_check(self):
        """Test the health check endpoint."""
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request("GET", "/health")
        response = conn.getresponse()
        data = json.loads(response.read().decode())

        assert response.status == HTTP_OK
        assert data["status"] == "ok"
        conn.close()

    def test_not_found(self):
        """Test the 404 error handler."""
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request("GET", "/nonexistent-endpoint")
        response = conn.getresponse()
        data = json.loads(response.read().decode())

        assert response.status == HTTP_NOT_FOUND
        assert data["error"] == "Not found"
        assert data["path"] == "/nonexistent-endpoint"
        conn.close()


if __name__ == "__main__":
    unittest.main()
