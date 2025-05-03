"""
Monetization GraphQL resolvers.

This module provides resolvers for monetization queries and mutations.
"""

import logging
from typing import Any, Dict, Float, List, Optional, Union

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
    from ..schemas.monetization import (
        BillingPeriodEnum,
        FeatureInput,
        FeatureType,
        PricingTierInput,
        PricingTierType,
        RevenueProjectionInput,
        RevenueProjectionType,
        SubscriptionModelInput,
        SubscriptionModelType,
        SubscriptionTypeEnum,
    )

    @strawberry.type
    class MonetizationQuery:
        """Monetization query resolvers."""

        @strawberry.field
        async def subscription_models(
            self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
        ) -> List[SubscriptionModelType]:
            """
            Get a list of subscription models.

            Args:
                info: GraphQL resolver info
                limit: Maximum number of models to return
                offset: Number of models to skip

            Returns:
                List of subscription models
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return []

            # Get subscription models from service
            try:
                models = await service.get_subscription_models(limit=limit, offset=offset)
                return [
                    SubscriptionModelType(
                        id=str(model.id),
                        name=model.name,
                        description=model.description,
                        subscription_type=SubscriptionTypeEnum(model.subscription_type),
                        created_at=model.created_at.isoformat() if model.created_at else None,
                        updated_at=model.updated_at.isoformat() if model.updated_at else None,
                    )
                    for model in models
                ]
            except Exception as e:
                logger.error(f"Error getting subscription models: {str(e)}")
                return []

        @strawberry.field
        async def subscription_model(self, info: Info, id: str) -> Optional[SubscriptionModelType]:
            """
            Get a subscription model by ID.

            Args:
                info: GraphQL resolver info
                id: Subscription model ID

            Returns:
                Subscription model if found, None otherwise
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return None

            # Get subscription model from service
            try:
                model = await service.get_subscription_model(id)
                if not model:
                    return None

                return SubscriptionModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    subscription_type=SubscriptionTypeEnum(model.subscription_type),
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error getting subscription model: {str(e)}")
                return None

        @strawberry.field
        async def revenue_projection(
            self, info: Info, input: RevenueProjectionInput
        ) -> Optional[RevenueProjectionType]:
            """
            Get a revenue projection.

            Args:
                info: GraphQL resolver info
                input: Revenue projection input

            Returns:
                Revenue projection if successful, None otherwise
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return None

            # Get revenue projection from service
            try:
                projection = await service.calculate_revenue_projection(
                    subscription_model_id=input.subscription_model_id,
                    initial_customers=input.initial_customers,
                    growth_rate=input.growth_rate,
                    churn_rate=input.churn_rate,
                    time_period_months=input.time_period_months,
                )

                if not projection:
                    return None

                return RevenueProjectionType(
                    subscription_model_id=str(projection.subscription_model_id),
                    initial_customers=projection.initial_customers,
                    growth_rate=projection.growth_rate,
                    churn_rate=projection.churn_rate,
                    time_period_months=projection.time_period_months,
                    monthly_revenue=projection.monthly_revenue,
                    annual_revenue=projection.annual_revenue,
                    lifetime_value=projection.lifetime_value,
                    break_even_months=projection.break_even_months,
                )
            except Exception as e:
                logger.error(f"Error calculating revenue projection: {str(e)}")
                return None

    @strawberry.type
    class MonetizationMutation:
        """Monetization mutation resolvers."""

        @strawberry.mutation
        async def create_subscription_model(
            self, info: Info, input: SubscriptionModelInput
        ) -> Optional[SubscriptionModelType]:
            """
            Create a new subscription model.

            Args:
                info: GraphQL resolver info
                input: Subscription model input

            Returns:
                Created subscription model if successful, None otherwise
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return None

            # Create subscription model
            try:
                model = await service.create_subscription_model(
                    name=input.name,
                    description=input.description,
                    subscription_type=input.subscription_type.value,
                )

                return SubscriptionModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    subscription_type=SubscriptionTypeEnum(model.subscription_type),
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error creating subscription model: {str(e)}")
                return None

        @strawberry.mutation
        async def update_subscription_model(
            self, info: Info, id: str, input: SubscriptionModelInput
        ) -> Optional[SubscriptionModelType]:
            """
            Update a subscription model.

            Args:
                info: GraphQL resolver info
                id: Subscription model ID
                input: Subscription model input

            Returns:
                Updated subscription model if successful, None otherwise
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return None

            # Update subscription model
            try:
                model = await service.update_subscription_model(
                    id=id,
                    name=input.name,
                    description=input.description,
                    subscription_type=input.subscription_type.value,
                )

                if not model:
                    return None

                return SubscriptionModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    subscription_type=SubscriptionTypeEnum(model.subscription_type),
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error updating subscription model: {str(e)}")
                return None

        @strawberry.mutation
        async def delete_subscription_model(self, info: Info, id: str) -> bool:
            """
            Delete a subscription model.

            Args:
                info: GraphQL resolver info
                id: Subscription model ID

            Returns:
                True if successful, False otherwise
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return False

            # Delete subscription model
            try:
                success = await service.delete_subscription_model(id)
                return success
            except Exception as e:
                logger.error(f"Error deleting subscription model: {str(e)}")
                return False

        @strawberry.mutation
        async def add_pricing_tier(
            self, info: Info, subscription_model_id: str, input: PricingTierInput
        ) -> Optional[SubscriptionModelType]:
            """
            Add a pricing tier to a subscription model.

            Args:
                info: GraphQL resolver info
                subscription_model_id: Subscription model ID
                input: Pricing tier input

            Returns:
                Updated subscription model if successful, None otherwise
            """
            # Get monetization service from context
            service = info.context["services"].get("monetization")
            if not service:
                logger.warning("Monetization service not available")
                return None

            # Add pricing tier
            try:
                model = await service.add_pricing_tier(
                    subscription_model_id=subscription_model_id,
                    name=input.name,
                    description=input.description,
                    price=input.price,
                    billing_period=input.billing_period.value,
                )

                if not model:
                    return None

                return SubscriptionModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    subscription_type=SubscriptionTypeEnum(model.subscription_type),
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error adding pricing tier: {str(e)}")
                return None
