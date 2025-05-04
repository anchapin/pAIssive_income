"""
"""
Celery configuration for the pAIssive Income UI.
Celery configuration for the pAIssive Income UI.


This module sets up Celery for background task processing.
This module sets up Celery for background task processing.
"""
"""


import logging
import logging
import os
import os
import time
import time


from celery import Celery
from celery import Celery


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




def create_celery_app(app=None):
    def create_celery_app(app=None):
    """Create and configure Celery application."""

    # Initialize Celery
    celery = Celery(
    "paissive_income",
    broker="pyamqp://guest@localhost//",  # Default RabbitMQ broker URL
    backend="rpc://",  # Use RPC for result backend
    include=["ui.tasks"],  # Include task modules
    )

    # Update broker URL from environment variable if available
    celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", celery.conf.broker_url)

    # Load additional configuration from environment
    celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour time limit for tasks
    worker_concurrency=os.environ.get("CELERY_CONCURRENCY", 2),
    )

    class ContextTask(celery.Task):

    def __call__(self, *args, **kwargs):
    """Execute task with app context."""
    if app is not None:
    with app.app_context():
    return self.run(*args, **kwargs)
    return self.run(*args, **kwargs)

    celery.Task = ContextTask

    logger.info("Celery app configured")
    return celery


    # Create default Celery app without Flask context
    celery_app = create_celery_app()