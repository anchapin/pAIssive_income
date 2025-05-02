"""
Tests for the RevenueProjector class.
"""

import json
import os
import shutil
import tempfile

import pytest

from monetization.revenue_projector import RevenueProjector
from monetization.subscription_models import SubscriptionModel


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def revenue_projector():
    """Create a RevenueProjector instance for testing."""
    return RevenueProjector(
        name="Test Revenue Projector",
        description="A test revenue projector",
        initial_users=100,
        user_acquisition_rate=50,
        conversion_rate=0.2,
        churn_rate=0.05,
        tier_distribution={"basic": 0.6, "pro": 0.3, "premium": 0.1},
    )


@pytest.fixture
def subscription_model():
    """Create a SubscriptionModel instance for testing."""
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add features
    feature1 = model.add_feature(
        name="Feature 1", description="A test feature", feature_type="functional"
    )

    feature2 = model.add_feature(
        name="Feature 2", description="Another test feature", feature_type="premium"
    )

    # Add tiers
    basic_tier = model.add_tier(
        name="Basic",
        description="Basic tier",
        price_monthly=9.99,
        features=[feature1["id"]],
    )

    pro_tier = model.add_tier(
        name="Pro",
        description="Pro tier",
        price_monthly=19.99,
        features=[feature1["id"], feature2["id"]],
    )

    premium_tier = model.add_tier(
        name="Premium",
        description="Premium tier",
        price_monthly=29.99,
        features=[feature1["id"], feature2["id"]],
    )

    return model


def test_revenue_projector_init(revenue_projector):
    """Test RevenueProjector initialization."""
    # Check that the projector has the expected attributes
    assert revenue_projector.name == "Test Revenue Projector"
    assert revenue_projector.description == "A test revenue projector"
    assert revenue_projector.initial_users == 100
    assert revenue_projector.user_acquisition_rate == 50
    assert revenue_projector.conversion_rate == 0.2
    assert revenue_projector.churn_rate == 0.05
    assert revenue_projector.tier_distribution == {
        "basic": 0.6,
        "pro": 0.3,
        "premium": 0.1,
    }
    assert hasattr(revenue_projector, "id")
    assert hasattr(revenue_projector, "created_at")
    assert hasattr(revenue_projector, "updated_at")


def test_project_users(revenue_projector):
    """Test project_users method."""
    # Project users for 12 months
    user_projections = revenue_projector.project_users(months=12, growth_rate=0.05)

    # Check that the projections list has the expected length
    assert len(user_projections) == 12

    # Check that each projection has the expected keys
    for projection in user_projections:
        assert "month" in projection
        assert "total_users" in projection
        assert "free_users" in projection
        assert "paid_users" in projection
        assert "new_users" in projection
        assert "churned_users" in projection

    # Check that the first month's projection is correct
    first_month = user_projections[0]
    assert first_month["month"] == 1
    assert first_month["total_users"] > 100  # Should be more than initial users
    assert first_month["free_users"] > 0
    assert first_month["paid_users"] > 0
    assert first_month["new_users"] > 0
    assert first_month["churned_users"] >= 0

    # Check that the last month's projection is correct
    last_month = user_projections[-1]
    assert last_month["month"] == 12
    assert last_month["total_users"] > first_month["total_users"]  # Should grow over time

    # Test with different parameters
    user_projections = revenue_projector.project_users(months=24, growth_rate=0.1)

    # Check that the projections list has the expected length
    assert len(user_projections) == 24

    # Check that the growth rate affects the projections
    assert user_projections[-1]["total_users"] > user_projections[0]["total_users"]


def test_project_revenue_without_model(revenue_projector):
    """Test project_revenue method without a subscription model."""
    # Project revenue for 12 months
    revenue_projections = revenue_projector.project_revenue(months=12, growth_rate=0.05)

    # Check that the projections is a list
    assert isinstance(revenue_projections, list)

    # Check that the projections list has the expected length
    assert len(revenue_projections) == 12

    # Check that each projection has the expected keys
    for projection in revenue_projections:
        assert "month" in projection
        assert "total_users" in projection
        assert "free_users" in projection
        assert "paid_users" in projection
        assert "tier_users" in projection
        assert "tier_revenue" in projection
        assert "cumulative_revenue" in projection

    # Check that the first month's projection is correct
    first_month = revenue_projections[0]
    assert first_month["month"] == 1
    assert first_month["total_users"] > 0
    assert first_month["free_users"] > 0
    assert first_month["paid_users"] >= 0
    assert "tier_users" in first_month
    assert "tier_revenue" in first_month
    assert "cumulative_revenue" in first_month


def test_project_revenue_with_model(revenue_projector, subscription_model):
    """Test project_revenue method with a subscription model."""
    # Project revenue for 12 months
    revenue_projections = revenue_projector.project_revenue(
        months=12, growth_rate=0.05, subscription_model=subscription_model
    )

    # Check that the projections is a list
    assert isinstance(revenue_projections, list)

    # Check that the projections list has the expected length
    assert len(revenue_projections) == 12

    # Check that each projection has the expected keys
    for projection in revenue_projections:
        assert "month" in projection
        assert "total_users" in projection
        assert "free_users" in projection
        assert "paid_users" in projection
        assert "tier_users" in projection
        assert "tier_revenue" in projection
        assert "cumulative_revenue" in projection

        # Check that the tier users and revenue dictionaries have the expected keys
        assert "Basic" in projection["tier_users"]
        assert "Pro" in projection["tier_users"]
        assert "Premium" in projection["tier_users"]
        assert "Basic" in projection["tier_revenue"]
        assert "Pro" in projection["tier_revenue"]
        assert "Premium" in projection["tier_revenue"]

    # Check that the first month's projection is correct
    first_month = revenue_projections[0]
    assert first_month["month"] == 1
    assert first_month["total_users"] > 0
    assert first_month["free_users"] > 0
    assert first_month["paid_users"] >= 0


def test_project_revenue_with_prices(revenue_projector, subscription_model):
    """Test project_revenue method with custom prices."""
    # Define custom prices
    prices = {
        subscription_model.tiers[0]["id"]: 14.99,  # Basic tier
        subscription_model.tiers[1]["id"]: 24.99,  # Pro tier
        subscription_model.tiers[2]["id"]: 39.99,  # Premium tier
    }

    # Project revenue for 12 months
    revenue_projections = revenue_projector.project_revenue(
        months=12,
        growth_rate=0.05,
        subscription_model=subscription_model,
        prices=prices,
    )

    # Check that the projections is a list
    assert isinstance(revenue_projections, list)

    # Check that the projections list has the expected length
    assert len(revenue_projections) == 12

    # Check that each projection has the expected keys
    for projection in revenue_projections:
        assert "month" in projection
        assert "total_users" in projection
        assert "free_users" in projection
        assert "paid_users" in projection
        assert "tier_users" in projection
        assert "tier_revenue" in projection
        assert "cumulative_revenue" in projection

        # Check that the tier users and revenue dictionaries have the expected keys
        assert "Basic" in projection["tier_users"]
        assert "Pro" in projection["tier_users"]
        assert "Premium" in projection["tier_users"]
        assert "Basic" in projection["tier_revenue"]
        assert "Pro" in projection["tier_revenue"]
        assert "Premium" in projection["tier_revenue"]

    # Check that the first month's projection is correct
    first_month = revenue_projections[0]
    basic_users = first_month["tier_users"]["Basic"]
    pro_users = first_month["tier_users"]["Pro"]
    premium_users = first_month["tier_users"]["Premium"]

    # Check that the tier users are reasonable
    assert basic_users >= 0
    assert pro_users >= 0
    assert premium_users >= 0


def test_to_dict(revenue_projector):
    """Test to_dict method."""
    # Convert to dictionary
    projector_dict = revenue_projector.to_dict()

    # Check that the dictionary has the expected keys
    assert "id" in projector_dict
    assert "name" in projector_dict
    assert "description" in projector_dict
    assert "initial_users" in projector_dict
    assert "user_acquisition_rate" in projector_dict
    assert "conversion_rate" in projector_dict
    assert "churn_rate" in projector_dict
    assert "tier_distribution" in projector_dict
    assert "created_at" in projector_dict
    assert "updated_at" in projector_dict

    # Check that the values are correct
    assert projector_dict["name"] == "Test Revenue Projector"
    assert projector_dict["description"] == "A test revenue projector"
    assert projector_dict["initial_users"] == 100
    assert projector_dict["user_acquisition_rate"] == 50
    assert projector_dict["conversion_rate"] == 0.2
    assert projector_dict["churn_rate"] == 0.05
    assert projector_dict["tier_distribution"] == {
        "basic": 0.6,
        "pro": 0.3,
        "premium": 0.1,
    }


def test_to_json(revenue_projector):
    """Test to_json method."""
    # Convert to JSON
    projector_json = revenue_projector.to_json()

    # Check that the JSON is a string
    assert isinstance(projector_json, str)

    # Parse the JSON
    projector_dict = json.loads(projector_json)

    # Check that the dictionary has the expected keys
    assert "id" in projector_dict
    assert "name" in projector_dict
    assert "description" in projector_dict
    assert "initial_users" in projector_dict
    assert "user_acquisition_rate" in projector_dict
    assert "conversion_rate" in projector_dict
    assert "churn_rate" in projector_dict
    assert "tier_distribution" in projector_dict
    assert "created_at" in projector_dict
    assert "updated_at" in projector_dict


def test_save_to_file(revenue_projector, temp_dir):
    """Test save_to_file method."""
    # Create a file path
    file_path = os.path.join(temp_dir, "test_projector.json")

    # Save to file
    revenue_projector.save_to_file(file_path)

    # Check that the file exists
    assert os.path.exists(file_path)

    # Read the file
    with open(file_path, "r") as f:
        projector_dict = json.load(f)

    # Check that the dictionary has the expected keys
    assert "id" in projector_dict
    assert "name" in projector_dict
    assert "description" in projector_dict
    assert "initial_users" in projector_dict
    assert "user_acquisition_rate" in projector_dict
    assert "conversion_rate" in projector_dict
    assert "churn_rate" in projector_dict
    assert "tier_distribution" in projector_dict
    assert "created_at" in projector_dict
    assert "updated_at" in projector_dict


def test_load_from_file(revenue_projector, temp_dir):
    """Test load_from_file method."""
    # Create a file path
    file_path = os.path.join(temp_dir, "test_projector.json")

    # Save to file
    revenue_projector.save_to_file(file_path)

    # Load from file
    loaded_projector = RevenueProjector.load_from_file(file_path)

    # Check that the loaded projector has the expected attributes
    assert loaded_projector.name == revenue_projector.name
    assert loaded_projector.description == revenue_projector.description
    assert loaded_projector.initial_users == revenue_projector.initial_users
    assert loaded_projector.user_acquisition_rate == revenue_projector.user_acquisition_rate
    assert loaded_projector.conversion_rate == revenue_projector.conversion_rate
    assert loaded_projector.churn_rate == revenue_projector.churn_rate
    assert loaded_projector.tier_distribution == revenue_projector.tier_distribution
    assert loaded_projector.id == revenue_projector.id
    assert loaded_projector.created_at == revenue_projector.created_at
    assert loaded_projector.updated_at == revenue_projector.updated_at


def test_repr(revenue_projector):
    """Test __repr__ method."""
    # Get the string representation
    repr_str = repr(revenue_projector)

    # Check that the string contains the expected information
    assert "RevenueProjector" in repr_str
    assert revenue_projector.id in repr_str
    assert revenue_projector.name in repr_str
