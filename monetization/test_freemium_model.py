"""
Test script for the FreemiumModel class.
"""


import os

from subscription_models import FreemiumModel


def test_freemium_model():
    ():
    """Test the functionality of the FreemiumModel class."""
    print("Testing FreemiumModel class...")

    # Create a freemium subscription model
    model = FreemiumModel(
    name="Test Freemium Model", description="A test freemium subscription model"
    )

    # Verify that the free tier was created
    assert len(model.tiers) == 1, f"Expected 1 tier (free tier), got {len(model.tiers)}"
    assert (
    model.tiers[0]["price_monthly"] == 0.0
    ), f"Expected free tier price to be 0.0, got {model.tiers[0]['price_monthly']}"

    # Add features
    feature1 = model.add_feature(
    name="Feature 1", description="Test feature 1", feature_type="functional"
    )

    feature2 = model.add_feature(
    name="Feature 2", description="Test feature 2", feature_type="functional"
    )

    # Add feature to free tier
    result = model.add_feature_to_free_tier(feature1["id"])
    assert result, "Failed to add feature to free tier"

    # Add paid tiers
    tier1 = model.add_paid_tier(
    name="Tier 1", description="Test tier 1", price_monthly=9.99
    )

    tier2 = model.add_paid_tier(
    name="Tier 2", description="Test tier 2", price_monthly=19.99
    )

    # Verify that the paid tiers were created
    assert (
    len(model.tiers) == 3
    ), f"Expected 3 tiers (free + 2 paid), got {len(model.tiers)}"

    # Assign features to paid tiers
    model.assign_feature_to_tier(feature1["id"], tier1["id"])
    model.assign_feature_to_tier(feature1["id"], tier2["id"])
    model.assign_feature_to_tier(feature2["id"], tier2["id"])

    # Test getting tier features
    free_tier_id = model.get_free_tier_id()
    free_features = model.get_tier_features(free_tier_id)
    assert (
    len(free_features) == 1
    ), f"Expected 1 feature in free tier, got {len(free_features)}"
    assert (
    free_features[0]["name"] == "Feature 1"
    ), f"Expected 'Feature 1', got '{free_features[0]['name']}'"

    tier1_features = model.get_tier_features(tier1["id"])
    assert (
    len(tier1_features) == 1
    ), f"Expected 1 feature in tier 1, got {len(tier1_features)}"

    tier2_features = model.get_tier_features(tier2["id"])
    assert (
    len(tier2_features) == 2
    ), f"Expected 2 features in tier 2, got {len(tier2_features)}"

    # Test updating free tier limits
    new_limits = {"usage": "very_limited", "api_calls": 50, "exports": 2}
    result = model.update_free_tier_limits(new_limits)
    assert result, "Failed to update free tier limits"

    # Verify that the limits were updated
    free_tier = next((t for t in model.tiers if t["id"] == free_tier_id), None)
    assert (
    free_tier["limits"]["api_calls"] == 50
    ), f"Expected api_calls limit to be 50, got {free_tier['limits']['api_calls']}"

    # Test to_dict
    model_dict = model.to_dict()
    assert (
    model_dict["model_type"] == "freemium"
    ), f"Expected model_type to be 'freemium', got '{model_dict.get('model_type')}'"
    assert (
    model_dict["free_tier_id"] == free_tier_id
    ), f"Expected free_tier_id to be '{free_tier_id}', got '{model_dict.get('free_tier_id')}'"

    # Test save_to_file and load_from_file
    test_file = "test_freemium_model.json"
    model.save_to_file(test_file)

    loaded_model = FreemiumModel.load_from_file(test_file)
    assert (
    loaded_model.name == model.name
    ), f"Expected '{model.name}', got '{loaded_model.name}'"
    assert len(loaded_model.tiers) == len(
    model.tiers
    ), f"Expected {len(model.tiers)} tiers, got {len(loaded_model.tiers)}"

    # Clean up
    os.remove(test_file)

    print("All tests passed!")


    if __name__ == "__main__":
    test_freemium_model()