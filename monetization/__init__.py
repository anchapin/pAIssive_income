"""
"""
Monetization package for the pAIssive Income project.
Monetization package for the pAIssive Income project.


This package provides tools and templates for monetizing AI-powered software tools
This package provides tools and templates for monetizing AI-powered software tools
through subscription models and other revenue streams.
through subscription models and other revenue streams.
"""
"""


from .calculator import MonetizationCalculator
from .calculator import MonetizationCalculator
from .invoice import Invoice, InvoiceItem, InvoiceStatus
from .invoice import Invoice, InvoiceItem, InvoiceStatus
from .invoice_delivery import InvoiceDelivery, InvoiceFormatter
from .invoice_delivery import InvoiceDelivery, InvoiceFormatter
from .invoice_manager import InvoiceManager
from .invoice_manager import InvoiceManager
from .metered_billing import MeteredBillingPricing, MeteringInterval
from .metered_billing import MeteredBillingPricing, MeteringInterval
from .mock_payment_processor import MockPaymentProcessor
from .mock_payment_processor import MockPaymentProcessor
from .payment_method import PaymentMethod
from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager
from .payment_method_manager import PaymentMethodManager
from .payment_processor import PaymentProcessor
from .payment_processor import PaymentProcessor
from .payment_processor_factory import factory as payment_processor_factory
from .payment_processor_factory import factory as payment_processor_factory
from .pricing_calculator import PricingCalculator
from .pricing_calculator import PricingCalculator
from .prorated_billing import ProratedBilling
from .prorated_billing import ProratedBilling
from .receipt import Receipt, ReceiptItem
from .receipt import Receipt, ReceiptItem
from .receipt_manager import ReceiptManager
from .receipt_manager import ReceiptManager
from .revenue_projector import RevenueProjector
from .revenue_projector import RevenueProjector
from .subscription import SubscriptionPlan, SubscriptionTier
from .subscription import SubscriptionPlan, SubscriptionTier
from .subscription_manager import SubscriptionManager
from .subscription_manager import SubscriptionManager
from .subscription_models import FreemiumModel, SubscriptionModel
from .subscription_models import FreemiumModel, SubscriptionModel
from .tiered_pricing import (TieredPricingCalculator, TieredPricingRule,
from .tiered_pricing import (TieredPricingCalculator, TieredPricingRule,
VolumeDiscount)
VolumeDiscount)
from .transaction import Transaction, TransactionStatus, TransactionType
from .transaction import Transaction, TransactionStatus, TransactionType
from .transaction_manager import TransactionManager
from .transaction_manager import TransactionManager
from .usage_based_pricing import UsageBasedPricing
from .usage_based_pricing import UsageBasedPricing
from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker
from .user_subscription import Subscription, SubscriptionStatus
from .user_subscription import Subscription, SubscriptionStatus


__all__
__all__


# Import billing calculation
# Import billing calculation
from .billing_calculator import (BillingCalculator, PricingModel,
from .billing_calculator import (BillingCalculator, PricingModel,
PricingPackage, PricingRule, PricingTier)
PricingPackage, PricingRule, PricingTier)
# Import custom pricing
# Import custom pricing
from .custom_pricing import (ConditionalPricingRule,
from .custom_pricing import (ConditionalPricingRule,
CustomerSegmentPricingRule,
CustomerSegmentPricingRule,
CustomPricingCalculator, CustomPricingRule,
CustomPricingCalculator, CustomPricingRule,
FormulaBasedPricingRule, SeasonalPricingRule,
FormulaBasedPricingRule, SeasonalPricingRule,
TimeBasedPricingRule)
TimeBasedPricingRule)


# Import invoice generation
# Import invoice generation
# Import payment processing
# Import payment processing
(
(
PaymentProcessorFactory,
PaymentProcessorFactory,
)
)
# Import promotional pricing
# Import promotional pricing
from .promotional_pricing import (BundlePromotion, CouponPromotion,
from .promotional_pricing import (BundlePromotion, CouponPromotion,
DiscountType, LoyaltyPromotion, Promotion,
DiscountType, LoyaltyPromotion, Promotion,
PromotionManager, PromotionStatus,
PromotionManager, PromotionStatus,
PromotionType, ReferralPromotion,
PromotionType, ReferralPromotion,
TimeLimitedPromotion)
TimeLimitedPromotion)
# Import subscription management
# Import subscription management
# Import subscription analytics
# Import subscription analytics
from .subscription_analytics import (ChurnAnalysis, SubscriptionForecasting,
from .subscription_analytics import (ChurnAnalysis, SubscriptionForecasting,
SubscriptionMetrics)
SubscriptionMetrics)


# Import subscription models
# Import subscription models
# Import usage-based pricing
# Import usage-based pricing
(
(
ConsumptionBasedPricing,
ConsumptionBasedPricing,
HybridUsagePricing,
HybridUsagePricing,
PayAsYouGoPricing,
PayAsYouGoPricing,
TieredUsagePricing,
TieredUsagePricing,
)
)
# Import usage tracking
# Import usage tracking
from .usage_tracking import (UsageCategory, UsageLimit, UsageMetric,
from .usage_tracking import (UsageCategory, UsageLimit, UsageMetric,
UsageQuota, UsageRecord)
UsageQuota, UsageRecord)


= [
= [
# Subscription models
# Subscription models
"SubscriptionModel",
"SubscriptionModel",
"FreemiumModel",
"FreemiumModel",
"PricingCalculator",
"PricingCalculator",
"RevenueProjector",
"RevenueProjector",
"MonetizationCalculator",
"MonetizationCalculator",
# Subscription management
# Subscription management
"SubscriptionPlan",
"SubscriptionPlan",
"SubscriptionTier",
"SubscriptionTier",
"Subscription",
"Subscription",
"SubscriptionStatus",
"SubscriptionStatus",
"SubscriptionManager",
"SubscriptionManager",
# Payment processing
# Payment processing
"PaymentProcessor",
"PaymentProcessor",
"MockPaymentProcessor",
"MockPaymentProcessor",
"PaymentProcessorFactory",
"PaymentProcessorFactory",
"payment_processor_factory",
"payment_processor_factory",
"PaymentMethod",
"PaymentMethod",
"PaymentMethodManager",
"PaymentMethodManager",
"Transaction",
"Transaction",
"TransactionStatus",
"TransactionStatus",
"TransactionType",
"TransactionType",
"TransactionManager",
"TransactionManager",
"Receipt",
"Receipt",
"ReceiptItem",
"ReceiptItem",
"ReceiptManager",
"ReceiptManager",
# Usage tracking
# Usage tracking
"UsageRecord",
"UsageRecord",
"UsageLimit",
"UsageLimit",
"UsageQuota",
"UsageQuota",
"UsageMetric",
"UsageMetric",
"UsageCategory",
"UsageCategory",
"UsageTracker",
"UsageTracker",
# Billing calculation
# Billing calculation
"PricingModel",
"PricingModel",
"PricingTier",
"PricingTier",
"PricingPackage",
"PricingPackage",
"PricingRule",
"PricingRule",
"BillingCalculator",
"BillingCalculator",
"VolumeDiscount",
"VolumeDiscount",
"TieredPricingRule",
"TieredPricingRule",
"TieredPricingCalculator",
"TieredPricingCalculator",
"ProratedBilling",
"ProratedBilling",
# Usage-based pricing
# Usage-based pricing
"UsageBasedPricing",
"UsageBasedPricing",
"PayAsYouGoPricing",
"PayAsYouGoPricing",
"TieredUsagePricing",
"TieredUsagePricing",
"ConsumptionBasedPricing",
"ConsumptionBasedPricing",
"HybridUsagePricing",
"HybridUsagePricing",
"MeteredBillingPricing",
"MeteredBillingPricing",
"MeteringInterval",
"MeteringInterval",
# Custom pricing
# Custom pricing
"CustomPricingRule",
"CustomPricingRule",
"CustomPricingCalculator",
"CustomPricingCalculator",
"TimeBasedPricingRule",
"TimeBasedPricingRule",
"SeasonalPricingRule",
"SeasonalPricingRule",
"CustomerSegmentPricingRule",
"CustomerSegmentPricingRule",
"ConditionalPricingRule",
"ConditionalPricingRule",
"FormulaBasedPricingRule",
"FormulaBasedPricingRule",
# Promotional pricing
# Promotional pricing
"Promotion",
"Promotion",
"PromotionManager",
"PromotionManager",
"PromotionStatus",
"PromotionStatus",
"PromotionType",
"PromotionType",
"DiscountType",
"DiscountType",
"TimeLimitedPromotion",
"TimeLimitedPromotion",
"CouponPromotion",
"CouponPromotion",
"ReferralPromotion",
"ReferralPromotion",
"BundlePromotion",
"BundlePromotion",
"LoyaltyPromotion",
"LoyaltyPromotion",
# Invoice generation
# Invoice generation
"Invoice",
"Invoice",
"InvoiceItem",
"InvoiceItem",
"InvoiceStatus",
"InvoiceStatus",
"InvoiceManager",
"InvoiceManager",
"InvoiceDelivery",
"InvoiceDelivery",
"InvoiceFormatter",
"InvoiceFormatter",
# Subscription analytics
# Subscription analytics
"SubscriptionMetrics",
"SubscriptionMetrics",
"ChurnAnalysis",
"ChurnAnalysis",
"SubscriptionForecasting",
"SubscriptionForecasting",
]
]