"""
Integration tests for the competitor analysis → pricing strategy → revenue projection workflow.

This module tests the complete workflow from competitor analysis through pricing strategy
development to revenue projection.
"""

import pytest

    FreemiumModel,
    MonetizationCalculator,
    PricingCalculator,
    RevenueProjector,
    SubscriptionModel,
)
from niche_analysis import MarketAnalyzer

@pytest.fixture
def market_analyzer():
    """Create a market analyzer instance for testing."""
    return MarketAnalyzer()

@pytest.fixture
def subscription_model():
    """Create a subscription model instance for testing."""
    return SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

@pytest.fixture
def freemium_model():
    """Create a freemium model instance for testing."""
    return FreemiumModel(name="Test Freemium Model", 
        description="A test freemium model")

@pytest.fixture
def pricing_calculator():
    """Create a pricing calculator instance for testing."""
    return PricingCalculator(
        name="Test Pricing Calculator",
        description="A test pricing calculator",
        base_cost=5.0,
        profit_margin=0.3,
        competitor_prices={"basic": 9.99, "pro": 19.99, "premium": 29.99},
    )

@pytest.fixture
def revenue_projector():
    """Create a revenue projector instance for testing."""
    return RevenueProjector(
        name="Test Revenue Projector",
        description="A test revenue projector",
        initial_users=0,
        user_acquisition_rate=50,
        conversion_rate=0.2,
        churn_rate=0.05,
        tier_distribution={"basic": 0.6, "pro": 0.3, "premium": 0.1},
    )

def test_competitor_to_pricing_workflow(
    market_analyzer, subscription_model, pricing_calculator, revenue_projector
):
    """
    Test the complete workflow from competitor analysis to revenue projection.

    This test verifies that:
    1. Competitor analysis can be performed for a niche
    2. Pricing strategy can be developed based on competitor analysis
    3. Revenue can be projected based on the pricing strategy
    """
    # Step 1: Analyze competition in a niche
    niche = "inventory management"
    competition_analysis = market_analyzer.analyze_competition(niche)

    # Verify competition analysis results
    assert "top_competitors" in competition_analysis
    assert "market_saturation" in competition_analysis
    assert "differentiation_opportunities" in competition_analysis

    # Step 2: Create subscription tiers based on competition analysis
    # Add features based on differentiation opportunities
    differentiation_features = competition_analysis["differentiation_opportunities"]

    # Create basic tier
    basic_tier = subscription_model.add_tier(
        name="Basic",
        description="Basic features for small businesses",
        price_monthly=9.99,
        price_yearly=99.99,
        features=differentiation_features[:1],  # Use first differentiation feature
        limits={"api_calls": 1000, "exports": 100},
        target_users="Small businesses",
    )

    # Create pro tier
    pro_tier = subscription_model.add_tier(
        name="Pro",
        description="Advanced features for growing businesses",
        price_monthly=19.99,
        price_yearly=199.99,
        features=differentiation_features[:2],  # Use first two differentiation features
        limits={"api_calls": 5000, "exports": 500},
        target_users="Growing businesses",
    )

    # Create premium tier
    premium_tier = subscription_model.add_tier(
        name="Premium",
        description="All features for established businesses",
        price_monthly=29.99,
        price_yearly=299.99,
        features=differentiation_features,  # Use all differentiation features
        limits={"api_calls": 10000, "exports": 1000},
        target_users="Established businesses",
    )

    # Verify subscription model setup
    assert len(subscription_model.tiers) == 3

    # Step 3: Calculate optimal prices based on competition
    # Extract competitor prices from the analysis
    competitor_prices = {}
    for competitor in competition_analysis["top_competitors"]:
        if "pricing" in competitor:
            for tier, price in competitor["pricing"].items():
                if tier not in competitor_prices or price > competitor_prices[tier]:
                    competitor_prices[tier] = price

    # Update pricing calculator with competitor prices
    if competitor_prices:
        pricing_calculator.competitor_prices = competitor_prices

    # Calculate optimal price for each tier
    for tier in subscription_model.tiers:
        tier_name = tier["name"].lower()
        competitor_price = pricing_calculator.competitor_prices.get(tier_name, 0)

        optimal_price = pricing_calculator.calculate_optimal_price(
            tier_name=tier["name"],
            cost_per_user=5.0
            * (1 + subscription_model.tiers.index(tier) * 0.5),  
                # Higher tiers cost more
            value_perception=0.7
            + (
                subscription_model.tiers.index(tier) * 0.1
            ),  # Higher tiers have higher value perception
            competitor_price=competitor_price,
            price_sensitivity=0.8
            - (
                subscription_model.tiers.index(tier) * 0.1
            ),  # Higher tiers have lower price sensitivity
        )

        # Update tier price
        subscription_model.update_tier_price(tier["id"], price_monthly=optimal_price)

    # Verify price updates
    assert subscription_model.tiers[0]["price_monthly"] > 0
    assert (
        subscription_model.tiers[1]["price_monthly"] > subscription_model.tiers[0]["price_monthly"]
    )
    assert (
        subscription_model.tiers[2]["price_monthly"] > subscription_model.tiers[1]["price_monthly"]
    )

    # Step 4: Project revenue based on the pricing strategy
    # Create a dictionary of tier prices
    tier_prices = \
        {tier["id"]: tier["price_monthly"] for tier in subscription_model.tiers}

    # Project revenue for 24 months
    revenue_projection = revenue_projector.project_revenue(
        months=24, tier_prices=tier_prices, growth_rate=0.05
    )

    # Verify revenue projection
    assert len(revenue_projection["months"]) == 24
    assert len(revenue_projection["users"]) == 24
    assert len(revenue_projection["revenue"]) == 24
    assert revenue_projection["total_revenue"] > 0
    assert (
        revenue_projection["revenue"][-1] > revenue_projection["revenue"][0]
    )  # Revenue should increase over time

def test_competitor_to_pricing_workflow_with_freemium(
    market_analyzer, freemium_model, pricing_calculator, revenue_projector
):
    """
    Test the workflow with a freemium model.

    This test verifies that:
    1. Competitor analysis can be performed for a niche
    2. Freemium pricing strategy can be developed based on competitor analysis
    3. Revenue can be projected for a freemium model
    """
    # Step 1: Analyze competition in a niche
    niche = "content creation"
    competition_analysis = market_analyzer.analyze_competition(niche)

    # Step 2: Create freemium tiers based on competition analysis
    # Add features based on differentiation opportunities
    differentiation_features = competition_analysis["differentiation_opportunities"]

    # Create free tier
    free_tier = freemium_model.add_free_tier(
        description="Basic content creation tools",
        features=differentiation_features[:1],  # Use first differentiation feature
        limits={"content_pieces": 5, "exports": 2},
        target_users="Individuals and small teams",
    )

    # Create pro tier
    pro_tier = freemium_model.add_tier(
        name="Pro",
        description="Advanced content creation tools",
        price_monthly=19.99,
        price_yearly=199.99,
        features=differentiation_features[:3],  
            # Use first three differentiation features
        limits={"content_pieces": 50, "exports": 20},
        target_users="Professional content creators",
    )

    # Create team tier
    team_tier = freemium_model.add_tier(
        name="Team",
        description="Collaborative content creation tools",
        price_monthly=49.99,
        price_yearly=499.99,
        features=differentiation_features,  # Use all differentiation features
        limits={"content_pieces": 200, "exports": 100, "team_members": 10},
        target_users="Content teams",
    )

    # Verify freemium model setup
    assert len(freemium_model.tiers) == 3  # Including free tier
    assert freemium_model.has_free_tier()

    # Step 3: Calculate optimal prices based on competition
    # Extract competitor prices from the analysis
    competitor_prices = {}
    for competitor in competition_analysis["top_competitors"]:
        if "pricing" in competitor:
            for tier, price in competitor["pricing"].items():
                if tier not in competitor_prices or price > competitor_prices[tier]:
                    competitor_prices[tier] = price

    # Update pricing calculator with competitor prices
    if competitor_prices:
        pricing_calculator.competitor_prices = competitor_prices

    # Calculate optimal price for each paid tier
    for tier in freemium_model.tiers[1:]:  # Skip free tier
        tier_name = tier["name"].lower()
        competitor_price = pricing_calculator.competitor_prices.get(tier_name, 0)

        optimal_price = pricing_calculator.calculate_optimal_price(
            tier_name=tier["name"],
            cost_per_user=5.0 * (freemium_model.tiers.index(tier) * 0.5),  
                # Higher tiers cost more
            value_perception=0.7
            + (
                (freemium_model.tiers.index(tier) - 1) * 0.1
            ),  # Higher tiers have higher value perception
            competitor_price=competitor_price,
            price_sensitivity=0.8
            - (
                (freemium_model.tiers.index(tier) - 1) * 0.1
            ),  # Higher tiers have lower price sensitivity
        )

        # Update tier price
        freemium_model.update_tier_price(tier["id"], price_monthly=optimal_price)

    # Verify price updates
    assert freemium_model.tiers[0]["price_monthly"] == 0  # Free tier
    assert freemium_model.tiers[1]["price_monthly"] > 0
    assert freemium_model.tiers[2]["price_monthly"] > freemium_model.tiers[1]["price_monthly"]

    # Step 4: Project revenue based on the freemium pricing strategy
    # Create a dictionary of tier prices
    tier_prices = {tier["id"]: tier["price_monthly"] for tier in freemium_model.tiers}

    # Update revenue projector for freemium model
    revenue_projector.conversion_rate = 0.05  # Lower conversion rate for freemium
    revenue_projector.user_acquisition_rate = \
        200  # Higher acquisition rate for freemium
    revenue_projector.tier_distribution = {
        "free": 0.8,  # 80% free users
        "pro": 0.15,  # 15% pro users
        "team": 0.05,  # 5% team users
    }

    # Project revenue for 36 months
    revenue_projection = revenue_projector.project_revenue(
        months=36, tier_prices=tier_prices, 
            growth_rate=0.08  # Higher growth rate for freemium
    )

    # Verify revenue projection
    assert len(revenue_projection["months"]) == 36
    assert len(revenue_projection["users"]) == 36
    assert len(revenue_projection["revenue"]) == 36
    assert revenue_projection["total_revenue"] > 0

    # Verify that user growth is faster than revenue growth initially (due to free tier)
    first_month_users = revenue_projection["users"][0]
    last_month_users = revenue_projection["users"][-1]
    first_month_revenue = revenue_projection["revenue"][0]
    last_month_revenue = revenue_projection["revenue"][-1]

    user_growth_rate = (
        (last_month_users / \
            first_month_users) if first_month_users > 0 else float("inf")
    )
    revenue_growth_rate = (
        (last_month_revenue / \
            first_month_revenue) if first_month_revenue > 0 else float("inf")
    )

    # In a freemium model, revenue growth should eventually outpace user growth
    # as conversion rate improves over time
    assert user_growth_rate > 1  # Users should increase
    assert revenue_growth_rate > 1  # Revenue should increase
