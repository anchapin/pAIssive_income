"""webhook_service - Module for api/services.webhook_service."""

# Standard library imports
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Third-party imports
import requests

from api.services.webhook_security import WebhookSignatureVerifier

# Local imports
from common_utils.logging import get_logger

logger = get_logger(__name__)


class WebhookService:
    """Service for managing and delivering webhooks."""

    def __init__(self, db=None):
        """
        Initialize the webhook service.

        Args:
            db: Database connection object. If None, a default connection will be used.

        """
        self.db = db
        self.signature_verifier = WebhookSignatureVerifier()

    def register_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new webhook.

        Args:
            webhook_data: Dictionary containing webhook configuration
                - url: Webhook destination URL
                - events: List of event types to subscribe to
                - description: Optional description
                - headers: Optional custom headers
                - is_active: Whether the webhook is active

        Returns:
            Dictionary containing the created webhook details

        """
        # Validate required fields
        if "url" not in webhook_data:
            raise ValueError("URL")

        # Generate a webhook ID and secret
        webhook_id = f"webhook-{uuid.uuid4().hex[:8]}"
        webhook_secret = f"whsec_{uuid.uuid4().hex}"

        # Add metadata
        webhook = {
            **webhook_data,
            "id": webhook_id,
            "secret": webhook_secret,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Store in database
        if self.db:
            stored_webhook = self.db.add_webhook(webhook)
            return stored_webhook

        return webhook

    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a webhook by ID.

        Args:
            webhook_id: The ID of the webhook to retrieve

        Returns:
            Dictionary containing webhook details or None if not found

        """
        if self.db:
            return self.db.get_webhook(webhook_id)
        return None

    def list_webhooks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all webhooks, optionally filtered.

        Args:
            filters: Optional dictionary of filters

        Returns:
            List of webhook dictionaries

        """
        if self.db:
            return self.db.list_webhooks(filters)
        return []

    def update_webhook(self, webhook_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a webhook.

        Args:
            webhook_id: The ID of the webhook to update
            update_data: Dictionary containing fields to update

        Returns:
            Updated webhook dictionary or None if not found

        """
        if self.db:
            return self.db.update_webhook(webhook_id, update_data)
        return None

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.

        Args:
            webhook_id: The ID of the webhook to delete

        Returns:
            True if deleted successfully, False otherwise

        """
        if self.db:
            return self.db.delete_webhook(webhook_id)
        return False

    def deliver_webhook(self, webhook: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """
        Deliver an event to a webhook endpoint.

        Args:
            webhook: Webhook configuration dictionary
            event_data: Event data to deliver

        Returns:
            True if delivered successfully, False otherwise

        """
        try:
            # Prepare the payload
            payload = json.dumps(event_data)

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "pAIssive-income-webhook/1.0",
                "X-Webhook-ID": webhook["id"],
            }

            # Add custom headers if provided
            if webhook.get("headers"):
                headers.update(webhook["headers"])

            # Add signature if secret is available
            if webhook.get("secret"):
                signature = self.signature_verifier.create_signature(
                    payload, webhook["secret"]
                )
                headers["X-Webhook-Signature"] = signature

            # Send the request
            response = requests.post(
                webhook["url"],
                data=payload,
                headers=headers,
                timeout=10,  # 10 second timeout
            )

            # Log the result
            logger.info(
                f"Webhook delivery to {webhook['url']} completed with status {response.status_code}"
            )

            # Check if status code is 2xx
            http_ok_min = 200
            http_ok_max = 300
            is_success = http_ok_min <= response.status_code < http_ok_max
        except Exception:
            logger.exception("Webhook delivery failed")
            return False

        return is_success

    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> int:
        """
        Process an event and deliver to all matching webhooks.

        Args:
            event_type: Type of event (e.g., "user.created")
            event_data: Event data

        Returns:
            Number of webhooks successfully delivered

        """
        if not self.db:
            return 0

        # Find all active webhooks subscribed to this event
        webhooks = self.db.find_webhooks_by_event(event_type, active_only=True)

        # Prepare the full event payload
        full_event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Deliver to each webhook
        success_count = 0
        for webhook in webhooks:
            if self.deliver_webhook(webhook, full_event):
                success_count += 1

        return success_count
