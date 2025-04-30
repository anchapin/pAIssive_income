"""
API schema definitions.

This module contains Pydantic models for API requests and responses.
"""

# Re-export schemas for easier imports
from .webhook import (
    WebhookEventType,
    WebhookDeliveryStatus,
    WebhookRequest,
    WebhookUpdate,
    WebhookResponse,
    WebhookList,
    WebhookDeliveryAttempt,
    WebhookDeliveryResponse,
    WebhookDeliveryList
)

# Import bulk operation schemas
from .bulk_operations import (
    BulkOperationStats,
    BulkOperationError,
    BulkResponse,
    BulkCreateRequest,
    BulkCreateResponse,
    BulkUpdateRequest,
    BulkUpdateResponse,
    BulkDeleteRequest,
    BulkDeleteResponse
)
