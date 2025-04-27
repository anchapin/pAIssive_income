"""
Property-based tests for the subscription management logic.

These tests verify that subscription management operations work correctly
across a wide range of input parameters.
"""
import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, example, assume
from monetization.subscription_manager import SubscriptionManager
from monetization.subscription_models import Subscription, SubscriptionTier, SubscriptionStatus


# Strategies for generating subscription data
user_ids = st.integers(min_value=1, max_value=10000)
tier_names = st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")
tier_prices = st.decimals(min_value=0.01, max_value=999.99, places=2)
billing_cycles = st.sampled_from(['monthly', 'quarterly', 'yearly'])
start_dates = st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 1, 1))


@st.composite
def subscription_tiers(draw):
    """Generate a valid subscription tier."""
    name = draw(tier_names)
    price = draw(tier_prices)
    features = draw(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5))
    
    return SubscriptionTier(
        name=name,
        price=float(price),
        features=features
    )


@st.composite
def subscriptions(draw):
    """Generate a valid subscription."""
    user_id = draw(user_ids)
    tier = draw(subscription_tiers())
    start_date = draw(start_dates)
    billing_cycle = draw(billing_cycles)
    
    # Generate a random status with bias toward active
    status = draw(st.sampled_from([
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.ACTIVE,  # Make active more likely
        SubscriptionStatus.PAUSED,
        SubscriptionStatus.CANCELLED
    ]))
    
    # Generate next billing date based on start date and billing cycle
    days_to_add = 30  # Default for monthly
    if billing_cycle == 'quarterly':
        days_to_add = 90
    elif billing_cycle == 'yearly':
        days_to_add = 365
    
    next_billing_date = start_date + timedelta(days=days_to_add)
    
    return Subscription(
        user_id=user_id,
        tier=tier,
        start_date=start_date,
        status=status,
        billing_cycle=billing_cycle,
        next_billing_date=next_billing_date
    )


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
        assert retrieved.tier.name == subscription.tier.name
        assert abs(retrieved.tier.price - subscription.tier.price) < 0.01  # Compare with small epsilon for float comparison
    
    # Property 3: Cancel operation should change subscription status to CANCELLED
    # Pick the first subscription to cancel
    if subscription_list:
        test_sub = subscription_list[0]
        manager.cancel_subscription(test_sub.user_id)
        updated_sub = manager.get_subscription_by_user(test_sub.user_id)
        assert updated_sub is not None
        assert updated_sub.status == SubscriptionStatus.CANCELLED
    
    # Property 4: Total active subscriptions should be less than or equal to total subscriptions
    active_count = manager.get_active_subscription_count()
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
        if sub.next_billing_date <= test_date:
            should_renew.append(sub.user_id)
    
    # Process renewals
    renewed = manager.process_renewals(test_date)
    
    # Property 1: The number of renewals should match our expectation
    assert len(renewed) == len(should_renew)
    
    # Property 2: Every subscription that should be renewed should be in the renewed list
    for user_id in should_renew:
        assert user_id in renewed
    
    # Property 3: For each renewed subscription, the next_billing_date should be updated
    for user_id in renewed:
        sub = manager.get_subscription_by_user(user_id)
        assert sub.next_billing_date > test_date


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
    original_next_billing = subscription.next_billing_date
    
    # Pause the subscription
    manager.pause_subscription(subscription.user_id)
    paused_sub = manager.get_subscription_by_user(subscription.user_id)
    
    # Property 1: The subscription status should be PAUSED
    assert paused_sub.status == SubscriptionStatus.PAUSED
    
    # Property 2: The next_billing_date should remain unchanged when paused
    assert paused_sub.next_billing_date == original_next_billing
    
    # Resume the subscription
    manager.resume_subscription(subscription.user_id)
    resumed_sub = manager.get_subscription_by_user(subscription.user_id)
    
    # Property 3: The subscription status should be back to ACTIVE
    assert resumed_sub.status == SubscriptionStatus.ACTIVE
    
    # Property 4: The next_billing_date should be extended by the number of days paused
    # (In a real implementation, we would typically track pause time)
    # Here we simulate passing of time during the pause
    test_date = datetime.now() + timedelta(days=pause_days)
    manager.resume_subscription(subscription.user_id, pause_duration_days=pause_days)
    extended_sub = manager.get_subscription_by_user(subscription.user_id)
    
    # Expected billing date should be extended by pause_days
    expected_next_billing = original_next_billing + timedelta(days=pause_days)
    
    # Allow for small differences in datetime calculations
    difference = abs((extended_sub.next_billing_date - expected_next_billing).total_seconds())
    assert difference < 60  # Allow up to 60 seconds difference


@given(
    subscription=subscriptions(),
    new_tier=subscription_tiers()
)
def test_tier_upgrade_properties(subscription, new_tier):
    """Test properties of upgrading subscription tiers."""
    
    # Only test with active subscriptions
    assume(subscription.status == SubscriptionStatus.ACTIVE)
    
    # Make sure the new tier is different and has a higher price
    assume(subscription.tier.name != new_tier.name)
    assume(new_tier.price > subscription.tier.price)
    
    # Create a SubscriptionManager instance with our generated subscription
    manager = SubscriptionManager()
    manager.add_subscription(subscription)
    
    # Upgrade the tier
    manager.change_subscription_tier(subscription.user_id, new_tier)
    upgraded_sub = manager.get_subscription_by_user(subscription.user_id)
    
    # Property 1: The subscription should have the new tier
    assert upgraded_sub.tier.name == new_tier.name
    assert upgraded_sub.tier.price == new_tier.price
    
    # Property 2: The subscription status should remain ACTIVE
    assert upgraded_sub.status == SubscriptionStatus.ACTIVE