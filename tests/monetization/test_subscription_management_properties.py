"""
Property-based tests for the subscription management logic.

These tests verify that subscription management operations work correctly
across a wide range of input parameters.
"""
import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, example, assume
from monetization.subscription_manager import SubscriptionManager
from monetization.user_subscription import Subscription, SubscriptionStatus
from monetization.subscription import SubscriptionPlan


# Strategies for generating subscription data
user_ids = st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")
tier_names = st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")
tier_prices = st.floats(min_value=0.01, max_value=999.99)
billing_cycles = st.sampled_from(['monthly', 'annual'])
start_dates = st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 1, 1))


@st.composite
def subscription_plans(draw):
    """Generate a valid subscription plan."""
    plan = SubscriptionPlan(
        name=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")),
        description=draw(st.text(max_size=200))
    )

    # Add 1-3 features
    num_features = draw(st.integers(min_value=1, max_value=3))
    features = []
    for i in range(num_features):
        feature = plan.add_feature(
            name=f"Feature {i+1}",
            description=f"Test feature {i+1}",
            type="boolean"
        )
        features.append(feature)

    # Add 1-3 tiers
    num_tiers = draw(st.integers(min_value=1, max_value=3))
    tiers = []
    for i in range(num_tiers):
        tier = plan.add_tier(
            name=f"Tier {i+1}",
            description=f"Test tier {i+1}",
            price_monthly=draw(tier_prices),
            price_annual=draw(tier_prices) * 10  # Annual price typically lower than 12x monthly
        )

        # Add all features to this tier with random limits
        for feature in features:
            plan.add_feature_to_tier(
                tier["id"],
                feature["id"],
                value=True,
                limit=draw(st.integers(min_value=10, max_value=1000)) if draw(st.booleans()) else None
            )

        tiers.append(tier)

    return plan


@st.composite
def subscriptions(draw):
    """Generate a valid subscription with a plan and tier."""
    plan = draw(subscription_plans())

    # Ensure we have at least one tier
    assume(len(plan.tiers) > 0)

    tier = plan.tiers[0]
    user_id = draw(user_ids)
    start_date = draw(start_dates)
    billing_cycle = draw(billing_cycles)

    # Generate a random status with bias toward active
    status_options = [
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.ACTIVE,  # Make active more likely
        SubscriptionStatus.TRIAL,
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.CANCELED,
        SubscriptionStatus.EXPIRED
    ]

    # Create subscription
    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        tier_id=tier["id"],
        billing_cycle=billing_cycle,
        start_date=start_date
    )

    # If we want a non-active status, update it
    random_status = draw(st.sampled_from(status_options))
    if random_status != SubscriptionStatus.ACTIVE:
        subscription.status = random_status
        # Add a status history entry
        subscription.status_history.append({
            "status": random_status,
            "timestamp": datetime.now().isoformat(),
            "reason": f"Status changed to {random_status} for testing"
        })

    # Add some random metadata
    metadata_keys = ["source", "campaign", "referrer", "utm_medium", "coupon_code"]
    num_metadata = draw(st.integers(min_value=0, max_value=3))
    for _ in range(num_metadata):
        key = draw(st.sampled_from(metadata_keys))
        subscription.add_metadata(key, draw(st.text(min_size=1, max_size=20)))

    return subscription


@given(
    subscription_list=st.lists(subscriptions(), min_size=1, max_size=10)
)
def test_subscription_manager_properties(subscription_list):
    """Test properties of SubscriptionManager across a wide range of inputs."""

    # Create a SubscriptionManager instance with our generated subscriptions
    manager = SubscriptionManager()

    # Add all generated subscriptions to the manager
    for subscription in subscription_list:
        manager.add_subscription(subscription)

    # Property 1: The number of subscriptions in the manager should match what we added
    stored_subscriptions = manager.get_all_subscriptions()
    assert len(stored_subscriptions) == len(subscription_list)

    # Property 2: We should be able to retrieve any subscription by user_id
    for subscription in subscription_list:
        retrieved = manager.get_subscription_by_user(subscription.user_id)
        assert retrieved is not None
        assert retrieved.user_id == subscription.user_id
        assert retrieved.tier_id == subscription.tier_id
        assert retrieved.plan_id == subscription.plan_id

    # Property 3: Cancel operation should change subscription status to CANCELED
    # Pick the first subscription to cancel
    if subscription_list:
        test_sub = subscription_list[0]
        manager.cancel_subscription(test_sub.id)
        updated_sub = manager.get_subscription(test_sub.id)
        assert updated_sub is not None
        assert updated_sub.status == SubscriptionStatus.CANCELED or \
               updated_sub.get_metadata("cancel_at_period_end") == True

    # Property 4: Total active subscriptions should be less than or equal to total subscriptions
    active_count = len([s for s in manager.get_all_subscriptions() if s.is_active()])
    total_count = len(manager.get_all_subscriptions())
    assert active_count <= total_count


@given(
    subscription_list=st.lists(subscriptions(), min_size=1, max_size=10),
    days_forward=st.integers(min_value=1, max_value=400)
)
def test_renewal_properties(subscription_list, days_forward):
    """Test properties of subscription renewals across a wide range of inputs."""

    # Create a SubscriptionManager instance with our generated subscriptions
    manager = SubscriptionManager()

    # Add all generated subscriptions to the manager, but only consider active ones
    active_subscriptions = []
    for subscription in subscription_list:
        if subscription.status == SubscriptionStatus.ACTIVE:
            manager.add_subscription(subscription)
            active_subscriptions.append(subscription)

    # Skip the test if we don't have any active subscriptions
    assume(len(active_subscriptions) > 0)

    # Calculate a date in the future for renewal checks
    test_date = datetime.now() + timedelta(days=days_forward)

    # Collect subscriptions that should be renewed before test_date
    should_renew = []
    for sub in active_subscriptions:
        if sub.current_period_end <= test_date:
            should_renew.append(sub.id)

    # Process renewals as of the test date
    renewed = manager.process_renewals(test_date)

    # Property 1: The number of renewals should match our expectation
    assert len(renewed) == len(should_renew)

    # Property 2: Every subscription that should be renewed should be in the renewed list
    for sub_id in should_renew:
        assert sub_id in renewed

    # Property 3: For each renewed subscription, the next_period_end should be after test_date
    for sub_id in renewed:
        sub = manager.get_subscription(sub_id)
        assert sub.current_period_end > test_date


@given(
    subscription=subscriptions(),
    pause_days=st.integers(min_value=1, max_value=90)
)
def test_pause_resume_properties(subscription, pause_days):
    """Test properties of pausing and resuming subscriptions."""

    # Only test with active subscriptions
    assume(subscription.status == SubscriptionStatus.ACTIVE)

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Store the original next_billing_date
    original_next_billing = subscription.current_period_end

    # Pause the subscription
    manager.pause_subscription(subscription.id)
    paused_sub = manager.get_subscription(subscription.id)

    # Property 1: The subscription status should be PAUSED
    assert paused_sub.status == SubscriptionStatus.PAUSED

    # Property 2: The pause_collection flag should be True
    assert paused_sub.get_metadata("pause_collection") == True

    # Resume the subscription after pause_days
    resume_date = datetime.now() + timedelta(days=pause_days)
    manager.resume_subscription(subscription.id, resume_date=resume_date)
    resumed_sub = manager.get_subscription(subscription.id)

    # Property 3: The subscription status should be ACTIVE after resuming
    assert resumed_sub.status == SubscriptionStatus.ACTIVE

    # Property 4: The pause_collection flag should be False after resuming
    assert resumed_sub.get_metadata("pause_collection") == False

    # Property 5: The current_period_end should be adjusted to account for the pause
    # This is a complex calculation and varies by implementation, but we can check that
    # the new end date is later than the original one
    assert resumed_sub.current_period_end > original_next_billing


@given(
    subscription=subscriptions(),
    new_billing_cycle=st.sampled_from(['monthly', 'annual'])
)
def test_change_billing_cycle_properties(subscription, new_billing_cycle):
    """Test properties of changing billing cycles."""

    # Only test with active subscriptions and ensure we're changing to a different cycle
    assume(subscription.status == SubscriptionStatus.ACTIVE)
    assume(subscription.billing_cycle != new_billing_cycle)

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Store original values
    original_billing_cycle = subscription.billing_cycle
    original_price = subscription.price

    # Change billing cycle
    manager.change_billing_cycle(subscription.id, new_billing_cycle)
    updated_sub = manager.get_subscription(subscription.id)

    # Property 1: The billing cycle should be updated
    assert updated_sub.billing_cycle == new_billing_cycle

    # Property 2: The price should change according to the new billing cycle
    if new_billing_cycle == 'monthly':
        # Monthly price should be lower than annual
        if original_billing_cycle == 'annual':
            assert updated_sub.price < original_price
    else:  # annual
        # Annual price should be higher than monthly
        if original_billing_cycle == 'monthly':
            assert updated_sub.price > original_price

    # Property 3: The current_period_end should be adjusted according to the new billing cycle
    if new_billing_cycle == 'monthly':
        # A monthly period is shorter than an annual period
        assert (updated_sub.current_period_end - updated_sub.current_period_start).days <= 31
    else:  # annual
        # An annual period is longer than a monthly period
        assert (updated_sub.current_period_end - updated_sub.current_period_start).days >= 364


@given(
    subscription=subscriptions()
)
def test_feature_access_properties(subscription):
    """Test properties of feature access checks."""

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Get the tier and its features
    tier_features = subscription.get_features()

    # Property 1: The subscription should have access to all features in its tier
    for feature in tier_features:
        if feature.get("value") == True:  # Only check features that are enabled
            assert manager.has_feature_access(subscription.id, feature["name"]) == True

    # Property 2: Subscription should not have access to non-existent features
    assert manager.has_feature_access(subscription.id, "Non-existent Feature") == False

    # Property 3: Features with limits should respect those limits
    for feature in tier_features:
        if "limit" in feature and feature["limit"] is not None:
            # Check that the usage limit matches what's defined in the tier
            limit = manager.get_usage_limit(subscription.id, feature["name"])
            assert limit is not None
            assert limit == feature["limit"]

            # Test usage tracking
            # Reset usage first
            subscription.reset_feature_usage(feature["id"])
            assert subscription.get_feature_usage(feature["id"]) == 0

            # Increment usage to just under the limit
            subscription.increment_feature_usage(feature["id"], feature["limit"] - 1)
            assert subscription.is_feature_limit_reached(feature["id"]) == False

            # Increment once more to reach the limit
            subscription.increment_feature_usage(feature["id"], 1)
            assert subscription.is_feature_limit_reached(feature["id"]) == True


@given(
    subscription=subscriptions()
)
def test_subscription_state_transitions(subscription):
    """Test properties of subscription state transitions."""

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Property 1: Canceling an active subscription should make it canceled or
    # set cancel_at_period_end flag
    if subscription.status == SubscriptionStatus.ACTIVE:
        manager.cancel_subscription(subscription.id, cancel_at_period_end=True)
        updated_sub = manager.get_subscription(subscription.id)
        assert updated_sub.get_metadata("cancel_at_period_end") == True

        # If immediate cancellation instead of at period end
        manager.cancel_subscription(subscription.id, cancel_at_period_end=False)
        updated_sub = manager.get_subscription(subscription.id)
        assert updated_sub.status == SubscriptionStatus.CANCELED

    # Property 2: A canceled subscription can be reactivated
    if subscription.status == SubscriptionStatus.CANCELED:
        manager.reactivate_subscription(subscription.id)
        updated_sub = manager.get_subscription(subscription.id)
        assert updated_sub.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]

    # Property 3: Updating subscription status directly should work
    new_status = SubscriptionStatus.PAST_DUE
    manager.update_subscription_status(subscription.id, new_status, "Testing status change")
    updated_sub = manager.get_subscription(subscription.id)
    assert updated_sub.status == new_status

    # Property 4: Status history should be updated after status changes
    assert len(updated_sub.status_history) >= 2  # Initial + our change
    last_entry = updated_sub.status_history[-1]
    assert last_entry["status"] == new_status


@given(
    subscription=subscriptions()
)
def test_trial_expiration_properties(subscription):
    """Test properties of trial expirations."""
    # Force the subscription into trial mode
    subscription.status = SubscriptionStatus.TRIAL
    subscription.trial_end_date = datetime.now() - timedelta(days=1)  # Trial ended yesterday

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Check trial expirations
    updated_subscriptions = manager.check_trial_expirations()

    # Property 1: Our subscription should be in the updated list
    assert any(sub.id == subscription.id for sub in updated_subscriptions)

    # Property 2: The subscription should now be active, not trial
    updated_sub = manager.get_subscription(subscription.id)
    assert updated_sub.status == SubscriptionStatus.ACTIVE

    # Property 3: The status history should reflect the change
    last_entry = updated_sub.status_history[-1]
    assert last_entry["status"] == SubscriptionStatus.ACTIVE
    assert "trial" in last_entry["reason"].lower()


@given(
    subscription=subscriptions()
)
def test_tier_upgrade_downgrade_properties(subscription):
    """Test properties of upgrading and downgrading subscription tiers."""
    # Only test with active subscriptions and plans that have multiple tiers
    assume(subscription.status == SubscriptionStatus.ACTIVE)
    assume(len(subscription.plan.tiers) >= 2)

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Get current tier and an alternative tier
    current_tier_id = subscription.tier_id
    current_tier = subscription.get_tier()

    # Find another tier from the same plan
    other_tiers = [t for t in subscription.plan.tiers if t["id"] != current_tier_id]
    assume(len(other_tiers) > 0)

    # Find a higher priced tier for upgrade test
    upgrade_tier = None
    for tier in other_tiers:
        if tier["price_monthly"] > current_tier["price_monthly"]:
            upgrade_tier = tier
            break

    # If we found an upgrade tier, test upgrade
    if upgrade_tier:
        # Store original values
        original_price = subscription.price

        # Upgrade to the higher tier
        manager.change_subscription_tier(
            subscription_id=subscription.id,
            new_tier_id=upgrade_tier["id"],
            prorate=True
        )

        # Check the updated subscription
        upgraded_sub = manager.get_subscription(subscription.id)

        # Property 1: The tier ID should be updated
        assert upgraded_sub.tier_id == upgrade_tier["id"]

        # Property 2: The price should be higher after upgrading
        if subscription.billing_cycle == "monthly":
            assert upgraded_sub.price == upgrade_tier["price_monthly"]
        else:
            assert upgraded_sub.price == upgrade_tier["price_annual"]

        # Property 3: The status should still be ACTIVE
        assert upgraded_sub.status == SubscriptionStatus.ACTIVE

        # Property 4: There should be a record of the tier change in metadata
        tier_change = upgraded_sub.get_metadata("tier_change")
        assert tier_change is not None
        assert tier_change["old_tier_id"] == current_tier_id
        assert tier_change["new_tier_id"] == upgrade_tier["id"]

    # Find a lower priced tier for downgrade test
    downgrade_tier = None
    for tier in other_tiers:
        if tier["price_monthly"] < current_tier["price_monthly"]:
            downgrade_tier = tier
            break

    # If we found a downgrade tier, test downgrade
    if downgrade_tier:
        # Reset subscription to original tier if we did an upgrade
        if upgrade_tier:
            subscription.tier_id = current_tier_id
            # Update the manager's copy
            manager.add_subscription(subscription)

        # Store original values
        original_price = subscription.price

        # Downgrade to the lower tier
        manager.change_subscription_tier(
            subscription_id=subscription.id,
            new_tier_id=downgrade_tier["id"],
            prorate=True
        )

        # Check the updated subscription
        downgraded_sub = manager.get_subscription(subscription.id)

        # Property 1: The tier ID should be updated
        assert downgraded_sub.tier_id == downgrade_tier["id"]

        # Property 2: The price should be lower after downgrading
        if subscription.billing_cycle == "monthly":
            assert downgraded_sub.price == downgrade_tier["price_monthly"]
        else:
            assert downgraded_sub.price == downgrade_tier["price_annual"]

        # Property 3: The status should still be ACTIVE
        assert downgraded_sub.status == SubscriptionStatus.ACTIVE

        # Property 4: There should be a record of the tier change in metadata
        tier_change = downgraded_sub.get_metadata("tier_change")
        assert tier_change is not None
        assert tier_change["old_tier_id"] == current_tier_id
        assert tier_change["new_tier_id"] == downgrade_tier["id"]


@given(
    subscription=subscriptions(),
    proration_days=st.integers(min_value=1, max_value=29)
)
def test_subscription_proration_properties(subscription, proration_days):
    """Test properties of subscription proration when changing tiers or billing cycles."""
    # Only test with active monthly subscriptions
    assume(subscription.status == SubscriptionStatus.ACTIVE)
    assume(subscription.billing_cycle == "monthly")
    assume(len(subscription.plan.tiers) >= 2)

    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)

    # Set the current period to start from today and end in 30 days
    today = datetime.now()
    subscription.current_period_start = today
    subscription.current_period_end = today + timedelta(days=30)

    # Get current tier and find an upgrade tier
    current_tier_id = subscription.tier_id
    current_tier = subscription.get_tier()

    # Find a higher priced tier
    other_tiers = [t for t in subscription.plan.tiers if t["id"] != current_tier_id]
    upgrade_tier = None
    for tier in other_tiers:
        if tier["price_monthly"] > current_tier["price_monthly"]:
            upgrade_tier = tier
            break

    # Skip if we can't find an upgrade tier
    assume(upgrade_tier is not None)

    # Set the effective date to be partway through the billing cycle
    effective_date = today + timedelta(days=proration_days)

    # Test proration when upgrading
    manager.change_subscription_tier(
        subscription_id=subscription.id,
        new_tier_id=upgrade_tier["id"],
        prorate=True,
        effective_date=effective_date
    )

    # Check the updated subscription
    upgraded_sub = manager.get_subscription(subscription.id)

    # Property 1: The tier should be changed
    assert upgraded_sub.tier_id == upgrade_tier["id"]

    # Property 2: There should be proration data in the metadata
    tier_change = upgraded_sub.get_metadata("tier_change")
    assert tier_change is not None
    assert "prorated_amount" in tier_change

    # Property 3: The prorated amount should be greater than 0 for an upgrade
    assert tier_change["prorated_amount"] > 0

    # Property 4: For a partial period, the prorated amount should be less than
    # the full price difference
    price_difference = upgrade_tier["price_monthly"] - current_tier["price_monthly"]
    days_left = 30 - proration_days
    expected_proration = price_difference * (days_left / 30)
    assert abs(tier_change["prorated_amount"] - expected_proration) < 0.01


@given(
    subscription_list=st.lists(subscriptions(), min_size=2, max_size=10)
)
def test_subscription_batch_operations_properties(subscription_list):
    """Test properties of batch operations on subscriptions."""

    # Create a SubscriptionManager instance with our generated subscriptions
    manager = SubscriptionManager()

    # Add all generated subscriptions to the manager, filtering for active ones
    active_subscriptions = []
    for subscription in subscription_list:
        if subscription.status == SubscriptionStatus.ACTIVE:
            manager.add_subscription(subscription)
            active_subscriptions.append(subscription)

    # Skip test if we don't have at least 2 active subscriptions
    assume(len(active_subscriptions) >= 2)

    # Test batch processing of expirations
    # First, set some subscriptions to expire today
    expiring_ids = []
    for i, sub in enumerate(active_subscriptions):
        if i % 2 == 0:  # Every other subscription
            sub.current_period_end = datetime.now() - timedelta(days=1)
            expiring_ids.append(sub.id)
            # Update the manager's copy
            manager.add_subscription(sub)

    # Process expirations
    processed_subs = manager.check_period_expirations()

    # Property 1: The number of processed subscriptions should match our expiring ones
    assert len(processed_subs) == len(expiring_ids)

    # Property 2: All IDs should match what we expected
    processed_ids = [s.id for s in processed_subs]
    for sub_id in expiring_ids:
        assert sub_id in processed_ids

    # Property 3: Batch processing should update all subscriptions properly
    for sub_id in expiring_ids:
        updated_sub = manager.get_subscription(sub_id)
        # Either the subscription was renewed or canceled
        if updated_sub.get_metadata("cancel_at_period_end", False):
            assert updated_sub.status == SubscriptionStatus.CANCELED
        else:
            # If it was renewed, the period end date should be in the future
            assert updated_sub.current_period_end > datetime.now()


# Helper method to add a subscription to the manager
def add_subscription(manager, plan):
    """Helper to add a subscription to the manager."""
    # Ensure we have at least one tier
    assume(len(plan.tiers) > 0)

    # Create and add subscription
    sub = Subscription(
        user_id="test_user",
        plan=plan,
        tier_id=plan.tiers[0]["id"],
        billing_cycle="monthly"
    )
    manager.add_subscription(sub)
    return sub