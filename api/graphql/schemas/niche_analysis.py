"""
"""
Niche Analysis GraphQL schema.
Niche Analysis GraphQL schema.


This module provides GraphQL types and resolvers for the niche analysis module.
This module provides GraphQL types and resolvers for the niche analysis module.
"""
"""




import logging
import logging
from typing import List, Optional
from typing import List, Optional


import strawberry
import strawberry
from strawberry.types import Info
from strawberry.types import Info


STRAWBERRY_AVAILABLE
STRAWBERRY_AVAILABLE


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:


    @strawberry.type
    @strawberry.type
    class MarketSegment:
    class MarketSegment:
    """Market segment information"""

    id: strawberry.ID
    name: str
    description: str
    opportunity_score: float

    @strawberry.type
    class NicheOpportunity:

    id: strawberry.ID
    name: str
    segment_id: strawberry.ID
    segment_name: str
    description: str
    opportunity_score: float
    competition_level: str
    growth_potential: str

    @strawberry.type
    class NicheAnalysisResult:

    id: strawberry.ID
    date_created: str
    segments: List[MarketSegment]
    opportunities: List[NicheOpportunity]

    @strawberry.input
    class AnalyzeNichesInput:

    segment_ids: List[strawberry.ID]

    @strawberry.type
    class NicheAnalysisQuery:


    @strawberry.field
    @strawberry.field
    def market_segments(self, info: Info) -> List[MarketSegment]:
    def market_segments(self, info: Info) -> List[MarketSegment]:
    """
    """
    Get all market segments.
    Get all market segments.


    Returns:
    Returns:
    List of market segments
    List of market segments
    """
    """
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    return []
    return []


    segments = service.get_market_segments()
    segments = service.get_market_segments()
    return [
    return [
    MarketSegment(
    MarketSegment(
    id=str(segment.id),
    id=str(segment.id),
    name=segment.name,
    name=segment.name,
    description=segment.description,
    description=segment.description,
    opportunity_score=segment.opportunity_score,
    opportunity_score=segment.opportunity_score,
    )
    )
    for segment in segments
    for segment in segments
    ]
    ]


    @strawberry.field
    @strawberry.field
    def niche_analysis_results(self, info: Info) -> List[NicheAnalysisResult]:
    def niche_analysis_results(self, info: Info) -> List[NicheAnalysisResult]:
    """
    """
    Get all niche analysis results.
    Get all niche analysis results.


    Returns:
    Returns:
    List of niche analysis results
    List of niche analysis results
    """
    """
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    return []
    return []


    results = service.get_all_niche_results()
    results = service.get_all_niche_results()
    return [
    return [
    NicheAnalysisResult(
    NicheAnalysisResult(
    id=str(result.id),
    id=str(result.id),
    date_created=result.date_created.isoformat(),
    date_created=result.date_created.isoformat(),
    segments=[
    segments=[
    MarketSegment(
    MarketSegment(
    id=str(segment.id),
    id=str(segment.id),
    name=segment.name,
    name=segment.name,
    description=segment.description,
    description=segment.description,
    opportunity_score=segment.opportunity_score,
    opportunity_score=segment.opportunity_score,
    )
    )
    for segment in result.segments
    for segment in result.segments
    ],
    ],
    opportunities=[
    opportunities=[
    NicheOpportunity(
    NicheOpportunity(
    id=str(opportunity.id),
    id=str(opportunity.id),
    name=opportunity.name,
    name=opportunity.name,
    segment_id=str(opportunity.segment_id),
    segment_id=str(opportunity.segment_id),
    segment_name=opportunity.segment_name,
    segment_name=opportunity.segment_name,
    description=opportunity.description,
    description=opportunity.description,
    opportunity_score=opportunity.opportunity_score,
    opportunity_score=opportunity.opportunity_score,
    competition_level=opportunity.competition_level,
    competition_level=opportunity.competition_level,
    growth_potential=opportunity.growth_potential,
    growth_potential=opportunity.growth_potential,
    )
    )
    for opportunity in result.opportunities
    for opportunity in result.opportunities
    ],
    ],
    )
    )
    for result in results
    for result in results
    ]
    ]


    @strawberry.field
    @strawberry.field
    def niche_analysis_result(
    def niche_analysis_result(
    self, info: Info, id: strawberry.ID
    self, info: Info, id: strawberry.ID
    ) -> Optional[NicheAnalysisResult]:
    ) -> Optional[NicheAnalysisResult]:
    """
    """
    Get a specific niche analysis result.
    Get a specific niche analysis result.


    Args:
    Args:
    id: ID of the niche analysis result
    id: ID of the niche analysis result


    Returns:
    Returns:
    Niche analysis result if found, None otherwise
    Niche analysis result if found, None otherwise
    """
    """
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    return None
    return None


    result = service.get_niche_result(id)
    result = service.get_niche_result(id)
    if not result:
    if not result:
    return None
    return None


    return NicheAnalysisResult(
    return NicheAnalysisResult(
    id=str(result.id),
    id=str(result.id),
    date_created=result.date_created.isoformat(),
    date_created=result.date_created.isoformat(),
    segments=[
    segments=[
    MarketSegment(
    MarketSegment(
    id=str(segment.id),
    id=str(segment.id),
    name=segment.name,
    name=segment.name,
    description=segment.description,
    description=segment.description,
    opportunity_score=segment.opportunity_score,
    opportunity_score=segment.opportunity_score,
    )
    )
    for segment in result.segments
    for segment in result.segments
    ],
    ],
    opportunities=[
    opportunities=[
    NicheOpportunity(
    NicheOpportunity(
    id=str(opportunity.id),
    id=str(opportunity.id),
    name=opportunity.name,
    name=opportunity.name,
    segment_id=str(opportunity.segment_id),
    segment_id=str(opportunity.segment_id),
    segment_name=opportunity.segment_name,
    segment_name=opportunity.segment_name,
    description=opportunity.description,
    description=opportunity.description,
    opportunity_score=opportunity.opportunity_score,
    opportunity_score=opportunity.opportunity_score,
    competition_level=opportunity.competition_level,
    competition_level=opportunity.competition_level,
    growth_potential=opportunity.growth_potential,
    growth_potential=opportunity.growth_potential,
    )
    )
    for opportunity in result.opportunities
    for opportunity in result.opportunities
    ],
    ],
    )
    )


    @strawberry.type
    @strawberry.type
    class NicheAnalysisMutation:
    class NicheAnalysisMutation:
    """Niche analysis mutation fields"""

    @strawberry.mutation
    async def analyze_niches(
    self, info: Info, input: AnalyzeNichesInput
    ) -> Optional[NicheAnalysisResult]:
    """
    """
    Analyze niches based on selected market segments.
    Analyze niches based on selected market segments.


    Args:
    Args:
    input: Analysis input with segment IDs
    input: Analysis input with segment IDs


    Returns:
    Returns:
    Niche analysis result
    Niche analysis result
    """
    """
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    return None
    return None


    result = await service.analyze_niches(input.segment_ids)
    result = await service.analyze_niches(input.segment_ids)
    if not result:
    if not result:
    return None
    return None


    return NicheAnalysisResult(
    return NicheAnalysisResult(
    id=str(result.id),
    id=str(result.id),
    date_created=result.date_created.isoformat(),
    date_created=result.date_created.isoformat(),
    segments=[
    segments=[
    MarketSegment(
    MarketSegment(
    id=str(segment.id),
    id=str(segment.id),
    name=segment.name,
    name=segment.name,
    description=segment.description,
    description=segment.description,
    opportunity_score=segment.opportunity_score,
    opportunity_score=segment.opportunity_score,
    )
    )
    for segment in result.segments
    for segment in result.segments
    ],
    ],
    opportunities=[
    opportunities=[
    NicheOpportunity(
    NicheOpportunity(
    id=str(opportunity.id),
    id=str(opportunity.id),
    name=opportunity.name,
    name=opportunity.name,
    segment_id=str(opportunity.segment_id),
    segment_id=str(opportunity.segment_id),
    segment_name=opportunity.segment_name,
    segment_name=opportunity.segment_name,
    description=opportunity.description,
    description=opportunity.description,
    opportunity_score=opportunity.opportunity_score,
    opportunity_score=opportunity.opportunity_score,
    competition_level=opportunity.competition_level,
    competition_level=opportunity.competition_level,
    growth_potential=opportunity.growth_potential,
    growth_potential=opportunity.growth_potential,
    )
    )
    for opportunity in result.opportunities
    for opportunity in result.opportunities
    ],
    ],
    )
    )


    else:
    else:
    # Fallbacks if Strawberry isn't available
    # Fallbacks if Strawberry isn't available
    class NicheAnalysisQuery:
    class NicheAnalysisQuery:
    pass
    pass


    class NicheAnalysisMutation:
    class NicheAnalysisMutation:
    pass
    pass