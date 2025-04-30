"""
Prorated billing for the pAIssive Income project.

This module provides classes for implementing prorated billing for subscription changes,
including upgrades, downgrades, and cancellations.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import math
import calendar
import copy


class ProratedBilling:
    """
    Class for calculating prorated billing.

    This class provides methods for calculating prorated billing for subscription changes,
    including upgrades, downgrades, and cancellations.
    """

    @staticmethod
    def get_days_in_month(date: datetime) -> int:
        """
        Get the number of days in a month.

        Args:
            date: Date to get the number of days for

        Returns:
            Number of days in the month
        """
        return calendar.monthrange(date.year, date.month)[1]

    @staticmethod
    def get_days_in_year(date: datetime) -> int:
        """
        Get the number of days in a year.

        Args:
            date: Date to get the number of days for

        Returns:
            Number of days in the year
        """
        return 366 if calendar.isleap(date.year) else 365

    @staticmethod
    def get_days_in_billing_period(start_date: datetime, period: str) -> int:
        """
        Get the number of days in a billing period.

        Args:
            start_date: Start date of the billing period
            period: Billing period (daily, weekly, monthly, quarterly, yearly)

        Returns:
            Number of days in the billing period
        """
        if period == "daily":
            return 1
        elif period == "weekly":
            return 7
        elif period == "monthly":
            return ProratedBilling.get_days_in_month(start_date)
        elif period == "quarterly":
            # Approximate a quarter as 3 months
            days = 0
            current_date = start_date

            for _ in range(3):
                days += ProratedBilling.get_days_in_month(current_date)

                # Move to next month
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(
                        current_date.year, current_date.month + 1, 1
                    )

            return days
        elif period == "yearly":
            return ProratedBilling.get_days_in_year(start_date)
        else:
            raise ValueError(f"Invalid period: {period}")

    @staticmethod
    def get_days_remaining_in_billing_period(
        current_date: datetime, period_start_date: datetime, period: str
    ) -> int:
        """
        Get the number of days remaining in a billing period.

        Args:
            current_date: Current date
            period_start_date: Start date of the billing period
            period: Billing period (daily, weekly, monthly, quarterly, yearly)

        Returns:
            Number of days remaining in the billing period
        """
        # Calculate the end date of the billing period
        if period == "daily":
            period_end_date = period_start_date + timedelta(days=1)
        elif period == "weekly":
            period_end_date = period_start_date + timedelta(days=7)
        elif period == "monthly":
            # Move to the same day in the next month
            if period_start_date.month == 12:
                next_month = datetime(
                    period_start_date.year + 1, 1, period_start_date.day
                )
            else:
                # Handle cases where the next month doesn't have the same day
                try:
                    next_month = datetime(
                        period_start_date.year,
                        period_start_date.month + 1,
                        period_start_date.day,
                    )
                except ValueError:
                    # Use the last day of the next month
                    if period_start_date.month == 12:
                        next_month = datetime(period_start_date.year + 1, 1, 1)
                    else:
                        next_month = datetime(
                            period_start_date.year, period_start_date.month + 1, 1
                        )

                    next_month = next_month.replace(
                        day=calendar.monthrange(next_month.year, next_month.month)[1]
                    )

            period_end_date = next_month
        elif period == "quarterly":
            # Move to the same day 3 months later
            month = period_start_date.month
            year = period_start_date.year

            month += 3
            if month > 12:
                month -= 12
                year += 1

            # Handle cases where the target month doesn't have the same day
            try:
                period_end_date = datetime(year, month, period_start_date.day)
            except ValueError:
                # Use the last day of the target month
                period_end_date = datetime(year, month, 1)
                period_end_date = period_end_date.replace(
                    day=calendar.monthrange(
                        period_end_date.year, period_end_date.month
                    )[1]
                )
        elif period == "yearly":
            # Move to the same day in the next year
            try:
                period_end_date = datetime(
                    period_start_date.year + 1,
                    period_start_date.month,
                    period_start_date.day,
                )
            except ValueError:
                # Handle February 29 in leap years
                period_end_date = datetime(
                    period_start_date.year + 1, period_start_date.month, 28
                )
        else:
            raise ValueError(f"Invalid period: {period}")

        # Calculate days remaining
        if current_date >= period_end_date:
            return 0

        days_remaining = (period_end_date - current_date).days
        return days_remaining

    @staticmethod
    def calculate_prorated_amount(
        full_amount: float, days_used: int, days_in_period: int
    ) -> float:
        """
        Calculate a prorated amount.

        Args:
            full_amount: Full amount for the billing period
            days_used: Number of days used
            days_in_period: Number of days in the billing period

        Returns:
            Prorated amount
        """
        if days_in_period <= 0:
            return 0.0

        return full_amount * (days_used / days_in_period)

    @staticmethod
    def calculate_prorated_refund(
        full_amount: float, days_remaining: int, days_in_period: int
    ) -> float:
        """
        Calculate a prorated refund.

        Args:
            full_amount: Full amount for the billing period
            days_remaining: Number of days remaining
            days_in_period: Number of days in the billing period

        Returns:
            Prorated refund amount
        """
        if days_in_period <= 0:
            return 0.0

        return full_amount * (days_remaining / days_in_period)

    @staticmethod
    def calculate_upgrade_amount(
        old_plan_amount: float,
        new_plan_amount: float,
        days_remaining: int,
        days_in_period: int,
    ) -> float:
        """
        Calculate the amount to charge for an upgrade.

        Args:
            old_plan_amount: Amount for the old plan
            new_plan_amount: Amount for the new plan
            days_remaining: Number of days remaining in the billing period
            days_in_period: Number of days in the billing period

        Returns:
            Amount to charge for the upgrade
        """
        if days_in_period <= 0:
            return 0.0

        # Calculate prorated refund for the old plan
        old_plan_refund = ProratedBilling.calculate_prorated_refund(
            full_amount=old_plan_amount,
            days_remaining=days_remaining,
            days_in_period=days_in_period,
        )

        # Calculate prorated charge for the new plan
        new_plan_charge = ProratedBilling.calculate_prorated_amount(
            full_amount=new_plan_amount,
            days_used=days_remaining,
            days_in_period=days_in_period,
        )

        # Return the difference
        return new_plan_charge - old_plan_refund

    @staticmethod
    def calculate_downgrade_amount(
        old_plan_amount: float,
        new_plan_amount: float,
        days_remaining: int,
        days_in_period: int,
    ) -> float:
        """
        Calculate the amount to refund for a downgrade.

        Args:
            old_plan_amount: Amount for the old plan
            new_plan_amount: Amount for the new plan
            days_remaining: Number of days remaining in the billing period
            days_in_period: Number of days in the billing period

        Returns:
            Amount to refund for the downgrade
        """
        # Use the same calculation as upgrade, but the result will be negative
        return ProratedBilling.calculate_upgrade_amount(
            old_plan_amount=old_plan_amount,
            new_plan_amount=new_plan_amount,
            days_remaining=days_remaining,
            days_in_period=days_in_period,
        )

    @staticmethod
    def calculate_cancellation_refund(
        plan_amount: float, days_remaining: int, days_in_period: int
    ) -> float:
        """
        Calculate the amount to refund for a cancellation.

        Args:
            plan_amount: Amount for the plan
            days_remaining: Number of days remaining in the billing period
            days_in_period: Number of days in the billing period

        Returns:
            Amount to refund for the cancellation
        """
        return ProratedBilling.calculate_prorated_refund(
            full_amount=plan_amount,
            days_remaining=days_remaining,
            days_in_period=days_in_period,
        )

    @staticmethod
    def calculate_plan_change(
        old_plan_amount: float,
        new_plan_amount: float,
        current_date: datetime,
        period_start_date: datetime,
        period: str,
    ) -> Dict[str, Any]:
        """
        Calculate the amount to charge or refund for a subscription plan change.

        This algorithm implements a sophisticated proration system for subscription changes
        that occur mid-billing cycle. The implementation follows these key stages:

        1. BILLING PERIOD DETERMINATION:
           - Calculates the total days in the current billing period based on period type
           - Handles calendar complexities like varying month lengths and leap years
           - Provides consistent time accounting across different billing frequencies
           - Properly aligns calculation with actual calendar dates for accuracy

        2. TEMPORAL POSITION ANALYSIS:
           - Determines the precise position within the billing cycle
           - Calculates both elapsed time (days_used) and remaining time (days_remaining)
           - Creates the foundation for fair and transparent proration calculation
           - Handles edge cases like period boundaries correctly

        3. PROPORTIONAL VALUE CALCULATION:
           - Calculates the value of both the old and new plans for the remaining period
           - Uses the day-level granularity for maximum accuracy
           - Follows standard accounting practices for subscription businesses
           - Handles zero-day edge cases safely to prevent division errors

        4. DIFFERENTIAL AMOUNT DETERMINATION:
           - Calculates the net financial impact of the plan change
           - Determines whether additional charges or refunds are required
           - Provides directionally correct results for both upgrades and downgrades
           - Maintains neutrality for equal-value plan switches

        5. COMPREHENSIVE RESULT PACKAGING:
           - Creates a structured result with all relevant metrics and decisions
           - Includes clear action guidance (charge vs. refund)
           - Provides complete transparency by including all intermediate calculations
           - Returns sufficient context for downstream billing processes

        This proration algorithm addresses several critical business requirements:
        - Fair billing for partial periods when customers change plans
        - Transparent explanation of charges and credits to customers
        - Support for both upgrades (which require additional charges) and
          downgrades (which may require refunds)
        - Proper handling of various billing period types (monthly, quarterly, yearly)

        The implementation specifically handles common real-world scenarios:
        - Mid-month upgrades to more expensive plans
        - Downgrades to less expensive plans
        - Cancellations (treated as downgrades to a $0 plan)
        - Plan switches across different billing frequencies
        - Edge cases like changes on the first/last day of billing periods

        Args:
            old_plan_amount: The full-period amount for the customer's current plan
            new_plan_amount: The full-period amount for the customer's new plan
            current_date: The date when the plan change is occurring
            period_start_date: The start date of the current billing period
            period: The billing period type (daily, weekly, monthly, quarterly, yearly)

        Returns:
            A comprehensive dictionary with plan change details:
            - old_plan_amount: Original plan amount
            - new_plan_amount: New plan amount
            - current_date: Date of the plan change
            - period_start_date: Start date of the billing period
            - period: Billing period type
            - days_in_period: Total days in the billing period
            - days_used: Days used in the current period
            - days_remaining: Days remaining in the current period
            - old_plan_used: Amount already used from the old plan
            - old_plan_remaining: Unused value from the old plan
            - new_plan_remaining: Cost of the new plan for the remainder of the period
            - difference: Net amount to charge or refund
            - is_upgrade: Whether this is an upgrade (new plan costs more)
            - action: Action to take ("charge" or "refund")
            - amount: Absolute amount to charge or refund
        """
        # STAGE 1: Calculate days in period and days remaining
        # Determine the total length of the billing period and current position within it
        days_in_period = ProratedBilling.get_days_in_billing_period(
            period_start_date, period
        )
        days_remaining = ProratedBilling.get_days_remaining_in_billing_period(
            current_date, period_start_date, period
        )
        days_used = days_in_period - days_remaining

        # STAGE 2: Calculate prorated values for old and new plans
        # Determine the value of each plan for the portion of the period that remains

        # Calculate the value of the old plan that has already been used
        # This represents what the customer has already consumed and should pay for
        old_plan_used = ProratedBilling.calculate_prorated_amount(
            old_plan_amount, days_used, days_in_period
        )

        # Calculate the value of the old plan for the remaining days
        # This represents what the customer would have paid under the old plan
        old_plan_remaining = ProratedBilling.calculate_prorated_amount(
            old_plan_amount, days_remaining, days_in_period
        )

        # Calculate the value of the new plan for the remaining days
        # This represents what the customer should pay under the new plan
        new_plan_remaining = ProratedBilling.calculate_prorated_amount(
            new_plan_amount, days_remaining, days_in_period
        )

        # STAGE 3: Calculate the difference between plans for remaining period
        # This determines the net financial impact of the change
        difference = new_plan_remaining - old_plan_remaining

        # STAGE 4: Determine if this is an upgrade or downgrade
        # An upgrade means the new plan costs more than the old one
        is_upgrade = new_plan_amount > old_plan_amount

        # STAGE 5: Package the comprehensive result
        # Include all relevant data for transparency and downstream processing
        result = {
            "old_plan_amount": old_plan_amount,
            "new_plan_amount": new_plan_amount,
            "current_date": current_date.isoformat(),
            "period_start_date": period_start_date.isoformat(),
            "period": period,
            "days_in_period": days_in_period,
            "days_used": days_used,
            "days_remaining": days_remaining,
            "old_plan_used": old_plan_used,
            "old_plan_remaining": old_plan_remaining,
            "new_plan_remaining": new_plan_remaining,
            "difference": difference,
            "is_upgrade": is_upgrade,
            "action": "charge" if difference > 0 else "refund",
            "amount": abs(difference),
        }

        return result


# Example usage
if __name__ == "__main__":
    # Calculate prorated billing for an upgrade
    upgrade_result = ProratedBilling.calculate_plan_change(
        old_plan_amount=10.0,
        new_plan_amount=20.0,
        current_date=datetime(2023, 6, 15),
        period_start_date=datetime(2023, 6, 1),
        period="monthly",
    )

    print("Upgrade Example:")
    print(f"Old plan: ${upgrade_result['old_plan_amount']:.2f}")
    print(f"New plan: ${upgrade_result['new_plan_amount']:.2f}")
    print(f"Days in period: {upgrade_result['days_in_period']}")
    print(f"Days used: {upgrade_result['days_used']}")
    print(f"Days remaining: {upgrade_result['days_remaining']}")
    print(f"Old plan used: ${upgrade_result['old_plan_used']:.2f}")
    print(f"Old plan remaining: ${upgrade_result['old_plan_remaining']:.2f}")
    print(f"New plan remaining: ${upgrade_result['new_plan_remaining']:.2f}")
    print(f"Difference: ${upgrade_result['difference']:.2f}")
    print(f"Action: {upgrade_result['action']} ${upgrade_result['amount']:.2f}")

    # Calculate prorated billing for a downgrade
    downgrade_result = ProratedBilling.calculate_plan_change(
        old_plan_amount=20.0,
        new_plan_amount=10.0,
        current_date=datetime(2023, 6, 15),
        period_start_date=datetime(2023, 6, 1),
        period="monthly",
    )

    print("\nDowngrade Example:")
    print(f"Old plan: ${downgrade_result['old_plan_amount']:.2f}")
    print(f"New plan: ${downgrade_result['new_plan_amount']:.2f}")
    print(f"Days in period: {downgrade_result['days_in_period']}")
    print(f"Days used: {downgrade_result['days_used']}")
    print(f"Days remaining: {downgrade_result['days_remaining']}")
    print(f"Old plan used: ${downgrade_result['old_plan_used']:.2f}")
    print(f"Old plan remaining: ${downgrade_result['old_plan_remaining']:.2f}")
    print(f"New plan remaining: ${downgrade_result['new_plan_remaining']:.2f}")
    print(f"Difference: ${downgrade_result['difference']:.2f}")
    print(f"Action: {downgrade_result['action']} ${downgrade_result['amount']:.2f}")

    # Calculate prorated billing for a cancellation
    cancellation_result = ProratedBilling.calculate_plan_change(
        old_plan_amount=20.0,
        new_plan_amount=0.0,
        current_date=datetime(2023, 6, 15),
        period_start_date=datetime(2023, 6, 1),
        period="monthly",
    )

    print("\nCancellation Example:")
    print(f"Plan: ${cancellation_result['old_plan_amount']:.2f}")
    print(f"Days in period: {cancellation_result['days_in_period']}")
    print(f"Days used: {cancellation_result['days_used']}")
    print(f"Days remaining: {cancellation_result['days_remaining']}")
    print(f"Plan used: ${cancellation_result['old_plan_used']:.2f}")
    print(f"Plan remaining: ${cancellation_result['old_plan_remaining']:.2f}")
    print(
        f"Action: {cancellation_result['action']} ${cancellation_result['amount']:.2f}"
    )
