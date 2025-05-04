"""
"""
Webhook service for the API server.
Webhook service for the API server.


This module provides services for webhook management and delivery.
This module provides services for webhook management and delivery.
"""
"""


import asyncio
import asyncio
import json
import json
import logging
import logging
import time
import time
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


import aiohttp
import aiohttp


from .audit_service import AuditService
from .audit_service import AuditService
from .metrics import (track_queue_latency, track_webhook_delivery,
from .metrics import (track_queue_latency, track_webhook_delivery,
track_webhook_error, track_webhook_retry,
track_webhook_error, track_webhook_retry,
update_queue_size, update_webhook_health)
update_queue_size, update_webhook_health)
from .webhook_security import WebhookSignatureVerifier
from .webhook_security import WebhookSignatureVerifier


# Configure logger
# Configure logger
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class WebhookService:
    class WebhookService:
    """
    """
    Service for webhook management and delivery.
    Service for webhook management and delivery.
    """
    """


    def __init__(self, audit_service: Optional[AuditService] = None):
    def __init__(self, audit_service: Optional[AuditService] = None):
    """
    """
    Initialize the webhook service.
    Initialize the webhook service.


    Args:
    Args:
    audit_service: Audit service for recording events
    audit_service: Audit service for recording events
    """
    """
    self.webhooks = {}
    self.webhooks = {}
    self.deliveries = {}
    self.deliveries = {}
    self.running = False
    self.running = False
    self.delivery_queue = asyncio.Queue()
    self.delivery_queue = asyncio.Queue()
    self.worker_task = None
    self.worker_task = None
    self.audit_service = audit_service or AuditService()
    self.audit_service = audit_service or AuditService()


    async def deliver_event(
    async def deliver_event(
    self, webhook_id: str, event_type: str, event_data: Dict[str, Any]
    self, webhook_id: str, event_type: str, event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Deliver an event to a specific webhook immediately.
    Deliver an event to a specific webhook immediately.


    Args:
    Args:
    webhook_id: ID of the webhook to deliver to
    webhook_id: ID of the webhook to deliver to
    event_type: Type of event to deliver
    event_type: Type of event to deliver
    event_data: Event data to deliver
    event_data: Event data to deliver


    Returns:
    Returns:
    Delivery result
    Delivery result


    Raises:
    Raises:
    ValueError: If webhook is not found, inactive, or not subscribed to event type
    ValueError: If webhook is not found, inactive, or not subscribed to event type
    """
    """
    # Get webhook
    # Get webhook
    webhook = await self.get_webhook(webhook_id)
    webhook = await self.get_webhook(webhook_id)
    if not webhook:
    if not webhook:
    raise ValueError(f"Webhook not found: {webhook_id}")
    raise ValueError(f"Webhook not found: {webhook_id}")


    # Check if webhook is active
    # Check if webhook is active
    if not webhook["is_active"]:
    if not webhook["is_active"]:
    raise ValueError(f"Webhook is not active: {webhook_id}")
    raise ValueError(f"Webhook is not active: {webhook_id}")


    # Check if webhook is subscribed to this event type
    # Check if webhook is subscribed to this event type
    if event_type not in webhook["events"]:
    if event_type not in webhook["events"]:
    raise ValueError(
    raise ValueError(
    f"Webhook {webhook_id} is not subscribed to event type: {event_type}"
    f"Webhook {webhook_id} is not subscribed to event type: {event_type}"
    )
    )


    # Create delivery record
    # Create delivery record
    delivery_id = str(uuid.uuid4())
    delivery_id = str(uuid.uuid4())
    delivery = {
    delivery = {
    "id": delivery_id,
    "id": delivery_id,
    "webhook_id": webhook_id,
    "webhook_id": webhook_id,
    "event_type": event_type,
    "event_type": event_type,
    "event_data": event_data,
    "event_data": event_data,
    "status": "pending",
    "status": "pending",
    "attempts": 0,
    "attempts": 0,
    "created_at": datetime.utcnow().isoformat(),
    "created_at": datetime.utcnow().isoformat(),
    }
    }


    # Store delivery
    # Store delivery
    self.deliveries[delivery_id] = delivery
    self.deliveries[delivery_id] = delivery


    # Deliver webhook directly
    # Deliver webhook directly
    await self._deliver_webhook(webhook, delivery)
    await self._deliver_webhook(webhook, delivery)


    return delivery
    return delivery


    async def start(self):
    async def start(self):
    """
    """
    Start the webhook service.
    Start the webhook service.
    """
    """
    if self.running:
    if self.running:
    return self.running = True
    return self.running = True
    self.worker_task = asyncio.create_task(self._delivery_worker())
    self.worker_task = asyncio.create_task(self._delivery_worker())
    logger.info("Webhook service started")
    logger.info("Webhook service started")


    async def stop(self):
    async def stop(self):
    """
    """
    Stop the webhook service.
    Stop the webhook service.
    """
    """
    if not self.running:
    if not self.running:
    return self.running = False
    return self.running = False
    if self.worker_task:
    if self.worker_task:
    self.worker_task.cancel()
    self.worker_task.cancel()
    try:
    try:
    await self.worker_task
    await self.worker_task
except asyncio.CancelledError:
except asyncio.CancelledError:
    pass
    pass
    logger.info("Webhook service stopped")
    logger.info("Webhook service stopped")


    async def register_webhook(
    async def register_webhook(
    self,
    self,
    data: Dict[str, Any],
    data: Dict[str, Any],
    actor_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Register a new webhook.
    Register a new webhook.


    Args:
    Args:
    data: Webhook data
    data: Webhook data
    actor_id: ID of the actor registering the webhook
    actor_id: ID of the actor registering the webhook
    ip_address: IP address of the actor
    ip_address: IP address of the actor
    user_agent: User agent of the actor
    user_agent: User agent of the actor


    Returns:
    Returns:
    Registered webhook
    Registered webhook
    """
    """
    webhook_id = str(uuid.uuid4())
    webhook_id = str(uuid.uuid4())
    webhook = {
    webhook = {
    "id": webhook_id,
    "id": webhook_id,
    "url": data["url"],
    "url": data["url"],
    "events": data["events"],
    "events": data["events"],
    "description": data.get("description"),
    "description": data.get("description"),
    "headers": data.get("headers", {}),
    "headers": data.get("headers", {}),
    "is_active": data.get("is_active", True),
    "is_active": data.get("is_active", True),
    "created_at": datetime.utcnow().isoformat(),
    "created_at": datetime.utcnow().isoformat(),
    "last_called_at": None,
    "last_called_at": None,
    "secret": f"whsec_{uuid.uuid4().hex}",
    "secret": f"whsec_{uuid.uuid4().hex}",
    }
    }


    self.webhooks[webhook_id] = webhook
    self.webhooks[webhook_id] = webhook
    logger.info(f"Webhook registered: {webhook_id}")
    logger.info(f"Webhook registered: {webhook_id}")


    # Record audit event
    # Record audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.created",
    event_type="webhook.created",
    resource_type="webhook",
    resource_type="webhook",
    action="create",
    action="create",
    resource_id=webhook_id,
    resource_id=webhook_id,
    actor_id=actor_id,
    actor_id=actor_id,
    actor_type="user" if actor_id else "system",
    actor_type="user" if actor_id else "system",
    status="success",
    status="success",
    details={
    details={
    "url": data["url"],
    "url": data["url"],
    "events": data["events"],
    "events": data["events"],
    "description": data.get("description"),
    "description": data.get("description"),
    "is_active": data.get("is_active", True),
    "is_active": data.get("is_active", True),
    },
    },
    ip_address=ip_address,
    ip_address=ip_address,
    user_agent=user_agent,
    user_agent=user_agent,
    )
    )


    return webhook
    return webhook


    async def list_webhooks(self) -> List[Dict[str, Any]]:
    async def list_webhooks(self) -> List[Dict[str, Any]]:
    """
    """
    List all webhooks.
    List all webhooks.


    Returns:
    Returns:
    List of webhooks
    List of webhooks
    """
    """
    return list(self.webhooks.values())
    return list(self.webhooks.values())


    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a webhook by ID.
    Get a webhook by ID.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID


    Returns:
    Returns:
    Webhook if found, None otherwise
    Webhook if found, None otherwise
    """
    """
    return self.webhooks.get(webhook_id)
    return self.webhooks.get(webhook_id)


    async def update_webhook(
    async def update_webhook(
    self,
    self,
    webhook_id: str,
    webhook_id: str,
    data: Dict[str, Any],
    data: Dict[str, Any],
    actor_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_agent: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
    ) -> Optional[Dict[str, Any]]:
    """
    """
    Update a webhook.
    Update a webhook.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    data: Updated webhook data
    data: Updated webhook data
    actor_id: ID of the actor updating the webhook
    actor_id: ID of the actor updating the webhook
    ip_address: IP address of the actor
    ip_address: IP address of the actor
    user_agent: User agent of the actor
    user_agent: User agent of the actor


    Returns:
    Returns:
    Updated webhook if found, None otherwise
    Updated webhook if found, None otherwise
    """
    """
    webhook = self.webhooks.get(webhook_id)
    webhook = self.webhooks.get(webhook_id)


    if not webhook:
    if not webhook:
    return None
    return None


    # Store original values for audit
    # Store original values for audit
    original_values = {
    original_values = {
    "url": webhook["url"],
    "url": webhook["url"],
    "events": webhook["events"],
    "events": webhook["events"],
    "description": webhook.get("description"),
    "description": webhook.get("description"),
    "headers": webhook.get("headers", {}),
    "headers": webhook.get("headers", {}),
    "is_active": webhook.get("is_active", True),
    "is_active": webhook.get("is_active", True),
    }
    }


    # Update webhook fields
    # Update webhook fields
    if "url" in data:
    if "url" in data:
    webhook["url"] = data["url"]
    webhook["url"] = data["url"]
    if "events" in data:
    if "events" in data:
    webhook["events"] = data["events"]
    webhook["events"] = data["events"]
    if "description" in data:
    if "description" in data:
    webhook["description"] = data["description"]
    webhook["description"] = data["description"]
    if "headers" in data:
    if "headers" in data:
    webhook["headers"] = data["headers"]
    webhook["headers"] = data["headers"]
    if "is_active" in data:
    if "is_active" in data:
    webhook["is_active"] = data["is_active"]
    webhook["is_active"] = data["is_active"]


    logger.info(f"Webhook updated: {webhook_id}")
    logger.info(f"Webhook updated: {webhook_id}")


    # Record audit event
    # Record audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.updated",
    event_type="webhook.updated",
    resource_type="webhook",
    resource_type="webhook",
    action="update",
    action="update",
    resource_id=webhook_id,
    resource_id=webhook_id,
    actor_id=actor_id,
    actor_id=actor_id,
    actor_type="user" if actor_id else "system",
    actor_type="user" if actor_id else "system",
    status="success",
    status="success",
    details={
    details={
    "original": original_values,
    "original": original_values,
    "updated": {
    "updated": {
    "url": webhook["url"],
    "url": webhook["url"],
    "events": webhook["events"],
    "events": webhook["events"],
    "description": webhook.get("description"),
    "description": webhook.get("description"),
    "headers": webhook.get("headers", {}),
    "headers": webhook.get("headers", {}),
    "is_active": webhook.get("is_active", True),
    "is_active": webhook.get("is_active", True),
    },
    },
    "changes": {
    "changes": {
    k: data[k]
    k: data[k]
    for k in data
    for k in data
    if k in original_values and data[k] != original_values[k]
    if k in original_values and data[k] != original_values[k]
    },
    },
    },
    },
    ip_address=ip_address,
    ip_address=ip_address,
    user_agent=user_agent,
    user_agent=user_agent,
    )
    )


    return webhook
    return webhook


    async def delete_webhook(
    async def delete_webhook(
    self,
    self,
    webhook_id: str,
    webhook_id: str,
    actor_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_agent: Optional[str] = None,
    ) -> bool:
    ) -> bool:
    """
    """
    Delete a webhook.
    Delete a webhook.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    actor_id: ID of the actor deleting the webhook
    actor_id: ID of the actor deleting the webhook
    ip_address: IP address of the actor
    ip_address: IP address of the actor
    user_agent: User agent of the actor
    user_agent: User agent of the actor


    Returns:
    Returns:
    True if the webhook was deleted, False otherwise
    True if the webhook was deleted, False otherwise
    """
    """
    if webhook_id not in self.webhooks:
    if webhook_id not in self.webhooks:
    return False
    return False


    # Store webhook data for audit
    # Store webhook data for audit
    webhook_data = self.webhooks[webhook_id].copy()
    webhook_data = self.webhooks[webhook_id].copy()


    # Delete webhook
    # Delete webhook
    del self.webhooks[webhook_id]
    del self.webhooks[webhook_id]
    logger.info(f"Webhook deleted: {webhook_id}")
    logger.info(f"Webhook deleted: {webhook_id}")


    # Record audit event
    # Record audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.deleted",
    event_type="webhook.deleted",
    resource_type="webhook",
    resource_type="webhook",
    action="delete",
    action="delete",
    resource_id=webhook_id,
    resource_id=webhook_id,
    actor_id=actor_id,
    actor_id=actor_id,
    actor_type="user" if actor_id else "system",
    actor_type="user" if actor_id else "system",
    status="success",
    status="success",
    details={
    details={
    "url": webhook_data["url"],
    "url": webhook_data["url"],
    "events": webhook_data["events"],
    "events": webhook_data["events"],
    "description": webhook_data.get("description"),
    "description": webhook_data.get("description"),
    "is_active": webhook_data.get("is_active", True),
    "is_active": webhook_data.get("is_active", True),
    },
    },
    ip_address=ip_address,
    ip_address=ip_address,
    user_agent=user_agent,
    user_agent=user_agent,
    )
    )


    return True
    return True


    async def trigger_event(
    async def trigger_event(
    self, event_type: str, event_data: Dict[str, Any]
    self, event_type: str, event_data: Dict[str, Any]
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    Trigger an event and deliver it to subscribed webhooks.
    Trigger an event and deliver it to subscribed webhooks.


    Args:
    Args:
    event_type: Type of event
    event_type: Type of event
    event_data: Event data
    event_data: Event data


    Returns:
    Returns:
    List of delivery IDs
    List of delivery IDs
    """
    """
    delivery_ids = []
    delivery_ids = []


    # Find webhooks subscribed to this event type
    # Find webhooks subscribed to this event type
    for webhook in self.webhooks.values():
    for webhook in self.webhooks.values():
    if not webhook["is_active"]:
    if not webhook["is_active"]:
    continue
    continue


    if event_type in webhook["events"]:
    if event_type in webhook["events"]:
    # Create delivery
    # Create delivery
    delivery_id = str(uuid.uuid4())
    delivery_id = str(uuid.uuid4())
    delivery = {
    delivery = {
    "id": delivery_id,
    "id": delivery_id,
    "webhook_id": webhook["id"],
    "webhook_id": webhook["id"],
    "event_type": event_type,
    "event_type": event_type,
    "event_data": event_data,
    "event_data": event_data,
    "status": "pending",
    "status": "pending",
    "attempts": 0,
    "attempts": 0,
    "max_attempts": 5,
    "max_attempts": 5,
    "created_at": datetime.utcnow().isoformat(),
    "created_at": datetime.utcnow().isoformat(),
    "next_attempt_at": datetime.utcnow().isoformat(),
    "next_attempt_at": datetime.utcnow().isoformat(),
    }
    }


    self.deliveries[delivery_id] = delivery
    self.deliveries[delivery_id] = delivery
    delivery_ids.append(delivery_id)
    delivery_ids.append(delivery_id)


    # Queue delivery
    # Queue delivery
    await self.delivery_queue.put(delivery_id)
    await self.delivery_queue.put(delivery_id)
    logger.info(
    logger.info(
    f"Event queued for delivery: {event_type} to webhook {webhook['id']}"
    f"Event queued for delivery: {event_type} to webhook {webhook['id']}"
    )
    )


    return delivery_ids
    return delivery_ids


    async def get_deliveries(
    async def get_deliveries(
    self, webhook_id: Optional[str] = None, status: Optional[str] = None
    self, webhook_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get webhook deliveries.
    Get webhook deliveries.


    Args:
    Args:
    webhook_id: Filter by webhook ID
    webhook_id: Filter by webhook ID
    status: Filter by status
    status: Filter by status


    Returns:
    Returns:
    List of deliveries
    List of deliveries
    """
    """
    deliveries = list(self.deliveries.values())
    deliveries = list(self.deliveries.values())


    # Filter by webhook ID
    # Filter by webhook ID
    if webhook_id:
    if webhook_id:
    deliveries = [d for d in deliveries if d["webhook_id"] == webhook_id]
    deliveries = [d for d in deliveries if d["webhook_id"] == webhook_id]


    # Filter by status
    # Filter by status
    if status:
    if status:
    deliveries = [d for d in deliveries if d["status"] == status]
    deliveries = [d for d in deliveries if d["status"] == status]


    return deliveries
    return deliveries


    async def _delivery_worker(self):
    async def _delivery_worker(self):
    """
    """
    Worker for delivering webhooks.
    Worker for delivering webhooks.
    """
    """
    while self.running:
    while self.running:
    try:
    try:
    # Get delivery from queue
    # Get delivery from queue
    delivery_id = await self.delivery_queue.get()
    delivery_id = await self.delivery_queue.get()
    delivery = self.deliveries.get(delivery_id)
    delivery = self.deliveries.get(delivery_id)


    if not delivery:
    if not delivery:
    self.delivery_queue.task_done()
    self.delivery_queue.task_done()
    continue
    continue


    # Get webhook
    # Get webhook
    webhook = self.webhooks.get(delivery["webhook_id"])
    webhook = self.webhooks.get(delivery["webhook_id"])


    if not webhook or not webhook["is_active"]:
    if not webhook or not webhook["is_active"]:
    self.delivery_queue.task_done()
    self.delivery_queue.task_done()
    continue
    continue


    # Deliver webhook
    # Deliver webhook
    success = await self._deliver_webhook(webhook, delivery)
    success = await self._deliver_webhook(webhook, delivery)


    if not success and delivery["attempts"] < delivery["max_attempts"]:
    if not success and delivery["attempts"] < delivery["max_attempts"]:
    # Track retry attempt
    # Track retry attempt
    track_webhook_retry(
    track_webhook_retry(
    webhook_id=webhook["id"], event_type=delivery["event_type"]
    webhook_id=webhook["id"], event_type=delivery["event_type"]
    )
    )


    # Calculate next attempt time (exponential backoff)
    # Calculate next attempt time (exponential backoff)
    backoff = min(2 ** delivery["attempts"], 60)  # Max 60 minutes
    backoff = min(2 ** delivery["attempts"], 60)  # Max 60 minutes
    next_attempt = datetime.utcnow().timestamp() + backoff * 60
    next_attempt = datetime.utcnow().timestamp() + backoff * 60
    delivery["next_attempt_at"] = datetime.fromtimestamp(
    delivery["next_attempt_at"] = datetime.fromtimestamp(
    next_attempt
    next_attempt
    ).isoformat()
    ).isoformat()


    # Record retry audit event
    # Record retry audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.delivery.retried",
    event_type="webhook.delivery.retried",
    resource_type="webhook_delivery",
    resource_type="webhook_delivery",
    action="retry",
    action="retry",
    resource_id=delivery_id,
    resource_id=delivery_id,
    actor_id=None,
    actor_id=None,
    actor_type="system",
    actor_type="system",
    status="info",
    status="info",
    details={
    details={
    "webhook_id": webhook["id"],
    "webhook_id": webhook["id"],
    "event_type": delivery["event_type"],
    "event_type": delivery["event_type"],
    "attempt": delivery["attempts"],
    "attempt": delivery["attempts"],
    "max_attempts": delivery["max_attempts"],
    "max_attempts": delivery["max_attempts"],
    "next_attempt_at": delivery["next_attempt_at"],
    "next_attempt_at": delivery["next_attempt_at"],
    },
    },
    )
    )


    # Requeue for later
    # Requeue for later
    await asyncio.sleep(1)  # Small delay to avoid tight loop
    await asyncio.sleep(1)  # Small delay to avoid tight loop
    await self.delivery_queue.put(delivery_id)
    await self.delivery_queue.put(delivery_id)
    elif not success:
    elif not success:
    # Track max retries exceeded
    # Track max retries exceeded
    delivery["status"] = "max_retries_exceeded"
    delivery["status"] = "max_retries_exceeded"
    track_webhook_error(
    track_webhook_error(
    webhook_id=webhook["id"],
    webhook_id=webhook["id"],
    event_type=delivery["event_type"],
    event_type=delivery["event_type"],
    error_type="max_retries_exceeded",
    error_type="max_retries_exceeded",
    )
    )


    self.delivery_queue.task_done()
    self.delivery_queue.task_done()


except asyncio.CancelledError:
except asyncio.CancelledError:
    break
    break
except Exception as e:
except Exception as e:
    logger.error(f"Error in delivery worker: {str(e)}")
    logger.error(f"Error in delivery worker: {str(e)}")
    await asyncio.sleep(1)  # Small delay to avoid tight loop
    await asyncio.sleep(1)  # Small delay to avoid tight loop


    async def _deliver_webhook(
    async def _deliver_webhook(
    self, webhook: Dict[str, Any], delivery: Dict[str, Any]
    self, webhook: Dict[str, Any], delivery: Dict[str, Any]
    ) -> bool:
    ) -> bool:
    """
    """
    Deliver a webhook.
    Deliver a webhook.


    Args:
    Args:
    webhook: Webhook to deliver
    webhook: Webhook to deliver
    delivery: Delivery information
    delivery: Delivery information


    Returns:
    Returns:
    True if delivery was successful, False otherwise
    True if delivery was successful, False otherwise
    """
    """
    start_time = datetime.utcnow().timestamp()
    start_time = datetime.utcnow().timestamp()


    # Increment attempt counter
    # Increment attempt counter
    delivery["attempts"] += 1
    delivery["attempts"] += 1
    delivery["status"] = "retrying" if delivery["attempts"] > 1 else "pending"
    delivery["status"] = "retrying" if delivery["attempts"] > 1 else "pending"


    # Update queue size metric
    # Update queue size metric
    update_queue_size(self.delivery_queue.qsize())
    update_queue_size(self.delivery_queue.qsize())


    # Track queue latency
    # Track queue latency
    queued_time = (
    queued_time = (
    start_time - datetime.fromisoformat(delivery["created_at"]).timestamp()
    start_time - datetime.fromisoformat(delivery["created_at"]).timestamp()
    )
    )
    track_queue_latency(queued_time)
    track_queue_latency(queued_time)


    # Prepare payload
    # Prepare payload
    payload = {
    payload = {
    "id": delivery["id"],
    "id": delivery["id"],
    "type": delivery["event_type"],
    "type": delivery["event_type"],
    "created_at": delivery["created_at"],
    "created_at": delivery["created_at"],
    "data": delivery["event_data"],
    "data": delivery["event_data"],
    }
    }


    # Convert payload to JSON
    # Convert payload to JSON
    payload_json = json.dumps(payload)
    payload_json = json.dumps(payload)


    # Generate signature
    # Generate signature
    signature = WebhookSignatureVerifier.create_signature(
    signature = WebhookSignatureVerifier.create_signature(
    webhook["secret"], payload_json
    webhook["secret"], payload_json
    )
    )


    # Prepare headers
    # Prepare headers
    headers = {
    headers = {
    "Content-Type": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "pAIssive-Income-Webhook/1.0",
    "User-Agent": "pAIssive-Income-Webhook/1.0",
    "X-Webhook-ID": webhook["id"],
    "X-Webhook-ID": webhook["id"],
    "X-Webhook-Signature": signature,
    "X-Webhook-Signature": signature,
    }
    }


    # Add custom headers
    # Add custom headers
    if webhook.get("headers"):
    if webhook.get("headers"):
    headers.update(webhook["headers"])
    headers.update(webhook["headers"])


    try:
    try:
    # Send webhook
    # Send webhook
    async with aiohttp.ClientSession() as session:
    async with aiohttp.ClientSession() as session:
    async with session.post(
    async with session.post(
    webhook["url"], data=payload_json, headers=headers, timeout=10
    webhook["url"], data=payload_json, headers=headers, timeout=10
    ) as response:
    ) as response:
    # Get response
    # Get response
    status_code = response.status
    status_code = response.status
    response_body = await response.text()
    response_body = await response.text()


    # Calculate delivery duration
    # Calculate delivery duration
    duration = datetime.utcnow().timestamp() - start_time
    duration = datetime.utcnow().timestamp() - start_time


    # Update delivery record
    # Update delivery record
    delivery["response_code"] = status_code
    delivery["response_code"] = status_code
    delivery["response_body"] = response_body
    delivery["response_body"] = response_body


    # Check if successful
    # Check if successful
    if 200 <= status_code < 300:
    if 200 <= status_code < 300:
    delivery["status"] = "success"
    delivery["status"] = "success"
    webhook["last_called_at"] = datetime.utcnow().isoformat()
    webhook["last_called_at"] = datetime.utcnow().isoformat()


    # Track successful delivery
    # Track successful delivery
    track_webhook_delivery(
    track_webhook_delivery(
    webhook_id=webhook["id"],
    webhook_id=webhook["id"],
    event_type=delivery["event_type"],
    event_type=delivery["event_type"],
    duration=duration,
    duration=duration,
    status="success",
    status="success",
    )
    )


    # Update health status
    # Update health status
    update_webhook_health(webhook["id"], webhook["url"], True)
    update_webhook_health(webhook["id"], webhook["url"], True)


    logger.info(
    logger.info(
    f"Webhook delivered successfully: {delivery['id']} to {webhook['url']}"
    f"Webhook delivered successfully: {delivery['id']} to {webhook['url']}"
    )
    )


    # Record success audit event
    # Record success audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.delivery.sent",
    event_type="webhook.delivery.sent",
    resource_type="webhook_delivery",
    resource_type="webhook_delivery",
    action="send",
    action="send",
    resource_id=delivery["id"],
    resource_id=delivery["id"],
    actor_id=None,
    actor_id=None,
    actor_type="system",
    actor_type="system",
    status="success",
    status="success",
    details={
    details={
    "webhook_id": webhook["id"],
    "webhook_id": webhook["id"],
    "event_type": delivery["event_type"],
    "event_type": delivery["event_type"],
    "url": webhook["url"],
    "url": webhook["url"],
    "response_code": status_code,
    "response_code": status_code,
    "attempt": delivery["attempts"],
    "attempt": delivery["attempts"],
    },
    },
    )
    )


    return True
    return True
    else:
    else:
    delivery["status"] = "failed"
    delivery["status"] = "failed"
    logger.warning(
    logger.warning(
    f"Webhook delivery failed with status {status_code}: {delivery['id']} to {webhook['url']}"
    f"Webhook delivery failed with status {status_code}: {delivery['id']} to {webhook['url']}"
    )
    )


    # Track failed delivery
    # Track failed delivery
    track_webhook_delivery(
    track_webhook_delivery(
    webhook_id=webhook["id"],
    webhook_id=webhook["id"],
    event_type=delivery["event_type"],
    event_type=delivery["event_type"],
    duration=duration,
    duration=duration,
    status="failed",
    status="failed",
    )
    )


    # Update health status
    # Update health status
    update_webhook_health(webhook["id"], webhook["url"], False)
    update_webhook_health(webhook["id"], webhook["url"], False)


    # Track error
    # Track error
    track_webhook_error(
    track_webhook_error(
    webhook_id=webhook["id"],
    webhook_id=webhook["id"],
    event_type=delivery["event_type"],
    event_type=delivery["event_type"],
    error_type=f"http_{status_code}",
    error_type=f"http_{status_code}",
    )
    )


    # Record failure audit event
    # Record failure audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.delivery.failed",
    event_type="webhook.delivery.failed",
    resource_type="webhook_delivery",
    resource_type="webhook_delivery",
    action="send",
    action="send",
    resource_id=delivery["id"],
    resource_id=delivery["id"],
    actor_id=None,
    actor_id=None,
    actor_type="system",
    actor_type="system",
    status="failure",
    status="failure",
    details={
    details={
    "webhook_id": webhook["id"],
    "webhook_id": webhook["id"],
    "event_type": delivery["event_type"],
    "event_type": delivery["event_type"],
    "url": webhook["url"],
    "url": webhook["url"],
    "response_code": status_code,
    "response_code": status_code,
    "response_body": response_body,
    "response_body": response_body,
    "attempt": delivery["attempts"],
    "attempt": delivery["attempts"],
    "max_attempts": delivery["max_attempts"],
    "max_attempts": delivery["max_attempts"],
    },
    },
    )
    )


    return False
    return False


except Exception as e:
except Exception as e:
    # Update delivery
    # Update delivery
    delivery["status"] = "failed"
    delivery["status"] = "failed"
    delivery["error"] = str(e)
    delivery["error"] = str(e)


    # Track failed delivery
    # Track failed delivery
    duration = datetime.utcnow().timestamp() - start_time
    duration = datetime.utcnow().timestamp() - start_time
    track_webhook_delivery(
    track_webhook_delivery(
    webhook_id=webhook["id"],
    webhook_id=webhook["id"],
    event_type=delivery["event_type"],
    event_type=delivery["event_type"],
    duration=duration,
    duration=duration,
    status="failed",
    status="failed",
    )
    )


    # Update health status
    # Update health status
    update_webhook_health(webhook["id"], webhook["url"], False)
    update_webhook_health(webhook["id"], webhook["url"], False)


    # Track error
    # Track error
    track_webhook_error(
    track_webhook_error(
    webhook_id=webhook["id"],
    webhook_id=webhook["id"],
    event_type=delivery["event_type"],
    event_type=delivery["event_type"],
    error_type="connection_error",
    error_type="connection_error",
    )
    )


    logger.warning(f"Webhook delivery failed with error: {str(e)}")
    logger.warning(f"Webhook delivery failed with error: {str(e)}")


    # Record error audit event
    # Record error audit event
    self.audit_service.create_event(
    self.audit_service.create_event(
    event_type="webhook.delivery.failed",
    event_type="webhook.delivery.failed",
    resource_type="webhook_delivery",
    resource_type="webhook_delivery",
    action="send",
    action="send",
    resource_id=delivery["id"],
    resource_id=delivery["id"],
    actor_id=None,
    actor_id=None,
    actor_type="system",
    actor_type="system",
    status="failure",
    status="failure",
    details={
    details={
    "webhook_id": webhook["id"],
    "webhook_id": webhook["id"],
    "event_type": delivery["event_type"],
    "event_type": delivery["event_type"],
    "url": webhook["url"],
    "url": webhook["url"],
    "error": str(e),
    "error": str(e),
    "attempt": delivery["attempts"],
    "attempt": delivery["attempts"],
    "max_attempts": delivery["max_attempts"],
    "max_attempts": delivery["max_attempts"],
    },
    },
    )
    )


    return False
    return False