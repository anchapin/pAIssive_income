"""
"""
Task manager for the pAIssive Income UI.
Task manager for the pAIssive Income UI.


This module provides utilities for managing asynchronous tasks.
This module provides utilities for managing asynchronous tasks.
"""
"""




import logging
import logging
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


from celery.result import AsyncResult
from celery.result import AsyncResult


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




def get_task_status(task_id: str) -> Dict[str, Any]:
    def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    """
    Get the current status of a task.
    Get the current status of a task.


    Args:
    Args:
    task_id: ID of the task
    task_id: ID of the task


    Returns:
    Returns:
    Dictionary with task status information
    Dictionary with task status information
    """
    """
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
    "result": None,
    "result": None,
    }
    }
    elif task_result.state == "PROGRESS":
    elif task_result.state == "PROGRESS":
    response = {
    response = {
    "state": task_result.state,
    "state": task_result.state,
    "current": task_result.info.get("current", 0),
    "current": task_result.info.get("current", 0),
    "total": task_result.info.get("total", 100),
    "total": task_result.info.get("total", 100),
    "status": task_result.info.get("message", ""),
    "status": task_result.info.get("message", ""),
    "result": task_result.info.get("result"),
    "result": task_result.info.get("result"),
    }
    }
    elif task_result.state == "FAILURE":
    elif task_result.state == "FAILURE":
    response = {
    response = {
    "state": task_result.state,
    "state": task_result.state,
    "current": 100,
    "current": 100,
    "total": 100,
    "total": 100,
    "status": "Failed",
    "status": "Failed",
    "error": str(task_result.info),
    "error": str(task_result.info),
    "result": None,
    "result": None,
    }
    }
    elif task_result.state == "SUCCESS":
    elif task_result.state == "SUCCESS":
    response = {
    response = {
    "state": task_result.state,
    "state": task_result.state,
    "current": 100,
    "current": 100,
    "total": 100,
    "total": 100,
    "status": "Completed",
    "status": "Completed",
    "result": task_result.result,
    "result": task_result.result,
    }
    }
    else:
    else:
    response = {
    response = {
    "state": task_result.state,
    "state": task_result.state,
    "current": 0,
    "current": 0,
    "total": 100,
    "total": 100,
    "status": "Unknown state",
    "status": "Unknown state",
    "result": None,
    "result": None,
    }
    }


    return response
    return response




    def check_task_completion(task_id: str) -> bool:
    def check_task_completion(task_id: str) -> bool:
    """
    """
    Check if a task is completed.
    Check if a task is completed.


    Args:
    Args:
    task_id: ID of the task
    task_id: ID of the task


    Returns:
    Returns:
    True if the task is completed (success or failure), False otherwise
    True if the task is completed (success or failure), False otherwise
    """
    """
    task_result = AsyncResult(task_id, app=celery_app)
    task_result = AsyncResult(task_id, app=celery_app)
    return task_result.ready()
    return task_result.ready()




    def store_task_id(session, key: str, task_id: str) -> None:
    def store_task_id(session, key: str, task_id: str) -> None:
    """
    """
    Store a task ID in the session.
    Store a task ID in the session.


    Args:
    Args:
    session: Flask session object
    session: Flask session object
    key: Key to store the task ID under
    key: Key to store the task ID under
    task_id: ID of the task
    task_id: ID of the task
    """
    """
    if "tasks" not in session:
    if "tasks" not in session:
    session["tasks"] = {}
    session["tasks"] = {}


    session["tasks"][key] = task_id
    session["tasks"][key] = task_id
    session.modified = True
    session.modified = True




    def get_task_id(session, key: str) -> Optional[str]:
    def get_task_id(session, key: str) -> Optional[str]:
    """
    """
    Get a task ID from the session.
    Get a task ID from the session.


    Args:
    Args:
    session: Flask session object
    session: Flask session object
    key: Key the task ID is stored under
    key: Key the task ID is stored under


    Returns:
    Returns:
    Task ID if found, None otherwise
    Task ID if found, None otherwise
    """
    """
    if "tasks" not in session:
    if "tasks" not in session:
    return None
    return None


    return session["tasks"].get(key)
    return session["tasks"].get(key)




    def cancel_task(task_id: str) -> bool:
    def cancel_task(task_id: str) -> bool:
    """
    """
    Cancel a running task.
    Cancel a running task.


    Args:
    Args:
    task_id: ID of the task
    task_id: ID of the task


    Returns:
    Returns:
    True if the task was cancelled, False otherwise
    True if the task was cancelled, False otherwise
    """
    """
    task_result = AsyncResult(task_id, app=celery_app)
    task_result = AsyncResult(task_id, app=celery_app)


    if task_result.state in ["PENDING", "STARTED", "PROGRESS"]:
    if task_result.state in ["PENDING", "STARTED", "PROGRESS"]:
    task_result.revoke(terminate=True)
    task_result.revoke(terminate=True)
    logger.info(f"Task {task_id} cancelled")
    logger.info(f"Task {task_id} cancelled")
    return True
    return True
    else:
    else:
    logger.info(
    logger.info(
    f"Task {task_id} could not be cancelled (state: {task_result.state})"
    f"Task {task_id} could not be cancelled (state: {task_result.state})"
    )
    )
    return False
    return False