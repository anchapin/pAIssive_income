"""
API schema definitions.

This module contains Pydantic models for API requests and responses.
"""

# Import bulk operation schemas
from .bulk_operations import (
    BulkCreateRequest,
    BulkCreateResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    BulkOperationError,
    BulkOperationStats,
    BulkResponse,
    BulkUpdateRequest,
    BulkUpdateResponse,
)

# Re-export schemas for easier imports
from .webhook import (
    WebhookDeliveryAttempt,
    WebhookDeliveryList,
    WebhookDeliveryResponse,
    WebhookDeliveryStatus,
    WebhookEventType,
    WebhookList,
    WebhookRequest,
    WebhookResponse,
    WebhookUpdate,
)
