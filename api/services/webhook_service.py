"""
Webhook service for the API server.

This module provides services for webhook management and delivery.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from .audit_service import AuditService
from .metrics import (
    track_queue_latency,
    track_webhook_delivery,
    track_webhook_error,
    track_webhook_retry,
    update_queue_size,
    update_webhook_health,
)
from .webhook_security import WebhookSignatureVerifier

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookService:
    """
    Service for webhook management and delivery.
    """

    def __init__(self, audit_service: Optional[AuditService] = None):
        """
        Initialize the webhook service.

        Args:
            audit_service: Audit service for recording events
        """
        self.webhooks = {}
        self.deliveries = {}
        self.running = False
        self.delivery_queue = asyncio.Queue()
        self.worker_task = None
        self.audit_service = audit_service or AuditService()

    async def deliver_event(
        self, webhook_id: str, event_type: str, event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deliver an event to a specific webhook immediately.

        Args:
            webhook_id: ID of the webhook to deliver to
            event_type: Type of event to deliver
            event_data: Event data to deliver

        Returns:
            Delivery result

        Raises:
            ValueError: If webhook is not found, inactive, or not subscribed to event type
        """
        # Get webhook
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook not found: {webhook_id}")

        # Check if webhook is active
        if not webhook["is_active"]:
            raise ValueError(f"Webhook is not active: {webhook_id}")

        # Check if webhook is subscribed to this event type
        if event_type not in webhook["events"]:
            raise ValueError(
                f"Webhook {webhook_id} is not subscribed to event type: {event_type}"
            )

        # Create delivery record
        delivery_id = str(uuid.uuid4())
        delivery = {
            "id": delivery_id,
            "webhook_id": webhook_id,
            "event_type": event_type,
            "event_data": event_data,
            "status": "pending",
            "attempts": 0,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Store delivery
        self.deliveries[delivery_id] = delivery

        # Deliver webhook directly
        await self._deliver_webhook(webhook, delivery)

        return delivery

    async def start(self):
        """
        Start the webhook service.
        """
        if self.running:
            return

        self.running = True
        self.worker_task = asyncio.create_task(self._delivery_worker())
        logger.info("Webhook service started")

    async def stop(self):
        """
        Stop the webhook service.
        """
        if not self.running:
            return

        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Webhook service stopped")

    async def register_webhook(
        self,
        data: Dict[str, Any],
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new webhook.

        Args:
            data: Webhook data
            actor_id: ID of the actor registering the webhook
            ip_address: IP address of the actor
            user_agent: User agent of the actor

        Returns:
            Registered webhook
        """
        webhook_id = str(uuid.uuid4())
        webhook = {
            "id": webhook_id,
            "url": data["url"],
            "events": data["events"],
            "description": data.get("description"),
            "headers": data.get("headers", {}),
            "is_active": data.get("is_active", True),
            "created_at": datetime.utcnow().isoformat(),
            "last_called_at": None,
            "secret": f"whsec_{uuid.uuid4().hex}",
        }

        self.webhooks[webhook_id] = webhook
        logger.info(f"Webhook registered: {webhook_id}")

        # Record audit event
        self.audit_service.create_event(
            event_type="webhook.created",
            resource_type="webhook",
            action="create",
            resource_id=webhook_id,
            actor_id=actor_id,
            actor_type="user" if actor_id else "system",
            status="success",
            details={
                "url": data["url"],
                "events": data["events"],
                "description": data.get("description"),
                "is_active": data.get("is_active", True),
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return webhook

    async def list_webhooks(self) -> List[Dict[str, Any]]:
        """
        List all webhooks.

        Returns:
            List of webhooks
        """
        return list(self.webhooks.values())

    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a webhook by ID.

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhook if found, None otherwise
        """
        return self.webhooks.get(webhook_id)

    async def update_webhook(
        self,
        webhook_id: str,
        data: Dict[str, Any],
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a webhook.

        Args:
            webhook_id: Webhook ID
            data: Updated webhook data
            actor_id: ID of the actor updating the webhook
            ip_address: IP address of the actor
            user_agent: User agent of the actor

        Returns:
            Updated webhook if found, None otherwise
        """
        webhook = self.webhooks.get(webhook_id)

        if not webhook:
            return None

        # Store original values for audit
        original_values = {
            "url": webhook["url"],
            "events": webhook["events"],
            "description": webhook.get("description"),
            "headers": webhook.get("headers", {}),
            "is_active": webhook.get("is_active", True),
        }

        # Update webhook fields
        if "url" in data:
            webhook["url"] = data["url"]
        if "events" in data:
            webhook["events"] = data["events"]
        if "description" in data:
            webhook["description"] = data["description"]
        if "headers" in data:
            webhook["headers"] = data["headers"]
        if "is_active" in data:
            webhook["is_active"] = data["is_active"]

        logger.info(f"Webhook updated: {webhook_id}")

        # Record audit event
        self.audit_service.create_event(
            event_type="webhook.updated",
            resource_type="webhook",
            action="update",
            resource_id=webhook_id,
            actor_id=actor_id,
            actor_type="user" if actor_id else "system",
            status="success",
            details={
                "original": original_values,
                "updated": {
                    "url": webhook["url"],
                    "events": webhook["events"],
                    "description": webhook.get("description"),
                    "headers": webhook.get("headers", {}),
                    "is_active": webhook.get("is_active", True),
                },
                "changes": {
                    k: data[k]
                    for k in data
                    if k in original_values and data[k] != original_values[k]
                },
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return webhook

    async def delete_webhook(
        self,
        webhook_id: str,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """
        Delete a webhook.

        Args:
            webhook_id: Webhook ID
            actor_id: ID of the actor deleting the webhook
            ip_address: IP address of the actor
            user_agent: User agent of the actor

        Returns:
            True if the webhook was deleted, False otherwise
        """
        if webhook_id not in self.webhooks:
            return False

        # Store webhook data for audit
        webhook_data = self.webhooks[webhook_id].copy()

        # Delete webhook
        del self.webhooks[webhook_id]
        logger.info(f"Webhook deleted: {webhook_id}")

        # Record audit event
        self.audit_service.create_event(
            event_type="webhook.deleted",
            resource_type="webhook",
            action="delete",
            resource_id=webhook_id,
            actor_id=actor_id,
            actor_type="user" if actor_id else "system",
            status="success",
            details={
                "url": webhook_data["url"],
                "events": webhook_data["events"],
                "description": webhook_data.get("description"),
                "is_active": webhook_data.get("is_active", True),
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return True

    async def trigger_event(
        self, event_type: str, event_data: Dict[str, Any]
    ) -> List[str]:
        """
        Trigger an event and deliver it to subscribed webhooks.

        Args:
            event_type: Type of event
            event_data: Event data

        Returns:
            List of delivery IDs
        """
        delivery_ids = []

        # Find webhooks subscribed to this event type
        for webhook in self.webhooks.values():
            if not webhook["is_active"]:
                continue

            if event_type in webhook["events"]:
                # Create delivery
                delivery_id = str(uuid.uuid4())
                delivery = {
                    "id": delivery_id,
                    "webhook_id": webhook["id"],
                    "event_type": event_type,
                    "event_data": event_data,
                    "status": "pending",
                    "attempts": 0,
                    "max_attempts": 5,
                    "created_at": datetime.utcnow().isoformat(),
                    "next_attempt_at": datetime.utcnow().isoformat(),
                }

                self.deliveries[delivery_id] = delivery
                delivery_ids.append(delivery_id)

                # Queue delivery
                await self.delivery_queue.put(delivery_id)
                logger.info(
                    f"Event queued for delivery: {event_type} to webhook {webhook['id']}"
                )

        return delivery_ids

    async def get_deliveries(
        self, webhook_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get webhook deliveries.

        Args:
            webhook_id: Filter by webhook ID
            status: Filter by status

        Returns:
            List of deliveries
        """
        deliveries = list(self.deliveries.values())

        # Filter by webhook ID
        if webhook_id:
            deliveries = [d for d in deliveries if d["webhook_id"] == webhook_id]

        # Filter by status
        if status:
            deliveries = [d for d in deliveries if d["status"] == status]

        return deliveries

    async def _delivery_worker(self):
        """
        Worker for delivering webhooks.
        """
        while self.running:
            try:
                # Get delivery from queue
                delivery_id = await self.delivery_queue.get()
                delivery = self.deliveries.get(delivery_id)

                if not delivery:
                    self.delivery_queue.task_done()
                    continue

                # Get webhook
                webhook = self.webhooks.get(delivery["webhook_id"])

                if not webhook or not webhook["is_active"]:
                    self.delivery_queue.task_done()
                    continue

                # Deliver webhook
                success = await self._deliver_webhook(webhook, delivery)

                if not success and delivery["attempts"] < delivery["max_attempts"]:
                    # Track retry attempt
                    track_webhook_retry(
                        webhook_id=webhook["id"], event_type=delivery["event_type"]
                    )

                    # Calculate next attempt time (exponential backoff)
                    backoff = min(2 ** delivery["attempts"], 60)  # Max 60 minutes
                    next_attempt = datetime.utcnow().timestamp() + backoff * 60
                    delivery["next_attempt_at"] = datetime.fromtimestamp(
                        next_attempt
                    ).isoformat()

                    # Record retry audit event
                    self.audit_service.create_event(
                        event_type="webhook.delivery.retried",
                        resource_type="webhook_delivery",
                        action="retry",
                        resource_id=delivery_id,
                        actor_id=None,
                        actor_type="system",
                        status="info",
                        details={
                            "webhook_id": webhook["id"],
                            "event_type": delivery["event_type"],
                            "attempt": delivery["attempts"],
                            "max_attempts": delivery["max_attempts"],
                            "next_attempt_at": delivery["next_attempt_at"],
                        },
                    )

                    # Requeue for later
                    await asyncio.sleep(1)  # Small delay to avoid tight loop
                    await self.delivery_queue.put(delivery_id)
                elif not success:
                    # Track max retries exceeded
                    delivery["status"] = "max_retries_exceeded"
                    track_webhook_error(
                        webhook_id=webhook["id"],
                        event_type=delivery["event_type"],
                        error_type="max_retries_exceeded",
                    )

                self.delivery_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in delivery worker: {str(e)}")
                await asyncio.sleep(1)  # Small delay to avoid tight loop

    async def _deliver_webhook(
        self, webhook: Dict[str, Any], delivery: Dict[str, Any]
    ) -> bool:
        """
        Deliver a webhook.

        Args:
            webhook: Webhook to deliver
            delivery: Delivery information

        Returns:
            True if delivery was successful, False otherwise
        """
        start_time = datetime.utcnow().timestamp()

        # Increment attempt counter
        delivery["attempts"] += 1
        delivery["status"] = "retrying" if delivery["attempts"] > 1 else "pending"

        # Update queue size metric
        update_queue_size(self.delivery_queue.qsize())

        # Track queue latency
        queued_time = (
            start_time - datetime.fromisoformat(delivery["created_at"]).timestamp()
        )
        track_queue_latency(queued_time)

        # Prepare payload
        payload = {
            "id": delivery["id"],
            "type": delivery["event_type"],
            "created_at": delivery["created_at"],
            "data": delivery["event_data"],
        }

        # Convert payload to JSON
        payload_json = json.dumps(payload)

        # Generate signature
        signature = WebhookSignatureVerifier.create_signature(
            webhook["secret"], payload_json
        )

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "pAIssive-Income-Webhook/1.0",
            "X-Webhook-ID": webhook["id"],
            "X-Webhook-Signature": signature,
        }

        # Add custom headers
        if webhook.get("headers"):
            headers.update(webhook["headers"])

        try:
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook["url"], data=payload_json, headers=headers, timeout=10
                ) as response:
                    # Get response
                    status_code = response.status
                    response_body = await response.text()

                    # Calculate delivery duration
                    duration = datetime.utcnow().timestamp() - start_time

                    # Update delivery record
                    delivery["response_code"] = status_code
                    delivery["response_body"] = response_body

                    # Check if successful
                    if 200 <= status_code < 300:
                        delivery["status"] = "success"
                        webhook["last_called_at"] = datetime.utcnow().isoformat()

                        # Track successful delivery
                        track_webhook_delivery(
                            webhook_id=webhook["id"],
                            event_type=delivery["event_type"],
                            duration=duration,
                            status="success",
                        )

                        # Update health status
                        update_webhook_health(webhook["id"], webhook["url"], True)

                        logger.info(
                            f"Webhook delivered successfully: {delivery['id']} to {webhook['url']}"
                        )

                        # Record success audit event
                        self.audit_service.create_event(
                            event_type="webhook.delivery.sent",
                            resource_type="webhook_delivery",
                            action="send",
                            resource_id=delivery["id"],
                            actor_id=None,
                            actor_type="system",
                            status="success",
                            details={
                                "webhook_id": webhook["id"],
                                "event_type": delivery["event_type"],
                                "url": webhook["url"],
                                "response_code": status_code,
                                "attempt": delivery["attempts"],
                            },
                        )

                        return True
                    else:
                        delivery["status"] = "failed"
                        logger.warning(
                            f"Webhook delivery failed with status {status_code}: {delivery['id']} to {webhook['url']}"
                        )

                        # Track failed delivery
                        track_webhook_delivery(
                            webhook_id=webhook["id"],
                            event_type=delivery["event_type"],
                            duration=duration,
                            status="failed",
                        )

                        # Update health status
                        update_webhook_health(webhook["id"], webhook["url"], False)

                        # Track error
                        track_webhook_error(
                            webhook_id=webhook["id"],
                            event_type=delivery["event_type"],
                            error_type=f"http_{status_code}",
                        )

                        # Record failure audit event
                        self.audit_service.create_event(
                            event_type="webhook.delivery.failed",
                            resource_type="webhook_delivery",
                            action="send",
                            resource_id=delivery["id"],
                            actor_id=None,
                            actor_type="system",
                            status="failure",
                            details={
                                "webhook_id": webhook["id"],
                                "event_type": delivery["event_type"],
                                "url": webhook["url"],
                                "response_code": status_code,
                                "response_body": response_body,
                                "attempt": delivery["attempts"],
                                "max_attempts": delivery["max_attempts"],
                            },
                        )

                        return False

        except Exception as e:
            # Update delivery
            delivery["status"] = "failed"
            delivery["error"] = str(e)

            # Track failed delivery
            duration = datetime.utcnow().timestamp() - start_time
            track_webhook_delivery(
                webhook_id=webhook["id"],
                event_type=delivery["event_type"],
                duration=duration,
                status="failed",
            )

            # Update health status
            update_webhook_health(webhook["id"], webhook["url"], False)

            # Track error
            track_webhook_error(
                webhook_id=webhook["id"],
                event_type=delivery["event_type"],
                error_type="connection_error",
            )

            logger.warning(f"Webhook delivery failed with error: {str(e)}")

            # Record error audit event
            self.audit_service.create_event(
                event_type="webhook.delivery.failed",
                resource_type="webhook_delivery",
                action="send",
                resource_id=delivery["id"],
                actor_id=None,
                actor_type="system",
                status="failure",
                details={
                    "webhook_id": webhook["id"],
                    "event_type": delivery["event_type"],
                    "url": webhook["url"],
                    "error": str(e),
                    "attempt": delivery["attempts"],
                    "max_attempts": delivery["max_attempts"],
                },
            )

            return False