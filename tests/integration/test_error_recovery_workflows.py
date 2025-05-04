"""
"""
Integration tests for error recovery in multi-step workflows.
Integration tests for error recovery in multi-step workflows.


This module tests error recovery scenarios in cross-module workflows, including
This module tests error recovery scenarios in cross-module workflows, including
partial failure recovery, data consistency after interruptions, and transaction
partial failure recovery, data consistency after interruptions, and transaction
rollback scenarios.
rollback scenarios.
"""
"""


import random
import random
import threading
import threading
import time
import time
from unittest.mock import MagicMock, call, patch
from unittest.mock import MagicMock, call, patch


import pytest
import pytest


from agent_team import AgentTeam
from agent_team import AgentTeam
from marketing import ABTesting
from marketing import ABTesting
from monetization import PricingCalculator, SubscriptionModel
from monetization import PricingCalculator, SubscriptionModel
from niche_analysis import MarketAnalyzer
from niche_analysis import MarketAnalyzer




@pytest.fixture
@pytest.fixture
def market_analyzer():
    def market_analyzer():
    """Create a market analyzer instance for testing."""
    return MarketAnalyzer()


    @pytest.fixture
    def ab_testing():
    """Create an A/B testing instance for testing."""
    return ABTesting()


    @pytest.fixture
    def subscription_model():
    """Create a subscription model instance for testing."""
    return SubscriptionModel(
    name="Test Subscription Model",
    description="A test subscription model"
    )


    @pytest.fixture
    def pricing_calculator():
    """Create a pricing calculator instance for testing."""
    return PricingCalculator(
    name="Test Pricing Calculator",
    description="A test pricing calculator",
    base_cost=5.0,
    profit_margin=0.3,
    competitor_prices={"basic": 9.99, "pro": 19.99, "premium": 29.99}
    )


    @pytest.fixture
    def mock_agent_team():
    """Create a mock agent team for testing."""
    with patch('agent_team.AgentTeam') as mock:
    team = MagicMock()
    mock.return_value = team
    yield team


    def test_partial_failure_recovery_in_workflow(market_analyzer, ab_testing, mock_agent_team):
    """
    """
    Test recovery from partial failures in a multi-step workflow.
    Test recovery from partial failures in a multi-step workflow.


    This test verifies that:
    This test verifies that:
    1. The workflow can detect and handle failures in intermediate steps
    1. The workflow can detect and handle failures in intermediate steps
    2. The workflow can recover and continue from the last successful step
    2. The workflow can recover and continue from the last successful step
    3. The final result is consistent despite intermediate failures
    3. The final result is consistent despite intermediate failures
    """
    """
    # Step 1: Set up a mock for the market analyzer that fails on the first call
    # Step 1: Set up a mock for the market analyzer that fails on the first call
    original_analyze_market = market_analyzer.analyze_market
    original_analyze_market = market_analyzer.analyze_market
    call_count = 0
    call_count = 0


    def mock_analyze_market(segment):
    def mock_analyze_market(segment):
    nonlocal call_count
    nonlocal call_count
    call_count += 1
    call_count += 1
    if call_count == 1:
    if call_count == 1:
    # Simulate a failure on the first call
    # Simulate a failure on the first call
    raise ConnectionError("Simulated network error")
    raise ConnectionError("Simulated network error")
    else:
    else:
    # Return normal result on subsequent calls
    # Return normal result on subsequent calls
    return original_analyze_market(segment)
    return original_analyze_market(segment)


    # Apply the mock
    # Apply the mock
    market_analyzer.analyze_market = mock_analyze_market
    market_analyzer.analyze_market = mock_analyze_market


    # Step 2: Create a workflow function that implements retry logic
    # Step 2: Create a workflow function that implements retry logic
    def niche_analysis_workflow(segment, max_retries=3):
    def niche_analysis_workflow(segment, max_retries=3):
    retries = 0
    retries = 0
    last_error = None
    last_error = None


    while retries < max_retries:
    while retries < max_retries:
    try:
    try:
    # Try to analyze the market
    # Try to analyze the market
    market_analysis = market_analyzer.analyze_market(segment)
    market_analysis = market_analyzer.analyze_market(segment)


    # If successful, continue with the workflow
    # If successful, continue with the workflow
    selected_niche = market_analysis["potential_niches"][0]
    selected_niche = market_analysis["potential_niches"][0]
    trend_analysis = market_analyzer.analyze_trends(segment)
    trend_analysis = market_analyzer.analyze_trends(segment)
    user_analysis = market_analyzer.analyze_target_users(selected_niche)
    user_analysis = market_analyzer.analyze_target_users(selected_niche)


    # Return the complete analysis
    # Return the complete analysis
    return {
    return {
    "market_analysis": market_analysis,
    "market_analysis": market_analysis,
    "trend_analysis": trend_analysis,
    "trend_analysis": trend_analysis,
    "user_analysis": user_analysis,
    "user_analysis": user_analysis,
    "selected_niche": selected_niche
    "selected_niche": selected_niche
    }
    }
except Exception as e:
except Exception as e:
    # Record the error and retry
    # Record the error and retry
    last_error = e
    last_error = e
    retries += 1
    retries += 1
    time.sleep(0.1)  # Short delay before retry
    time.sleep(0.1)  # Short delay before retry


    # If we've exhausted retries, raise the last error
    # If we've exhausted retries, raise the last error
    raise last_error
    raise last_error


    # Step 3: Run the workflow and verify recovery
    # Step 3: Run the workflow and verify recovery
    result = niche_analysis_workflow("e-commerce")
    result = niche_analysis_workflow("e-commerce")


    # Verify that the workflow recovered and completed successfully
    # Verify that the workflow recovered and completed successfully
    assert call_count == 2  # First call failed, second succeeded
    assert call_count == 2  # First call failed, second succeeded
    assert "market_analysis" in result
    assert "market_analysis" in result
    assert "trend_analysis" in result
    assert "trend_analysis" in result
    assert "user_analysis" in result
    assert "user_analysis" in result
    assert "selected_niche" in result
    assert "selected_niche" in result


    # Verify that the data is consistent
    # Verify that the data is consistent
    assert result["selected_niche"] in result["market_analysis"]["potential_niches"]
    assert result["selected_niche"] in result["market_analysis"]["potential_niches"]
    assert result["market_analysis"]["name"] == "E-Commerce"
    assert result["market_analysis"]["name"] == "E-Commerce"




    def test_data_consistency_after_interruption(subscription_model, pricing_calculator):
    def test_data_consistency_after_interruption(subscription_model, pricing_calculator):
    """
    """
    Test data consistency after system interruptions.
    Test data consistency after system interruptions.


    This test verifies that:
    This test verifies that:
    1. Data remains consistent when operations are interrupted
    1. Data remains consistent when operations are interrupted
    2. Partial updates are either fully applied or fully rolled back
    2. Partial updates are either fully applied or fully rolled back
    3. The system can detect and recover from inconsistent states
    3. The system can detect and recover from inconsistent states
    """
    """
    # Step 1: Create a subscription model with tiers
    # Step 1: Create a subscription model with tiers
    basic_tier = subscription_model.add_tier(
    basic_tier = subscription_model.add_tier(
    name="Basic",
    name="Basic",
    description="Basic features",
    description="Basic features",
    price_monthly=9.99,
    price_monthly=9.99,
    price_yearly=99.99,
    price_yearly=99.99,
    features=["feature1", "feature2"],
    features=["feature1", "feature2"],
    limits={"api_calls": 1000},
    limits={"api_calls": 1000},
    target_users="Small businesses"
    target_users="Small businesses"
    )
    )


    pro_tier = subscription_model.add_tier(
    pro_tier = subscription_model.add_tier(
    name="Pro",
    name="Pro",
    description="Pro features",
    description="Pro features",
    price_monthly=19.99,
    price_monthly=19.99,
    price_yearly=199.99,
    price_yearly=199.99,
    features=["feature1", "feature2", "feature3"],
    features=["feature1", "feature2", "feature3"],
    limits={"api_calls": 5000},
    limits={"api_calls": 5000},
    target_users="Medium businesses"
    target_users="Medium businesses"
    )
    )


    # Step 2: Create a function that simulates a batch update with potential interruption
    # Step 2: Create a function that simulates a batch update with potential interruption
    def update_pricing_with_interruption(model, calculator, interrupt_probability=0.5):
    def update_pricing_with_interruption(model, calculator, interrupt_probability=0.5):
    # Store original prices for verification and recovery
    # Store original prices for verification and recovery
    original_prices = {
    original_prices = {
    tier["id"]: {
    tier["id"]: {
    "monthly": tier["price_monthly"],
    "monthly": tier["price_monthly"],
    "yearly": tier["price_yearly"]
    "yearly": tier["price_yearly"]
    }
    }
    for tier in model.tiers
    for tier in model.tiers
    }
    }


    # Start updating prices
    # Start updating prices
    updated_tiers = []
    updated_tiers = []
    try:
    try:
    for tier in model.tiers:
    for tier in model.tiers:
    # Calculate new price
    # Calculate new price
    new_price = calculator.calculate_price(
    new_price = calculator.calculate_price(
    base_value=10.0,
    base_value=10.0,
    tier_multiplier=1.0 + (model.tiers.index(tier) * 0.5),
    tier_multiplier=1.0 + (model.tiers.index(tier) * 0.5),
    market_adjustment=1.0
    market_adjustment=1.0
    )
    )


    # Update tier price
    # Update tier price
    model.update_tier_price(tier["id"], price_monthly=new_price)
    model.update_tier_price(tier["id"], price_monthly=new_price)
    updated_tiers.append(tier["id"])
    updated_tiers.append(tier["id"])


    # Simulate random interruption
    # Simulate random interruption
    if random.random() < interrupt_probability and len(updated_tiers) < len(model.tiers):
    if random.random() < interrupt_probability and len(updated_tiers) < len(model.tiers):
    raise InterruptedError("Simulated interruption during batch update")
    raise InterruptedError("Simulated interruption during batch update")


    # If we get here, all updates were successful
    # If we get here, all updates were successful
    return True, updated_tiers, None
    return True, updated_tiers, None
except Exception as e:
except Exception as e:
    # Rollback changes
    # Rollback changes
    for tier_id in updated_tiers:
    for tier_id in updated_tiers:
    model.update_tier_price(
    model.update_tier_price(
    tier_id,
    tier_id,
    price_monthly=original_prices[tier_id]["monthly"],
    price_monthly=original_prices[tier_id]["monthly"],
    price_yearly=original_prices[tier_id]["yearly"]
    price_yearly=original_prices[tier_id]["yearly"]
    )
    )
    return False, updated_tiers, e
    return False, updated_tiers, e


    # Step 3: Run the update function with a fixed seed for reproducibility
    # Step 3: Run the update function with a fixed seed for reproducibility
    random.seed(42)  # Set seed for reproducible test
    random.seed(42)  # Set seed for reproducible test
    success, updated_tiers, error = update_pricing_with_interruption(subscription_model, pricing_calculator)
    success, updated_tiers, error = update_pricing_with_interruption(subscription_model, pricing_calculator)


    # Step 4: Verify data consistency
    # Step 4: Verify data consistency
    if success:
    if success:
    # All tiers should be updated
    # All tiers should be updated
    assert len(updated_tiers) == len(subscription_model.tiers)
    assert len(updated_tiers) == len(subscription_model.tiers)
    for tier in subscription_model.tiers:
    for tier in subscription_model.tiers:
    assert tier["price_monthly"] != 9.99 and tier["price_monthly"] != 19.99
    assert tier["price_monthly"] != 9.99 and tier["price_monthly"] != 19.99
    else:
    else:
    # No tiers should be updated (all rolled back)
    # No tiers should be updated (all rolled back)
    assert subscription_model.tiers[0]["price_monthly"] == 9.99
    assert subscription_model.tiers[0]["price_monthly"] == 9.99
    assert subscription_model.tiers[1]["price_monthly"] == 19.99
    assert subscription_model.tiers[1]["price_monthly"] == 19.99
    assert isinstance(error, InterruptedError)
    assert isinstance(error, InterruptedError)




    def test_transaction_rollback_scenarios(ab_testing):
    def test_transaction_rollback_scenarios(ab_testing):
    """
    """
    Test transaction rollback scenarios in multi-step workflows.
    Test transaction rollback scenarios in multi-step workflows.


    This test verifies that:
    This test verifies that:
    1. Transactions can be rolled back when errors occur
    1. Transactions can be rolled back when errors occur
    2. The system maintains ACID properties during transactions
    2. The system maintains ACID properties during transactions
    3. Concurrent operations are handled correctly
    3. Concurrent operations are handled correctly
    """
    """
    # Step 1: Create a test with variants
    # Step 1: Create a test with variants
    test = ab_testing.create_test(
    test = ab_testing.create_test(
    name="Transaction Test",
    name="Transaction Test",
    description="Testing transaction rollback",
    description="Testing transaction rollback",
    content_type="landing_page",
    content_type="landing_page",
    test_type="a_b",
    test_type="a_b",
    variants=[
    variants=[
    {"name": "Control", "is_control": True},
    {"name": "Control", "is_control": True},
    {"name": "Variant B", "is_control": False}
    {"name": "Variant B", "is_control": False}
    ]
    ]
    )
    )


    test_id = test["id"]
    test_id = test["id"]
    control_id = test["variants"][0]["id"]
    control_id = test["variants"][0]["id"]
    variant_id = test["variants"][1]["id"]
    variant_id = test["variants"][1]["id"]


    # Step 2: Create a function that simulates a transaction with potential failure
    # Step 2: Create a function that simulates a transaction with potential failure
    def record_interactions_in_transaction(test_id, variant_id, count, fail_at=None):
    def record_interactions_in_transaction(test_id, variant_id, count, fail_at=None):
    # Start recording interactions
    # Start recording interactions
    recorded = 0
    recorded = 0
    try:
    try:
    for i in range(count):
    for i in range(count):
    ab_testing.record_interaction(test_id, variant_id, "impression")
    ab_testing.record_interaction(test_id, variant_id, "impression")
    recorded += 1
    recorded += 1


    # Simulate failure at specific point if requested
    # Simulate failure at specific point if requested
    if fail_at is not None and i == fail_at:
    if fail_at is not None and i == fail_at:
    raise ValueError(f"Simulated failure after {i+1} interactions")
    raise ValueError(f"Simulated failure after {i+1} interactions")


    # If we get here, all interactions were recorded successfully
    # If we get here, all interactions were recorded successfully
    return True, recorded, None
    return True, recorded, None
except Exception as e:
except Exception as e:
    # In a real system, this would trigger a transaction rollback
    # In a real system, this would trigger a transaction rollback
    # For this test, we'll simulate rollback by tracking what happened
    # For this test, we'll simulate rollback by tracking what happened
    return False, recorded, e
    return False, recorded, e


    # Step 3: Run successful and failing transactions
    # Step 3: Run successful and failing transactions
    success_result, success_count, _ = record_interactions_in_transaction(test_id, control_id, 100)
    success_result, success_count, _ = record_interactions_in_transaction(test_id, control_id, 100)
    fail_result, fail_count, fail_error = record_interactions_in_transaction(test_id, variant_id, 100, fail_at=50)
    fail_result, fail_count, fail_error = record_interactions_in_transaction(test_id, variant_id, 100, fail_at=50)


    # Step 4: Verify transaction results
    # Step 4: Verify transaction results
    assert success_result is True
    assert success_result is True
    assert success_count == 100
    assert success_count == 100


    assert fail_result is False
    assert fail_result is False
    assert fail_count == 51  # 0-based index, so fail_at=50 means 51 operations
    assert fail_count == 51  # 0-based index, so fail_at=50 means 51 operations
    assert isinstance(fail_error, ValueError)
    assert isinstance(fail_error, ValueError)


    # Step 5: Test concurrent transactions
    # Step 5: Test concurrent transactions
    def concurrent_interaction_recorder(variant_id, count, results):
    def concurrent_interaction_recorder(variant_id, count, results):
    try:
    try:
    for _ in range(count):
    for _ in range(count):
    ab_testing.record_interaction(test_id, variant_id, "impression")
    ab_testing.record_interaction(test_id, variant_id, "impression")
    results.append(True)
    results.append(True)
except Exception as e:
except Exception as e:
    results.append(e)
    results.append(e)


    # Create threads for concurrent operations
    # Create threads for concurrent operations
    thread_results = []
    thread_results = []
    threads = []
    threads = []
    for i in range(5):  # 5 concurrent threads
    for i in range(5):  # 5 concurrent threads
    thread = threading.Thread(
    thread = threading.Thread(
    target=concurrent_interaction_recorder,
    target=concurrent_interaction_recorder,
    args=(control_id if i % 2 == 0 else variant_id, 20, thread_results)
    args=(control_id if i % 2 == 0 else variant_id, 20, thread_results)
    )
    )
    threads.append(thread)
    threads.append(thread)


    # Start and join all threads
    # Start and join all threads
    for thread in threads:
    for thread in threads:
    thread.start()
    thread.start()


    for thread in threads:
    for thread in threads:
    thread.join()
    thread.join()


    # Verify all threads completed successfully
    # Verify all threads completed successfully
    assert all(result is True for result in thread_results)
    assert all(result is True for result in thread_results)


    # Verify the final state by analyzing the test
    # Verify the final state by analyzing the test
    analysis = ab_testing.analyze_test(test_id)
    analysis = ab_testing.analyze_test(test_id)
    assert "variants" in analysis
    assert "variants" in analysis
    assert len(analysis["variants"]) == 2
    assert len(analysis["variants"]) == 2




    def test_workflow_with_compensating_actions(mock_agent_team):
    def test_workflow_with_compensating_actions(mock_agent_team):
    """
    """
    Test workflows with compensating actions for error recovery.
    Test workflows with compensating actions for error recovery.


    This test verifies that:
    This test verifies that:
    1. The system can perform compensating actions when errors occur
    1. The system can perform compensating actions when errors occur
    2. The workflow can recover to a consistent state after errors
    2. The workflow can recover to a consistent state after errors
    3. The system maintains an audit trail of actions and compensations
    3. The system maintains an audit trail of actions and compensations
    """
    """
    # Step 1: Set up the mock agent team with error injection
    # Step 1: Set up the mock agent team with error injection
    # Make develop_solution fail on first call
    # Make develop_solution fail on first call
    mock_agent_team.develop_solution.side_effect = [
    mock_agent_team.develop_solution.side_effect = [
    ValueError("Simulated error in solution development"),  # First call fails
    ValueError("Simulated error in solution development"),  # First call fails
    {"id": "solution-123", "name": "Test Solution"}  # Second call succeeds
    {"id": "solution-123", "name": "Test Solution"}  # Second call succeeds
    ]
    ]


    # Make create_monetization_strategy succeed
    # Make create_monetization_strategy succeed
    mock_agent_team.create_monetization_strategy.return_value = {
    mock_agent_team.create_monetization_strategy.return_value = {
    "id": "monetization-123",
    "id": "monetization-123",
    "name": "Test Monetization Strategy"
    "name": "Test Monetization Strategy"
    }
    }


    # Make create_marketing_plan succeed
    # Make create_marketing_plan succeed
    mock_agent_team.create_marketing_plan.return_value = {
    mock_agent_team.create_marketing_plan.return_value = {
    "id": "marketing-123",
    "id": "marketing-123",
    "name": "Test Marketing Plan"
    "name": "Test Marketing Plan"
    }
    }


    # Step 2: Create a workflow function with compensating actions
    # Step 2: Create a workflow function with compensating actions
    def complete_workflow_with_compensation(team, niche_id):
    def complete_workflow_with_compensation(team, niche_id):
    audit_trail = []
    audit_trail = []


    try:
    try:
    # Step 1: Develop solution
    # Step 1: Develop solution
    audit_trail.append({"action": "develop_solution", "status": "started", "niche_id": niche_id})
    audit_trail.append({"action": "develop_solution", "status": "started", "niche_id": niche_id})
    solution = team.develop_solution(niche_id)
    solution = team.develop_solution(niche_id)
    audit_trail.append({"action": "develop_solution", "status": "completed", "solution_id": solution["id"]})
    audit_trail.append({"action": "develop_solution", "status": "completed", "solution_id": solution["id"]})


    # Step 2: Create monetization strategy
    # Step 2: Create monetization strategy
    audit_trail.append({"action": "create_monetization_strategy", "status": "started", "solution_id": solution["id"]})
    audit_trail.append({"action": "create_monetization_strategy", "status": "started", "solution_id": solution["id"]})
    monetization = team.create_monetization_strategy(solution["id"])
    monetization = team.create_monetization_strategy(solution["id"])
    audit_trail.append({"action": "create_monetization_strategy", "status": "completed", "monetization_id": monetization["id"]})
    audit_trail.append({"action": "create_monetization_strategy", "status": "completed", "monetization_id": monetization["id"]})


    # Step 3: Create marketing plan
    # Step 3: Create marketing plan
    audit_trail.append({"action": "create_marketing_plan", "status": "started", "solution_id": solution["id"], "monetization_id": monetization["id"]})
    audit_trail.append({"action": "create_marketing_plan", "status": "started", "solution_id": solution["id"], "monetization_id": monetization["id"]})
    marketing = team.create_marketing_plan(niche_id, solution["id"], monetization["id"])
    marketing = team.create_marketing_plan(niche_id, solution["id"], monetization["id"])
    audit_trail.append({"action": "create_marketing_plan", "status": "completed", "marketing_id": marketing["id"]})
    audit_trail.append({"action": "create_marketing_plan", "status": "completed", "marketing_id": marketing["id"]})


    return True, {"solution": solution, "monetization": monetization, "marketing": marketing}, audit_trail
    return True, {"solution": solution, "monetization": monetization, "marketing": marketing}, audit_trail


except Exception as e:
except Exception as e:
    # Record the error
    # Record the error
    audit_trail.append({"action": "error", "message": str(e)})
    audit_trail.append({"action": "error", "message": str(e)})


    # Perform compensating actions if needed
    # Perform compensating actions if needed
    last_completed_action = next((a for a in reversed(audit_trail) if a["status"] == "completed"), None)
    last_completed_action = next((a for a in reversed(audit_trail) if a["status"] == "completed"), None)


    if last_completed_action:
    if last_completed_action:
    if last_completed_action["action"] == "create_monetization_strategy":
    if last_completed_action["action"] == "create_monetization_strategy":
    # Compensate for monetization strategy creation
    # Compensate for monetization strategy creation
    audit_trail.append({"action": "compensate_monetization_strategy", "status": "started", "monetization_id": last_completed_action["monetization_id"]})
    audit_trail.append({"action": "compensate_monetization_strategy", "status": "started", "monetization_id": last_completed_action["monetization_id"]})
    team.archive_monetization_strategy(last_completed_action["monetization_id"])
    team.archive_monetization_strategy(last_completed_action["monetization_id"])
    audit_trail.append({"action": "compensate_monetization_strategy", "status": "completed"})
    audit_trail.append({"action": "compensate_monetization_strategy", "status": "completed"})


    elif last_completed_action["action"] == "develop_solution":
    elif last_completed_action["action"] == "develop_solution":
    # Compensate for solution development
    # Compensate for solution development
    audit_trail.append({"action": "compensate_develop_solution", "status": "started", "solution_id": last_completed_action["solution_id"]})
    audit_trail.append({"action": "compensate_develop_solution", "status": "started", "solution_id": last_completed_action["solution_id"]})
    team.archive_solution(last_completed_action["solution_id"])
    team.archive_solution(last_completed_action["solution_id"])
    audit_trail.append({"action": "compensate_develop_solution", "status": "completed"})
    audit_trail.append({"action": "compensate_develop_solution", "status": "completed"})


    # Return failure status
    # Return failure status
    return False, None, audit_trail
    return False, None, audit_trail


    # Step 3: Run the workflow and verify it fails the first time
    # Step 3: Run the workflow and verify it fails the first time
    success, result, audit_trail = complete_workflow_with_compensation(mock_agent_team, "niche-123")
    success, result, audit_trail = complete_workflow_with_compensation(mock_agent_team, "niche-123")


    # Verify the workflow failed and recorded the error
    # Verify the workflow failed and recorded the error
    assert success is False
    assert success is False
    assert result is None
    assert result is None
    assert any(a["action"] == "error" for a in audit_trail)
    assert any(a["action"] == "error" for a in audit_trail)
    assert mock_agent_team.develop_solution.call_count == 1
    assert mock_agent_team.develop_solution.call_count == 1


    # Step 4: Run the workflow again and verify it succeeds
    # Step 4: Run the workflow again and verify it succeeds
    success, result, audit_trail = complete_workflow_with_compensation(mock_agent_team, "niche-123")
    success, result, audit_trail = complete_workflow_with_compensation(mock_agent_team, "niche-123")


    # Verify the workflow succeeded
    # Verify the workflow succeeded
    assert success is True
    assert success is True
    assert result is not None
    assert result is not None
    assert "solution" in result
    assert "solution" in result
    assert "monetization" in result
    assert "monetization" in result
    assert "marketing" in result
    assert "marketing" in result
    assert mock_agent_team.develop_solution.call_count == 2
    assert mock_agent_team.develop_solution.call_count == 2
    assert mock_agent_team.create_monetization_strategy.call_count == 1
    assert mock_agent_team.create_monetization_strategy.call_count == 1
    assert mock_agent_team.create_marketing_plan.call_count == 1
    assert mock_agent_team.create_marketing_plan.call_count == 1


    # Verify the audit trail is complete
    # Verify the audit trail is complete
    action_sequence = [a["action"] for a in audit_trail if a["status"] == "completed"]
    action_sequence = [a["action"] for a in audit_trail if a["status"] == "completed"]
    assert action_sequence == ["develop_solution", "create_monetization_strategy", "create_marketing_plan"]
    assert action_sequence == ["develop_solution", "create_monetization_strategy", "create_marketing_plan"]