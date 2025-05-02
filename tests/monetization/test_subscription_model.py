"""
Tests for the SubscriptionModel class.
"""

import json
import os

import pytest

from monetization.subscription_models import SubscriptionModel


def test_subscription_model_init():
    """Test SubscriptionModel initialization."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Check that the model has the expected attributes
    assert model.name == "Test Subscription Model"
    assert model.description == "A test subscription model"
    assert isinstance(model.id, str)
    assert len(model.tiers) == 0
    assert len(model.features) == 0
    assert "monthly" in model.billing_cycles
    assert "yearly" in model.billing_cycles
    assert isinstance(model.created_at, str)
    assert isinstance(model.updated_at, str)


def test_add_feature():
    """Test add_feature method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a feature
    feature = model.add_feature(
        name="Test Feature",
        description="A test feature",
        feature_type="functional",
        value_proposition="Save time",
        development_cost="low",
    )

    # Check that the feature was added
    assert len(model.features) == 1
    assert model.features[0]["name"] == "Test Feature"
    assert model.features[0]["description"] == "A test feature"
    assert model.features[0]["feature_type"] == "functional"
    assert model.features[0]["value_proposition"] == "Save time"
    assert model.features[0]["development_cost"] == "low"
    assert isinstance(model.features[0]["id"], str)

    # Check that the returned feature is the same as the one in the model
    assert feature == model.features[0]


def test_add_tier():
    """Test add_tier method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a tier
    tier = model.add_tier(
        name="Test Tier",
        description="A test tier",
        price_monthly=9.99,
        price_yearly=99.99,
        features=["feature1", "feature2"],
        limits={"api_calls": 100, "exports": 10},
        target_users="Individual users",
    )

    # Check that the tier was added
    assert len(model.tiers) == 1
    assert model.tiers[0]["name"] == "Test Tier"
    assert model.tiers[0]["description"] == "A test tier"
    assert model.tiers[0]["price_monthly"] == 9.99
    assert model.tiers[0]["price_yearly"] == 99.99
    assert model.tiers[0]["features"] == ["feature1", "feature2"]
    assert model.tiers[0]["limits"] == {"api_calls": 100, "exports": 10}
    assert model.tiers[0]["target_users"] == "Individual users"
    assert isinstance(model.tiers[0]["id"], str)

    # Check that the returned tier is the same as the one in the model
    assert tier == model.tiers[0]


def test_get_tier_by_id():
    """Test get_tier_by_id method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a tier
    tier = model.add_tier(
        name="Test Tier", description="A test tier", price_monthly=9.99
    )

    # Get the tier by ID
    retrieved_tier = model.get_tier_by_id(tier["id"])

    # Check that the retrieved tier is the same as the one we added
    assert retrieved_tier == tier

    # Try to get a non-existent tier
    assert model.get_tier_by_id("non-existent-id") is None


def test_get_feature_by_id():
    """Test get_feature_by_id method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a feature
    feature = model.add_feature(
        name="Test Feature", description="A test feature", feature_type="functional"
    )

    # Get the feature by ID
    retrieved_feature = model.get_feature_by_id(feature["id"])

    # Check that the retrieved feature is the same as the one we added
    assert retrieved_feature == feature

    # Try to get a non-existent feature
    assert model.get_feature_by_id("non-existent-id") is None


def test_update_tier_price():
    """Test update_tier_price method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a tier
    tier = model.add_tier(
        name="Test Tier",
        description="A test tier",
        price_monthly=9.99,
        price_yearly=99.99,
    )

    # Update the tier price
    model.update_tier_price(tier["id"], price_monthly=14.99, price_yearly=149.99)

    # Check that the tier price was updated
    assert model.tiers[0]["price_monthly"] == 14.99
    assert model.tiers[0]["price_yearly"] == 149.99

    # Try to update a non-existent tier
    with pytest.raises(Exception):
        model.update_tier_price("non-existent-id", price_monthly=19.99)


def test_to_dict():
    """Test to_dict method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a feature
    model.add_feature(
        name="Test Feature", description="A test feature", feature_type="functional"
    )

    # Add a tier
    model.add_tier(
        name="Test Tier", description="A test tier", price_monthly=9.99
    )

    # Convert to dictionary
    model_dict = model.to_dict()

    # Check that the dictionary has the expected keys
    assert "id" in model_dict
    assert "name" in model_dict
    assert "description" in model_dict
    assert "tiers" in model_dict
    assert "features" in model_dict
    assert "billing_cycles" in model_dict
    assert "created_at" in model_dict
    assert "updated_at" in model_dict

    # Check that the values are correct
    assert model_dict["name"] == "Test Subscription Model"
    assert model_dict["description"] == "A test subscription model"
    assert len(model_dict["tiers"]) == 1
    assert len(model_dict["features"]) == 1
    assert model_dict["tiers"][0]["name"] == "Test Tier"
    assert model_dict["features"][0]["name"] == "Test Feature"


def test_to_json():
    """Test to_json method."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Convert to JSON
    model_json = model.to_json()

    # Check that the JSON is valid
    model_dict = json.loads(model_json)
    assert "id" in model_dict
    assert "name" in model_dict
    assert model_dict["name"] == "Test Subscription Model"


def test_save_load_file(temp_dir):
    """Test save_to_file and load_from_file methods."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add a feature
    model.add_feature(
        name="Test Feature", description="A test feature", feature_type="functional"
    )

    # Add a tier
    model.add_tier(
        name="Test Tier", description="A test tier", price_monthly=9.99
    )

    # Save to file
    file_path = os.path.join(temp_dir, "test_model.json")
    model.save_to_file(file_path)

    # Check that the file exists
    assert os.path.exists(file_path)

    # Load from file
    loaded_model = SubscriptionModel.load_from_file(file_path)

    # Check that the loaded model has the same values
    assert loaded_model.name == model.name
    assert loaded_model.description == model.description
    assert len(loaded_model.tiers) == len(model.tiers)
    assert len(loaded_model.features) == len(model.features)
    assert loaded_model.tiers[0]["name"] == model.tiers[0]["name"]
    assert loaded_model.features[0]["name"] == model.features[0]["name"]
