"""
Integration tests for the solution-to-monetization workflow.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent_team import AgentTeam
from monetization import PricingCalculator, RevenueProjector, SubscriptionModel


@pytest.fixture
def mock_solution():
    """Create a mock solution for testing."""
    return {
        "id": "solution1",
        "name": "AI Inventory Manager",
        "description": "An AI-powered solution for inventory management",
        "features": [
            {
                "id": "feature1",
                "name": "Demand Forecasting",
                "description": "Predict future inventory needs based on historical data",
                "complexity": "high",
                "development_cost": "high",
                "value_proposition": "Save time and reduce stockouts",
            },
            {
                "id": "feature2",
                "name": "Reorder Alerts",
                "description": "Get alerts when inventory is running low",
                "complexity": "medium",
                "development_cost": "medium",
                "value_proposition": "Never run out of stock again",
            },
            {
                "id": "feature3",
                "name": "Inventory Analytics",
                "description": "Get insights into your inventory performance",
                "complexity": "medium",
                "development_cost": "medium",
                "value_proposition": "Make data-driven inventory decisions",
            },
        ],
        "market_data": {
            "target_audience": "E-commerce store owners and inventory managers",
            "market_size": "large",
            "competition": "medium",
        },
    }


@pytest.fixture
def mock_agents():
    """Create mock agents for testing."""
    # Mock the DeveloperAgent
    mock_developer = MagicMock()
    mock_developer.design_solution.return_value = {
        "id": "solution1",
        "name": "AI Inventory Manager",
        "description": "An AI-powered solution for inventory management",
        "features": [
            {
                "id": "feature1",
                "name": "Demand Forecasting",
                "description": "Predict future inventory needs based on historical data",
            },
            {
                "id": "feature2",
                "name": "Reorder Alerts",
                "description": "Get alerts when inventory is running low",
            },
        ],
    }

    # Mock the MonetizationAgent
    mock_monetization = MagicMock()
    mock_monetization.create_strategy.return_value = {
        "id": "strategy1",
        "name": "Freemium Strategy",
        "description": "A freemium monetization strategy",
        "subscription_model": {
            "name": "Inventory Manager Subscription",
            "tiers": [
                {
                    "name": "Free",
                    "price_monthly": 0.0,
                    "features": ["Basic Forecasting"],
                },
                {
                    "name": "Pro",
                    "price_monthly": 19.99,
                    "features": ["Advanced Forecasting", "Reorder Alerts"],
                },
            ],
        },
    }

    return {
        "developer": mock_developer,
        "monetization": mock_monetization,
    }


@patch("agent_team.team_config.DeveloperAgent")
@patch("agent_team.team_config.MonetizationAgent")
def test_solution_to_monetization_workflow(
    mock_monetization_class, mock_developer_class, mock_agents, mock_solution
):
    """Test the solution-to-monetization workflow."""
    # Set up the mock agents
    mock_developer_class.return_value = mock_agents["developer"]
    mock_monetization_class.return_value = mock_agents["monetization"]

    # Create a team
    team = AgentTeam("Test Team")

    # Create a monetization strategy from the solution
    monetization = team.create_monetization_strategy(mock_solution)

    # Check that the monetization agent's create_strategy method was called with the solution
    mock_agents["monetization"].create_strategy.assert_called_once_with(mock_solution)

    # Check that a monetization strategy was returned
    assert monetization["name"] == "Freemium Strategy"
    assert (
        monetization["subscription_model"]["name"] == "Inventory Manager Subscription"
    )
    assert len(monetization["subscription_model"]["tiers"]) == 2


def test_solution_features_to_subscription_model_integration(mock_solution):
    """Test the integration of solution features into subscription model."""
    # Create a subscription model based on the solution
    model = SubscriptionModel(
        name=f"{mock_solution['name']} Subscription",
        description=f"Subscription model for {mock_solution['name']}",
    )

    # Add features from the solution to the subscription model
    for feature in mock_solution["features"]:
        feature_type = (
            "premium"
            if feature.get("complexity") in ["high", "medium"]
            else "functional"
        )
        model.add_feature(
            name=feature["name"],
            description=feature["description"],
            feature_type=feature_type,
            value_proposition=feature.get("value_proposition", ""),
        )

    # Create tiers based on feature complexity and development cost
    basic_features = [
        f["id"] for f in model.features if f["feature_type"] == "functional"
    ]
    premium_features = [
        f["id"] for f in model.features if f["feature_type"] == "premium"
    ]

    # Add a free tier with basic features
    free_tier = model.add_tier(
        name="Free",
        description="Basic features for free users",
        price_monthly=0.0,
        features=basic_features[
            :1
        ],  # Only include the first basic feature in the free tier
    )

    # Add a pro tier with all features
    pro_tier = model.add_tier(
        name="Pro",
        description="All features for professional users",
        price_monthly=19.99,
        features=basic_features + premium_features,
    )

    # Add a business tier with all features and higher limits
    business_tier = model.add_tier(
        name="Business",
        description="All features with higher limits for business users",
        price_monthly=49.99,
        features=basic_features + premium_features,
    )

    # Verify that the subscription model has the correct features and tiers
    assert len(model.features) == len(mock_solution["features"])
    assert len(model.tiers) == 3

    # Check that the feature names were preserved
    model_feature_names = [feature["name"] for feature in model.features]
    for feature in mock_solution["features"]:
        assert feature["name"] in model_feature_names

    # Check that the tiers have the correct price structure
    assert model.tiers[0]["price_monthly"] == 0.0
    assert model.tiers[1]["price_monthly"] == 19.99
    assert model.tiers[2]["price_monthly"] == 49.99


def test_solution_to_pricing_calculator_integration(mock_solution):
    """Test the integration of solution data into pricing calculations."""
    # Calculate development costs based on solution features
    development_cost_map = {"low": 1000, "medium": 5000, "high": 10000}
    total_development_cost = sum(
        development_cost_map[feature.get("development_cost", "medium")]
        for feature in mock_solution["features"]
    )

    # Estimate ongoing costs per user
    cost_per_user = 5.0  # Base cost per user

    # Create a pricing calculator
    calculator = PricingCalculator(
        name=f"{mock_solution['name']} Pricing Calculator",
        description=f"Pricing calculator for {mock_solution['name']}",
        base_cost=cost_per_user,
        profit_margin=0.4,
        competitor_prices={"free": 0, "basic": 9.99, "pro": 19.99, "business": 49.99},
    )

    # Calculate optimal prices for different tiers
    pro_price = calculator.calculate_optimal_price(
        tier_name="Pro",
        cost_per_user=cost_per_user * 1.5,  # Higher cost for pro tier
        value_perception=0.8,
        competitor_price=19.99,
        price_sensitivity=0.7,
    )

    business_price = calculator.calculate_optimal_price(
        tier_name="Business",
        cost_per_user=cost_per_user * 2.5,  # Even higher cost for business tier
        value_perception=0.9,
        competitor_price=49.99,
        price_sensitivity=0.6,
    )

    # Verify that the calculated prices are reasonable
    assert pro_price > cost_per_user * 1.5  # Price should cover costs
    assert business_price > cost_per_user * 2.5  # Price should cover costs
    assert business_price > pro_price  # Business tier should be more expensive than Pro


def test_solution_to_revenue_projector_integration(mock_solution):
    """Test the integration of solution data into revenue projections."""
    # Create a subscription model based on the solution
    model = SubscriptionModel(
        name=f"{mock_solution['name']} Subscription",
        description=f"Subscription model for {mock_solution['name']}",
    )

    # Add features from the solution
    for feature in mock_solution["features"]:
        model.add_feature(name=feature["name"], description=feature["description"])

    # Add tiers
    free_tier = model.add_tier(
        name="Free", description="Basic features for free users", price_monthly=0.0
    )

    pro_tier = model.add_tier(
        name="Pro",
        description="All features for professional users",
        price_monthly=19.99,
    )

    business_tier = model.add_tier(
        name="Business",
        description="All features with higher limits for business users",
        price_monthly=49.99,
    )

    # Estimate market size and growth based on solution's market data
    market_size_map = {"small": 5000, "medium": 50000, "large": 500000}
    initial_users = market_size_map.get(
        mock_solution.get("market_data", {}).get("market_size", "medium"), 50000
    )

    competition_map = {"low": 0.4, "medium": 0.2, "high": 0.1}
    conversion_rate = competition_map.get(
        mock_solution.get("market_data", {}).get("competition", "medium"), 0.2
    )

    # Create a revenue projector
    projector = RevenueProjector(
        name=f"{mock_solution['name']} Revenue Projector",
        description=f"Revenue projector for {mock_solution['name']}",
        initial_users=initial_users,
        user_acquisition_rate=initial_users
        * 0.1,  # Acquire 10% of initial users per month
        conversion_rate=conversion_rate,
        churn_rate=0.05,
        tier_distribution={"Free": 0.7, "Pro": 0.2, "Business": 0.1},
    )

    # Project revenue for 24 months
    revenue_projections = projector.project_revenue(
        months=24, growth_rate=0.05, subscription_model=model
    )

    # Verify that the revenue projections are generated correctly
    assert len(revenue_projections) == 24
    assert all(
        isinstance(month["total_revenue"], float) for month in revenue_projections
    )
    assert all(isinstance(month["tier_revenue"], dict) for month in revenue_projections)

    # Verify that the tier revenue is calculated correctly
    for month in revenue_projections:
        assert (
            month["tier_revenue"]["Free"] == 0.0
        )  # Free tier should generate no revenue
        assert month["tier_revenue"]["Pro"] > 0.0  # Pro tier should generate revenue
        assert (
            month["tier_revenue"]["Business"] > 0.0
        )  # Business tier should generate revenue
        assert (
            month["tier_revenue"]["Pro"] < month["tier_revenue"]["Business"]
        )  # Business tier should generate more revenue than Pro


def test_end_to_end_solution_to_monetization_workflow(mock_solution):
    """Test end-to-end workflow from solution to monetization."""
    # 1. Create a subscription model based on the solution
    model = SubscriptionModel(
        name=f"{mock_solution['name']} Subscription",
        description=f"Subscription model for {mock_solution['name']}",
    )

    # 2. Add features from the solution
    feature_map = {}
    for feature in mock_solution["features"]:
        feature_type = (
            "premium"
            if feature.get("complexity") in ["high", "medium"]
            else "functional"
        )
        feature_obj = model.add_feature(
            name=feature["name"],
            description=feature["description"],
            feature_type=feature_type,
            value_proposition=feature.get("value_proposition", ""),
        )
        feature_map[feature["id"]] = feature_obj["id"]

    # 3. Add tiers based on feature complexity
    basic_features = [
        f["id"] for f in model.features if f["feature_type"] == "functional"
    ]
    premium_features = [
        f["id"] for f in model.features if f["feature_type"] == "premium"
    ]

    # 4. Create a free tier with limited features
    free_tier = model.add_tier(
        name="Free",
        description="Basic features for free users",
        price_monthly=0.0,
        features=basic_features[
            :1
        ],  # Only include the first basic feature in the free tier
        limits={"api_calls": 100, "exports": 10},
    )

    # 5. Create a pro tier with more features
    pro_tier = model.add_tier(
        name="Pro",
        description="Professional features for power users",
        price_monthly=19.99,
        features=basic_features
        + premium_features[:1],  # Include basic features and one premium feature
        limits={"api_calls": 1000, "exports": 100},
    )

    # 6. Create a business tier with all features
    business_tier = model.add_tier(
        name="Business",
        description="All features for business users",
        price_monthly=49.99,
        features=basic_features + premium_features,  # Include all features
        limits={"api_calls": 10000, "exports": 1000},
    )

    # 7. Calculate development costs
    development_cost_map = {"low": 1000, "medium": 5000, "high": 10000}
    total_development_cost = sum(
        development_cost_map[feature.get("development_cost", "medium")]
        for feature in mock_solution["features"]
    )

    # 8. Estimate costs per user
    cost_per_user = 5.0  # Base cost per user

    # 9. Create a pricing calculator
    calculator = PricingCalculator(
        name=f"{mock_solution['name']} Pricing Calculator",
        description=f"Pricing calculator for {mock_solution['name']}",
        base_cost=cost_per_user,
        profit_margin=0.4,
        competitor_prices={"free": 0, "basic": 9.99, "pro": 19.99, "business": 49.99},
    )

    # 10. Calculate optimal prices
    pro_price = calculator.calculate_optimal_price(
        tier_name="Pro",
        cost_per_user=cost_per_user * 1.5,
        value_perception=0.8,
        competitor_price=19.99,
        price_sensitivity=0.7,
    )

    business_price = calculator.calculate_optimal_price(
        tier_name="Business",
        cost_per_user=cost_per_user * 2.5,
        value_perception=0.9,
        competitor_price=49.99,
        price_sensitivity=0.6,
    )

    # 11. Update tier prices
    model.update_tier_price(pro_tier["id"], price_monthly=pro_price)
    model.update_tier_price(business_tier["id"], price_monthly=business_price)

    # 12. Estimate market size and growth
    market_size_map = {"small": 5000, "medium": 50000, "large": 500000}
    initial_users = market_size_map.get(
        mock_solution.get("market_data", {}).get("market_size", "medium"), 50000
    )

    competition_map = {"low": 0.4, "medium": 0.2, "high": 0.1}
    conversion_rate = competition_map.get(
        mock_solution.get("market_data", {}).get("competition", "medium"), 0.2
    )

    # 13. Create a revenue projector
    projector = RevenueProjector(
        name=f"{mock_solution['name']} Revenue Projector",
        description=f"Revenue projector for {mock_solution['name']}",
        initial_users=initial_users,
        user_acquisition_rate=initial_users * 0.1,
        conversion_rate=conversion_rate,
        churn_rate=0.05,
        tier_distribution={"Free": 0.7, "Pro": 0.2, "Business": 0.1},
    )

    # 14. Project revenue
    revenue_projections = projector.project_revenue(
        months=24, growth_rate=0.05, subscription_model=model
    )

    # 15. Calculate total revenue
    total_revenue = sum(month["total_revenue"] for month in revenue_projections)

    # 16. Calculate ROI
    roi = (total_revenue - total_development_cost) / total_development_cost

    # 17. Verify that the model, prices, and projections are reasonable
    assert len(model.features) == len(mock_solution["features"])
    assert len(model.tiers) == 3
    assert model.tiers[0]["price_monthly"] == 0.0
    assert model.tiers[1]["price_monthly"] == pro_price
    assert model.tiers[2]["price_monthly"] == business_price
    assert roi > 0  # ROI should be positive

    # 18. Return the monetization strategy as a complete package
    monetization_strategy = {
        "name": f"{mock_solution['name']} Monetization Strategy",
        "description": f"A monetization strategy for {mock_solution['name']}",
        "subscription_model": model,
        "development_cost": total_development_cost,
        "revenue_projections": revenue_projections,
        "roi": roi,
        "break_even_month": next(
            (
                i
                for i, month in enumerate(revenue_projections)
                if sum(m["total_revenue"] for m in revenue_projections[: i + 1])
                >= total_development_cost
            ),
            None,
        ),
    }

    assert monetization_strategy["name"]
    assert monetization_strategy["subscription_model"]
    assert monetization_strategy["revenue_projections"]
    assert monetization_strategy["roi"] > 0
    assert isinstance(monetization_strategy["break_even_month"], int)
