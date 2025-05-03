"""
Task manager for the pAIssive Income UI.

This module provides utilities for managing asynchronous tasks.
"""


import logging
from typing import Any, Dict, Optional

from celery.result import AsyncResult

from .tasks import celery_app



# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the current status of a task.

    Args:
        task_id: ID of the task

    Returns:
        Dictionary with task status information
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        response = {
            "state": task_result.state,
            "current": 0,
            "total": 100,
            "status": "Pending...",
            "result": None,
        }
    elif task_result.state == "PROGRESS":
        response = {
            "state": task_result.state,
            "current": task_result.info.get("current", 0),
            "total": task_result.info.get("total", 100),
            "status": task_result.info.get("message", ""),
            "result": task_result.info.get("result"),
        }
    elif task_result.state == "FAILURE":
        response = {
            "state": task_result.state,
            "current": 100,
            "total": 100,
            "status": "Failed",
            "error": str(task_result.info),
            "result": None,
        }
    elif task_result.state == "SUCCESS":
        response = {
            "state": task_result.state,
            "current": 100,
            "total": 100,
            "status": "Completed",
            "result": task_result.result,
        }
    else:
        response = {
            "state": task_result.state,
            "current": 0,
            "total": 100,
            "status": "Unknown state",
            "result": None,
        }

    return response


def check_task_completion(task_id: str) -> bool:
    """
    Check if a task is completed.

    Args:
        task_id: ID of the task

    Returns:
        True if the task is completed (success or failure), False otherwise
    """
    task_result = AsyncResult(task_id, app=celery_app)
    return task_result.ready()


def store_task_id(session, key: str, task_id: str) -> None:
    """
    Store a task ID in the session.

    Args:
        session: Flask session object
        key: Key to store the task ID under
        task_id: ID of the task
    """
    if "tasks" not in session:
        session["tasks"] = {}

    session["tasks"][key] = task_id
    session.modified = True


def get_task_id(session, key: str) -> Optional[str]:
    """
    Get a task ID from the session.

    Args:
        session: Flask session object
        key: Key the task ID is stored under

    Returns:
        Task ID if found, None otherwise
    """
    if "tasks" not in session:
        return None

    return session["tasks"].get(key)


def cancel_task(task_id: str) -> bool:
    """
    Cancel a running task.

    Args:
        task_id: ID of the task

    Returns:
        True if the task was cancelled, False otherwise
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state in ["PENDING", "STARTED", "PROGRESS"]:
        task_result.revoke(terminate=True)
        logger.info(f"Task {task_id} cancelled")
        return True
    else:
        logger.info(
            f"Task {task_id} could not be cancelled (state: {task_result.state})"
        )
        return False