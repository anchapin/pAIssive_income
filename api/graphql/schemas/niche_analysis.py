"""
Niche Analysis GraphQL schema.

This module provides GraphQL types and resolvers for the niche analysis module.
"""


import logging
from typing import List, Optional


    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE 

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:

= True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:

    @strawberry.type
    class MarketSegment:
        """Market segment information"""

        id: strawberry.ID
        name: str
        description: str
        opportunity_score: float

    @strawberry.type
    class NicheOpportunity:
        """Niche opportunity information"""

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
        """Result of niche analysis"""

        id: strawberry.ID
        date_created: str
        segments: List[MarketSegment]
        opportunities: List[NicheOpportunity]

    @strawberry.input
    class AnalyzeNichesInput:
        """Input for niche analysis"""

        segment_ids: List[strawberry.ID]

    @strawberry.type
    class NicheAnalysisQuery:
        """Niche analysis query fields"""

        @strawberry.field
        def market_segments(self, info: Info) -> List[MarketSegment]:
            """
            Get all market segments.

            Returns:
                List of market segments
            """
            service = info.context["services"].get("niche_analysis")
            if not service:
                return []

            segments = service.get_market_segments()
            return [
                MarketSegment(
                    id=str(segment.id),
                    name=segment.name,
                    description=segment.description,
                    opportunity_score=segment.opportunity_score,
                )
                for segment in segments
            ]

        @strawberry.field
        def niche_analysis_results(self, info: Info) -> List[NicheAnalysisResult]:
            """
            Get all niche analysis results.

            Returns:
                List of niche analysis results
            """
            service = info.context["services"].get("niche_analysis")
            if not service:
                return []

            results = service.get_all_niche_results()
            return [
                NicheAnalysisResult(
                    id=str(result.id),
                    date_created=result.date_created.isoformat(),
                    segments=[
                        MarketSegment(
                            id=str(segment.id),
                            name=segment.name,
                            description=segment.description,
                            opportunity_score=segment.opportunity_score,
                        )
                        for segment in result.segments
                    ],
                    opportunities=[
                        NicheOpportunity(
                            id=str(opportunity.id),
                            name=opportunity.name,
                            segment_id=str(opportunity.segment_id),
                            segment_name=opportunity.segment_name,
                            description=opportunity.description,
                            opportunity_score=opportunity.opportunity_score,
                            competition_level=opportunity.competition_level,
                            growth_potential=opportunity.growth_potential,
                        )
                        for opportunity in result.opportunities
                    ],
                )
                for result in results
            ]

        @strawberry.field
        def niche_analysis_result(
            self, info: Info, id: strawberry.ID
        ) -> Optional[NicheAnalysisResult]:
            """
            Get a specific niche analysis result.

            Args:
                id: ID of the niche analysis result

            Returns:
                Niche analysis result if found, None otherwise
            """
            service = info.context["services"].get("niche_analysis")
            if not service:
                return None

            result = service.get_niche_result(id)
            if not result:
                return None

            return NicheAnalysisResult(
                id=str(result.id),
                date_created=result.date_created.isoformat(),
                segments=[
                    MarketSegment(
                        id=str(segment.id),
                        name=segment.name,
                        description=segment.description,
                        opportunity_score=segment.opportunity_score,
                    )
                    for segment in result.segments
                ],
                opportunities=[
                    NicheOpportunity(
                        id=str(opportunity.id),
                        name=opportunity.name,
                        segment_id=str(opportunity.segment_id),
                        segment_name=opportunity.segment_name,
                        description=opportunity.description,
                        opportunity_score=opportunity.opportunity_score,
                        competition_level=opportunity.competition_level,
                        growth_potential=opportunity.growth_potential,
                    )
                    for opportunity in result.opportunities
                ],
            )

    @strawberry.type
    class NicheAnalysisMutation:
        """Niche analysis mutation fields"""

        @strawberry.mutation
        async def analyze_niches(
            self, info: Info, input: AnalyzeNichesInput
        ) -> Optional[NicheAnalysisResult]:
            """
            Analyze niches based on selected market segments.

            Args:
                input: Analysis input with segment IDs

            Returns:
                Niche analysis result
            """
            service = info.context["services"].get("niche_analysis")
            if not service:
                return None

            result = await service.analyze_niches(input.segment_ids)
            if not result:
                return None

            return NicheAnalysisResult(
                id=str(result.id),
                date_created=result.date_created.isoformat(),
                segments=[
                    MarketSegment(
                        id=str(segment.id),
                        name=segment.name,
                        description=segment.description,
                        opportunity_score=segment.opportunity_score,
                    )
                    for segment in result.segments
                ],
                opportunities=[
                    NicheOpportunity(
                        id=str(opportunity.id),
                        name=opportunity.name,
                        segment_id=str(opportunity.segment_id),
                        segment_name=opportunity.segment_name,
                        description=opportunity.description,
                        opportunity_score=opportunity.opportunity_score,
                        competition_level=opportunity.competition_level,
                        growth_potential=opportunity.growth_potential,
                    )
                    for opportunity in result.opportunities
                ],
            )

else:
    # Fallbacks if Strawberry isn't available
    class NicheAnalysisQuery:
        pass

    class NicheAnalysisMutation:
        pass