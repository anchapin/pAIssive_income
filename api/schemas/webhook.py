"""
Webhook schemas for the API server.

This module provides Pydantic schemas for webhook data.
"""

import enum
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class WebhookEventType(str, enum.Enum):
    """Types of webhook events."""
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Niche analysis events
    NICHE_ANALYSIS_STARTED = "niche_analysis.started"
    NICHE_ANALYSIS_COMPLETED = "niche_analysis.completed"
    NICHE_ANALYSIS_FAILED = "niche_analysis.failed"
    
    # Monetization events
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_FAILED = "payment.failed"
    REFUND_PROCESSED = "refund.processed"
    
    # Marketing events
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_UPDATED = "campaign.updated"
    CAMPAIGN_DELETED = "campaign.deleted"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_COMPLETED = "campaign.completed"
    
    # AI model events
    MODEL_INFERENCE_STARTED = "model_inference.started"
    MODEL_INFERENCE_COMPLETED = "model_inference.completed"
    MODEL_INFERENCE_FAILED = "model_inference.failed"
    MODEL_DOWNLOADED = "model.downloaded"
    
    # Agent team events
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"


class WebhookDeliveryStatus(str, enum.Enum):
    """Status of webhook delivery."""
    
    PENDING = "pending"      # Delivery is pending
    SUCCESS = "success"      # Delivery was successful (2xx response)
    FAILED = "failed"        # Delivery failed
    RETRYING = "retrying"    # Delivery failed but will be retried


class WebhookCreate(BaseModel):
    """Data required to create a webhook."""
    
    url: HttpUrl = Field(..., description="URL to send webhook events to")
    events: List[WebhookEventType] = Field(..., description="List of events to subscribe to")
    description: Optional[str] = Field(None, description="Optional description of the webhook")
    active: bool = Field(True, description="Whether the webhook is active")
    secret: Optional[str] = Field(None, description="Secret used to sign the webhook payload")


class WebhookUpdate(BaseModel):
    """Data that can be updated for a webhook."""
    
    url: Optional[HttpUrl] = Field(None, description="URL to send webhook events to")
    events: Optional[List[WebhookEventType]] = Field(None, description="List of events to subscribe to")
    description: Optional[str] = Field(None, description="Description of the webhook")
    active: Optional[bool] = Field(None, description="Whether the webhook is active")
    secret: Optional[str] = Field(None, description="Secret used to sign the webhook payload")


class WebhookResponse(BaseModel):
    """Response model for a webhook."""
    
    id: str = Field(..., description="Unique webhook ID")
    url: HttpUrl = Field(..., description="URL to send webhook events to")
    events: List[str] = Field(..., description="List of events subscribed to")
    description: Optional[str] = Field(None, description="Description of the webhook")
    active: bool = Field(..., description="Whether the webhook is active")
    created_at: str = Field(..., description="Timestamp when the webhook was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the webhook was last updated")
    secret_set: bool = Field(..., description="Whether a secret is set for this webhook")


class WebhookList(BaseModel):
    """Response model for a list of webhooks."""
    
    webhooks: List[WebhookResponse] = Field(..., description="List of webhooks")


class WebhookDeliveryAttempt(BaseModel):
    """Details of a webhook delivery attempt."""
    
    id: str = Field(..., description="Unique attempt ID")
    webhook_id: str = Field(..., description="ID of the webhook")
    delivery_id: str = Field(..., description="ID of the delivery")
    event_type: str = Field(..., description="Type of event")
    status: str = Field(..., description="Status of the delivery attempt")
    timestamp: str = Field(..., description="Timestamp of the delivery attempt")
    request_data: Dict[str, Any] = Field(..., description="Data sent in the webhook request")
    response_code: Optional[int] = Field(None, description="HTTP response code")
    response_body: Optional[str] = Field(None, description="Response body")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")


class WebhookDeliveryResponse(BaseModel):
    """Response model for a webhook delivery."""
    
    id: str = Field(..., description="Unique delivery ID")
    webhook_id: str = Field(..., description="ID of the webhook")
    event_type: str = Field(..., description="Type of event")
    status: str = Field(..., description="Status of the delivery")
    timestamp: str = Field(..., description="Timestamp of the delivery")
    attempts: List[WebhookDeliveryAttempt] = Field(..., description="Delivery attempts")


class WebhookDeliveryList(BaseModel):
    """Response model for a list of webhook deliveries."""
    
    deliveries: List[WebhookDeliveryResponse] = Field(..., description="List of deliveries")
    total: int = Field(..., description="Total number of deliveries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of deliveries per page")