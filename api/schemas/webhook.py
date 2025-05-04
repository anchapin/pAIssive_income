"""
Webhook schemas for the API server.
"""


from datetime import datetime
from enum import Enum
from ipaddress import ip_network
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


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

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"


    class WebhookRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    url: HttpUrl = Field(..., description="Webhook URL")
    events: List[WebhookEventType] = Field(..., description="Events to subscribe to")
    description: Optional[str] = Field(None, description="Webhook description")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    is_active: bool = Field(True, description="Whether the webhook is active")

    @field_validator("events")
    def events_not_empty(cls, v):
    """Validate that events list is not empty."""
    if not v:
    raise ValueError(
    "events list cannot be empty, at least one event type must be specified"
    )
    return v


    class WebhookUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    url: Optional[HttpUrl] = Field(None, description="New webhook URL")
    events: Optional[List[WebhookEventType]] = Field(
    None, description="New list of events to subscribe to"
    )
    description: Optional[str] = Field(None, description="New webhook description")
    headers: Optional[Dict[str, str]] = Field(None, description="New custom headers")
    is_active: Optional[bool] = Field(None, description="New active status")

    @field_validator("events")
    def events_not_empty_if_provided(cls, v):
    """Validate that events list is not empty if provided."""
    if v is not None and not v:
    raise ValueError(
    "events list cannot be empty, at least one event type must be specified"
    )
    return v


    class WebhookResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(..., description="Webhook ID")
    url: HttpUrl = Field(..., description="Webhook URL")
    events: List[WebhookEventType] = Field(..., description="Events subscribed to")
    description: Optional[str] = Field(None, description="Webhook description")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    is_active: bool = Field(True, description="Whether the webhook is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_called_at: Optional[datetime] = Field(
    None, description="Last delivery timestamp"
    )
    secret: str = Field(..., description="Webhook secret for signature verification")

    @field_validator("events")
    def events_not_empty(cls, v):
    """Validate that events list is not empty."""
    if not v:
    raise ValueError(
    "events list cannot be empty, at least one event type must be specified"
    )
    return v


    class WebhookList(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    items: List[WebhookResponse] = Field(..., description="List of webhooks")
    total: int = Field(..., description="Total number of webhooks")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of webhooks per page")
    pages: int = Field(..., description="Total number of pages")


    class WebhookDeliveryAttempt(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

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
    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(..., description="Delivery ID")
    webhook_id: str = Field(..., description="Webhook ID")
    status: WebhookDeliveryStatus = Field(..., description="Overall delivery status")
    timestamp: datetime = Field(..., description="Timestamp of the delivery")
    attempts: List[WebhookDeliveryAttempt] = Field(..., description="Delivery attempts")


    class WebhookDeliveryList(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Response model for listing webhook deliveries."""

    items: List[WebhookDeliveryResponse] = Field(..., description="List of deliveries")
    total: int = Field(..., description="Total number of deliveries")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of deliveries per page")
    pages: int = Field(..., description="Total number of pages")


    class IPAllowlistConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    allowed_ips: List[str] = Field(
    ..., description="List of allowed IP addresses or CIDR ranges"
    )
    enabled: bool = Field(True, description="Whether IP allowlisting is enabled")

    @field_validator("allowed_ips")
    def validate_ip_addresses(cls, v):
    """Validate IP addresses and CIDR ranges."""
    for ip in v:
    try:
    ip_network(ip)
except ValueError:
    raise ValueError(f"Invalid IP address or CIDR range: {ip}")
    return v


    class IPAllowlistResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    webhook_id: str = Field(..., description="Webhook ID")
    allowed_ips: List[str] = Field(
    ..., description="List of allowed IP addresses or CIDR ranges"
    )
    enabled: bool = Field(..., description="Whether IP allowlisting is enabled")
    updated_at: datetime = Field(..., description="Last update timestamp")


    class SecretRotationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    webhook_id: str = Field(..., description="Webhook ID")
    new_secret: str = Field(..., description="New webhook secret")
    old_secret_expiry: datetime = Field(
    ..., description="Expiration timestamp for the old secret"
    )


    class RateLimitConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    per_minute: int = Field(
    ..., ge=1, le=1000, description="Maximum requests per minute"
    )
    per_hour: int = Field(..., ge=1, le=10000, description="Maximum requests per hour")

    @field_validator("per_hour")
    def validate_hourly_limit(cls, v, values):
    """Validate that hourly limit is greater than per-minute limit * 60."""
    if "per_minute" in values and v < values["per_minute"] * 60:
    raise ValueError("Hourly limit must be greater than per-minute limit * 60")
    return v


    class RateLimitResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    webhook_id: str = Field(..., description="Webhook ID")
    rate_limits: RateLimitConfig = Field(..., description="Rate limit configuration")
    updated_at: datetime = Field(..., description="Last update timestamp")