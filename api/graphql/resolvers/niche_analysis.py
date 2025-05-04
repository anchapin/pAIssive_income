"""
"""
Niche Analysis GraphQL resolvers.
Niche Analysis GraphQL resolvers.


This module provides resolvers for niche analysis queries and mutations.
This module provides resolvers for niche analysis queries and mutations.
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
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:
    from ..schemas.niche_analysis import (NicheAnalysisInput, NicheInput,
    from ..schemas.niche_analysis import (NicheAnalysisInput, NicheInput,
    NicheType, OpportunityType)
    NicheType, OpportunityType)


    @strawberry.type
    @strawberry.type
    class NicheAnalysisQuery:
    class NicheAnalysisQuery:
    """Niche analysis query resolvers."""

    @strawberry.field
    async def niches(
    self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
    ) -> List[NicheType]:
    """
    """
    Get a list of niches.
    Get a list of niches.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    limit: Maximum number of niches to return
    limit: Maximum number of niches to return
    offset: Number of niches to skip
    offset: Number of niches to skip


    Returns:
    Returns:
    List of niches
    List of niches
    """
    """
    # Get niche analysis service from context
    # Get niche analysis service from context
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    logger.warning("Niche analysis service not available")
    logger.warning("Niche analysis service not available")
    return []
    return []


    # Get niches from service
    # Get niches from service
    try:
    try:
    niches = await service.get_niches(limit=limit, offset=offset)
    niches = await service.get_niches(limit=limit, offset=offset)
    return [
    return [
    NicheType(
    NicheType(
    id=str(niche.id),
    id=str(niche.id),
    name=niche.name,
    name=niche.name,
    description=niche.description,
    description=niche.description,
    market_size=niche.market_size,
    market_size=niche.market_size,
    growth_rate=niche.growth_rate,
    growth_rate=niche.growth_rate,
    competition_level=niche.competition_level,
    competition_level=niche.competition_level,
    created_at=(
    created_at=(
    niche.created_at.isoformat() if niche.created_at else None
    niche.created_at.isoformat() if niche.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    niche.updated_at.isoformat() if niche.updated_at else None
    niche.updated_at.isoformat() if niche.updated_at else None
    ),
    ),
    )
    )
    for niche in niches
    for niche in niches
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting niches: {str(e)}")
    logger.error(f"Error getting niches: {str(e)}")
    return []
    return []


    @strawberry.field
    @strawberry.field
    async def niche(self, info: Info, id: str) -> Optional[NicheType]:
    async def niche(self, info: Info, id: str) -> Optional[NicheType]:
    """
    """
    Get a niche by ID.
    Get a niche by ID.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: Niche ID
    id: Niche ID


    Returns:
    Returns:
    Niche if found, None otherwise
    Niche if found, None otherwise
    """
    """
    # Get niche analysis service from context
    # Get niche analysis service from context
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    logger.warning("Niche analysis service not available")
    logger.warning("Niche analysis service not available")
    return None
    return None


    # Get niche from service
    # Get niche from service
    try:
    try:
    niche = await service.get_niche(id)
    niche = await service.get_niche(id)
    if not niche:
    if not niche:
    return None
    return None


    return NicheType(
    return NicheType(
    id=str(niche.id),
    id=str(niche.id),
    name=niche.name,
    name=niche.name,
    description=niche.description,
    description=niche.description,
    market_size=niche.market_size,
    market_size=niche.market_size,
    growth_rate=niche.growth_rate,
    growth_rate=niche.growth_rate,
    competition_level=niche.competition_level,
    competition_level=niche.competition_level,
    created_at=(
    created_at=(
    niche.created_at.isoformat() if niche.created_at else None
    niche.created_at.isoformat() if niche.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    niche.updated_at.isoformat() if niche.updated_at else None
    niche.updated_at.isoformat() if niche.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error getting niche: {str(e)}")
    logger.error(f"Error getting niche: {str(e)}")
    return None
    return None


    @strawberry.field
    @strawberry.field
    async def opportunities(
    async def opportunities(
    self,
    self,
    info: Info,
    info: Info,
    niche_id: Optional[str] = None,
    niche_id: Optional[str] = None,
    limit: Optional[int] = 10,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    offset: Optional[int] = 0,
    ) -> List[OpportunityType]:
    ) -> List[OpportunityType]:
    """
    """
    Get a list of opportunities.
    Get a list of opportunities.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    niche_id: Filter by niche ID
    niche_id: Filter by niche ID
    limit: Maximum number of opportunities to return
    limit: Maximum number of opportunities to return
    offset: Number of opportunities to skip
    offset: Number of opportunities to skip


    Returns:
    Returns:
    List of opportunities
    List of opportunities
    """
    """
    # Get niche analysis service from context
    # Get niche analysis service from context
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    logger.warning("Niche analysis service not available")
    logger.warning("Niche analysis service not available")
    return []
    return []


    # Get opportunities from service
    # Get opportunities from service
    try:
    try:
    opportunities = await service.get_opportunities(
    opportunities = await service.get_opportunities(
    niche_id=niche_id, limit=limit, offset=offset
    niche_id=niche_id, limit=limit, offset=offset
    )
    )


    return [
    return [
    OpportunityType(
    OpportunityType(
    id=str(opp.id),
    id=str(opp.id),
    niche_id=str(opp.niche_id),
    niche_id=str(opp.niche_id),
    problem_id=str(opp.problem_id),
    problem_id=str(opp.problem_id),
    title=opp.title,
    title=opp.title,
    description=opp.description,
    description=opp.description,
    score=opp.score,
    score=opp.score,
    market_potential=opp.market_potential,
    market_potential=opp.market_potential,
    feasibility=opp.feasibility,
    feasibility=opp.feasibility,
    profitability=opp.profitability,
    profitability=opp.profitability,
    created_at=(
    created_at=(
    opp.created_at.isoformat() if opp.created_at else None
    opp.created_at.isoformat() if opp.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    opp.updated_at.isoformat() if opp.updated_at else None
    opp.updated_at.isoformat() if opp.updated_at else None
    ),
    ),
    )
    )
    for opp in opportunities
    for opp in opportunities
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting opportunities: {str(e)}")
    logger.error(f"Error getting opportunities: {str(e)}")
    return []
    return []


    @strawberry.type
    @strawberry.type
    class NicheAnalysisMutation:
    class NicheAnalysisMutation:
    """Niche analysis mutation resolvers."""

    @strawberry.mutation
    async def create_niche_analysis(
    self, info: Info, input: NicheAnalysisInput
    ) -> Optional[NicheType]:
    """
    """
    Create a new niche analysis.
    Create a new niche analysis.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    input: Niche analysis input
    input: Niche analysis input


    Returns:
    Returns:
    Created niche if successful, None otherwise
    Created niche if successful, None otherwise
    """
    """
    # Get niche analysis service from context
    # Get niche analysis service from context
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    logger.warning("Niche analysis service not available")
    logger.warning("Niche analysis service not available")
    return None
    return None


    # Create niche analysis
    # Create niche analysis
    try:
    try:
    niche = await service.create_niche_analysis(
    niche = await service.create_niche_analysis(
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    market_size=input.market_size,
    market_size=input.market_size,
    growth_rate=input.growth_rate,
    growth_rate=input.growth_rate,
    competition_level=input.competition_level,
    competition_level=input.competition_level,
    )
    )


    return NicheType(
    return NicheType(
    id=str(niche.id),
    id=str(niche.id),
    name=niche.name,
    name=niche.name,
    description=niche.description,
    description=niche.description,
    market_size=niche.market_size,
    market_size=niche.market_size,
    growth_rate=niche.growth_rate,
    growth_rate=niche.growth_rate,
    competition_level=niche.competition_level,
    competition_level=niche.competition_level,
    created_at=(
    created_at=(
    niche.created_at.isoformat() if niche.created_at else None
    niche.created_at.isoformat() if niche.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    niche.updated_at.isoformat() if niche.updated_at else None
    niche.updated_at.isoformat() if niche.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating niche analysis: {str(e)}")
    logger.error(f"Error creating niche analysis: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def update_niche(
    async def update_niche(
    self, info: Info, id: str, input: NicheInput
    self, info: Info, id: str, input: NicheInput
    ) -> Optional[NicheType]:
    ) -> Optional[NicheType]:
    """
    """
    Update a niche.
    Update a niche.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: Niche ID
    id: Niche ID
    input: Niche input
    input: Niche input


    Returns:
    Returns:
    Updated niche if successful, None otherwise
    Updated niche if successful, None otherwise
    """
    """
    # Get niche analysis service from context
    # Get niche analysis service from context
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    logger.warning("Niche analysis service not available")
    logger.warning("Niche analysis service not available")
    return None
    return None


    # Update niche
    # Update niche
    try:
    try:
    niche = await service.update_niche(
    niche = await service.update_niche(
    id=id,
    id=id,
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    market_size=input.market_size,
    market_size=input.market_size,
    growth_rate=input.growth_rate,
    growth_rate=input.growth_rate,
    competition_level=input.competition_level,
    competition_level=input.competition_level,
    )
    )


    if not niche:
    if not niche:
    return None
    return None


    return NicheType(
    return NicheType(
    id=str(niche.id),
    id=str(niche.id),
    name=niche.name,
    name=niche.name,
    description=niche.description,
    description=niche.description,
    market_size=niche.market_size,
    market_size=niche.market_size,
    growth_rate=niche.growth_rate,
    growth_rate=niche.growth_rate,
    competition_level=niche.competition_level,
    competition_level=niche.competition_level,
    created_at=(
    created_at=(
    niche.created_at.isoformat() if niche.created_at else None
    niche.created_at.isoformat() if niche.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    niche.updated_at.isoformat() if niche.updated_at else None
    niche.updated_at.isoformat() if niche.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error updating niche: {str(e)}")
    logger.error(f"Error updating niche: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def delete_niche(self, info: Info, id: str) -> bool:
    async def delete_niche(self, info: Info, id: str) -> bool:
    """
    """
    Delete a niche.
    Delete a niche.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: Niche ID
    id: Niche ID


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    # Get niche analysis service from context
    # Get niche analysis service from context
    service = info.context["services"].get("niche_analysis")
    service = info.context["services"].get("niche_analysis")
    if not service:
    if not service:
    logger.warning("Niche analysis service not available")
    logger.warning("Niche analysis service not available")
    return False
    return False


    # Delete niche
    # Delete niche
    try:
    try:
    success = await service.delete_niche(id)
    success = await service.delete_niche(id)
    return success
    return success
except Exception as e:
except Exception as e:
    logger.error(f"Error deleting niche: {str(e)}")
    logger.error(f"Error deleting niche: {str(e)}")
    return False
    return False