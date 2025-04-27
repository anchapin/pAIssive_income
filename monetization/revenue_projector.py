"""
Revenue Projector for the pAIssive Income project.

This module provides classes for projecting revenue for AI-powered software tools.
It includes tools for user acquisition, conversion, churn, and lifetime value calculations.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import json
import math
import copy


class RevenueProjector:
    """
    Class for projecting revenue for subscription-based software products.

    This class provides tools for calculating user acquisition, conversion rates,
    churn rates, lifetime value, and revenue projections.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        initial_users: int = 0,
        user_acquisition_rate: int = 50,
        conversion_rate: float = 0.2,
        churn_rate: float = 0.05,
        tier_distribution: Optional[Dict[str, float]] = None
    ):
        """
        Initialize a revenue projector.

        Args:
            name: Name of the revenue projector
            description: Description of the revenue projector
            initial_users: Initial number of users
            user_acquisition_rate: Number of new users per month
            conversion_rate: Conversion rate from free to paid
            churn_rate: Monthly churn rate
            tier_distribution: Distribution of users across tiers (e.g., {"basic": 0.6, "pro": 0.3, "premium": 0.1})
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.initial_users = initial_users
        self.user_acquisition_rate = user_acquisition_rate
        self.conversion_rate = conversion_rate
        self.churn_rate = churn_rate
        self.tier_distribution = tier_distribution or {"basic": 0.6, "pro": 0.3, "premium": 0.1}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def project_users(
        self,
        months: int = 36,
        growth_rate: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Project user growth over time.

        Args:
            months: Number of months to project
            growth_rate: Monthly growth rate in user acquisition

        Returns:
            List of dictionaries with user projections by month
        """
        # First, calculate the raw user numbers
        total_users = [self.initial_users]
        free_users = [self.initial_users]
        paid_users = [0]

        # Calculate user growth for each month
        current_acquisition_rate = self.user_acquisition_rate

        for month in range(1, months + 1):
            # Calculate new users this month
            new_users = current_acquisition_rate

            # Calculate churned users this month
            churned_users = int(total_users[-1] * self.churn_rate)

            # Calculate conversions from free to paid this month
            new_conversions = int(free_users[-1] * self.conversion_rate)

            # Update user counts
            new_total = total_users[-1] + new_users - churned_users
            new_paid = paid_users[-1] + new_conversions - int(paid_users[-1] * self.churn_rate)
            new_free = new_total - new_paid

            total_users.append(new_total)
            free_users.append(new_free)
            paid_users.append(new_paid)

            # Increase acquisition rate for next month
            current_acquisition_rate = int(current_acquisition_rate * (1 + growth_rate))

        # Now, format the data as expected by the tests
        user_projections = []
        for month in range(1, months + 1):
            user_projections.append({
                "month": month,
                "total_users": total_users[month],
                "free_users": free_users[month],
                "paid_users": paid_users[month],
                "new_users": current_acquisition_rate,
                "churned_users": int(total_users[month-1] * self.churn_rate),
                "conversion_rate": self.conversion_rate,
                "churn_rate": self.churn_rate
            })

        # Also store the raw data for internal use
        self._raw_user_projections = {
            "total_users": total_users,
            "free_users": free_users,
            "paid_users": paid_users,
        }

        return user_projections

    def project_revenue(
        self,
        months: int = 36,
        growth_rate: float = 0.05,
        subscription_model: Any = None,
        prices: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Project revenue over time.

        Args:
            months: Number of months to project
            growth_rate: Monthly growth rate in user acquisition
            subscription_model: Subscription model to project revenue for
            prices: Optional dictionary of tier IDs and their prices

        Returns:
            Dictionary with revenue projections by month
        """
        # Project user growth
        user_projections_list = self.project_users(months, growth_rate)

        # Use the raw user projections for internal calculations
        user_projections = self._raw_user_projections

        # Initialize revenue tracking
        monthly_revenue = [0]
        cumulative_revenue = [0]
        tier_users = {}
        tier_revenue = {}

        # If no subscription model is provided, create a simple projection
        if subscription_model is None:
            # Use tier distribution to calculate users per tier
            for month in range(1, months + 1):
                paid_users = user_projections["paid_users"][month]
                month_tier_users = {}
                month_tier_revenue = {}
                month_revenue = 0

                # Calculate users and revenue for each tier
                for tier_name, distribution in self.tier_distribution.items():
                    tier_users_count = int(paid_users * distribution)
                    month_tier_users[tier_name] = tier_users_count

                    # Use default prices if none provided
                    tier_price = 9.99
                    if tier_name.lower() == "pro":
                        tier_price = 19.99
                    elif tier_name.lower() == "premium" or tier_name.lower() == "business":
                        tier_price = 49.99

                    # Calculate revenue with proper rounding to avoid floating point issues
                    tier_rev = round(tier_users_count * tier_price, 2)
                    month_tier_revenue[tier_name] = tier_rev
                    month_revenue += tier_rev

                # Store results for this month
                tier_users[month] = month_tier_users
                tier_revenue[month] = month_tier_revenue
                monthly_revenue.append(month_revenue)
                cumulative_revenue.append(cumulative_revenue[-1] + month_revenue)
        else:
            # Get the tiers from the subscription model
            tiers = getattr(subscription_model, "tiers", [])

            # If prices not provided, extract from subscription model
            if prices is None:
                prices = {}
                for tier in tiers:
                    tier_id = tier.get("id")
                    price_monthly = tier.get("price_monthly", 0)
                    if tier_id and price_monthly > 0:
                        prices[tier_id] = price_monthly

            # Get tier IDs by name for distribution
            tier_ids_by_name = {}
            tier_names_by_id = {}
            for tier in tiers:
                if tier.get("price_monthly", 0) > 0:  # Only paid tiers
                    name = tier["name"]
                    tier_ids_by_name[name.lower()] = tier["id"]
                    tier_names_by_id[tier["id"]] = name

            # If we don't have exact matches for tier names, use the first paid tiers
            if not tier_ids_by_name:
                paid_tiers = [t for t in tiers if t.get("price_monthly", 0) > 0]
                if len(paid_tiers) >= 1:
                    tier_ids_by_name["basic"] = paid_tiers[0]["id"]
                    tier_names_by_id[paid_tiers[0]["id"]] = "Basic"
                if len(paid_tiers) >= 2:
                    tier_ids_by_name["pro"] = paid_tiers[1]["id"]
                    tier_names_by_id[paid_tiers[1]["id"]] = "Pro"
                if len(paid_tiers) >= 3:
                    tier_ids_by_name["premium"] = paid_tiers[2]["id"]
                    tier_names_by_id[paid_tiers[2]["id"]] = "Premium"

            # Calculate revenue for each month
            for month in range(1, months + 1):
                paid_users = user_projections["paid_users"][month]
                month_tier_users = {}
                month_tier_revenue = {}
                month_revenue = 0

                # Calculate revenue from each tier
                for tier_name, distribution in self.tier_distribution.items():
                    tier_name_lower = tier_name.lower()
                    if tier_name_lower in tier_ids_by_name:
                        tier_id = tier_ids_by_name[tier_name_lower]
                        display_name = tier_names_by_id.get(tier_id, tier_name)
                        tier_users_count = int(paid_users * distribution)
                        tier_price = prices.get(tier_id, 0)
                        # Calculate revenue with proper rounding to avoid floating point issues
                        tier_rev = round(tier_users_count * tier_price, 2)

                        month_tier_users[display_name] = tier_users_count
                        month_tier_revenue[display_name] = tier_rev
                        month_revenue += tier_rev

                # Store results for this month
                tier_users[month] = month_tier_users
                tier_revenue[month] = month_tier_revenue
                monthly_revenue.append(month_revenue)
                cumulative_revenue.append(cumulative_revenue[-1] + month_revenue)

        # Calculate yearly summaries
        yearly_summaries = []
        for year in range(1, (months // 12) + 1):
            start_month = (year - 1) * 12
            end_month = year * 12

            yearly_summaries.append({
                "year": year,
                "total_users": user_projections["total_users"][end_month],
                "free_users": user_projections["free_users"][end_month],
                "paid_users": user_projections["paid_users"][end_month],
                "yearly_revenue": sum(monthly_revenue[start_month + 1:end_month + 1]),
                "cumulative_revenue": cumulative_revenue[end_month],
            })

        # Create monthly projections with tier details
        monthly_projections = []
        for month in range(1, months + 1):
            monthly_projections.append({
                "month": month,
                "total_users": user_projections["total_users"][month],
                "free_users": user_projections["free_users"][month],
                "paid_users": user_projections["paid_users"][month],
                "tier_users": tier_users.get(month, {}),
                "tier_revenue": tier_revenue.get(month, {}),
                "total_revenue": monthly_revenue[month],
                "cumulative_revenue": cumulative_revenue[month]
            })

        # Store the full projection data for internal use
        self._full_projection = {
            "id": str(uuid.uuid4()),
            "subscription_model_id": getattr(subscription_model, "id", None),
            "projection_months": months,
            "growth_rate": growth_rate,
            "user_projections": user_projections,
            "monthly_revenue": monthly_revenue,
            "cumulative_revenue": cumulative_revenue,
            "monthly_projections": monthly_projections,
            "yearly_summaries": yearly_summaries,
            "total_revenue": cumulative_revenue[-1],
            "timestamp": datetime.now().isoformat(),
        }

        # Return the monthly projections as expected by the tests
        return monthly_projections

    def calculate_lifetime_value(
        self,
        average_revenue_per_user: float,
        churn_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate customer lifetime value.

        Args:
            average_revenue_per_user: Average monthly revenue per user
            churn_rate: Monthly churn rate (if None, uses the instance's churn_rate)

        Returns:
            Dictionary with lifetime value calculations
        """
        if churn_rate is None:
            churn_rate = self.churn_rate

        # Calculate average customer lifetime in months
        average_lifetime_months = 1 / churn_rate

        # Calculate lifetime value
        lifetime_value = average_revenue_per_user * average_lifetime_months

        # Calculate 1-year, 3-year, and 5-year values
        one_year_value = average_revenue_per_user * min(12, average_lifetime_months)
        three_year_value = average_revenue_per_user * min(36, average_lifetime_months)
        five_year_value = average_revenue_per_user * min(60, average_lifetime_months)

        return {
            "id": str(uuid.uuid4()),
            "average_revenue_per_user": average_revenue_per_user,
            "churn_rate": churn_rate,
            "average_lifetime_months": average_lifetime_months,
            "lifetime_value": lifetime_value,
            "one_year_value": one_year_value,
            "three_year_value": three_year_value,
            "five_year_value": five_year_value,
            "timestamp": datetime.now().isoformat(),
        }

    def calculate_payback_period(
        self,
        customer_acquisition_cost: float,
        average_revenue_per_user: float,
        gross_margin: float = 0.8
    ) -> Dict[str, Any]:
        """
        Calculate customer payback period.

        Args:
            customer_acquisition_cost: Cost to acquire a customer
            average_revenue_per_user: Average monthly revenue per user
            gross_margin: Gross margin percentage

        Returns:
            Dictionary with payback period calculations
        """
        # Calculate monthly contribution margin per user
        monthly_contribution = average_revenue_per_user * gross_margin

        # Calculate payback period in months
        payback_period_months = customer_acquisition_cost / monthly_contribution

        return {
            "id": str(uuid.uuid4()),
            "customer_acquisition_cost": customer_acquisition_cost,
            "average_revenue_per_user": average_revenue_per_user,
            "gross_margin": gross_margin,
            "monthly_contribution": monthly_contribution,
            "payback_period_months": payback_period_months,
            "timestamp": datetime.now().isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the revenue projector to a dictionary.

        Returns:
            Dictionary representation of the revenue projector
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "initial_users": self.initial_users,
            "user_acquisition_rate": self.user_acquisition_rate,
            "conversion_rate": self.conversion_rate,
            "churn_rate": self.churn_rate,
            "tier_distribution": self.tier_distribution,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the revenue projector to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the revenue projector
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, file_path: str) -> None:
        """
        Save the revenue projector to a JSON file.

        Args:
            file_path: Path to save the file
        """
        with open(file_path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'RevenueProjector':
        """
        Load a revenue projector from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            RevenueProjector instance
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        projector = cls(
            name=data["name"],
            description=data["description"],
            initial_users=data["initial_users"],
            user_acquisition_rate=data["user_acquisition_rate"],
            conversion_rate=data["conversion_rate"],
            churn_rate=data["churn_rate"],
            tier_distribution=data["tier_distribution"]
        )

        projector.id = data["id"]
        projector.created_at = data["created_at"]
        projector.updated_at = data["updated_at"]

        return projector

    def __str__(self) -> str:
        """String representation of the revenue projector."""
        return f"{self.name} (acquisition: {self.user_acquisition_rate}/month, conversion: {self.conversion_rate:.1%}, churn: {self.churn_rate:.1%})"

    def __repr__(self) -> str:
        """Detailed string representation of the revenue projector."""
        return f"RevenueProjector(id={self.id}, name={self.name}, acquisition={self.user_acquisition_rate}, conversion={self.conversion_rate:.1%}, churn={self.churn_rate:.1%})"


# Example usage
if __name__ == "__main__":
    # Import required classes
    from subscription_models import SubscriptionModel
    from pricing_calculator import PricingCalculator

    # Create a subscription model
    model = SubscriptionModel(
        name="AI Tool Subscription",
        description="Subscription model for an AI-powered tool"
    )

    # Add tiers
    basic_tier = model.add_tier(
        name="Basic",
        description="Essential features for individuals",
        price_monthly=9.99,
        target_users="Individual creators and small businesses"
    )

    pro_tier = model.add_tier(
        name="Pro",
        description="Advanced features for professionals",
        price_monthly=19.99,
        target_users="Professional content creators and marketing teams"
    )

    premium_tier = model.add_tier(
        name="Premium",
        description="All features for enterprise users",
        price_monthly=49.99,
        target_users="Enterprise teams and agencies"
    )

    # Create a pricing calculator
    calculator = PricingCalculator(
        name="AI Tool Pricing Calculator",
        description="Pricing calculator for an AI-powered tool",
        pricing_strategy="value-based"
    )

    # Calculate prices
    prices = {
        basic_tier["id"]: 9.99,
        pro_tier["id"]: 19.99,
        premium_tier["id"]: 49.99
    }

    # Create a revenue projector
    projector = RevenueProjector(
        name="AI Tool Revenue Projector",
        description="Revenue projector for an AI-powered tool",
        initial_users=0,
        user_acquisition_rate=50,
        conversion_rate=0.2,
        churn_rate=0.05,
        tier_distribution={"basic": 0.6, "pro": 0.3, "premium": 0.1}
    )

    # Project revenue
    projection = projector.project_revenue(
        subscription_model=model,
        prices=prices,
        months=36,
        growth_rate=0.05
    )

    # Print projection summary
    print(f"Revenue Projection for {model.name}")
    print(f"Projection period: {projection['projection_months']} months")
    print(f"Growth rate: {projection['growth_rate']:.1%} per month")

    print("\nYearly Summaries:")
    for year in projection["yearly_summaries"]:
        print(f"Year {year['year']}:")
        print(f"  Total Users: {year['total_users']}")
        print(f"  Paid Users: {year['paid_users']}")
        print(f"  Yearly Revenue: ${year['yearly_revenue']:.2f}")
        print(f"  Cumulative Revenue: ${year['cumulative_revenue']:.2f}")

    print(f"\nTotal Revenue: ${projection['total_revenue']:.2f}")

    # Calculate lifetime value
    average_revenue = (9.99 * 0.6 + 19.99 * 0.3 + 49.99 * 0.1)
    ltv = projector.calculate_lifetime_value(average_revenue)

    print(f"\nCustomer Lifetime Value:")
    print(f"Average Revenue Per User: ${ltv['average_revenue_per_user']:.2f}")
    print(f"Average Customer Lifetime: {ltv['average_lifetime_months']:.1f} months")
    print(f"Lifetime Value: ${ltv['lifetime_value']:.2f}")

    # Calculate payback period
    payback = projector.calculate_payback_period(
        customer_acquisition_cost=50,
        average_revenue_per_user=average_revenue
    )

    print(f"\nCustomer Payback Period:")
    print(f"Customer Acquisition Cost: ${payback['customer_acquisition_cost']:.2f}")
    print(f"Monthly Contribution: ${payback['monthly_contribution']:.2f}")
    print(f"Payback Period: {payback['payback_period_months']:.1f} months")
