"""
Tests for the A/B testing module.
"""

import pytest
from datetime import datetime
import numpy as np

from marketing.ab_testing import ABTesting, ABTest
from marketing.ab_testing import TestAlreadyEndedError, InvalidVariantError, InsufficientDataError
from marketing.errors import InvalidTestConfigurationError, TestNotFoundError


class TestABTest:
    """Tests for the ABTest class."""
    
    def test_init(self):
        """Test the constructor."""
        # Test with minimal parameters
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        assert test.id == "test123"
        assert test.name == "Test A/B Test"
        assert test.description == "A test A/B test"
        assert test.content_type == "email"
        assert test.test_type == "a_b"
        assert len(test.variants) == 2
        assert test.status == "active"
        assert test.ended_at is None
        assert test.winning_variant_id is None
        
        # Verify variants have required fields
        for variant in test.variants:
            assert "id" in variant
            assert "name" in variant
            assert "is_control" in variant
            assert "metrics" in variant
            assert "impressions" in variant["metrics"]
            assert "clicks" in variant["metrics"]
            assert "conversions" in variant["metrics"]
            assert "click_through_rate" in variant["metrics"]
            assert "conversion_rate" in variant["metrics"]
        
        # Test with no control variant (should set first variant as control)
        variants = [
            {"name": "Variant A"},
            {"name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        assert test.variants[0]["is_control"]
        assert not test.variants[1].get("is_control", False)
        
        # Test with no variants (should raise InvalidTestConfigurationError)
        with pytest.raises(InvalidTestConfigurationError):
            ABTest(
                id="test123",
                name="Test A/B Test",
                description="A test A/B test",
                content_type="email",
                test_type="a_b",
                variants=[]
            )
    
    def test_to_dict(self):
        """Test the to_dict method."""
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_dict = test.to_dict()
        
        assert test_dict["id"] == "test123"
        assert test_dict["name"] == "Test A/B Test"
        assert test_dict["description"] == "A test A/B test"
        assert test_dict["content_type"] == "email"
        assert test_dict["test_type"] == "a_b"
        assert len(test_dict["variants"]) == 2
        assert test_dict["status"] == "active"
        assert test_dict["ended_at"] is None
        assert test_dict["winning_variant_id"] is None
        assert isinstance(test_dict["created_at"], str)
        assert isinstance(test_dict["updated_at"], str)
    
    def test_record_interaction(self):
        """Test the record_interaction method."""
        variants = [
            {"id": "control", "name": "Control", "is_control": True},
            {"id": "variant", "name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        # Record an impression
        interaction = test.record_interaction("control", "impression", "user1")
        
        assert interaction["test_id"] == "test123"
        assert interaction["variant_id"] == "control"
        assert interaction["interaction_type"] == "impression"
        assert interaction["user_id"] == "user1"
        
        # Check that the variant metrics were updated
        assert test.variants[0]["metrics"]["impressions"] == 1
        assert test.variants[0]["metrics"]["clicks"] == 0
        assert test.variants[0]["metrics"]["conversions"] == 0
        assert test.variants[0]["metrics"]["click_through_rate"] == 0.0
        assert test.variants[0]["metrics"]["conversion_rate"] == 0.0
        
        # Record a click
        test.record_interaction("control", "click", "user1")
        
        # Check that the variant metrics were updated
        assert test.variants[0]["metrics"]["impressions"] == 1
        assert test.variants[0]["metrics"]["clicks"] == 1
        assert test.variants[0]["metrics"]["conversions"] == 0
        assert test.variants[0]["metrics"]["click_through_rate"] == 1.0
        assert test.variants[0]["metrics"]["conversion_rate"] == 0.0
        
        # Record a conversion
        test.record_interaction("control", "conversion", "user1")
        
        # Check that the variant metrics were updated
        assert test.variants[0]["metrics"]["impressions"] == 1
        assert test.variants[0]["metrics"]["clicks"] == 1
        assert test.variants[0]["metrics"]["conversions"] == 1
        assert test.variants[0]["metrics"]["click_through_rate"] == 1.0
        assert test.variants[0]["metrics"]["conversion_rate"] == 1.0
        
        # Test with invalid variant ID
        with pytest.raises(InvalidVariantError):
            test.record_interaction("nonexistent", "impression", "user1")
        
        # Test with ended test
        test.status = "completed"
        test.ended_at = datetime.now()
        
        with pytest.raises(TestAlreadyEndedError):
            test.record_interaction("control", "impression", "user1")
    
    def test_get_results(self):
        """Test the get_results method."""
        variants = [
            {"id": "control", "name": "Control", "is_control": True},
            {"id": "variant", "name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        # Add some interactions
        for _ in range(100):
            test.record_interaction("control", "impression")
        for _ in range(10):
            test.record_interaction("control", "click")
        for _ in range(2):
            test.record_interaction("control", "conversion")
            
        for _ in range(100):
            test.record_interaction("variant", "impression")
        for _ in range(20):
            test.record_interaction("variant", "click")
        for _ in range(6):
            test.record_interaction("variant", "conversion")
        
        results = test.get_results()
        
        assert results["test_id"] == "test123"
        assert results["name"] == "Test A/B Test"
        assert results["status"] == "active"
        assert results["total_impressions"] == 200
        assert results["total_clicks"] == 30
        assert results["total_conversions"] == 8
        assert results["overall_click_through_rate"] == 0.15  # 30/200
        assert results["overall_conversion_rate"] == 8/30
        
        # Check variant results
        assert len(results["variants"]) == 2
        
        control_result = next(v for v in results["variants"] if v["id"] == "control")
        variant_result = next(v for v in results["variants"] if v["id"] == "variant")
        
        assert control_result["metrics"]["impressions"] == 100
        assert control_result["metrics"]["clicks"] == 10
        assert control_result["metrics"]["conversions"] == 2
        assert control_result["metrics"]["click_through_rate"] == 0.1  # 10/100
        assert control_result["metrics"]["conversion_rate"] == 0.2  # 2/10
        
        assert variant_result["metrics"]["impressions"] == 100
        assert variant_result["metrics"]["clicks"] == 20
        assert variant_result["metrics"]["conversions"] == 6
        assert variant_result["metrics"]["click_through_rate"] == 0.2  # 20/100
        assert variant_result["metrics"]["conversion_rate"] == 0.3  # 6/20
        
        # Check lifts
        assert "ctr_lift" in variant_result
        assert "conversion_lift" in variant_result
        assert variant_result["ctr_lift"] == 100.0  # (0.2/0.1 - 1) * 100
        assert variant_result["conversion_lift"] == 50.0  # (0.3/0.2 - 1) * 100
    
    def test_analyze_test(self):
        """Test the analyze_test method."""
        variants = [
            {"id": "control", "name": "Control", "is_control": True},
            {"id": "variant", "name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        # Not enough data
        with pytest.raises(InsufficientDataError):
            test.analyze_test()
        
        # Add enough data for analysis
        for _ in range(1000):
            test.record_interaction("control", "impression")
        for _ in range(100):
            test.record_interaction("control", "click")
        for _ in range(10):
            test.record_interaction("control", "conversion")
            
        for _ in range(1000):
            test.record_interaction("variant", "impression")
        for _ in range(200):
            test.record_interaction("variant", "click")
        for _ in range(30):
            test.record_interaction("variant", "conversion")
        
        analysis = test.analyze_test()
        
        assert analysis["test_id"] == "test123"
        assert analysis["name"] == "Test A/B Test"
        assert analysis["confidence_level"] == 0.95
        assert analysis["has_significant_results"] is True
        assert analysis["recommended_winner"] == "variant"
        
        # Check variant analyses
        assert len(analysis["variants"]) == 2
        
        control_analysis = next(v for v in analysis["variants"] if v["id"] == "control")
        variant_analysis = next(v for v in analysis["variants"] if v["id"] == "variant")
        
        assert control_analysis["is_control"] is True
        assert variant_analysis["is_control"] is False
        
        # Verify p-values and significance
        assert "ctr_p_value" in variant_analysis
        assert "ctr_is_significant" in variant_analysis
        assert "conversion_p_value" in variant_analysis
        assert "conversion_is_significant" in variant_analysis
        assert "is_better_than_control" in variant_analysis
        
        # With these numbers, both CTR and conversion rate should be significantly better
        assert variant_analysis.get("ctr_is_significant") == True  # Use == instead of is
        assert variant_analysis.get("conversion_is_significant") == True  # Use == instead of is
    
    def test_end_test(self):
        """Test the end_test method."""
        variants = [
            {"id": "control", "name": "Control", "is_control": True},
            {"id": "variant", "name": "Variant B"}
        ]
        
        test = ABTest(
            id="test123",
            name="Test A/B Test",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        # Add some interactions
        for _ in range(1000):
            test.record_interaction("control", "impression")
        for _ in range(100):
            test.record_interaction("control", "click")
            
        for _ in range(1000):
            test.record_interaction("variant", "impression")
        for _ in range(200):
            test.record_interaction("variant", "click")
        
        # End the test with explicit winner
        result = test.end_test("variant")
        
        assert result["test_id"] == "test123"
        assert result["name"] == "Test A/B Test"
        assert result["status"] == "completed"
        assert result["winning_variant_id"] == "variant"
        assert result["ended_at"] is not None
        assert "results" in result
        
        # Check that the test state was updated
        assert test.status == "completed"
        assert test.ended_at is not None
        assert test.winning_variant_id == "variant"
        
        # Test attempting to end an already ended test
        with pytest.raises(TestAlreadyEndedError):
            test.end_test()
        
        # Create a new test to test automatic winner selection
        test2 = ABTest(
            id="test456",
            name="Test A/B Test 2",
            description="A test A/B test",
            content_type="email",
            test_type="a_b",
            variants=variants.copy()
        )
        
        # Add interactions with variant B clearly better
        for _ in range(1000):
            test2.record_interaction("control", "impression")
        for _ in range(100):
            test2.record_interaction("control", "click")
            
        for _ in range(1000):
            test2.record_interaction("variant", "impression")
        for _ in range(200):
            test2.record_interaction("variant", "click")
        
        # End the test without specifying a winner
        result = test2.end_test()
        
        # It should automatically select variant as the winner
        assert result["winning_variant_id"] == "variant"


class TestABTesting:
    """Tests for the ABTesting class."""
    
    def test_create_test(self):
        """Test the create_test method."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        # Create a valid test
        test = ab_testing.create_test(
            name="Email Subject Line Test",
            description="Testing email subject lines",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        assert test["name"] == "Email Subject Line Test"
        assert test["description"] == "Testing email subject lines"
        assert test["content_type"] == "email"
        assert test["test_type"] == "a_b"
        assert len(test["variants"]) == 2
        assert test["status"] == "active"
        
        # Test with invalid test type
        with pytest.raises(InvalidTestConfigurationError):
            ab_testing.create_test(
                name="Invalid Test",
                description="Testing with invalid type",
                content_type="email",
                test_type="invalid",
                variants=variants
            )
        
        # Test with too few variants
        with pytest.raises(InvalidTestConfigurationError):
            ab_testing.create_test(
                name="Invalid Test",
                description="Testing with too few variants",
                content_type="email",
                test_type="a_b",
                variants=[{"name": "Control"}]
            )
    
    def test_get_variants(self):
        """Test the get_variants method."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Email Subject Line Test",
            description="Testing email subject lines",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        
        # Get variants for a valid test
        result_variants = ab_testing.get_variants(test_id)
        
        assert len(result_variants) == 2
        assert result_variants[0]["name"] == "Control"
        assert result_variants[1]["name"] == "Variant B"
        
        # Test with invalid test ID
        with pytest.raises(TestNotFoundError):
            ab_testing.get_variants("nonexistent")
    
    def test_record_interaction(self):
        """Test the record_interaction method."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Email Subject Line Test",
            description="Testing email subject lines",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        variant_id = test["variants"][0]["id"]
        
        # Record a valid interaction
        interaction = ab_testing.record_interaction(
            test_id=test_id,
            variant_id=variant_id,
            interaction_type="impression",
            user_id="user1"
        )
        
        assert interaction["test_id"] == test_id
        assert interaction["variant_id"] == variant_id
        assert interaction["interaction_type"] == "impression"
        assert interaction["user_id"] == "user1"
        
        # Test with invalid test ID
        with pytest.raises(TestNotFoundError):
            ab_testing.record_interaction(
                test_id="nonexistent",
                variant_id=variant_id,
                interaction_type="impression"
            )
        
        # Test with invalid variant ID
        with pytest.raises(InvalidVariantError):
            ab_testing.record_interaction(
                test_id=test_id,
                variant_id="nonexistent",
                interaction_type="impression"
            )
    
    def test_get_results(self):
        """Test the get_results method."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Email Subject Line Test",
            description="Testing email subject lines",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Add some interactions
        for _ in range(100):
            ab_testing.record_interaction(test_id, control_id, "impression")
        for _ in range(10):
            ab_testing.record_interaction(test_id, control_id, "click")
            
        for _ in range(100):
            ab_testing.record_interaction(test_id, variant_id, "impression")
        for _ in range(20):
            ab_testing.record_interaction(test_id, variant_id, "click")
        
        results = ab_testing.get_results(test_id)
        
        assert results["test_id"] == test_id
        assert results["total_impressions"] == 200
        assert results["total_clicks"] == 30
        assert len(results["variants"]) == 2
        
        # Test with invalid test ID
        with pytest.raises(TestNotFoundError):
            ab_testing.get_results("nonexistent")
    
    def test_analyze_test(self):
        """Test the analyze_test method."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Email Subject Line Test",
            description="Testing email subject lines",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Add enough data for analysis
        for _ in range(1000):
            ab_testing.record_interaction(test_id, control_id, "impression")
        for _ in range(100):
            ab_testing.record_interaction(test_id, control_id, "click")
            
        for _ in range(1000):
            ab_testing.record_interaction(test_id, variant_id, "impression")
        for _ in range(200):
            ab_testing.record_interaction(test_id, variant_id, "click")
        
        analysis = ab_testing.analyze_test(test_id)
        
        assert analysis["test_id"] == test_id
        assert analysis["has_significant_results"] is True
        assert len(analysis["variants"]) == 2
        
        # Test with invalid test ID
        with pytest.raises(TestNotFoundError):
            ab_testing.analyze_test("nonexistent")
    
    def test_end_test(self):
        """Test the end_test method."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Email Subject Line Test",
            description="Testing email subject lines",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        variant_id = test["variants"][1]["id"]
        
        # End the test
        result = ab_testing.end_test(test_id, variant_id)
        
        assert result["test_id"] == test_id
        assert result["status"] == "completed"
        assert result["winning_variant_id"] == variant_id
        assert result["ended_at"] is not None
        
        # Test with invalid test ID
        with pytest.raises(TestNotFoundError):
            ab_testing.end_test("nonexistent")
        
        # Test ending an already ended test
        with pytest.raises(TestAlreadyEndedError):
            ab_testing.end_test(test_id)


class TestUserJourneyTracking:
    """Tests for user journey tracking in A/B tests."""

    def test_user_multiple_interactions(self):
        """Test tracking multiple interactions from same user across variants."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        # Create test
        test = ab_testing.create_test(
            name="User Journey Test",
            description="Testing user journey tracking",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        user_id = "test_user_1"
        
        # Simulate user journey
        # First sees control variant
        interaction1 = ab_testing.record_interaction(
            test_id=test_id,
            variant_id=control_id,
            interaction_type="impression",
            user_id=user_id,
            metadata={"source": "email"}
        )
        
        # Then clicks control variant
        interaction2 = ab_testing.record_interaction(
            test_id=test_id,
            variant_id=control_id,
            interaction_type="click",
            user_id=user_id,
            metadata={"source": "email", "timestamp": datetime.now().isoformat()}
        )
        
        # Later sees variant B
        interaction3 = ab_testing.record_interaction(
            test_id=test_id,
            variant_id=variant_id,
            interaction_type="impression",
            user_id=user_id,
            metadata={"source": "email", "campaign": "followup"}
        )
        
        # Verify interactions were recorded with correct user attribution
        assert interaction1["user_id"] == user_id
        assert interaction2["user_id"] == user_id
        assert interaction3["user_id"] == user_id
        
        # Verify metadata was preserved
        assert interaction1["metadata"]["source"] == "email"
        assert interaction2["metadata"]["source"] == "email"
        assert interaction3["metadata"]["source"] == "email"
        assert interaction3["metadata"]["campaign"] == "followup"
        
        # Verify test results show correct attribution
        results = ab_testing.get_results(test_id)
        control_result = next(v for v in results["variants"] if v["id"] == control_id)
        variant_result = next(v for v in results["variants"] if v["id"] == variant_id)
        
        assert control_result["metrics"]["impressions"] == 1
        assert control_result["metrics"]["clicks"] == 1
        assert variant_result["metrics"]["impressions"] == 1
        assert variant_result["metrics"]["clicks"] == 0

    def test_user_session_management(self):
        """Test user session management and attribution across variants."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Session Management Test",
            description="Testing session management",
            content_type="landing_page",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Simulate multiple users with different session patterns
        users = ["user1", "user2"]
        session_ids = ["session1", "session2"]
        
        # User 1 interactions in first session
        ab_testing.record_interaction(
            test_id=test_id,
            variant_id=control_id,
            interaction_type="impression",
            user_id=users[0],
            metadata={"session_id": session_ids[0]}
        )
        
        ab_testing.record_interaction(
            test_id=test_id,
            variant_id=control_id,
            interaction_type="click",
            user_id=users[0],
            metadata={"session_id": session_ids[0]}
        )
        
        # User 1 interactions in second session
        ab_testing.record_interaction(
            test_id=test_id,
            variant_id=variant_id,
            interaction_type="impression",
            user_id=users[0],
            metadata={"session_id": session_ids[1]}
        )
        
        # User 2 interactions in first session
        ab_testing.record_interaction(
            test_id=test_id,
            variant_id=variant_id,
            interaction_type="impression",
            user_id=users[1],
            metadata={"session_id": session_ids[0]}
        )
        
        ab_testing.record_interaction(
            test_id=test_id,
            variant_id=variant_id,
            interaction_type="click",
            user_id=users[1],
            metadata={"session_id": session_ids[0]}
        )
        
        ab_testing.record_interaction(
            test_id=test_id,
            variant_id=variant_id,
            interaction_type="conversion",
            user_id=users[1],
            metadata={"session_id": session_ids[0]}
        )
        
        # Get test results
        results = ab_testing.get_results(test_id)
        
        # Verify metrics reflect all sessions
        assert results["total_impressions"] == 3  # Two for user1, one for user2
        assert results["total_clicks"] == 2  # One from each user
        assert results["total_conversions"] == 1  # One from user2
        
        # Verify control variant metrics
        control_result = next(v for v in results["variants"] if v["id"] == control_id)
        assert control_result["metrics"]["impressions"] == 1
        assert control_result["metrics"]["clicks"] == 1
        assert control_result["metrics"]["conversions"] == 0
        
        # Verify variant B metrics
        variant_result = next(v for v in results["variants"] if v["id"] == variant_id)
        assert variant_result["metrics"]["impressions"] == 2
        assert variant_result["metrics"]["clicks"] == 1
        assert variant_result["metrics"]["conversions"] == 1

    def test_user_segmentation(self):
        """Test user segmentation in A/B test analysis."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="User Segmentation Test",
            description="Testing user segmentation",
            content_type="landing_page",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Simulate different user segments
        mobile_users = ["mobile_user1", "mobile_user2"]
        desktop_users = ["desktop_user1", "desktop_user2"]
        
        # Mobile users interactions
        for user_id in mobile_users:
            ab_testing.record_interaction(
                test_id=test_id,
                variant_id=control_id,
                interaction_type="impression",
                user_id=user_id,
                metadata={"device": "mobile", "browser": "safari"}
            )
            
            if user_id == "mobile_user1":
                ab_testing.record_interaction(
                    test_id=test_id,
                    variant_id=control_id,
                    interaction_type="click",
                    user_id=user_id,
                    metadata={"device": "mobile", "browser": "safari"}
                )
        
        # Desktop users interactions
        for user_id in desktop_users:
            ab_testing.record_interaction(
                test_id=test_id,
                variant_id=variant_id,
                interaction_type="impression",
                user_id=user_id,
                metadata={"device": "desktop", "browser": "chrome"}
            )
            
            # Both desktop users click and convert
            ab_testing.record_interaction(
                test_id=test_id,
                variant_id=variant_id,
                interaction_type="click",
                user_id=user_id,
                metadata={"device": "desktop", "browser": "chrome"}
            )
            
            ab_testing.record_interaction(
                test_id=test_id,
                variant_id=variant_id,
                interaction_type="conversion",
                user_id=user_id,
                metadata={"device": "desktop", "browser": "chrome"}
            )
        
        # Get test results
        results = ab_testing.get_results(test_id)
        
        # Verify total metrics
        assert results["total_impressions"] == 4  # 2 mobile + 2 desktop
        assert results["total_clicks"] == 3  # 1 mobile + 2 desktop
        assert results["total_conversions"] == 2  # 2 desktop
        
        # Verify control variant (mobile) metrics
        control_result = next(v for v in results["variants"] if v["id"] == control_id)
        assert control_result["metrics"]["impressions"] == 2
        assert control_result["metrics"]["clicks"] == 1
        assert control_result["metrics"]["conversions"] == 0
        assert control_result["metrics"]["click_through_rate"] == 0.5  # 1/2
        
        # Verify variant B (desktop) metrics
        variant_result = next(v for v in results["variants"] if v["id"] == variant_id)
        assert variant_result["metrics"]["impressions"] == 2
        assert variant_result["metrics"]["clicks"] == 2
        assert variant_result["metrics"]["conversions"] == 2
        assert variant_result["metrics"]["click_through_rate"] == 1.0  # 2/2
        assert variant_result["metrics"]["conversion_rate"] == 1.0  # 2/2
        
        # Analyze test results
        analysis = ab_testing.analyze_test(test_id)
        
        # Variant B (desktop) should show better performance
        variant_analysis = next(v for v in analysis["variants"] if not v["is_control"])
        assert variant_analysis["is_better_than_control"] is True


class TestStatisticalEdgeCases:
    """Tests for statistical edge cases in A/B testing."""

    def test_uneven_sample_sizes(self):
        """Test handling of extremely uneven sample sizes between variants."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Uneven Sample Test",
            description="Testing extremely uneven sample sizes",
            content_type="email",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Create highly uneven sample sizes (10:1 ratio)
        # Control: 1000 impressions, 100 clicks (10% CTR)
        for _ in range(1000):
            ab_testing.record_interaction(test_id, control_id, "impression")
        for _ in range(100):
            ab_testing.record_interaction(test_id, control_id, "click")
        
        # Variant B: 100 impressions, 15 clicks (15% CTR)
        for _ in range(100):
            ab_testing.record_interaction(test_id, variant_id, "impression")
        for _ in range(15):
            ab_testing.record_interaction(test_id, variant_id, "click")
        
        # Analyze results
        analysis = ab_testing.analyze_test(test_id)
        
        # Even with better performance, variant B shouldn't be significant due to small sample
        variant_analysis = next(v for v in analysis["variants"] if not v["is_control"])
        assert not variant_analysis["ctr_is_significant"]
        
        # Add more interactions to variant B to reach significance threshold
        for _ in range(900):
            ab_testing.record_interaction(test_id, variant_id, "impression")
        for _ in range(135):  # Maintaining 15% CTR
            ab_testing.record_interaction(test_id, variant_id, "click")
        
        # Re-analyze with balanced samples
        analysis = ab_testing.analyze_test(test_id)
        variant_analysis = next(v for v in analysis["variants"] if not v["is_control"])
        assert variant_analysis["ctr_is_significant"]

    def test_small_effect_sizes(self):
        """Test behavior with very small effect sizes."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Small Effect Size Test",
            description="Testing very small effect sizes",
            content_type="landing_page",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Control: 10,000 impressions, 1000 clicks (10% CTR)
        for _ in range(10000):
            ab_testing.record_interaction(test_id, control_id, "impression")
        for _ in range(1000):
            ab_testing.record_interaction(test_id, control_id, "click")
        
        # Variant B: 10,000 impressions, 1020 clicks (10.2% CTR - only 0.2% improvement)
        for _ in range(10000):
            ab_testing.record_interaction(test_id, variant_id, "impression")
        for _ in range(1020):
            ab_testing.record_interaction(test_id, variant_id, "click")
        
        # Analyze results
        analysis = ab_testing.analyze_test(test_id)
        
        # Very small improvement shouldn't be significant despite large sample
        variant_analysis = next(v for v in analysis["variants"] if not v["is_control"])
        assert not variant_analysis["ctr_is_significant"]
        
        # Add more clicks to create a larger effect size
        for _ in range(80):  # Bringing total to 1100 clicks (11% CTR)
            ab_testing.record_interaction(test_id, variant_id, "click")
        
        # Re-analyze with larger effect size
        analysis = ab_testing.analyze_test(test_id)
        variant_analysis = next(v for v in analysis["variants"] if not v["is_control"])
        assert variant_analysis["ctr_is_significant"]

    def test_extreme_values(self):
        """Test confidence interval calculations with extreme values."""
        ab_testing = ABTesting()
        
        variants = [
            {"name": "Control", "is_control": True},
            {"name": "Variant B"}
        ]
        
        test = ab_testing.create_test(
            name="Extreme Values Test",
            description="Testing extreme conversion rates",
            content_type="landing_page",
            test_type="a_b",
            variants=variants
        )
        
        test_id = test["id"]
        control_id = test["variants"][0]["id"]
        variant_id = test["variants"][1]["id"]
        
        # Control: Very low conversion rate (0.1%)
        for _ in range(10000):
            ab_testing.record_interaction(test_id, control_id, "impression")
        for _ in range(1000):
            ab_testing.record_interaction(test_id, control_id, "click")
        for _ in range(1):  # Just 1 conversion
            ab_testing.record_interaction(test_id, control_id, "conversion")
        
        # Variant B: Very high conversion rate (99.9%)
        for _ in range(10000):
            ab_testing.record_interaction(test_id, variant_id, "impression")
        for _ in range(1000):
            ab_testing.record_interaction(test_id, variant_id, "click")
        for _ in range(999):  # Almost all convert
            ab_testing.record_interaction(test_id, variant_id, "conversion")
        
        # Analyze results
        analysis = ab_testing.analyze_test(test_id)
        
        # Should detect significance with extreme difference
        variant_analysis = next(v for v in analysis["variants"] if not v["is_control"])
        assert variant_analysis["conversion_is_significant"]
        assert variant_analysis["is_better_than_control"]
        
        # Verify metrics are calculated correctly for extreme values
        results = ab_testing.get_results(test_id)
        control_result = next(v for v in results["variants"] if v["id"] == control_id)
        variant_result = next(v for v in results["variants"] if v["id"] == variant_id)
        
        # Control conversion rate should be 0.1%
        assert abs(control_result["metrics"]["conversion_rate"] - 0.001) < 0.0001
        
        # Variant conversion rate should be 99.9%
        assert abs(variant_result["metrics"]["conversion_rate"] - 0.999) < 0.0001