"""Pydantic schemas for the niche_analysis package."""

from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

# Enums for categorical values
MarketSize = Literal["large", "medium", "small", "unknown"]
GrowthRate = Literal["high", "medium", "low", "unknown"]
CompetitionLevel = Literal["high", "medium", "low", "unknown"]
BarrierLevel = Literal["high", "medium", "low", "unknown"]
TechAdoption = Literal["high", "medium", "low", "unknown"]
Severity = Literal["high", "medium", "low"]
ImpactLevel = Literal["high", "medium", "low"]
MaturityLevel = Literal["emerging", "growing", "mature"]
Likelihood = Literal["high", "medium", "low"]
Timeframe = Literal["short-term", "medium-term", "long-term"]
SegmentSize = Literal["large", "medium", "small"]
PriorityLevel = Literal["high", "medium", "low"]


class MarketSegmentAnalysis(BaseModel):
    """Market segment analysis result."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    market_size: MarketSize
    growth_rate: GrowthRate
    competition: CompetitionLevel
    barriers_to_entry: BarrierLevel
    technological_adoption: TechAdoption
    potential_niches: List[str]
    target_users: List[str]


class CompetitorProfile(BaseModel):
    """Profile of a competitor in a niche."""
    name: str
    description: str
    estimated_market_share: Optional[float] = None
    key_strengths: List[str]
    key_weaknesses: List[str]
    pricing_info: Optional[str] = None


class CompetitionAnalysis(BaseModel):
    """Analysis of competition in a niche."""
    niche: str
    competitor_count: int
    top_competitors: List[CompetitorProfile]
    market_saturation: CompetitionLevel
    entry_barriers: BarrierLevel
    differentiation_opportunities: List[str]


class TrendProfile(BaseModel):
    """Profile of a current market trend."""
    name: str
    description: str
    impact_level: ImpactLevel
    maturity_level: MaturityLevel


class PredictionProfile(BaseModel):
    """Profile of a future market prediction."""
    name: str
    description: str
    likelihood: Likelihood
    timeframe: Timeframe


class TrendAnalysis(BaseModel):
    """Analysis of trends for a market segment."""
    segment: str
    current_trends: List[TrendProfile]
    future_predictions: List[PredictionProfile]
    technological_shifts: List[str]


class UserSegmentProfile(BaseModel):
    """Profile of a user segment in a niche."""
    name: str
    description: str
    segment_size: SegmentSize
    priority_level: PriorityLevel


class TargetUserAnalysis(BaseModel):
    """Analysis of target users for a niche."""
    niche: str
    user_segments: List[UserSegmentProfile]
    demographics: Dict[str, Any]
    psychographics: Dict[str, Any]
    pain_points: List[str]
    goals: List[str]
    buying_behavior: Dict[str, Any]


class Problem(BaseModel):
    """A problem or pain point in a niche."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    consequences: List[str]
    severity: Severity
    current_solutions: Dict[str, str]
    solution_gaps: Dict[str, str]
    timestamp: datetime


class ProblemSeverityAnalysis(BaseModel):
    """Detailed analysis of a problem's severity."""
    severity: Severity
    analysis: Dict[str, str]
    potential_impact_of_solution: str
    user_willingness_to_pay: str


class OpportunityScore(BaseModel):
    """Scoring result for a niche opportunity."""
    id: UUID = Field(default_factory=uuid4)
    niche: str
    overall_score: float
    factor_scores: Dict[str, float]
    analysis: Dict[str, List[str]]
    recommendations: List[str]
    timestamp: datetime

    @field_validator("overall_score")
    @classmethod
    def score_between_0_and_1(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("overall_score must be between 0 and 1")
        return v


class OpportunityComparison(BaseModel):
    """Comparison of multiple opportunities."""
    ranked_opportunities: List[OpportunityScore]
    top_recommendation: OpportunityScore
    comparison_factors: Dict[str, Any]
    recommendations: List[str]