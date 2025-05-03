"""
Socket.IO integration for the pAIssive Income UI.

This module provides real-time updates for long-running tasks and
user interactions using Socket.IO.
"""

import logging
from typing import Any, Dict, Optional

from flask_socketio import Namespace, SocketIO, emit, join_room, leave_room

from flask import Flask
from interfaces.ui_interfaces import ITaskService
from service_initialization import get_service

# Set up logging
logger = logging.getLogger(__name__)


class SocketIONamespace(Namespace):
    """Custom Socket.IO namespace for pAIssive Income events."""

    def on_connect(self):
        """Handle client connection."""
        logger.info("Client connected")

    def on_disconnect(self):
        """Handle client disconnection."""
        logger.info("Client disconnected")

    def on_join(self, data: Dict[str, Any]):
        """
        Join a task room to receive updates.

        Args:
            data: Dictionary containing task_id
        """
        task_id = data.get("task_id")
        if task_id:
            join_room(task_id)
            logger.info(f"Client joined room: {task_id}")

    def on_leave(self, data: Dict[str, Any]):
        """
        Leave a task room.

        Args:
            data: Dictionary containing task_id
        """
        task_id = data.get("task_id")
        if task_id:
            leave_room(task_id)
            logger.info(f"Client left room: {task_id}")

    def on_task_progress(self, data: Dict[str, Any]):
        """
        Handle task progress updates.

        Args:
            data: Progress update data including task_id, status, progress, and message
        """
        task_id = data.get("task_id")
        if task_id:
            emit("task_progress", data, room=task_id)
            logger.debug(f"Task progress update sent: {data}")

    def on_error(self, data: Dict[str, Any]):
        """
        Handle error events.

        Args:
            data: Error details including task_id and error message
        """
        task_id = data.get("task_id")
        if task_id:
            emit("error", data, room=task_id)
            logger.error(f"Error event sent: {data}")

    def on_get_status(self, data: Dict[str, Any]):
        """
        Handle status requests.

        Args:
            data: Dictionary containing task_id
        """
        task_id = data.get("task_id")
        if task_id:
            try:
                # Get task service and retrieve status
                task_service = get_service(ITaskService)
                status = task_service.get_task_status(task_id)
                emit("status", status)
                logger.debug(f"Status sent for task {task_id}: {status}")
            except Exception as e:
                error_data = {"task_id": task_id, "error": str(e), "type": "status_error"}
                emit("error", error_data)
                logger.error(f"Error getting status for task {task_id}: {e}")

    def on_model_update(self, data: Dict[str, Any]):
        """
        Handle model updates.

        Args:
            data: Model update information
        """
        emit("model_update", data, broadcast=True)
        logger.info(f"Model update broadcast: {data}")

    def on_resource_usage(self, data: Dict[str, Any]):
        """
        Handle resource usage updates.

        Args:
            data: Resource usage information
        """
        emit("resource_usage", data, broadcast=True)
        logger.debug(f"Resource usage broadcast: {data}")

    def on_authenticate(self, auth_data: Dict[str, Any]) -> bool:
        """
        Handle client authentication.

        Args:
            auth_data: Authentication data including token

        Returns:
            bool: True if authentication successful, False otherwise
        """
        token = auth_data.get("token")
        if not token:
            logger.warning("Authentication attempt without token")
            return False

        try:
            # Validate token (implement actual validation logic)
            is_valid = token == "valid_token"  # Replace with real validation
            if is_valid:
                logger.info("Client authenticated successfully")
            else:
                logger.warning("Invalid authentication token")
            return is_valid
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False


def init_socketio(app: Flask, async_mode: Optional[str] = None) -> SocketIO:
    """
    Initialize Socket.IO with the Flask application.

    Args:
        app: Flask application instance
        async_mode: Optional async mode (e.g., 'eventlet', 'gevent')

    Returns:
        Configured Socket.IO instance
    """
    # Create Socket.IO instance
    socketio = SocketIO(
        app,
        async_mode=async_mode,
        cors_allowed_origins="*",  # Configure as needed
        logger=True,
        engineio_logger=True,
    )

    # Register namespace
    socketio.on_namespace(SocketIONamespace("/"))

    # Register error handler
    @socketio.on_error_default
    def default_error_handler(e):
        logger.error(f"Socket.IO error: {e}")
        error_data = {"error": str(e), "type": "socket_error"}
        emit("error", error_data)

    return socketio
