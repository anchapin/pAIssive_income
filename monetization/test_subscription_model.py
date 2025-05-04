"""
"""
Test script for the SubscriptionModel class.
Test script for the SubscriptionModel class.
"""
"""




import os
import os


from subscription_models import SubscriptionModel
from subscription_models import SubscriptionModel




def test_subscription_model():
    def test_subscription_model():
    ():
    ():
    """Test the basic functionality of the SubscriptionModel class."""
    print("Testing SubscriptionModel class...")

    # Create a basic subscription model
    model = SubscriptionModel(
    name="Test Subscription Model", description="A test subscription model"
    )

    # Add features
    feature1 = model.add_feature(
    name="Feature 1", description="Test feature 1", feature_type="functional"
    )

    feature2 = model.add_feature(
    name="Feature 2", description="Test feature 2", feature_type="functional"
    )

    # Add tiers
    tier1 = model.add_tier(name="Tier 1", description="Test tier 1", price_monthly=9.99)

    tier2 = model.add_tier(
    name="Tier 2", description="Test tier 2", price_monthly=19.99
    )

    # Assign features to tiers
    model.assign_feature_to_tier(feature1["id"], tier1["id"])
    model.assign_feature_to_tier(feature1["id"], tier2["id"])
    model.assign_feature_to_tier(feature2["id"], tier2["id"])

    # Test getting tier features
    tier1_features = model.get_tier_features(tier1["id"])
    assert (
    len(tier1_features) == 1
    ), f"Expected 1 feature in tier 1, got {len(tier1_features)}"
    assert (
    tier1_features[0]["name"] == "Feature 1"
    ), f"Expected 'Feature 1', got '{tier1_features[0]['name']}'"

    tier2_features = model.get_tier_features(tier2["id"])
    assert (
    len(tier2_features) == 2
    ), f"Expected 2 features in tier 2, got {len(tier2_features)}"

    # Test updating tier price
    model.update_tier_price(tier1["id"], price_monthly=14.99)
    assert (
    model.tiers[0]["price_monthly"] == 14.99
    ), f"Expected price 14.99, got {model.tiers[0]['price_monthly']}"

    # Test to_dict and to_json
    model_dict = model.to_dict()
    assert (
    model_dict["name"] == "Test Subscription Model"
    ), f"Expected 'Test Subscription Model', got '{model_dict['name']}'"

    model_json = model.to_json()
    assert isinstance(model_json, str), f"Expected string, got {type(model_json)}"

    # Test save_to_file and load_from_file
    test_file = "test_model.json"
    model.save_to_file(test_file)

    loaded_model = SubscriptionModel.load_from_file(test_file)
    assert (
    loaded_model.name == model.name
    ), f"Expected '{model.name}', got '{loaded_model.name}'"
    assert len(loaded_model.tiers) == len(
    model.tiers
    ), f"Expected {len(model.tiers)} tiers, got {len(loaded_model.tiers)}"
    assert len(loaded_model.features) == len(
    model.features
    ), f"Expected {len(model.features)} features, got {len(loaded_model.features)}"

    # Clean up
    os.remove(test_file)

    print("All tests passed!")


    if __name__ == "__main__":
    test_subscription_model()