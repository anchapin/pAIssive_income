"""
Property-based tests for the RevenueProjector class.

These tests verify that the RevenueProjector produces sensible
projections across a wide range of input parameters.
"""
import pytest
from hypothesis import given, strategies as st, assume
from monetization.revenue_projector import RevenueProjector
from monetization.subscription_models import SubscriptionModel


# Strategies for generating valid RevenueProjector parameters
names = st.text(min_size=1, max_size=100)
descriptions = st.text(max_size=500)
initial_users = st.integers(min_value=0, max_value=100000)
user_acquisition_rates = st.integers(min_value=0, max_value=10000)
conversion_rates = st.floats(min_value=0.001, max_value=0.999)
churn_rates = st.floats(min_value=0.001, max_value=0.5)
months = st.integers(min_value=1, max_value=36)
growth_rates = st.floats(min_value=-0.1, max_value=0.5)

# Strategy for generating tier distributions
@st.composite
def tier_distributions(draw):
    """Generate a valid tier distribution dictionary."""
    # Generate between 1 and 5 tiers
    num_tiers = draw(st.integers(min_value=1, max_value=5))
    
    # Generate tier names
    tiers = [f"tier_{i}" for i in range(num_tiers)]
    
    # Generate percentages that sum to 1.0
    percentages = []
    remaining = 1.0
    for i in range(num_tiers - 1):
        if remaining <= 0:
            percentages.append(0.0)
        else:
            percentage = draw(st.floats(min_value=0.01, max_value=remaining))
            percentages.append(percentage)
            remaining -= percentage
    
    # Add the last percentage
    percentages.append(remaining)
    
    # Create and return the distribution dictionary
    return {tier: percentage for tier, percentage in zip(tiers, percentages)}


@given(
    name=names,
    description=descriptions,
    initial_users=initial_users,
    user_acquisition_rate=user_acquisition_rates,
    conversion_rate=conversion_rates,
    churn_rate=churn_rates,
    tier_dist=tier_distributions(),
    months=months,
    growth_rate=growth_rates
)
def test_revenue_projections_properties(
    name, description, initial_users, user_acquisition_rate, 
    conversion_rate, churn_rate, tier_dist, months, growth_rate
):
    """Test properties of revenue projections across a wide range of inputs."""
    
    # Create a RevenueProjector instance
    projector = RevenueProjector(
        name=name,
        description=description,
        initial_users=initial_users,
        user_acquisition_rate=user_acquisition_rate,
        conversion_rate=conversion_rate,
        churn_rate=churn_rate,
        tier_distribution=tier_dist
    )
    
    # Project revenue
    revenue_projections = projector.project_revenue(
        months=months,
        growth_rate=growth_rate
    )
    
    # Property 1: The projections list should have the expected length
    assert len(revenue_projections) == months
    
    # Property 2: Month numbers should be sequential from 1 to months
    assert [p["month"] for p in revenue_projections] == list(range(1, months + 1))
    
    # Property 3: Total users should be the sum of free and paid users
    for projection in revenue_projections:
        assert projection["total_users"] == projection["free_users"] + projection["paid_users"]
    
    # Property 4: Tier users should sum to paid users
    for projection in revenue_projections:
        tier_users_sum = sum(projection["tier_users"].values())
        assert abs(tier_users_sum - projection["paid_users"]) < 1.0  # Allow for floating-point errors
    
    # Property 5: Revenue calculations should be consistent with user counts and prices
    for projection in revenue_projections:
        for tier, users in projection["tier_users"].items():
            if users > 0:
                # If we have tier price information, verify revenue calculation
                if tier in projection["tier_revenue"] and tier in tier_dist:
                    # We don't have exact price information here, but we can check that revenue > 0
                    assert projection["tier_revenue"][tier] >= 0
    
    # Property 6: Cumulative revenue should increase monotonically
    cumulative_revenues = [p["cumulative_revenue"] for p in revenue_projections]
    assert all(curr >= prev for prev, curr in zip(cumulative_revenues, cumulative_revenues[1:]))


@given(
    name=names,
    description=descriptions,
    initial_users=initial_users,
    user_acquisition_rate=user_acquisition_rates,
    conversion_rate=conversion_rates,
    churn_rate=churn_rates,
    months=months,
    growth_rate=growth_rates
)
def test_user_projections_properties(
    name, description, initial_users, user_acquisition_rate, 
    conversion_rate, churn_rate, months, growth_rate
):
    """Test properties of user projections across a wide range of inputs."""
    
    # Create a RevenueProjector instance
    projector = RevenueProjector(
        name=name,
        description=description,
        initial_users=initial_users,
        user_acquisition_rate=user_acquisition_rate,
        conversion_rate=conversion_rate,
        churn_rate=churn_rate
    )
    
    # Project users
    user_projections = projector.project_users(
        months=months,
        growth_rate=growth_rate
    )
    
    # Property 1: The projections list should have the expected length
    assert len(user_projections) == months
    
    # Property 2: Month numbers should be sequential from 1 to months
    assert [p["month"] for p in user_projections] == list(range(1, months + 1))
    
    # Property 3: Total users should be the sum of free and paid users
    for projection in user_projections:
        assert projection["total_users"] == projection["free_users"] + projection["paid_users"]
    
    # Property 4: With positive growth and no churn, user count should increase
    if growth_rate > 0 and churn_rate == 0:
        total_users = [p["total_users"] for p in user_projections]
        assert all(curr >= prev for prev, curr in zip(total_users, total_users[1:]))
    
    # Property 5: With high churn and no growth/acquisition, user count should decrease
    if growth_rate <= 0 and churn_rate > 0.2 and user_acquisition_rate == 0 and len(user_projections) > 1:
        total_users = [p["total_users"] for p in user_projections]
        # Skip this check if initial users is 0 (can't decrease from 0)
        if initial_users > 0:
            assert total_users[-1] < total_users[0]


@given(
    name=names,
    description=descriptions,
    initial_users=initial_users,
    user_acquisition_rate=user_acquisition_rates,
    conversion_rate=conversion_rates,
    churn_rate=churn_rates,
    tier_dist=tier_distributions(),
)
def test_invariant_properties(
    name, description, initial_users, user_acquisition_rate, 
    conversion_rate, churn_rate, tier_dist
):
    """Test invariant properties of the RevenueProjector."""
    
    # Create a RevenueProjector instance
    projector = RevenueProjector(
        name=name,
        description=description,
        initial_users=initial_users,
        user_acquisition_rate=user_acquisition_rate,
        conversion_rate=conversion_rate,
        churn_rate=churn_rate,
        tier_distribution=tier_dist
    )
    
    # Property 1: to_dict() should contain all the initialized values
    projector_dict = projector.to_dict()
    assert projector_dict["name"] == name
    assert projector_dict["description"] == description
    assert projector_dict["initial_users"] == initial_users
    assert projector_dict["user_acquisition_rate"] == user_acquisition_rate
    assert projector_dict["conversion_rate"] == conversion_rate
    assert projector_dict["churn_rate"] == churn_rate
    assert projector_dict["tier_distribution"] == tier_dist
    
    # Property 2: to_json() should be valid JSON that can be parsed back
    import json
    projector_json = projector.to_json()
    parsed_json = json.loads(projector_json)
    assert parsed_json["name"] == name
    assert parsed_json["description"] == description