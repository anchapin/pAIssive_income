"""
Integration tests for the niche analysis → market trend → A/B testing workflow.

This module tests the complete workflow from niche analysis through market trend
analysis to A/B testing setup and analysis.
"""
import pytest
from unittest.mock import patch, MagicMock

from niche_analysis import MarketAnalyzer
from marketing import ABTesting
from agent_team import AgentTeam


@pytest.fixture
def market_analyzer():
    """Create a market analyzer instance for testing."""
    return MarketAnalyzer()


@pytest.fixture
def ab_testing():
    """Create an A/B testing instance for testing."""
    return ABTesting()


@pytest.fixture
def mock_agent_team():
    """Create a mock agent team for testing."""
    with patch('agent_team.AgentTeam') as mock:
        team = MagicMock()
        mock.return_value = team
        yield team


def test_niche_to_ab_testing_workflow(market_analyzer, ab_testing, mock_agent_team):
    """
    Test the complete workflow from niche analysis to A/B testing.
    
    This test verifies that:
    1. Market analysis can identify niches
    2. Market trends can be analyzed for those niches
    3. Target users can be identified
    4. A/B tests can be created based on the niche and user analysis
    5. Test results can be analyzed
    """
    # Step 1: Analyze market segment to find niches
    market_segment = "e-commerce"
    market_analysis = market_analyzer.analyze_market(market_segment)
    
    # Verify market analysis results
    assert "potential_niches" in market_analysis
    assert len(market_analysis["potential_niches"]) > 0
    
    # Select a niche for further analysis
    selected_niche = market_analysis["potential_niches"][0]
    
    # Step 2: Analyze market trends for the selected niche
    trend_analysis = market_analyzer.analyze_trends(market_segment)
    
    # Verify trend analysis results
    assert "trends" in trend_analysis
    assert len(trend_analysis["trends"]) > 0
    
    # Step 3: Analyze target users for the selected niche
    user_analysis = market_analyzer.analyze_target_users(selected_niche)
    
    # Verify user analysis results
    assert "user_segments" in user_analysis
    assert len(user_analysis["user_segments"]) > 0
    
    # Step 4: Create A/B tests based on the niche and user analysis
    # Create variants based on user segments
    variants = []
    for i, segment in enumerate(user_analysis["user_segments"]):
        is_control = (i == 0)  # First segment is control
        variant = {
            "name": f"Variant for {segment}",
            "is_control": is_control,
            "content": {
                "headline": f"Solution for {segment}",
                "description": f"Tailored for {segment} needs",
                "cta": "Try Now" if is_control else "Get Started"
            },
            "target_segment": segment
        }
        variants.append(variant)
    
    # Create the A/B test
    test = ab_testing.create_test(
        name=f"Landing Page Test for {selected_niche}",
        description=f"Testing landing page variants for {selected_niche} based on user segments",
        content_type="landing_page",
        test_type="a_b",
        variants=variants
    )
    
    # Verify test creation
    assert "id" in test
    assert "variants" in test
    assert len(test["variants"]) == len(user_analysis["user_segments"])
    
    # Step 5: Simulate interactions with the test
    # For each variant, simulate impressions and conversions
    for variant in test["variants"]:
        variant_id = variant["id"]
        # Simulate 1000 impressions
        for _ in range(1000):
            ab_testing.record_interaction(test["id"], variant_id, "impression")
        
        # Simulate different conversion rates for different variants
        # Control variant: 10% conversion
        # Other variants: 8-15% conversion depending on the variant
        conversion_rate = 0.1 if variant["is_control"] else (0.08 + (hash(variant["name"]) % 8) / 100)
        conversion_count = int(1000 * conversion_rate)
        
        for _ in range(conversion_count):
            ab_testing.record_interaction(test["id"], variant_id, "conversion")
    
    # Step 6: Analyze test results
    results = ab_testing.analyze_test(test["id"])
    
    # Verify analysis results
    assert "variants" in results
    assert "winner" in results
    assert "confidence_level" in results
    assert results["confidence_level"] > 0
    
    # Step 7: Use agent team to implement the winning variant
    winning_variant = results["winner"]
    mock_agent_team.implement_ab_test_winner(test["id"], winning_variant["id"])
    
    # Verify that the agent team method was called
    mock_agent_team.implement_ab_test_winner.assert_called_once_with(test["id"], winning_variant["id"])


def test_niche_to_ab_testing_workflow_with_multivariate(market_analyzer, ab_testing):
    """
    Test the workflow with multivariate testing.
    
    This test verifies that:
    1. Market analysis can identify niches
    2. Multivariate tests can be created based on the niche analysis
    3. Test results can be analyzed with multiple variables
    """
    # Step 1: Analyze market segment to find niches
    market_segment = "content creation"
    market_analysis = market_analyzer.analyze_market(market_segment)
    
    # Select a niche for further analysis
    selected_niche = market_analysis["potential_niches"][0]
    
    # Step 2: Analyze target users for the selected niche
    user_analysis = market_analyzer.analyze_target_users(selected_niche)
    
    # Step 3: Create multivariate test with different headlines, descriptions, and CTAs
    headlines = [
        "Create Amazing Content Faster",
        "AI-Powered Content Creation",
        "Professional Content in Minutes"
    ]
    
    descriptions = [
        "Our AI tools help you create high-quality content with minimal effort",
        "Generate blog posts, social media content, and more with our advanced AI",
        "Save time and resources with automated content creation"
    ]
    
    ctas = [
        "Start Creating",
        "Try It Free",
        "Get Started Now"
    ]
    
    # Create variants for all combinations
    variants = []
    control_set = True
    
    for headline in headlines:
        for description in descriptions:
            for cta in ctas:
                variant = {
                    "name": f"{headline[:10]}... / {description[:10]}... / {cta}",
                    "is_control": control_set,  # First combination is control
                    "content": {
                        "headline": headline,
                        "description": description,
                        "cta": cta
                    }
                }
                variants.append(variant)
                control_set = False  # Only the first one is control
    
    # Create the multivariate test
    test = ab_testing.create_test(
        name=f"Multivariate Landing Page Test for {selected_niche}",
        description=f"Testing different combinations of headlines, descriptions, and CTAs for {selected_niche}",
        content_type="landing_page",
        test_type="multivariate",
        variants=variants
    )
    
    # Verify test creation
    assert "id" in test
    assert "variants" in test
    assert len(test["variants"]) == len(headlines) * len(descriptions) * len(ctas)
    
    # Step 4: Simulate interactions with the test
    for variant in test["variants"]:
        variant_id = variant["id"]
        # Simulate 500 impressions per variant
        for _ in range(500):
            ab_testing.record_interaction(test["id"], variant_id, "impression")
        
        # Simulate conversions based on content
        # - Headlines affect conversion by up to 5%
        # - Descriptions affect conversion by up to 3%
        # - CTAs affect conversion by up to 2%
        headline_factor = 0.08 + (headlines.index(variant["content"]["headline"]) * 0.025)
        description_factor = 1.0 + (descriptions.index(variant["content"]["description"]) * 0.015)
        cta_factor = 1.0 + (ctas.index(variant["content"]["cta"]) * 0.01)
        
        conversion_rate = headline_factor * description_factor * cta_factor
        conversion_count = int(500 * conversion_rate)
        
        for _ in range(conversion_count):
            ab_testing.record_interaction(test["id"], variant_id, "conversion")
    
    # Step 5: Analyze test results
    results = ab_testing.analyze_test(test["id"])
    
    # Verify analysis results
    assert "variants" in results
    assert "winner" in results
    assert "confidence_level" in results
    assert "factor_analysis" in results  # Multivariate tests should include factor analysis
