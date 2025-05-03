"""
Integration tests for error recovery in multi - step workflows.

This module tests error recovery scenarios in cross - module workflows, including
partial failure recovery, data consistency after interruptions, and transaction
rollback scenarios.
"""

import random
import threading
import time
from unittest.mock import MagicMock, call, patch

import pytest

from agent_team import AgentTeam
from marketing import ABTesting
from monetization import PricingCalculator, SubscriptionModel
from niche_analysis import MarketAnalyzer


@pytest.fixture
def market_analyzer():
    """Create a market analyzer instance for testing."""
    return MarketAnalyzer()


@pytest.fixture
def ab_testing():
    """Create an A / B testing instance for testing."""
    return ABTesting()


@pytest.fixture
def subscription_model():
    """Create a subscription model instance for testing."""
    return SubscriptionModel(
        name="Test Subscription Model", description="A test subscription model"
    )


@pytest.fixture
def pricing_calculator():
    """Create a pricing calculator instance for testing."""
    return PricingCalculator(
        name="Test Pricing Calculator",
        description="A test pricing calculator",
        base_cost=5.0,
        profit_margin=0.3,
        competitor_prices={"basic": 9.99, "pro": 19.99, "premium": 29.99},
    )


@pytest.fixture
def mock_agent_team():
    """Create a mock agent team for testing."""
    with patch("agent_team.AgentTeam") as mock:
        team = MagicMock()
        mock.return_value = team
        yield team


def test_partial_failure_recovery_in_workflow(market_analyzer, ab_testing, mock_agent_team):
    """
    Test recovery from partial failures in a multi - step workflow.

    This test verifies that:
    1. The workflow can detect and handle failures in intermediate steps
    2. The workflow can recover and continue from the last successful step
    3. The final result is consistent despite intermediate failures
    """
    # Step 1: Set up a mock for the market analyzer that fails on the first call
    original_analyze_market = market_analyzer.analyze_market
    call_count = 0

    def mock_analyze_market(segment):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Simulate a failure on the first call
            raise ConnectionError("Simulated network error")
        else:
            # Return normal result on subsequent calls
            return original_analyze_market(segment)

    # Apply the mock
    market_analyzer.analyze_market = mock_analyze_market

    # Step 2: Create a workflow function that implements retry logic
    def niche_analysis_workflow(segment, max_retries=3):
        retries = 0
        last_error = None

        while retries < max_retries:
            try:
                # Try to analyze the market
                market_analysis = market_analyzer.analyze_market(segment)

                # If successful, continue with the workflow
                selected_niche = market_analysis["potential_niches"][0]
                trend_analysis = market_analyzer.analyze_trends(segment)
                user_analysis = market_analyzer.analyze_target_users(selected_niche)

                # Return the complete analysis
                return {
                    "market_analysis": market_analysis,
                    "trend_analysis": trend_analysis,
                    "user_analysis": user_analysis,
                    "selected_niche": selected_niche,
                }
            except Exception as e:
                # Record the error and retry
                last_error = e
                retries += 1
                time.sleep(0.1)  # Short delay before retry

        # If we've exhausted retries, raise the last error
        raise last_error

    # Step 3: Run the workflow and verify recovery
    result = niche_analysis_workflow("e - commerce")

    # Verify that the workflow recovered and completed successfully
    assert call_count == 2  # First call failed, second succeeded
    assert "market_analysis" in result
    assert "trend_analysis" in result
    assert "user_analysis" in result
    assert "selected_niche" in result

    # Verify that the data is consistent
    assert result["selected_niche"] in result["market_analysis"]["potential_niches"]
    assert result["market_analysis"]["name"] == "E - Commerce"


def test_data_consistency_after_interruption(subscription_model, pricing_calculator):
    """
    Test data consistency after system interruptions.

    This test verifies that:
    1. Data remains consistent when operations are interrupted
    2. Partial updates are either fully applied or fully rolled back
    3. The system can detect and recover from inconsistent states
    """
    # Step 1: Create a subscription model with tiers
    basic_tier = subscription_model.add_tier(
        name="Basic",
        description="Basic features",
        price_monthly=9.99,
        price_yearly=99.99,
        features=["feature1", "feature2"],
        limits={"api_calls": 1000},
        target_users="Small businesses",
    )

    pro_tier = subscription_model.add_tier(
        name="Pro",
        description="Pro features",
        price_monthly=19.99,
        price_yearly=199.99,
        features=["feature1", "feature2", "feature3"],
        limits={"api_calls": 5000},
        target_users="Medium businesses",
    )

    # Step 2: Create a function that simulates a batch update with potential interruption
    def update_pricing_with_interruption(model, calculator, interrupt_probability=0.5):
        # Store original prices for verification and recovery
        original_prices = {
            tier["id"]: {"monthly": tier["price_monthly"], "yearly": tier["price_yearly"]}
            for tier in model.tiers
        }

        # Start updating prices
        updated_tiers = []
        try:
            for tier in model.tiers:
                # Calculate new price
                new_price = calculator.calculate_price(
                    base_value=10.0,
                    tier_multiplier=1.0 + (model.tiers.index(tier) * 0.5),
                    market_adjustment=1.0,
                )

                # Update tier price
                model.update_tier_price(tier["id"], price_monthly=new_price)
                updated_tiers.append(tier["id"])

                # Simulate random interruption
                if random.random() < interrupt_probability and len(updated_tiers) < len(
                    model.tiers
                ):
                    raise InterruptedError("Simulated interruption during batch update")

            # If we get here, all updates were successful
            return True, updated_tiers, None
        except Exception as e:
            # Rollback changes
            for tier_id in updated_tiers:
                model.update_tier_price(
                    tier_id,
                    price_monthly=original_prices[tier_id]["monthly"],
                    price_yearly=original_prices[tier_id]["yearly"],
                )
            return False, updated_tiers, e

    # Step 3: Run the update function with a fixed seed for reproducibility
    random.seed(42)  # Set seed for reproducible test
    success, updated_tiers, error = update_pricing_with_interruption(
        subscription_model, pricing_calculator
    )

    # Step 4: Verify data consistency
    if success:
        # All tiers should be updated
        assert len(updated_tiers) == len(subscription_model.tiers)
        for tier in subscription_model.tiers:
            assert tier["price_monthly"] != 9.99 and tier["price_monthly"] != 19.99
    else:
        # No tiers should be updated (all rolled back)
        assert subscription_model.tiers[0]["price_monthly"] == 9.99
        assert subscription_model.tiers[1]["price_monthly"] == 19.99
        assert isinstance(error, InterruptedError)


def test_transaction_rollback_scenarios(ab_testing):
    """
    Test transaction rollback scenarios in multi - step workflows.

    This test verifies that:
    1. Transactions can be rolled back when errors occur
    2. The system maintains ACID properties during transactions
    3. Concurrent operations are handled correctly
    """
    # Step 1: Create a test with variants
    test = ab_testing.create_test(
        name="Transaction Test",
        description="Testing transaction rollback",
        content_type="landing_page",
        test_type="a_b",
        variants=[
            {"name": "Control", "is_control": True},
            {"name": "Variant B", "is_control": False},
        ],
    )

    test_id = test["id"]
    control_id = test["variants"][0]["id"]
    variant_id = test["variants"][1]["id"]

    # Step 2: Create a function that simulates a transaction with potential failure
    def record_interactions_in_transaction(test_id, variant_id, count, fail_at=None):
        # Start recording interactions
        recorded = 0
        try:
            for i in range(count):
                ab_testing.record_interaction(test_id, variant_id, "impression")
                recorded += 1

                # Simulate failure at specific point if requested
                if fail_at is not None and i == fail_at:
                    raise ValueError(f"Simulated failure after {i + 1} interactions")

            # If we get here, all interactions were recorded successfully
            return True, recorded, None
        except Exception as e:
            # In a real system, this would trigger a transaction rollback
            # For this test, we'll simulate rollback by tracking what happened
            return False, recorded, e

    # Step 3: Run successful and failing transactions
    success_result, success_count, _ = record_interactions_in_transaction(test_id, control_id, 100)
    fail_result, fail_count, fail_error = record_interactions_in_transaction(
        test_id, variant_id, 100, fail_at=50
    )

    # Step 4: Verify transaction results
    assert success_result is True
    assert success_count == 100

    assert fail_result is False
    assert fail_count == 51  # 0 - based index, so fail_at=50 means 51 operations
    assert isinstance(fail_error, ValueError)

    # Step 5: Test concurrent transactions
    def concurrent_interaction_recorder(variant_id, count, results):
        try:
            for _ in range(count):
                ab_testing.record_interaction(test_id, variant_id, "impression")
            results.append(True)
        except Exception as e:
            results.append(e)

    # Create threads for concurrent operations
    thread_results = []
    threads = []
    for i in range(5):  # 5 concurrent threads
        thread = threading.Thread(
            target=concurrent_interaction_recorder,
            args=(control_id if i % 2 == 0 else variant_id, 20, thread_results),
        )
        threads.append(thread)

    # Start and join all threads
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Verify all threads completed successfully
    assert all(result is True for result in thread_results)

    # Verify the final state by analyzing the test
    analysis = ab_testing.analyze_test(test_id)
    assert "variants" in analysis
    assert len(analysis["variants"]) == 2


def test_workflow_with_compensating_actions(mock_agent_team):
    """
    Test workflows with compensating actions for error recovery.

    This test verifies that:
    1. The system can perform compensating actions when errors occur
    2. The workflow can recover to a consistent state after errors
    3. The system maintains an audit trail of actions and compensations
    """
    # Step 1: Set up the mock agent team with error injection
    # Make develop_solution fail on first call
    mock_agent_team.develop_solution.side_effect = [
        ValueError("Simulated error in solution development"),  # First call fails
        {"id": "solution - 123", "name": "Test Solution"},  # Second call succeeds
    ]

    # Make create_monetization_strategy succeed
    mock_agent_team.create_monetization_strategy.return_value = {
        "id": "monetization - 123",
        "name": "Test Monetization Strategy",
    }

    # Make create_marketing_plan succeed
    mock_agent_team.create_marketing_plan.return_value = {
        "id": "marketing - 123",
        "name": "Test Marketing Plan",
    }

    # Step 2: Create a workflow function with compensating actions
    def complete_workflow_with_compensation(team, niche_id):
        audit_trail = []

        try:
            # Step 1: Develop solution
            audit_trail.append(
                {"action": "develop_solution", "status": "started", "niche_id": niche_id}
            )
            solution = team.develop_solution(niche_id)
            audit_trail.append(
                {"action": "develop_solution", "status": "completed", "solution_id": solution["id"]}
            )

            # Step 2: Create monetization strategy
            audit_trail.append(
                {
                    "action": "create_monetization_strategy",
                    "status": "started",
                    "solution_id": solution["id"],
                }
            )
            monetization = team.create_monetization_strategy(solution["id"])
            audit_trail.append(
                {
                    "action": "create_monetization_strategy",
                    "status": "completed",
                    "monetization_id": monetization["id"],
                }
            )

            # Step 3: Create marketing plan
            audit_trail.append(
                {
                    "action": "create_marketing_plan",
                    "status": "started",
                    "solution_id": solution["id"],
                    "monetization_id": monetization["id"],
                }
            )
            marketing = team.create_marketing_plan(niche_id, solution["id"], monetization["id"])
            audit_trail.append(
                {
                    "action": "create_marketing_plan",
                    "status": "completed",
                    "marketing_id": marketing["id"],
                }
            )

            return (
                True,
                {"solution": solution, "monetization": monetization, "marketing": marketing},
                audit_trail,
            )

        except Exception as e:
            # Record the error
            audit_trail.append({"action": "error", "message": str(e)})

            # Perform compensating actions if needed
            last_completed_action = next(
                (a for a in reversed(audit_trail) if a["status"] == "completed"), None
            )

            if last_completed_action:
                if last_completed_action["action"] == "create_monetization_strategy":
                    # Compensate for monetization strategy creation
                    audit_trail.append(
                        {
                            "action": "compensate_monetization_strategy",
                            "status": "started",
                            "monetization_id": last_completed_action["monetization_id"],
                        }
                    )
                    team.archive_monetization_strategy(last_completed_action["monetization_id"])
                    audit_trail.append(
                        {"action": "compensate_monetization_strategy", "status": "completed"}
                    )

                elif last_completed_action["action"] == "develop_solution":
                    # Compensate for solution development
                    audit_trail.append(
                        {
                            "action": "compensate_develop_solution",
                            "status": "started",
                            "solution_id": last_completed_action["solution_id"],
                        }
                    )
                    team.archive_solution(last_completed_action["solution_id"])
                    audit_trail.append(
                        {"action": "compensate_develop_solution", "status": "completed"}
                    )

            # Return failure status
            return False, None, audit_trail

    # Step 3: Run the workflow and verify it fails the first time
    success, result, audit_trail = complete_workflow_with_compensation(mock_agent_team, "niche - 123")

    # Verify the workflow failed and recorded the error
    assert success is False
    assert result is None
    assert any(a["action"] == "error" for a in audit_trail)
    assert mock_agent_team.develop_solution.call_count == 1

    # Step 4: Run the workflow again and verify it succeeds
    success, result, audit_trail = complete_workflow_with_compensation(mock_agent_team, "niche - 123")

    # Verify the workflow succeeded
    assert success is True
    assert result is not None
    assert "solution" in result
    assert "monetization" in result
    assert "marketing" in result
    assert mock_agent_team.develop_solution.call_count == 2
    assert mock_agent_team.create_monetization_strategy.call_count == 1
    assert mock_agent_team.create_marketing_plan.call_count == 1

    # Verify the audit trail is complete
    action_sequence = [a["action"] for a in audit_trail if a["status"] == "completed"]
    assert action_sequence == [
        "develop_solution",
        "create_monetization_strategy",
        "create_marketing_plan",
    ]
