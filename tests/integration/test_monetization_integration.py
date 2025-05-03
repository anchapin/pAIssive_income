"""
Integration tests for the Monetization module.
"""

import os

import pytest

from monetization.pricing_calculator import PricingCalculator
from monetization.revenue_projector import RevenueProjector
from monetization.subscription_manager import SubscriptionManager
from monetization.subscription_models import FreemiumModel, SubscriptionModel


@pytest.fixture
def temp_subscription_dir(temp_dir):
    """Create a temporary directory for subscriptions."""
    subscription_dir = os.path.join(temp_dir, "subscriptions")
    os.makedirs(subscription_dir, exist_ok=True)
    return subscription_dir


def test_subscription_model_to_manager_integration(temp_subscription_dir):
    """Test integration between SubscriptionModel and SubscriptionManager."""
    # Create a subscription model
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add features
    feature1 = model.add_feature(
        name="Feature 1", description="A test feature", feature_type="functional"
    )

    feature2 = model.add_feature(
        name="Feature 2", description="Another test feature", feature_type="premium"
    )

    # Add tiers
    tier1 = model.add_tier(
        name="Basic",
        description="Basic tier",
        price_monthly=9.99,
        features=[feature1["id"]],
    )

    tier2 = model.add_tier(
        name="Pro",
        description="Pro tier",
        price_monthly=19.99,
        features=[feature1["id"], feature2["id"]],
    )

    # Save the model to a file
    model_path = os.path.join(temp_subscription_dir, "test_model.json")
    model.save_to_file(model_path)

    # Create a subscription manager
    manager = SubscriptionManager(storage_dir=temp_subscription_dir)

    # Create a subscription plan from the model
    plan = manager.create_plan_from_model(model)

    # Check that the plan was created with the correct attributes
    assert plan.name == model.name
    assert plan.description == model.description
    assert len(plan.features) == len(model.features)
    assert len(plan.tiers) == len(model.tiers)

    # Check that the features were transferred
    plan_feature_names = [feature.name for feature in plan.features]
    assert "Feature 1" in plan_feature_names
    assert "Feature 2" in plan_feature_names

    # Check that the tiers were transferred
    plan_tier_names = [tier.name for tier in plan.tiers]
    assert "Basic" in plan_tier_names
    assert "Pro" in plan_tier_names

    # Create a subscription for a user
    subscription = manager.create_subscription(user_id="user1", plan_id=plan.id, tier_name="Pro")

    # Check that the subscription was created with the correct attributes
    assert subscription.user_id == "user1"
    assert subscription.plan_id == plan.id
    assert subscription.tier_name == "Pro"
    assert subscription.status == "active"

    # Get the subscription
    retrieved_subscription = manager.get_subscription(subscription.id)

    # Check that the subscription was retrieved
    assert retrieved_subscription.id == subscription.id
    assert retrieved_subscription.user_id == "user1"
    assert retrieved_subscription.plan_id == plan.id
    assert retrieved_subscription.tier_name == "Pro"

    # Get subscriptions for the user
    user_subscriptions = manager.get_user_subscriptions("user1")

    # Check that the user's subscriptions were retrieved
    assert len(user_subscriptions) == 1
    assert user_subscriptions[0].id == subscription.id


def test_freemium_model_to_pricing_calculator_integration():
    """Test integration between FreemiumModel and PricingCalculator."""
    # Create a freemium model
    model = FreemiumModel(name="Test Freemium Model", description="A test freemium model")

    # Add features
    feature1 = model.add_feature(
        name="Basic Feature", description="A basic feature", feature_type="functional"
    )

    feature2 = model.add_feature(
        name="Premium Feature", description="A premium feature", feature_type="premium"
    )

    # Add a paid tier
    tier = model.add_tier(
        name="Pro",
        description="Pro tier",
        price_monthly=19.99,
        features=[feature1["id"], feature2["id"]],
    )

    # Create a pricing calculator
    calculator = PricingCalculator(
        name="Test Pricing Calculator",
        description="A test pricing calculator",
        base_cost=5.0,
        profit_margin=0.3,
        competitor_prices={"basic": 9.99, "pro": 19.99, "premium": 29.99},
    )

    # Calculate optimal price for the Pro tier
    optimal_price = calculator.calculate_optimal_price(
        tier_name="Pro",
        cost_per_user=5.0,
        value_perception=0.8,
        competitor_price=19.99,
        price_sensitivity=0.7,
    )

    # Check that the optimal price is reasonable
    assert optimal_price > 0
    assert isinstance(optimal_price, float)

    # Update the tier price based on the calculation
    model.update_tier_price(tier["id"], price_monthly=optimal_price)

    # Check that the tier price was updated
    assert model.tiers[1]["price_monthly"] == optimal_price


def test_subscription_model_to_revenue_projector_integration():
    """Test integration between SubscriptionModel and RevenueProjector."""
    # Create a subscription model
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add tiers
    basic_tier = model.add_tier(name="Basic", description="Basic tier", price_monthly=9.99)

    pro_tier = model.add_tier(name="Pro", description="Pro tier", price_monthly=19.99)

    premium_tier = model.add_tier(name="Premium", description="Premium tier", price_monthly=29.99)

    # Create a revenue projector
    projector = RevenueProjector(
        name="Test Revenue Projector",
        description="A test revenue projector",
        initial_users=100,
        user_acquisition_rate=50,
        conversion_rate=0.2,
        churn_rate=0.05,
        tier_distribution={"Basic": 0.6, "Pro": 0.3, "Premium": 0.1},
    )

    # Project users
    user_projections = projector.project_users(months=12, growth_rate=0.05)

    # Check that user projections were generated
    assert len(user_projections) == 12
    assert all(isinstance(month["total_users"], int) for month in user_projections)
    assert all(isinstance(month["new_users"], int) for month in user_projections)
    assert all(isinstance(month["churned_users"], int) for month in user_projections)

    # Project revenue
    revenue_projections = projector.project_revenue(
        months=12, growth_rate=0.05, subscription_model=model
    )

    # Check that revenue projections were generated
    assert len(revenue_projections) == 12
    assert all(isinstance(month["total_revenue"], float) for month in revenue_projections)
    assert all(isinstance(month["tier_revenue"], dict) for month in revenue_projections)
    assert all("Basic" in month["tier_revenue"] for month in revenue_projections)
    assert all("Pro" in month["tier_revenue"] for month in revenue_projections)
    assert all("Premium" in month["tier_revenue"] for month in revenue_projections)

    # Check that the revenue is calculated correctly
    for month in revenue_projections:
        # Use round to handle floating point precision issues
        assert month["tier_revenue"]["Basic"] == round(month["tier_users"]["Basic"] * 9.99, 2)
        assert month["tier_revenue"]["Pro"] == round(month["tier_users"]["Pro"] * 19.99, 2)
        assert month["tier_revenue"]["Premium"] == round(month["tier_users"]["Premium"] * 29.99, 2)
        assert round(month["total_revenue"], 2) == round(sum(month["tier_revenue"].values()), 2)


def test_end_to_end_monetization_workflow(temp_subscription_dir):
    """Test end - to - end workflow for the Monetization module."""
    # 1. Create a freemium model
    model = FreemiumModel(
        name="AI Tool Subscription",
        description="Subscription model for an AI - powered tool",
        free_tier_name="Free",
        free_tier_description="Basic features for free users",
        free_tier_limits={"api_calls": 100, "exports": 10},
    )

    # 2. Add features
    basic_feature = model.add_feature(
        name="Basic Text Generation",
        description="Generate basic text using AI",
        feature_type="functional",
        value_proposition="Save time on writing",
    )

    advanced_feature = model.add_feature(
        name="Advanced Text Generation",
        description="Generate high - quality text with more control",
        feature_type="premium",
        value_proposition="Create professional content faster",
    )

    api_feature = model.add_feature(
        name="API Access",
        description="Access the AI through an API",
        feature_type="integration",
        value_proposition="Integrate AI into your workflow",
    )

    # 3. Add paid tiers
    pro_tier = model.add_tier(
        name="Pro",
        description="Professional features for content creators",
        price_monthly=19.99,
        price_yearly=199.99,
        features=[basic_feature["id"], advanced_feature["id"]],
        limits={"api_calls": 1000, "exports": 100},
        target_users="Content creators and marketers",
    )

    business_tier = model.add_tier(
        name="Business",
        description="Advanced features for businesses",
        price_monthly=49.99,
        price_yearly=499.99,
        features=[basic_feature["id"], advanced_feature["id"], api_feature["id"]],
        limits={"api_calls": 10000, "exports": 1000},
        target_users="Small and medium businesses",
    )

    # 4. Create a pricing calculator
    calculator = PricingCalculator(
        name="AI Tool Pricing Calculator",
        description="Calculator for AI tool pricing",
        base_cost=5.0,
        profit_margin=0.4,
        competitor_prices={"free": 0, "basic": 9.99, "pro": 19.99, "business": 49.99},
    )

    # 5. Calculate optimal prices
    pro_price = calculator.calculate_optimal_price(
        tier_name="Pro",
        cost_per_user=8.0,
        value_perception=0.8,
        competitor_price=19.99,
        price_sensitivity=0.7,
    )

    business_price = calculator.calculate_optimal_price(
        tier_name="Business",
        cost_per_user=15.0,
        value_perception=0.9,
        competitor_price=49.99,
        price_sensitivity=0.6,
    )

    # 6. Update tier prices
    model.update_tier_price(pro_tier["id"], price_monthly=pro_price, price_yearly=pro_price * 10)
    model.update_tier_price(
        business_tier["id"],
        price_monthly=business_price,
        price_yearly=business_price * 10,
    )

    # 7. Create a revenue projector
    projector = RevenueProjector(
        name="AI Tool Revenue Projector",
        description="Projector for AI tool revenue",
        initial_users=200,
        user_acquisition_rate=100,
        conversion_rate=0.15,
        churn_rate=0.05,
        tier_distribution={"Free": 0.7, "Pro": 0.2, "Business": 0.1},
    )

    # 8. Project revenue for 24 months
    revenue_projections = projector.project_revenue(
        months=24, growth_rate=0.08, subscription_model=model
    )

    # 9. Create a subscription manager
    manager = SubscriptionManager(storage_dir=temp_subscription_dir)

    # 10. Create a subscription plan from the model
    plan = manager.create_plan_from_model(model)

    # 11. Create subscriptions for users
    free_subscription = manager.create_subscription(
        user_id="user1", plan_id=plan.id, tier_name="Free"
    )

    pro_subscription = manager.create_subscription(
        user_id="user2", plan_id=plan.id, tier_name="Pro"
    )

    business_subscription = manager.create_subscription(
        user_id="user3", plan_id=plan.id, tier_name="Business"
    )

    # 12. Check subscription status and features
    assert free_subscription.status == "active"
    assert pro_subscription.status == "active"
    assert business_subscription.status == "active"

    # 13. Check feature access
    assert manager.has_feature_access(free_subscription.id, "Basic Text Generation")
    assert not manager.has_feature_access(free_subscription.id, "Advanced Text Generation")
    assert not manager.has_feature_access(free_subscription.id, "API Access")

    assert manager.has_feature_access(pro_subscription.id, "Basic Text Generation")
    assert manager.has_feature_access(pro_subscription.id, "Advanced Text Generation")
    assert not manager.has_feature_access(pro_subscription.id, "API Access")

    assert manager.has_feature_access(business_subscription.id, "Basic Text Generation")
    assert manager.has_feature_access(business_subscription.id, "Advanced Text Generation")
    assert manager.has_feature_access(business_subscription.id, "API Access")

    # 14. Check usage limits
    assert manager.get_usage_limit(free_subscription.id, "api_calls") == 100
    assert manager.get_usage_limit(pro_subscription.id, "api_calls") == 1000
    assert manager.get_usage_limit(business_subscription.id, "api_calls") == 10000

    # 15. Simulate a subscription upgrade
    upgraded_subscription = manager.upgrade_subscription(
        subscription_id=free_subscription.id, new_tier_name="Pro"
    )

    # 16. Check the upgraded subscription
    assert upgraded_subscription.tier_name == "Pro"
    assert manager.has_feature_access(upgraded_subscription.id, "Advanced Text Generation")
    assert manager.get_usage_limit(upgraded_subscription.id, "api_calls") == 1000
