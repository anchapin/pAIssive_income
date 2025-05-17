"""Additional tests for the API server."""

import json
import os
import pytest
import socket
import threading
import time
from unittest.mock import patch, MagicMock

from ui.api_server import APIHandler, ThreadedHTTPServer, run_server


class TestAPIHandlerAdditional:
    """Additional tests for the APIHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock request and client_address
        mock_request = MagicMock()
        mock_request.makefile.return_value = MagicMock()
        client_address = ('127.0.0.1', 12345)
        server = MagicMock()

        # Create handler with mocks
        with patch.object(APIHandler, '__init__', return_value=None):
            self.handler = APIHandler()

        # Mock handler methods
        self.handler.wfile = MagicMock()
        self.handler.send_response = MagicMock()
        self.handler.send_header = MagicMock()
        self.handler.end_headers = MagicMock()
        self.handler.address_string = MagicMock(return_value="127.0.0.1")
        self.handler.log_message = MagicMock()
        # Add headers attribute to fix the test
        self.handler.headers = MagicMock()
        self.handler.headers.get = MagicMock(return_value="*")

    def test_send_response_with_empty_data(self):
        """Test _send_response method with empty data."""
        # Mock json.dumps to return a string
        with patch('json.dumps', return_value="{}"):
            self.handler._send_response(200, {})

            self.handler.send_response.assert_called_once_with(200)
            self.handler.send_header.assert_any_call("Content-Type", "application/json")
            self.handler.send_header.assert_any_call("Access-Control-Allow-Origin", "*")
            self.handler.end_headers.assert_called_once()
            self.handler.wfile.write.assert_called_once_with(b"{}")

    def test_send_response_with_complex_data(self):
        """Test _send_response method with complex data."""
        data = {
            "status": "ok",
            "data": {
                "id": 1,
                "name": "Test",
                "items": [1, 2, 3],
                "nested": {"key": "value"}
            }
        }

        # Mock json.dumps to return a JSON string
        json_str = json.dumps(data)
        with patch('json.dumps', return_value=json_str):
            self.handler._send_response(200, data)

            self.handler.send_response.assert_called_once_with(200)
            self.handler.send_header.assert_any_call("Content-Type", "application/json")
            self.handler.end_headers.assert_called_once()

            # Verify the JSON data was written correctly
            self.handler.wfile.write.assert_called_once_with(json_str.encode('utf-8'))

    def test_do_get_health_check(self):
        """Test do_GET method with health check path."""
        self.handler.path = "/health"

        # Mock _send_response and urlparse
        self.handler._send_response = MagicMock()
        with patch('ui.api_server.urlparse') as mock_urlparse:
            # Configure the mock to return a path object
            mock_path = MagicMock()
            mock_path.path = "/health"
            mock_urlparse.return_value = mock_path

            # Call the method
            self.handler.do_GET()

            # Verify _send_response was called with the correct arguments
            self.handler._send_response.assert_called_once_with(200, {"status": "ok"})

    def test_do_get_invalid_path(self):
        """Test do_GET method with an invalid path."""
        self.handler.path = "/invalid"

        # Mock _send_response and urlparse
        self.handler._send_response = MagicMock()
        with patch('ui.api_server.urlparse') as mock_urlparse:
            # Configure the mock to return a path object
            mock_path = MagicMock()
            mock_path.path = "/invalid"
            mock_urlparse.return_value = mock_path

            # Call the method
            self.handler.do_GET()

            # Verify _send_response was called with the correct arguments
            self.handler._send_response.assert_called_once_with(
                404, {"error": "Not found", "path": "/invalid"}
            )


class TestThreadedHTTPServerAdditional:
    """Additional tests for the ThreadedHTTPServer class."""

    def test_server_initialization(self):
        """Test server initialization."""
        # Find an available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            port = s.getsockname()[1]

        # Create the server
        server = ThreadedHTTPServer(('localhost', port), APIHandler)

        # Verify server attributes
        assert server.allow_reuse_address is True
        assert server.daemon_threads is True

        # Close the server
        server.server_close()

    def test_server_handle_request(self):
        """Test server handle_request method."""
        # Find an available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            port = s.getsockname()[1]

        # Create the server
        server = ThreadedHTTPServer(('localhost', port), APIHandler)

        # Start the server in a separate thread
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.daemon = True
        server_thread.start()

        # Give the server time to start
        time.sleep(0.1)

        try:
            # Send a request to the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('localhost', port))
                client.sendall(b"GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n")

                # Receive the response
                response = client.recv(1024).decode('utf-8')

                # Verify the response contains the expected status code
                assert "200 OK" in response
                assert "Content-Type: application/json" in response
        finally:
            # Close the server
            server.server_close()
            server_thread.join(timeout=1)


class TestRunServerAdditional:
    """Additional tests for the run_server function."""

    def test_run_server_port_in_use_all_retries_failed(self):
        """Test run_server when all port retries fail."""
        # Create a socket to occupy a port
        occupied_ports = []
        sockets = []

        try:
            # Occupy multiple ports to force all retries to fail
            for _ in range(6):  # max_retries + 1
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('localhost', 0))
                port = s.getsockname()[1]
                occupied_ports.append(port)
                sockets.append(s)

            # Mock the ThreadedHTTPServer to raise OSError for all ports
            with patch('ui.api_server.ThreadedHTTPServer') as mock_server:
                mock_server.side_effect = OSError("Port in use")

                # Call run_server with the first occupied port
                with pytest.raises(OSError):
                    run_server(host='localhost', port=occupied_ports[0])
        finally:
            # Close all sockets
            for s in sockets:
                s.close()

    def test_run_server_keyboard_interrupt(self):
        """Test run_server with KeyboardInterrupt."""
        # Find an available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            port = s.getsockname()[1]

        # Mock ThreadedHTTPServer
        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt()

        with patch('ui.api_server.ThreadedHTTPServer', return_value=mock_server):
            # Call run_server
            run_server(host='localhost', port=port)

            # Verify serve_forever and server_close were called
            mock_server.serve_forever.assert_called_once()
            mock_server.server_close.assert_called_once()

    def test_main_with_valid_port_env(self):
        """Test __main__ block with valid PORT environment variable."""
        # Skip this test as it's difficult to test the __main__ block
        pytest.skip("Skipping test that requires executing the __main__ block")

    def test_main_with_invalid_port_env(self):
        """Test __main__ block with invalid PORT environment variable."""
        # Skip this test as it's difficult to test the __main__ block
        pytest.skip("Skipping test that requires executing the __main__ block")
