"""
"""
Tests for target user analysis functionality.
Tests for target user analysis functionality.
"""
"""




import pytest
import pytest


from niche_analysis.errors import InsufficientDataError, InvalidUserDataError
from niche_analysis.errors import InsufficientDataError, InvalidUserDataError


(
(
UserNeedsPrioritizer,
UserNeedsPrioritizer,
UserSegmentationAnalyzer,
UserSegmentationAnalyzer,
WillingnessToPay,
WillingnessToPay,
)
)




class TestTargetUserAnalysis:
    class TestTargetUserAnalysis:
    """Test cases for target user analysis."""

    def setup_method(self):
    """Set up test fixtures."""
    self.segmentation_analyzer = UserSegmentationAnalyzer()
    self.needs_prioritizer = UserNeedsPrioritizer()
    self.wtp_analyzer = WillingnessToPay()

    def test_user_segmentation(self):
    """Test user segmentation analysis."""
    # Test data
    user_data = [
    {
    "role": "developer",
    "company_size": "startup",
    "tech_stack": ["python", "javascript"],
    "pain_points": ["code quality", "testing"],
    "budget": "medium",
    },
    {
    "role": "team_lead",
    "company_size": "enterprise",
    "tech_stack": ["java", "python"],
    "pain_points": ["productivity", "collaboration"],
    "budget": "high",
    },
    ]

    # Perform segmentation
    segments = self.segmentation_analyzer.segment_users(user_data)

    # Validate segmentation
    assert "segments" in segments
    assert "segment_sizes" in segments
    assert "segment_characteristics" in segments
    assert isinstance(segments["segments"], list)
    assert isinstance(segments["segment_sizes"], dict)
    assert isinstance(segments["segment_characteristics"], dict)

    # Validate segment details
    for segment in segments["segments"]:
    assert "name" in segment
    assert "description" in segment
    assert "size_percentage" in segment
    assert "key_characteristics" in segment
    assert 0 <= segment["size_percentage"] <= 100

    def test_user_needs_prioritization(self):
    """Test user needs prioritization."""
    # Test data
    needs_data = [
    {
    "need": "code quality",
    "frequency": 0.8,
    "impact": 0.9,
    "current_solutions": 0.5,
    },
    {
    "need": "testing automation",
    "frequency": 0.7,
    "impact": 0.8,
    "current_solutions": 0.4,
    },
    ]

    # Prioritize needs
    prioritized_needs = self.needs_prioritizer.prioritize_needs(needs_data)

    # Validate prioritization
    assert "prioritized_list" in prioritized_needs
    assert "priority_scores" in prioritized_needs
    assert "opportunity_index" in prioritized_needs
    assert isinstance(prioritized_needs["prioritized_list"], list)
    assert isinstance(prioritized_needs["priority_scores"], dict)
    assert all(
    0 <= score <= 1 for score in prioritized_needs["priority_scores"].values()
    )

    # Validate need categorization
    categories = self.needs_prioritizer.categorize_needs(needs_data)
    assert "must_have" in categories
    assert "nice_to_have" in categories
    assert "future_considerations" in categories
    assert isinstance(categories["must_have"], list)

    def test_willingness_to_pay_estimation(self):
    """Test willingness to pay analysis."""
    # Test data
    pricing_data = {
    "segment": "enterprise_developers",
    "survey_responses": [
    {"price_point": 50, "would_pay": True},
    {"price_point": 100, "would_pay": True},
    {"price_point": 200, "would_pay": False},
    ],
    "market_data": {
    "competitor_prices": [49.99, 99.99, 149.99],
    "typical_budget": "medium",
    },
    }

    # Estimate willingness to pay
    wtp_analysis = self.wtp_analyzer.estimate_willingness_to_pay(pricing_data)

    # Validate WTP analysis
    assert "optimal_price_point" in wtp_analysis
    assert "price_sensitivity" in wtp_analysis
    assert "revenue_optimization" in wtp_analysis
    assert isinstance(wtp_analysis["optimal_price_point"], (int, float))
    assert 0 <= wtp_analysis["price_sensitivity"] <= 1
    assert "projected_revenue" in wtp_analysis["revenue_optimization"]

    def test_user_persona_creation(self):
    """Test user persona creation."""
    # Test data
    user_research = {
    "interviews": [
    {
    "role": "senior_developer",
    "goals": ["improve_productivity", "reduce_errors"],
    "challenges": ["complex_codebase", "tight_deadlines"],
    "preferences": ["automated_tools", "integrated_workflow"],
    }
    ],
    "survey_data": {
    "common_pain_points": ["code_quality", "testing"],
    "tool_preferences": ["vs_code", "git"],
    "collaboration_needs": ["high"],
    },
    }

    # Create personas
    personas = self.segmentation_analyzer.create_user_personas(user_research)

    # Validate personas
    assert isinstance(personas, list)
    for persona in personas:
    assert "name" in persona
    assert "role" in persona
    assert "goals" in persona
    assert "pain_points" in persona
    assert "preferences" in persona
    assert "typical_day" in persona
    assert "decision_factors" in persona

    def test_user_journey_mapping(self):
    """Test user journey mapping."""
    # Test data
    journey_data = {
    "awareness": {
    "channels": ["search", "social_media"],
    "pain_points": ["discovery"],
    },
    "consideration": {
    "evaluation_criteria": ["features", "price"],
    "information_needs": ["documentation", "reviews"],
    },
    "decision": {
    "key_factors": ["trial_experience", "support"],
    "obstacles": ["budget_approval"],
    },
    }

    # Map user journey
    journey_map = self.segmentation_analyzer.map_user_journey(journey_data)

    # Validate journey map
    assert "stages" in journey_map
    assert "touchpoints" in journey_map
    assert "pain_points" in journey_map
    assert "opportunities" in journey_map
    for stage in journey_map["stages"]:
    assert "name" in stage
    assert "description" in stage
    assert "user_needs" in stage
    assert "improvement_opportunities" in stage

    def test_segment_value_analysis(self):
    """Test segment value analysis."""
    # Test data
    segment_data = {
    "enterprise": {
    "size": 1000,
    "average_deal_size": 5000,
    "acquisition_cost": 1000,
    "churn_rate": 0.1,
    },
    "startup": {
    "size": 5000,
    "average_deal_size": 1000,
    "acquisition_cost": 200,
    "churn_rate": 0.2,
    },
    }

    # Analyze segment value
    value_analysis = self.segmentation_analyzer.analyze_segment_value(segment_data)

    # Validate value analysis
    assert "segment_ltv" in value_analysis
    assert "segment_roi" in value_analysis
    assert "segment_priority" in value_analysis
    for segment in value_analysis["segment_ltv"]:
    assert isinstance(value_analysis["segment_ltv"][segment], (int, float))
    assert isinstance(value_analysis["segment_roi"][segment], float)
    assert 0 <= value_analysis["segment_priority"][segment] <= 1

    def test_invalid_data_handling(self):
    """Test handling of invalid user data."""
    # Test with insufficient user data
    with pytest.raises(InsufficientDataError):
    self.segmentation_analyzer.segment_users([])

    # Test with missing required fields
    with pytest.raises(InvalidUserDataError):
    self.segmentation_analyzer.segment_users([{"role": "developer"}])

    # Test with invalid survey responses
    with pytest.raises(ValueError):
    self.wtp_analyzer.estimate_willingness_to_pay(
    {"survey_responses": [{"price_point": -50}]}  # Invalid negative price
    )

    def test_cross_segment_analysis(self):
    """Test cross-segment analysis."""
    # Test data
    segments = {
    "enterprise": {
    "needs": ["security", "scalability"],
    "preferences": ["enterprise_support", "compliance"],
    },
    "startup": {
    "needs": ["cost_efficiency", "quick_setup"],
    "preferences": ["self_service", "flexibility"],
    },
    }

    # Analyze cross-segment patterns
    patterns = self.segmentation_analyzer.analyze_cross_segment_patterns(segments)

    # Validate cross-segment analysis
    assert "common_needs" in patterns
    assert "unique_needs" in patterns
    assert "segment_overlaps" in patterns
    assert isinstance(patterns["common_needs"], list)
    assert isinstance(patterns["unique_needs"], dict)
    assert isinstance(patterns["segment_overlaps"], float)
    assert 0 <= patterns["segment_overlaps"] <= 1


    if __name__ == "__main__":
    pytest.main(["-v", "test_target_user_analysis.py"])