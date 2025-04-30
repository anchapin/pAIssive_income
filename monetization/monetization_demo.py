"""
Demo script for the monetization tools.

This script demonstrates how to use the subscription models, pricing calculator,
and revenue projector together to create a complete monetization strategy.
"""

from subscription_models import SubscriptionModel, FreemiumModel
from pricing_calculator import PricingCalculator
from revenue_projector import RevenueProjector


def run_demo():
    """Run a demonstration of the monetization tools."""
    print("=" * 80)
    print("pAIssive Income Monetization Tools Demo")
    print("=" * 80)

    # Step 1: Create a freemium subscription model
    print("\n1. Creating a Freemium Subscription Model")
    print("-" * 50)

    model = FreemiumModel(
        name="AI Script Generator",
        description="AI-powered tool for generating YouTube scripts",
    )

    # Add features
    print("Adding features:")
    feature1 = model.add_feature(
        name="Basic Script Generation",
        description="Generate basic scripts using AI",
        feature_type="functional",
        value_proposition="Save time on writing basic scripts",
        development_cost="low",
    )
    print(f"- {feature1['name']}: {feature1['description']}")

    feature2 = model.add_feature(
        name="Advanced Script Generation",
        description="Generate advanced scripts with more control",
        feature_type="functional",
        value_proposition="Create professional scripts faster",
        development_cost="medium",
    )
    print(f"- {feature2['name']}: {feature2['description']}")

    feature3 = model.add_feature(
        name="Script Templates",
        description="Access to pre-made script templates",
        feature_type="content",
        value_proposition="Start with proven formats",
        development_cost="medium",
    )
    print(f"- {feature3['name']}: {feature3['description']}")

    feature4 = model.add_feature(
        name="Export Options",
        description="Export scripts in multiple formats",
        feature_type="functional",
        value_proposition="Use scripts in your preferred tools",
        development_cost="low",
    )
    print(f"- {feature4['name']}: {feature4['description']}")

    feature5 = model.add_feature(
        name="Priority Support",
        description="Get priority support from our team",
        feature_type="support",
        value_proposition="Get help when you need it",
        development_cost="high",
    )
    print(f"- {feature5['name']}: {feature5['description']}")

    # Add feature to free tier
    model.add_feature_to_free_tier(feature1["id"])

    # Update free tier limits
    model.update_free_tier_limits(
        {
            "scripts_per_month": 5,
            "max_script_length": 500,
            "export_formats": ["txt"],
        }
    )

    # Add paid tiers
    print("\nAdding subscription tiers:")
    pro_tier = model.add_paid_tier(
        name="Pro",
        description="Advanced features for content creators",
        price_monthly=19.99,
        target_users="Professional content creators and small channels",
    )
    print(
        f"- {pro_tier['name']}: ${pro_tier['price_monthly']}/month - {pro_tier['description']}"
    )

    premium_tier = model.add_paid_tier(
        name="Premium",
        description="All features for serious YouTubers",
        price_monthly=49.99,
        target_users="Serious YouTubers and content teams",
    )
    print(
        f"- {premium_tier['name']}: ${premium_tier['price_monthly']}/month - {premium_tier['description']}"
    )

    # Assign features to paid tiers
    model.assign_feature_to_tier(feature1["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature1["id"], premium_tier["id"])

    model.assign_feature_to_tier(feature2["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature2["id"], premium_tier["id"])

    model.assign_feature_to_tier(feature3["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature3["id"], premium_tier["id"])

    model.assign_feature_to_tier(feature4["id"], premium_tier["id"])

    model.assign_feature_to_tier(feature5["id"], premium_tier["id"])

    # Step 2: Calculate optimal pricing
    print("\n2. Calculating Optimal Pricing")
    print("-" * 50)

    calculator = PricingCalculator(
        name="Script Generator Pricing Calculator",
        description="Pricing calculator for the AI Script Generator",
        pricing_strategy="value-based",
    )

    # Analyze price sensitivity
    print("Analyzing price sensitivity:")
    analysis = calculator.analyze_price_sensitivity(
        base_price=19.99, market_size=10000, price_elasticity=1.2
    )

    print(f"Base price: ${analysis['base_price']:.2f}")
    print(f"Market size: {analysis['market_size']} potential customers")
    print(f"Price elasticity: {analysis['price_elasticity']}")

    print("\nPrice points:")
    for point in analysis["price_points"]:
        print(
            f"- Price: ${point['price']:.2f}, Demand: {point['demand']}, Revenue: ${point['revenue']:.2f}"
        )

    print(f"\nOptimal price: ${analysis['optimal_price']:.2f}")
    print(f"Optimal demand: {analysis['optimal_demand']} customers")
    print(f"Optimal revenue: ${analysis['optimal_revenue']:.2f}")

    # Calculate optimal prices
    prices = {
        model.get_free_tier_id(): 0.0,
        pro_tier["id"]: 19.99,
        premium_tier["id"]: 49.99,
    }

    # Step 3: Project revenue
    print("\n3. Projecting Revenue")
    print("-" * 50)

    projector = RevenueProjector(
        name="Script Generator Revenue Projector",
        description="Revenue projector for the AI Script Generator",
        initial_users=0,
        user_acquisition_rate=100,
        conversion_rate=0.1,
        churn_rate=0.05,
        tier_distribution={"basic": 0.0, "pro": 0.7, "premium": 0.3},
    )

    # Project revenue
    projection = projector.project_revenue(
        subscription_model=model, prices=prices, months=36, growth_rate=0.05
    )

    # Print projection summary
    print(f"Revenue Projection for {model.name}")
    print(f"Projection period: {projection['projection_months']} months")
    print(f"Growth rate: {projection['growth_rate']:.1%} per month")

    print("\nYearly Summaries:")
    for year in projection["yearly_summaries"]:
        print(f"Year {year['year']}:")
        print(f"  Total Users: {year['total_users']}")
        print(f"  Paid Users: {year['paid_users']}")
        print(f"  Yearly Revenue: ${year['yearly_revenue']:.2f}")
        print(f"  Cumulative Revenue: ${year['cumulative_revenue']:.2f}")

    print(f"\nTotal Revenue (3 years): ${projection['total_revenue']:.2f}")

    # Calculate lifetime value
    average_revenue = 19.99 * 0.7 + 49.99 * 0.3
    ltv = projector.calculate_lifetime_value(average_revenue)

    print(f"\nCustomer Lifetime Value:")
    print(f"Average Revenue Per User: ${ltv['average_revenue_per_user']:.2f}")
    print(f"Average Customer Lifetime: {ltv['average_lifetime_months']:.1f} months")
    print(f"Lifetime Value: ${ltv['lifetime_value']:.2f}")

    # Calculate payback period
    payback = projector.calculate_payback_period(
        customer_acquisition_cost=30, average_revenue_per_user=average_revenue
    )

    print(f"\nCustomer Payback Period:")
    print(f"Customer Acquisition Cost: ${payback['customer_acquisition_cost']:.2f}")
    print(f"Monthly Contribution: ${payback['monthly_contribution']:.2f}")
    print(f"Payback Period: {payback['payback_period_months']:.1f} months")

    print("\n" + "=" * 80)
    print("Demo Complete")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
