"""
Webhook schemas for the API server.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class WebhookEventType(str, Enum):
    """Types of webhook events."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    STRATEGY_CREATED = "strategy.created"
    STRATEGY_UPDATED = "strategy.updated"
    STRATEGY_DELETED = "strategy.deleted"
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_UPDATED = "campaign.updated"
    CAMPAIGN_DELETED = "campaign.deleted"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    NICHE_ANALYSIS_STARTED = "niche_analysis.started"
    NICHE_ANALYSIS_COMPLETED = "niche_analysis.completed"
    NICHE_ANALYSIS_FAILED = "niche_analysis.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    PAYMENT_RECEIVED = "payment.received"

class WebhookDeliveryStatus(str, Enum):
    """Status of a webhook delivery attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"

class WebhookRequest(BaseModel):
    """Request model for registering a webhook."""
    url: HttpUrl = Field(..., description="Webhook URL")
    events: List[WebhookEventType] = Field(..., description="Events to subscribe to")
    description: Optional[str] = Field(None, description="Webhook description")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    is_active: bool = Field(True, description="Whether the webhook is active")

class WebhookUpdate(BaseModel):
    """Request model for updating a webhook."""
    url: Optional[HttpUrl] = Field(None, description="New webhook URL")
    events: Optional[List[WebhookEventType]] = Field(None, description="New list of events to subscribe to")
    description: Optional[str] = Field(None, description="New webhook description")
    headers: Optional[Dict[str, str]] = Field(None, description="New custom headers")
    is_active: Optional[bool] = Field(None, description="New active status")

class WebhookResponse(BaseModel):
    """Response model for webhook operations."""
    id: str = Field(..., description="Webhook ID")
    url: HttpUrl = Field(..., description="Webhook URL")
    events: List[WebhookEventType] = Field(..., description="Events subscribed to")
    description: Optional[str] = Field(None, description="Webhook description")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    is_active: bool = Field(True, description="Whether the webhook is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_called_at: Optional[datetime] = Field(None, description="Last delivery timestamp")
    secret: str = Field(..., description="Webhook secret for signature verification")

class WebhookList(BaseModel):
    """Response model for listing webhooks."""
    items: List[WebhookResponse] = Field(..., description="List of webhooks")
    total: int = Field(..., description="Total number of webhooks")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of webhooks per page")
    pages: int = Field(..., description="Total number of pages")

class WebhookDeliveryAttempt(BaseModel):
    """Model for a webhook delivery attempt."""
    id: str = Field(..., description="Attempt ID")
    webhook_id: str = Field(..., description="Webhook ID")
    event_type: WebhookEventType = Field(..., description="Event type")
    status: WebhookDeliveryStatus = Field(..., description="Delivery status")
    request_url: HttpUrl = Field(..., description="Request URL")
    request_headers: Dict[str, str] = Field(..., description="Request headers")
    request_body: Dict[str, Any] = Field(..., description="Request body")
    response_code: Optional[int] = Field(None, description="Response status code")
    response_body: Optional[str] = Field(None, description="Response body")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(..., description="Timestamp of the attempt")
    retries: int = Field(0, description="Number of retry attempts")
    next_retry: Optional[datetime] = Field(None, description="Next retry timestamp")

class WebhookDeliveryResponse(BaseModel):
    """Response model for webhook delivery."""
    id: str = Field(..., description="Delivery ID")
    webhook_id: str = Field(..., description="Webhook ID")
    status: WebhookDeliveryStatus = Field(..., description="Overall delivery status")
    timestamp: datetime = Field(..., description="Timestamp of the delivery")
    attempts: List[WebhookDeliveryAttempt] = Field(..., description="Delivery attempts")

class WebhookDeliveryList(BaseModel):
    """Response model for listing webhook deliveries."""
    items: List[WebhookDeliveryResponse] = Field(..., description="List of deliveries")
    total: int = Field(..., description="Total number of deliveries")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of deliveries per page")
    pages: int = Field(..., description="Total number of pages")