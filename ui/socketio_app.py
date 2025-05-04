"""
"""
Flask-SocketIO integration for the pAIssive Income UI.
Flask-SocketIO integration for the pAIssive Income UI.


This module provides real-time communication between the server and clients
This module provides real-time communication between the server and clients
for updating task progress and status.
for updating task progress and status.
"""
"""


import logging
import logging
import time
import time
from typing import Any, Dict
from typing import Any, Dict


from celery.result import AsyncResult
from celery.result import AsyncResult
from flask_socketio import SocketIO, emit
from flask_socketio import SocketIO, emit


from .tasks import celery_app
from .tasks import celery_app






# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Initialize SocketIO without attaching it to app yet
# Initialize SocketIO without attaching it to app yet
socketio = SocketIO()
socketio = SocketIO()




def init_socketio(app):
    def init_socketio(app):
    """
    """
    Initialize SocketIO with the Flask app.
    Initialize SocketIO with the Flask app.


    Args:
    Args:
    app: Flask application
    app: Flask application
    """
    """
    socketio.init_app(app, async_mode="threading", cors_allowed_origins="*")
    socketio.init_app(app, async_mode="threading", cors_allowed_origins="*")
    logger.info("SocketIO initialized")
    logger.info("SocketIO initialized")


    # Define socket events
    # Define socket events
    @socketio.on("connect")
    @socketio.on("connect")
    def handle_connect():
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
    """
    Handle client subscription to task updates.
    Handle client subscription to task updates.


    Args:
    Args:
    data: Dictionary with task_id
    data: Dictionary with task_id
    """
    """
    task_id = data.get("task_id")
    task_id = data.get("task_id")
    if not task_id:
    if not task_id:
    emit("error", {"message": "No task ID provided"})
    emit("error", {"message": "No task ID provided"})
    return
    return


    logger.info(f"Client {socketio.request.sid} subscribed to task {task_id}")
    logger.info(f"Client {socketio.request.sid} subscribed to task {task_id}")


    # Join a room named after the task ID
    # Join a room named after the task ID
    socketio.join_room(task_id)
    socketio.join_room(task_id)


    # Send initial task status
    # Send initial task status
    task_result = AsyncResult(task_id, app=celery_app)
    task_result = AsyncResult(task_id, app=celery_app)


    if task_result.state == "PENDING":
    if task_result.state == "PENDING":
    response = {
    response = {
    "state": task_result.state,
    "state": task_result.state,
    "current": 0,
    "current": 0,
    "total": 100,
    "total": 100,
    "status": "Pending...",
    "status": "Pending...",
    "result": {},
    "result": {},
    }
    }
    elif task_result.state == "FAILURE":
    elif task_result.state == "FAILURE":
    response = {
    response = {
    "state": task_result.state,
    "state": task_result.state,
    "current": 0,
    "current": 0,
    "total": 100,
    "total": 100,
    "status": str(task_result.info),
    "status": str(task_result.info),
    "result": {},
    "result": {},
    }
    }
    else:
    else:
    response = task_result.info if task_result.info else {}
    response = task_result.info if task_result.info else {}
    if "result" not in response:
    if "result" not in response:
    response["result"] = {}
    response["result"] = {}


    emit("task_update", response)
    emit("task_update", response)


    @socketio.on("unsubscribe")
    @socketio.on("unsubscribe")
    def handle_unsubscribe(data):
    def handle_unsubscribe(data):
    """
    """
    Handle client unsubscription from task updates.
    Handle client unsubscription from task updates.


    Args:
    Args:
    data: Dictionary with task_id
    data: Dictionary with task_id
    """
    """
    task_id = data.get("task_id")
    task_id = data.get("task_id")
    if not task_id:
    if not task_id:
    emit("error", {"message": "No task ID provided"})
    emit("error", {"message": "No task ID provided"})
    return
    return


    logger.info(f"Client {socketio.request.sid} unsubscribed from task {task_id}")
    logger.info(f"Client {socketio.request.sid} unsubscribed from task {task_id}")


    # Leave the room named after the task ID
    # Leave the room named after the task ID
    socketio.leave_room(task_id)
    socketio.leave_room(task_id)
    emit("unsubscribe_response", {"status": "unsubscribed"})
    emit("unsubscribe_response", {"status": "unsubscribed"})


    @socketio.on_error()
    @socketio.on_error()
    def handle_error(e):
    def handle_error(e):
    """Handle socket error."""
    logger.error(f"SocketIO error: {str(e)}")


    def emit_task_update(task_id: str, data: Dict[str, Any]):
    """
    """
    Emit task update to subscribed clients.
    Emit task update to subscribed clients.


    Args:
    Args:
    task_id: ID of the task
    task_id: ID of the task
    data: Dictionary with task status and progress
    data: Dictionary with task status and progress
    """
    """
    socketio.emit("task_update", data, room=task_id)
    socketio.emit("task_update", data, room=task_id)
    logger.debug(f"Task update emitted for {task_id}: {data}")
    logger.debug(f"Task update emitted for {task_id}: {data}")