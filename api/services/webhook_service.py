"""
Webhook service for the API server.

This service manages webhooks, including registration, delivery, and event handling.
"""

import os
import uuid
import json
import time
import hmac
import hashlib
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime, timezone
import aiohttp

from ..schemas.webhook import WebhookEventType, WebhookDeliveryStatus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebhookService:
    """
    Service for managing webhooks and sending webhook events.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(WebhookService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the webhook service."""
        if self._initialized:
            return
            
        # In-memory storage (would be replaced with a database in production)
        self.webhooks = {}  # webhook_id -> webhook
        self.deliveries = {}  # delivery_id -> delivery
        self.webhook_events = {}  # event_type -> set of webhook_ids
        
        # Delivery queue
        self.delivery_queue = asyncio.Queue()
        self.worker_task = None
        
        # Configuration
        self.max_retries = 5
        self.retry_delays = [30, 60, 300, 600, 1800]  # in seconds
        self.request_timeout = 10  # in seconds
        
        # Start delivery worker
        self._start_delivery_worker()
        
        self._initialized = True
    
    def _start_delivery_worker(self) -> None:
        """Start the delivery worker task."""
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._delivery_worker())
    
    async def _delivery_worker(self) -> None:
        """Worker task for processing webhook deliveries."""
        while True:
            try:
                # Get delivery from queue
                delivery_id, webhook_id, payload, attempt = await self.delivery_queue.get()
                
                try:
                    # Get webhook
                    webhook = self.webhooks.get(webhook_id)
                    if not webhook:
                        logger.error(f"Webhook {webhook_id} not found for delivery {delivery_id}")
                        continue
                    
                    # Skip if webhook is not active
                    if not webhook["active"]:
                        logger.info(f"Skipping delivery to inactive webhook {webhook_id}")
                        continue
                    
                    # Attempt delivery
                    await self._deliver_webhook(delivery_id, webhook, payload, attempt)
                    
                finally:
                    # Mark task as done
                    self.delivery_queue.task_done()
                    
            except asyncio.CancelledError:
                # Task was cancelled
                break
                
            except Exception as e:
                logger.error(f"Error in webhook delivery worker: {e}")
                # Continue processing other deliveries
    
    async def _deliver_webhook(
        self, 
        delivery_id: str, 
        webhook: Dict[str, Any], 
        payload: Dict[str, Any],
        attempt: int
    ) -> None:
        """
        Deliver a webhook to its destination.
        
        Args:
            delivery_id: Delivery ID
            webhook: Webhook to deliver to
            payload: Data to deliver
            attempt: Attempt number (starting from 1)
        """
        # Get delivery or create a new one
        delivery = self.deliveries.get(delivery_id)
        if not delivery:
            event_type = payload.get("event")
            delivery = {
                "id": delivery_id,
                "webhook_id": webhook["id"],
                "event_type": event_type,
                "status": WebhookDeliveryStatus.PENDING,
                "timestamp": self._get_iso_timestamp(),
                "attempts": []
            }
            self.deliveries[delivery_id] = delivery
        
        # Create attempt data
        attempt_id = f"{delivery_id}_attempt_{attempt}"
        attempt_data = {
            "id": attempt_id,
            "webhook_id": webhook["id"],
            "delivery_id": delivery_id,
            "event_type": payload.get("event"),
            "status": WebhookDeliveryStatus.PENDING,
            "timestamp": self._get_iso_timestamp(),
            "request_data": payload,
            "response_code": None,
            "response_body": None,
            "error_message": None
        }
        
        # Add attempt to delivery
        delivery["attempts"].append(attempt_data)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "pAIssive-Income-Webhooks/1.0",
            "X-Webhook-ID": webhook["id"],
            "X-Webhook-Event": payload.get("event", "unknown"),
            "X-Webhook-Delivery": delivery_id,
            "X-Webhook-Attempt": str(attempt)
        }
        
        # Add signature if secret is set
        if webhook.get("secret"):
            signature = self._generate_signature(webhook["secret"], payload)
            headers["X-Webhook-Signature"] = signature
        
        # Update status
        delivery["status"] = WebhookDeliveryStatus.RETRYING if attempt > 1 else WebhookDeliveryStatus.PENDING
        attempt_data["status"] = delivery["status"]
        
        # Deliver webhook
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    # Send request
                    start_time = time.time()
                    async with session.post(
                        webhook["url"],
                        json=payload,
                        headers=headers,
                        timeout=self.request_timeout
                    ) as response:
                        # Get response
                        response_code = response.status
                        response_time = time.time() - start_time
                        response_body = await response.text()
                        
                        # Update attempt data
                        attempt_data["response_code"] = response_code
                        attempt_data["response_body"] = response_body
                        
                        # Check if successful
                        if 200 <= response_code < 300:
                            # Success
                            delivery["status"] = WebhookDeliveryStatus.SUCCESS
                            attempt_data["status"] = WebhookDeliveryStatus.SUCCESS
                            logger.info(
                                f"Webhook {webhook['id']} delivered successfully "
                                f"(delivery={delivery_id}, attempt={attempt}, time={response_time:.2f}s)"
                            )
                        else:
                            # Failed with HTTP error
                            error_message = f"HTTP error {response_code}: {response_body}"
                            attempt_data["error_message"] = error_message
                            await self._handle_delivery_failure(
                                delivery, 
                                attempt_data,
                                webhook, 
                                payload, 
                                attempt, 
                                error_message
                            )
                
                except asyncio.TimeoutError:
                    # Request timed out
                    error_message = f"Request timed out after {self.request_timeout} seconds"
                    attempt_data["error_message"] = error_message
                    await self._handle_delivery_failure(
                        delivery, 
                        attempt_data, 
                        webhook, 
                        payload, 
                        attempt, 
                        error_message
                    )
                
                except aiohttp.ClientError as e:
                    # Client error
                    error_message = f"Request error: {str(e)}"
                    attempt_data["error_message"] = error_message
                    await self._handle_delivery_failure(
                        delivery, 
                        attempt_data, 
                        webhook, 
                        payload, 
                        attempt, 
                        error_message
                    )
        
        except Exception as e:
            # Unexpected error
            error_message = f"Unexpected error: {str(e)}"
            attempt_data["error_message"] = error_message
            await self._handle_delivery_failure(
                delivery, 
                attempt_data, 
                webhook, 
                payload, 
                attempt, 
                error_message
            )
    
    async def _handle_delivery_failure(
        self,
        delivery: Dict[str, Any],
        attempt_data: Dict[str, Any],
        webhook: Dict[str, Any],
        payload: Dict[str, Any],
        attempt: int,
        error_message: str
    ) -> None:
        """
        Handle webhook delivery failure.
        
        Args:
            delivery: Delivery data
            attempt_data: Attempt data
            webhook: Webhook data
            payload: Payload data
            attempt: Attempt number
            error_message: Error message
        """
        # Log error
        logger.error(
            f"Webhook {webhook['id']} delivery failed "
            f"(delivery={delivery['id']}, attempt={attempt}): {error_message}"
        )
        
        # Check if we should retry
        if attempt < self.max_retries:
            # Schedule retry
            retry_delay = self.retry_delays[min(attempt - 1, len(self.retry_delays) - 1)]
            
            logger.info(
                f"Retrying webhook {webhook['id']} delivery "
                f"in {retry_delay} seconds "
                f"(delivery={delivery['id']}, attempt={attempt + 1}/{self.max_retries})"
            )
            
            # Update delivery status
            delivery["status"] = WebhookDeliveryStatus.RETRYING
            attempt_data["status"] = WebhookDeliveryStatus.RETRYING
            
            # Schedule retry
            asyncio.create_task(self._schedule_retry(
                delivery["id"],
                webhook["id"],
                payload,
                attempt + 1,
                retry_delay
            ))
            
        else:
            # Max retries reached
            logger.warning(
                f"Webhook {webhook['id']} delivery failed after {attempt} attempts "
                f"(delivery={delivery['id']})"
            )
            
            # Update delivery status
            delivery["status"] = WebhookDeliveryStatus.FAILED
            attempt_data["status"] = WebhookDeliveryStatus.FAILED
    
    async def _schedule_retry(
        self,
        delivery_id: str,
        webhook_id: str,
        payload: Dict[str, Any],
        attempt: int,
        delay: int
    ) -> None:
        """
        Schedule a webhook delivery retry.
        
        Args:
            delivery_id: Delivery ID
            webhook_id: Webhook ID
            payload: Payload to deliver
            attempt: Attempt number
            delay: Delay in seconds
        """
        await asyncio.sleep(delay)
        await self.delivery_queue.put((delivery_id, webhook_id, payload, attempt))
    
    def _generate_signature(self, secret: str, payload: Dict[str, Any]) -> str:
        """
        Generate a signature for a webhook payload.
        
        Args:
            secret: Webhook secret
            payload: Payload to sign
            
        Returns:
            HMAC signature
        """
        payload_str = json.dumps(payload, separators=(',', ':'))
        return hmac.new(
            secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_iso_timestamp(self) -> str:
        """
        Get current ISO 8601 timestamp.
        
        Returns:
            ISO 8601 timestamp
        """
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    
    def _generate_id(self, prefix: str = '') -> str:
        """
        Generate a unique ID.
        
        Args:
            prefix: Optional ID prefix
            
        Returns:
            Unique ID
        """
        return f"{prefix}{str(uuid.uuid4())}"
    
    async def register_webhook(
        self,
        url: str,
        events: List[Union[str, WebhookEventType]],
        description: Optional[str] = None,
        active: bool = True,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new webhook.
        
        Args:
            url: Webhook URL
            events: List of event types
            description: Optional webhook description
            active: Whether the webhook is active
            secret: Optional secret for signing payloads
            
        Returns:
            Registered webhook
        """
        # Generate a unique webhook ID
        webhook_id = self._generate_id('whk_')
        
        # Convert event types to strings
        event_strings = [e.value if isinstance(e, WebhookEventType) else str(e) for e in events]
        
        # Create webhook
        created_at = self._get_iso_timestamp()
        webhook = {
            "id": webhook_id,
            "url": str(url),
            "events": event_strings,
            "description": description,
            "active": active,
            "created_at": created_at,
            "updated_at": None,
            "secret": secret
        }
        
        # Save webhook
        self.webhooks[webhook_id] = webhook
        
        # Register webhook for events
        for event in event_strings:
            if event not in self.webhook_events:
                self.webhook_events[event] = set()
            self.webhook_events[event].add(webhook_id)
        
        # Return webhook (without secret)
        return {
            "id": webhook_id,
            "url": str(url),
            "events": event_strings,
            "description": description,
            "active": active,
            "created_at": created_at,
            "updated_at": None,
            "secret_set": secret is not None
        }
    
    async def update_webhook(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[Union[str, WebhookEventType]]] = None,
        description: Optional[str] = None,
        active: Optional[bool] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing webhook.
        
        Args:
            webhook_id: Webhook ID
            url: Updated webhook URL
            events: Updated list of event types
            description: Updated webhook description
            active: Updated webhook status
            secret: Updated webhook secret
            
        Returns:
            Updated webhook
        
        Raises:
            ValueError: If the webhook doesn't exist
        """
        # Get webhook
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook {webhook_id} not found")
        
        # Update webhook URL
        if url is not None:
            webhook["url"] = str(url)
        
        # Update webhook description
        if description is not None:
            webhook["description"] = description
        
        # Update webhook status
        if active is not None:
            webhook["active"] = active
        
        # Update webhook secret
        if secret is not None:
            webhook["secret"] = secret
        
        # Update event types
        if events is not None:
            # Convert event types to strings
            event_strings = [e.value if isinstance(e, WebhookEventType) else str(e) for e in events]
            
            # Remove webhook from old events
            for event in webhook["events"]:
                if event in self.webhook_events and webhook_id in self.webhook_events[event]:
                    self.webhook_events[event].remove(webhook_id)
                    if not self.webhook_events[event]:
                        del self.webhook_events[event]
            
            # Update webhook events
            webhook["events"] = event_strings
            
            # Register webhook for new events
            for event in event_strings:
                if event not in self.webhook_events:
                    self.webhook_events[event] = set()
                self.webhook_events[event].add(webhook_id)
        
        # Update timestamp
        webhook["updated_at"] = self._get_iso_timestamp()
        
        # Return webhook (without secret)
        return {
            "id": webhook_id,
            "url": webhook["url"],
            "events": webhook["events"],
            "description": webhook["description"],
            "active": webhook["active"],
            "created_at": webhook["created_at"],
            "updated_at": webhook["updated_at"],
            "secret_set": webhook["secret"] is not None
        }
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            True if the webhook was deleted, False if it didn't exist
        """
        # Get webhook
        webhook = self.webhooks.pop(webhook_id, None)
        if not webhook:
            return False
        
        # Remove webhook from events
        for event in webhook["events"]:
            if event in self.webhook_events and webhook_id in self.webhook_events[event]:
                self.webhook_events[event].remove(webhook_id)
                if not self.webhook_events[event]:
                    del self.webhook_events[event]
        
        return True
    
    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            Webhook or None if it doesn't exist
        """
        # Get webhook
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            return None
        
        # Return webhook (without secret)
        return {
            "id": webhook_id,
            "url": webhook["url"],
            "events": webhook["events"],
            "description": webhook["description"],
            "active": webhook["active"],
            "created_at": webhook["created_at"],
            "updated_at": webhook["updated_at"],
            "secret_set": webhook["secret"] is not None
        }
    
    async def get_webhooks(self) -> List[Dict[str, Any]]:
        """
        Get all webhooks.
        
        Returns:
            List of webhooks
        """
        # Return webhooks (without secrets)
        return [
            {
                "id": webhook_id,
                "url": webhook["url"],
                "events": webhook["events"],
                "description": webhook["description"],
                "active": webhook["active"],
                "created_at": webhook["created_at"],
                "updated_at": webhook["updated_at"],
                "secret_set": webhook["secret"] is not None
            }
            for webhook_id, webhook in self.webhooks.items()
        ]
    
    async def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a webhook delivery.
        
        Args:
            delivery_id: Delivery ID
            
        Returns:
            Delivery or None if it doesn't exist
        """
        return self.deliveries.get(delivery_id)
    
    async def get_deliveries(
        self,
        webhook_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        status: Optional[WebhookDeliveryStatus] = None
    ) -> Dict[str, Any]:
        """
        Get webhook deliveries.
        
        Args:
            webhook_id: Optional webhook ID filter
            page: Page number
            page_size: Items per page
            status: Optional status filter
            
        Returns:
            Deliveries and pagination info
        """
        # Filter deliveries
        filtered_deliveries = []
        for delivery in self.deliveries.values():
            # Apply webhook filter
            if webhook_id and delivery["webhook_id"] != webhook_id:
                continue
            
            # Apply status filter
            if status and delivery["status"] != status:
                continue
            
            filtered_deliveries.append(delivery)
        
        # Sort deliveries by timestamp descending
        filtered_deliveries.sort(key=lambda d: d["timestamp"], reverse=True)
        
        # Apply pagination
        total = len(filtered_deliveries)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            "deliveries": filtered_deliveries[start_idx:end_idx],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def retry_delivery(self, delivery_id: str) -> Dict[str, Any]:
        """
        Retry a failed webhook delivery.
        
        Args:
            delivery_id: Delivery ID
            
        Returns:
            Updated delivery
            
        Raises:
            ValueError: If the delivery doesn't exist or can't be retried
        """
        # Get delivery
        delivery = self.deliveries.get(delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        # Check if delivery can be retried
        if delivery["status"] not in [WebhookDeliveryStatus.FAILED]:
            raise ValueError(f"Delivery {delivery_id} cannot be retried (status: {delivery['status']})")
        
        # Get webhook
        webhook_id = delivery["webhook_id"]
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook {webhook_id} not found for delivery {delivery_id}")
        
        # Get last attempt
        if not delivery["attempts"]:
            raise ValueError(f"Delivery {delivery_id} has no attempts")
        
        last_attempt = delivery["attempts"][-1]
        
        # Schedule retry
        delivery["status"] = WebhookDeliveryStatus.RETRYING
        await self.delivery_queue.put((
            delivery_id, 
            webhook_id, 
            last_attempt["request_data"], 
            len(delivery["attempts"]) + 1
        ))
        
        return delivery
    
    async def trigger_event(
        self,
        event_type: Union[str, WebhookEventType],
        data: Dict[str, Any]
    ) -> int:
        """
        Trigger a webhook event.
        
        Args:
            event_type: Event type
            data: Event data
            
        Returns:
            Number of webhooks triggered
        """
        # Convert event type to string
        event = event_type.value if isinstance(event_type, WebhookEventType) else str(event_type)
        
        # Get webhooks for this event
        webhook_ids = self.webhook_events.get(event, set())
        if not webhook_ids:
            return 0
        
        # Prepare payload
        payload = {
            "event": event,
            "timestamp": self._get_iso_timestamp(),
            "data": data
        }
        
        # Queue deliveries
        count = 0
        for webhook_id in webhook_ids:
            # Generate a unique delivery ID
            delivery_id = self._generate_id('dlv_')
            
            # Queue delivery
            await self.delivery_queue.put((delivery_id, webhook_id, payload, 1))
            count += 1
        
        logger.info(f"Triggered event {event} for {count} webhooks")
        return count
    
    # Helper methods for specific events
    
    async def trigger_niche_analysis_completed(
        self,
        analysis_id: str,
        results: Dict[str, Any]
    ) -> int:
        """
        Trigger a niche analysis completed event.
        
        Args:
            analysis_id: Analysis ID
            results: Analysis results
            
        Returns:
            Number of webhooks triggered
        """
        return await self.trigger_event(
            WebhookEventType.NICHE_ANALYSIS_COMPLETED,
            {
                "analysis_id": analysis_id,
                "results": results
            }
        )
    
    async def trigger_subscription_created(
        self,
        subscription_id: str,
        subscription_data: Dict[str, Any]
    ) -> int:
        """
        Trigger a subscription created event.
        
        Args:
            subscription_id: Subscription ID
            subscription_data: Subscription data
            
        Returns:
            Number of webhooks triggered
        """
        return await self.trigger_event(
            WebhookEventType.SUBSCRIPTION_CREATED,
            {
                "subscription_id": subscription_id,
                "subscription": subscription_data
            }
        )
    
    async def trigger_payment_received(
        self,
        payment_id: str,
        payment_data: Dict[str, Any]
    ) -> int:
        """
        Trigger a payment received event.
        
        Args:
            payment_id: Payment ID
            payment_data: Payment data
            
        Returns:
            Number of webhooks triggered
        """
        return await self.trigger_event(
            WebhookEventType.PAYMENT_RECEIVED,
            {
                "payment_id": payment_id,
                "payment": payment_data
            }
        )