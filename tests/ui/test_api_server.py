"""test_api_server - Module for tests/ui.test_api_server."""

# Standard library imports
import http.client
import json
import os

# Local imports
import sys
import threading
import time
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ui.api_server import run_server


class TestAPIServer(unittest.TestCase):
    """Test suite for the API server."""

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

        self.assertEqual(response.status, 200)
        self.assertEqual(data["status"], "ok")
        conn.close()

    def test_not_found(self):
        """Test the 404 error handler."""
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request("GET", "/nonexistent-endpoint")
        response = conn.getresponse()
        data = json.loads(response.read().decode())

        self.assertEqual(response.status, 404)
        self.assertEqual(data["error"], "Not found")
        self.assertEqual(data["path"], "/nonexistent-endpoint")
        conn.close()


if __name__ == "__main__":
    unittest.main()
