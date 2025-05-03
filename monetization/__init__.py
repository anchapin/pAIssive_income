"""
Monetization package for the pAIssive Income project.

This package provides tools and templates for monetizing AI-powered software tools
through subscription models and other revenue streams.
"""

from .calculator import MonetizationCalculator


from .invoice import Invoice, InvoiceItem, InvoiceStatus
from .invoice_delivery import InvoiceDelivery, InvoiceFormatter
from .invoice_manager import InvoiceManager
from .metered_billing import MeteredBillingPricing, MeteringInterval
from .mock_payment_processor import MockPaymentProcessor
from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager


from .payment_processor import PaymentProcessor
from .payment_processor_factory import 
from .payment_processor_factory import factory as payment_processor_factory
from .pricing_calculator import PricingCalculator


from .prorated_billing import ProratedBilling
from .receipt import Receipt, ReceiptItem
from .receipt_manager import ReceiptManager
from .revenue_projector import RevenueProjector


from .subscription import SubscriptionPlan, SubscriptionTier


from .subscription_manager import SubscriptionManager


from .subscription_models import FreemiumModel, SubscriptionModel
from .tiered_pricing import TieredPricingCalculator, TieredPricingRule, VolumeDiscount
from .transaction import Transaction, TransactionStatus, TransactionType
from .transaction_manager import TransactionManager


from .usage_based_pricing import UsageBasedPricing
from .usage_pricing_strategies import 
from .usage_tracker import UsageTracker


from .user_subscription import Subscription, SubscriptionStatus

__all__ 

# Import billing calculation
from .billing_calculator import (
    BillingCalculator,
    PricingModel,
    PricingPackage,
    PricingRule,
    PricingTier,
)
# Import custom pricing
from .custom_pricing import (
    ConditionalPricingRule,
    CustomerSegmentPricingRule,
    CustomPricingCalculator,
    CustomPricingRule,
    FormulaBasedPricingRule,
    SeasonalPricingRule,
    TimeBasedPricingRule,
)

# Import invoice generation
# Import payment processing
(
    PaymentProcessorFactory,
)
# Import promotional pricing
from .promotional_pricing import (
    BundlePromotion,
    CouponPromotion,
    DiscountType,
    LoyaltyPromotion,
    Promotion,
    PromotionManager,
    PromotionStatus,
    PromotionType,
    ReferralPromotion,
    TimeLimitedPromotion,
)
# Import subscription management
# Import subscription analytics
from .subscription_analytics import (
    ChurnAnalysis,
    SubscriptionForecasting,
    SubscriptionMetrics,
)
# Import subscription models
# Import usage-based pricing
(
    ConsumptionBasedPricing,
    HybridUsagePricing,
    PayAsYouGoPricing,
    TieredUsagePricing,
)
# Import usage tracking
from .usage_tracking import (
    UsageCategory,
    UsageLimit,
    UsageMetric,
    UsageQuota,
    UsageRecord,
)
= [
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
    # Usage-based pricing
    "UsageBasedPricing",
    "PayAsYouGoPricing",
    "TieredUsagePricing",
    "ConsumptionBasedPricing",
    "HybridUsagePricing",
    "MeteredBillingPricing",
    "MeteringInterval",
    # Custom pricing
    "CustomPricingRule",
    "CustomPricingCalculator",
    "TimeBasedPricingRule",
    "SeasonalPricingRule",
    "CustomerSegmentPricingRule",
    "ConditionalPricingRule",
    "FormulaBasedPricingRule",
    # Promotional pricing
    "Promotion",
    "PromotionManager",
    "PromotionStatus",
    "PromotionType",
    "DiscountType",
    "TimeLimitedPromotion",
    "CouponPromotion",
    "ReferralPromotion",
    "BundlePromotion",
    "LoyaltyPromotion",
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