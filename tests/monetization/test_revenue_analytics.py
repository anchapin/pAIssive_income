"""
Tests for revenue analytics functionality.

This module contains tests for revenue analytics, including MRR / ARR calculation,
customer lifetime value predictions, and churn analysis.
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from monetization.revenue_analytics import (
    ChurnAnalyzer,
    CustomerLifetimeValue,
    EventType,
    RevenueAnalytics,
    RevenueMetrics,
    RevenueProjector,
    SubscriptionEvent,
)


class TestRevenueAnalytics:
    """Tests for revenue analytics functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create revenue analytics
        self.revenue_analytics = RevenueAnalytics()

        # Create churn analyzer
        self.churn_analyzer = ChurnAnalyzer()

        # Create customer lifetime value calculator
        self.clv_calculator = CustomerLifetimeValue()

        # Create revenue projector
        self.revenue_projector = RevenueProjector()

        # Test subscription data
        self.subscription_data = [
            # Active subscriptions
            {
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "plan_id": "plan_basic",
                "amount": Decimal("10.00"),
                "currency": "USD",
                "status": "active",
                "start_date": (datetime.utcnow() - timedelta(days=100)).isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                    
                "canceled_at": None,
            },
            {
                "subscription_id": "sub_002",
                "customer_id": "cust_002",
                "plan_id": "plan_premium",
                "amount": Decimal("50.00"),
                "currency": "USD",
                "status": "active",
                "start_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=20)).isoformat(),
                    
                "canceled_at": None,
            },
            {
                "subscription_id": "sub_003",
                "customer_id": "cust_003",
                "plan_id": "plan_enterprise",
                "amount": Decimal("200.00"),
                "currency": "USD",
                "status": "active",
                "start_date": (datetime.utcnow() - timedelta(days=80)).isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=10)).isoformat(),
                    
                "canceled_at": None,
            },
            # Canceled subscriptions
            {
                "subscription_id": "sub_004",
                "customer_id": "cust_004",
                "plan_id": "plan_basic",
                "amount": Decimal("10.00"),
                "currency": "USD",
                "status": "canceled",
                "start_date": (datetime.utcnow() - timedelta(days=70)).isoformat(),
                "current_period_end": (datetime.utcnow() - timedelta(days=40)).isoformat(),
                    
                "canceled_at": (datetime.utcnow() - timedelta(days=45)).isoformat(),
            },
            {
                "subscription_id": "sub_005",
                "customer_id": "cust_005",
                "plan_id": "plan_premium",
                "amount": Decimal("50.00"),
                "currency": "USD",
                "status": "canceled",
                "start_date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
                "current_period_end": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    
                "canceled_at": (datetime.utcnow() - timedelta(days=35)).isoformat(),
            },
            # Upgraded subscriptions
            {
                "subscription_id": "sub_006",
                "customer_id": "cust_006",
                "plan_id": "plan_basic",
                "amount": Decimal("10.00"),
                "currency": "USD",
                "status": "canceled",
                "start_date": (datetime.utcnow() - timedelta(days=50)).isoformat(),
                "current_period_end": (datetime.utcnow() - timedelta(days=20)).isoformat(),
                    
                "canceled_at": (datetime.utcnow() - timedelta(days=25)).isoformat(),
            },
            {
                "subscription_id": "sub_007",
                "customer_id": "cust_006",
                "plan_id": "plan_premium",
                "amount": Decimal("50.00"),
                "currency": "USD",
                "status": "active",
                "start_date": (datetime.utcnow() - timedelta(days=25)).isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                    
                "canceled_at": None,
            },
        ]

        # Test subscription events
        self.subscription_events = [
            # New subscriptions
            {
                "event_id": "evt_001",
                "event_type": EventType.SUBSCRIPTION_CREATED,
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "plan_id": "plan_basic",
                "amount": Decimal("10.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=100)).isoformat(),
            },
            {
                "event_id": "evt_002",
                "event_type": EventType.SUBSCRIPTION_CREATED,
                "subscription_id": "sub_002",
                "customer_id": "cust_002",
                "plan_id": "plan_premium",
                "amount": Decimal("50.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=90)).isoformat(),
            },
            {
                "event_id": "evt_003",
                "event_type": EventType.SUBSCRIPTION_CREATED,
                "subscription_id": "sub_003",
                "customer_id": "cust_003",
                "plan_id": "plan_enterprise",
                "amount": Decimal("200.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=80)).isoformat(),
            },
            # Cancellations
            {
                "event_id": "evt_004",
                "event_type": EventType.SUBSCRIPTION_CANCELED,
                "subscription_id": "sub_004",
                "customer_id": "cust_004",
                "plan_id": "plan_basic",
                "amount": Decimal("10.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=45)).isoformat(),
            },
            {
                "event_id": "evt_005",
                "event_type": EventType.SUBSCRIPTION_CANCELED,
                "subscription_id": "sub_005",
                "customer_id": "cust_005",
                "plan_id": "plan_premium",
                "amount": Decimal("50.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=35)).isoformat(),
            },
            # Upgrades
            {
                "event_id": "evt_006",
                "event_type": EventType.SUBSCRIPTION_CANCELED,
                "subscription_id": "sub_006",
                "customer_id": "cust_006",
                "plan_id": "plan_basic",
                "amount": Decimal("10.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=25)).isoformat(),
            },
            {
                "event_id": "evt_007",
                "event_type": EventType.SUBSCRIPTION_CREATED,
                "subscription_id": "sub_007",
                "customer_id": "cust_006",
                "plan_id": "plan_premium",
                "amount": Decimal("50.00"),
                "timestamp": (datetime.utcnow() - timedelta(days=25)).isoformat(),
            },
        ]

    def test_mrr_arr_calculation(self):
        """Test MRR / ARR calculation."""
        # Mock subscription data
        with patch.object(self.revenue_analytics, 
            "get_active_subscriptions") as mock_subs:
            mock_subs.return_value = \
                [s for s in self.subscription_data if s["status"] == "active"]

            # Calculate MRR
            mrr = self.revenue_analytics.calculate_mrr()

            # Expected MRR: $10 + $50 + $200 + $50 = $310
            expected_mrr = Decimal("310.00")
            assert mrr == expected_mrr

            # Calculate ARR
            arr = self.revenue_analytics.calculate_arr()

            # Expected ARR: MRR * 12 = $310 * 12 = $3720
            expected_arr = expected_mrr * 12
            assert arr == expected_arr

            # Calculate MRR by plan
            mrr_by_plan = self.revenue_analytics.calculate_mrr_by_plan()

            # Expected MRR by plan:
            # - Basic: $10
            # - Premium: $50 + $50 = $100
            # - Enterprise: $200
            assert mrr_by_plan["plan_basic"] == Decimal("10.00")
            assert mrr_by_plan["plan_premium"] == Decimal("100.00")
            assert mrr_by_plan["plan_enterprise"] == Decimal("200.00")

    def test_mrr_movements(self):
        """Test MRR movements (new, churn, expansion, contraction)."""
        # Mock subscription events
        with patch.object(self.revenue_analytics, 
            "get_subscription_events") as mock_events:
            # Set up events for a specific time period
            start_date = datetime.utcnow() - timedelta(days=30)
            end_date = datetime.utcnow()

            # Filter events in the time period
            period_events = [
                e
                for e in self.subscription_events
                if start_date <= datetime.fromisoformat(e["timestamp"]) <= end_date
            ]

            mock_events.return_value = period_events

            # Calculate MRR movements
            mrr_movements = self.revenue_analytics.calculate_mrr_movements(
                start_date=start_date, end_date=end_date
            )

            # Expected movements:
            # - New: $0 (no new subscriptions in this period)
            # - Churn: -$50 (sub_005 canceled)
            # - Expansion: +$40 (sub_006 upgraded from $10 to $50)
            # - Contraction: $0 (no downgrades)
            assert mrr_movements["new"] == Decimal("0.00")
            assert mrr_movements["churn"] == Decimal(" - 50.00")
            assert mrr_movements["expansion"] == Decimal("40.00")
            assert mrr_movements["contraction"] == Decimal("0.00")

            # Calculate net MRR change
            net_mrr_change = self.revenue_analytics.calculate_net_mrr_change(
                start_date=start_date, end_date=end_date
            )

            # Expected net change: -$50 + $40 = -$10
            expected_net_change = Decimal(" - 10.00")
            assert net_mrr_change == expected_net_change

    def test_customer_lifetime_value(self):
        """Test customer lifetime value predictions."""
        # Mock customer data
        customer_data = [
            {
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "plan_id": "plan_basic",
                "monthly_revenue": Decimal("10.00"),
                "start_date": (datetime.utcnow() - timedelta(days=100)).isoformat(),
                "status": "active",
            },
            {
                "customer_id": "cust_002",
                "subscription_id": "sub_002",
                "plan_id": "plan_premium",
                "monthly_revenue": Decimal("50.00"),
                "start_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "status": "active",
            },
            {
                "customer_id": "cust_003",
                "subscription_id": "sub_003",
                "plan_id": "plan_enterprise",
                "monthly_revenue": Decimal("200.00"),
                "start_date": (datetime.utcnow() - timedelta(days=80)).isoformat(),
                "status": "active",
            },
        ]

        # Mock churn rate
        churn_rate = 0.05  # 5% monthly churn

        with patch.object(self.clv_calculator, "get_customer_data") as mock_customers:
            mock_customers.return_value = customer_data

            with patch.object(self.churn_analyzer, 
                "calculate_churn_rate") as mock_churn:
                mock_churn.return_value = churn_rate

                # Calculate CLV for each customer
                for customer in customer_data:
                    clv = self.clv_calculator.calculate_clv(
                        customer_id=customer["customer_id"],
                        monthly_revenue=customer["monthly_revenue"],
                        churn_rate=churn_rate,
                        discount_rate=0.1,  # 10% discount rate
                        months=36,  # 3 - year horizon
                    )

                    # CLV should be positive and proportional to monthly revenue
                    assert clv > 0
                    assert clv > customer["monthly_revenue"]

                # Calculate average CLV by plan
                avg_clv_by_plan = self.clv_calculator.calculate_avg_clv_by_plan(
                    churn_rate=churn_rate, discount_rate=0.1, months=36
                )

                # Verify CLV by plan
                assert avg_clv_by_plan["plan_basic"] > 0
                assert avg_clv_by_plan["plan_premium"] > avg_clv_by_plan["plan_basic"]
                assert avg_clv_by_plan["plan_enterprise"] > avg_clv_by_plan["plan_premium"]

    def test_churn_analysis(self):
        """Test churn analysis and prevention."""
        # Mock subscription data
        with patch.object(self.churn_analyzer, "get_subscription_data") as mock_subs:
            mock_subs.return_value = self.subscription_data

            # Calculate overall churn rate
            churn_rate = self.churn_analyzer.calculate_churn_rate()

            # Expected churn rate: 2 churned out of 7 total = ~28.6%
            assert 0.25 <= churn_rate <= 0.3

            # Calculate churn rate by plan
            churn_by_plan = self.churn_analyzer.calculate_churn_rate_by_plan()

            # Expected churn by plan:
            # - Basic: 1 out of 2 = 50%
            # - Premium: 1 out of 3 = 33.3%
            # - Enterprise: 0 out of 1 = 0%
            assert 0.45 <= churn_by_plan["plan_basic"] <= 0.55
            assert 0.3 <= churn_by_plan["plan_premium"] <= 0.4
            assert churn_by_plan["plan_enterprise"] == 0.0

            # Calculate average customer lifetime
            avg_lifetime = self.churn_analyzer.calculate_avg_customer_lifetime()

            # Average lifetime should be positive
            assert avg_lifetime > 0

            # Calculate churn reasons
            churn_reasons = {"sub_004": "Price too high", "sub_005": "Missing features"}

            with patch.object(self.churn_analyzer, "get_churn_reasons") as mock_reasons:
                mock_reasons.return_value = churn_reasons

                # Analyze churn reasons
                reason_analysis = self.churn_analyzer.analyze_churn_reasons()

                # Verify analysis
                assert "Price too high" in reason_analysis
                assert "Missing features" in reason_analysis
                assert reason_analysis["Price too high"] == 1
                assert reason_analysis["Missing features"] == 1

            # Test churn prediction
            churn_risk_factors = {
                "cust_001": 0.2,  # Low risk
                "cust_002": 0.6,  # Medium risk
                "cust_003": 0.1,  # Low risk
            }

            with patch.object(self.churn_analyzer, 
                "predict_churn_risk") as mock_predict:
                mock_predict.side_effect = lambda customer_id: churn_risk_factors.get(
                    customer_id, 0.0
                )

                # Get at - risk customers
                at_risk_customers = \
                    self.churn_analyzer.get_at_risk_customers(risk_threshold=0.5)

                # Only cust_002 should be at risk
                assert len(at_risk_customers) == 1
                assert at_risk_customers[0]["customer_id"] == "cust_002"

                # Test churn prevention recommendations
                prevention_strategies = {
                    "cust_002": [
                        "Offer discount",
                        "Schedule check - in call",
                        "Highlight unused features",
                    ]
                }

                with patch.object(
                    self.churn_analyzer, "get_prevention_strategies"
                ) as mock_strategies:
                    mock_strategies.side_effect = \
                        lambda customer_id: prevention_strategies.get(
                        customer_id, []
                    )

                    # Get prevention strategies for at - risk customer
                    strategies = \
                        self.churn_analyzer.get_prevention_strategies("cust_002")

                    # Verify strategies
                    assert len(strategies) == 3
                    assert "Offer discount" in strategies
                    assert "Schedule check - in call" in strategies
                    assert "Highlight unused features" in strategies

    def test_revenue_projections(self):
        """Test revenue projections."""
        # Mock current MRR and growth rate
        current_mrr = Decimal("310.00")
        monthly_growth_rate = 0.1  # 10% monthly growth
        churn_rate = 0.05  # 5% monthly churn

        with patch.object(self.revenue_analytics, "calculate_mrr") as mock_mrr:
            mock_mrr.return_value = current_mrr

            with patch.object(self.revenue_analytics, 
                "calculate_growth_rate") as mock_growth:
                mock_growth.return_value = monthly_growth_rate

                with patch.object(self.churn_analyzer, 
                    "calculate_churn_rate") as mock_churn:
                    mock_churn.return_value = churn_rate

                    # Project revenue for 12 months
                    projection = self.revenue_projector.project_revenue(
                        months=12,
                        current_mrr=current_mrr,
                        growth_rate=monthly_growth_rate,
                        churn_rate=churn_rate,
                    )

                    # Verify projection
                    assert len(projection) == 12
                    assert projection[0] == current_mrr

                    # Each month should grow by (growth_rate - churn_rate)
                    net_growth_rate = monthly_growth_rate - churn_rate
                    for i in range(1, 12):
                        expected_mrr = projection[i - 1] * (1 + net_growth_rate)
                        assert abs(projection[i] - expected_mrr) < Decimal("0.01")

                    # Project revenue by plan
                    plan_distribution = {
                        "plan_basic": 0.1,  # 10% of revenue
                        "plan_premium": 0.3,  # 30% of revenue
                        "plan_enterprise": 0.6,  # 60% of revenue
                    }

                    with patch.object(self.revenue_analytics, 
                        "get_plan_distribution") as mock_dist:
                        mock_dist.return_value = plan_distribution

                        # Project revenue by plan
                        plan_projection = \
                            self.revenue_projector.project_revenue_by_plan(
                            months=12,
                            current_mrr=current_mrr,
                            growth_rate=monthly_growth_rate,
                            churn_rate=churn_rate,
                        )

                        # Verify plan projection
                        assert len(plan_projection) == 12

                        # Check first month
                        assert plan_projection[0]["plan_basic"] == current_mrr * \
                            Decimal("0.1")
                        assert plan_projection[0]["plan_premium"] == current_mrr * \
                            Decimal("0.3")
                        assert plan_projection[0]["plan_enterprise"] == current_mrr * \
                            Decimal("0.6")

                        # Check last month
                        total_last_month = sum(plan_projection[11].values())
                        assert abs(total_last_month - projection[11]) < Decimal("0.01")


if __name__ == "__main__":
    pytest.main([" - v", "test_revenue_analytics.py"])
