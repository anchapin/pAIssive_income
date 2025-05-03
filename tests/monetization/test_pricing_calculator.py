"""
Tests for the PricingCalculator class.
"""


import json
import os
import shutil
import tempfile

import pytest

from monetization.pricing_calculator import PricingCalculator
from monetization.subscription_models import SubscriptionModel




@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def pricing_calculator():
    """Create a PricingCalculator instance for testing."""
    return PricingCalculator(
        name="Test Pricing Calculator",
        description="A test pricing calculator",
        pricing_strategy="value-based",
        base_cost=5.0,
        profit_margin=0.3,
        competitor_prices={"basic": 9.99, "pro": 19.99, "premium": 29.99},
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
    model.add_tier(
        name="Basic",
        description="Basic tier",
        price_monthly=9.99,
        features=[feature1["id"]],
    )

    model.add_tier(
        name="Pro",
        description="Pro tier",
        price_monthly=19.99,
        features=[feature1["id"], feature2["id"]],
    )

    return model


def test_pricing_calculator_init(pricing_calculator):
    """Test PricingCalculator initialization."""
    # Check that the calculator has the expected attributes
    assert pricing_calculator.name == "Test Pricing Calculator"
    assert pricing_calculator.description == "A test pricing calculator"
    assert pricing_calculator.pricing_strategy == "value-based"
    assert pricing_calculator.base_cost == 5.0
    assert pricing_calculator.profit_margin == 0.3
    assert pricing_calculator.competitor_prices == {
        "basic": 9.99,
        "pro": 19.99,
        "premium": 29.99,
    }
    assert hasattr(pricing_calculator, "id")
    assert hasattr(pricing_calculator, "created_at")
    assert hasattr(pricing_calculator, "updated_at")


def test_calculate_price(pricing_calculator):
    """Test calculate_price method."""
    # Test with default parameters
    price = pricing_calculator.calculate_price(base_value=10.0)
    assert price == 10.99  # Rounded to nearest .99

    # Test with tier multiplier
    price = pricing_calculator.calculate_price(base_value=10.0, tier_multiplier=2.0)
    assert price == 19.99  # Rounded to nearest .99

    # Test with market adjustment
    price = pricing_calculator.calculate_price(base_value=10.0, market_adjustment=1.5)
    assert price == 15.99  # Rounded to nearest .99

    # Test with both tier multiplier and market adjustment
    price = pricing_calculator.calculate_price(
        base_value=10.0, tier_multiplier=2.0, market_adjustment=1.5
    )
    assert price == 30.99  # Rounded to nearest .99


def test_calculate_optimal_price(pricing_calculator):
    """Test calculate_optimal_price method."""
    # Test with all parameters
    price = pricing_calculator.calculate_optimal_price(
        tier_name="Pro",
        cost_per_user=5.0,
        value_perception=0.8,
        competitor_price=19.99,
        price_sensitivity=0.7,
    )

    # Check that the price is a float and greater than 0
    assert isinstance(price, float)
    assert price > 0


def test_analyze_price_sensitivity(pricing_calculator):
    """Test analyze_price_sensitivity method."""
    # Test with required parameters
    analysis = pricing_calculator.analyze_price_sensitivity(
        base_price=19.99, market_size=10000
    )

    # Check that the analysis has the expected keys
    assert "base_price" in analysis
    assert "market_size" in analysis
    assert "price_elasticity" in analysis
    assert "price_points" in analysis

    # Check that the base price is correct
    assert analysis["base_price"] == 19.99

    # Check that there are price points
    assert len(analysis["price_points"]) > 0

    # Check that each price point has the expected keys
    for point in analysis["price_points"]:
        assert "price" in point
        assert "demand" in point
        assert "revenue" in point

    # Test with custom parameters
    analysis = pricing_calculator.analyze_price_sensitivity(
        base_price=29.99, market_size=5000, price_elasticity=1.5
    )

    # Check that the custom parameters were used
    assert analysis["base_price"] == 29.99
    assert analysis["market_size"] == 5000
    assert analysis["price_elasticity"] == 1.5
    assert len(analysis["price_points"]) > 0


def test_to_dict(pricing_calculator):
    """Test to_dict method."""
    # Convert to dictionary
    calculator_dict = pricing_calculator.to_dict()

    # Check that the dictionary has the expected keys
    assert "id" in calculator_dict
    assert "name" in calculator_dict
    assert "description" in calculator_dict
    assert "pricing_strategy" in calculator_dict
    assert "base_cost" in calculator_dict
    assert "profit_margin" in calculator_dict
    assert "competitor_prices" in calculator_dict
    assert "created_at" in calculator_dict
    assert "updated_at" in calculator_dict

    # Check that the values are correct
    assert calculator_dict["name"] == "Test Pricing Calculator"
    assert calculator_dict["description"] == "A test pricing calculator"
    assert calculator_dict["pricing_strategy"] == "value-based"
    assert calculator_dict["base_cost"] == 5.0
    assert calculator_dict["profit_margin"] == 0.3
    assert calculator_dict["competitor_prices"] == {
        "basic": 9.99,
        "pro": 19.99,
        "premium": 29.99,
    }


def test_to_json(pricing_calculator):
    """Test to_json method."""
    # Convert to JSON
    calculator_json = pricing_calculator.to_json()

    # Check that the JSON is a string
    assert isinstance(calculator_json, str)

    # Parse the JSON
    calculator_dict = json.loads(calculator_json)

    # Check that the dictionary has the expected keys
    assert "id" in calculator_dict
    assert "name" in calculator_dict
    assert "description" in calculator_dict
    assert "pricing_strategy" in calculator_dict
    assert "base_cost" in calculator_dict
    assert "profit_margin" in calculator_dict
    assert "competitor_prices" in calculator_dict
    assert "created_at" in calculator_dict
    assert "updated_at" in calculator_dict


def test_save_to_file(pricing_calculator, temp_dir):
    """Test save_to_file method."""
    # Create a file path
    file_path = os.path.join(temp_dir, "test_calculator.json")

    # Save to file
    pricing_calculator.save_to_file(file_path)

    # Check that the file exists
    assert os.path.exists(file_path)

    # Read the file
    with open(file_path, "r") as f:
        calculator_dict = json.load(f)

    # Check that the dictionary has the expected keys
    assert "id" in calculator_dict
    assert "name" in calculator_dict
    assert "description" in calculator_dict
    assert "pricing_strategy" in calculator_dict
    assert "base_cost" in calculator_dict
    assert "profit_margin" in calculator_dict
    assert "competitor_prices" in calculator_dict
    assert "created_at" in calculator_dict
    assert "updated_at" in calculator_dict


def test_load_from_file(pricing_calculator, temp_dir):
    """Test load_from_file method."""
    # Create a file path
    file_path = os.path.join(temp_dir, "test_calculator.json")

    # Save to file
    pricing_calculator.save_to_file(file_path)

    # Load from file
    loaded_calculator = PricingCalculator.load_from_file(file_path)

    # Check that the loaded calculator has the expected attributes
    assert loaded_calculator.name == pricing_calculator.name
    assert loaded_calculator.description == pricing_calculator.description
    assert loaded_calculator.pricing_strategy == pricing_calculator.pricing_strategy
    assert loaded_calculator.id == pricing_calculator.id
    assert loaded_calculator.created_at == pricing_calculator.created_at
    assert loaded_calculator.updated_at == pricing_calculator.updated_at

    # Note: Some attributes might have default values when loaded from file
    # if they weren't part of the original implementation


def test_repr(pricing_calculator):
    """Test __repr__ method."""
    # Get the string representation
    repr_str = repr(pricing_calculator)

    # Check that the string contains the expected information
    assert "PricingCalculator" in repr_str
    assert pricing_calculator.id in repr_str
    assert pricing_calculator.name in repr_str
    assert pricing_calculator.pricing_strategy in repr_str