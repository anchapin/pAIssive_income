"""
Tests for Socket.IO integration in the pAIssive Income UI.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from flask_socketio import SocketIO

from flask import Flask
from ui.socketio_app import SocketIONamespace, init_socketio


@pytest.fixture
def mock_app():
    """Create a mock Flask app."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test_key"
    return app


@pytest.fixture
def mock_socketio(mock_app):
    """Create a mock Socket.IO instance."""
    return init_socketio(mock_app)


@pytest.fixture
def mock_client(mock_app, mock_socketio):
    """Create a mock Socket.IO test client."""
    return mock_socketio.test_client(mock_app)


class TestSocketIOIntegration:
    """Test Socket.IO integration."""

    def test_connection(self, mock_client):
        """Test client connection."""
        assert mock_client.is_connected()

    def test_disconnect(self, mock_client):
        """Test client disconnection."""
        mock_client.disconnect()
        assert not mock_client.is_connected()

    def test_task_progress_update(self, mock_client):
        """Test task progress update event."""
        # Connect a client and join a room
        mock_client.connect()
        mock_client.emit("join", {"task_id": "test_task"})

        # Emit a progress update
        mock_client.get_received()  # Clear received messages
        mock_client.emit(
            "task_progress",
            {
                "task_id": "test_task",
                "status": "ANALYZING",
                "progress": 50,
                "message": "Analyzing data...",
            },
        )

        # Check received messages
        received = mock_client.get_received()
        assert len(received) == 1
        assert received[0]["name"] == "task_progress"
        assert received[0]["args"][0]["task_id"] == "test_task"
        assert received[0]["args"][0]["status"] == "ANALYZING"
        assert received[0]["args"][0]["progress"] == 50

    def test_multiple_clients_task_updates(self, mock_app, mock_socketio):
        """Test task updates with multiple clients."""
        # Create two test clients
        client1 = mock_socketio.test_client(mock_app)
        client2 = mock_socketio.test_client(mock_app)

        # Connect both clients and join the same task room
        client1.connect()
        client2.connect()
        task_id = "shared_task"
        client1.emit("join", {"task_id": task_id})
        client2.emit("join", {"task_id": task_id})

        # Clear received messages
        client1.get_received()
        client2.get_received()

        # Emit a progress update
        update_data = {
            "task_id": task_id,
            "status": "PROCESSING",
            "progress": 75,
            "message": "Processing shared task...",
        }
        mock_socketio.emit("task_progress", update_data, room=task_id)

        # Check that both clients received the update
        received1 = client1.get_received()
        received2 = client2.get_received()
        assert len(received1) == len(received2) == 1
        assert received1[0]["name"] == received2[0]["name"] == "task_progress"
        assert received1[0]["args"][0] == received2[0]["args"][0] == update_data

    def test_error_handling(self, mock_client):
        """Test error event handling."""
        # Connect client
        mock_client.connect()

        # Emit an error event
        mock_client.get_received()  # Clear received messages
        error_data = {
            "error": "Task failed",
            "task_id": "error_task",
            "details": "An unexpected error occurred",
        }
        mock_client.emit("error", error_data)

        # Check received messages
        received = mock_client.get_received()
        assert len(received) == 1
        assert received[0]["name"] == "error"
        assert received[0]["args"][0]["error"] == "Task failed"
        assert received[0]["args"][0]["task_id"] == "error_task"

    def test_room_management(self, mock_client):
        """Test room joining and leaving."""
        # Connect client
        mock_client.connect()

        # Join a room
        mock_client.get_received()  # Clear received messages
        mock_client.emit("join", {"task_id": "room_test"})

        # Leave the room
        mock_client.emit("leave", {"task_id": "room_test"})

        # Try to receive updates (should not receive any)
        mock_socketio = SocketIO()
        mock_socketio.emit(
            "task_progress",
            {"task_id": "room_test", "status": "COMPLETE", "progress": 100},
            room="room_test",
        )

        received = mock_client.get_received()
        assert len([msg for msg in received if msg["name"] == "task_progress"]) == 0

    @patch("ui.socketio_app.get_service")
    def test_service_integration(self, mock_get_service, mock_client):
        """Test integration with services."""
        # Create mock service
        mock_service = MagicMock()
        mock_service.get_task_status.return_value = {
            "status": "RUNNING",
            "progress": 60,
            "message": "Processing task...",
        }
        mock_get_service.return_value = mock_service

        # Connect client and request status
        mock_client.connect()
        mock_client.get_received()  # Clear received messages
        mock_client.emit("get_status", {"task_id": "service_test"})

        # Check that service was called and response was sent
        received = mock_client.get_received()
        assert len(received) == 1
        assert received[0]["args"][0]["status"] == "RUNNING"
        assert received[0]["args"][0]["progress"] == 60

    def test_broadcast_messages(self, mock_app, mock_socketio):
        """Test broadcasting messages to all clients."""
        # Create multiple test clients
        clients = [
            mock_socketio.test_client(mock_app),
            mock_socketio.test_client(mock_app),
            mock_socketio.test_client(mock_app),
        ]

        # Connect all clients
        for client in clients:
            client.connect()
            client.get_received()  # Clear initial messages

        # Broadcast a message
        broadcast_data = {"type": "system_update", 
            "message": "System maintenance in 5 minutes"}
        mock_socketio.emit("broadcast", broadcast_data)

        # Check that all clients received the message
        for client in clients:
            received = client.get_received()
            assert len(received) == 1
            assert received[0]["name"] == "broadcast"
            assert received[0]["args"][0] == broadcast_data

    def test_custom_events(self, mock_client):
        """Test handling of custom events."""
        # Connect client
        mock_client.connect()
        mock_client.get_received()  # Clear received messages

        # Test custom events
        events = [
            {
                "name": "model_update",
                "data": {
                    "model_id": "gpt - 4",
                    "status": "ready",
                    "capabilities": ["text", "chat", "embeddings"],
                },
            },
            {"name": "resource_usage", "data": {"cpu": 45.2, "memory": 1024.5, 
                "requests": 150}},
        ]

        # Emit each custom event
        for event in events:
            mock_client.emit(event["name"], event["data"])
            received = mock_client.get_received()
            assert len(received) == 1
            assert received[0]["name"] == event["name"]
            assert received[0]["args"][0] == event["data"]

    def test_namespace_handlers(self, mock_app):
        """Test custom namespace event handlers."""

        # Create a custom namespace
        class TestNamespace(SocketIONamespace):
            def on_custom_event(self, data):
                self.emit("custom_response", {"received": data})

        # Create Socket.IO instance with custom namespace
        socketio = SocketIO(mock_app)
        socketio.on_namespace(TestNamespace(" / test"))

        # Create test client with custom namespace
        client = socketio.test_client(mock_app, namespace=" / test")

        # Test custom event handling
        client.emit("custom_event", {"test": "data"}, namespace=" / test")
        received = client.get_received(namespace=" / test")
        assert len(received) == 1
        assert received[0]["name"] == "custom_response"
        assert received[0]["args"][0]["received"] == {"test": "data"}

    def test_authentication(self, mock_app):
        """Test Socket.IO authentication."""
        # Create Socket.IO instance with authentication
        socketio = SocketIO(mock_app)

        @socketio.on("authenticate")
        def handle_auth(auth_data):
            if auth_data.get("token") == "valid_token":
                return True
            return False

        # Create test client
        client = socketio.test_client(mock_app)

        # Test successful authentication
        client.emit("authenticate", {"token": "valid_token"})
        received = client.get_received()
        assert len(received) > 0
        assert received[0]["args"][0] is True

        # Test failed authentication
        client.emit("authenticate", {"token": "invalid_token"})
        received = client.get_received()
        assert len(received) > 0
        assert received[0]["args"][0] is False
