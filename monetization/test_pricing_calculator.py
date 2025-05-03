"""
Test script for the PricingCalculator class.
"""

import os

from pricing_calculator import PricingCalculator
from subscription_models import SubscriptionModel


def test_pricing_calculator():
    """Test the functionality of the PricingCalculator class."""
    print("Testing PricingCalculator class...")

    # Create a pricing calculator
    calculator = PricingCalculator(
        name="Test Pricing Calculator",
        description="A test pricing calculator",
        pricing_strategy="value - based",
    )

    # Test calculate_price
    price = calculator.calculate_price(base_value=10.0, tier_multiplier=2.0, 
        market_adjustment=1.0)
    assert price == 19.99, f"Expected price to be 19.99, got {price}"

    # Create a subscription model for testing
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add tiers
    free_tier = model.add_tier(name="Free", description="Free tier", price_monthly=0.0)

    basic_tier = model.add_tier(name="Basic", description="Basic tier", 
        price_monthly=9.99)

    pro_tier = model.add_tier(name="Pro", description="Pro tier", price_monthly=19.99)

    premium_tier = model.add_tier(name="Premium", description="Premium tier", 
        price_monthly=49.99)

    # Test calculate_optimal_prices
    prices = calculator.calculate_optimal_prices(
        subscription_model=model, base_value=10.0, market_adjustment=1.0
    )

    assert len(prices) == 4, f"Expected 4 prices, got {len(prices)}"
    assert (
        prices[free_tier["id"]] == 0.0
    ), f"Expected free tier price to be 0.0, got {prices[free_tier['id']]}"
    assert (
        prices[basic_tier["id"]] == 9.99
    ), f"Expected basic tier price to be 9.99, got {prices[basic_tier['id']]}"
    assert (
        prices[pro_tier["id"]] == 19.99
    ), f"Expected pro tier price to be 19.99, got {prices[pro_tier['id']]}"
    assert (
        prices[premium_tier["id"]] == 49.99
    ), f"Expected premium tier price to be 49.99, got {prices[premium_tier['id']]}"

    # Test analyze_price_sensitivity
    analysis = calculator.analyze_price_sensitivity(
        base_price=19.99, market_size=10000, price_elasticity=1.0
    )

    assert (
        len(analysis["price_points"]) == 5
    ), f"Expected 5 price points, got {len(analysis['price_points'])}"
    assert (
        analysis["base_price"] == 19.99
    ), f"Expected base price to be 19.99, got {analysis['base_price']}"
    assert (
        analysis["market_size"] == 10000
    ), f"Expected market size to be 10000, got {analysis['market_size']}"

    # Test to_dict and to_json
    calculator_dict = calculator.to_dict()
    assert (
        calculator_dict["name"] == "Test Pricing Calculator"
    ), f"Expected 'Test Pricing Calculator', got '{calculator_dict['name']}'"

    calculator_json = calculator.to_json()
    assert isinstance(calculator_json, str), f"Expected string, 
        got {type(calculator_json)}"

    # Test save_to_file and load_from_file
    test_file = "test_calculator.json"
    calculator.save_to_file(test_file)

    loaded_calculator = PricingCalculator.load_from_file(test_file)
    assert (
        loaded_calculator.name == calculator.name
    ), f"Expected '{calculator.name}', got '{loaded_calculator.name}'"
    assert (
        loaded_calculator.pricing_strategy == calculator.pricing_strategy
    ), f"Expected '{calculator.pricing_strategy}', 
        got '{loaded_calculator.pricing_strategy}'"

    # Clean up
    os.remove(test_file)

    print("All tests passed!")


if __name__ == "__main__":
    test_pricing_calculator()
