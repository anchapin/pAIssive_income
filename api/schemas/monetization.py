"""
Monetization schemas for the API server.

This module provides Pydantic models for Monetization API request and response validation.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class SubscriptionType(str, Enum):
    """Subscription type enumeration."""

    FREEMIUM = "freemium"
    TIERED = "tiered"
    USAGE_BASED = "usage_based"
    HYBRID = "hybrid"


class BillingPeriod(str, Enum):
    """Billing period enumeration."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    LIFETIME = "lifetime"


class FeatureResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Feature response model."""

    id: str = Field(..., description="Feature ID")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    category: Optional[str] = Field(None, description="Feature category")
    is_premium: bool = Field(..., description="Whether the feature is premium")


class PricingTierResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Pricing tier response model."""

    id: str = Field(..., description="Tier ID")
    name: str = Field(..., description="Tier name")
    description: str = Field(..., description="Tier description")
    price_monthly: float = Field(..., description="Monthly price")
    price_annual: Optional[float] = Field(None, description="Annual price")
    features: List[FeatureResponse] = Field(
        ..., description="Features included in the tier"
    )
    is_popular: bool = Field(False, description="Whether this is the popular tier")
    is_free: bool = Field(False, description="Whether this is a free tier")
    user_limit: Optional[int] = Field(None, description="Maximum number of users")
    storage_limit: Optional[int] = Field(None, description="Storage limit in GB")
    api_limit: Optional[int] = Field(None, description="API call limit")


class SubscriptionModelRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Subscription model request model."""

    name: str = Field(..., description="Model name")
    description: str = Field(..., description="Model description")
    solution_id: str = Field(..., description="Solution ID")
    model_type: SubscriptionType = Field(..., description="Subscription model type")
    features: List[Dict[str, Any]] = Field(..., description="Features to include")
    tiers: List[Dict[str, Any]] = Field(..., description="Pricing tiers")


class SubscriptionModelResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Subscription model response model."""

    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    description: str = Field(..., description="Model description")
    solution_id: str = Field(..., description="Solution ID")
    model_type: SubscriptionType = Field(..., description="Subscription model type")
    features: List[FeatureResponse] = Field(..., description="Features included")
    tiers: List[PricingTierResponse] = Field(..., description="Pricing tiers")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class RevenueProjectionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Revenue projection request model."""

    subscription_model_id: str = Field(..., description="Subscription model ID")
    initial_users: int = Field(..., description="Initial number of users")
    growth_rate: float = Field(..., description="Monthly growth rate (0-1)")
    churn_rate: float = Field(..., description="Monthly churn rate (0-1)")
    conversion_rate: float = Field(
        ..., description="Conversion rate from free to paid (0-1)"
    )
    time_period: int = Field(..., description="Projection time period in months")


class RevenueProjectionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Revenue projection response model."""

    id: str = Field(..., description="Projection ID")
    subscription_model_id: str = Field(..., description="Subscription model ID")
    initial_users: int = Field(..., description="Initial number of users")
    growth_rate: float = Field(..., description="Monthly growth rate (0-1)")
    churn_rate: float = Field(..., description="Monthly churn rate (0-1)")
    conversion_rate: float = Field(
        ..., description="Conversion rate from free to paid (0-1)"
    )
    time_period: int = Field(..., description="Projection time period in months")
    monthly_projections: List[Dict[str, Any]] = Field(
        ..., description="Monthly revenue projections"
    )
    total_revenue: float = Field(..., description="Total projected revenue")
    total_users: int = Field(..., description="Total projected users")
    created_at: datetime = Field(..., description="Creation timestamp")
