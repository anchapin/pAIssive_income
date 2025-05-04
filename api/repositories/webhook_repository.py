"""
"""
Webhook repository for the API server.
Webhook repository for the API server.


This module provides a repository for storing and retrieving webhooks.
This module provides a repository for storing and retrieving webhooks.
"""
"""




import hashlib
import hashlib
import hmac
import hmac
import json
import json
import logging
import logging
import os
import os
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from typing import Any, Dict, List, Optional, Set


from ..schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from ..schemas.webhook import WebhookDeliveryStatus, WebhookEventType


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




class WebhookRepository:
    class WebhookRepository:
    """Repository for webhook storage and retrieval."""

    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the webhook repository.
    Initialize the webhook repository.


    Args:
    Args:
    storage_path: Path where webhook data will be stored
    storage_path: Path where webhook data will be stored
    """
    """
    self.storage_path = storage_path or "webhooks"
    self.storage_path = storage_path or "webhooks"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    # Create subdirectories
    # Create subdirectories
    self.webhooks_dir = os.path.join(self.storage_path, "webhooks")
    self.webhooks_dir = os.path.join(self.storage_path, "webhooks")
    self.deliveries_dir = os.path.join(self.storage_path, "deliveries")
    self.deliveries_dir = os.path.join(self.storage_path, "deliveries")
    self.attempts_dir = os.path.join(self.storage_path, "attempts")
    self.attempts_dir = os.path.join(self.storage_path, "attempts")


    os.makedirs(self.webhooks_dir, exist_ok=True)
    os.makedirs(self.webhooks_dir, exist_ok=True)
    os.makedirs(self.deliveries_dir, exist_ok=True)
    os.makedirs(self.deliveries_dir, exist_ok=True)
    os.makedirs(self.attempts_dir, exist_ok=True)
    os.makedirs(self.attempts_dir, exist_ok=True)


    # Initialize data structures
    # Initialize data structures
    self.webhooks: Dict[str, Dict[str, Any]] = {}
    self.webhooks: Dict[str, Dict[str, Any]] = {}
    self.deliveries: Dict[str, Dict[str, Any]] = {}
    self.deliveries: Dict[str, Dict[str, Any]] = {}
    self.attempts: Dict[str, Dict[str, Any]] = {}
    self.attempts: Dict[str, Dict[str, Any]] = {}


    # Initialize event to webhook mapping
    # Initialize event to webhook mapping
    self.event_to_webhooks: Dict[str, Set[str]] = {}
    self.event_to_webhooks: Dict[str, Set[str]] = {}


    # Load data
    # Load data
    self._load_data()
    self._load_data()


    def _load_data(self) -> None:
    def _load_data(self) -> None:
    """Load webhook data from storage."""
    # Load webhooks
    for filename in os.listdir(self.webhooks_dir):
    if filename.endswith(".json"):
    webhook_id = filename[:-5]  # Remove .json extension
    webhook_file = os.path.join(self.webhooks_dir, filename)
    try:
    with open(webhook_file, "r") as f:
    webhook = json.load(f)
    self.webhooks[webhook_id] = webhook

    # Update event to webhook mapping
    for event in webhook.get("events", []):
    if event not in self.event_to_webhooks:
    self.event_to_webhooks[event] = set()
    self.event_to_webhooks[event].add(webhook_id)
except Exception as e:
    logger.error(f"Error loading webhook {webhook_id}: {e}")

    logger.info(f"Loaded {len(self.webhooks)} webhooks")

    # Load deliveries
    for filename in os.listdir(self.deliveries_dir):
    if filename.endswith(".json"):
    delivery_id = filename[:-5]
    delivery_file = os.path.join(self.deliveries_dir, filename)
    try:
    with open(delivery_file, "r") as f:
    delivery = json.load(f)
    self.deliveries[delivery_id] = delivery
except Exception as e:
    logger.error(f"Error loading delivery {delivery_id}: {e}")

    logger.info(f"Loaded {len(self.deliveries)} webhook deliveries")

    # Load attempts
    for filename in os.listdir(self.attempts_dir):
    if filename.endswith(".json"):
    attempt_id = filename[:-5]
    attempt_file = os.path.join(self.attempts_dir, filename)
    try:
    with open(attempt_file, "r") as f:
    attempt = json.load(f)
    self.attempts[attempt_id] = attempt
except Exception as e:
    logger.error(f"Error loading attempt {attempt_id}: {e}")

    logger.info(f"Loaded {len(self.attempts)} webhook delivery attempts")

    def _save_webhook(self, webhook_id: str, webhook: Dict[str, Any]) -> None:
    """
    """
    Save webhook data to storage.
    Save webhook data to storage.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    webhook: Webhook data
    webhook: Webhook data
    """
    """
    webhook_file = os.path.join(self.webhooks_dir, f"{webhook_id}.json")
    webhook_file = os.path.join(self.webhooks_dir, f"{webhook_id}.json")
    with open(webhook_file, "w") as f:
    with open(webhook_file, "w") as f:
    json.dump(webhook, f, indent=2)
    json.dump(webhook, f, indent=2)


    def _save_delivery(self, delivery_id: str, delivery: Dict[str, Any]) -> None:
    def _save_delivery(self, delivery_id: str, delivery: Dict[str, Any]) -> None:
    """
    """
    Save delivery data to storage.
    Save delivery data to storage.


    Args:
    Args:
    delivery_id: Delivery ID
    delivery_id: Delivery ID
    delivery: Delivery data
    delivery: Delivery data
    """
    """
    delivery_file = os.path.join(self.deliveries_dir, f"{delivery_id}.json")
    delivery_file = os.path.join(self.deliveries_dir, f"{delivery_id}.json")
    with open(delivery_file, "w") as f:
    with open(delivery_file, "w") as f:
    json.dump(delivery, f, indent=2)
    json.dump(delivery, f, indent=2)


    def _save_attempt(self, attempt_id: str, attempt: Dict[str, Any]) -> None:
    def _save_attempt(self, attempt_id: str, attempt: Dict[str, Any]) -> None:
    """
    """
    Save attempt data to storage.
    Save attempt data to storage.


    Args:
    Args:
    attempt_id: Attempt ID
    attempt_id: Attempt ID
    attempt: Attempt data
    attempt: Attempt data
    """
    """
    attempt_file = os.path.join(self.attempts_dir, f"{attempt_id}.json")
    attempt_file = os.path.join(self.attempts_dir, f"{attempt_id}.json")
    with open(attempt_file, "w") as f:
    with open(attempt_file, "w") as f:
    json.dump(attempt, f, indent=2)
    json.dump(attempt, f, indent=2)


    def create_webhook(
    def create_webhook(
    self,
    self,
    url: str,
    url: str,
    events: List[WebhookEventType],
    events: List[WebhookEventType],
    description: Optional[str] = None,
    description: Optional[str] = None,
    active: bool = True,
    active: bool = True,
    secret: Optional[str] = None,
    secret: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a new webhook.
    Create a new webhook.


    Args:
    Args:
    url: Webhook URL
    url: Webhook URL
    events: List of events to subscribe to
    events: List of events to subscribe to
    description: Optional description
    description: Optional description
    active: Whether the webhook is active
    active: Whether the webhook is active
    secret: Secret for signing payloads
    secret: Secret for signing payloads


    Returns:
    Returns:
    Created webhook
    Created webhook
    """
    """
    webhook_id = str(uuid.uuid4())
    webhook_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    now = datetime.now().isoformat()


    # Hash secret if provided
    # Hash secret if provided
    secret_hash = None
    secret_hash = None
    if secret:
    if secret:
    secret_hash = self._hash_secret(secret)
    secret_hash = self._hash_secret(secret)


    webhook = {
    webhook = {
    "id": webhook_id,
    "id": webhook_id,
    "url": url,
    "url": url,
    "description": description,
    "description": description,
    "events": [
    "events": [
    event.value if isinstance(event, WebhookEventType) else event
    event.value if isinstance(event, WebhookEventType) else event
    for event in events
    for event in events
    ],
    ],
    "active": active,
    "active": active,
    "created_at": now,
    "created_at": now,
    "updated_at": None,
    "updated_at": None,
    "secret_hash": secret_hash,
    "secret_hash": secret_hash,
    }
    }


    self.webhooks[webhook_id] = webhook
    self.webhooks[webhook_id] = webhook


    # Update event to webhook mapping
    # Update event to webhook mapping
    for event in webhook["events"]:
    for event in webhook["events"]:
    if event not in self.event_to_webhooks:
    if event not in self.event_to_webhooks:
    self.event_to_webhooks[event] = set()
    self.event_to_webhooks[event] = set()
    self.event_to_webhooks[event].add(webhook_id)
    self.event_to_webhooks[event].add(webhook_id)


    # Save webhook
    # Save webhook
    self._save_webhook(webhook_id, webhook)
    self._save_webhook(webhook_id, webhook)


    logger.info(f"Created webhook {webhook_id} for URL {url}")
    logger.info(f"Created webhook {webhook_id} for URL {url}")
    return webhook
    return webhook


    def update_webhook(
    def update_webhook(
    self,
    self,
    webhook_id: str,
    webhook_id: str,
    url: Optional[str] = None,
    url: Optional[str] = None,
    description: Optional[str] = None,
    description: Optional[str] = None,
    events: Optional[List[WebhookEventType]] = None,
    events: Optional[List[WebhookEventType]] = None,
    active: Optional[bool] = None,
    active: Optional[bool] = None,
    secret: Optional[str] = None,
    secret: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update an existing webhook.
    Update an existing webhook.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    url: Optional new URL
    url: Optional new URL
    description: Optional new description
    description: Optional new description
    events: Optional new list of events
    events: Optional new list of events
    active: Optional new active status
    active: Optional new active status
    secret: Optional new secret
    secret: Optional new secret


    Returns:
    Returns:
    Updated webhook
    Updated webhook


    Raises:
    Raises:
    ValueError: If webhook not found
    ValueError: If webhook not found
    """
    """
    if webhook_id not in self.webhooks:
    if webhook_id not in self.webhooks:
    raise ValueError(f"Webhook {webhook_id} not found")
    raise ValueError(f"Webhook {webhook_id} not found")


    webhook = self.webhooks[webhook_id]
    webhook = self.webhooks[webhook_id]
    now = datetime.now().isoformat()
    now = datetime.now().isoformat()


    # Remove webhook from event mappings if events are changing
    # Remove webhook from event mappings if events are changing
    if events is not None:
    if events is not None:
    for event in webhook["events"]:
    for event in webhook["events"]:
    if event in self.event_to_webhooks:
    if event in self.event_to_webhooks:
    self.event_to_webhooks[event].discard(webhook_id)
    self.event_to_webhooks[event].discard(webhook_id)


    # Update webhook fields
    # Update webhook fields
    if url is not None:
    if url is not None:
    webhook["url"] = url
    webhook["url"] = url


    if description is not None:
    if description is not None:
    webhook["description"] = description
    webhook["description"] = description


    if events is not None:
    if events is not None:
    webhook["events"] = [
    webhook["events"] = [
    event.value if isinstance(event, WebhookEventType) else event
    event.value if isinstance(event, WebhookEventType) else event
    for event in events
    for event in events
    ]
    ]


    # Update event to webhook mapping
    # Update event to webhook mapping
    for event in webhook["events"]:
    for event in webhook["events"]:
    if event not in self.event_to_webhooks:
    if event not in self.event_to_webhooks:
    self.event_to_webhooks[event] = set()
    self.event_to_webhooks[event] = set()
    self.event_to_webhooks[event].add(webhook_id)
    self.event_to_webhooks[event].add(webhook_id)


    if active is not None:
    if active is not None:
    webhook["active"] = active
    webhook["active"] = active


    if secret is not None:
    if secret is not None:
    webhook["secret_hash"] = self._hash_secret(secret)
    webhook["secret_hash"] = self._hash_secret(secret)


    webhook["updated_at"] = now
    webhook["updated_at"] = now


    # Save webhook
    # Save webhook
    self._save_webhook(webhook_id, webhook)
    self._save_webhook(webhook_id, webhook)


    logger.info(f"Updated webhook {webhook_id}")
    logger.info(f"Updated webhook {webhook_id}")
    return webhook
    return webhook


    def delete_webhook(self, webhook_id: str) -> bool:
    def delete_webhook(self, webhook_id: str) -> bool:
    """
    """
    Delete a webhook.
    Delete a webhook.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID


    Returns:
    Returns:
    True if webhook was deleted, False otherwise
    True if webhook was deleted, False otherwise
    """
    """
    if webhook_id not in self.webhooks:
    if webhook_id not in self.webhooks:
    return False
    return False


    webhook = self.webhooks[webhook_id]
    webhook = self.webhooks[webhook_id]


    # Remove webhook from event mappings
    # Remove webhook from event mappings
    for event in webhook["events"]:
    for event in webhook["events"]:
    if event in self.event_to_webhooks:
    if event in self.event_to_webhooks:
    self.event_to_webhooks[event].discard(webhook_id)
    self.event_to_webhooks[event].discard(webhook_id)


    # Remove webhook
    # Remove webhook
    del self.webhooks[webhook_id]
    del self.webhooks[webhook_id]


    # Delete webhook file
    # Delete webhook file
    webhook_file = os.path.join(self.webhooks_dir, f"{webhook_id}.json")
    webhook_file = os.path.join(self.webhooks_dir, f"{webhook_id}.json")
    if os.path.exists(webhook_file):
    if os.path.exists(webhook_file):
    os.remove(webhook_file)
    os.remove(webhook_file)


    logger.info(f"Deleted webhook {webhook_id}")
    logger.info(f"Deleted webhook {webhook_id}")
    return True
    return True


    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
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
    Webhook data or None if not found
    Webhook data or None if not found
    """
    """
    return self.webhooks.get(webhook_id)
    return self.webhooks.get(webhook_id)


    def get_webhooks(self) -> List[Dict[str, Any]]:
    def get_webhooks(self) -> List[Dict[str, Any]]:
    """
    """
    Get all webhooks.
    Get all webhooks.


    Returns:
    Returns:
    List of webhooks
    List of webhooks
    """
    """
    return list(self.webhooks.values())
    return list(self.webhooks.values())


    def get_webhooks_for_event(self, event: str) -> List[Dict[str, Any]]:
    def get_webhooks_for_event(self, event: str) -> List[Dict[str, Any]]:
    """
    """
    Get webhooks subscribed to a specific event.
    Get webhooks subscribed to a specific event.


    Args:
    Args:
    event: Event type
    event: Event type


    Returns:
    Returns:
    List of webhooks subscribed to the event
    List of webhooks subscribed to the event
    """
    """
    webhook_ids = self.event_to_webhooks.get(event, set())
    webhook_ids = self.event_to_webhooks.get(event, set())
    return [
    return [
    self.webhooks[wid]
    self.webhooks[wid]
    for wid in webhook_ids
    for wid in webhook_ids
    if wid in self.webhooks and self.webhooks[wid]["active"]
    if wid in self.webhooks and self.webhooks[wid]["active"]
    ]
    ]


    def create_delivery(
    def create_delivery(
    self, webhook_id: str, event_type: str, payload: Dict[str, Any]
    self, webhook_id: str, event_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a webhook delivery record.
    Create a webhook delivery record.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    event_type: Event type
    event_type: Event type
    payload: Event payload
    payload: Event payload


    Returns:
    Returns:
    Delivery record
    Delivery record


    Raises:
    Raises:
    ValueError: If webhook not found
    ValueError: If webhook not found
    """
    """
    if webhook_id not in self.webhooks:
    if webhook_id not in self.webhooks:
    raise ValueError(f"Webhook {webhook_id} not found")
    raise ValueError(f"Webhook {webhook_id} not found")


    delivery_id = str(uuid.uuid4())
    delivery_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    now = datetime.now().isoformat()


    delivery = {
    delivery = {
    "id": delivery_id,
    "id": delivery_id,
    "webhook_id": webhook_id,
    "webhook_id": webhook_id,
    "event_type": event_type,
    "event_type": event_type,
    "status": WebhookDeliveryStatus.PENDING.value,
    "status": WebhookDeliveryStatus.PENDING.value,
    "timestamp": now,
    "timestamp": now,
    "attempts": [],
    "attempts": [],
    }
    }


    self.deliveries[delivery_id] = delivery
    self.deliveries[delivery_id] = delivery


    # Save delivery
    # Save delivery
    self._save_delivery(delivery_id, delivery)
    self._save_delivery(delivery_id, delivery)


    logger.info(
    logger.info(
    f"Created delivery {delivery_id} for webhook {webhook_id} and event {event_type}"
    f"Created delivery {delivery_id} for webhook {webhook_id} and event {event_type}"
    )
    )
    return delivery
    return delivery


    def create_delivery_attempt(
    def create_delivery_attempt(
    self, delivery_id: str, request_data: Dict[str, Any]
    self, delivery_id: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a webhook delivery attempt record.
    Create a webhook delivery attempt record.


    Args:
    Args:
    delivery_id: Delivery ID
    delivery_id: Delivery ID
    request_data: Request data sent to the webhook
    request_data: Request data sent to the webhook


    Returns:
    Returns:
    Attempt record
    Attempt record


    Raises:
    Raises:
    ValueError: If delivery not found
    ValueError: If delivery not found
    """
    """
    if delivery_id not in self.deliveries:
    if delivery_id not in self.deliveries:
    raise ValueError(f"Delivery {delivery_id} not found")
    raise ValueError(f"Delivery {delivery_id} not found")


    delivery = self.deliveries[delivery_id]
    delivery = self.deliveries[delivery_id]
    attempt_id = str(uuid.uuid4())
    attempt_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    now = datetime.now().isoformat()


    attempt = {
    attempt = {
    "id": attempt_id,
    "id": attempt_id,
    "delivery_id": delivery_id,
    "delivery_id": delivery_id,
    "webhook_id": delivery["webhook_id"],
    "webhook_id": delivery["webhook_id"],
    "event_type": delivery["event_type"],
    "event_type": delivery["event_type"],
    "status": WebhookDeliveryStatus.PENDING.value,
    "status": WebhookDeliveryStatus.PENDING.value,
    "request_data": request_data,
    "request_data": request_data,
    "response_code": None,
    "response_code": None,
    "response_body": None,
    "response_body": None,
    "timestamp": now,
    "timestamp": now,
    "error_message": None,
    "error_message": None,
    }
    }


    self.attempts[attempt_id] = attempt
    self.attempts[attempt_id] = attempt


    # Add attempt to delivery
    # Add attempt to delivery
    delivery["attempts"].append(attempt_id)
    delivery["attempts"].append(attempt_id)
    self._save_delivery(delivery_id, delivery)
    self._save_delivery(delivery_id, delivery)


    # Save attempt
    # Save attempt
    self._save_attempt(attempt_id, attempt)
    self._save_attempt(attempt_id, attempt)


    logger.info(f"Created delivery attempt {attempt_id} for delivery {delivery_id}")
    logger.info(f"Created delivery attempt {attempt_id} for delivery {delivery_id}")
    return attempt
    return attempt


    def update_delivery_attempt(
    def update_delivery_attempt(
    self,
    self,
    attempt_id: str,
    attempt_id: str,
    status: WebhookDeliveryStatus,
    status: WebhookDeliveryStatus,
    response_code: Optional[int] = None,
    response_code: Optional[int] = None,
    response_body: Optional[str] = None,
    response_body: Optional[str] = None,
    error_message: Optional[str] = None,
    error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a webhook delivery attempt record.
    Update a webhook delivery attempt record.


    Args:
    Args:
    attempt_id: Attempt ID
    attempt_id: Attempt ID
    status: New status
    status: New status
    response_code: HTTP response code
    response_code: HTTP response code
    response_body: Response body
    response_body: Response body
    error_message: Error message
    error_message: Error message


    Returns:
    Returns:
    Updated attempt record
    Updated attempt record


    Raises:
    Raises:
    ValueError: If attempt not found
    ValueError: If attempt not found
    """
    """
    if attempt_id not in self.attempts:
    if attempt_id not in self.attempts:
    raise ValueError(f"Attempt {attempt_id} not found")
    raise ValueError(f"Attempt {attempt_id} not found")


    attempt = self.attempts[attempt_id]
    attempt = self.attempts[attempt_id]


    # Update attempt fields
    # Update attempt fields
    attempt["status"] = (
    attempt["status"] = (
    status.value if isinstance(status, WebhookDeliveryStatus) else status
    status.value if isinstance(status, WebhookDeliveryStatus) else status
    )
    )


    if response_code is not None:
    if response_code is not None:
    attempt["response_code"] = response_code
    attempt["response_code"] = response_code


    if response_body is not None:
    if response_body is not None:
    attempt["response_body"] = response_body
    attempt["response_body"] = response_body


    if error_message is not None:
    if error_message is not None:
    attempt["error_message"] = error_message
    attempt["error_message"] = error_message


    # Save attempt
    # Save attempt
    self._save_attempt(attempt_id, attempt)
    self._save_attempt(attempt_id, attempt)


    # Update delivery status if needed
    # Update delivery status if needed
    delivery_id = attempt["delivery_id"]
    delivery_id = attempt["delivery_id"]
    if delivery_id in self.deliveries:
    if delivery_id in self.deliveries:
    delivery = self.deliveries[delivery_id]
    delivery = self.deliveries[delivery_id]


    # Update delivery status based on the latest attempt
    # Update delivery status based on the latest attempt
    delivery["status"] = attempt["status"]
    delivery["status"] = attempt["status"]
    self._save_delivery(delivery_id, delivery)
    self._save_delivery(delivery_id, delivery)


    logger.info(f"Updated delivery attempt {attempt_id} with status {status}")
    logger.info(f"Updated delivery attempt {attempt_id} with status {status}")
    return attempt
    return attempt


    def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
    def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a delivery by ID.
    Get a delivery by ID.


    Args:
    Args:
    delivery_id: Delivery ID
    delivery_id: Delivery ID


    Returns:
    Returns:
    Delivery data or None if not found
    Delivery data or None if not found
    """
    """
    if delivery_id not in self.deliveries:
    if delivery_id not in self.deliveries:
    return None
    return None


    delivery = self.deliveries[delivery_id].copy()
    delivery = self.deliveries[delivery_id].copy()


    # Expand attempt IDs to full attempt data
    # Expand attempt IDs to full attempt data
    expanded_attempts = []
    expanded_attempts = []
    for attempt_id in delivery["attempts"]:
    for attempt_id in delivery["attempts"]:
    if attempt_id in self.attempts:
    if attempt_id in self.attempts:
    expanded_attempts.append(self.attempts[attempt_id])
    expanded_attempts.append(self.attempts[attempt_id])


    delivery["attempts"] = expanded_attempts
    delivery["attempts"] = expanded_attempts
    return delivery
    return delivery


    def get_deliveries(
    def get_deliveries(
    self,
    self,
    webhook_id: Optional[str] = None,
    webhook_id: Optional[str] = None,
    limit: int = 100,
    limit: int = 100,
    offset: int = 0,
    offset: int = 0,
    status: Optional[WebhookDeliveryStatus] = None,
    status: Optional[WebhookDeliveryStatus] = None,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get webhook deliveries.
    Get webhook deliveries.


    Args:
    Args:
    webhook_id: Optional webhook ID filter
    webhook_id: Optional webhook ID filter
    limit: Maximum number of deliveries to return
    limit: Maximum number of deliveries to return
    offset: Number of deliveries to skip
    offset: Number of deliveries to skip
    status: Optional status filter
    status: Optional status filter


    Returns:
    Returns:
    List of deliveries
    List of deliveries
    """
    """
    deliveries = []
    deliveries = []


    for delivery_id, delivery in self.deliveries.items():
    for delivery_id, delivery in self.deliveries.items():
    # Apply filters
    # Apply filters
    if webhook_id and delivery["webhook_id"] != webhook_id:
    if webhook_id and delivery["webhook_id"] != webhook_id:
    continue
    continue


    if status and delivery["status"] != (
    if status and delivery["status"] != (
    status.value if isinstance(status, WebhookDeliveryStatus) else status
    status.value if isinstance(status, WebhookDeliveryStatus) else status
    ):
    ):
    continue
    continue


    deliveries.append(self.get_delivery(delivery_id))
    deliveries.append(self.get_delivery(delivery_id))


    # Sort by timestamp (newest first)
    # Sort by timestamp (newest first)
    deliveries.sort(key=lambda d: d["timestamp"], reverse=True)
    deliveries.sort(key=lambda d: d["timestamp"], reverse=True)


    # Apply pagination
    # Apply pagination
    return deliveries[offset : offset + limit]
    return deliveries[offset : offset + limit]


    def count_deliveries(
    def count_deliveries(
    self,
    self,
    webhook_id: Optional[str] = None,
    webhook_id: Optional[str] = None,
    status: Optional[WebhookDeliveryStatus] = None,
    status: Optional[WebhookDeliveryStatus] = None,
    ) -> int:
    ) -> int:
    """
    """
    Count webhook deliveries.
    Count webhook deliveries.


    Args:
    Args:
    webhook_id: Optional webhook ID filter
    webhook_id: Optional webhook ID filter
    status: Optional status filter
    status: Optional status filter


    Returns:
    Returns:
    Number of matching deliveries
    Number of matching deliveries
    """
    """
    count = 0
    count = 0


    for delivery in self.deliveries.values():
    for delivery in self.deliveries.values():
    # Apply filters
    # Apply filters
    if webhook_id and delivery["webhook_id"] != webhook_id:
    if webhook_id and delivery["webhook_id"] != webhook_id:
    continue
    continue


    if status and delivery["status"] != (
    if status and delivery["status"] != (
    status.value if isinstance(status, WebhookDeliveryStatus) else status
    status.value if isinstance(status, WebhookDeliveryStatus) else status
    ):
    ):
    continue
    continue


    count += 1
    count += 1


    return count
    return count


    def sign_payload(self, webhook_id: str, payload: Dict[str, Any]) -> Optional[str]:
    def sign_payload(self, webhook_id: str, payload: Dict[str, Any]) -> Optional[str]:
    """
    """
    Sign a webhook payload using the webhook's secret.
    Sign a webhook payload using the webhook's secret.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    payload: Payload to sign
    payload: Payload to sign


    Returns:
    Returns:
    HMAC signature or None if no secret is set
    HMAC signature or None if no secret is set
    """
    """
    webhook = self.get_webhook(webhook_id)
    webhook = self.get_webhook(webhook_id)
    if not webhook or not webhook.get("secret_hash"):
    if not webhook or not webhook.get("secret_hash"):
    return None
    return None


    # The actual secret is never stored, but we can verify signatures
    # The actual secret is never stored, but we can verify signatures
    # using the hashed secret
    # using the hashed secret
    secret_hash = webhook["secret_hash"]
    secret_hash = webhook["secret_hash"]


    # Convert payload to string
    # Convert payload to string
    payload_str = json.dumps(payload, sort_keys=True)
    payload_str = json.dumps(payload, sort_keys=True)


    # Sign payload
    # Sign payload
    signature = hmac.new(
    signature = hmac.new(
    secret_hash.encode(), payload_str.encode(), hashlib.sha256
    secret_hash.encode(), payload_str.encode(), hashlib.sha256
    ).hexdigest()
    ).hexdigest()


    return signature
    return signature


    def _hash_secret(self, secret: str) -> str:
    def _hash_secret(self, secret: str) -> str:
    """
    """
    Hash a webhook secret.
    Hash a webhook secret.


    Args:
    Args:
    secret: Secret to hash
    secret: Secret to hash


    Returns:
    Returns:
    Hashed secret
    Hashed secret
    """
    """
    # In a real implementation, use a proper key derivation function
    # In a real implementation, use a proper key derivation function
    # For simplicity, we're using a simple hash here
    # For simplicity, we're using a simple hash here
    return hashlib.sha256(secret.encode()).hexdigest()
    return hashlib.sha256(secret.encode()).hexdigest()