"""
Flask-SocketIO integration for the pAIssive Income UI.

This module provides real-time communication between the server and clients
for updating task progress and status.
"""

import logging
from typing import Any, Dict

from celery.result import AsyncResult
from flask_socketio import SocketIO, emit

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize SocketIO without attaching it to app yet
socketio = SocketIO()


def init_socketio(app):
    """
    Initialize SocketIO with the Flask app.

    Args:
        app: Flask application
    """
    socketio.init_app(app, async_mode="threading", cors_allowed_origins="*")
    logger.info("SocketIO initialized")

    # Define socket events
    @socketio.on("connect")
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {socketio.request.sid}")
        emit("connect_response", {"status": "connected"})

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {socketio.request.sid}")

    @socketio.on("subscribe")
    def handle_subscribe(data):
        """
        Handle client subscription to task updates.

        Args:
            data: Dictionary with task_id
        """
        task_id = data.get("task_id")
        if not task_id:
            emit("error", {"message": "No task ID provided"})
            return

        logger.info(f"Client {socketio.request.sid} subscribed to task {task_id}")

        # Join a room named after the task ID
        socketio.join_room(task_id)

        # Send initial task status
        from .tasks import celery_app

        task_result = AsyncResult(task_id, app=celery_app)

        if task_result.state == "PENDING":
            response = {
                "state": task_result.state,
                "current": 0,
                "total": 100,
                "status": "Pending...",
                "result": {},
            }
        elif task_result.state == "FAILURE":
            response = {
                "state": task_result.state,
                "current": 0,
                "total": 100,
                "status": str(task_result.info),
                "result": {},
            }
        else:
            response = task_result.info if task_result.info else {}
            if "result" not in response:
                response["result"] = {}

        emit("task_update", response)

    @socketio.on("unsubscribe")
    def handle_unsubscribe(data):
        """
        Handle client unsubscription from task updates.

        Args:
            data: Dictionary with task_id
        """
        task_id = data.get("task_id")
        if not task_id:
            emit("error", {"message": "No task ID provided"})
            return

        logger.info(f"Client {socketio.request.sid} unsubscribed from task {task_id}")

        # Leave the room named after the task ID
        socketio.leave_room(task_id)
        emit("unsubscribe_response", {"status": "unsubscribed"})

    @socketio.on_error()
    def handle_error(e):
        """Handle socket error."""
        logger.error(f"SocketIO error: {str(e)}")


def emit_task_update(task_id: str, data: Dict[str, Any]):
    """
    Emit task update to subscribed clients.

    Args:
        task_id: ID of the task
        data: Dictionary with task status and progress
    """
    socketio.emit("task_update", data, room=task_id)
    logger.debug(f"Task update emitted for {task_id}: {data}")
