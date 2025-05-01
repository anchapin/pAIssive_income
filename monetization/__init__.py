"""
Monetization package for the pAIssive Income project.

This package provides tools and templates for monetizing AI-powered software tools
through subscription models and other revenue streams.
"""

# Import billing calculation
from .billing_calculator import (
    BillingCalculator,
    PricingModel,
    PricingPackage,
    PricingRule,
    PricingTier,
)
from .calculator import MonetizationCalculator

# Import invoice generation
from .invoice import Invoice, InvoiceItem, InvoiceStatus
from .invoice_delivery import InvoiceDelivery, InvoiceFormatter
from .invoice_manager import InvoiceManager
from .mock_payment_processor import MockPaymentProcessor
from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager

# Import payment processing
from .payment_processor import PaymentProcessor
from .payment_processor_factory import PaymentProcessorFactory
from .payment_processor_factory import factory as payment_processor_factory
from .pricing_calculator import PricingCalculator
from .prorated_billing import ProratedBilling
from .receipt import Receipt, ReceiptItem
from .receipt_manager import ReceiptManager
from .revenue_projector import RevenueProjector

# Import subscription management
from .subscription import SubscriptionPlan, SubscriptionTier

# Import subscription analytics
from .subscription_analytics import (
    ChurnAnalysis,
    SubscriptionForecasting,
    SubscriptionMetrics,
)
from .subscription_manager import SubscriptionManager

# Import subscription models
from .subscription_models import FreemiumModel, SubscriptionModel
from .tiered_pricing import TieredPricingCalculator, TieredPricingRule, VolumeDiscount
from .transaction import Transaction, TransactionStatus, TransactionType
from .transaction_manager import TransactionManager
from .usage_tracker import UsageTracker

# Import usage tracking
from .usage_tracking import (
    UsageCategory,
    UsageLimit,
    UsageMetric,
    UsageQuota,
    UsageRecord,
)
from .user_subscription import Subscription, SubscriptionStatus

__all__ = [
    # Subscription models
    "SubscriptionModel",
    "FreemiumModel",
    "PricingCalculator",
    "RevenueProjector",
    "MonetizationCalculator",
    # Subscription management
    "SubscriptionPlan",
    "SubscriptionTier",
    "Subscription",
    "SubscriptionStatus",
    "SubscriptionManager",
    # Payment processing
    "PaymentProcessor",
    "MockPaymentProcessor",
    "PaymentProcessorFactory",
    "payment_processor_factory",
    "PaymentMethod",
    "PaymentMethodManager",
    "Transaction",
    "TransactionStatus",
    "TransactionType",
    "TransactionManager",
    "Receipt",
    "ReceiptItem",
    "ReceiptManager",
    # Usage tracking
    "UsageRecord",
    "UsageLimit",
    "UsageQuota",
    "UsageMetric",
    "UsageCategory",
    "UsageTracker",
    # Billing calculation
    "PricingModel",
    "PricingTier",
    "PricingPackage",
    "PricingRule",
    "BillingCalculator",
    "VolumeDiscount",
    "TieredPricingRule",
    "TieredPricingCalculator",
    "ProratedBilling",
    # Invoice generation
    "Invoice",
    "InvoiceItem",
    "InvoiceStatus",
    "InvoiceManager",
    "InvoiceDelivery",
    "InvoiceFormatter",
    # Subscription analytics
    "SubscriptionMetrics",
    "ChurnAnalysis",
    "SubscriptionForecasting",
]
