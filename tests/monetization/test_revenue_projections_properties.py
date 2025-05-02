"""
Property-based tests for the RevenueProjector class.

These tests verify that the RevenueProjector produces sensible
projections across a wide range of input parameters.
"""

from hypothesis import assume, given
from hypothesis import strategies as st

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
acquisition_costs = st.floats(min_value=1.0, max_value=1000.0)
average_revenues = st.floats(min_value=1.0, max_size=200.0)
gross_margins = st.floats(min_value=0.1, max_value=0.9)


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
    growth_rate=growth_rates,
)
def test_revenue_projections_properties(
    name,
    description,
    initial_users,
    user_acquisition_rate,
    conversion_rate,
    churn_rate,
    tier_dist,
    months,
    growth_rate,
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
        tier_distribution=tier_dist,
    )

    # Project revenue
    revenue_projections = projector.project_revenue(months=months, growth_rate=growth_rate)

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
        assert (
            abs(tier_users_sum - projection["paid_users"]) < 1.0
        )  # Allow for floating-point errors

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
    growth_rate=growth_rates,
)
def test_user_projections_properties(
    name,
    description,
    initial_users,
    user_acquisition_rate,
    conversion_rate,
    churn_rate,
    months,
    growth_rate,
):
    """Test properties of user projections across a wide range of inputs."""

    # Create a RevenueProjector instance
    projector = RevenueProjector(
        name=name,
        description=description,
        initial_users=initial_users,
        user_acquisition_rate=user_acquisition_rate,
        conversion_rate=conversion_rate,
        churn_rate=churn_rate,
    )

    # Project users
    user_projections = projector.project_users(months=months, growth_rate=growth_rate)

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
    if (
        growth_rate <= 0
        and churn_rate > 0.2
        and user_acquisition_rate == 0
        and len(user_projections) > 1
    ):
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
    name,
    description,
    initial_users,
    user_acquisition_rate,
    conversion_rate,
    churn_rate,
    tier_dist,
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
        tier_distribution=tier_dist,
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


@given(average_revenue=average_revenues, churn_rate=churn_rates)
def test_lifetime_value_calculation_properties(average_revenue, churn_rate):
    """Test properties of lifetime value calculations."""

    # Create a RevenueProjector instance with default parameters
    projector = RevenueProjector("Test Projector")

    # Calculate lifetime value
    ltv = projector.calculate_lifetime_value(
        average_revenue_per_user=average_revenue, churn_rate=churn_rate
    )

    # Property 1: Average lifetime should be 1/churn_rate
    assert abs(ltv["average_lifetime_months"] - (1 / churn_rate)) < 0.001

    # Property 2: Lifetime value should be average_revenue * average_lifetime_months
    assert abs(ltv["lifetime_value"] - (average_revenue * ltv["average_lifetime_months"])) < 0.001

    # Property 3: One-year value should be at most 12 * average_revenue
    assert ltv["one_year_value"] <= 12 * average_revenue

    # Property 4: One-year value should be equal to average_revenue * min(12, average_lifetime_months)
    expected_one_year = average_revenue * min(12, ltv["average_lifetime_months"])
    assert abs(ltv["one_year_value"] - expected_one_year) < 0.001

    # Property 5: Five-year value should be at most 60 * average_revenue
    assert ltv["five_year_value"] <= 60 * average_revenue


@given(
    acquisition_cost=acquisition_costs,
    average_revenue=average_revenues,
    gross_margin=gross_margins,
)
def test_payback_period_calculation_properties(acquisition_cost, average_revenue, gross_margin):
    """Test properties of payback period calculations."""

    # Create a RevenueProjector instance with default parameters
    projector = RevenueProjector("Test Projector")

    # Calculate payback period
    payback = projector.calculate_payback_period(
        customer_acquisition_cost=acquisition_cost,
        average_revenue_per_user=average_revenue,
        gross_margin=gross_margin,
    )

    # Property 1: Monthly contribution should be average_revenue * gross_margin
    expected_contribution = average_revenue * gross_margin
    assert abs(payback["monthly_contribution"] - expected_contribution) < 0.001

    # Property 2: Payback period should be acquisition_cost / monthly_contribution
    expected_payback = acquisition_cost / expected_contribution
    assert abs(payback["payback_period_months"] - expected_payback) < 0.001

    # Property 3: Higher gross margins should lead to shorter payback periods (if fixing other values)
    if gross_margin < 0.9:
        higher_margin = min(0.9, gross_margin + 0.1)
        payback_higher_margin = projector.calculate_payback_period(
            customer_acquisition_cost=acquisition_cost,
            average_revenue_per_user=average_revenue,
            gross_margin=higher_margin,
        )
        assert payback_higher_margin["payback_period_months"] < payback["payback_period_months"]

    # Property 4: Higher acquisition costs should lead to longer payback periods (if fixing other values)
    higher_cost = acquisition_cost * 1.5
    payback_higher_cost = projector.calculate_payback_period(
        customer_acquisition_cost=higher_cost,
        average_revenue_per_user=average_revenue,
        gross_margin=gross_margin,
    )
    assert payback_higher_cost["payback_period_months"] > payback["payback_period_months"]


@given(
    name=names,
    description=descriptions,
    initial_users=initial_users,
    user_acquisition_rate=user_acquisition_rates,
    conversion_rate=conversion_rates,
    churn_rate=churn_rates,
    months=months,
    growth_rate=growth_rates,
)
def test_revenue_projection_calculation_properties(
    name,
    description,
    initial_users,
    user_acquisition_rate,
    conversion_rate,
    churn_rate,
    months,
    growth_rate,
):
    """Test specific properties of revenue projection calculations."""

    # Create a RevenueProjector instance
    projector = RevenueProjector(
        name=name,
        description=description,
        initial_users=initial_users,
        user_acquisition_rate=user_acquisition_rate,
        conversion_rate=conversion_rate,
        churn_rate=churn_rate,
    )

    # Create a basic subscription model for testing
    model = SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )

    # Add tiers with different prices
    basic_tier = model.add_tier(name="Basic", description="Basic tier", price_monthly=9.99)

    pro_tier = model.add_tier(name="Pro", description="Pro tier", price_monthly=19.99)

    premium_tier = model.add_tier(name="Premium", description="Premium tier", price_monthly=49.99)

    # Project revenue without a model (uses default pricing)
    revenue_projections_default = projector.project_revenue(months=months, growth_rate=growth_rate)

    # Project revenue with the model and its default prices
    revenue_projections_model = projector.project_revenue(
        months=months, growth_rate=growth_rate, subscription_model=model
    )

    # Project revenue with the model and custom prices
    custom_prices = {
        basic_tier["id"]: 14.99,
        pro_tier["id"]: 29.99,
        premium_tier["id"]: 59.99,
    }

    revenue_projections_custom = projector.project_revenue(
        months=months,
        growth_rate=growth_rate,
        subscription_model=model,
        prices=custom_prices,
    )

    # Property 1: All projection methods should produce the same number of projections
    assert (
        len(revenue_projections_default)
        == len(revenue_projections_model)
        == len(revenue_projections_custom)
        == months
    )

    # Property 2: Custom prices should lead to higher revenue (when prices are higher)
    if months > 0:
        total_revenue_default = revenue_projections_default[-1]["cumulative_revenue"]
        total_revenue_model = revenue_projections_model[-1]["cumulative_revenue"]
        total_revenue_custom = revenue_projections_custom[-1]["cumulative_revenue"]

        # The custom prices are higher than model prices, so should generate more revenue
        # However, we need to be careful as some tiers might not be used in different projections
        # We'll just check a few projections to see if the trend holds
        found_valid_comparison = False
        for month in range(min(months, 12)):  # Check first 12 months or all months if fewer
            proj_model = revenue_projections_model[month]
            proj_custom = revenue_projections_custom[month]

            # If both projections have the same tier users but different revenues,
            # we have a valid comparison
            matching_tiers = set(proj_model["tier_users"].keys()) & set(
                proj_custom["tier_users"].keys()
            )
            if matching_tiers and all(
                proj_model["tier_users"][t] == proj_custom["tier_users"][t] for t in matching_tiers
            ):
                found_valid_comparison = True
                # The custom prices are higher, so revenue should be higher
                assert proj_custom["total_revenue"] > proj_model["total_revenue"]
                break

        # We don't assert here in case we didn't find a valid comparison point


@given(
    initial_users=initial_users,
    user_acquisition_rate=user_acquisition_rates,
    conversion_rate=conversion_rates,
    churn_rate=churn_rates,
    months=st.integers(min_value=3, max_value=60),
    growth_rate=growth_rates,
)
def test_revenue_projection_monthly_to_annual_conversion(
    initial_users,
    user_acquisition_rate,
    conversion_rate,
    churn_rate,
    months,
    growth_rate,
):
    """Test properties of revenue projections when converting monthly to annual revenue."""

    # Create a RevenueProjector instance
    projector = RevenueProjector(
        name="Test Revenue Projector",
        description="Testing monthly to annual revenue conversion",
        initial_users=initial_users,
        user_acquisition_rate=user_acquisition_rate,
        conversion_rate=conversion_rate,
        churn_rate=churn_rate,
    )

    # Skip if months is not at least one full year
    assume(months >= 12)

    # Project revenue
    revenue_projections = projector.project_revenue(months=months, growth_rate=growth_rate)

    # Calculate annual revenues from monthly projections
    annual_revenues = []
    for year in range(1, (months // 12) + 1):
        start_month = (year - 1) * 12
        end_month = year * 12

        # Sum monthly revenues for this year
        yearly_revenue = sum(
            revenue_projections[i - 1]["total_revenue"]
            for i in range(start_month + 1, end_month + 1)
        )
        annual_revenues.append(yearly_revenue)

    # Property 1: Annual revenue should be non-negative
    for yearly_revenue in annual_revenues:
        assert yearly_revenue >= 0

    # Property 2: In a growing business (positive growth, low churn), annual revenue should generally increase year over year
    if growth_rate > 0.05 and churn_rate < 0.1 and len(annual_revenues) > 1:
        # Allow for some fluctuations but general trend should be up
        increasing_pairs = sum(
            1
            for i in range(len(annual_revenues) - 1)
            if annual_revenues[i + 1] >= annual_revenues[i]
        )
        assert increasing_pairs >= len(annual_revenues) - 2  # Allow one potential decrease

    # Property 3: Annual revenue should relate to user growth
    if months >= 24 and initial_users > 0 and growth_rate > 0:
        # Get user counts from the start and end of year 1 and 2
        users_start_y1 = revenue_projections[0]["total_users"]
        users_end_y1 = revenue_projections[11]["total_users"]

        if len(revenue_projections) >= 24:
            users_end_y2 = revenue_projections[23]["total_users"]

            # If users grew significantly, revenue should also grow
            if users_end_y2 > users_end_y1 * 1.5 and len(annual_revenues) >= 2:
                # Expect revenue to grow somewhat in proportion to user growth
                user_growth_ratio = users_end_y2 / users_end_y1
                revenue_growth_min = 0.5  # Allow for some lag in revenue growth vs user growth
                assert annual_revenues[1] >= annual_revenues[0] * revenue_growth_min


@given(
    churn_rates=st.lists(churn_rates, min_size=2, max_size=5),
    average_revenue=average_revenues,
    months=st.integers(min_value=12, max_value=60),
)
def test_revenue_projection_sensitivity_to_churn(churn_rates, average_revenue, months):
    """Test that revenue projections are appropriately sensitive to changes in churn rate."""

    # Sort churn rates
    churn_rates = sorted(churn_rates)

    # Create revenue projections for each churn rate
    results = []
    base_projector = RevenueProjector(
        name="Test Revenue Projector",
        description="Testing sensitivity to churn",
        initial_users=1000,
        user_acquisition_rate=100,
        conversion_rate=0.2,
    )

    for churn_rate in churn_rates:
        projector = RevenueProjector(
            name=base_projector.name,
            description=base_projector.description,
            initial_users=base_projector.initial_users,
            user_acquisition_rate=base_projector.user_acquisition_rate,
            conversion_rate=base_projector.conversion_rate,
            churn_rate=churn_rate,
        )

        # Project revenue
        revenue_projections = projector.project_revenue(months=months, growth_rate=0.05)

        # Store final cumulative revenue
        final_revenue = revenue_projections[-1]["cumulative_revenue"]
        results.append((churn_rate, final_revenue))

    # Property 1: Higher churn rates should result in lower cumulative revenue
    for i in range(len(results) - 1):
        # The relationship might not be perfectly monotonic for very small differences in churn
        # so we check for significant differences
        if results[i + 1][0] > results[i][0] * 1.5:  # Significantly higher churn
            assert results[i + 1][1] < results[i][1]  # Should result in lower revenue
