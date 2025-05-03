"""
Niche Analysis GraphQL resolvers.

This module provides resolvers for niche analysis queries and mutations.
"""

import logging
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:
    from ..schemas.niche_analysis import (
        MarketSegmentInput,
        MarketSegmentType,
        NicheAnalysisInput,
        NicheInput,
        NicheType,
        OpportunityType,
        ProblemInput,
        ProblemType,
    )

    @strawberry.type
    class NicheAnalysisQuery:
        """Niche analysis query resolvers."""

        @strawberry.field
        async def niches(
            self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
        ) -> List[NicheType]:
            """
            Get a list of niches.

            Args:
                info: GraphQL resolver info
                limit: Maximum number of niches to return
                offset: Number of niches to skip

            Returns:
                List of niches
            """
            # Get niche analysis service from context
            service = info.context["services"].get("niche_analysis")
            if not service:
                logger.warning("Niche analysis service not available")
                return []

            # Get niches from service
            try:
                niches = await service.get_niches(limit=limit, offset=offset)
                return [
                    NicheType(
                        id=str(niche.id),
                        name=niche.name,
                        description=niche.description,
                        market_size=niche.market_size,
                        growth_rate=niche.growth_rate,
                        competition_level=niche.competition_level,
                        created_at=niche.created_at.isoformat() if niche.created_at else None,
                        updated_at=niche.updated_at.isoformat() if niche.updated_at else None,
                    )
                    for niche in niches
                ]
            except Exception as e:
                logger.error(f"Error getting niches: {str(e)}")
                return []

        @strawberry.field
        async def niche(self, info: Info, id: str) -> Optional[NicheType]:
            """
            Get a niche by ID.

            Args:
                info: GraphQL resolver info
                id: Niche ID

            Returns:
                Niche if found, None otherwise
            """
            # Get niche analysis service from context
            service = info.context["services"].get("niche_analysis")
            if not service:
                logger.warning("Niche analysis service not available")
                return None

            # Get niche from service
            try:
                niche = await service.get_niche(id)
                if not niche:
                    return None

                return NicheType(
                    id=str(niche.id),
                    name=niche.name,
                    description=niche.description,
                    market_size=niche.market_size,
                    growth_rate=niche.growth_rate,
                    competition_level=niche.competition_level,
                    created_at=niche.created_at.isoformat() if niche.created_at else None,
                    updated_at=niche.updated_at.isoformat() if niche.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error getting niche: {str(e)}")
                return None

        @strawberry.field
        async def opportunities(
            self,
            info: Info,
            niche_id: Optional[str] = None,
            limit: Optional[int] = 10,
            offset: Optional[int] = 0,
        ) -> List[OpportunityType]:
            """
            Get a list of opportunities.

            Args:
                info: GraphQL resolver info
                niche_id: Filter by niche ID
                limit: Maximum number of opportunities to return
                offset: Number of opportunities to skip

            Returns:
                List of opportunities
            """
            # Get niche analysis service from context
            service = info.context["services"].get("niche_analysis")
            if not service:
                logger.warning("Niche analysis service not available")
                return []

            # Get opportunities from service
            try:
                opportunities = await service.get_opportunities(
                    niche_id=niche_id, limit=limit, offset=offset
                )

                return [
                    OpportunityType(
                        id=str(opp.id),
                        niche_id=str(opp.niche_id),
                        problem_id=str(opp.problem_id),
                        title=opp.title,
                        description=opp.description,
                        score=opp.score,
                        market_potential=opp.market_potential,
                        feasibility=opp.feasibility,
                        profitability=opp.profitability,
                        created_at=opp.created_at.isoformat() if opp.created_at else None,
                        updated_at=opp.updated_at.isoformat() if opp.updated_at else None,
                    )
                    for opp in opportunities
                ]
            except Exception as e:
                logger.error(f"Error getting opportunities: {str(e)}")
                return []

    @strawberry.type
    class NicheAnalysisMutation:
        """Niche analysis mutation resolvers."""

        @strawberry.mutation
        async def create_niche_analysis(
            self, info: Info, input: NicheAnalysisInput
        ) -> Optional[NicheType]:
            """
            Create a new niche analysis.

            Args:
                info: GraphQL resolver info
                input: Niche analysis input

            Returns:
                Created niche if successful, None otherwise
            """
            # Get niche analysis service from context
            service = info.context["services"].get("niche_analysis")
            if not service:
                logger.warning("Niche analysis service not available")
                return None

            # Create niche analysis
            try:
                niche = await service.create_niche_analysis(
                    name=input.name,
                    description=input.description,
                    market_size=input.market_size,
                    growth_rate=input.growth_rate,
                    competition_level=input.competition_level,
                )

                return NicheType(
                    id=str(niche.id),
                    name=niche.name,
                    description=niche.description,
                    market_size=niche.market_size,
                    growth_rate=niche.growth_rate,
                    competition_level=niche.competition_level,
                    created_at=niche.created_at.isoformat() if niche.created_at else None,
                    updated_at=niche.updated_at.isoformat() if niche.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error creating niche analysis: {str(e)}")
                return None

        @strawberry.mutation
        async def update_niche(self, info: Info, id: str, input: NicheInput) -> Optional[NicheType]:
            """
            Update a niche.

            Args:
                info: GraphQL resolver info
                id: Niche ID
                input: Niche input

            Returns:
                Updated niche if successful, None otherwise
            """
            # Get niche analysis service from context
            service = info.context["services"].get("niche_analysis")
            if not service:
                logger.warning("Niche analysis service not available")
                return None

            # Update niche
            try:
                niche = await service.update_niche(
                    id=id,
                    name=input.name,
                    description=input.description,
                    market_size=input.market_size,
                    growth_rate=input.growth_rate,
                    competition_level=input.competition_level,
                )

                if not niche:
                    return None

                return NicheType(
                    id=str(niche.id),
                    name=niche.name,
                    description=niche.description,
                    market_size=niche.market_size,
                    growth_rate=niche.growth_rate,
                    competition_level=niche.competition_level,
                    created_at=niche.created_at.isoformat() if niche.created_at else None,
                    updated_at=niche.updated_at.isoformat() if niche.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error updating niche: {str(e)}")
                return None

        @strawberry.mutation
        async def delete_niche(self, info: Info, id: str) -> bool:
            """
            Delete a niche.

            Args:
                info: GraphQL resolver info
                id: Niche ID

            Returns:
                True if successful, False otherwise
            """
            # Get niche analysis service from context
            service = info.context["services"].get("niche_analysis")
            if not service:
                logger.warning("Niche analysis service not available")
                return False

            # Delete niche
            try:
                success = await service.delete_niche(id)
                return success
            except Exception as e:
                logger.error(f"Error deleting niche: {str(e)}")
                return False
