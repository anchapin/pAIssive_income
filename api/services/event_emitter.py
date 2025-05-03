"""
Event emitter service for the API server.

This service provides a centralized event emitter to trigger events across the application
and send webhook notifications.
"""

import time


import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Union

from ..config import WebhookEventType
from .webhook_service import WebhookService



# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EventEmitter:
    """
    Service for emitting events throughout the application and triggering webhooks.
    """

    # Singleton instance
    _instance = None

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
        Register an event listener.

        Args:
            event: Event name
            listener: Listener callback

        Returns:
            Unsubscribe function
        """
        # Convert event type to string
        event_name = event.value if isinstance(event, WebhookEventType) else str(event)

        # Initialize event listeners if needed
        if event_name not in self.listeners:
            self.listeners[event_name] = []

        # Add listener
        self.listeners[event_name].append(listener)

        # Log registration
        if self.debug:
            logger.debug(f"Added listener for event {event_name}")

        # Return unsubscribe function
        def unsubscribe() -> None:
            if listener in self.listeners.get(event_name, []):
                self.listeners[event_name].remove(listener)
                if self.debug:
                    logger.debug(f"Removed listener for event {event_name}")

                return unsubscribe

    def once(self, event: Union[str, WebhookEventType], listener: Callable) -> Callable:
        """
        Register a one-time event listener.

        Args:
            event: Event name
            listener: Listener callback

        Returns:
            Unsubscribe function
        """

        # Create wrapper that removes itself after first call
        @wraps(listener)
        def wrapper(*args, **kwargs):
            unsubscribe()
                    return listener(*args, **kwargs)

        # Register wrapper
        unsubscribe = self.on(event, wrapper)

                return unsubscribe

    async def emit(
        self, event: Union[str, WebhookEventType], data: Dict[str, Any]
    ) -> int:
        """
        Emit an event.

        Args:
            event: Event name
            data: Event data

        Returns:
            Number of listeners notified
        """
        # Convert event type to string
        event_name = event.value if isinstance(event, WebhookEventType) else str(event)

        # Check if event has listeners
        listeners = self.listeners.get(event_name, [])

        # Log event
        log_level = logging.DEBUG if len(listeners) == 0 else logging.INFO
        if self.debug or log_level == logging.INFO:
            logger.log(
                log_level, f"Emitting event {event_name} to {len(listeners)} listeners"
            )

        # Notify listeners
        for listener in listeners:
            try:
                # Call listener (which might be async or not)
                result = listener(data)

                # Handle async results
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in listener for event {event_name}: {str(e)}")

        # Trigger webhook notifications
        await self.webhook_service.trigger_event(event_name, data)

                return len(listeners)

    # Convenience methods for common events

    async def emit_niche_analysis_created(
        self, analysis_id: str, analysis_data: Dict[str, Any]
    ) -> int:
        """
        Emit niche analysis created event.

        Args:
            analysis_id: Niche analysis ID
            analysis_data: Analysis data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.NICHE_ANALYSIS_CREATED,
            {"analysis_id": analysis_id, "analysis": analysis_data},
        )

    async def emit_niche_analysis_updated(
        self, analysis_id: str, analysis_data: Dict[str, Any]
    ) -> int:
        """
        Emit niche analysis updated event.

        Args:
            analysis_id: Niche analysis ID
            analysis_data: Analysis data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.NICHE_ANALYSIS_UPDATED,
            {"analysis_id": analysis_id, "analysis": analysis_data},
        )

    async def emit_opportunity_scored(
        self, opportunity_id: str, score: float, opportunity_data: Dict[str, Any]
    ) -> int:
        """
        Emit opportunity scored event.

        Args:
            opportunity_id: Opportunity ID
            score: Opportunity score
            opportunity_data: Opportunity data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.OPPORTUNITY_SCORED,
            {
                "opportunity_id": opportunity_id,
                "score": score,
                "opportunity": opportunity_data,
            },
        )

    async def emit_monetization_plan_created(
        self, plan_id: str, plan_data: Dict[str, Any]
    ) -> int:
        """
        Emit monetization plan created event.

        Args:
            plan_id: Plan ID
            plan_data: Plan data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.MONETIZATION_PLAN_CREATED,
            {"plan_id": plan_id, "plan": plan_data},
        )

    async def emit_marketing_campaign_created(
        self, campaign_id: str, campaign_data: Dict[str, Any]
    ) -> int:
        """
        Emit marketing campaign created event.

        Args:
            campaign_id: Campaign ID
            campaign_data: Campaign data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.MARKETING_CAMPAIGN_CREATED,
            {"campaign_id": campaign_id, "campaign": campaign_data},
        )

    async def emit_marketing_campaign_completed(
        self, campaign_id: str, results: Dict[str, Any], campaign_data: Dict[str, Any]
    ) -> int:
        """
        Emit marketing campaign completed event.

        Args:
            campaign_id: Campaign ID
            results: Campaign results
            campaign_data: Campaign data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.MARKETING_CAMPAIGN_COMPLETED,
            {"campaign_id": campaign_id, "results": results, "campaign": campaign_data},
        )

    async def emit_user_created(self, user_id: str, user_data: Dict[str, Any]) -> int:
        """
        Emit user created event.

        Args:
            user_id: User ID
            user_data: User data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.USER_CREATED, {"user_id": user_id, "user": user_data}
        )

    async def emit_project_shared(
        self, project_id: str, shared_with: List[str], project_data: Dict[str, Any]
    ) -> int:
        """
        Emit project shared event.

        Args:
            project_id: Project ID
            shared_with: List of user IDs the project is shared with
            project_data: Project data

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.PROJECT_SHARED,
            {
                "project_id": project_id,
                "shared_with": shared_with,
                "project": project_data,
            },
        )

    async def emit_agent_task_completed(
        self, task_id: str, agent_id: str, results: Dict[str, Any]
    ) -> int:
        """
        Emit agent task completed event.

        Args:
            task_id: Task ID
            agent_id: Agent ID
            results: Task results

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.AGENT_TASK_COMPLETED,
            {"task_id": task_id, "agent_id": agent_id, "results": results},
        )

    async def emit_model_inference_completed(
        self,
        model_id: str,
        inference_id: str,
        results: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> int:
        """
        Emit model inference completed event.

        Args:
            model_id: Model ID
            inference_id: Inference ID
            results: Inference results
            stats: Performance statistics

        Returns:
            Number of listeners notified
        """
                return await self.emit(
            WebhookEventType.MODEL_INFERENCE_COMPLETED,
            {
                "model_id": model_id,
                "inference_id": inference_id,
                "results": results,
                "statistics": stats,
            },
        )