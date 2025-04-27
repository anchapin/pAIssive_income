"""
Monetization package for the pAIssive Income project.

This package provides tools and templates for monetizing AI-powered software tools
through subscription models and other revenue streams.
"""

# Import subscription models
from .subscription_models import SubscriptionModel, FreemiumModel
from .pricing_calculator import PricingCalculator
from .revenue_projector import RevenueProjector

# Import subscription management
from .subscription import SubscriptionPlan, SubscriptionTier
from .user_subscription import Subscription, SubscriptionStatus
from .subscription_manager import SubscriptionManager

# Import payment processing
from .payment_processor import PaymentProcessor
from .mock_payment_processor import MockPaymentProcessor
from .payment_processor_factory import PaymentProcessorFactory, factory as payment_processor_factory
from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager
from .transaction import Transaction, TransactionStatus, TransactionType
from .transaction_manager import TransactionManager
from .receipt import Receipt, ReceiptItem
from .receipt_manager import ReceiptManager

# Import usage tracking
from .usage_tracking import UsageRecord, UsageLimit, UsageQuota, UsageMetric, UsageCategory
from .usage_tracker import UsageTracker

# Import billing calculation
from .billing_calculator import PricingModel, PricingTier, PricingPackage, PricingRule, BillingCalculator
from .tiered_pricing import VolumeDiscount, TieredPricingRule, TieredPricingCalculator
from .prorated_billing import ProratedBilling

# Import invoice generation
from .invoice import Invoice, InvoiceItem, InvoiceStatus
from .invoice_manager import InvoiceManager
from .invoice_delivery import InvoiceDelivery, InvoiceFormatter

# Import subscription analytics
from .subscription_analytics import SubscriptionMetrics, ChurnAnalysis, SubscriptionForecasting

__all__ = [
    # Subscription models
    'SubscriptionModel',
    'FreemiumModel',
    'PricingCalculator',
    'RevenueProjector',

    # Subscription management
    'SubscriptionPlan',
    'SubscriptionTier',
    'Subscription',
    'SubscriptionStatus',
    'SubscriptionManager',

    # Payment processing
    'PaymentProcessor',
    'MockPaymentProcessor',
    'PaymentProcessorFactory',
    'payment_processor_factory',
    'PaymentMethod',
    'PaymentMethodManager',
    'Transaction',
    'TransactionStatus',
    'TransactionType',
    'TransactionManager',
    'Receipt',
    'ReceiptItem',
    'ReceiptManager',

    # Usage tracking
    'UsageRecord',
    'UsageLimit',
    'UsageQuota',
    'UsageMetric',
    'UsageCategory',
    'UsageTracker',

    # Billing calculation
    'PricingModel',
    'PricingTier',
    'PricingPackage',
    'PricingRule',
    'BillingCalculator',
    'VolumeDiscount',
    'TieredPricingRule',
    'TieredPricingCalculator',
    'ProratedBilling',

    # Invoice generation
    'Invoice',
    'InvoiceItem',
    'InvoiceStatus',
    'InvoiceManager',
    'InvoiceDelivery',
    'InvoiceFormatter',

    # Subscription analytics
    'SubscriptionMetrics',
    'ChurnAnalysis',
    'SubscriptionForecasting',
]
