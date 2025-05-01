"""
Marketing schemas for the API server.

This module provides Pydantic models for marketing-related data.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MarketingStrategyRequest(BaseModel):
    """Request model for creating a marketing strategy."""
    niche_id: str = Field(..., description="ID of the target niche")
    target_audience: Dict[str, Any] = Field(..., description="Target audience details")
    channels: List[str] = Field(..., description="List of marketing channels")
    content_types: List[str] = Field(..., description="List of content types")
    kpis: List[str] = Field(..., description="List of KPIs to track")

class MarketingStrategyResponse(BaseModel):
    """Response model for a marketing strategy."""
    id: str = Field(..., description="Strategy ID")
    niche_id: str = Field(..., description="ID of the target niche")
    target_audience: Dict[str, Any] = Field(..., description="Target audience details")
    channels: List[str] = Field(..., description="List of marketing channels")
    content_types: List[str] = Field(..., description="List of content types")
    kpis: List[str] = Field(..., description="List of KPIs to track")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    content_type: str = Field(..., description="Type of content to generate")
    topic: str = Field(..., description="Content topic")
    target_audience: str = Field(..., description="Target audience")
    tone: str = Field(..., description="Content tone")
    length: str = Field(..., description="Content length")

class ContentGenerationResponse(BaseModel):
    """Response model for content generation task."""
    task_id: str = Field(..., description="Task ID")
    status_url: str = Field(..., description="URL to check task status")

class PersonaResponse(BaseModel):
    """Response model for a user persona."""
    id: str = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    demographics: Dict[str, Any] = Field(..., description="Demographic information")

class ChannelResponse(BaseModel):
    """Response model for a marketing channel."""
    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    platforms: List[str] = Field(..., description="List of platforms")
    content_types: List[str] = Field(..., description="Supported content types")

class CampaignGoals(BaseModel):
    """Model for campaign goals."""
    metrics: List[str] = Field(..., description="Metrics to track")
    targets: Dict[str, Any] = Field(..., description="Target values for metrics")

class MarketingCampaignRequest(BaseModel):
    """Request model for creating a marketing campaign."""
    name: str = Field(..., description="Campaign name")
    description: str = Field(..., description="Campaign description")
    strategy_id: str = Field(..., description="Marketing strategy ID")
    start_date: str = Field(..., description="Campaign start date")
    end_date: str = Field(..., description="Campaign end date")
    budget: float = Field(..., description="Campaign budget")
    channels: List[str] = Field(..., description="Marketing channels")
    target_audience: Dict[str, Any] = Field(..., description="Target audience details")
    goals: CampaignGoals = Field(..., description="Campaign goals")

class MarketingCampaignResponse(BaseModel):
    """Response model for a marketing campaign."""
    id: str = Field(..., description="Campaign ID")
    name: Optional[str] = Field(None, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    strategy_id: Optional[str] = Field(None, description="Marketing strategy ID")
    status: str = Field(..., description="Campaign status")
    budget: Optional[float] = Field(None, description="Campaign budget")
    channels: Optional[List[str]] = Field(None, description="Marketing channels")
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience details")
    goals: Optional[CampaignGoals] = Field(None, description="Campaign goals")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Campaign metrics")
    activation_date: Optional[str] = Field(None, description="Campaign activation date")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")