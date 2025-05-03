"""
Interfaces for the Monetization module.

This module provides interfaces for the monetization components to enable dependency injection
and improve testability and maintainability.
"""


from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class SubscriptionStatus

(Enum):
    """Subscription status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING = "pending"
    TRIAL = "trial"


class TransactionStatus(Enum):
    """Transaction status enum."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class TransactionType(Enum):
    """Transaction type enum."""

    PAYMENT = "payment"
    REFUND = "refund"
    CREDIT = "credit"
    DEBIT = "debit"


class ISubscriptionModel(ABC):
    """Interface for subscription model."""

    @abstractmethod
    def create_subscription_tiers(
        self, solution: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create subscription tiers for a solution.

        Args:
            solution: Solution dictionary

        Returns:
            List of subscription tier dictionaries
        """
        pass

    @abstractmethod
    def calculate_pricing(
        self, solution: Dict[str, Any], tiers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate pricing for subscription tiers.

        Args:
            solution: Solution dictionary
            tiers: List of subscription tier dictionaries

        Returns:
            Pricing dictionary
        """
        pass

    @abstractmethod
    def project_revenue(
        self, solution: Dict[str, Any], tiers: List[Dict[str, Any]], users: int
    ) -> Dict[str, Any]:
        """
        Project revenue for a solution.

        Args:
            solution: Solution dictionary
            tiers: List of subscription tier dictionaries
            users: Number of users

        Returns:
            Revenue projection dictionary
        """
        pass


class IPricingCalculator(ABC):
    """Interface for pricing calculator."""

    @abstractmethod
    def calculate_price(self, costs: Dict[str, float], margin: float) -> float:
        """
        Calculate price based on costs and margin.

        Args:
            costs: Dictionary of costs
            margin: Profit margin

        Returns:
            Calculated price
        """
        pass

    @abstractmethod
    def calculate_tier_prices(
        self, base_price: float, tiers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate prices for subscription tiers.

        Args:
            base_price: Base price
            tiers: List of subscription tier dictionaries

        Returns:
            List of subscription tier dictionaries with prices
        """
        pass

    @abstractmethod
    def calculate_discount(self, price: float, discount_percentage: float) -> float:
        """
        Calculate discounted price.

        Args:
            price: Original price
            discount_percentage: Discount percentage

        Returns:
            Discounted price
        """
        pass


class IRevenueProjector(ABC):
    """Interface for revenue projector."""

    @abstractmethod
    def project_monthly_revenue(
        self, tiers: List[Dict[str, Any]], user_distribution: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Project monthly revenue.

        Args:
            tiers: List of subscription tier dictionaries
            user_distribution: Dictionary of user counts by tier

        Returns:
            Monthly revenue projection dictionary
        """
        pass

    @abstractmethod
    def project_annual_revenue(
        self,
        tiers: List[Dict[str, Any]],
        user_distribution: Dict[str, int],
        growth_rate: float,
    ) -> Dict[str, Any]:
        """
        Project annual revenue.

        Args:
            tiers: List of subscription tier dictionaries
            user_distribution: Dictionary of user counts by tier
            growth_rate: Monthly growth rate

        Returns:
            Annual revenue projection dictionary
        """
        pass

    @abstractmethod
    def calculate_lifetime_value(self, arpu: float, churn_rate: float) -> float:
        """
        Calculate customer lifetime value.

        Args:
            arpu: Average revenue per user
            churn_rate: Monthly churn rate

        Returns:
            Customer lifetime value
        """
        pass


class ISubscriptionManager(ABC):
    """Interface for subscription manager."""

    @abstractmethod
    def create_subscription(
        self, user_id: str, tier_id: str, payment_method_id: str
    ) -> Dict[str, Any]:
        """
        Create a subscription.

        Args:
            user_id: User ID
            tier_id: Subscription tier ID
            payment_method_id: Payment method ID

        Returns:
            Subscription dictionary
        """
        pass

    @abstractmethod
    def update_subscription(
        self, subscription_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a subscription.

        Args:
            subscription_id: Subscription ID
            updates: Dictionary of updates

        Returns:
            Updated subscription dictionary
        """
        pass

    @abstractmethod
    def cancel_subscription(
        self, subscription_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.

        Args:
            subscription_id: Subscription ID
            reason: Optional cancellation reason

        Returns:
            Canceled subscription dictionary
        """
        pass

    @abstractmethod
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get a subscription.

        Args:
            subscription_id: Subscription ID

        Returns:
            Subscription dictionary
        """
        pass

    @abstractmethod
    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get subscriptions for a user.

        Args:
            user_id: User ID

        Returns:
            List of subscription dictionaries
        """
        pass


class IMonetizationCalculator(ABC):
    """Interface for monetization calculator."""

    @abstractmethod
    def calculate_subscription_revenue(
        self, tiers: List[Dict[str, Any]], user_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate subscription revenue.

        Args:
            tiers: List of subscription tier dictionaries
            user_counts: Dictionary of user counts by tier

        Returns:
            Revenue dictionary
        """
        pass

    @abstractmethod
    def calculate_costs(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate costs for a solution.

        Args:
            solution: Solution dictionary

        Returns:
            Costs dictionary
        """
        pass

    @abstractmethod
    def calculate_profit(
        self, revenue: Dict[str, Any], costs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate profit.

        Args:
            revenue: Revenue dictionary
            costs: Costs dictionary

        Returns:
            Profit dictionary
        """
        pass

    @abstractmethod
    def project_growth(
        self, initial_users: int, growth_rate: float, months: int
    ) -> Dict[str, Any]:
        """
        Project user growth.

        Args:
            initial_users: Initial number of users
            growth_rate: Monthly growth rate
            months: Number of months to project

        Returns:
            Growth projection dictionary
        """
        pass