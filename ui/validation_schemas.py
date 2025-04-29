"""
Validation schemas for the UI module.

This module provides Pydantic models for validating user input in the UI.
These schemas ensure that data received through web forms and API endpoints
is properly validated before being processed.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID


class NicheAnalysisRequest(BaseModel):
    """Schema for niche analysis request validation."""
    market_segments: List[str] = Field(
        ...,  # This makes the field required
        description="List of market segment IDs to analyze",
        min_length=1  # At least one market segment must be selected
    )

    model_config = ConfigDict(
        extra="forbid"  # Forbid extra fields to prevent unexpected input
    )


class DeveloperSolutionRequest(BaseModel):
    """Schema for solution development request validation."""
    niche_id: str = Field(
        ...,
        description="ID of the niche to develop a solution for",
        min_length=1
    )

    model_config = ConfigDict(
        extra="forbid"
    )
    
    @field_validator('niche_id')
    @classmethod
    def validate_niche_id(cls, v: str) -> str:
        """Validate that niche_id is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Niche ID cannot be empty")
        return v


class MonetizationStrategyRequest(BaseModel):
    """Schema for monetization strategy request validation."""
    solution_id: str = Field(
        ...,
        description="ID of the solution to create a monetization strategy for",
        min_length=1
    )

    model_config = ConfigDict(
        extra="forbid"
    )
    
    @field_validator('solution_id')
    @classmethod
    def validate_solution_id(cls, v: str) -> str:
        """Validate that solution_id is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Solution ID cannot be empty")
        return v


class MarketingCampaignRequest(BaseModel):
    """Schema for marketing campaign request validation."""
    solution_id: str = Field(
        ...,
        description="ID of the solution to create a marketing campaign for",
        min_length=1
    )

    model_config = ConfigDict(
        extra="forbid"
    )
    
    @field_validator('solution_id')
    @classmethod
    def validate_solution_id(cls, v: str) -> str:
        """Validate that solution_id is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Solution ID cannot be empty")
        return v


class TaskRequest(BaseModel):
    """Schema for task-related requests."""
    task_id: UUID = Field(
        ...,
        description="ID of the task to operate on"
    )

    model_config = ConfigDict(
        extra="forbid"
    )


class ApiQueryParams(BaseModel):
    """Schema for common API query parameters."""
    limit: Optional[int] = Field(
        default=100,
        description="Maximum number of items to return",
        ge=1,
        le=1000
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of items to skip",
        ge=0
    )
    sort_by: Optional[str] = Field(
        default=None,
        description="Field to sort by"
    )
    sort_order: Optional[str] = Field(
        default="asc",
        description="Sort order (asc or desc)",
        pattern="^(asc|desc)$"
    )
    
    model_config = ConfigDict(
        extra="ignore"  # Ignore extra query parameters
    )