"""
"""
Event emitter service for the API server.
Event emitter service for the API server.


This service provides a centralized event emitter to trigger events across the application
This service provides a centralized event emitter to trigger events across the application
and send webhook notifications.
and send webhook notifications.
"""
"""


import asyncio
import asyncio
import logging
import logging
import time
import time
from functools import wraps
from functools import wraps
from typing import Any, Callable, Dict, List, Union
from typing import Any, Callable, Dict, List, Union


from ..config import WebhookEventType
from ..config import WebhookEventType
from .webhook_service import WebhookService
from .webhook_service import WebhookService


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




class EventEmitter:
    class EventEmitter:
    """
    """
    Service for emitting events throughout the application and triggering webhooks.
    Service for emitting events throughout the application and triggering webhooks.
    """
    """


    # Singleton instance
    # Singleton instance
    _instance = None
    _instance = None


    def __new__(cls):
    def __new__(cls):
    """Create a singleton instance."""
    if cls._instance is None:
    cls._instance = super(EventEmitter, cls).__new__(cls)
    cls._instance._initialized = False
    return cls._instance

    def __init__(self):
    """Initialize the event emitter."""
    if self._initialized:
    return # Initialize webhook service
    self.webhook_service = WebhookService()

    # Event listeners
    self.listeners: Dict[str, List[Callable]] = {}

    # Debug logging
    self.debug = False

    self._initialized = True

    def on(self, event: Union[str, WebhookEventType], listener: Callable) -> Callable:
    """
    """
    Register an event listener.
    Register an event listener.


    Args:
    Args:
    event: Event name
    event: Event name
    listener: Listener callback
    listener: Listener callback


    Returns:
    Returns:
    Unsubscribe function
    Unsubscribe function
    """
    """
    # Convert event type to string
    # Convert event type to string
    event_name = event.value if isinstance(event, WebhookEventType) else str(event)
    event_name = event.value if isinstance(event, WebhookEventType) else str(event)


    # Initialize event listeners if needed
    # Initialize event listeners if needed
    if event_name not in self.listeners:
    if event_name not in self.listeners:
    self.listeners[event_name] = []
    self.listeners[event_name] = []


    # Add listener
    # Add listener
    self.listeners[event_name].append(listener)
    self.listeners[event_name].append(listener)


    # Log registration
    # Log registration
    if self.debug:
    if self.debug:
    logger.debug(f"Added listener for event {event_name}")
    logger.debug(f"Added listener for event {event_name}")


    # Return unsubscribe function
    # Return unsubscribe function
    def unsubscribe() -> None:
    def unsubscribe() -> None:
    if listener in self.listeners.get(event_name, []):
    if listener in self.listeners.get(event_name, []):
    self.listeners[event_name].remove(listener)
    self.listeners[event_name].remove(listener)
    if self.debug:
    if self.debug:
    logger.debug(f"Removed listener for event {event_name}")
    logger.debug(f"Removed listener for event {event_name}")


    return unsubscribe
    return unsubscribe


    def once(self, event: Union[str, WebhookEventType], listener: Callable) -> Callable:
    def once(self, event: Union[str, WebhookEventType], listener: Callable) -> Callable:
    """
    """
    Register a one-time event listener.
    Register a one-time event listener.


    Args:
    Args:
    event: Event name
    event: Event name
    listener: Listener callback
    listener: Listener callback


    Returns:
    Returns:
    Unsubscribe function
    Unsubscribe function
    """
    """


    # Create wrapper that removes itself after first call
    # Create wrapper that removes itself after first call
    @wraps(listener)
    @wraps(listener)
    def wrapper(*args, **kwargs):
    def wrapper(*args, **kwargs):
    unsubscribe()
    unsubscribe()
    return listener(*args, **kwargs)
    return listener(*args, **kwargs)


    # Register wrapper
    # Register wrapper
    unsubscribe = self.on(event, wrapper)
    unsubscribe = self.on(event, wrapper)


    return unsubscribe
    return unsubscribe


    async def emit(
    async def emit(
    self, event: Union[str, WebhookEventType], data: Dict[str, Any]
    self, event: Union[str, WebhookEventType], data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit an event.
    Emit an event.


    Args:
    Args:
    event: Event name
    event: Event name
    data: Event data
    data: Event data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    # Convert event type to string
    # Convert event type to string
    event_name = event.value if isinstance(event, WebhookEventType) else str(event)
    event_name = event.value if isinstance(event, WebhookEventType) else str(event)


    # Check if event has listeners
    # Check if event has listeners
    listeners = self.listeners.get(event_name, [])
    listeners = self.listeners.get(event_name, [])


    # Log event
    # Log event
    log_level = logging.DEBUG if len(listeners) == 0 else logging.INFO
    log_level = logging.DEBUG if len(listeners) == 0 else logging.INFO
    if self.debug or log_level == logging.INFO:
    if self.debug or log_level == logging.INFO:
    logger.log(
    logger.log(
    log_level, f"Emitting event {event_name} to {len(listeners)} listeners"
    log_level, f"Emitting event {event_name} to {len(listeners)} listeners"
    )
    )


    # Notify listeners
    # Notify listeners
    for listener in listeners:
    for listener in listeners:
    try:
    try:
    # Call listener (which might be async or not)
    # Call listener (which might be async or not)
    result = listener(data)
    result = listener(data)


    # Handle async results
    # Handle async results
    if asyncio.iscoroutine(result):
    if asyncio.iscoroutine(result):
    await result
    await result
except Exception as e:
except Exception as e:
    logger.error(f"Error in listener for event {event_name}: {str(e)}")
    logger.error(f"Error in listener for event {event_name}: {str(e)}")


    # Trigger webhook notifications
    # Trigger webhook notifications
    await self.webhook_service.trigger_event(event_name, data)
    await self.webhook_service.trigger_event(event_name, data)


    return len(listeners)
    return len(listeners)


    # Convenience methods for common events
    # Convenience methods for common events


    async def emit_niche_analysis_created(
    async def emit_niche_analysis_created(
    self, analysis_id: str, analysis_data: Dict[str, Any]
    self, analysis_id: str, analysis_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit niche analysis created event.
    Emit niche analysis created event.


    Args:
    Args:
    analysis_id: Niche analysis ID
    analysis_id: Niche analysis ID
    analysis_data: Analysis data
    analysis_data: Analysis data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.NICHE_ANALYSIS_CREATED,
    WebhookEventType.NICHE_ANALYSIS_CREATED,
    {"analysis_id": analysis_id, "analysis": analysis_data},
    {"analysis_id": analysis_id, "analysis": analysis_data},
    )
    )


    async def emit_niche_analysis_updated(
    async def emit_niche_analysis_updated(
    self, analysis_id: str, analysis_data: Dict[str, Any]
    self, analysis_id: str, analysis_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit niche analysis updated event.
    Emit niche analysis updated event.


    Args:
    Args:
    analysis_id: Niche analysis ID
    analysis_id: Niche analysis ID
    analysis_data: Analysis data
    analysis_data: Analysis data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.NICHE_ANALYSIS_UPDATED,
    WebhookEventType.NICHE_ANALYSIS_UPDATED,
    {"analysis_id": analysis_id, "analysis": analysis_data},
    {"analysis_id": analysis_id, "analysis": analysis_data},
    )
    )


    async def emit_opportunity_scored(
    async def emit_opportunity_scored(
    self, opportunity_id: str, score: float, opportunity_data: Dict[str, Any]
    self, opportunity_id: str, score: float, opportunity_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit opportunity scored event.
    Emit opportunity scored event.


    Args:
    Args:
    opportunity_id: Opportunity ID
    opportunity_id: Opportunity ID
    score: Opportunity score
    score: Opportunity score
    opportunity_data: Opportunity data
    opportunity_data: Opportunity data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.OPPORTUNITY_SCORED,
    WebhookEventType.OPPORTUNITY_SCORED,
    {
    {
    "opportunity_id": opportunity_id,
    "opportunity_id": opportunity_id,
    "score": score,
    "score": score,
    "opportunity": opportunity_data,
    "opportunity": opportunity_data,
    },
    },
    )
    )


    async def emit_monetization_plan_created(
    async def emit_monetization_plan_created(
    self, plan_id: str, plan_data: Dict[str, Any]
    self, plan_id: str, plan_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit monetization plan created event.
    Emit monetization plan created event.


    Args:
    Args:
    plan_id: Plan ID
    plan_id: Plan ID
    plan_data: Plan data
    plan_data: Plan data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.MONETIZATION_PLAN_CREATED,
    WebhookEventType.MONETIZATION_PLAN_CREATED,
    {"plan_id": plan_id, "plan": plan_data},
    {"plan_id": plan_id, "plan": plan_data},
    )
    )


    async def emit_marketing_campaign_created(
    async def emit_marketing_campaign_created(
    self, campaign_id: str, campaign_data: Dict[str, Any]
    self, campaign_id: str, campaign_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit marketing campaign created event.
    Emit marketing campaign created event.


    Args:
    Args:
    campaign_id: Campaign ID
    campaign_id: Campaign ID
    campaign_data: Campaign data
    campaign_data: Campaign data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.MARKETING_CAMPAIGN_CREATED,
    WebhookEventType.MARKETING_CAMPAIGN_CREATED,
    {"campaign_id": campaign_id, "campaign": campaign_data},
    {"campaign_id": campaign_id, "campaign": campaign_data},
    )
    )


    async def emit_marketing_campaign_completed(
    async def emit_marketing_campaign_completed(
    self, campaign_id: str, results: Dict[str, Any], campaign_data: Dict[str, Any]
    self, campaign_id: str, results: Dict[str, Any], campaign_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit marketing campaign completed event.
    Emit marketing campaign completed event.


    Args:
    Args:
    campaign_id: Campaign ID
    campaign_id: Campaign ID
    results: Campaign results
    results: Campaign results
    campaign_data: Campaign data
    campaign_data: Campaign data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.MARKETING_CAMPAIGN_COMPLETED,
    WebhookEventType.MARKETING_CAMPAIGN_COMPLETED,
    {"campaign_id": campaign_id, "results": results, "campaign": campaign_data},
    {"campaign_id": campaign_id, "results": results, "campaign": campaign_data},
    )
    )


    async def emit_user_created(self, user_id: str, user_data: Dict[str, Any]) -> int:
    async def emit_user_created(self, user_id: str, user_data: Dict[str, Any]) -> int:
    """
    """
    Emit user created event.
    Emit user created event.


    Args:
    Args:
    user_id: User ID
    user_id: User ID
    user_data: User data
    user_data: User data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.USER_CREATED, {"user_id": user_id, "user": user_data}
    WebhookEventType.USER_CREATED, {"user_id": user_id, "user": user_data}
    )
    )


    async def emit_project_shared(
    async def emit_project_shared(
    self, project_id: str, shared_with: List[str], project_data: Dict[str, Any]
    self, project_id: str, shared_with: List[str], project_data: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit project shared event.
    Emit project shared event.


    Args:
    Args:
    project_id: Project ID
    project_id: Project ID
    shared_with: List of user IDs the project is shared with
    shared_with: List of user IDs the project is shared with
    project_data: Project data
    project_data: Project data


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.PROJECT_SHARED,
    WebhookEventType.PROJECT_SHARED,
    {
    {
    "project_id": project_id,
    "project_id": project_id,
    "shared_with": shared_with,
    "shared_with": shared_with,
    "project": project_data,
    "project": project_data,
    },
    },
    )
    )


    async def emit_agent_task_completed(
    async def emit_agent_task_completed(
    self, task_id: str, agent_id: str, results: Dict[str, Any]
    self, task_id: str, agent_id: str, results: Dict[str, Any]
    ) -> int:
    ) -> int:
    """
    """
    Emit agent task completed event.
    Emit agent task completed event.


    Args:
    Args:
    task_id: Task ID
    task_id: Task ID
    agent_id: Agent ID
    agent_id: Agent ID
    results: Task results
    results: Task results


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.AGENT_TASK_COMPLETED,
    WebhookEventType.AGENT_TASK_COMPLETED,
    {"task_id": task_id, "agent_id": agent_id, "results": results},
    {"task_id": task_id, "agent_id": agent_id, "results": results},
    )
    )


    async def emit_model_inference_completed(
    async def emit_model_inference_completed(
    self,
    self,
    model_id: str,
    model_id: str,
    inference_id: str,
    inference_id: str,
    results: Dict[str, Any],
    results: Dict[str, Any],
    stats: Dict[str, Any],
    stats: Dict[str, Any],
    ) -> int:
    ) -> int:
    """
    """
    Emit model inference completed event.
    Emit model inference completed event.


    Args:
    Args:
    model_id: Model ID
    model_id: Model ID
    inference_id: Inference ID
    inference_id: Inference ID
    results: Inference results
    results: Inference results
    stats: Performance statistics
    stats: Performance statistics


    Returns:
    Returns:
    Number of listeners notified
    Number of listeners notified
    """
    """
    return await self.emit(
    return await self.emit(
    WebhookEventType.MODEL_INFERENCE_COMPLETED,
    WebhookEventType.MODEL_INFERENCE_COMPLETED,
    {
    {
    "model_id": model_id,
    "model_id": model_id,
    "inference_id": inference_id,
    "inference_id": inference_id,
    "results": results,
    "results": results,
    "statistics": stats,
    "statistics": stats,
    },
    },
    )
    )