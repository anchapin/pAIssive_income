"""
Pydantic schemas for the niche analysis module.

This module provides Pydantic models for data validation in the niche analysis module.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CurrentSolutionSchema(BaseModel):
    """Pydantic model for current solutions to a problem."""

    manual_processes: str = Field(
        ..., description="Description of manual processes used to solve the problem"
    )
    general_tools: str = Field(
        ..., description="Description of general-purpose tools used to solve the problem"
    )
    outsourcing: str = Field(
        ..., description="Description of outsourcing approach used to solve the problem"
    )


class SolutionGapSchema(BaseModel):
    """Pydantic model for gaps in current solutions to a problem."""

    automation: str = Field(..., description="Description of automation gap")
    specialization: str = Field(..., description="Description of specialization gap")
    integration: str = Field(..., description="Description of integration gap")


class ProblemSchema(BaseModel):
    """Pydantic model for a problem identified in a niche."""

    id: str = Field(..., description="Unique identifier for the problem")
    name: str = Field(..., description="Name of the problem")
    description: str = Field(..., description="Description of the problem")
    consequences: List[str] = Field(..., description="List of consequences of the problem")
    severity: str = Field(..., description="Severity of the problem (high, medium, low)")
    current_solutions: CurrentSolutionSchema = Field(
        ..., description="Current solutions to the problem"
    )
    solution_gaps: SolutionGapSchema = Field(..., description="Gaps in current solutions")
    timestamp: str = Field(..., description="Timestamp of when the problem was identified")


class SeverityAnalysisSchema(BaseModel):
    """Pydantic model for severity analysis of a problem."""

    impact_on_users: str = Field(..., description="Impact on users")
    frequency: str = Field(..., description="Frequency of occurrence")
    emotional_response: str = Field(..., description="Emotional response to the problem")
    business_impact: str = Field(..., description="Impact on business")
    urgency: str = Field(..., description="Urgency of solving the problem")


class ProblemSeverityAnalysisSchema(BaseModel):
    """Pydantic model for problem severity analysis."""

    id: str = Field(..., description="Unique identifier for the analysis")
    problem_id: str = Field(..., description="ID of the problem being analyzed")
    severity: str = Field(..., description="Severity level (high, medium, low)")
    analysis: SeverityAnalysisSchema = Field(..., description="Detailed severity analysis")
    potential_impact_of_solution: str = Field(
        ..., description="Potential impact of solving the problem"
    )
    user_willingness_to_pay: str = Field(..., description="User willingness to pay for a solution")
    timestamp: str = Field(..., description="Timestamp of the analysis")


class CompetitorSchema(BaseModel):
    """Pydantic model for a competitor in a niche."""

    name: str = Field(..., description="Name of the competitor")
    description: str = Field(..., description="Description of the competitor")
    market_share: str = Field(..., description="Market share of the competitor")
    strengths: List[str] = Field(..., description="Strengths of the competitor")
    weaknesses: List[str] = Field(..., description="Weaknesses of the competitor")
    pricing: str = Field(..., description="Pricing information of the competitor")


class CompetitionAnalysisSchema(BaseModel):
    """Pydantic model for competition analysis of a niche."""

    id: str = Field(..., description="Unique identifier for the analysis")
    niche: str = Field(..., description="Niche being analyzed")
    competitor_count: int = Field(..., description="Number of competitors")
    top_competitors: List[CompetitorSchema] = Field(..., description="Top competitors in the niche")
    market_saturation: str = Field(..., description="Market saturation level")
    entry_barriers: str = Field(..., description="Entry barriers to the market")
    differentiation_opportunities: List[str] = Field(
        ..., description="Opportunities for differentiation"
    )
    timestamp: str = Field(..., description="Timestamp of the analysis")


class UserSegmentSchema(BaseModel):
    """Pydantic model for a user segment in a niche."""

    name: str = Field(..., description="Name of the user segment")
    description: str = Field(..., description="Description of the user segment")
    size: str = Field(..., description="Size of the user segment")
    priority: str = Field(..., description="Priority of the user segment")


class DemographicsSchema(BaseModel):
    """Pydantic model for demographics of target users."""

    age_range: str = Field(..., description="Age range of target users")
    gender: str = Field(..., description="Gender distribution of target users")
    location: str = Field(..., description="Geographic location of target users")
    education: str = Field(..., description="Education level of target users")
    income: str = Field(..., description="Income level of target users")


class PsychographicsSchema(BaseModel):
    """Pydantic model for psychographics of target users."""

    goals: List[str] = Field(..., description="Goals of target users")
    values: List[str] = Field(..., description="Values of target users")
    challenges: List[str] = Field(..., description="Challenges of target users")


class BuyingBehaviorSchema(BaseModel):
    """Pydantic model for buying behavior of target users."""

    decision_factors: List[str] = Field(..., description="Decision factors in purchasing")
    purchase_process: str = Field(..., description="Description of the purchase process")
    price_sensitivity: str = Field(..., description="Price sensitivity of target users")


class TargetUserAnalysisSchema(BaseModel):
    """Pydantic model for target user analysis."""

    id: str = Field(..., description="Unique identifier for the analysis")
    niche: str = Field(..., description="Niche being analyzed")
    user_segments: List[UserSegmentSchema] = Field(..., description="User segments in the niche")
    demographics: DemographicsSchema = Field(..., description="Demographics of target users")
    psychographics: PsychographicsSchema = Field(..., description="Psychographics of target users")
    pain_points: List[str] = Field(..., description="Pain points of target users")
    goals: List[str] = Field(..., description="Goals of target users")
    buying_behavior: BuyingBehaviorSchema = Field(
        ..., description="Buying behavior of target users"
    )
    timestamp: str = Field(..., description="Timestamp of the analysis")


class TrendSchema(BaseModel):
    """Pydantic model for a market trend."""

    name: str = Field(..., description="Name of the trend")
    description: str = Field(..., description="Description of the trend")
    impact: str = Field(..., description="Impact of the trend")
    maturity: str = Field(..., description="Maturity level of the trend")


class PredictionSchema(BaseModel):
    """Pydantic model for a market prediction."""

    name: str = Field(..., description="Name of the prediction")
    description: str = Field(..., description="Description of the prediction")
    likelihood: str = Field(..., description="Likelihood of the prediction")
    timeframe: str = Field(..., description="Timeframe for the prediction")


class TrendAnalysisSchema(BaseModel):
    """Pydantic model for market trend analysis."""

    id: str = Field(..., description="Unique identifier for the analysis")
    segment: str = Field(..., description="Market segment being analyzed")
    current_trends: List[TrendSchema] = Field(..., description="Current trends in the segment")
    future_predictions: List[PredictionSchema] = Field(
        ..., description="Future predictions for the segment"
    )
    technological_shifts: List[str] = Field(..., description="Technological shifts in the segment")


class MarketSegmentSchema(BaseModel):
    """Pydantic model for a market segment."""

    id: str = Field(..., description="Unique identifier for the segment")
    name: str = Field(..., description="Name of the segment")
    description: str = Field(..., description="Description of the segment")
    market_size: str = Field(..., description="Size of the market")
    growth_rate: str = Field(..., description="Growth rate of the market")
    competition: str = Field(..., description="Competition level in the market")
    barriers_to_entry: str = Field(..., description="Barriers to entry in the market")
    technological_adoption: str = Field(..., description="Technological adoption in the market")
    potential_niches: List[str] = Field(..., description="Potential niches in the market")
    target_users: List[str] = Field(..., description="Target users in the market")


class FactorScoreSchema(BaseModel):
    """Pydantic model for a scoring factor in opportunity scoring."""

    score: float = Field(..., description="Score for the factor", ge=0.0, le=1.0)
    weight: float = Field(..., description="Weight of the factor", ge=0.0, le=1.0)
    weighted_score: float = Field(..., description="Weighted score for the factor", ge=0.0, le=1.0)
    analysis: str = Field(..., description="Analysis of the factor")


class FactorScoresSchema(BaseModel):
    """Pydantic model for all factor scores in opportunity scoring."""

    market_size: FactorScoreSchema = Field(..., description="Market size factor score")
    growth_rate: FactorScoreSchema = Field(..., description="Growth rate factor score")
    competition: FactorScoreSchema = Field(..., description="Competition factor score")
    problem_severity: FactorScoreSchema = Field(..., description="Problem severity factor score")
    solution_feasibility: FactorScoreSchema = Field(
        ..., description="Solution feasibility factor score"
    )
    monetization_potential: FactorScoreSchema = Field(
        ..., description="Monetization potential factor score"
    )


class FactorsSchema(BaseModel):
    """Pydantic model for raw factor scores in opportunity scoring."""

    market_size: float = Field(..., description="Market size factor score", ge=0.0, le=1.0)
    growth_rate: float = Field(..., description="Growth rate factor score", ge=0.0, le=1.0)
    competition: float = Field(..., description="Competition factor score", ge=0.0, le=1.0)
    problem_severity: float = Field(
        ..., description="Problem severity factor score", ge=0.0, le=1.0
    )
    solution_feasibility: float = Field(
        ..., description="Solution feasibility factor score", ge=0.0, le=1.0
    )
    monetization_potential: float = Field(
        ..., description="Monetization potential factor score", ge=0.0, le=1.0
    )


class OpportunityScoreSchema(BaseModel):
    """Pydantic model for opportunity scoring results."""

    id: str = Field(..., description="Unique identifier for the opportunity score")
    niche: str = Field(..., description="Niche being scored")
    score: float = Field(..., description="Overall opportunity score", ge=0.0, le=1.0)
    overall_score: float = Field(
        ..., description="Overall opportunity score (same as score)", ge=0.0, le=1.0
    )
    opportunity_assessment: str = Field(..., description="Assessment of the opportunity")
    factor_scores: FactorScoresSchema = Field(..., description="Detailed factor scores")
    factors: FactorsSchema = Field(..., description="Raw factor scores")
    recommendations: List[str] = Field(..., description="Recommended actions")
    timestamp: str = Field(..., description="Timestamp of the scoring")


class RankedOpportunitySchema(BaseModel):
    """Pydantic model for a ranked opportunity in opportunity comparison."""

    id: str = Field(..., description="Unique identifier for the opportunity")
    niche: str = Field(..., description="Niche of the opportunity")
    overall_score: float = Field(
        ..., description="Overall score of the opportunity", ge=0.0, le=1.0
    )
    rank: int = Field(..., description="Rank of the opportunity", gt=0)


class TopRecommendationSchema(BaseModel):
    """Pydantic model for a top recommendation in opportunity comparison."""

    id: str = Field(..., description="Unique identifier for the recommendation")
    niche: str = Field(..., description="Niche of the recommendation")
    overall_score: float = Field(
        ..., description="Overall score of the recommendation", ge=0.0, le=1.0
    )
    assessment: str = Field(..., description="Assessment of the recommendation")
    next_steps: List[str] = Field(..., description="Recommended next steps")


class ScoreDistributionSchema(BaseModel):
    """Pydantic model for score distribution in opportunity comparison."""

    excellent: int = Field(..., description="Number of opportunities with excellent scores")
    very_good: int = Field(..., description="Number of opportunities with very good scores")
    good: int = Field(..., description="Number of opportunities with good scores")
    fair: int = Field(..., description="Number of opportunities with fair scores")
    limited: int = Field(..., description="Number of opportunities with limited scores")


class ComparativeAnalysisSchema(BaseModel):
    """Pydantic model for comparative analysis in opportunity comparison."""

    highest_score: Optional[float] = Field(None, description="Highest opportunity score")
    lowest_score: Optional[float] = Field(None, description="Lowest opportunity score")
    average_score: Optional[float] = Field(None, description="Average opportunity score")
    score_distribution: ScoreDistributionSchema = Field(..., description="Distribution of scores")


class OpportunityComparisonSchema(BaseModel):
    """Pydantic model for opportunity comparison results."""

    id: str = Field(..., description="Unique identifier for the comparison")
    opportunities_count: int = Field(..., description="Number of opportunities compared")
    ranked_opportunities: List[RankedOpportunitySchema] = Field(
        ..., description="Ranked list of opportunities"
    )
    top_recommendation: Optional[TopRecommendationSchema] = Field(
        None, description="Top recommendation"
    )
    comparison_factors: Dict[str, str] = Field(..., description="Factors used for comparison")
    comparative_analysis: ComparativeAnalysisSchema = Field(
        ..., description="Comparative analysis of opportunities"
    )
    recommendations: List[str] = Field(..., description="Overall recommendations")
    timestamp: str = Field(..., description="Timestamp of the comparison")
