"""
Marketing GraphQL schema.

This module provides GraphQL types and resolvers for the marketing module.
"""

import logging
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:

    @strawberry.type
    class AudiencePersona:
        """Audience persona for marketing campaigns"""

        id: strawberry.ID
        name: str
        description: str
        demographics: List[str]
        interests: List[str]
        pain_points: List[str]
        goals: List[str]

    @strawberry.type
    class MarketingChannel:
        """Marketing channel for campaigns"""

        id: strawberry.ID
        name: str
        description: str
        platforms: List[str]
        effectiveness_score: float
        cost_per_lead: float

    @strawberry.type
    class ContentPiece:
        """Content piece for a marketing campaign"""

        id: strawberry.ID
        title: str
        description: str
        content_type: str
        channel: str
        audience: str
        calls_to_action: List[str]
        keywords: List[str]
        estimated_engagement: float

    @strawberry.type
    class MarketingCampaign:
        """Marketing campaign for a solution"""

        id: strawberry.ID
        solution_id: strawberry.ID
        solution_name: str
        name: str
        description: str
        target_audiences: List[AudiencePersona]
        channels: List[MarketingChannel]
        content_pieces: List[ContentPiece]
        estimated_reach: int
        estimated_conversion_rate: float
        estimated_cost: float
        date_created: str

    @strawberry.input
    class GenerateCampaignInput:
        """Input for generating a marketing campaign"""

        solution_id: strawberry.ID
        audience_ids: List[strawberry.ID]
        channel_ids: List[strawberry.ID]
        campaign_goals: Optional[List[str]] = None
        budget: Optional[float] = None

    @strawberry.type
    class MarketingQuery:
        """Marketing query fields"""

        @strawberry.field
        def audience_personas(self, info: Info) -> List[AudiencePersona]:
            """
            Get all audience personas.

            Returns:
                List of audience personas
            """
            service = info.context["services"].get("marketing")
            if not service:
                return []

            personas = service.get_audience_personas()
            return [
                AudiencePersona(
                    id=str(persona.id),
                    name=persona.name,
                    description=persona.description,
                    demographics=persona.demographics,
                    interests=persona.interests,
                    pain_points=persona.pain_points,
                    goals=persona.goals,
                )
                for persona in personas
            ]

        @strawberry.field
        def marketing_channels(self, info: Info) -> List[MarketingChannel]:
            """
            Get all marketing channels.

            Returns:
                List of marketing channels
            """
            service = info.context["services"].get("marketing")
            if not service:
                return []

            channels = service.get_channels()
            return [
                MarketingChannel(
                    id=str(channel.id),
                    name=channel.name,
                    description=channel.description,
                    platforms=channel.platforms,
                    effectiveness_score=channel.effectiveness_score,
                    cost_per_lead=channel.cost_per_lead,
                )
                for channel in channels
            ]

        @strawberry.field
        def marketing_campaigns(self, info: Info) -> List[MarketingCampaign]:
            """
            Get all marketing campaigns.

            Returns:
                List of marketing campaigns
            """
            service = info.context["services"].get("marketing")
            if not service:
                return []

            campaigns = service.get_all_campaigns()
            return [self._format_campaign(campaign) for campaign in campaigns]

        @strawberry.field
        def marketing_campaign(self, info: Info, id: strawberry.ID) -> Optional[MarketingCampaign]:
            """
            Get a specific marketing campaign.

            Args:
                id: ID of the marketing campaign

            Returns:
                Marketing campaign if found, None otherwise
            """
            service = info.context["services"].get("marketing")
            if not service:
                return None

            campaign = service.get_campaign(id)
            if not campaign:
                return None

            return self._format_campaign(campaign)

        def _format_campaign(self, campaign) -> MarketingCampaign:
            """Helper method to format campaign data"""
            return MarketingCampaign(
                id=str(campaign.id),
                solution_id=str(campaign.solution_id),
                solution_name=campaign.solution_name,
                name=campaign.name,
                description=campaign.description,
                target_audiences=[
                    AudiencePersona(
                        id=str(audience.id),
                        name=audience.name,
                        description=audience.description,
                        demographics=audience.demographics,
                        interests=audience.interests,
                        pain_points=audience.pain_points,
                        goals=audience.goals,
                    )
                    for audience in campaign.target_audiences
                ],
                channels=[
                    MarketingChannel(
                        id=str(channel.id),
                        name=channel.name,
                        description=channel.description,
                        platforms=channel.platforms,
                        effectiveness_score=channel.effectiveness_score,
                        cost_per_lead=channel.cost_per_lead,
                    )
                    for channel in campaign.channels
                ],
                content_pieces=[
                    ContentPiece(
                        id=str(content.id),
                        title=content.title,
                        description=content.description,
                        content_type=content.content_type,
                        channel=content.channel,
                        audience=content.audience,
                        calls_to_action=content.calls_to_action,
                        keywords=content.keywords,
                        estimated_engagement=content.estimated_engagement,
                    )
                    for content in campaign.content_pieces
                ],
                estimated_reach=campaign.estimated_reach,
                estimated_conversion_rate=campaign.estimated_conversion_rate,
                estimated_cost=campaign.estimated_cost,
                date_created=campaign.date_created.isoformat(),
            )

    @strawberry.type
    class MarketingMutation:
        """Marketing mutation fields"""

        @strawberry.mutation
        async def generate_marketing_campaign(
            self, info: Info, input: GenerateCampaignInput
        ) -> Optional[MarketingCampaign]:
            """
            Generate a marketing campaign for a solution.

            Args:
                input: Campaign generation input

            Returns:
                Generated marketing campaign
            """
            service = info.context["services"].get("marketing")
            if not service:
                return None

            # Generate campaign
            campaign = await service.generate_campaign(
                solution_id=input.solution_id,
                audience_ids=input.audience_ids,
                channel_ids=input.channel_ids,
                campaign_goals=input.campaign_goals,
                budget=input.budget,
            )

            if not campaign:
                return None

            # Format and return campaign
            return MarketingCampaign(
                id=str(campaign.id),
                solution_id=str(campaign.solution_id),
                solution_name=campaign.solution_name,
                name=campaign.name,
                description=campaign.description,
                target_audiences=[
                    AudiencePersona(
                        id=str(audience.id),
                        name=audience.name,
                        description=audience.description,
                        demographics=audience.demographics,
                        interests=audience.interests,
                        pain_points=audience.pain_points,
                        goals=audience.goals,
                    )
                    for audience in campaign.target_audiences
                ],
                channels=[
                    MarketingChannel(
                        id=str(channel.id),
                        name=channel.name,
                        description=channel.description,
                        platforms=channel.platforms,
                        effectiveness_score=channel.effectiveness_score,
                        cost_per_lead=channel.cost_per_lead,
                    )
                    for channel in campaign.channels
                ],
                content_pieces=[
                    ContentPiece(
                        id=str(content.id),
                        title=content.title,
                        description=content.description,
                        content_type=content.content_type,
                        channel=content.channel,
                        audience=content.audience,
                        calls_to_action=content.calls_to_action,
                        keywords=content.keywords,
                        estimated_engagement=content.estimated_engagement,
                    )
                    for content in campaign.content_pieces
                ],
                estimated_reach=campaign.estimated_reach,
                estimated_conversion_rate=campaign.estimated_conversion_rate,
                estimated_cost=campaign.estimated_cost,
                date_created=campaign.date_created.isoformat(),
            )

else:
    # Fallbacks if Strawberry isn't available
    class MarketingQuery:
        pass

    class MarketingMutation:
        pass
