"""
"""
API schema definitions.
API schema definitions.


This module contains Pydantic models for API requests and responses.
This module contains Pydantic models for API requests and responses.
"""
"""


# Import bulk operation schemas
# Import bulk operation schemas
from .bulk_operations import (BulkCreateRequest, BulkCreateResponse,
from .bulk_operations import (BulkCreateRequest, BulkCreateResponse,
BulkDeleteRequest, BulkDeleteResponse,
BulkDeleteRequest, BulkDeleteResponse,
BulkOperationError, BulkOperationStats,
BulkOperationError, BulkOperationStats,
BulkResponse, BulkUpdateRequest,
BulkResponse, BulkUpdateRequest,
BulkUpdateResponse)
BulkUpdateResponse)
# Re-export schemas for easier imports
# Re-export schemas for easier imports
from .webhook import (WebhookDeliveryAttempt, WebhookDeliveryList,
from .webhook import (WebhookDeliveryAttempt, WebhookDeliveryList,
WebhookDeliveryResponse, WebhookDeliveryStatus,
WebhookDeliveryResponse, WebhookDeliveryStatus,
WebhookEventType, WebhookList, WebhookRequest,
WebhookEventType, WebhookList, WebhookRequest,
WebhookResponse, WebhookUpdate)
WebhookResponse, WebhookUpdate)

