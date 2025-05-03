"""
Webhook repository for the API server.

This module provides a repository for storing and retrieving webhooks.
"""


import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..schemas.webhook import WebhookDeliveryStatus, WebhookEventType



# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WebhookRepository:
    """Repository for webhook storage and retrieval."""

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the webhook repository.

        Args:
            storage_path: Path where webhook data will be stored
        """
        self.storage_path = storage_path or "webhooks"
        os.makedirs(self.storage_path, exist_ok=True)

        # Create subdirectories
        self.webhooks_dir = os.path.join(self.storage_path, "webhooks")
        self.deliveries_dir = os.path.join(self.storage_path, "deliveries")
        self.attempts_dir = os.path.join(self.storage_path, "attempts")

        os.makedirs(self.webhooks_dir, exist_ok=True)
        os.makedirs(self.deliveries_dir, exist_ok=True)
        os.makedirs(self.attempts_dir, exist_ok=True)

        # Initialize data structures
        self.webhooks: Dict[str, Dict[str, Any]] = {}
        self.deliveries: Dict[str, Dict[str, Any]] = {}
        self.attempts: Dict[str, Dict[str, Any]] = {}

        # Initialize event to webhook mapping
        self.event_to_webhooks: Dict[str, Set[str]] = {}

        # Load data
        self._load_data()

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
        Save webhook data to storage.

        Args:
            webhook_id: Webhook ID
            webhook: Webhook data
        """
        webhook_file = os.path.join(self.webhooks_dir, f"{webhook_id}.json")
        with open(webhook_file, "w") as f:
            json.dump(webhook, f, indent=2)

    def _save_delivery(self, delivery_id: str, delivery: Dict[str, Any]) -> None:
        """
        Save delivery data to storage.

        Args:
            delivery_id: Delivery ID
            delivery: Delivery data
        """
        delivery_file = os.path.join(self.deliveries_dir, f"{delivery_id}.json")
        with open(delivery_file, "w") as f:
            json.dump(delivery, f, indent=2)

    def _save_attempt(self, attempt_id: str, attempt: Dict[str, Any]) -> None:
        """
        Save attempt data to storage.

        Args:
            attempt_id: Attempt ID
            attempt: Attempt data
        """
        attempt_file = os.path.join(self.attempts_dir, f"{attempt_id}.json")
        with open(attempt_file, "w") as f:
            json.dump(attempt, f, indent=2)

    def create_webhook(
        self,
        url: str,
        events: List[WebhookEventType],
        description: Optional[str] = None,
        active: bool = True,
        secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new webhook.

        Args:
            url: Webhook URL
            events: List of events to subscribe to
            description: Optional description
            active: Whether the webhook is active
            secret: Secret for signing payloads

        Returns:
            Created webhook
        """
        webhook_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Hash secret if provided
        secret_hash = None
        if secret:
            secret_hash = self._hash_secret(secret)

        webhook = {
            "id": webhook_id,
            "url": url,
            "description": description,
            "events": [
                event.value if isinstance(event, WebhookEventType) else event
                for event in events
            ],
            "active": active,
            "created_at": now,
            "updated_at": None,
            "secret_hash": secret_hash,
        }

        self.webhooks[webhook_id] = webhook

        # Update event to webhook mapping
        for event in webhook["events"]:
            if event not in self.event_to_webhooks:
                self.event_to_webhooks[event] = set()
            self.event_to_webhooks[event].add(webhook_id)

        # Save webhook
        self._save_webhook(webhook_id, webhook)

        logger.info(f"Created webhook {webhook_id} for URL {url}")
        return webhook

    def update_webhook(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
        events: Optional[List[WebhookEventType]] = None,
        active: Optional[bool] = None,
        secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing webhook.

        Args:
            webhook_id: Webhook ID
            url: Optional new URL
            description: Optional new description
            events: Optional new list of events
            active: Optional new active status
            secret: Optional new secret

        Returns:
            Updated webhook

        Raises:
            ValueError: If webhook not found
        """
        if webhook_id not in self.webhooks:
            raise ValueError(f"Webhook {webhook_id} not found")

        webhook = self.webhooks[webhook_id]
        now = datetime.now().isoformat()

        # Remove webhook from event mappings if events are changing
        if events is not None:
            for event in webhook["events"]:
                if event in self.event_to_webhooks:
                    self.event_to_webhooks[event].discard(webhook_id)

        # Update webhook fields
        if url is not None:
            webhook["url"] = url

        if description is not None:
            webhook["description"] = description

        if events is not None:
            webhook["events"] = [
                event.value if isinstance(event, WebhookEventType) else event
                for event in events
            ]

            # Update event to webhook mapping
            for event in webhook["events"]:
                if event not in self.event_to_webhooks:
                    self.event_to_webhooks[event] = set()
                self.event_to_webhooks[event].add(webhook_id)

        if active is not None:
            webhook["active"] = active

        if secret is not None:
            webhook["secret_hash"] = self._hash_secret(secret)

        webhook["updated_at"] = now

        # Save webhook
        self._save_webhook(webhook_id, webhook)

        logger.info(f"Updated webhook {webhook_id}")
        return webhook

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.

        Args:
            webhook_id: Webhook ID

        Returns:
            True if webhook was deleted, False otherwise
        """
        if webhook_id not in self.webhooks:
            return False

        webhook = self.webhooks[webhook_id]

        # Remove webhook from event mappings
        for event in webhook["events"]:
            if event in self.event_to_webhooks:
                self.event_to_webhooks[event].discard(webhook_id)

        # Remove webhook
        del self.webhooks[webhook_id]

        # Delete webhook file
        webhook_file = os.path.join(self.webhooks_dir, f"{webhook_id}.json")
        if os.path.exists(webhook_file):
            os.remove(webhook_file)

        logger.info(f"Deleted webhook {webhook_id}")
        return True

    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a webhook by ID.

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhook data or None if not found
        """
        return self.webhooks.get(webhook_id)

    def get_webhooks(self) -> List[Dict[str, Any]]:
        """
        Get all webhooks.

        Returns:
            List of webhooks
        """
        return list(self.webhooks.values())

    def get_webhooks_for_event(self, event: str) -> List[Dict[str, Any]]:
        """
        Get webhooks subscribed to a specific event.

        Args:
            event: Event type

        Returns:
            List of webhooks subscribed to the event
        """
        webhook_ids = self.event_to_webhooks.get(event, set())
        return [
            self.webhooks[wid]
            for wid in webhook_ids
            if wid in self.webhooks and self.webhooks[wid]["active"]
        ]

    def create_delivery(
        self, webhook_id: str, event_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a webhook delivery record.

        Args:
            webhook_id: Webhook ID
            event_type: Event type
            payload: Event payload

        Returns:
            Delivery record

        Raises:
            ValueError: If webhook not found
        """
        if webhook_id not in self.webhooks:
            raise ValueError(f"Webhook {webhook_id} not found")

        delivery_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        delivery = {
            "id": delivery_id,
            "webhook_id": webhook_id,
            "event_type": event_type,
            "status": WebhookDeliveryStatus.PENDING.value,
            "timestamp": now,
            "attempts": [],
        }

        self.deliveries[delivery_id] = delivery

        # Save delivery
        self._save_delivery(delivery_id, delivery)

        logger.info(
            f"Created delivery {delivery_id} for webhook {webhook_id} and event {event_type}"
        )
        return delivery

    def create_delivery_attempt(
        self, delivery_id: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a webhook delivery attempt record.

        Args:
            delivery_id: Delivery ID
            request_data: Request data sent to the webhook

        Returns:
            Attempt record

        Raises:
            ValueError: If delivery not found
        """
        if delivery_id not in self.deliveries:
            raise ValueError(f"Delivery {delivery_id} not found")

        delivery = self.deliveries[delivery_id]
        attempt_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        attempt = {
            "id": attempt_id,
            "delivery_id": delivery_id,
            "webhook_id": delivery["webhook_id"],
            "event_type": delivery["event_type"],
            "status": WebhookDeliveryStatus.PENDING.value,
            "request_data": request_data,
            "response_code": None,
            "response_body": None,
            "timestamp": now,
            "error_message": None,
        }

        self.attempts[attempt_id] = attempt

        # Add attempt to delivery
        delivery["attempts"].append(attempt_id)
        self._save_delivery(delivery_id, delivery)

        # Save attempt
        self._save_attempt(attempt_id, attempt)

        logger.info(f"Created delivery attempt {attempt_id} for delivery {delivery_id}")
        return attempt

    def update_delivery_attempt(
        self,
        attempt_id: str,
        status: WebhookDeliveryStatus,
        response_code: Optional[int] = None,
        response_body: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a webhook delivery attempt record.

        Args:
            attempt_id: Attempt ID
            status: New status
            response_code: HTTP response code
            response_body: Response body
            error_message: Error message

        Returns:
            Updated attempt record

        Raises:
            ValueError: If attempt not found
        """
        if attempt_id not in self.attempts:
            raise ValueError(f"Attempt {attempt_id} not found")

        attempt = self.attempts[attempt_id]

        # Update attempt fields
        attempt["status"] = (
            status.value if isinstance(status, WebhookDeliveryStatus) else status
        )

        if response_code is not None:
            attempt["response_code"] = response_code

        if response_body is not None:
            attempt["response_body"] = response_body

        if error_message is not None:
            attempt["error_message"] = error_message

        # Save attempt
        self._save_attempt(attempt_id, attempt)

        # Update delivery status if needed
        delivery_id = attempt["delivery_id"]
        if delivery_id in self.deliveries:
            delivery = self.deliveries[delivery_id]

            # Update delivery status based on the latest attempt
            delivery["status"] = attempt["status"]
            self._save_delivery(delivery_id, delivery)

        logger.info(f"Updated delivery attempt {attempt_id} with status {status}")
        return attempt

    def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a delivery by ID.

        Args:
            delivery_id: Delivery ID

        Returns:
            Delivery data or None if not found
        """
        if delivery_id not in self.deliveries:
            return None

        delivery = self.deliveries[delivery_id].copy()

        # Expand attempt IDs to full attempt data
        expanded_attempts = []
        for attempt_id in delivery["attempts"]:
            if attempt_id in self.attempts:
                expanded_attempts.append(self.attempts[attempt_id])

        delivery["attempts"] = expanded_attempts
        return delivery

    def get_deliveries(
        self,
        webhook_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        status: Optional[WebhookDeliveryStatus] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get webhook deliveries.

        Args:
            webhook_id: Optional webhook ID filter
            limit: Maximum number of deliveries to return
            offset: Number of deliveries to skip
            status: Optional status filter

        Returns:
            List of deliveries
        """
        deliveries = []

        for delivery_id, delivery in self.deliveries.items():
            # Apply filters
            if webhook_id and delivery["webhook_id"] != webhook_id:
                continue

            if status and delivery["status"] != (
                status.value if isinstance(status, WebhookDeliveryStatus) else status
            ):
                continue

            deliveries.append(self.get_delivery(delivery_id))

        # Sort by timestamp (newest first)
        deliveries.sort(key=lambda d: d["timestamp"], reverse=True)

        # Apply pagination
        return deliveries[offset : offset + limit]

    def count_deliveries(
        self,
        webhook_id: Optional[str] = None,
        status: Optional[WebhookDeliveryStatus] = None,
    ) -> int:
        """
        Count webhook deliveries.

        Args:
            webhook_id: Optional webhook ID filter
            status: Optional status filter

        Returns:
            Number of matching deliveries
        """
        count = 0

        for delivery in self.deliveries.values():
            # Apply filters
            if webhook_id and delivery["webhook_id"] != webhook_id:
                continue

            if status and delivery["status"] != (
                status.value if isinstance(status, WebhookDeliveryStatus) else status
            ):
                continue

            count += 1

        return count

    def sign_payload(self, webhook_id: str, payload: Dict[str, Any]) -> Optional[str]:
        """
        Sign a webhook payload using the webhook's secret.

        Args:
            webhook_id: Webhook ID
            payload: Payload to sign

        Returns:
            HMAC signature or None if no secret is set
        """
        webhook = self.get_webhook(webhook_id)
        if not webhook or not webhook.get("secret_hash"):
            return None

        # The actual secret is never stored, but we can verify signatures
        # using the hashed secret
        secret_hash = webhook["secret_hash"]

        # Convert payload to string
        payload_str = json.dumps(payload, sort_keys=True)

        # Sign payload
        signature = hmac.new(
            secret_hash.encode(), payload_str.encode(), hashlib.sha256
        ).hexdigest()

        return signature

    def _hash_secret(self, secret: str) -> str:
        """
        Hash a webhook secret.

        Args:
            secret: Secret to hash

        Returns:
            Hashed secret
        """
        # In a real implementation, use a proper key derivation function
        # For simplicity, we're using a simple hash here
        return hashlib.sha256(secret.encode()).hexdigest()