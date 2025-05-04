"""
"""
Tests for the channel strategies components in the Marketing module.
Tests for the channel strategies components in the Marketing module.
"""
"""


from marketing.channel_strategies import (ContentMarketingStrategy,
from marketing.channel_strategies import (ContentMarketingStrategy,
EmailMarketingStrategy,
EmailMarketingStrategy,
MarketingStrategy,
MarketingStrategy,
SocialMediaStrategy)
SocialMediaStrategy)




def test_marketing_strategy_init():
    def test_marketing_strategy_init():
    """Test MarketingStrategy initialization."""
    strategy = MarketingStrategy(
    name="Test Marketing Strategy", description="A test marketing strategy"
    )

    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Marketing Strategy"
    assert strategy.description == "A test marketing strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")


    def test_marketing_strategy_create_plan():
    """Test create_plan method of MarketingStrategy."""
    strategy = MarketingStrategy(
    name="Test Marketing Strategy", description="A test marketing strategy"
    )

    # Create a plan
    plan = strategy.create_plan(
    niche="e-commerce",
    target_audience="Small business owners",
    budget=1000,
    timeline="3 months",
    )

    # Check that the plan has the expected attributes
    assert "id" in plan
    assert "name" in plan
    assert "description" in plan
    assert "niche" in plan
    assert "target_audience" in plan
    assert "budget" in plan
    assert "timeline" in plan
    assert "channels" in plan
    assert "goals" in plan
    assert "metrics" in plan
    assert "created_at" in plan

    # Check specific values
    assert plan["niche"] == "e-commerce"
    assert plan["target_audience"] == "Small business owners"
    assert plan["budget"] == 1000
    assert plan["timeline"] == "3 months"
    assert isinstance(plan["channels"], list)
    assert isinstance(plan["goals"], list)
    assert isinstance(plan["metrics"], list)


    def test_content_marketing_strategy_init():
    """Test ContentMarketingStrategy initialization."""
    strategy = ContentMarketingStrategy(
    name="Test Content Marketing Strategy",
    description="A test content marketing strategy",
    )

    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Content Marketing Strategy"
    assert strategy.description == "A test content marketing strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")
    assert hasattr(strategy, "content_types")
    assert isinstance(strategy.content_types, list)
    assert len(strategy.content_types) > 0


    def test_content_marketing_strategy_create_content_plan():
    """Test create_content_plan method of ContentMarketingStrategy."""
    strategy = ContentMarketingStrategy(
    name="Test Content Marketing Strategy",
    description="A test content marketing strategy",
    )

    # Create a content plan
    plan = strategy.create_content_plan(
    niche="e-commerce",
    target_audience="Small business owners",
    content_types=["blog_posts", "videos", "infographics"],
    frequency="weekly",
    distribution_channels=["website", "social_media"],
    )

    # Check that the plan has the expected attributes
    assert "id" in plan
    assert "name" in plan
    assert "niche" in plan
    assert "target_audience" in plan
    assert "content_types" in plan
    assert "frequency" in plan
    assert "distribution_channels" in plan
    assert "content_calendar" in plan
    assert "created_at" in plan

    # Check specific values
    assert plan["niche"] == "e-commerce"
    assert plan["target_audience"] == "Small business owners"
    assert plan["content_types"] == ["blog_posts", "videos", "infographics"]
    assert plan["frequency"] == "weekly"
    assert plan["distribution_channels"] == ["website", "social_media"]
    assert isinstance(plan["content_calendar"], list)


    def test_social_media_strategy_init():
    """Test SocialMediaStrategy initialization."""
    strategy = SocialMediaStrategy(
    name="Test Social Media Strategy", description="A test social media strategy"
    )

    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Social Media Strategy"
    assert strategy.description == "A test social media strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")
    assert hasattr(strategy, "platforms")
    assert isinstance(strategy.platforms, list)
    assert len(strategy.platforms) > 0


    def test_social_media_strategy_create_platform_plan():
    """Test create_platform_plan method of SocialMediaStrategy."""
    strategy = SocialMediaStrategy(
    name="Test Social Media Strategy", description="A test social media strategy"
    )

    # Create a platform plan
    plan = strategy.create_platform_plan(
    platform="instagram",
    target_audience="Small business owners",
    content_types=["images", "stories", "reels"],
    posting_frequency="daily",
    engagement_tactics=["hashtags", "contests", "collaborations"],
    )

    # Check that the plan has the expected attributes
    assert "id" in plan
    assert "platform" in plan
    assert "target_audience" in plan
    assert "content_types" in plan
    assert "posting_frequency" in plan
    assert "engagement_tactics" in plan
    assert "content_ideas" in plan
    assert "metrics" in plan
    assert "created_at" in plan

    # Check specific values
    assert plan["platform"] == "instagram"
    assert plan["target_audience"] == "Small business owners"
    assert plan["content_types"] == ["images", "stories", "reels"]
    assert plan["posting_frequency"] == "daily"
    assert plan["engagement_tactics"] == ["hashtags", "contests", "collaborations"]
    assert isinstance(plan["content_ideas"], list)
    assert isinstance(plan["metrics"], list)


    def test_email_marketing_strategy_init():
    """Test EmailMarketingStrategy initialization."""
    strategy = EmailMarketingStrategy(
    name="Test Email Marketing Strategy",
    description="A test email marketing strategy",
    )

    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Email Marketing Strategy"
    assert strategy.description == "A test email marketing strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")
    assert hasattr(strategy, "email_types")
    assert isinstance(strategy.email_types, list)
    assert len(strategy.email_types) > 0


    def test_email_marketing_strategy_create_campaign():
    """Test create_campaign method of EmailMarketingStrategy."""
    strategy = EmailMarketingStrategy(
    name="Test Email Marketing Strategy",
    description="A test email marketing strategy",
    )

    # Create a campaign
    campaign = strategy.create_campaign(
    name="Welcome Campaign",
    target_audience="New subscribers",
    email_sequence=["welcome", "product_intro", "case_study", "offer"],
    frequency="3 days apart",
    goals=["build_relationship", "introduce_product", "convert"],
    )

    # Check that the campaign has the expected attributes
    assert "id" in campaign
    assert "name" in campaign
    assert "target_audience" in campaign
    assert "email_sequence" in campaign
    assert "frequency" in campaign
    assert "goals" in campaign
    assert "metrics" in campaign
    assert "created_at" in campaign

    # Check specific values
    assert campaign["name"] == "Welcome Campaign"
    assert campaign["target_audience"] == "New subscribers"
    assert campaign["email_sequence"] == [
    "welcome",
    "product_intro",
    "case_study",
    "offer",
    ]
    assert campaign["frequency"] == "3 days apart"
    assert campaign["goals"] == ["build_relationship", "introduce_product", "convert"]
    assert isinstance(campaign["metrics"], list)


    def test_channel_prioritization():
    """Test channel prioritization based on target audience and goals."""
    strategy = MarketingStrategy(
    name="Test Marketing Strategy", description="A test marketing strategy"
    )

    # Create a plan with specific audience and goals
    plan = strategy.create_plan(
    niche="e-commerce",
    target_audience={
    "primary": "Small business owners",
    "demographics": {
    "age": "30-50",
    "business_size": "1-50 employees",
    "industry": "retail",
    },
    },
    budget=10000,
    timeline="6 months",
    goals={
    "primary": "lead_generation",
    "secondary": ["brand_awareness", "customer_retention"],
    },
    )

    # Check channel prioritization
    assert "channels" in plan
    channels = plan["channels"]

    # Verify channels are sorted by priority
    for i in range(len(channels) - 1):
    assert channels[i]["priority_score"] >= channels[i + 1]["priority_score"]

    # Verify budget allocation aligns with priority
    for i in range(len(channels) - 1):
    assert channels[i]["budget_allocation"] >= channels[i + 1]["budget_allocation"]

    # Verify primary channels match goals
    primary_channels = [c for c in channels if c["priority_score"] > 0.7]
    assert any(c["focus"] == "lead_generation" for c in primary_channels)

    # Verify channel-audience fit
    for channel in channels:
    assert "audience_fit_score" in channel
    assert 0 <= channel["audience_fit_score"] <= 1


    def test_budget_based_channel_strategy():
    """Test channel strategy adaptation based on budget constraints."""
    strategy = MarketingStrategy(
    name="Test Marketing Strategy", description="A test marketing strategy"
    )

    # Test with different budget levels
    low_budget_plan = strategy.create_plan(
    niche="e-commerce",
    target_audience="Small business owners",
    budget=1000,
    timeline="3 months",
    )

    high_budget_plan = strategy.create_plan(
    niche="e-commerce",
    target_audience="Small business owners",
    budget=50000,
    timeline="3 months",
    )

    # Low budget should focus on cost-effective channels
    low_budget_channels = low_budget_plan["channels"]
    assert len(low_budget_channels) <= 3  # Focus on fewer channels
    assert any(c["type"] == "social_media_organic" for c in low_budget_channels)
    assert any(c["type"] == "content_marketing" for c in low_budget_channels)

    # High budget should include paid channels
    high_budget_channels = high_budget_plan["channels"]
    assert len(high_budget_channels) >= 4  # More comprehensive strategy
    assert any(c["type"] == "paid_advertising" for c in high_budget_channels)
    assert any(c["type"] == "influencer_marketing" for c in high_budget_channels)

    # Verify budget allocations
    assert sum(c["budget_allocation"] for c in low_budget_channels) <= 1000
    assert sum(c["budget_allocation"] for c in high_budget_channels) <= 50000


    def test_cross_channel_campaign_coordination():
    """Test coordination between different marketing channels."""
    strategy = MarketingStrategy(
    name="Test Marketing Strategy", description="A test marketing strategy"
    )

    # Create an integrated campaign plan
    campaign = strategy.create_integrated_campaign(
    name="Product Launch Campaign",
    channels=["social_media", "email", "content", "paid_ads"],
    timeline={
    "pre_launch": "2 weeks",
    "launch": "1 week",
    "post_launch": "4 weeks",
    },
    budget=20000,
    main_goal="product_launch",
    )

    # Check campaign structure
    assert "phases" in campaign
    assert len(campaign["phases"]) == 3  # pre-launch, launch, post-launch

    # Check channel coordination
    for phase in campaign["phases"]:
    assert "channel_actions" in phase
    assert "timeline" in phase
    assert "goals" in phase

    # Verify each channel has coordinated actions
    channel_actions = phase["channel_actions"]
    assert all("timing" in action for action in channel_actions)
    assert all("coordination_points" in action for action in channel_actions)

    # Check for message consistency
    messages = [action["message_theme"] for action in channel_actions]
    assert (
    len(set(messages)) == 1
    )  # All channels should share the same message theme


    def test_channel_performance_metrics():
    """Test channel performance metrics and ROI calculation."""
    strategy = MarketingStrategy(
    name="Test Marketing Strategy", description="A test marketing strategy"
    )

    # Create a plan with initial metrics
    strategy.create_plan(
    niche="e-commerce",
    target_audience="Small business owners",
    budget=10000,
    timeline="3 months",
    )

    # Add performance data
    performance_data = {
    "social_media": {
    "spend": 3000,
    "impressions": 50000,
    "clicks": 2500,
    "conversions": 75,
    "revenue": 7500,
    },
    "email_marketing": {
    "spend": 1000,
    "sends": 10000,
    "opens": 3000,
    "clicks": 600,
    "conversions": 30,
    "revenue": 3000,
    },
    }

    # Calculate ROI and metrics
    metrics = strategy.calculate_channel_metrics(performance_data)

    # Check metric calculations
    social_metrics = metrics["social_media"]
    assert "roi" in social_metrics
    assert "cpa" in social_metrics  # Cost per acquisition
    assert "cpc" in social_metrics  # Cost per click
    assert "conversion_rate" in social_metrics

    # Verify ROI calculations
    assert social_metrics["roi"] == (7500 - 3000) / 3000  # (revenue - cost) / cost
    assert social_metrics["cpa"] == 3000 / 75  # cost / conversions
    assert social_metrics["conversion_rate"] == 75 / 2500  # conversions / clicks

    # Compare channel performance
    assert "channel_rankings" in metrics
    rankings = metrics["channel_rankings"]
    assert rankings[0]["channel"] in ["social_media", "email_marketing"]
    assert "roi" in rankings[0]
    assert "efficiency_score" in rankings[0]
