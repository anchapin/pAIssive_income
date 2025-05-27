"""test_api_server - Module for tests/ui.test_api_server."""

# Standard library imports
import http.client
import json
import logging
import socket
import sys
import threading
import time
import unittest

import pytest

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
    mock_server = None
    server_stopped = None

    @classmethod
    def setUpClass(cls):
        """Start the server in a separate thread."""
        # Create an event to signal when the server has stopped
        cls.server_stopped = threading.Event()

        # Find an available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))
            cls.port = s.getsockname()[1]

        # Define a function to run the server and handle shutdown
        def run_test_server():
            try:
                # Create the server
                server_address = ("localhost", cls.port)
                from ui.api_server import APIHandler, ThreadedHTTPServer
                cls.mock_server = ThreadedHTTPServer(server_address, APIHandler)

                # Set timeout to ensure serve_forever doesn't block indefinitely
                cls.mock_server.timeout = 0.5

                # Run the server until interrupted
                cls.mock_server.serve_forever()
            except KeyboardInterrupt:
                # Server will be stopped by the teardown method
                print("Server interrupted by keyboard")
            except OSError as e:
                # Port might be in use
                print(f"Could not start server: {e}")
                cls.server_stopped.set()  # Signal that the server failed to start
            except Exception as e:
                print(f"Unexpected error in server thread: {e}")
            finally:
                print("Server thread exiting")
                if cls.mock_server:
                    try:
                        cls.mock_server.server_close()
                    except Exception as e:
                        print(f"Error closing server: {e}")
                cls.server_stopped.set()  # Signal that the server has stopped

        # Start the server in a separate thread
        cls.server_thread = threading.Thread(target=run_test_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Wait for the server to start
        time.sleep(1)

        # Check if the server started successfully
        if cls.server_stopped.is_set() and not cls.mock_server:
            pytest.skip("Failed to start test server")

    @classmethod
    def tearDownClass(cls):
        """Stop the server."""
        # Stop the server if it's running
        if cls.mock_server:
            try:
                # Use the proper method to shut down the server
                cls.mock_server.shutdown()

                # Close the server socket
                cls.mock_server.server_close()

                # Wait for the server to stop
                cls.server_stopped.wait(timeout=2.0)

                # Join the thread with a timeout
                cls.server_thread.join(timeout=1.0)

                # If the thread is still alive, log a warning and try to force it to stop
                if cls.server_thread.is_alive():
                    print("Warning: Server thread did not terminate cleanly")
                    # In Python 3.9+, we could use thread_obj.is_alive() here
                    # For compatibility with older Python versions, we'll just log the warning
            except Exception as e:
                print(f"Error shutting down server: {e}")
            finally:
                # Ensure the server is marked as stopped
                cls.server_stopped.set()
                cls.mock_server = None

    def test_health_check(self):
        """Test the health check endpoint."""
        conn = None
        try:
            conn = http.client.HTTPConnection("localhost", self.port, timeout=5)
            conn.request("GET", "/health")
            response = conn.getresponse()
            data = json.loads(response.read().decode())

            assert response.status == HTTP_OK
            assert data["status"] == "ok"
        finally:
            if conn:
                conn.close()

    def test_not_found(self):
        """Test the 404 error handler."""
        conn = None
        try:
            conn = http.client.HTTPConnection("localhost", self.port, timeout=5)
            conn.request("GET", "/nonexistent-endpoint")
            response = conn.getresponse()
            data = json.loads(response.read().decode())

            assert response.status == HTTP_NOT_FOUND
            assert data["error"] == "Not found"
            assert data["path"] == "/nonexistent-endpoint"
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    unittest.main()
