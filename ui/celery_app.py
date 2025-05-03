"""
Celery configuration for the pAIssive Income UI.

This module sets up Celery for handling asynchronous tasks and
integrates with Socket.IO for real-time progress updates.
"""
import logging
from typing import Any, Dict, Optional

from celery import Celery
from celery.signals import (
    after_task_publish,
    task_failure,
    task_prerun,
    task_success,
)

from flask import Flask

from .socketio_app import socketio

# Set up logging
logger = logging.getLogger(__name__)

def create_celery_app(app: Flask) -> Celery:
    """
    Create and configure Celery for the Flask application.

    Args:
        app: Flask application instance

    Returns:
        Configured Celery instance
    """
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    )

    # Configure Celery
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_publish_retry=True,
        task_publish_retry_policy={
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 0.5,
        },
    )

    class ContextTask(celery.Task):
        """Task that maintains Flask application context."""

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            """Execute task with application context."""
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def emit_task_event(event_name: str, task_id: str, data: Dict[str, Any]):
    """
    Emit a Socket.IO event for task updates.

    Args:
        event_name: Name of the event
        task_id: ID of the task
        data: Event data
    """
    try:
        event_data = {"task_id": task_id, **data}
        socketio.emit(event_name, event_data, room=task_id)
        logger.debug(f"Emitted {event_name} for task {task_id}: {data}")
    except Exception as e:
        logger.error(f"Error emitting {event_name} for task {task_id}: {e}")

@after_task_publish.connect
def task_sent_handler(sender: Optional[str] = None, headers: Optional[Dict] = None, **kwargs):
    """
    Handle task publish events.

    Args:
        sender: Name of the task
        headers: Task headers
        kwargs: Additional arguments
    """
    try:
        task_id = headers.get("id") if headers else None
        if task_id:
            emit_task_event(
                "task_progress",
                task_id,
                {
                    "status": "PENDING",
                    "message": "Task queued",
                    "progress": 0
                }
            )
    except Exception as e:
        logger.error(f"Error in task_sent_handler: {e}")

@task_prerun.connect
def task_prerun_handler(task_id: str, task: Any, *args, **kwargs):
    """
    Handle task pre-run events.

    Args:
        task_id: ID of the task
        task: Task instance
        args: Additional arguments
        kwargs: Additional keyword arguments
    """
    try:
        emit_task_event(
            "task_progress",
            task_id,
            {
                "status": "STARTED",
                "message": "Task started",
                "progress": 0
            }
        )
    except Exception as e:
        logger.error(f"Error in task_prerun_handler: {e}")

@task_success.connect
def task_success_handler(sender: Optional[Any] = None, result: Any = None, **kwargs):
    """
    Handle task success events.

    Args:
        sender: Task instance
        result: Task result
        kwargs: Additional keyword arguments
    """
    try:
        task_id = sender.request.id if sender and sender.request else None
        if task_id:
            emit_task_event(
                "task_progress",
                task_id,
                {
                    "status": "SUCCESS",
                    "message": "Task completed successfully",
                    "progress": 100,
                    "result": result
                }
            )
    except Exception as e:
        logger.error(f"Error in task_success_handler: {e}")

@task_failure.connect
def task_failure_handler(
    sender: Optional[Any] = None,
    exception: Optional[Exception] = None,
    traceback: Optional[str] = None,
    **kwargs
):
    """
    Handle task failure events.

    Args:
        sender: Task instance
        exception: Exception that occurred
        traceback: Exception traceback
        kwargs: Additional keyword arguments
    """
    try:
        task_id = sender.request.id if sender and sender.request else None
        if task_id:
            emit_task_event(
                "error",
                task_id,
                {
                    "status": "FAILURE",
                    "message": f"Task failed: {str(exception)}",
                    "error": str(exception),
                    "traceback": traceback,
                }
            )
    except Exception as e:
        logger.error(f"Error in task_failure_handler: {e}")

# Create Celery instance (will be initialized with create_celery_app)
celery_app = Celery(__name__)
