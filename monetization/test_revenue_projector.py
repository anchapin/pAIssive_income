"""
Test script for the RevenueProjector class.
"""


import os

from revenue_projector import RevenueProjector
from subscription_models import SubscriptionModel


def test_revenue_projector():
    ():
    """Test the functionality of the RevenueProjector class."""
    print("Testing RevenueProjector class...")

    # Create a revenue projector
    projector = RevenueProjector(
    name="Test Revenue Projector",
    description="A test revenue projector",
    initial_users=0,
    user_acquisition_rate=50,
    conversion_rate=0.2,
    churn_rate=0.05,
    tier_distribution={"basic": 0.6, "pro": 0.3, "premium": 0.1},
    )

    # Test project_users
    user_projections = projector.project_users(months=12, growth_rate=0.05)

    assert (
    len(user_projections["total_users"]) == 13
    ), f"Expected 13 total user entries (0-12), got {len(user_projections['total_users'])}"
    assert (
    len(user_projections["free_users"]) == 13
    ), f"Expected 13 free user entries (0-12), got {len(user_projections['free_users'])}"
    assert (
    len(user_projections["paid_users"]) == 13
    ), f"Expected 13 paid user entries (0-12), got {len(user_projections['paid_users'])}"

    # Create a subscription model for testing
    model = SubscriptionModel(
    name="Test Subscription Model", description="A test subscription model"
    )

    # Add tiers
    basic_tier = model.add_tier(
    name="Basic", description="Basic tier", price_monthly=9.99
    )

    pro_tier = model.add_tier(name="Pro", description="Pro tier", price_monthly=19.99)

    premium_tier = model.add_tier(
    name="Premium", description="Premium tier", price_monthly=49.99
    )

    # Define prices
    prices = {basic_tier["id"]: 9.99, pro_tier["id"]: 19.99, premium_tier["id"]: 49.99}

    # Test project_revenue
    projection = projector.project_revenue(
    subscription_model=model, prices=prices, months=12, growth_rate=0.05
    )

    assert (
    len(projection["monthly_revenue"]) == 13
    ), f"Expected 13 monthly revenue entries (0-12), got {len(projection['monthly_revenue'])}"
    assert (
    len(projection["cumulative_revenue"]) == 13
    ), f"Expected 13 cumulative revenue entries (0-12), got {len(projection['cumulative_revenue'])}"
    assert (
    len(projection["yearly_summaries"]) == 1
    ), f"Expected 1 yearly summary, got {len(projection['yearly_summaries'])}"

    # Test calculate_lifetime_value
    average_revenue = 9.99 * 0.6 + 19.99 * 0.3 + 49.99 * 0.1
    ltv = projector.calculate_lifetime_value(average_revenue)

    assert (
    ltv["average_revenue_per_user"] == average_revenue
    ), f"Expected average revenue {average_revenue}, got {ltv['average_revenue_per_user']}"
    assert (
    ltv["churn_rate"] == 0.05
    ), f"Expected churn rate 0.05, got {ltv['churn_rate']}"
    assert (
    ltv["average_lifetime_months"] == 20.0
    ), f"Expected average lifetime 20.0 months, got {ltv['average_lifetime_months']}"

    # Test calculate_payback_period
    payback = projector.calculate_payback_period(
    customer_acquisition_cost=50, average_revenue_per_user=average_revenue
    )

    assert (
    payback["customer_acquisition_cost"] == 50
    ), f"Expected acquisition cost 50, got {payback['customer_acquisition_cost']}"
    assert (
    payback["average_revenue_per_user"] == average_revenue
    ), f"Expected average revenue {average_revenue}, got {payback['average_revenue_per_user']}"
    assert (
    payback["gross_margin"] == 0.8
    ), f"Expected gross margin 0.8, got {payback['gross_margin']}"

    # Test to_dict and to_json
    projector_dict = projector.to_dict()
    assert (
    projector_dict["name"] == "Test Revenue Projector"
    ), f"Expected 'Test Revenue Projector', got '{projector_dict['name']}'"

    projector_json = projector.to_json()
    assert isinstance(
    projector_json, str
    ), f"Expected string, got {type(projector_json)}"

    # Test save_to_file and load_from_file
    test_file = "test_projector.json"
    projector.save_to_file(test_file)

    loaded_projector = RevenueProjector.load_from_file(test_file)
    assert (
    loaded_projector.name == projector.name
    ), f"Expected '{projector.name}', got '{loaded_projector.name}'"
    assert (
    loaded_projector.user_acquisition_rate == projector.user_acquisition_rate
    ), f"Expected {projector.user_acquisition_rate}, got {loaded_projector.user_acquisition_rate}"

    # Clean up
    os.remove(test_file)

    print("All tests passed!")


    if __name__ == "__main__":
    test_revenue_projector()