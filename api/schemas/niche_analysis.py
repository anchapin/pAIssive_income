"""
Niche Analysis schemas for the API server.

This module provides Pydantic models for Niche Analysis API request and response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .bulk_operations import (
    BulkCreateRequest,
    BulkCreateResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    BulkOperationError,
    BulkOperationStats,
    BulkUpdateRequest,
    BulkUpdateResponse,
)


class ProblemResponse(BaseModel):
    """Problem response model."""

    id: str = Field(..., description="Problem ID")
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Problem description")
    severity: float = Field(..., description="Problem severity (0-1)")
    frequency: float = Field(..., description="Problem frequency (0-1)")
    impact: float = Field(..., description="Problem impact (0-1)")
    score: float = Field(..., description="Problem score (0-1)")


class MarketSegmentResponse(BaseModel):
    """Market segment response model."""

    id: str = Field(..., description="Market segment ID")
    name: str = Field(..., description="Market segment name")
    description: str = Field(..., description="Market segment description")
    size: str = Field(..., description="Market segment size")
    growth_rate: float = Field(..., description="Market segment growth rate")
    competition_level: str = Field(..., description="Market segment competition level")
    barriers_to_entry: str = Field(..., description="Market segment barriers to entry")
    target_audience: Dict[str, Any] = Field(..., description="Target audience information")


class OpportunityResponse(BaseModel):
    """Opportunity response model."""

    id: str = Field(..., description="Opportunity ID")
    title: str = Field(..., description="Opportunity title")
    description: str = Field(..., description="Opportunity description")
    score: float = Field(..., description="Opportunity score (0-1)")
    market_size: str = Field(..., description="Market size")
    competition: str = Field(..., description="Competition level")
    difficulty: str = Field(..., description="Implementation difficulty")
    potential_revenue: str = Field(..., description="Potential revenue")
    time_to_market: str = Field(..., description="Estimated time to market")


class NicheResponse(BaseModel):
    """Niche response model."""

    id: str = Field(..., description="Niche ID")
    name: str = Field(..., description="Niche name")
    description: str = Field(..., description="Niche description")
    market_segment: str = Field(..., description="Market segment")
    opportunity_score: float = Field(..., description="Opportunity score (0-1)")
    problems: List[ProblemResponse] = Field(..., description="Problems in the niche")
    opportunities: List[OpportunityResponse] = Field(..., description="Opportunities in the niche")
    created_at: datetime = Field(..., description="Creation timestamp")


class NicheAnalysisRequest(BaseModel):
    """Niche analysis request model."""

    segments: List[str] = Field(..., description="Market segments to analyze")
    force_refresh: bool = Field(False, description="Force refresh of analysis data")
    max_results: Optional[int] = Field(None, description="Maximum number of results to return")


class NicheAnalysisResponse(BaseModel):
    """Niche analysis response model."""

    analysis_id: str = Field(..., description="Analysis ID")
    segments: List[str] = Field(..., description="Analyzed market segments")
    niches: List[NicheResponse] = Field(..., description="Analyzed niches")
    created_at: datetime = Field(..., description="Creation timestamp")


# Bulk operation schemas for niches
class NicheCreateRequest(BaseModel):
    """Request model for creating a niche."""

    name: str = Field(..., description="Niche name")
    description: str = Field(..., description="Niche description")
    market_segment: str = Field(..., description="Market segment")
    problems: List[Dict[str, Any]] = Field(
        default_factory=list, description="Problems in the niche"
    )
    opportunities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Opportunities in the niche"
    )


class BulkNicheCreateRequest(BulkCreateRequest[NicheCreateRequest]):
    """Request model for bulk niche creation."""

    pass


class BulkNicheCreateResponse(BulkCreateResponse[NicheResponse]):
    """Response model for bulk niche creation."""

    pass


class NicheUpdateRequest(BaseModel):
    """Request model for updating a niche."""

    id: str = Field(..., description="Niche ID")
    name: Optional[str] = Field(None, description="Niche name")
    description: Optional[str] = Field(None, description="Niche description")
    market_segment: Optional[str] = Field(None, description="Market segment")
    problems: Optional[List[Dict[str, Any]]] = Field(None, description="Problems in the niche")
    opportunities: Optional[List[Dict[str, Any]]] = Field(
        None, description="Opportunities in the niche"
    )


class BulkNicheUpdateRequest(BulkUpdateRequest[NicheUpdateRequest]):
    """Request model for bulk niche updates."""

    pass


class BulkNicheUpdateResponse(BulkUpdateResponse[NicheResponse]):
    """Response model for bulk niche updates."""

    pass


class BulkNicheDeleteRequest(BulkDeleteRequest):
    """Request model for bulk niche deletion."""

    pass


class BulkNicheDeleteResponse(BulkDeleteResponse):
    """Response model for bulk niche deletion."""

    pass
