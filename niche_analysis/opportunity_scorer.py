"""
Opportunity Scorer for the pAIssive Income project.
Scores niche opportunities based on various factors.
"""

from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from .schemas import (
    OpportunityScoreSchema, OpportunityComparisonSchema,
    FactorScoreSchema, FactorScoresSchema, FactorsSchema,
    RankedOpportunitySchema, TopRecommendationSchema,
    ComparativeAnalysisSchema, ScoreDistributionSchema
)
