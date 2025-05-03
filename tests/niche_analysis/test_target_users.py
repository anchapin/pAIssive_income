"""Tests for target user analysis functionality."""


import pytest

from niche_analysis.market_analyzer import MarketAnalyzer




@pytest.fixture
def market_analyzer():
    """Create a MarketAnalyzer instance for testing."""
            return MarketAnalyzer()


class TestTargetUserAnalysis:
    """Tests for target user analysis."""

    def test_user_segment_generation(self, market_analyzer):
        """Test generation of user segments."""
        result = market_analyzer.analyze_target_users("content creation")

        # Verify basic structure
        assert "id" in result
        assert "niche" in result
        assert "user_segments" in result
        assert len(result["user_segments"]) > 0

        # Test first segment structure
        segment = result["user_segments"][0]
        assert "name" in segment
        assert "description" in segment
        assert "size" in segment
        assert "priority" in segment

        # Verify size classifications are valid
        assert segment["size"] in ["large", "medium", "small"]

        # Verify priority levels are valid
        assert segment["priority"] in ["high", "medium", "low"]

        # First segment should be highest priority
        assert segment["priority"] == "high"

    def test_demographic_profiling(self, market_analyzer):
        """Test demographic profile analysis."""
        result = market_analyzer.analyze_target_users("content creation")

        # Verify demographics exist
        assert "demographics" in result
        demographics = result["demographics"]

        # Test demographic fields
        assert "age_range" in demographics
        assert "gender" in demographics
        assert "location" in demographics
        assert "education" in demographics
        assert "income" in demographics

        # Verify demographic values
        assert isinstance(demographics["age_range"], str)
        assert demographics["gender"] in ["male", "female", "mixed"]
        assert isinstance(demographics["location"], str)
        assert isinstance(demographics["education"], str)
        assert isinstance(demographics["income"], str)

    def test_psychographic_profiling(self, market_analyzer):
        """Test psychographic profile analysis."""
        result = market_analyzer.analyze_target_users("content creation")

        # Verify psychographics exist
        assert "psychographics" in result
        psychographics = result["psychographics"]

        # Test psychographic fields
        assert "goals" in psychographics
        assert "values" in psychographics
        assert "challenges" in psychographics

        # Verify arrays have content
        assert len(psychographics["goals"]) > 0
        assert len(psychographics["values"]) > 0
        assert len(psychographics["challenges"]) > 0

        # Verify goals include common business objectives
        assert "efficiency" in psychographics["goals"]
        assert "growth" in psychographics["goals"]
        assert "profitability" in psychographics["goals"]

    def test_need_prioritization(self, market_analyzer):
        """Test user need and pain point analysis."""
        result = market_analyzer.analyze_target_users("content creation")

        # Verify pain points exist
        assert "pain_points" in result
        assert len(result["pain_points"]) > 0

        # Verify goals exist
        assert "goals" in result
        assert len(result["goals"]) > 0

        # Pain points should be specific
        for pain_point in result["pain_points"]:
            assert len(pain_point) > 0
            assert isinstance(pain_point, str)

        # Goals should be actionable
        for goal in result["goals"]:
            assert len(goal) > 0
            assert isinstance(goal, str)

    def test_buying_behavior_analysis(self, market_analyzer):
        """Test buying behavior analysis."""
        result = market_analyzer.analyze_target_users("content creation")

        # Verify buying behavior exists
        assert "buying_behavior" in result
        behavior = result["buying_behavior"]

        # Test buying behavior fields
        assert "decision_factors" in behavior
        assert "purchase_process" in behavior
        assert "price_sensitivity" in behavior

        # Verify decision factors include key considerations
        decision_factors = behavior["decision_factors"]
        assert "price" in decision_factors
        assert "features" in decision_factors
        assert "ease of use" in decision_factors

        # Verify price sensitivity is valid
        assert behavior["price_sensitivity"] in ["high", "moderate", "low"]

    def test_target_user_cache_behavior(self, market_analyzer):
        """Test caching behavior for target user analysis."""
        # First analysis call
        first_result = market_analyzer.analyze_target_users("content creation")

        # Second call should use cache
        second_result = market_analyzer.analyze_target_users("content creation")
        assert first_result == second_result

        # Force refresh should bypass cache
        fresh_result = market_analyzer.analyze_target_users(
            "content creation", force_refresh=True
        )
        assert fresh_result != first_result  # Should have new timestamp