"""
Tests for revenue analytics functionality.

This module tests the revenue analytics functionality in the monetization module,
including MRR/ARR calculation, customer lifetime value predictions, and churn analysis.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil
from datetime import datetime, timedelta

from monetization.subscription import SubscriptionPlan, SubscriptionTier
from monetization.user_subscription import Subscription, SubscriptionStatus
from monetization.subscription_manager import SubscriptionManager
from monetization.subscription_analytics import SubscriptionMetrics, ChurnAnalysis, SubscriptionForecasting


class TestRevenueAnalytics(unittest.TestCase):
    """Test cases for revenue analytics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a subscription manager
        self.subscription_manager = SubscriptionManager(
            storage_dir=os.path.join(self.temp_dir, "subscriptions")
        )
        
        # Create subscription plans
        self.basic_plan = self.subscription_manager.create_plan(
            name="Basic Plan",
            description="Basic subscription plan"
        )
        
        self.pro_plan = self.subscription_manager.create_plan(
            name="Pro Plan",
            description="Professional subscription plan"
        )
        
        # Add tiers to plans
        self.basic_tier = self.basic_plan.add_tier(
            name="Basic",
            description="Basic tier",
            price_monthly=9.99,
            price_yearly=99.99
        )
        
        self.pro_tier = self.pro_plan.add_tier(
            name="Pro",
            description="Professional tier",
            price_monthly=29.99,
            price_yearly=299.99
        )
        
        # Create subscriptions
        self.active_subscriptions = []
        self.canceled_subscriptions = []
        
        # Create active subscriptions
        for i in range(10):
            subscription = self.subscription_manager.create_subscription(
                customer_id=f"customer_{i}",
                plan_id=self.basic_plan.id,
                tier_id=self.basic_tier["id"],
                billing_interval="monthly",
                start_date=datetime.now() - timedelta(days=30),
                status=SubscriptionStatus.ACTIVE
            )
            self.active_subscriptions.append(subscription)
        
        for i in range(5):
            subscription = self.subscription_manager.create_subscription(
                customer_id=f"pro_customer_{i}",
                plan_id=self.pro_plan.id,
                tier_id=self.pro_tier["id"],
                billing_interval="monthly",
                start_date=datetime.now() - timedelta(days=60),
                status=SubscriptionStatus.ACTIVE
            )
            self.active_subscriptions.append(subscription)
        
        # Create canceled subscriptions
        for i in range(3):
            subscription = self.subscription_manager.create_subscription(
                customer_id=f"canceled_customer_{i}",
                plan_id=self.basic_plan.id,
                tier_id=self.basic_tier["id"],
                billing_interval="monthly",
                start_date=datetime.now() - timedelta(days=90),
                end_date=datetime.now() - timedelta(days=30),
                status=SubscriptionStatus.CANCELED,
                cancellation_reason="too_expensive"
            )
            self.canceled_subscriptions.append(subscription)
        
        for i in range(2):
            subscription = self.subscription_manager.create_subscription(
                customer_id=f"canceled_pro_customer_{i}",
                plan_id=self.pro_plan.id,
                tier_id=self.pro_tier["id"],
                billing_interval="monthly",
                start_date=datetime.now() - timedelta(days=120),
                end_date=datetime.now() - timedelta(days=60),
                status=SubscriptionStatus.CANCELED,
                cancellation_reason="not_using"
            )
            self.canceled_subscriptions.append(subscription)
        
        # Create metrics calculator
        self.metrics = SubscriptionMetrics(self.subscription_manager)
        
        # Create churn analysis
        self.churn_analysis = ChurnAnalysis(self.subscription_manager)
        
        # Create subscription forecasting
        self.forecasting = SubscriptionForecasting(
            metrics=self.metrics,
            churn_analysis=self.churn_analysis
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_mrr_arr_calculation(self):
        """Test MRR/ARR calculation."""
        # Calculate MRR
        mrr = self.metrics.get_monthly_recurring_revenue()
        
        # Expected MRR: 10 basic * $9.99 + 5 pro * $29.99 = $99.90 + $149.95 = $249.85
        expected_mrr = (10 * 9.99) + (5 * 29.99)
        self.assertAlmostEqual(mrr, expected_mrr, places=2)
        
        # Calculate ARR
        arr = self.metrics.get_annual_recurring_revenue()
        
        # Expected ARR: MRR * 12 = $249.85 * 12 = $2,998.20
        expected_arr = expected_mrr * 12
        self.assertAlmostEqual(arr, expected_arr, places=2)
        
        # Calculate MRR for basic plan only
        basic_mrr = self.metrics.get_monthly_recurring_revenue(plan_id=self.basic_plan.id)
        
        # Expected basic MRR: 10 basic * $9.99 = $99.90
        expected_basic_mrr = 10 * 9.99
        self.assertAlmostEqual(basic_mrr, expected_basic_mrr, places=2)
        
        # Calculate MRR for pro plan only
        pro_mrr = self.metrics.get_monthly_recurring_revenue(plan_id=self.pro_plan.id)
        
        # Expected pro MRR: 5 pro * $29.99 = $149.95
        expected_pro_mrr = 5 * 29.99
        self.assertAlmostEqual(pro_mrr, expected_pro_mrr, places=2)

    def test_customer_lifetime_value_predictions(self):
        """Test customer lifetime value predictions."""
        # Calculate overall LTV
        ltv = self.churn_analysis.get_lifetime_value()
        
        # Calculate LTV for basic plan
        basic_ltv = self.churn_analysis.get_lifetime_value(plan_id=self.basic_plan.id)
        
        # Calculate LTV for pro plan
        pro_ltv = self.churn_analysis.get_lifetime_value(plan_id=self.pro_plan.id)
        
        # Verify LTV values
        self.assertGreater(ltv, 0)
        self.assertGreater(basic_ltv, 0)
        self.assertGreater(pro_ltv, 0)
        
        # Pro LTV should be higher than basic LTV
        self.assertGreater(pro_ltv, basic_ltv)
        
        # Calculate LTV with custom parameters
        custom_ltv = self.churn_analysis.get_lifetime_value(
            discount_rate=0.1,
            time_period="year"
        )
        
        # Verify custom LTV
        self.assertGreater(custom_ltv, 0)

    def test_churn_analysis_and_prevention(self):
        """Test churn analysis and prevention."""
        # Calculate churn rate
        churn_rate = self.churn_analysis.get_churn_rate()
        
        # Verify churn rate
        self.assertGreaterEqual(churn_rate, 0)
        self.assertLessEqual(churn_rate, 100)
        
        # Calculate retention rate
        retention_rate = self.churn_analysis.get_retention_rate()
        
        # Verify retention rate
        self.assertGreaterEqual(retention_rate, 0)
        self.assertLessEqual(retention_rate, 100)
        
        # Verify churn rate + retention rate = 100%
        self.assertAlmostEqual(churn_rate + retention_rate, 100, places=2)
        
        # Get churn by plan
        churn_by_plan = self.churn_analysis.get_churn_by_plan()
        
        # Verify churn by plan
        self.assertIn(self.basic_plan.id, churn_by_plan)
        self.assertIn(self.pro_plan.id, churn_by_plan)
        
        # Get churn reasons
        churn_reasons = self.churn_analysis.get_churn_reasons()
        
        # Verify churn reasons
        self.assertIn("too_expensive", churn_reasons)
        self.assertIn("not_using", churn_reasons)
        
        # Get at-risk subscriptions
        at_risk = self.churn_analysis.get_at_risk_subscriptions()
        
        # Verify at-risk subscriptions
        self.assertIsInstance(at_risk, list)

    def test_subscription_growth_forecasting(self):
        """Test subscription growth forecasting."""
        # Forecast subscriptions
        subscription_forecast = self.forecasting.forecast_subscriptions(
            periods=12,
            period_type="month"
        )
        
        # Verify forecast
        self.assertEqual(len(subscription_forecast), 12)
        self.assertGreaterEqual(subscription_forecast[0], 15)  # Should start with current count
        
        # Forecast revenue
        revenue_forecast = self.forecasting.forecast_revenue(
            periods=12,
            period_type="month"
        )
        
        # Verify revenue forecast
        self.assertEqual(len(revenue_forecast), 12)
        self.assertGreaterEqual(revenue_forecast[0], 249)  # Should start with current MRR
        
        # Get forecast summary
        summary = self.forecasting.get_forecast_summary(
            periods=12,
            period_type="month"
        )
        
        # Verify summary
        self.assertIn("current_subscriptions", summary)
        self.assertIn("current_mrr", summary)
        self.assertIn("current_churn_rate", summary)
        self.assertIn("subscription_forecast", summary)
        self.assertIn("revenue_forecast", summary)
        self.assertEqual(len(summary["subscription_forecast"]), 12)
        self.assertEqual(len(summary["revenue_forecast"]), 12)

    def test_subscription_distribution_analysis(self):
        """Test subscription distribution analysis."""
        # Get subscription distribution
        distribution = self.metrics.get_subscription_distribution()
        
        # Verify distribution
        self.assertIn(self.basic_plan.id, distribution)
        self.assertIn(self.pro_plan.id, distribution)
        self.assertIn(self.basic_tier["id"], distribution[self.basic_plan.id])
        self.assertIn(self.pro_tier["id"], distribution[self.pro_plan.id])
        self.assertEqual(distribution[self.basic_plan.id][self.basic_tier["id"]], 10)
        self.assertEqual(distribution[self.pro_plan.id][self.pro_tier["id"]], 5)
        
        # Get subscription summary
        summary = self.metrics.get_subscription_summary()
        
        # Verify summary
        self.assertEqual(summary["total_count"], 20)  # 15 active + 5 canceled
        self.assertEqual(summary["active_count"], 15)
        self.assertEqual(summary["canceled_count"], 5)
        self.assertAlmostEqual(summary["mrr"], (10 * 9.99) + (5 * 29.99), places=2)
        self.assertAlmostEqual(summary["arr"], ((10 * 9.99) + (5 * 29.99)) * 12, places=2)
        self.assertAlmostEqual(summary["arpu"], ((10 * 9.99) + (5 * 29.99)) / 15, places=2)


if __name__ == "__main__":
    unittest.main()
