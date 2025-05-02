"""
Example of webhook usage in the application.

This module demonstrates how to integrate webhooks with other parts of the application.
"""

import asyncio
import logging
from typing import Any, Dict

from ..schemas.webhook import WebhookEventType
from ..services.webhook_service import WebhookService

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NicheAnalysisService:
    """Example niche analysis service with webhook integration."""

    def __init__(self):
        """Initialize the service."""
        self.webhook_service = WebhookService()

    async def run_niche_analysis(
        self, analysis_id: str, niche: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run niche analysis with webhook notifications.

        Args:
            analysis_id: Unique ID for this analysis
            niche: Niche to analyze
            parameters: Analysis parameters

        Returns:
            Analysis results
        """
        # Trigger analysis started event
        await self.webhook_service.trigger_event(
            WebhookEventType.NICHE_ANALYSIS_STARTED,
            {"analysis_id": analysis_id, "niche": niche, "parameters": parameters},
        )

        try:
            # Simulate analysis running
            logger.info(f"Running niche analysis for '{niche}'")
            await asyncio.sleep(5)  # Simulate processing time

            # Generate sample results
            results = {
                "analysis_id": analysis_id,
                "niche": niche,
                "profitability_score": 85,
                "competition_score": 65,
                "market_size": "Medium",
                "estimated_monthly_revenue": "$2,500 - $5,000",
                "recommended_approach": "Content marketing with affiliate products",
                "keywords": [
                    {
                        "keyword": "best budget gaming laptop",
                        "volume": 12000,
                        "difficulty": "Medium",
                    },
                    {
                        "keyword": "gaming laptop under 1000",
                        "volume": 8500,
                        "difficulty": "Medium-High",
                    },
                    {
                        "keyword": "affordable gaming laptop reviews",
                        "volume": 5500,
                        "difficulty": "Low",
                    },
                ],
            }

            # Trigger analysis completed event
            await self.webhook_service.trigger_niche_analysis_completed(
                analysis_id=analysis_id, results=results
            )

            return results

        except Exception as e:
            error = str(e)
            logger.error(f"Niche analysis failed: {error}")

            # Trigger analysis failed event
            await self.webhook_service.trigger_event(
                WebhookEventType.NICHE_ANALYSIS_FAILED,
                {"analysis_id": analysis_id, "niche": niche, "error": error},
            )

            # Re-raise the exception
            raise


class MonetizationService:
    """Example monetization service with webhook integration."""

    def __init__(self):
        """Initialize the service."""
        self.webhook_service = WebhookService()

    async def create_subscription(
        self, user_id: str, plan_id: str, payment_method: str
    ) -> Dict[str, Any]:
        """
        Create a subscription with webhook notifications.

        Args:
            user_id: User ID
            plan_id: Subscription plan ID
            payment_method: Payment method ID

        Returns:
            Created subscription
        """
        # Create the subscription
        subscription = {
            "id": "sub_" + user_id[:8],
            "user_id": user_id,
            "plan_id": plan_id,
            "status": "active",
            "created_at": "2025-04-28T12:00:00Z",
            "current_period_end": "2025-05-28T12:00:00Z",
            "payment_method": payment_method,
        }

        # Trigger subscription created event
        await self.webhook_service.trigger_subscription_created(
            subscription_id=subscription["id"], subscription_data=subscription
        )

        return subscription

    async def process_payment(
        self, payment_id: str, amount: float, user_id: str
    ) -> Dict[str, Any]:
        """
        Process a payment with webhook notifications.

        Args:
            payment_id: Payment ID
            amount: Payment amount
            user_id: User ID

        Returns:
            Processed payment
        """
        # Process the payment
        payment = {
            "id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "currency": "USD",
            "status": "succeeded",
            "created_at": "2025-04-28T12:05:00Z",
        }

        # Trigger payment received event
        await self.webhook_service.trigger_payment_received(
            payment_id=payment_id, payment_data=payment
        )

        return payment


# Example usage
async def main():
    # Create services
    niche_service = NicheAnalysisService()
    monetization_service = MonetizationService()

    # Example: Register webhook
    webhook_service = WebhookService()
    webhook = await webhook_service.register_webhook(
        url="https://example.com/webhook",
        events=[
            WebhookEventType.NICHE_ANALYSIS_STARTED,
            WebhookEventType.NICHE_ANALYSIS_COMPLETED,
            WebhookEventType.NICHE_ANALYSIS_FAILED,
            WebhookEventType.SUBSCRIPTION_CREATED,
            WebhookEventType.PAYMENT_RECEIVED,
        ],
        description="Example webhook for notifications",
        secret="your-webhook-secret",
    )
    logger.info(f"Registered webhook: {webhook['id']}")

    # Run niche analysis
    try:
        results = await niche_service.run_niche_analysis(
            analysis_id="na_123456",
            niche="budget gaming laptops",
            parameters={
                "depth": "comprehensive",
                "include_keywords": True,
                "competitor_analysis": True,
            },
        )
        logger.info(f"Analysis results: {results}")
    except Exception as e:
        logger.error(f"Analysis error: {e}")

    # Create subscription
    subscription = await monetization_service.create_subscription(
        user_id="user_12345", plan_id="pro_monthly", payment_method="pm_card_visa"
    )
    logger.info(f"Created subscription: {subscription}")

    # Process payment
    payment = await monetization_service.process_payment(
        payment_id="py_123456", amount=49.99, user_id="user_12345"
    )
    logger.info(f"Processed payment: {payment}")


if __name__ == "__main__":
    asyncio.run(main())
