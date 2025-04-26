"""
Monetization package for the pAIssive Income project.

This package provides tools and templates for monetizing AI-powered software tools
through subscription models and other revenue streams.
"""

from .subscription_models import SubscriptionModel, FreemiumModel
from .pricing_calculator import PricingCalculator
from .revenue_projector import RevenueProjector

__all__ = [
    'SubscriptionModel',
    'FreemiumModel',
    'PricingCalculator',
    'RevenueProjector',
]
