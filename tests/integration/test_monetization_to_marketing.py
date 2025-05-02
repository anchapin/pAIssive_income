"""
Integration tests for the monetization-to-marketing workflow.
"""

import pytest
from unittest.mock import patch, MagicMock

from agent_team import AgentTeam
from marketing import MarketingPlan, ConcreteContentGenerator, ChannelStrategy


@pytest.fixture
def mock_monetization_strategy():
    """Create a mock monetization strategy for testing."""
    return {
        "id": "strategy1",
        "name": "Freemium Strategy",
        "description": "A freemium monetization strategy",
        "subscription_model": {
            "name": "Inventory Manager Subscription",
            "tiers": [
                {
                    "id": "tier1",
                    "name": "Free",
                    "price_monthly": 0.0,
                    "features": ["Basic Forecasting"],
                    "limits": {"api_calls": 100, "exports": 10},
                },
                {
                    "id": "tier2",
                    "name": "Pro",
                    "price_monthly": 19.99,
                    "features": ["Advanced Forecasting", "Reorder Alerts"],
                    "limits": {"api_calls": 1000, "exports": 100},
                },
                {
                    "id": "tier3",
                    "name": "Business",
                    "price_monthly": 49.99,
                    "features": [
                        "Advanced Forecasting",
                        "Reorder Alerts",
                        "Custom Reporting",
                        "API Access",
                    ],
                    "limits": {"api_calls": 10000, "exports": 1000},
                },
            ],
        },
        "target_audience": {
            "segments": [
                "Small businesses",
                "E-commerce store owners",
                "Retail inventory managers",
            ],
            "user_personas": {
                "free_tier": "Small business owners looking for basic inventory management",
                "pro_tier": "Growing e-commerce businesses with moderate inventory needs",
                "business_tier": "Established businesses with complex inventory requirements",
            },
        },
        "pricing_strategy": {
            "model_type": "freemium",
            "pricing_psychology": "price_anchoring",
            "discount_strategy": "annual_discount",
        },
        "revenue_projections": {
            "year_1": {
                "total": 250000,
                "by_tier": {"Free": 0, "Pro": 150000, "Business": 100000},
            },
            "year_3": {
                "total": 1200000,
                "by_tier": {"Free": 0, "Pro": 500000, "Business": 700000},
            },
        },
    }


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
                "value_proposition": "Save time and reduce stockouts",
            },
            {
                "id": "feature2",
                "name": "Reorder Alerts",
                "description": "Get alerts when inventory is running low",
                "complexity": "medium",
                "value_proposition": "Never run out of stock again",
            },
            {
                "id": "feature3",
                "name": "Custom Reporting",
                "description": "Generate custom inventory reports",
                "complexity": "medium",
                "value_proposition": "Get the insights you need",
            },
            {
                "id": "feature4",
                "name": "API Access",
                "description": "Access inventory data through API",
                "complexity": "high",
                "value_proposition": "Integrate with your existing systems",
            },
        ],
        "market_data": {
            "target_audience": "E-commerce store owners and inventory managers",
            "market_size": "large",
            "competition": "medium",
        },
    }


@pytest.fixture
def mock_niche():
    """Create a mock niche for testing."""
    return {
        "id": "niche1",
        "name": "Inventory Management",
        "market_segment": "e-commerce",
        "description": "AI tools for inventory management",
        "opportunity_score": 0.8,
        "market_data": {
            "market_size": "large",
            "growth_rate": "high",
            "competition": "medium",
        },
        "problems": [
            {
                "id": "problem1",
                "name": "Inventory Forecasting",
                "description": "Difficulty predicting inventory needs",
                "severity": "high",
            }
        ],
    }


@pytest.fixture
def mock_agents():
    """Create mock agents for testing."""
    # Mock the MarketingAgent
    mock_marketing = MagicMock()
    mock_marketing.create_plan.return_value = {
        "id": "plan1",
        "name": "Inventory Manager Marketing Plan",
        "description": "A marketing plan for the AI Inventory Manager",
        "channels": ["content", "social", "email", "ads"],
        "target_audience": "E-commerce store owners",
        "budget": {
            "amount": 5000,
            "period": "monthly",
            "allocation": {"content": 0.3, "social": 0.2, "email": 0.15, "ads": 0.35},
        },
        "content_calendar": {
            "content_types": ["blog_posts", "case_studies", "webinars", "newsletters"],
            "frequency": "weekly",
        },
    }

    return {"marketing": mock_marketing}


@patch("agent_team.team_config.MarketingAgent")
def test_monetization_to_marketing_workflow(
    mock_marketing_class,
    mock_agents,
    mock_monetization_strategy,
    mock_solution,
    mock_niche,
):
    """Test the monetization-to-marketing workflow."""
    # Set up the mock agents
    mock_marketing_class.return_value = mock_agents["marketing"]

    # Create a team
    team = AgentTeam("Test Team")

    # Create a marketing plan from the niche, solution, and monetization strategy
    marketing_plan = team.create_marketing_plan(
        mock_niche, mock_solution, mock_monetization_strategy
    )

    # Check that the marketing agent's create_plan method was called
    assert mock_agents["marketing"].create_plan.called

    # Check that it was called with the right number of arguments
    args, kwargs = mock_agents["marketing"].create_plan.call_args
    assert len(args) == 3  # Should be called with 3 positional arguments

    # Check that a marketing plan was returned
    assert marketing_plan["name"] == "Inventory Manager Marketing Plan"
    assert "content" in marketing_plan["channels"]
    assert "social" in marketing_plan["channels"]
    assert "email" in marketing_plan["channels"]
    assert marketing_plan["target_audience"] == "E-commerce store owners"


def test_subscription_tiers_to_channel_strategy_integration(
    mock_monetization_strategy, mock_solution
):
    """Test integration between subscription tiers and marketing channel strategy."""
    # Create a channel strategy using monetization data
    channel_strategy = ChannelStrategy(
        name=f"{mock_solution['name']} Channel Strategy",
        description=f"Channel strategy for {mock_solution['name']}",
    )

    # Extract target audiences from monetization strategy
    audiences = []
    for segment in mock_monetization_strategy["target_audience"]["segments"]:
        audiences.append({"name": segment, "tier_focus": "all"})

    for tier_name, persona in mock_monetization_strategy["target_audience"][
        "user_personas"
    ].items():
        audiences.append({"name": persona, "tier_focus": tier_name})

    # Add channels based on audience and tiers
    # Content marketing for all tiers
    channel_strategy.add_channel(
        name="Content Marketing",
        audience=["all"],
        description="Blog posts, guides, and case studies",
        tiers_focus=["all"],
        cost_efficiency=0.8,
        primary_metrics=["traffic", "leads", "conversions"],
    )

    # Email marketing for leads and premium tier upsells
    channel_strategy.add_channel(
        name="Email Marketing",
        audience=["leads", "free_tier"],
        description="Newsletters, product updates, and upgrade offers",
        tiers_focus=["pro_tier", "business_tier"],
        cost_efficiency=0.9,
        primary_metrics=["open_rate", "click_rate", "conversions"],
    )

    # Add social media strategy
    channel_strategy.add_channel(
        name="Social Media",
        audience=["all"],
        description="Social posts, engagement, and community building",
        tiers_focus=["free_tier", "pro_tier"],
        cost_efficiency=0.7,
        primary_metrics=["engagement", "followers", "traffic"],
    )

    # Add paid search specifically for business tier
    channel_strategy.add_channel(
        name="Paid Search",
        audience=["business_tier"],
        description="Google Ads for high-intent business keywords",
        tiers_focus=["business_tier"],
        cost_efficiency=0.6,
        primary_metrics=["clicks", "conversions", "ROI"],
    )

    # Verify channel strategy integration with monetization tiers
    assert len(channel_strategy.channels) == 4

    # Check that each channel has the appropriate focus
    free_tier_channels = [
        c
        for c in channel_strategy.channels
        if "free_tier" in c["tiers_focus"] or "all" in c["tiers_focus"]
    ]
    pro_tier_channels = [
        c
        for c in channel_strategy.channels
        if "pro_tier" in c["tiers_focus"] or "all" in c["tiers_focus"]
    ]
    business_tier_channels = [
        c
        for c in channel_strategy.channels
        if "business_tier" in c["tiers_focus"] or "all" in c["tiers_focus"]
    ]

    # All tiers should have content marketing
    assert any(c["name"] == "Content Marketing" for c in free_tier_channels)
    assert any(c["name"] == "Content Marketing" for c in pro_tier_channels)
    assert any(c["name"] == "Content Marketing" for c in business_tier_channels)

    # Business tier should have paid search
    assert any(c["name"] == "Paid Search" for c in business_tier_channels)
    assert not any(c["name"] == "Paid Search" for c in free_tier_channels)

    # Verify channel allocations are set up
    budget_allocation = channel_strategy.calculate_budget_allocation(10000)
    assert sum(budget_allocation.values()) == 10000
    assert all(value > 0 for value in budget_allocation.values())


def test_freemium_model_to_content_strategy_integration(mock_monetization_strategy):
    """Test integration between freemium model and content strategy."""
    # Extract the subscription model tiers
    tiers = mock_monetization_strategy["subscription_model"]["tiers"]

    # Create a content generator for each tier
    content_generators = {}

    for tier in tiers:
        tier_name = tier["name"]

        # Create content generator
        generator = ConcreteContentGenerator(
            name=f"{tier_name} Tier Content Generator",
            description=f"Content generator for {tier_name} tier",
        )

        # Add content types based on tier
        if tier_name == "Free":
            # For free tier, focus on awareness and education
            generator.add_content_type(
                name="Blog Posts",
                format="text",
                frequency="weekly",
                goal="awareness",
                target_metrics=["traffic", "signups"],
            )
            generator.add_content_type(
                name="Social Media Posts",
                format="text+image",
                frequency="daily",
                goal="engagement",
                target_metrics=["likes", "shares", "clicks"],
            )

        elif tier_name == "Pro":
            # For pro tier, focus on lead nurturing and conversion
            generator.add_content_type(
                name="Case Studies",
                format="pdf",
                frequency="monthly",
                goal="conversion",
                target_metrics=["downloads", "sales calls"],
            )
            generator.add_content_type(
                name="Webinars",
                format="video",
                frequency="monthly",
                goal="lead_nurturing",
                target_metrics=["registrations", "attendance", "upgrades"],
            )

        elif tier_name == "Business":
            # For business tier, focus on ROI and integration
            generator.add_content_type(
                name="White Papers",
                format="pdf",
                frequency="quarterly",
                goal="thought_leadership",
                target_metrics=["downloads", "sales meetings"],
            )
            generator.add_content_type(
                name="Integration Guides",
                format="text+code",
                frequency="as_needed",
                goal="retention",
                target_metrics=["api_adoption", "feature_usage"],
            )

        # Add features as topics
        tier_features = tier["features"]
        for feature in tier_features:
            generator.add_topic(
                name=feature,
                description=f"Content about {feature}",
                keywords=[feature.lower().replace(" ", "-"), feature.lower()],
            )

        content_generators[tier_name] = generator

    # Verify that content generators were created for each tier
    assert len(content_generators) == len(tiers)

    # Check that content types are appropriate for each tier
    assert any(
        ct["name"] == "Blog Posts" for ct in content_generators["Free"].content_types
    )
    assert any(
        ct["name"] == "Case Studies" for ct in content_generators["Pro"].content_types
    )
    assert any(
        ct["name"] == "White Papers"
        for ct in content_generators["Business"].content_types
    )

    # Generate sample content for validation
    free_content = content_generators["Free"].generate_content(
        content_type="Blog Posts",
        topic="Basic Forecasting",
        title="Introduction to Inventory Forecasting",
    )

    pro_content = content_generators["Pro"].generate_content(
        content_type="Case Studies",
        topic="Advanced Forecasting",
        title="How Company X Reduced Stockouts by 75% with Advanced Forecasting",
    )

    business_content = content_generators["Business"].generate_content(
        content_type="Integration Guides",
        topic="API Access",
        title="Integrating Your ERP System with Our Inventory API",
    )

    # Verify that content contains appropriate keywords
    assert "Basic Forecasting" in str(free_content)
    assert "Advanced Forecasting" in str(pro_content)
    assert "API" in str(business_content)


def test_pricing_strategy_to_marketing_message_alignment(mock_monetization_strategy):
    """Test alignment of pricing strategy with marketing messages."""
    # Extract the pricing strategy and tiers
    pricing_strategy = mock_monetization_strategy["pricing_strategy"]
    tiers = mock_monetization_strategy["subscription_model"]["tiers"]

    # Create marketing messages based on pricing strategy
    marketing_messages = {}

    # For freemium model, emphasize value of free tier and upgrade benefits
    if pricing_strategy["model_type"] == "freemium":
        marketing_messages["free_tier_headline"] = "Start Managing Inventory for Free"
        marketing_messages["free_tier_value_prop"] = (
            "Get basic inventory forecasting at no cost"
        )
        marketing_messages["upgrade_message"] = "Unlock Advanced Features with Pro"

    # For price anchoring strategy, emphasize most valuable plan
    if pricing_strategy["pricing_psychology"] == "price_anchoring":
        # Find the top tier
        top_tier = max(tiers, key=lambda t: t["price_monthly"])
        middle_tier = (
            [t for t in tiers if t["price_monthly"] > 0 and t != top_tier][0]
            if len(tiers) > 2
            else top_tier
        )

        marketing_messages["recommended_plan"] = middle_tier["name"]
        marketing_messages["price_comparison"] = (
            f"Get all essential features at just ${middle_tier['price_monthly']} per month"
        )
        marketing_messages["enterprise_message"] = (
            f"Need more? Our {top_tier['name']} plan includes everything at ${top_tier['price_monthly']} per month"
        )

    # For annual discounts, highlight savings
    if pricing_strategy["discount_strategy"] == "annual_discount":
        marketing_messages["annual_discount_headline"] = "Save 20% with Annual Billing"
        marketing_messages["annual_discount_message"] = (
            "Commit for a year and get 2 months free"
        )

    # Verify that marketing messages align with pricing strategy
    assert "free_tier_headline" in marketing_messages
    assert "upgrade_message" in marketing_messages

    if pricing_strategy["pricing_psychology"] == "price_anchoring":
        assert "recommended_plan" in marketing_messages
        assert "price_comparison" in marketing_messages

    if pricing_strategy["discount_strategy"] == "annual_discount":
        assert "annual_discount_headline" in marketing_messages
        assert "annual_discount_message" in marketing_messages

    # Verify message content aligns with strategy
    if pricing_strategy["model_type"] == "freemium":
        assert "Free" in marketing_messages["free_tier_headline"]
        assert "Unlock" in marketing_messages["upgrade_message"]


def test_revenue_projections_to_marketing_budget_allocation(mock_monetization_strategy):
    """Test using revenue projections to inform marketing budget allocation."""
    # Extract revenue projections
    revenue_projections = mock_monetization_strategy["revenue_projections"]

    # Calculate marketing budget as percentage of projected revenue
    year_1_revenue = revenue_projections["year_1"]["total"]
    marketing_budget_year_1 = year_1_revenue * 0.2  # 20% of revenue

    # Allocate budget based on tier revenue projections
    tier_allocations_year_1 = {}
    for tier, revenue in revenue_projections["year_1"]["by_tier"].items():
        tier_allocations_year_1[tier] = (
            (revenue / year_1_revenue) * marketing_budget_year_1
            if year_1_revenue > 0
            else 0
        )

    # Create a marketing plan with budget allocation
    marketing_plan = MarketingPlan(
        name="AI Inventory Manager Marketing Plan",
        description="Marketing plan based on monetization strategy and revenue projections",
    )

    # Add budget
    marketing_plan.set_budget(
        total_amount=marketing_budget_year_1,
        period="annual",
        allocation_strategy="tier_based",
    )

    # Add budget allocation for each tier
    for tier, amount in tier_allocations_year_1.items():
        marketing_plan.add_tier_budget_allocation(
            tier_name=tier,
            amount=amount,
            focus_areas=(
                ["acquisition"]
                if tier == "Free"
                else ["acquisition", "conversion", "retention"]
            ),
        )

    # Add channels and strategies
    marketing_plan.add_channel(
        name="Content Marketing",
        budget_percentage=0.30,
        primary_goal="awareness",
        target_tiers=["Free", "Pro"],
    )

    marketing_plan.add_channel(
        name="SEO",
        budget_percentage=0.15,
        primary_goal="traffic",
        target_tiers=["Free", "Pro", "Business"],
    )

    marketing_plan.add_channel(
        name="Email Marketing",
        budget_percentage=0.15,
        primary_goal="conversion",
        target_tiers=["Free", "Pro"],
    )

    marketing_plan.add_channel(
        name="Paid Advertising",
        budget_percentage=0.25,
        primary_goal="acquisition",
        target_tiers=["Pro", "Business"],
    )

    marketing_plan.add_channel(
        name="Direct Sales",
        budget_percentage=0.15,
        primary_goal="conversion",
        target_tiers=["Business"],
    )

    # Verify marketing budget allocation
    assert marketing_plan.budget["total_amount"] == marketing_budget_year_1
    assert marketing_plan.budget["period"] == "annual"

    # Check that the tier budget allocations are proportional to revenue
    for tier, allocation in marketing_plan.tier_budget_allocations.items():
        expected_proportion = (
            revenue_projections["year_1"]["by_tier"].get(tier, 0) / year_1_revenue
            if year_1_revenue > 0
            else 0
        )
        actual_proportion = (
            allocation["amount"] / marketing_budget_year_1
            if marketing_budget_year_1 > 0
            else 0
        )
        assert (
            abs(expected_proportion - actual_proportion) < 0.01
        )  # Within 1% margin for floating point comparison

    # Verify channel allocations
    channel_allocation_sum = sum(
        c["budget_percentage"] for c in marketing_plan.channels
    )
    assert abs(channel_allocation_sum - 1.0) < 0.01  # Should sum to approximately 1.0

    # Check that channels are targeting appropriate tiers
    free_tier_channels = [
        c for c in marketing_plan.channels if "Free" in c["target_tiers"]
    ]
    business_tier_channels = [
        c for c in marketing_plan.channels if "Business" in c["target_tiers"]
    ]

    assert len(free_tier_channels) >= 2  # Free tier should have at least 2 channels
    assert (
        len(business_tier_channels) >= 2
    )  # Business tier should have at least 2 channels
    assert any(
        c["name"] == "Direct Sales" for c in business_tier_channels
    )  # Business tier should include direct sales


def test_end_to_end_monetization_to_marketing_workflow(
    mock_monetization_strategy, mock_solution, mock_niche
):
    """Test end-to-end workflow from monetization strategy to marketing plan."""
    # Step 1: Extract key information from monetization strategy
    subscription_model = mock_monetization_strategy["subscription_model"]
    tiers = subscription_model["tiers"]
    target_audience = mock_monetization_strategy["target_audience"]
    pricing_strategy = mock_monetization_strategy["pricing_strategy"]
    revenue_projections = mock_monetization_strategy["revenue_projections"]

    # Step 2: Create a marketing plan
    marketing_plan = MarketingPlan(
        name=f"{mock_solution['name']} Marketing Plan",
        description=f"Comprehensive marketing plan for {mock_solution['name']}",
    )

    # Step 3: Set marketing goals based on monetization strategy and revenue projections
    year_1_revenue = revenue_projections["year_1"]["total"]
    marketing_plan.add_goal(
        name="Revenue Target",
        description=f"Achieve ${year_1_revenue} in annual recurring revenue",
        metric="ARR",
        target_value=year_1_revenue,
        timeframe="1 year",
    )

    free_to_paid_conversion_goal = 0.05  # 5% conversion from free to paid
    marketing_plan.add_goal(
        name="Free to Paid Conversion",
        description="Convert free tier users to paid subscriptions",
        metric="conversion_rate",
        target_value=free_to_paid_conversion_goal,
        timeframe="ongoing",
    )

    # Different goals for different tiers
    marketing_plan.add_goal(
        name="Free Tier User Acquisition",
        description="Acquire new free tier users",
        metric="free_signups",
        target_value=10000,
        timeframe="1 year",
    )

    marketing_plan.add_goal(
        name="Pro Tier User Acquisition",
        description="Acquire new pro tier subscribers",
        metric="pro_subscriptions",
        target_value=500,
        timeframe="1 year",
    )

    marketing_plan.add_goal(
        name="Business Tier User Acquisition",
        description="Acquire new business tier subscribers",
        metric="business_subscriptions",
        target_value=100,
        timeframe="1 year",
    )

    # Step 4: Calculate marketing budget and allocation
    marketing_budget = year_1_revenue * 0.2  # 20% of projected revenue
    marketing_plan.set_budget(
        total_amount=marketing_budget, period="annual", allocation_strategy="tier_based"
    )

    # Step 5: Define target personas based on monetization strategy
    for tier_name, persona_description in target_audience["user_personas"].items():
        marketing_plan.add_persona(
            name=f"{tier_name.replace('_', ' ').title()} User",
            description=persona_description,
            target_tier=tier_name,
            goals=["improve inventory management", "reduce stockouts"],
            pain_points=["manual inventory tracking", "stockouts", "overstocking"],
        )

    # Step 6: Define marketing channels and strategies based on tiers
    # Free tier - focus on awareness and acquisition
    marketing_plan.add_channel(
        name="Content Marketing",
        budget_percentage=0.25,
        primary_goal="awareness",
        target_tiers=["free_tier"],
        strategies=[
            "Educational blog posts about inventory management",
            "SEO optimization for inventory management keywords",
            "Free tools and resources",
        ],
    )

    marketing_plan.add_channel(
        name="Social Media",
        budget_percentage=0.15,
        primary_goal="engagement",
        target_tiers=["free_tier", "pro_tier"],
        strategies=[
            "Platform-specific content strategy",
            "Community building",
            "User testimonials and case studies",
        ],
    )

    # Pro tier - focus on conversion and retention
    marketing_plan.add_channel(
        name="Email Marketing",
        budget_percentage=0.20,
        primary_goal="conversion",
        target_tiers=["free_tier", "pro_tier"],
        strategies=[
            "Free-to-Pro upgrade campaigns",
            "Feature announcements",
            "Case studies showcasing ROI",
        ],
    )

    # Business tier - focus on high-value acquisition
    marketing_plan.add_channel(
        name="Paid Advertising",
        budget_percentage=0.25,
        primary_goal="acquisition",
        target_tiers=["pro_tier", "business_tier"],
        strategies=[
            "Google Ads for high-intent keywords",
            "Retargeting campaigns",
            "LinkedIn ads for business decision-makers",
        ],
    )

    marketing_plan.add_channel(
        name="Direct Sales",
        budget_percentage=0.15,
        primary_goal="conversion",
        target_tiers=["business_tier"],
        strategies=[
            "Outbound sales campaigns",
            "Demo requests follow-up",
            "Partner referral program",
        ],
    )

    # Step 7: Create content strategy aligned with monetization tiers
    marketing_plan.add_content_strategy(
        name="Tier-Based Content Strategy",
        description="Content strategy aligned with subscription tiers",
        content_types=[
            {
                "name": "Blog Posts",
                "target_tiers": ["free_tier"],
                "frequency": "weekly",
                "topics": ["Basic inventory management", "Getting started guides"],
            },
            {
                "name": "Case Studies",
                "target_tiers": ["pro_tier"],
                "frequency": "monthly",
                "topics": ["ROI from advanced forecasting", "Time savings with alerts"],
            },
            {
                "name": "White Papers",
                "target_tiers": ["business_tier"],
                "frequency": "quarterly",
                "topics": [
                    "Enterprise inventory management",
                    "API integration strategies",
                ],
            },
        ],
    )

    # Step 8: Create messaging strategy based on pricing strategy
    messaging = {}

    # For freemium model
    if pricing_strategy["model_type"] == "freemium":
        messaging["value_proposition"] = (
            "Start managing inventory for free, upgrade as you grow"
        )
        messaging["free_tier"] = "Get started with basic forecasting at no cost"
        messaging["pro_tier"] = "Unlock advanced features and save time with Pro"
        messaging["business_tier"] = (
            "Get full functionality and dedicated support with Business"
        )

    # For price anchoring
    if pricing_strategy["pricing_psychology"] == "price_anchoring":
        messaging["pricing_display"] = (
            "Show all three tiers with Pro as the recommended option"
        )
        messaging["recommended_plan"] = "Pro"

    # For annual discount
    if pricing_strategy["discount_strategy"] == "annual_discount":
        messaging["discount_message"] = "Save 20% with annual billing"

    marketing_plan.set_messaging_strategy(messaging)

    # Step 9: Create conversion funnels for each tier
    for tier_name in ["free_tier", "pro_tier", "business_tier"]:
        marketing_plan.add_conversion_funnel(
            name=f"{tier_name.replace('_', ' ').title()} Conversion Funnel",
            target_tier=tier_name,
            stages=[
                {
                    "name": "Awareness",
                    "channels": ["Content Marketing", "Social Media"],
                },
                {"name": "Interest", "channels": ["Email Marketing", "Retargeting"]},
                {"name": "Consideration", "channels": ["Case Studies", "Webinars"]},
                {
                    "name": "Conversion",
                    "channels": [
                        "Email Marketing",
                        "Direct Sales" if tier_name == "business_tier" else "Website",
                    ],
                },
                {
                    "name": "Retention",
                    "channels": ["Email Marketing", "Customer Success"],
                },
            ],
        )

    # Step 10: Verify the marketing plan is comprehensive and aligned with monetization strategy
    # Check budget allocation
    assert marketing_plan.budget["total_amount"] == marketing_budget

    # Check channel alignment
    channel_names = [c["name"] for c in marketing_plan.channels]
    assert "Content Marketing" in channel_names
    assert "Direct Sales" in channel_names

    # Check content strategy alignment with tiers
    content_strategy = marketing_plan.content_strategies[0]
    free_tier_content = [
        ct
        for ct in content_strategy["content_types"]
        if "free_tier" in ct["target_tiers"]
    ]
    business_tier_content = [
        ct
        for ct in content_strategy["content_types"]
        if "business_tier" in ct["target_tiers"]
    ]

    assert len(free_tier_content) >= 1
    assert len(business_tier_content) >= 1
    assert any("Blog Posts" == ct["name"] for ct in free_tier_content)
    assert any("White Papers" == ct["name"] for ct in business_tier_content)

    # Check messaging alignment with pricing strategy
    assert "free_tier" in marketing_plan.messaging_strategy
    assert "pro_tier" in marketing_plan.messaging_strategy
    assert "business_tier" in marketing_plan.messaging_strategy

    if pricing_strategy["model_type"] == "freemium":
        assert "free" in marketing_plan.messaging_strategy["value_proposition"].lower()

    if pricing_strategy["discount_strategy"] == "annual_discount":
        assert "discount_message" in marketing_plan.messaging_strategy

    # Check conversion funnels
    assert len(marketing_plan.conversion_funnels) == 3  # One for each tier

    # Final verification - the complete marketing plan should have all components
    assert hasattr(marketing_plan, "name")
    assert hasattr(marketing_plan, "description")
    assert hasattr(marketing_plan, "goals")
    assert hasattr(marketing_plan, "budget")
    assert hasattr(marketing_plan, "personas")
    assert hasattr(marketing_plan, "channels")
    assert hasattr(marketing_plan, "content_strategies")
    assert hasattr(marketing_plan, "messaging_strategy")
    assert hasattr(marketing_plan, "conversion_funnels")
