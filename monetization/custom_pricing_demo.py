"""
Custom pricing demo for the pAIssive Income project.

This script demonstrates how to use the custom pricing rules
to implement complex pricing strategies.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import time

from .usage_tracking import UsageMetric, UsageCategory
from .billing_calculator import BillingCalculator
from .custom_pricing import (
    CustomPricingCalculator,
    TimeBasedPricingRule,
    SeasonalPricingRule,
    CustomerSegmentPricingRule,
    ConditionalPricingRule,
    FormulaBasedPricingRule
)


def print_section(title: str) -> None:
    """Print a section title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def print_separator() -> None:
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def demonstrate_time_based_pricing() -> None:
    """Demonstrate time-based pricing."""
    print_section("Time-Based Pricing")
    
    # Create a time-based pricing rule
    rule = TimeBasedPricingRule(
        metric=UsageMetric.API_CALL,
        time_rates={
            "weekday:1-5": 0.01,  # $0.01 per API call on weekdays
            "weekend:6-7": 0.005,  # $0.005 per API call on weekends
            "hour:9-17": 0.015,  # $0.015 per API call during business hours
            "hour:0-8,18-23": 0.008  # $0.008 per API call during non-business hours
        },
        default_rate=0.01,
        category=UsageCategory.INFERENCE
    )
    
    # Create a calculator
    calculator = CustomPricingCalculator()
    calculator.add_custom_rule(rule)
    
    # Test different times
    test_times = [
        # Weekday during business hours
        datetime(2023, 5, 15, 14, 0, 0),  # Monday at 2 PM
        # Weekday outside business hours
        datetime(2023, 5, 16, 22, 0, 0),  # Tuesday at 10 PM
        # Weekend
        datetime(2023, 5, 20, 12, 0, 0),  # Saturday at noon
        # Current time
        datetime.now()
    ]
    
    quantity = 100  # 100 API calls
    
    print(f"Pricing for {quantity} API calls at different times:")
    
    for test_time in test_times:
        # Override the current time for testing
        rule.get_rate_for_time = lambda timestamp=None, test_time=test_time: rule._get_rate_for_time_impl(test_time)
        
        # Calculate cost
        cost = calculator.calculate_cost(
            metric=UsageMetric.API_CALL,
            quantity=quantity,
            category=UsageCategory.INFERENCE
        )
        
        # Determine the applicable rate
        rate = rule.get_rate_for_time()
        
        # Format the time
        time_str = test_time.strftime("%A at %I:%M %p")
        
        print(f"- {time_str}: ${cost:.2f} (rate: ${rate:.3f} per call)")


def demonstrate_seasonal_pricing() -> None:
    """Demonstrate seasonal pricing."""
    print_section("Seasonal Pricing")
    
    # Create a seasonal pricing rule
    rule = SeasonalPricingRule(
        metric=UsageMetric.STORAGE,
        seasonal_rates={
            "winter": 0.05,  # $0.05 per GB in winter
            "spring": 0.04,  # $0.04 per GB in spring
            "summer": 0.03,  # $0.03 per GB in summer
            "fall": 0.04,  # $0.04 per GB in fall
            "holiday:christmas": 0.02,  # $0.02 per GB during Christmas
            "holiday:newyear": 0.025  # $0.025 per GB during New Year
        },
        default_rate=0.04,
        category=UsageCategory.STORAGE
    )
    
    # Create a calculator
    calculator = CustomPricingCalculator()
    calculator.add_custom_rule(rule)
    
    # Test different dates
    test_dates = [
        # Winter
        datetime(2023, 1, 15),  # January
        # Spring
        datetime(2023, 4, 15),  # April
        # Summer
        datetime(2023, 7, 15),  # July
        # Fall
        datetime(2023, 10, 15),  # October
        # Christmas
        datetime(2023, 12, 25),  # December 25
        # New Year
        datetime(2023, 1, 1)  # January 1
    ]
    
    quantity = 10  # 10 GB of storage
    
    print(f"Pricing for {quantity} GB of storage at different times of year:")
    
    for test_date in test_dates:
        # Override the current time for testing
        rule.get_rate_for_season = lambda timestamp=None, test_date=test_date: rule._get_rate_for_season_impl(test_date)
        
        # Calculate cost
        cost = calculator.calculate_cost(
            metric=UsageMetric.STORAGE,
            quantity=quantity,
            category=UsageCategory.STORAGE
        )
        
        # Determine the applicable rate
        rate = rule.get_rate_for_season()
        
        # Format the date
        date_str = test_date.strftime("%B %d")
        
        # Determine the season
        month = test_date.month
        season = "Winter"
        if month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        elif month in [9, 10, 11]:
            season = "Fall"
        
        # Check for holidays
        holiday = ""
        if month == 12 and test_date.day == 25:
            holiday = " (Christmas)"
        elif month == 1 and test_date.day == 1:
            holiday = " (New Year)"
        
        print(f"- {date_str} ({season}{holiday}): ${cost:.2f} (rate: ${rate:.3f} per GB)")


def demonstrate_customer_segment_pricing() -> None:
    """Demonstrate customer segment pricing."""
    print_section("Customer Segment Pricing")
    
    # Create a customer segment pricing rule
    rule = CustomerSegmentPricingRule(
        metric=UsageMetric.TOKEN,
        segment_rates={
            "tier:free": 0.002,  # $0.002 per token for free tier
            "tier:premium": 0.0015,  # $0.0015 per token for premium tier
            "tier:enterprise": 0.001,  # $0.001 per token for enterprise tier
            "industry:education": 0.0012,  # $0.0012 per token for education industry
            "industry:healthcare": 0.0013,  # $0.0013 per token for healthcare industry
            "region:eu": 0.0018,  # $0.0018 per token for EU customers (GDPR compliance)
            "age:0-30": 0.0018,  # $0.0018 per token for new customers (0-30 days)
            "age:31-90": 0.0016,  # $0.0016 per token for recent customers (31-90 days)
            "age:91+": 0.0014  # $0.0014 per token for established customers (91+ days)
        },
        default_rate=0.002,
        category=UsageCategory.INFERENCE
    )
    
    # Create a calculator
    calculator = CustomPricingCalculator()
    calculator.add_custom_rule(rule)
    
    # Test different customer segments
    test_customers = [
        {
            "name": "Free Tier Customer",
            "data": {"tier": "free", "industry": "technology", "region": "us", "created_at": "2023-01-01T00:00:00"}
        },
        {
            "name": "Premium Tier Customer",
            "data": {"tier": "premium", "industry": "finance", "region": "us", "created_at": "2022-01-01T00:00:00"}
        },
        {
            "name": "Enterprise Tier Customer",
            "data": {"tier": "enterprise", "industry": "manufacturing", "region": "us", "created_at": "2021-01-01T00:00:00"}
        },
        {
            "name": "Education Industry Customer",
            "data": {"tier": "premium", "industry": "education", "region": "us", "created_at": "2022-06-01T00:00:00"}
        },
        {
            "name": "Healthcare Industry Customer",
            "data": {"tier": "premium", "industry": "healthcare", "region": "us", "created_at": "2022-06-01T00:00:00"}
        },
        {
            "name": "EU Region Customer",
            "data": {"tier": "premium", "industry": "technology", "region": "eu", "created_at": "2022-06-01T00:00:00"}
        },
        {
            "name": "New Customer (15 days)",
            "data": {"tier": "premium", "industry": "technology", "region": "us", "created_at": (datetime.now() - timedelta(days=15)).isoformat()}
        },
        {
            "name": "Recent Customer (60 days)",
            "data": {"tier": "premium", "industry": "technology", "region": "us", "created_at": (datetime.now() - timedelta(days=60)).isoformat()}
        },
        {
            "name": "Established Customer (120 days)",
            "data": {"tier": "premium", "industry": "technology", "region": "us", "created_at": (datetime.now() - timedelta(days=120)).isoformat()}
        }
    ]
    
    quantity = 1000  # 1000 tokens
    
    print(f"Pricing for {quantity} tokens for different customer segments:")
    
    for customer in test_customers:
        # Calculate cost
        cost = rule.calculate_custom_cost(
            quantity=quantity,
            customer_data=customer["data"]
        )
        
        # Determine the applicable rate
        rate = rule.get_rate_for_segment(customer["data"])
        
        print(f"- {customer['name']}: ${cost:.2f} (rate: ${rate:.4f} per token)")


def demonstrate_conditional_pricing() -> None:
    """Demonstrate conditional pricing."""
    print_section("Conditional Pricing")
    
    # Create a conditional pricing rule
    rule = ConditionalPricingRule(
        metric=UsageMetric.COMPUTE_TIME,
        conditions=[
            {
                "condition": "quantity > 100 and customer.tier == 'premium'",
                "rate": 0.08  # $0.08 per hour for premium customers with high usage
            },
            {
                "condition": "time.is_weekend and usage.total > 1000",
                "rate": 0.06  # $0.06 per hour on weekends with high total usage
            },
            {
                "condition": "customer.industry == 'research' and time.hour >= 22",
                "rate": 0.05  # $0.05 per hour for research customers during late hours
            },
            {
                "condition": "customer.tier == 'enterprise' and usage.average > 50",
                "rate": 0.07  # $0.07 per hour for enterprise customers with high average usage
            },
            {
                "condition": "quantity < 10 and customer.tier == 'free'",
                "rate": 0.12  # $0.12 per hour for free tier customers with low usage
            }
        ],
        default_rate=0.1,  # $0.1 per hour by default
        category=UsageCategory.COMPUTE
    )
    
    # Create a calculator
    calculator = CustomPricingCalculator()
    calculator.add_custom_rule(rule)
    
    # Test different conditions
    test_scenarios = [
        {
            "name": "Premium customer with high usage",
            "quantity": 150,
            "context": {
                "customer": {"tier": "premium", "industry": "technology"},
                "time": {"hour": 14, "is_weekend": False},
                "usage": {"total": 500, "average": 30}
            }
        },
        {
            "name": "Weekend with high total usage",
            "quantity": 50,
            "context": {
                "customer": {"tier": "premium", "industry": "technology"},
                "time": {"hour": 14, "is_weekend": True},
                "usage": {"total": 1500, "average": 30}
            }
        },
        {
            "name": "Research customer during late hours",
            "quantity": 50,
            "context": {
                "customer": {"tier": "premium", "industry": "research"},
                "time": {"hour": 23, "is_weekend": False},
                "usage": {"total": 500, "average": 30}
            }
        },
        {
            "name": "Enterprise customer with high average usage",
            "quantity": 50,
            "context": {
                "customer": {"tier": "enterprise", "industry": "technology"},
                "time": {"hour": 14, "is_weekend": False},
                "usage": {"total": 500, "average": 60}
            }
        },
        {
            "name": "Free tier customer with low usage",
            "quantity": 5,
            "context": {
                "customer": {"tier": "free", "industry": "technology"},
                "time": {"hour": 14, "is_weekend": False},
                "usage": {"total": 100, "average": 10}
            }
        },
        {
            "name": "Default scenario",
            "quantity": 50,
            "context": {
                "customer": {"tier": "premium", "industry": "technology"},
                "time": {"hour": 14, "is_weekend": False},
                "usage": {"total": 500, "average": 30}
            }
        }
    ]
    
    print("Pricing for compute time under different conditions:")
    
    for scenario in test_scenarios:
        # Calculate cost
        cost = rule.calculate_custom_cost(
            quantity=scenario["quantity"],
            context=scenario["context"]
        )
        
        # Determine the applicable rate
        rate = rule.get_rate_for_conditions(scenario["quantity"], scenario["context"])
        
        print(f"- {scenario['name']} ({scenario['quantity']} hours): ${cost:.2f} (rate: ${rate:.2f} per hour)")


def demonstrate_formula_based_pricing() -> None:
    """Demonstrate formula-based pricing."""
    print_section("Formula-Based Pricing")
    
    # Create a formula-based pricing rule
    rule = FormulaBasedPricingRule(
        metric=UsageMetric.BANDWIDTH,
        formula="base_fee + q * rate * (1 - volume_discount * min(1, q / discount_threshold))",
        variables={
            "base_fee": 5.0,  # $5.00 base fee
            "rate": 0.1,  # $0.10 per GB
            "volume_discount": 0.2,  # 20% maximum volume discount
            "discount_threshold": 100.0  # Discount threshold at 100 GB
        },
        category=UsageCategory.NETWORK
    )
    
    # Create a calculator
    calculator = CustomPricingCalculator()
    calculator.add_custom_rule(rule)
    
    # Test different quantities
    test_quantities = [10, 50, 100, 200, 500, 1000]
    
    print("Pricing for bandwidth usage with volume discount formula:")
    print(f"Formula: {rule.formula}")
    print(f"Variables: {rule.variables}")
    print()
    
    for quantity in test_quantities:
        # Calculate cost
        cost = calculator.calculate_cost(
            metric=UsageMetric.BANDWIDTH,
            quantity=quantity,
            category=UsageCategory.NETWORK
        )
        
        # Calculate effective rate
        effective_rate = cost / quantity if quantity > 0 else 0
        
        # Calculate discount percentage
        discount_percentage = rule.variables["volume_discount"] * min(1, quantity / rule.variables["discount_threshold"]) * 100
        
        print(f"- {quantity} GB: ${cost:.2f} (effective rate: ${effective_rate:.3f} per GB, discount: {discount_percentage:.1f}%)")
    
    # Create another formula-based pricing rule with a more complex formula
    complex_rule = FormulaBasedPricingRule(
        metric=UsageMetric.TOKEN,
        formula="base_rate * q * (1 - tier_discount) * (1 - seasonal_discount if time_month in [6, 7, 8] else 0) * (1 - loyalty_discount * min(1, customer_age / 365))",
        variables={
            "base_rate": 0.002,  # $0.002 per token
            "tier_discount": 0.1,  # 10% tier discount
            "seasonal_discount": 0.15,  # 15% seasonal discount
            "loyalty_discount": 0.2,  # 20% maximum loyalty discount
            "time_month": datetime.now().month,
            "customer_age": 180  # 180 days
        },
        category=UsageCategory.INFERENCE
    )
    
    # Add to calculator
    calculator.add_custom_rule(complex_rule)
    
    print("\nPricing for tokens with complex formula:")
    print(f"Formula: {complex_rule.formula}")
    print(f"Variables: {complex_rule.variables}")
    print()
    
    quantity = 1000  # 1000 tokens
    
    # Calculate cost
    cost = calculator.calculate_cost(
        metric=UsageMetric.TOKEN,
        quantity=quantity,
        category=UsageCategory.INFERENCE
    )
    
    # Calculate effective rate
    effective_rate = cost / quantity if quantity > 0 else 0
    
    # Calculate discount breakdown
    tier_discount = complex_rule.variables["tier_discount"] * 100
    seasonal_discount = complex_rule.variables["seasonal_discount"] * 100 if complex_rule.variables["time_month"] in [6, 7, 8] else 0
    loyalty_discount = complex_rule.variables["loyalty_discount"] * min(1, complex_rule.variables["customer_age"] / 365) * 100
    
    print(f"- {quantity} tokens: ${cost:.2f} (effective rate: ${effective_rate:.5f} per token)")
    print(f"  Discount breakdown: Tier: {tier_discount:.1f}%, Seasonal: {seasonal_discount:.1f}%, Loyalty: {loyalty_discount:.1f}%")


def demonstrate_combined_pricing() -> None:
    """Demonstrate combined pricing strategies."""
    print_section("Combined Pricing Strategies")
    
    # Create a calculator with multiple rules
    calculator = CustomPricingCalculator()
    
    # Add time-based pricing for API calls
    calculator.add_custom_rule(TimeBasedPricingRule(
        metric=UsageMetric.API_CALL,
        time_rates={
            "weekday:1-5": 0.01,
            "weekend:6-7": 0.005
        },
        default_rate=0.01,
        category=UsageCategory.INFERENCE
    ))
    
    # Add seasonal pricing for storage
    calculator.add_custom_rule(SeasonalPricingRule(
        metric=UsageMetric.STORAGE,
        seasonal_rates={
            "winter": 0.05,
            "summer": 0.03
        },
        default_rate=0.04,
        category=UsageCategory.STORAGE
    ))
    
    # Add customer segment pricing for tokens
    calculator.add_custom_rule(CustomerSegmentPricingRule(
        metric=UsageMetric.TOKEN,
        segment_rates={
            "tier:premium": 0.0015,
            "tier:enterprise": 0.001
        },
        default_rate=0.002,
        category=UsageCategory.INFERENCE
    ))
    
    # Add conditional pricing for compute time
    calculator.add_custom_rule(ConditionalPricingRule(
        metric=UsageMetric.COMPUTE_TIME,
        conditions=[
            {
                "condition": "time.is_weekend and customer.tier == 'premium'",
                "rate": 0.06
            }
        ],
        default_rate=0.1,
        category=UsageCategory.COMPUTE
    ))
    
    # Add formula-based pricing for bandwidth
    calculator.add_custom_rule(FormulaBasedPricingRule(
        metric=UsageMetric.BANDWIDTH,
        formula="base_fee + q * rate * (1 - volume_discount * min(1, q / discount_threshold))",
        variables={
            "base_fee": 5.0,
            "rate": 0.1,
            "volume_discount": 0.2,
            "discount_threshold": 100.0
        },
        category=UsageCategory.NETWORK
    ))
    
    # Create a customer context
    customer_context = {
        "customer": {
            "tier": "premium",
            "industry": "technology",
            "region": "us",
            "created_at": "2023-01-01T00:00:00"
        },
        "time": {
            "hour": datetime.now().hour,
            "is_weekend": datetime.now().isoweekday() >= 6
        },
        "usage": {
            "total": 1000,
            "average": 50
        }
    }
    
    # Calculate costs for different metrics
    api_cost = calculator.calculate_cost(
        metric=UsageMetric.API_CALL,
        quantity=100,
        category=UsageCategory.INFERENCE,
        context=customer_context
    )
    
    storage_cost = calculator.calculate_cost(
        metric=UsageMetric.STORAGE,
        quantity=10,
        category=UsageCategory.STORAGE,
        context=customer_context
    )
    
    token_cost = calculator.calculate_cost(
        metric=UsageMetric.TOKEN,
        quantity=1000,
        category=UsageCategory.INFERENCE,
        context=customer_context
    )
    
    compute_cost = calculator.calculate_cost(
        metric=UsageMetric.COMPUTE_TIME,
        quantity=10,
        category=UsageCategory.COMPUTE,
        context=customer_context
    )
    
    bandwidth_cost = calculator.calculate_cost(
        metric=UsageMetric.BANDWIDTH,
        quantity=50,
        category=UsageCategory.NETWORK,
        context=customer_context
    )
    
    # Calculate total cost
    total_cost = api_cost + storage_cost + token_cost + compute_cost + bandwidth_cost
    
    print("Combined pricing for a premium customer:")
    print(f"- API calls (100): ${api_cost:.2f}")
    print(f"- Storage (10 GB): ${storage_cost:.2f}")
    print(f"- Tokens (1000): ${token_cost:.2f}")
    print(f"- Compute time (10 hours): ${compute_cost:.2f}")
    print(f"- Bandwidth (50 GB): ${bandwidth_cost:.2f}")
    print(f"- Total: ${total_cost:.2f}")
    
    # Generate a sample invoice
    print("\nSample Invoice:")
    print("=" * 40)
    print("INVOICE")
    print("=" * 40)
    print(f"Customer: Premium Technology Customer")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Invoice #: INV-{random.randint(10000, 99999)}")
    print("-" * 40)
    print(f"API Calls: 100 @ variable rate      ${api_cost:.2f}")
    print(f"Storage: 10 GB @ seasonal rate      ${storage_cost:.2f}")
    print(f"Tokens: 1000 @ segment rate         ${token_cost:.2f}")
    print(f"Compute: 10 hours @ conditional rate ${compute_cost:.2f}")
    print(f"Bandwidth: 50 GB @ formula rate     ${bandwidth_cost:.2f}")
    print("-" * 40)
    print(f"Subtotal:                          ${total_cost:.2f}")
    print(f"Tax (10%):                         ${total_cost * 0.1:.2f}")
    print(f"Total:                             ${total_cost * 1.1:.2f}")
    print("=" * 40)


def main() -> None:
    """Run the custom pricing demo."""
    print_section("Custom Pricing Demo")
    
    # Demonstrate different pricing strategies
    demonstrate_time_based_pricing()
    demonstrate_seasonal_pricing()
    demonstrate_customer_segment_pricing()
    demonstrate_conditional_pricing()
    demonstrate_formula_based_pricing()
    demonstrate_combined_pricing()
    
    print_section("Demo Complete")


if __name__ == "__main__":
    main()
