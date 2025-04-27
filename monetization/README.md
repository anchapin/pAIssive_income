# Monetization

This directory contains tools and templates for monetizing AI-powered software tools through subscription models and other revenue streams.

## Overview

The monetization module is organized into five main components:

1. **Subscription Models**: Classes for creating and managing different subscription models and pricing tiers
2. **Pricing Calculator**: Tools to calculate optimal pricing for your products
3. **Revenue Projector**: Tools to project revenue based on different scenarios
4. **Subscription Management**: Classes for managing user subscriptions, including creation, renewal, and cancellation
5. **Payment Processing**: Classes for processing payments, managing payment methods, and handling subscriptions

## Subscription Models

The `subscription_models.py` module provides classes for creating and managing different subscription models, including:

- `SubscriptionModel`: Base class for all subscription models
- `FreemiumModel`: Freemium model with a free tier and paid tiers

Each model includes methods for:

- Tier definitions
- Feature allocation
- Pricing structure
- Billing cycle options

## Pricing Calculator

The `pricing_calculator.py` module provides tools to calculate optimal pricing for your products, including:

- `PricingCalculator`: Base class for all pricing calculators
- Methods for calculating optimal prices based on different strategies
- Price sensitivity analysis tools

## Revenue Projector

The `revenue_projector.py` module provides tools to project revenue based on different scenarios, including:

- `RevenueProjector`: Class for projecting revenue for subscription-based products
- User acquisition projections
- Conversion rate projections
- Churn rate projections
- Lifetime value calculations
- Cash flow projections

## Subscription Management

The subscription management system includes:

- `subscription.py`: Defines the `SubscriptionPlan` and `SubscriptionTier` classes for creating and managing subscription plans and tiers
- `user_subscription.py`: Defines the `Subscription` class for managing user subscriptions
- `subscription_manager.py`: Defines the `SubscriptionManager` class for managing subscription lifecycles
- `subscription_analytics.py`: Provides classes for analyzing subscription data, including metrics, churn analysis, and forecasting

## Payment Processing

The payment processing system includes:

- `payment_processor.py`: Defines the `PaymentProcessor` abstract base class
- `mock_payment_processor.py`: Provides a mock implementation for testing and development
- `payment_processor_factory.py`: Provides a factory for creating and managing payment processor instances
- `payment_method.py`: Defines the `PaymentMethod` class for managing payment methods
- `payment_method_manager.py`: Provides the `PaymentMethodManager` class for storing and retrieving payment methods
- `transaction.py`: Defines the `Transaction` class for managing payment transactions
- `transaction_manager.py`: Provides the `TransactionManager` class for processing and tracking transactions
- `receipt.py`: Defines the `Receipt` and `ReceiptItem` classes for generating receipts
- `receipt_manager.py`: Provides the `ReceiptManager` class for managing receipts

## Usage Tracking

The usage tracking system includes:

- `usage_tracking.py`: Defines the `UsageRecord`, `UsageLimit`, and `UsageQuota` classes for tracking usage
- `usage_tracker.py`: Provides the `UsageTracker` class for managing usage records, limits, and quotas

## Billing Calculation

The billing calculation system includes:

- `billing_calculator.py`: Defines the `BillingCalculator` class for calculating billing based on usage
- `tiered_pricing.py`: Provides the `TieredPricingCalculator` class for implementing tiered pricing models
- `prorated_billing.py`: Implements the `ProratedBilling` class for calculating prorated billing

## Invoice Generation

The invoice generation system includes:

- `invoice.py`: Defines the `Invoice` and `InvoiceItem` classes for generating and managing invoices
- `invoice_manager.py`: Provides the `InvoiceManager` class for storing and retrieving invoices
- `invoice_delivery.py`: Implements the `InvoiceDelivery` class for delivering invoices to customers

## Usage

To use these tools, import the relevant modules and call the functions with your specific parameters.

### Subscription Models Example

```python
from monetization.subscription_models import FreemiumModel
from monetization.pricing_calculator import PricingCalculator
from monetization.revenue_projector import RevenueProjector

# Create a freemium subscription model
model = FreemiumModel(
    name="AI Tool Subscription",
    description="Subscription model for an AI-powered tool"
)

# Add features and tiers
feature1 = model.add_feature(
    name="Basic Feature",
    description="A basic feature"
)

model.add_feature_to_free_tier(feature1["id"])

pro_tier = model.add_paid_tier(
    name="Pro",
    description="Pro tier with advanced features",
    price_monthly=19.99
)

# Calculate optimal pricing
calculator = PricingCalculator(
    name="AI Tool Pricing Calculator",
    description="Pricing calculator for an AI-powered tool"
)

analysis = calculator.analyze_price_sensitivity(
    base_price=19.99,
    market_size=10000,
    price_elasticity=1.2
)

# Project revenue
projector = RevenueProjector(
    name="AI Tool Revenue Projector",
    description="Revenue projector for an AI-powered tool",
    initial_users=0,
    user_acquisition_rate=50,
    conversion_rate=0.2,
    churn_rate=0.05
)

projection = projector.project_revenue(
    subscription_model=model,
    prices={pro_tier["id"]: 19.99},
    months=36
)

print(f"3-year revenue projection: ${projection['total_revenue']:.2f}")
```

### Subscription Management Example

```python
from monetization import SubscriptionPlan, SubscriptionManager

# Create a subscription plan
plan = SubscriptionPlan(
    name="AI Tool Subscription",
    description="Subscription plan for an AI-powered tool"
)

# Add features
feature1 = plan.add_feature(
    name="Content Generation",
    description="Generate content using AI"
)

# Add tiers
basic_tier = plan.add_tier(
    name="Basic",
    description="Essential features",
    price_monthly=9.99
)

plan.add_feature_to_tier(basic_tier["id"], feature1["id"])

# Create a subscription manager
manager = SubscriptionManager()
manager.add_plan(plan)

# Create a subscription
user_id = "user123"
subscription = manager.create_subscription(
    user_id=user_id,
    plan_id=plan.id,
    tier_id=basic_tier["id"]
)

print(f"Subscription created: {subscription}")
```

### Payment Processing Example

```python
from monetization import payment_processor_factory

# Create a payment processor
processor = payment_processor_factory.create_processor(
    processor_type="mock",
    processor_id="demo",
    config={"name": "Demo Processor"}
)

# Create a customer
customer = processor.create_customer(
    email="customer@example.com",
    name="Demo Customer"
)

# Create a payment method
payment_method = processor.create_payment_method(
    customer_id=customer["id"],
    payment_type="card",
    payment_details={
        "number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2030,
        "cvc": "123"
    }
)

# Process a payment
payment = processor.process_payment(
    amount=19.99,
    currency="USD",
    payment_method_id=payment_method["id"],
    description="Monthly subscription"
)

print(f"Payment processed: {payment['id']}")
```

### Payment Method Management Example

```python
from monetization import PaymentMethod, PaymentMethodManager

# Create a payment method manager
manager = PaymentMethodManager(storage_dir="payment_methods")

# Add a credit card payment method
card_payment = manager.add_payment_method(
    customer_id="cust_123",
    payment_type=PaymentMethod.TYPE_CARD,
    payment_details={
        "number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2030,
        "cvc": "123",
        "name": "John Doe"
    },
    set_as_default=True
)

# Add a bank account payment method
bank_payment = manager.add_payment_method(
    customer_id="cust_123",
    payment_type=PaymentMethod.TYPE_BANK_ACCOUNT,
    payment_details={
        "account_number": "000123456789",
        "routing_number": "110000000",
        "account_type": "checking",
        "bank_name": "Test Bank"
    }
)

# Get customer payment methods
payment_methods = manager.get_customer_payment_methods("cust_123")
for pm in payment_methods:
    default_str = " (default)" if pm.is_default else ""
    print(f"- {pm}{default_str}")

# Get default payment method
default_pm = manager.get_default_payment_method("cust_123")
print(f"Default payment method: {default_pm}")

# Set bank account as default
manager.set_default_payment_method("cust_123", bank_payment.id)
```

### Transaction Management Example

```python
from monetization import (
    Transaction, TransactionStatus, TransactionType,
    TransactionManager, MockPaymentProcessor
)

# Create a payment processor
processor = MockPaymentProcessor({
    "name": "Demo Processor",
    "success_rate": 1.0  # Always succeed for demo
})

# Create a transaction manager
manager = TransactionManager(
    payment_processor=processor,
    storage_dir="transactions"
)

# Create a transaction
transaction = manager.create_transaction(
    amount=29.99,
    currency="USD",
    customer_id="cust_123",
    payment_method_id="pm_456",
    description="Premium subscription payment",
    metadata={"subscription_id": "sub_789"}
)

# Process the transaction
processed_transaction = manager.process_transaction(transaction.id)

if processed_transaction.is_successful():
    print("Payment was successful!")
else:
    print(f"Payment failed: {processed_transaction.error['message']}")

# Create a partial refund
refund_transaction = manager.refund_transaction(
    transaction_id=transaction.id,
    amount=10.00,
    reason="Customer request"
)

# Get transaction summary
summary = manager.get_transaction_summary()
print(f"Total transactions: {summary['total_count']}")
print(f"Net amount: ${summary['net_amount']:.2f}")
```

### Receipt Generation Example

```python
from monetization import (
    Transaction, TransactionStatus,
    Receipt, ReceiptManager
)

# Create a transaction
transaction = Transaction(
    amount=49.99,
    currency="USD",
    customer_id="cust_123",
    payment_method_id="pm_456",
    description="Annual subscription payment",
    metadata={"subscription_id": "sub_789"}
)

# Set transaction as successful
transaction.update_status(TransactionStatus.SUCCEEDED, "Payment successful")

# Create a receipt manager
manager = ReceiptManager(
    company_info={
        "name": "AI Tools Inc.",
        "email": "support@aitools.com",
        "website": "https://aitools.com"
    }
)

# Generate a receipt
receipt = manager.generate_receipt(
    transaction=transaction,
    customer_info={
        "name": "John Doe",
        "email": "john.doe@example.com"
    },
    items=[
        {
            "description": "Premium Subscription (Annual)",
            "quantity": 1,
            "unit_price": 49.99,
            "tax_rate": 0.0825  # 8.25% tax
        }
    ]
)

# Add custom information
receipt.add_custom_field("Subscription Period", "Jan 1, 2023 - Dec 31, 2023")
receipt.set_notes("Thank you for your business!")

# Save receipt to files
receipt.save_to_file("receipt.txt", format="text")
receipt.save_to_file("receipt.html", format="html")

# Send receipt by email
manager.send_receipt(
    receipt_id=receipt.id,
    email="john.doe@example.com",
    subject="Your Receipt",
    format="html"
)
```

### Usage Tracking Example

```python
from monetization import (
    UsageMetric, UsageCategory,
    UsageLimit, UsageTracker
)

# Create a usage tracker
tracker = UsageTracker(storage_dir="usage_data")

# Add a usage limit
limit = UsageLimit(
    customer_id="cust_123",
    metric=UsageMetric.API_CALL,
    max_quantity=1000,
    period=UsageLimit.PERIOD_MONTHLY,
    category=UsageCategory.INFERENCE,
    resource_type="model",
    metadata={"tier": "basic"}
)

tracker.add_limit(limit)

# Check if usage is allowed
allowed, reason, quota = tracker.check_usage_allowed(
    customer_id="cust_123",
    metric=UsageMetric.API_CALL,
    quantity=10,
    category=UsageCategory.INFERENCE,
    resource_type="model"
)

if allowed:
    # Track usage
    record, updated_quota, exceeded = tracker.track_usage(
        customer_id="cust_123",
        metric=UsageMetric.API_CALL,
        quantity=10,
        category=UsageCategory.INFERENCE,
        resource_id="model_gpt4",
        resource_type="model",
        metadata={"endpoint": "/v1/completions"}
    )

    print(f"Tracked usage: {record}")

    if updated_quota:
        print(f"Updated quota: {updated_quota.used_quantity}/{updated_quota.allocated_quantity}")

    if exceeded:
        print(f"Warning: Quota exceeded!")
else:
    print(f"Usage not allowed: {reason}")

# Get usage summary
summary = tracker.get_usage_summary(customer_id="cust_123")
print(f"Total usage: {summary['total_quantity']}")

# Get usage trends
trends = tracker.get_usage_trends(
    customer_id="cust_123",
    interval="day",
    num_intervals=7
)
print(f"Trend direction: {trends['trend']['direction']}")
```

### Billing Calculation Example

```python
from monetization import (
    UsageMetric, UsageCategory,
    BillingCalculator, TieredPricingCalculator,
    ProratedBilling
)

# Create a billing calculator
calculator = TieredPricingCalculator()

# Add pricing rules
calculator.create_per_unit_pricing_rule(
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE
)

calculator.create_tiered_pricing_rule(
    metric=UsageMetric.TOKEN,
    tiers=[
        {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
        {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
        {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005}
    ],
    graduated=True,
    category=UsageCategory.INFERENCE
)

# Calculate costs
api_cost = calculator.calculate_cost(
    metric=UsageMetric.API_CALL,
    quantity=100,
    category=UsageCategory.INFERENCE
)

token_cost = calculator.calculate_cost(
    metric=UsageMetric.TOKEN,
    quantity=5000,
    category=UsageCategory.INFERENCE
)

print(f"API call cost: ${api_cost:.2f}")
print(f"Token cost: ${token_cost:.2f}")

# Calculate prorated billing for a plan change
result = ProratedBilling.calculate_plan_change(
    old_plan_amount=10.0,
    new_plan_amount=20.0,
    current_date=datetime.now(),
    period_start_date=datetime(datetime.now().year, datetime.now().month, 1),
    period="monthly"
)

print(f"Upgrade amount: ${result['amount']:.2f}")
```

### Invoice Generation Example

```python
from monetization import (
    Invoice, InvoiceStatus, InvoiceManager, InvoiceDelivery
)

# Create an invoice manager
manager = InvoiceManager(
    company_info={
        "name": "AI Tools Inc.",
        "email": "billing@aitools.com",
        "website": "https://aitools.com"
    }
)

# Create an invoice
invoice = manager.create_invoice(
    customer_id="cust_123",
    customer_info={
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
)

# Add items
invoice.add_item(
    description="Premium Subscription (Monthly)",
    quantity=1,
    unit_price=29.99,
    tax_rate=0.0825  # 8.25% tax
)

invoice.add_item(
    description="Additional User Licenses",
    quantity=3,
    unit_price=9.99,
    tax_rate=0.0825  # 8.25% tax
)

# Update status to sent
manager.update_invoice_status(invoice.id, InvoiceStatus.SENT)

# Add a payment
manager.add_payment(
    invoice_id=invoice.id,
    amount=30.00,
    payment_method="Credit Card",
    transaction_id="txn_123456"
)

# Create an invoice delivery system
delivery = InvoiceDelivery()

# Export invoice to different formats
html_output = delivery.export_invoice(invoice, format="html", output_path="invoice.html")
pdf_output = delivery.generate_pdf(invoice, output_path="invoice.pdf")

# Send invoice by email
delivery.send_invoice_by_email(
    invoice=invoice,
    email="john.doe@example.com",
    subject="Your Invoice",
    format="html",
    attach_pdf=True
)
```

### Subscription Analytics Example

```python
from monetization import (
    SubscriptionManager, SubscriptionMetrics,
    ChurnAnalysis, SubscriptionForecasting
)

# Create a subscription manager
manager = SubscriptionManager()

# Create metrics calculator
metrics = SubscriptionMetrics(manager)

# Calculate basic metrics
active_count = metrics.get_active_subscription_count()
mrr = metrics.get_monthly_recurring_revenue()
arr = metrics.get_annual_recurring_revenue()
arpu = metrics.get_average_revenue_per_user()

print(f"Active subscriptions: {active_count}")
print(f"MRR: ${mrr:.2f}")
print(f"ARR: ${arr:.2f}")
print(f"ARPU: ${arpu:.2f}")

# Get revenue by plan
revenue_by_plan = metrics.get_revenue_by_plan()
for plan_id, revenue in revenue_by_plan.items():
    plan = manager.get_plan(plan_id)
    print(f"- {plan.name}: ${revenue:.2f}/month")

# Create churn analysis
churn = ChurnAnalysis(manager)

# Calculate churn metrics
churn_rate = churn.get_churn_rate()
retention_rate = churn.get_retention_rate()
ltv = churn.get_lifetime_value()

print(f"Churn rate: {churn_rate:.2f}%")
print(f"Retention rate: {retention_rate:.2f}%")
print(f"Customer lifetime value: ${ltv:.2f}")

# Get at-risk subscriptions
at_risk = churn.get_at_risk_subscriptions()
print(f"At-risk subscriptions: {len(at_risk)}")

# Create forecasting
forecasting = SubscriptionForecasting(manager, metrics, churn)

# Forecast subscriptions and revenue
subscription_forecast = forecasting.forecast_subscriptions(periods=12)
revenue_forecast = forecasting.forecast_revenue(periods=12)

print(f"Forecasted subscriptions (12 months): {subscription_forecast[11]['subscriptions']}")
print(f"Forecasted MRR (12 months): ${revenue_forecast[11]['revenue']:.2f}")

# Forecast scenarios
scenarios = forecasting.forecast_revenue_scenarios(periods=12)
for scenario_name, forecast in scenarios.items():
    print(f"- {scenario_name}: ${forecast[11]['revenue']:.2f}/month")

# Forecast breakeven
breakeven = forecasting.forecast_breakeven(
    fixed_costs=5000.0,
    variable_cost_per_user=2.0,
    periods=24
)

if breakeven:
    print(f"Breakeven point: Month {breakeven['period']} with ${breakeven['revenue']:.2f} revenue")
```

## Demo

Run the demo scripts to see the monetization tools in action:

```bash
python monetization_demo.py
python payment_processing_demo.py
python payment_method_demo.py
python transaction_demo.py
python receipt_demo.py
python usage_tracking_demo.py
python billing_demo.py
python invoice_demo.py
python subscription_analytics_demo.py
```

## Testing

Run the test scripts to verify that the monetization tools are working correctly:

```bash
python test_subscription_model.py
python test_freemium_model.py
python test_pricing_calculator.py
python test_revenue_projector.py
```

Additional test scripts for the new functionality:

```bash
python test_subscription_plan.py
python test_subscription_manager.py
python test_payment_processor.py
python test_payment_method.py
python test_transaction.py
python test_receipt.py
python test_usage_tracking.py
python test_billing_calculator.py
python test_tiered_pricing.py
python test_prorated_billing.py
python test_invoice.py
python test_invoice_manager.py
python test_invoice_delivery.py
python test_subscription_analytics.py
```

## Customization

These tools are designed to be customized for your specific niche and solution. Look for comments marked with `TODO` for guidance on what to customize.

## Dependencies

The tools have the following dependencies:

- Python 3.8+
- Standard library modules (json, math, datetime, uuid)

No external dependencies are required.
