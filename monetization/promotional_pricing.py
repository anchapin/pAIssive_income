"""
Promotional pricing for the pAIssive Income project.

This module provides classes for implementing promotional pricing,
including time-limited promotions, coupon codes, referral discounts,
bundle discounts, loyalty rewards, free trials, and special offers.
"""

import random
import string
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class PromotionStatus:

    pass  # Added missing block
    """Enumeration of promotion statuses."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


    class PromotionType:

    TIME_LIMITED = "time_limited"
    COUPON = "coupon"
    REFERRAL = "referral"
    BUNDLE = "bundle"
    LOYALTY = "loyalty"
    FREE_TRIAL = "free_trial"
    NEW_CUSTOMER = "new_customer"
    CUSTOM = "custom"


    class DiscountType:

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_UNITS = "free_units"
    FREE_PRODUCT = "free_product"
    CUSTOM = "custom"


    class Promotion:
    """
    Base class for promotions.

    This class provides a framework for implementing various types of
    promotional pricing, including time-limited promotions, coupon codes,
    referral discounts, and more.
    """

    def __init__(
    self,
    name: str,
    description: str,
    promotion_type: str = PromotionType.CUSTOM,
    discount_type: str = DiscountType.PERCENTAGE,
    discount_value: float = 0.0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    max_uses_per_customer: Optional[int] = None,
    min_purchase_amount: float = 0.0,
    max_discount_amount: Optional[float] = None,
    applies_to_products: Optional[List[str]] = None,
    applies_to_categories: Optional[List[str]] = None,
    applies_to_customers: Optional[List[str]] = None,
    excludes_products: Optional[List[str]] = None,
    excludes_categories: Optional[List[str]] = None,
    excludes_customers: Optional[List[str]] = None,
    stackable: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = PromotionStatus.DRAFT,
    ):
    """
    Initialize a promotion.

    Args:
    name: Name of the promotion
    description: Description of the promotion
    promotion_type: Type of promotion
    discount_type: Type of discount
    discount_value: Value of the discount
    start_date: Start date of the promotion
    end_date: End date of the promotion
    max_uses: Maximum number of uses
    max_uses_per_customer: Maximum number of uses per customer
    min_purchase_amount: Minimum purchase amount
    max_discount_amount: Maximum discount amount
    applies_to_products: List of product IDs this promotion applies to
    applies_to_categories: List of category IDs this promotion applies to
    applies_to_customers: List of customer IDs this promotion applies to
    excludes_products: List of product IDs this promotion excludes
    excludes_categories: List of category IDs this promotion excludes
    excludes_customers: List of customer IDs this promotion excludes
    stackable: Whether this promotion can be stacked with other promotions
    metadata: Additional metadata for the promotion
    status: Status of the promotion
    """
    self.id = str(uuid.uuid4())
    self.name = name
    self.description = description
    self.promotion_type = promotion_type
    self.discount_type = discount_type
    self.discount_value = discount_value
    self.start_date = start_date or datetime.now()
    self.end_date = end_date
    self.max_uses = max_uses
    self.max_uses_per_customer = max_uses_per_customer
    self.min_purchase_amount = min_purchase_amount
    self.max_discount_amount = max_discount_amount
    self.applies_to_products = applies_to_products or []
    self.applies_to_categories = applies_to_categories or []
    self.applies_to_customers = applies_to_customers or []
    self.excludes_products = excludes_products or []
    self.excludes_categories = excludes_categories or []
    self.excludes_customers = excludes_customers or []
    self.stackable = stackable
    self.metadata = metadata or {}
    self.status = status
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.usage_count = 0
    self.customer_usage = {}  # Dict[customer_id, usage_count]

    def is_valid(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
    """
    Check if the promotion is valid for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)

    Returns:
    Tuple of (is_valid, reason)
    """
    # Check status
    if self.status != PromotionStatus.ACTIVE:
    return False, f"Promotion is not active (status: {self.status})"

    # Check dates
    now = reference_time or datetime.now()

    if now < self.start_date:
    return False, f"Promotion has not started yet (starts: {self.start_date})"

    if self.end_date and now > self.end_date:
    return False, f"Promotion has expired (ended: {self.end_date})"

    # Check usage limits
    if self.max_uses is not None and self.usage_count >= self.max_uses:
    return False, f"Promotion has reached maximum uses ({self.max_uses})"

    if customer_id and self.max_uses_per_customer is not None:
    customer_usage = self.customer_usage.get(customer_id, 0)
    if customer_usage >= self.max_uses_per_customer:
    return (
    False,
    f"Customer has reached maximum uses ({self.max_uses_per_customer})",
    )

    # Check purchase amount
    if purchase_amount < self.min_purchase_amount:
    return (
    False,
    f"Purchase amount ({purchase_amount}) is below minimum ({self.min_purchase_amount})",
    )

    # Check product and category restrictions
    if product_id:
    if self.applies_to_products and product_id not in self.applies_to_products:
    return False, f"Promotion does not apply to product {product_id}"

    if product_id in self.excludes_products:
    return False, f"Promotion excludes product {product_id}"

    if category_id:
    if (
    self.applies_to_categories
    and category_id not in self.applies_to_categories
    ):
    return False, f"Promotion does not apply to category {category_id}"

    if category_id in self.excludes_categories:
    return False, f"Promotion excludes category {category_id}"

    # Check customer restrictions
    if customer_id:
    if (
    self.applies_to_customers
    and customer_id not in self.applies_to_customers
    ):
    return False, f"Promotion does not apply to customer {customer_id}"

    if customer_id in self.excludes_customers:
    return False, f"Promotion excludes customer {customer_id}"

    # All checks passed
    return True, None

    def apply_discount(
    self,
    amount: float,
    quantity: float = 1.0,
    context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, Dict[str, Any]]:
    """
    Apply the promotion discount to an amount.

    Args:
    amount: Amount to apply discount to
    quantity: Quantity of items
    context: Additional context for discount calculation

    Returns:
    Tuple of (discounted_amount, discount_info)
    """
    context = context or {}
    discount_amount = 0.0

    # Calculate discount based on type
    if self.discount_type == DiscountType.PERCENTAGE:
    # Percentage discount
    discount_amount = amount * (self.discount_value / 100.0)

    elif self.discount_type == DiscountType.FIXED_AMOUNT:
    # Fixed amount discount
    discount_amount = min(amount, self.discount_value)

    elif self.discount_type == DiscountType.FREE_UNITS:
    # Free units discount
    unit_price = amount / quantity if quantity > 0 else 0
    free_units = min(quantity, self.discount_value)
    discount_amount = unit_price * free_units

    elif self.discount_type == DiscountType.FREE_PRODUCT:
    # Free product discount
    # This is handled differently depending on the implementation
    # For now, we'll just use the discount_value as the product value
    discount_amount = self.discount_value

    elif self.discount_type == DiscountType.CUSTOM:
    # Custom discount calculation
    # This should be overridden by subclasses
    discount_amount = self.calculate_custom_discount(amount, quantity, context)

    # Apply maximum discount amount if specified
    if (
    self.max_discount_amount is not None
    and discount_amount > self.max_discount_amount
    ):
    discount_amount = self.max_discount_amount

    # Ensure discount doesn't exceed the original amount
    discount_amount = min(discount_amount, amount)

    # Calculate discounted amount
    discounted_amount = amount - discount_amount

    # Prepare discount info
    discount_info = {
    "promotion_id": self.id,
    "promotion_name": self.name,
    "original_amount": amount,
    "discount_amount": discount_amount,
    "discounted_amount": discounted_amount,
    "discount_type": self.discount_type,
    "discount_value": self.discount_value,
    }

    return discounted_amount, discount_info

    def record_usage(self, customer_id: Optional[str] = None) -> None:
    """
    Record usage of the promotion.

    Args:
    customer_id: ID of the customer
    """
    self.usage_count += 1

    if customer_id:
    self.customer_usage[customer_id] = (
    self.customer_usage.get(customer_id, 0) + 1
    )

    self.updated_at = datetime.now()

    def calculate_custom_discount(
    self,
    amount: float,
    quantity: float = 1.0,
    context: Optional[Dict[str, Any]] = None,
    ) -> float:
    """
    Calculate a custom discount.

    This method should be overridden by subclasses that use
    the CUSTOM discount type.

    Args:
    amount: Amount to apply discount to
    quantity: Quantity of items
    context: Additional context for discount calculation

    Returns:
    Discount amount
    """
    # Default implementation returns 0
    return 0.0

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the promotion to a dictionary.

    Returns:
    Dictionary representation of the promotion
    """
    return {
    "id": self.id,
    "name": self.name,
    "description": self.description,
    "promotion_type": self.promotion_type,
    "discount_type": self.discount_type,
    "discount_value": self.discount_value,
    "start_date": self.start_date.isoformat() if self.start_date else None,
    "end_date": self.end_date.isoformat() if self.end_date else None,
    "max_uses": self.max_uses,
    "max_uses_per_customer": self.max_uses_per_customer,
    "min_purchase_amount": self.min_purchase_amount,
    "max_discount_amount": self.max_discount_amount,
    "applies_to_products": self.applies_to_products,
    "applies_to_categories": self.applies_to_categories,
    "applies_to_customers": self.applies_to_customers,
    "excludes_products": self.excludes_products,
    "excludes_categories": self.excludes_categories,
    "excludes_customers": self.excludes_customers,
    "stackable": self.stackable,
    "metadata": self.metadata,
    "status": self.status,
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "usage_count": self.usage_count,
    "customer_usage": self.customer_usage,
    }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Promotion":
    """
    Create a promotion from a dictionary.

    Args:
    data: Dictionary with promotion data

    Returns:
    Promotion instance
    """
    # Convert date strings to datetime objects
    start_date = None
    if data.get("start_date"):
    start_date = datetime.fromisoformat(data["start_date"])

    end_date = None
    if data.get("end_date"):
    end_date = datetime.fromisoformat(data["end_date"])

    # Create the promotion
    promotion = cls(
    name=data["name"],
    description=data["description"],
    promotion_type=data.get("promotion_type", PromotionType.CUSTOM),
    discount_type=data.get("discount_type", DiscountType.PERCENTAGE),
    discount_value=data.get("discount_value", 0.0),
    start_date=start_date,
    end_date=end_date,
    max_uses=data.get("max_uses"),
    max_uses_per_customer=data.get("max_uses_per_customer"),
    min_purchase_amount=data.get("min_purchase_amount", 0.0),
    max_discount_amount=data.get("max_discount_amount"),
    applies_to_products=data.get("applies_to_products", []),
    applies_to_categories=data.get("applies_to_categories", []),
    applies_to_customers=data.get("applies_to_customers", []),
    excludes_products=data.get("excludes_products", []),
    excludes_categories=data.get("excludes_categories", []),
    excludes_customers=data.get("excludes_customers", []),
    stackable=data.get("stackable", False),
    metadata=data.get("metadata", {}),
    status=data.get("status", PromotionStatus.DRAFT),
    )

    # Set additional attributes
    if "id" in data:
    promotion.id = data["id"]

    if "created_at" in data:
    promotion.created_at = datetime.fromisoformat(data["created_at"])

    if "updated_at" in data:
    promotion.updated_at = datetime.fromisoformat(data["updated_at"])

    if "usage_count" in data:
    promotion.usage_count = data["usage_count"]

    if "customer_usage" in data:
    promotion.customer_usage = data["customer_usage"]

    return promotion

    def __str__(self) -> str:
    """String representation of the promotion."""
    return f"{self.__class__.__name__}({self.name}, {self.promotion_type}, {self.discount_type}, {self.discount_value})"


    class PromotionManager:
    """
    Manager for promotions.

    This class provides methods for managing and applying promotions.
    """

    def __init__(
    self,
    promotions: Optional[List[Promotion]] = None,
    allow_stacking: bool = True,
    max_stacked_promotions: Optional[int] = None,
    ):
    """
    Initialize a promotion manager.

    Args:
    promotions: List of promotions
    allow_stacking: Whether to allow stacking promotions
    max_stacked_promotions: Maximum number of stacked promotions
    """
    self.promotions = promotions or []
    self.allow_stacking = allow_stacking
    self.max_stacked_promotions = max_stacked_promotions

    def add_promotion(self, promotion: Promotion) -> None:
    """
    Add a promotion.

    Args:
    promotion: Promotion to add
    """
    self.promotions.append(promotion)

    def remove_promotion(self, promotion_id: str) -> bool:
    """
    Remove a promotion.

    Args:
    promotion_id: ID of the promotion to remove

    Returns:
    True if the promotion was removed, False otherwise
    """
    for i, promotion in enumerate(self.promotions):
    if promotion.id == promotion_id:
    self.promotions.pop(i)
    return True

    return False

    def get_promotion(self, promotion_id: str) -> Optional[Promotion]:
    """
    Get a promotion by ID.

    Args:
    promotion_id: ID of the promotion to get

    Returns:
    The promotion, or None if not found
    """
    for promotion in self.promotions:
    if promotion.id == promotion_id:
    return promotion

    return None

    def get_valid_promotions(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    ) -> List[Promotion]:
    """
    Get valid promotions for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)

    Returns:
    List of valid promotions
    """
    valid_promotions = []

    for promotion in self.promotions:
    is_valid, _ = promotion.is_valid(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=purchase_amount,
    reference_time=reference_time,
    )

    if is_valid:
    valid_promotions.append(promotion)

    return valid_promotions

    def apply_promotions(
    self,
    amount: float,
    quantity: float = 1.0,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    promotion_ids: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
    record_usage: bool = True,
    ) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Apply promotions to an amount.

    Args:
    amount: Amount to apply promotions to
    quantity: Quantity of items
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    promotion_ids: List of promotion IDs to apply (if None, all valid promotions are considered)
    context: Additional context for discount calculation
    record_usage: Whether to record usage of applied promotions

    Returns:
    Tuple of (discounted_amount, discount_info_list)
    """
    context = context or {}

    # Get valid promotions
    if promotion_ids:
    # Use specified promotions
    promotions = [p for p in self.promotions if p.id in promotion_ids]
    else:
    # Get all valid promotions
    promotions = self.get_valid_promotions(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=amount,
    )

    # Filter out non-stackable promotions if needed
    if not self.allow_stacking:
    # If stacking is not allowed, find the best promotion
    best_promotion = None
    best_discount = 0.0

    for promotion in promotions:
    discounted, discount_info = promotion.apply_discount(
    amount, quantity, context
    )
    discount_amount = discount_info["discount_amount"]

    if discount_amount > best_discount:
    best_discount = discount_amount
    best_promotion = promotion

    promotions = [best_promotion] if best_promotion else []
    else:
    # If stacking is allowed, filter out non-stackable promotions
    stackable_promotions = [p for p in promotions if p.stackable]
    non_stackable_promotions = [p for p in promotions if not p.stackable]

    if non_stackable_promotions:
    # Find the best non-stackable promotion
    best_non_stackable = None
    best_discount = 0.0

    for promotion in non_stackable_promotions:
    discounted, discount_info = promotion.apply_discount(
    amount, quantity, context
    )
    discount_amount = discount_info["discount_amount"]

    if discount_amount > best_discount:
    best_discount = discount_amount
    best_non_stackable = promotion

    # Use the best non-stackable promotion and all stackable promotions
    promotions = stackable_promotions + (
    [best_non_stackable] if best_non_stackable else []
    )
    else:
    # Use all stackable promotions
    promotions = stackable_promotions

    # Apply maximum stacked promotions limit
    if (
    self.max_stacked_promotions is not None
    and len(promotions) > self.max_stacked_promotions
    ):
    # Sort promotions by discount amount (highest first)
    promotion_discounts = []

    for promotion in promotions:
    discounted, discount_info = promotion.apply_discount(
    amount, quantity, context
    )
    discount_amount = discount_info["discount_amount"]
    promotion_discounts.append((promotion, discount_amount))

    promotion_discounts.sort(key=lambda x: x[1], reverse=True)

    # Take the top N promotions
    promotions = [
    p for p, _ in promotion_discounts[: self.max_stacked_promotions]
    ]

    # Apply promotions
    current_amount = amount
    discount_info_list = []

    for promotion in promotions:
    discounted, discount_info = promotion.apply_discount(
    current_amount, quantity, context
    )

    if discount_info["discount_amount"] > 0:
    discount_info_list.append(discount_info)
    current_amount = discounted

    if record_usage:
    promotion.record_usage(customer_id)

    return current_amount, discount_info_list

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the promotion manager to a dictionary.

    Returns:
    Dictionary representation of the promotion manager
    """
    return {
    "promotions": [p.to_dict() for p in self.promotions],
    "allow_stacking": self.allow_stacking,
    "max_stacked_promotions": self.max_stacked_promotions,
    }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromotionManager":
    """
    Create a promotion manager from a dictionary.

    Args:
    data: Dictionary with promotion manager data

    Returns:
    PromotionManager instance
    """
    promotions = []

    if "promotions" in data:
    for promotion_data in data["promotions"]:
    promotion_type = promotion_data.get(
    "promotion_type", PromotionType.CUSTOM
    )

    # Import the promotion class dynamically
    # This assumes all promotion classes are defined in this module
    promotion_class = globals().get(
    f"{promotion_type.title()}Promotion", Promotion
    )

    promotion = promotion_class.from_dict(promotion_data)
    promotions.append(promotion)

    return cls(
    promotions=promotions,
    allow_stacking=data.get("allow_stacking", True),
    max_stacked_promotions=data.get("max_stacked_promotions"),
    )


    class TimeLimitedPromotion(Promotion):
    """
    Time-limited promotion.

    This class implements a promotion that is only valid for a specific
    time period, such as a seasonal sale or limited-time offer.
    """

    def __init__(
    self,
    name: str,
    description: str,
    discount_type: str = DiscountType.PERCENTAGE,
    discount_value: float = 0.0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    max_uses_per_customer: Optional[int] = None,
    min_purchase_amount: float = 0.0,
    max_discount_amount: Optional[float] = None,
    applies_to_products: Optional[List[str]] = None,
    applies_to_categories: Optional[List[str]] = None,
    applies_to_customers: Optional[List[str]] = None,
    excludes_products: Optional[List[str]] = None,
    excludes_categories: Optional[List[str]] = None,
    excludes_customers: Optional[List[str]] = None,
    stackable: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = PromotionStatus.DRAFT,
    time_of_day_start: Optional[str] = None,
    time_of_day_end: Optional[str] = None,
    days_of_week: Optional[List[int]] = None,
    ):
    """
    Initialize a time-limited promotion.

    Args:
    name: Name of the promotion
    description: Description of the promotion
    discount_type: Type of discount
    discount_value: Value of the discount
    start_date: Start date of the promotion
    end_date: End date of the promotion
    max_uses: Maximum number of uses
    max_uses_per_customer: Maximum number of uses per customer
    min_purchase_amount: Minimum purchase amount
    max_discount_amount: Maximum discount amount
    applies_to_products: List of product IDs this promotion applies to
    applies_to_categories: List of category IDs this promotion applies to
    applies_to_customers: List of customer IDs this promotion applies to
    excludes_products: List of product IDs this promotion excludes
    excludes_categories: List of category IDs this promotion excludes
    excludes_customers: List of customer IDs this promotion excludes
    stackable: Whether this promotion can be stacked with other promotions
    metadata: Additional metadata for the promotion
    status: Status of the promotion
    time_of_day_start: Start time of day (HH:MM format)
    time_of_day_end: End time of day (HH:MM format)
    days_of_week: List of days of week (1=Monday, 7=Sunday)
    """
    super().__init__(
    name=name,
    description=description,
    promotion_type=PromotionType.TIME_LIMITED,
    discount_type=discount_type,
    discount_value=discount_value,
    start_date=start_date,
    end_date=end_date,
    max_uses=max_uses,
    max_uses_per_customer=max_uses_per_customer,
    min_purchase_amount=min_purchase_amount,
    max_discount_amount=max_discount_amount,
    applies_to_products=applies_to_products,
    applies_to_categories=applies_to_categories,
    applies_to_customers=applies_to_customers,
    excludes_products=excludes_products,
    excludes_categories=excludes_categories,
    excludes_customers=excludes_customers,
    stackable=stackable,
    metadata=metadata,
    status=status,
    )

    self.time_of_day_start = time_of_day_start
    self.time_of_day_end = time_of_day_end
    self.days_of_week = days_of_week

    def is_valid(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
    """
    Check if the promotion is valid for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)

    Returns:
    Tuple of (is_valid, reason)
    """
    # Check basic validity
    is_valid, reason = super().is_valid(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=purchase_amount,
    reference_time=reference_time,
    )

    if not is_valid:
    return False, reason

    # Check time of day
    now = reference_time or datetime.now()

    if self.time_of_day_start and self.time_of_day_end:
    current_time_str = now.strftime("%H:%M")

    if not (self.time_of_day_start <= current_time_str <= self.time_of_day_end):
    return (
    False,
    f"Promotion is not valid at this time of day (valid: {self.time_of_day_start} to {self.time_of_day_end})",
    )

    # Check day of week
    if self.days_of_week:
    current_day = now.isoweekday()  # 1=Monday, 7=Sunday

    if current_day not in self.days_of_week:
    return (
    False,
    f"Promotion is not valid on this day of week (valid days: {self.days_of_week})",
    )

    # All checks passed
    return True, None

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the time-limited promotion to a dictionary.

    Returns:
    Dictionary representation of the time-limited promotion
    """
    result = super().to_dict()
    result.update(
    {
    "time_of_day_start": self.time_of_day_start,
    "time_of_day_end": self.time_of_day_end,
    "days_of_week": self.days_of_week,
    }
    )
    return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeLimitedPromotion":
    """
    Create a time-limited promotion from a dictionary.

    Args:
    data: Dictionary with time-limited promotion data

    Returns:
    TimeLimitedPromotion instance
    """
    # Convert date strings to datetime objects
    start_date = None
    if data.get("start_date"):
    start_date = datetime.fromisoformat(data["start_date"])

    end_date = None
    if data.get("end_date"):
    end_date = datetime.fromisoformat(data["end_date"])

    # Create the promotion
    promotion = cls(
    name=data["name"],
    description=data["description"],
    discount_type=data.get("discount_type", DiscountType.PERCENTAGE),
    discount_value=data.get("discount_value", 0.0),
    start_date=start_date,
    end_date=end_date,
    max_uses=data.get("max_uses"),
    max_uses_per_customer=data.get("max_uses_per_customer"),
    min_purchase_amount=data.get("min_purchase_amount", 0.0),
    max_discount_amount=data.get("max_discount_amount"),
    applies_to_products=data.get("applies_to_products", []),
    applies_to_categories=data.get("applies_to_categories", []),
    applies_to_customers=data.get("applies_to_customers", []),
    excludes_products=data.get("excludes_products", []),
    excludes_categories=data.get("excludes_categories", []),
    excludes_customers=data.get("excludes_customers", []),
    stackable=data.get("stackable", False),
    metadata=data.get("metadata", {}),
    status=data.get("status", PromotionStatus.DRAFT),
    time_of_day_start=data.get("time_of_day_start"),
    time_of_day_end=data.get("time_of_day_end"),
    days_of_week=data.get("days_of_week"),
    )

    # Set additional attributes
    if "id" in data:
    promotion.id = data["id"]

    if "created_at" in data:
    promotion.created_at = datetime.fromisoformat(data["created_at"])

    if "updated_at" in data:
    promotion.updated_at = datetime.fromisoformat(data["updated_at"])

    if "usage_count" in data:
    promotion.usage_count = data["usage_count"]

    if "customer_usage" in data:
    promotion.customer_usage = data["customer_usage"]

    return promotion


    class CouponPromotion(Promotion):
    """
    Coupon promotion.

    This class implements a promotion that is activated by a coupon code,
    such as a discount code or voucher.
    """

    def __init__(
    self,
    name: str,
    description: str,
    code: str,
    discount_type: str = DiscountType.PERCENTAGE,
    discount_value: float = 0.0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    max_uses_per_customer: Optional[int] = None,
    min_purchase_amount: float = 0.0,
    max_discount_amount: Optional[float] = None,
    applies_to_products: Optional[List[str]] = None,
    applies_to_categories: Optional[List[str]] = None,
    applies_to_customers: Optional[List[str]] = None,
    excludes_products: Optional[List[str]] = None,
    excludes_categories: Optional[List[str]] = None,
    excludes_customers: Optional[List[str]] = None,
    stackable: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = PromotionStatus.DRAFT,
    case_sensitive: bool = False,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    valid_codes: Optional[List[str]] = None,
    ):
    """
    Initialize a coupon promotion.

    Args:
    name: Name of the promotion
    description: Description of the promotion
    code: Coupon code
    discount_type: Type of discount
    discount_value: Value of the discount
    start_date: Start date of the promotion
    end_date: End date of the promotion
    max_uses: Maximum number of uses
    max_uses_per_customer: Maximum number of uses per customer
    min_purchase_amount: Minimum purchase amount
    max_discount_amount: Maximum discount amount
    applies_to_products: List of product IDs this promotion applies to
    applies_to_categories: List of category IDs this promotion applies to
    applies_to_customers: List of customer IDs this promotion applies to
    excludes_products: List of product IDs this promotion excludes
    excludes_categories: List of category IDs this promotion excludes
    excludes_customers: List of customer IDs this promotion excludes
    stackable: Whether this promotion can be stacked with other promotions
    metadata: Additional metadata for the promotion
    status: Status of the promotion
    case_sensitive: Whether the coupon code is case sensitive
    prefix: Prefix for the coupon code
    suffix: Suffix for the coupon code
    valid_codes: List of valid coupon codes (if None, only the main code is valid)
    """
    super().__init__(
    name=name,
    description=description,
    promotion_type=PromotionType.COUPON,
    discount_type=discount_type,
    discount_value=discount_value,
    start_date=start_date,
    end_date=end_date,
    max_uses=max_uses,
    max_uses_per_customer=max_uses_per_customer,
    min_purchase_amount=min_purchase_amount,
    max_discount_amount=max_discount_amount,
    applies_to_products=applies_to_products,
    applies_to_categories=applies_to_categories,
    applies_to_customers=applies_to_customers,
    excludes_products=excludes_products,
    excludes_categories=excludes_categories,
    excludes_customers=excludes_customers,
    stackable=stackable,
    metadata=metadata,
    status=status,
    )

    self.code = code
    self.case_sensitive = case_sensitive
    self.prefix = prefix
    self.suffix = suffix
    self.valid_codes = valid_codes or [code]
    self.used_codes = {}  # Dict[code, usage_count]

    def is_valid_code(self, code: str) -> bool:
    """
    Check if a coupon code is valid.

    Args:
    code: Coupon code to check

    Returns:
    True if the code is valid, False otherwise
    """
    if not self.case_sensitive:
    code = code.upper()
    valid_codes = [c.upper() for c in self.valid_codes]
    else:
    valid_codes = self.valid_codes

    # Check if the code matches exactly
    if code in valid_codes:
    return True

    # Check if the code matches with prefix/suffix
    if self.prefix and self.suffix:
    # Check if the code has the correct prefix and suffix
    if code.startswith(self.prefix) and code.endswith(self.suffix):
    # Extract the middle part
    middle = code[len(self.prefix) : -len(self.suffix)]

    # Check if the middle part is valid
    if middle.isalnum():
    return True
    elif self.prefix:
    # Check if the code has the correct prefix
    if code.startswith(self.prefix):
    # Extract the rest
    rest = code[len(self.prefix) :]

    # Check if the rest is valid
    if rest.isalnum():
    return True
    elif self.suffix:
    # Check if the code has the correct suffix
    if code.endswith(self.suffix):
    # Extract the rest
    rest = code[: -len(self.suffix)]

    # Check if the rest is valid
    if rest.isalnum():
    return True

    return False

    def is_valid(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    code: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
    """
    Check if the promotion is valid for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)
    code: Coupon code to check

    Returns:
    Tuple of (is_valid, reason)
    """
    # Check basic validity
    is_valid, reason = super().is_valid(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=purchase_amount,
    reference_time=reference_time,
    )

    if not is_valid:
    return False, reason

    # Check coupon code
    if code is not None:
    if not self.is_valid_code(code):
    return False, f"Invalid coupon code: {code}"

    # Check if the code has reached its maximum uses
    if self.max_uses is not None:
    code_usage = self.used_codes.get(code, 0)
    if code_usage >= self.max_uses:
    return False, f"Coupon code has reached maximum uses: {code}"

    # All checks passed
    return True, None

    def record_usage(
    self, customer_id: Optional[str] = None, code: Optional[str] = None
    ) -> None:
    """
    Record usage of the promotion.

    Args:
    customer_id: ID of the customer
    code: Coupon code that was used
    """
    super().record_usage(customer_id)

    if code:
    self.used_codes[code] = self.used_codes.get(code, 0) + 1

    def generate_codes(
    self,
    count: int,
    length: int = 8,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    characters: str = string.ascii_uppercase + string.digits,
    ) -> List[str]:
    """
    Generate random coupon codes.

    Args:
    count: Number of codes to generate
    length: Length of each code
    prefix: Prefix for the codes
    suffix: Suffix for the codes
    characters: Characters to use for the codes

    Returns:
    List of generated codes
    """
    prefix = prefix or self.prefix or ""
    suffix = suffix or self.suffix or ""

    codes = []

    for _ in range(count):
    # Generate a random code
    code = "".join(random.choice(characters) for _ in range(length))

    # Add prefix and suffix
    full_code = f"{prefix}{code}{suffix}"

    codes.append(full_code)

    # Add the generated codes to the valid codes
    self.valid_codes.extend(codes)

    return codes

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the coupon promotion to a dictionary.

    Returns:
    Dictionary representation of the coupon promotion
    """
    result = super().to_dict()
    result.update(
    {
    "code": self.code,
    "case_sensitive": self.case_sensitive,
    "prefix": self.prefix,
    "suffix": self.suffix,
    "valid_codes": self.valid_codes,
    "used_codes": self.used_codes,
    }
    )
    return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouponPromotion":
    """
    Create a coupon promotion from a dictionary.

    Args:
    data: Dictionary with coupon promotion data

    Returns:
    CouponPromotion instance
    """
    # Convert date strings to datetime objects
    start_date = None
    if data.get("start_date"):
    start_date = datetime.fromisoformat(data["start_date"])

    end_date = None
    if data.get("end_date"):
    end_date = datetime.fromisoformat(data["end_date"])

    # Create the promotion
    promotion = cls(
    name=data["name"],
    description=data["description"],
    code=data["code"],
    discount_type=data.get("discount_type", DiscountType.PERCENTAGE),
    discount_value=data.get("discount_value", 0.0),
    start_date=start_date,
    end_date=end_date,
    max_uses=data.get("max_uses"),
    max_uses_per_customer=data.get("max_uses_per_customer"),
    min_purchase_amount=data.get("min_purchase_amount", 0.0),
    max_discount_amount=data.get("max_discount_amount"),
    applies_to_products=data.get("applies_to_products", []),
    applies_to_categories=data.get("applies_to_categories", []),
    applies_to_customers=data.get("applies_to_customers", []),
    excludes_products=data.get("excludes_products", []),
    excludes_categories=data.get("excludes_categories", []),
    excludes_customers=data.get("excludes_customers", []),
    stackable=data.get("stackable", False),
    metadata=data.get("metadata", {}),
    status=data.get("status", PromotionStatus.DRAFT),
    case_sensitive=data.get("case_sensitive", False),
    prefix=data.get("prefix"),
    suffix=data.get("suffix"),
    valid_codes=data.get("valid_codes"),
    )

    # Set additional attributes
    if "id" in data:
    promotion.id = data["id"]

    if "created_at" in data:
    promotion.created_at = datetime.fromisoformat(data["created_at"])

    if "updated_at" in data:
    promotion.updated_at = datetime.fromisoformat(data["updated_at"])

    if "usage_count" in data:
    promotion.usage_count = data["usage_count"]

    if "customer_usage" in data:
    promotion.customer_usage = data["customer_usage"]

    if "used_codes" in data:
    promotion.used_codes = data["used_codes"]

    return promotion


    class ReferralPromotion(Promotion):
    """
    Referral promotion.

    This class implements a promotion that rewards customers for referring
    new customers, such as a refer-a-friend discount.
    """

    def __init__(
    self,
    name: str,
    description: str,
    referrer_discount_type: str = DiscountType.PERCENTAGE,
    referrer_discount_value: float = 0.0,
    referee_discount_type: str = DiscountType.PERCENTAGE,
    referee_discount_value: float = 0.0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    max_uses_per_customer: Optional[int] = None,
    min_purchase_amount: float = 0.0,
    max_discount_amount: Optional[float] = None,
    applies_to_products: Optional[List[str]] = None,
    applies_to_categories: Optional[List[str]] = None,
    applies_to_customers: Optional[List[str]] = None,
    excludes_products: Optional[List[str]] = None,
    excludes_categories: Optional[List[str]] = None,
    excludes_customers: Optional[List[str]] = None,
    stackable: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = PromotionStatus.DRAFT,
    referral_code_prefix: str = "REF-",
    referral_code_length: int = 8,
    min_referee_purchase_amount: float = 0.0,
    referee_max_uses: int = 1,
    require_referee_account: bool = True,
    ):
    """
    Initialize a referral promotion.

    Args:
    name: Name of the promotion
    description: Description of the promotion
    referrer_discount_type: Type of discount for the referrer
    referrer_discount_value: Value of the discount for the referrer
    referee_discount_type: Type of discount for the referee
    referee_discount_value: Value of the discount for the referee
    start_date: Start date of the promotion
    end_date: End date of the promotion
    max_uses: Maximum number of uses
    max_uses_per_customer: Maximum number of uses per customer
    min_purchase_amount: Minimum purchase amount
    max_discount_amount: Maximum discount amount
    applies_to_products: List of product IDs this promotion applies to
    applies_to_categories: List of category IDs this promotion applies to
    applies_to_customers: List of customer IDs this promotion applies to
    excludes_products: List of product IDs this promotion excludes
    excludes_categories: List of category IDs this promotion excludes
    excludes_customers: List of customer IDs this promotion excludes
    stackable: Whether this promotion can be stacked with other promotions
    metadata: Additional metadata for the promotion
    status: Status of the promotion
    referral_code_prefix: Prefix for referral codes
    referral_code_length: Length of referral codes
    min_referee_purchase_amount: Minimum purchase amount for referees
    referee_max_uses: Maximum number of uses per referee
    require_referee_account: Whether referees must create an account
    """
    super().__init__(
    name=name,
    description=description,
    promotion_type=PromotionType.REFERRAL,
    discount_type=referrer_discount_type,  # Use referrer discount type as the main discount type
    discount_value=referrer_discount_value,  # Use referrer discount value as the main discount value
    start_date=start_date,
    end_date=end_date,
    max_uses=max_uses,
    max_uses_per_customer=max_uses_per_customer,
    min_purchase_amount=min_purchase_amount,
    max_discount_amount=max_discount_amount,
    applies_to_products=applies_to_products,
    applies_to_categories=applies_to_categories,
    applies_to_customers=applies_to_customers,
    excludes_products=excludes_products,
    excludes_categories=excludes_categories,
    excludes_customers=excludes_customers,
    stackable=stackable,
    metadata=metadata,
    status=status,
    )

    self.referrer_discount_type = referrer_discount_type
    self.referrer_discount_value = referrer_discount_value
    self.referee_discount_type = referee_discount_type
    self.referee_discount_value = referee_discount_value
    self.referral_code_prefix = referral_code_prefix
    self.referral_code_length = referral_code_length
    self.min_referee_purchase_amount = min_referee_purchase_amount
    self.referee_max_uses = referee_max_uses
    self.require_referee_account = require_referee_account

    self.referral_codes = {}  # Dict[customer_id, referral_code]
    self.referrals = {}  # Dict[referral_code, List[referee_id]]
    self.referee_usage = {}  # Dict[referee_id, usage_count]

    def generate_referral_code(self, customer_id: str) -> str:
    """
    Generate a referral code for a customer.

    Args:
    customer_id: ID of the customer

    Returns:
    Referral code
    """
    # Check if the customer already has a referral code
    if customer_id in self.referral_codes:
    return self.referral_codes[customer_id]

    # Generate a random code
    code = "".join(
    random.choice(string.ascii_uppercase + string.digits)
    for _ in range(self.referral_code_length)
    )

    # Add prefix
    full_code = f"{self.referral_code_prefix}{code}"

    # Store the code
    self.referral_codes[customer_id] = full_code

    return full_code

    def get_referral_code(self, customer_id: str) -> Optional[str]:
    """
    Get the referral code for a customer.

    Args:
    customer_id: ID of the customer

    Returns:
    Referral code, or None if not found
    """
    return self.referral_codes.get(customer_id)

    def get_referrer_id(self, referral_code: str) -> Optional[str]:
    """
    Get the ID of the referrer for a referral code.

    Args:
    referral_code: Referral code

    Returns:
    ID of the referrer, or None if not found
    """
    for customer_id, code in self.referral_codes.items():
    if code == referral_code:
    return customer_id

    return None

    def record_referral(self, referral_code: str, referee_id: str) -> bool:
    """
    Record a referral.

    Args:
    referral_code: Referral code
    referee_id: ID of the referee

    Returns:
    True if the referral was recorded, False otherwise
    """
    # Check if the referral code is valid
    referrer_id = self.get_referrer_id(referral_code)

    if not referrer_id:
    return False

    # Check if the referee has already been referred
    for code, referees in self.referrals.items():
    if referee_id in referees:
    return False

    # Record the referral
    if referral_code not in self.referrals:
    self.referrals[referral_code] = []

    self.referrals[referral_code].append(referee_id)

    return True

    def get_referrals(self, customer_id: str) -> List[str]:
    """
    Get the referrals for a customer.

    Args:
    customer_id: ID of the customer

    Returns:
    List of referee IDs
    """
    referral_code = self.get_referral_code(customer_id)

    if not referral_code:
    return []

    return self.referrals.get(referral_code, [])

    def is_valid(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    referral_code: Optional[str] = None,
    is_referee: bool = False,
    ) -> Tuple[bool, Optional[str]]:
    """
    Check if the promotion is valid for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)
    referral_code: Referral code
    is_referee: Whether the customer is a referee

    Returns:
    Tuple of (is_valid, reason)
    """
    # Check basic validity
    is_valid, reason = super().is_valid(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=purchase_amount,
    reference_time=reference_time,
    )

    if not is_valid:
    return False, reason

    if is_referee:
    # Check referee-specific conditions
    if purchase_amount < self.min_referee_purchase_amount:
    return (
    False,
    f"Purchase amount ({purchase_amount}) is below minimum for referees ({self.min_referee_purchase_amount})",
    )

    if customer_id:
    # Check if the referee has reached maximum uses
    referee_usage = self.referee_usage.get(customer_id, 0)
    if referee_usage >= self.referee_max_uses:
    return (
    False,
    f"Referee has reached maximum uses ({self.referee_max_uses})",
    )

    if referral_code:
    # Check if the referral code is valid
    referrer_id = self.get_referrer_id(referral_code)
    if not referrer_id:
    return False, f"Invalid referral code: {referral_code}"

    # Check if the referrer is the same as the referee
    if referrer_id == customer_id:
    return False, "Referrer cannot be the same as referee"
    else:
    # Check referrer-specific conditions
    if customer_id:
    # Check if the customer has any referrals
    referrals = self.get_referrals(customer_id)
    if not referrals:
    return False, "Customer has no referrals"

    # All checks passed
    return True, None

    def apply_discount(
    self,
    amount: float,
    quantity: float = 1.0,
    context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, Dict[str, Any]]:
    """
    Apply the promotion discount to an amount.

    Args:
    amount: Amount to apply discount to
    quantity: Quantity of items
    context: Additional context for discount calculation

    Returns:
    Tuple of (discounted_amount, discount_info)
    """
    context = context or {}
    is_referee = context.get("is_referee", False)

    if is_referee:
    # Use referee discount
    discount_type = self.referee_discount_type
    discount_value = self.referee_discount_value
    else:
    # Use referrer discount
    discount_type = self.referrer_discount_type
    discount_value = self.referrer_discount_value

    # Calculate discount based on type
    discount_amount = 0.0

    if discount_type == DiscountType.PERCENTAGE:
    # Percentage discount
    discount_amount = amount * (discount_value / 100.0)

    elif discount_type == DiscountType.FIXED_AMOUNT:
    # Fixed amount discount
    discount_amount = min(amount, discount_value)

    elif discount_type == DiscountType.FREE_UNITS:
    # Free units discount
    unit_price = amount / quantity if quantity > 0 else 0
    free_units = min(quantity, discount_value)
    discount_amount = unit_price * free_units

    elif discount_type == DiscountType.FREE_PRODUCT:
    # Free product discount
    # This is handled differently depending on the implementation
    # For now, we'll just use the discount_value as the product value
    discount_amount = discount_value

    # Apply maximum discount amount if specified
    if (
    self.max_discount_amount is not None
    and discount_amount > self.max_discount_amount
    ):
    discount_amount = self.max_discount_amount

    # Ensure discount doesn't exceed the original amount
    discount_amount = min(discount_amount, amount)

    # Calculate discounted amount
    discounted_amount = amount - discount_amount

    # Prepare discount info
    discount_info = {
    "promotion_id": self.id,
    "promotion_name": self.name,
    "original_amount": amount,
    "discount_amount": discount_amount,
    "discounted_amount": discounted_amount,
    "discount_type": discount_type,
    "discount_value": discount_value,
    "is_referee": is_referee,
    }

    return discounted_amount, discount_info

    def record_usage(
    self,
    customer_id: Optional[str] = None,
    referral_code: Optional[str] = None,
    is_referee: bool = False,
    ) -> None:
    """
    Record usage of the promotion.

    Args:
    customer_id: ID of the customer
    referral_code: Referral code
    is_referee: Whether the customer is a referee
    """
    super().record_usage(customer_id)

    if is_referee and customer_id:
    self.referee_usage[customer_id] = self.referee_usage.get(customer_id, 0) + 1

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the referral promotion to a dictionary.

    Returns:
    Dictionary representation of the referral promotion
    """
    result = super().to_dict()
    result.update(
    {
    "referrer_discount_type": self.referrer_discount_type,
    "referrer_discount_value": self.referrer_discount_value,
    "referee_discount_type": self.referee_discount_type,
    "referee_discount_value": self.referee_discount_value,
    "referral_code_prefix": self.referral_code_prefix,
    "referral_code_length": self.referral_code_length,
    "min_referee_purchase_amount": self.min_referee_purchase_amount,
    "referee_max_uses": self.referee_max_uses,
    "require_referee_account": self.require_referee_account,
    "referral_codes": self.referral_codes,
    "referrals": self.referrals,
    "referee_usage": self.referee_usage,
    }
    )
    return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferralPromotion":
    """
    Create a referral promotion from a dictionary.

    Args:
    data: Dictionary with referral promotion data

    Returns:
    ReferralPromotion instance
    """
    # Convert date strings to datetime objects
    start_date = None
    if data.get("start_date"):
    start_date = datetime.fromisoformat(data["start_date"])

    end_date = None
    if data.get("end_date"):
    end_date = datetime.fromisoformat(data["end_date"])

    # Create the promotion
    promotion = cls(
    name=data["name"],
    description=data["description"],
    referrer_discount_type=data.get(
    "referrer_discount_type", DiscountType.PERCENTAGE
    ),
    referrer_discount_value=data.get("referrer_discount_value", 0.0),
    referee_discount_type=data.get(
    "referee_discount_type", DiscountType.PERCENTAGE
    ),
    referee_discount_value=data.get("referee_discount_value", 0.0),
    start_date=start_date,
    end_date=end_date,
    max_uses=data.get("max_uses"),
    max_uses_per_customer=data.get("max_uses_per_customer"),
    min_purchase_amount=data.get("min_purchase_amount", 0.0),
    max_discount_amount=data.get("max_discount_amount"),
    applies_to_products=data.get("applies_to_products", []),
    applies_to_categories=data.get("applies_to_categories", []),
    applies_to_customers=data.get("applies_to_customers", []),
    excludes_products=data.get("excludes_products", []),
    excludes_categories=data.get("excludes_categories", []),
    excludes_customers=data.get("excludes_customers", []),
    stackable=data.get("stackable", False),
    metadata=data.get("metadata", {}),
    status=data.get("status", PromotionStatus.DRAFT),
    referral_code_prefix=data.get("referral_code_prefix", "REF-"),
    referral_code_length=data.get("referral_code_length", 8),
    min_referee_purchase_amount=data.get("min_referee_purchase_amount", 0.0),
    referee_max_uses=data.get("referee_max_uses", 1),
    require_referee_account=data.get("require_referee_account", True),
    )

    # Set additional attributes
    if "id" in data:
    promotion.id = data["id"]

    if "created_at" in data:
    promotion.created_at = datetime.fromisoformat(data["created_at"])

    if "updated_at" in data:
    promotion.updated_at = datetime.fromisoformat(data["updated_at"])

    if "usage_count" in data:
    promotion.usage_count = data["usage_count"]

    if "customer_usage" in data:
    promotion.customer_usage = data["customer_usage"]

    if "referral_codes" in data:
    promotion.referral_codes = data["referral_codes"]

    if "referrals" in data:
    promotion.referrals = data["referrals"]

    if "referee_usage" in data:
    promotion.referee_usage = data["referee_usage"]

    return promotion


    class BundlePromotion(Promotion):
    """
    Bundle promotion.

    This class implements a promotion that offers discounts for purchasing
    multiple products together, such as a bundle discount.
    """

    def __init__(
    self,
    name: str,
    description: str,
    bundle_items: List[Dict[str, Any]],
    discount_type: str = DiscountType.PERCENTAGE,
    discount_value: float = 0.0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    max_uses_per_customer: Optional[int] = None,
    min_purchase_amount: float = 0.0,
    max_discount_amount: Optional[float] = None,
    applies_to_products: Optional[List[str]] = None,
    applies_to_categories: Optional[List[str]] = None,
    applies_to_customers: Optional[List[str]] = None,
    excludes_products: Optional[List[str]] = None,
    excludes_categories: Optional[List[str]] = None,
    excludes_customers: Optional[List[str]] = None,
    stackable: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = PromotionStatus.DRAFT,
    require_all_items: bool = True,
    min_quantity_per_item: int = 1,
    apply_to_cheapest: bool = False,
    apply_to_most_expensive: bool = False,
    ):
    """
    Initialize a bundle promotion.

    Args:
    name: Name of the promotion
    description: Description of the promotion
    bundle_items: List of items in the bundle, each with product_id and quantity
    discount_type: Type of discount
    discount_value: Value of the discount
    start_date: Start date of the promotion
    end_date: End date of the promotion
    max_uses: Maximum number of uses
    max_uses_per_customer: Maximum number of uses per customer
    min_purchase_amount: Minimum purchase amount
    max_discount_amount: Maximum discount amount
    applies_to_products: List of product IDs this promotion applies to
    applies_to_categories: List of category IDs this promotion applies to
    applies_to_customers: List of customer IDs this promotion applies to
    excludes_products: List of product IDs this promotion excludes
    excludes_categories: List of category IDs this promotion excludes
    excludes_customers: List of customer IDs this promotion excludes
    stackable: Whether this promotion can be stacked with other promotions
    metadata: Additional metadata for the promotion
    status: Status of the promotion
    require_all_items: Whether all items in the bundle are required
    min_quantity_per_item: Minimum quantity per item
    apply_to_cheapest: Whether to apply the discount to the cheapest item
    apply_to_most_expensive: Whether to apply the discount to the most expensive item
    """
    super().__init__(
    name=name,
    description=description,
    promotion_type=PromotionType.BUNDLE,
    discount_type=discount_type,
    discount_value=discount_value,
    start_date=start_date,
    end_date=end_date,
    max_uses=max_uses,
    max_uses_per_customer=max_uses_per_customer,
    min_purchase_amount=min_purchase_amount,
    max_discount_amount=max_discount_amount,
    applies_to_products=applies_to_products,
    applies_to_categories=applies_to_categories,
    applies_to_customers=applies_to_customers,
    excludes_products=excludes_products,
    excludes_categories=excludes_categories,
    excludes_customers=excludes_customers,
    stackable=stackable,
    metadata=metadata,
    status=status,
    )

    self.bundle_items = bundle_items
    self.require_all_items = require_all_items
    self.min_quantity_per_item = min_quantity_per_item
    self.apply_to_cheapest = apply_to_cheapest
    self.apply_to_most_expensive = apply_to_most_expensive

    def is_valid(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    cart_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[bool, Optional[str]]:
    """
    Check if the promotion is valid for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)
    cart_items: List of items in the cart, each with product_id, quantity, and price

    Returns:
    Tuple of (is_valid, reason)
    """
    # Check basic validity
    is_valid, reason = super().is_valid(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=purchase_amount,
    reference_time=reference_time,
    )

    if not is_valid:
    return False, reason

    # Check bundle-specific conditions
    if not cart_items:
    return False, "No cart items provided"

    # Check if the cart contains the required bundle items
    if self.require_all_items:
    # All items in the bundle must be in the cart with the required quantity
    for bundle_item in self.bundle_items:
    bundle_product_id = bundle_item["product_id"]
    bundle_quantity = bundle_item.get(
    "quantity", self.min_quantity_per_item
    )

    # Find the item in the cart
    cart_item = next(
    (
    item
    for item in cart_items
    if item["product_id"] == bundle_product_id
    ),
    None,
    )

    if not cart_item:
    return False, f"Bundle item {bundle_product_id} not in cart"

    if cart_item["quantity"] < bundle_quantity:
    return (
    False,
    f"Bundle item {bundle_product_id} quantity ({cart_item['quantity']}) is less than required ({bundle_quantity})",
    )
    else:
    # At least one item in the bundle must be in the cart with the required quantity
    valid_items = 0

    for bundle_item in self.bundle_items:
    bundle_product_id = bundle_item["product_id"]
    bundle_quantity = bundle_item.get(
    "quantity", self.min_quantity_per_item
    )

    # Find the item in the cart
    cart_item = next(
    (
    item
    for item in cart_items
    if item["product_id"] == bundle_product_id
    ),
    None,
    )

    if cart_item and cart_item["quantity"] >= bundle_quantity:
    valid_items += 1

    if valid_items == 0:
    return False, "No valid bundle items in cart"

    # All checks passed
    return True, None

    def apply_discount(
    self,
    amount: float,
    quantity: float = 1.0,
    context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, Dict[str, Any]]:
    """
    Apply the promotion discount to an amount.

    Args:
    amount: Amount to apply discount to
    quantity: Quantity of items
    context: Additional context for discount calculation

    Returns:
    Tuple of (discounted_amount, discount_info)
    """
    context = context or {}
    cart_items = context.get("cart_items", [])

    # If no cart items, use the standard discount calculation
    if not cart_items:
    return super().apply_discount(amount, quantity, context)

    # Calculate the discount based on the bundle configuration
    discount_amount = 0.0

    if self.apply_to_cheapest:
    # Apply the discount to the cheapest item in the bundle
    bundle_product_ids = [item["product_id"] for item in self.bundle_items]
    bundle_cart_items = [
    item for item in cart_items if item["product_id"] in bundle_product_ids
    ]

    if bundle_cart_items:
    # Sort by price (cheapest first)
    bundle_cart_items.sort(key=lambda item: item["price"])

    # Get the cheapest item
    cheapest_item = bundle_cart_items[0]

    # Calculate the discount for the cheapest item
    if self.discount_type == DiscountType.PERCENTAGE:
    discount_amount = (
    cheapest_item["price"]
    * cheapest_item["quantity"]
    * (self.discount_value / 100.0)
    )
    elif self.discount_type == DiscountType.FIXED_AMOUNT:
    discount_amount = min(
    cheapest_item["price"] * cheapest_item["quantity"],
    self.discount_value,
    )
    elif self.discount_type == DiscountType.FREE_UNITS:
    free_units = min(cheapest_item["quantity"], self.discount_value)
    discount_amount = cheapest_item["price"] * free_units
    elif self.discount_type == DiscountType.FREE_PRODUCT:
    discount_amount = self.discount_value

    elif self.apply_to_most_expensive:
    # Apply the discount to the most expensive item in the bundle
    bundle_product_ids = [item["product_id"] for item in self.bundle_items]
    bundle_cart_items = [
    item for item in cart_items if item["product_id"] in bundle_product_ids
    ]

    if bundle_cart_items:
    # Sort by price (most expensive first)
    bundle_cart_items.sort(key=lambda item: item["price"], reverse=True)

    # Get the most expensive item
    most_expensive_item = bundle_cart_items[0]

    # Calculate the discount for the most expensive item
    if self.discount_type == DiscountType.PERCENTAGE:
    discount_amount = (
    most_expensive_item["price"]
    * most_expensive_item["quantity"]
    * (self.discount_value / 100.0)
    )
    elif self.discount_type == DiscountType.FIXED_AMOUNT:
    discount_amount = min(
    most_expensive_item["price"] * most_expensive_item["quantity"],
    self.discount_value,
    )
    elif self.discount_type == DiscountType.FREE_UNITS:
    free_units = min(
    most_expensive_item["quantity"], self.discount_value
    )
    discount_amount = most_expensive_item["price"] * free_units
    elif self.discount_type == DiscountType.FREE_PRODUCT:
    discount_amount = self.discount_value

    else:
    # Apply the discount to the entire purchase amount
    if self.discount_type == DiscountType.PERCENTAGE:
    discount_amount = amount * (self.discount_value / 100.0)
    elif self.discount_type == DiscountType.FIXED_AMOUNT:
    discount_amount = min(amount, self.discount_value)
    elif self.discount_type == DiscountType.FREE_UNITS:
    # This doesn't make sense for the entire purchase, so we'll just use a percentage
    discount_amount = amount * (self.discount_value / 100.0)
    elif self.discount_type == DiscountType.FREE_PRODUCT:
    discount_amount = self.discount_value

    # Apply maximum discount amount if specified
    if (
    self.max_discount_amount is not None
    and discount_amount > self.max_discount_amount
    ):
    discount_amount = self.max_discount_amount

    # Ensure discount doesn't exceed the original amount
    discount_amount = min(discount_amount, amount)

    # Calculate discounted amount
    discounted_amount = amount - discount_amount

    # Prepare discount info
    discount_info = {
    "promotion_id": self.id,
    "promotion_name": self.name,
    "original_amount": amount,
    "discount_amount": discount_amount,
    "discounted_amount": discounted_amount,
    "discount_type": self.discount_type,
    "discount_value": self.discount_value,
    "bundle_items": self.bundle_items,
    "apply_to_cheapest": self.apply_to_cheapest,
    "apply_to_most_expensive": self.apply_to_most_expensive,
    }

    return discounted_amount, discount_info

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the bundle promotion to a dictionary.

    Returns:
    Dictionary representation of the bundle promotion
    """
    result = super().to_dict()
    result.update(
    {
    "bundle_items": self.bundle_items,
    "require_all_items": self.require_all_items,
    "min_quantity_per_item": self.min_quantity_per_item,
    "apply_to_cheapest": self.apply_to_cheapest,
    "apply_to_most_expensive": self.apply_to_most_expensive,
    }
    )
    return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BundlePromotion":
    """
    Create a bundle promotion from a dictionary.

    Args:
    data: Dictionary with bundle promotion data

    Returns:
    BundlePromotion instance
    """
    # Convert date strings to datetime objects
    start_date = None
    if data.get("start_date"):
    start_date = datetime.fromisoformat(data["start_date"])

    end_date = None
    if data.get("end_date"):
    end_date = datetime.fromisoformat(data["end_date"])

    # Create the promotion
    promotion = cls(
    name=data["name"],
    description=data["description"],
    bundle_items=data.get("bundle_items", []),
    discount_type=data.get("discount_type", DiscountType.PERCENTAGE),
    discount_value=data.get("discount_value", 0.0),
    start_date=start_date,
    end_date=end_date,
    max_uses=data.get("max_uses"),
    max_uses_per_customer=data.get("max_uses_per_customer"),
    min_purchase_amount=data.get("min_purchase_amount", 0.0),
    max_discount_amount=data.get("max_discount_amount"),
    applies_to_products=data.get("applies_to_products", []),
    applies_to_categories=data.get("applies_to_categories", []),
    applies_to_customers=data.get("applies_to_customers", []),
    excludes_products=data.get("excludes_products", []),
    excludes_categories=data.get("excludes_categories", []),
    excludes_customers=data.get("excludes_customers", []),
    stackable=data.get("stackable", False),
    metadata=data.get("metadata", {}),
    status=data.get("status", PromotionStatus.DRAFT),
    require_all_items=data.get("require_all_items", True),
    min_quantity_per_item=data.get("min_quantity_per_item", 1),
    apply_to_cheapest=data.get("apply_to_cheapest", False),
    apply_to_most_expensive=data.get("apply_to_most_expensive", False),
    )

    # Set additional attributes
    if "id" in data:
    promotion.id = data["id"]

    if "created_at" in data:
    promotion.created_at = datetime.fromisoformat(data["created_at"])

    if "updated_at" in data:
    promotion.updated_at = datetime.fromisoformat(data["updated_at"])

    if "usage_count" in data:
    promotion.usage_count = data["usage_count"]

    if "customer_usage" in data:
    promotion.customer_usage = data["customer_usage"]

    return promotion


    class LoyaltyPromotion(Promotion):
    """
    Loyalty promotion.

    This class implements a promotion that rewards customers for their loyalty,
    such as discounts based on purchase history or account age.
    """

    def __init__(
    self,
    name: str,
    description: str,
    loyalty_tiers: List[Dict[str, Any]],
    discount_type: str = DiscountType.PERCENTAGE,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    max_uses_per_customer: Optional[int] = None,
    min_purchase_amount: float = 0.0,
    max_discount_amount: Optional[float] = None,
    applies_to_products: Optional[List[str]] = None,
    applies_to_categories: Optional[List[str]] = None,
    applies_to_customers: Optional[List[str]] = None,
    excludes_products: Optional[List[str]] = None,
    excludes_categories: Optional[List[str]] = None,
    excludes_customers: Optional[List[str]] = None,
    stackable: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = PromotionStatus.DRAFT,
    loyalty_criteria: str = "purchase_count",
    reset_period: Optional[str] = None,
    ):
    """
    Initialize a loyalty promotion.

    Args:
    name: Name of the promotion
    description: Description of the promotion
    loyalty_tiers: List of loyalty tiers, each with min_value, max_value, and discount_value
    discount_type: Type of discount
    start_date: Start date of the promotion
    end_date: End date of the promotion
    max_uses: Maximum number of uses
    max_uses_per_customer: Maximum number of uses per customer
    min_purchase_amount: Minimum purchase amount
    max_discount_amount: Maximum discount amount
    applies_to_products: List of product IDs this promotion applies to
    applies_to_categories: List of category IDs this promotion applies to
    applies_to_customers: List of customer IDs this promotion applies to
    excludes_products: List of product IDs this promotion excludes
    excludes_categories: List of category IDs this promotion excludes
    excludes_customers: List of customer IDs this promotion excludes
    stackable: Whether this promotion can be stacked with other promotions
    metadata: Additional metadata for the promotion
    status: Status of the promotion
    loyalty_criteria: Criteria for loyalty (purchase_count, purchase_amount, account_age)
    reset_period: Period after which loyalty resets (monthly, yearly, never)
    """
    # Use the highest tier's discount value as the default discount value
    default_discount_value = 0.0
    if loyalty_tiers:
    # Sort tiers by min_value (ascending)
    sorted_tiers = sorted(loyalty_tiers, key=lambda t: t.get("min_value", 0))
    # Use the highest tier's discount value
    default_discount_value = sorted_tiers[-1].get("discount_value", 0.0)

    super().__init__(
    name=name,
    description=description,
    promotion_type=PromotionType.LOYALTY,
    discount_type=discount_type,
    discount_value=default_discount_value,  # Will be overridden based on tier
    start_date=start_date,
    end_date=end_date,
    max_uses=max_uses,
    max_uses_per_customer=max_uses_per_customer,
    min_purchase_amount=min_purchase_amount,
    max_discount_amount=max_discount_amount,
    applies_to_products=applies_to_products,
    applies_to_categories=applies_to_categories,
    applies_to_customers=applies_to_customers,
    excludes_products=excludes_products,
    excludes_categories=excludes_categories,
    excludes_customers=excludes_customers,
    stackable=stackable,
    metadata=metadata,
    status=status,
    )

    self.loyalty_tiers = loyalty_tiers
    self.loyalty_criteria = loyalty_criteria
    self.reset_period = reset_period
    self.customer_loyalty = {}  # Dict[customer_id, Dict[criteria, value]]
    self.last_reset = {}  # Dict[customer_id, datetime]

    def get_customer_loyalty(self, customer_id: str) -> Dict[str, Any]:
    """
    Get the loyalty data for a customer.

    Args:
    customer_id: ID of the customer

    Returns:
    Dictionary with loyalty data
    """
    return self.customer_loyalty.get(customer_id, {})

    def update_customer_loyalty(
    self,
    customer_id: str,
    purchase_count: int = 0,
    purchase_amount: float = 0.0,
    account_age: int = 0,
    ) -> None:
    """
    Update the loyalty data for a customer.

    Args:
    customer_id: ID of the customer
    purchase_count: Number of purchases to add
    purchase_amount: Purchase amount to add
    account_age: Account age in days
    """
    # Initialize customer loyalty if not exists
    if customer_id not in self.customer_loyalty:
    self.customer_loyalty[customer_id] = {
    "purchase_count": 0,
    "purchase_amount": 0.0,
    "account_age": 0,
    "last_updated": datetime.now(),
    }

    # Check if we need to reset loyalty
    if self.should_reset_loyalty(customer_id):
    self.reset_customer_loyalty(customer_id)

    # Update loyalty data
    loyalty = self.customer_loyalty[customer_id]
    loyalty["purchase_count"] += purchase_count
    loyalty["purchase_amount"] += purchase_amount
    loyalty["account_age"] = max(loyalty["account_age"], account_age)
    loyalty["last_updated"] = datetime.now()

    # Update last reset time if needed
    if customer_id not in self.last_reset:
    self.last_reset[customer_id] = datetime.now()

    def should_reset_loyalty(self, customer_id: str) -> bool:
    """
    Check if loyalty should be reset for a customer.

    Args:
    customer_id: ID of the customer

    Returns:
    True if loyalty should be reset, False otherwise
    """
    if not self.reset_period or self.reset_period == "never":
    return False

    if customer_id not in self.last_reset:
    return False

    last_reset = self.last_reset[customer_id]
    now = datetime.now()

    if self.reset_period == "monthly":
    # Reset if we're in a different month
    return now.year != last_reset.year or now.month != last_reset.month

    elif self.reset_period == "yearly":
    # Reset if we're in a different year
    return now.year != last_reset.year

    return False

    def reset_customer_loyalty(self, customer_id: str) -> None:
    """
    Reset the loyalty data for a customer.

    Args:
    customer_id: ID of the customer
    """
    if customer_id in self.customer_loyalty:
    # Keep account age, reset everything else
    account_age = self.customer_loyalty[customer_id].get("account_age", 0)

    self.customer_loyalty[customer_id] = {
    "purchase_count": 0,
    "purchase_amount": 0.0,
    "account_age": account_age,
    "last_updated": datetime.now(),
    }

    self.last_reset[customer_id] = datetime.now()

    def get_loyalty_tier(self, customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the loyalty tier for a customer.

    Args:
    customer_id: ID of the customer

    Returns:
    Loyalty tier dictionary, or None if not found
    """
    loyalty = self.get_customer_loyalty(customer_id)

    if not loyalty:
    return None

    # Get the value based on the loyalty criteria
    value = 0

    if self.loyalty_criteria == "purchase_count":
    value = loyalty.get("purchase_count", 0)
    elif self.loyalty_criteria == "purchase_amount":
    value = loyalty.get("purchase_amount", 0.0)
    elif self.loyalty_criteria == "account_age":
    value = loyalty.get("account_age", 0)

    # Find the matching tier
    matching_tier = None

    for tier in self.loyalty_tiers:
    min_value = tier.get("min_value", 0)
    max_value = tier.get("max_value")

    if min_value <= value and (max_value is None or value <= max_value):
    matching_tier = tier

    return matching_tier

    def is_valid(
    self,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    category_id: Optional[str] = None,
    purchase_amount: float = 0.0,
    reference_time: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
    """
    Check if the promotion is valid for a given context.

    Args:
    customer_id: ID of the customer
    product_id: ID of the product
    category_id: ID of the category
    purchase_amount: Purchase amount
    reference_time: Reference time (defaults to now)

    Returns:
    Tuple of (is_valid, reason)
    """
    # Check basic validity
    is_valid, reason = super().is_valid(
    customer_id=customer_id,
    product_id=product_id,
    category_id=category_id,
    purchase_amount=purchase_amount,
    reference_time=reference_time,
    )

    if not is_valid:
    return False, reason

    # Check loyalty-specific conditions
    if not customer_id:
    return False, "Customer ID is required for loyalty promotions"

    # Check if the customer has loyalty data
    loyalty = self.get_customer_loyalty(customer_id)

    if not loyalty:
    return False, "Customer has no loyalty data"

    # Check if the customer qualifies for any tier
    tier = self.get_loyalty_tier(customer_id)

    if not tier:
    return False, "Customer does not qualify for any loyalty tier"

    # All checks passed
    return True, None

    def apply_discount(
    self,
    amount: float,
    quantity: float = 1.0,
    context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, Dict[str, Any]]:
    """
    Apply the promotion discount to an amount.

    Args:
    amount: Amount to apply discount to
    quantity: Quantity of items
    context: Additional context for discount calculation

    Returns:
    Tuple of (discounted_amount, discount_info)
    """
    context = context or {}
    customer_id = context.get("customer_id")

    # If no customer ID, use the standard discount calculation
    if not customer_id:
    return super().apply_discount(amount, quantity, context)

    # Get the customer's loyalty tier
    tier = self.get_loyalty_tier(customer_id)

    if not tier:
    # No tier, no discount
    return amount, {
    "promotion_id": self.id,
    "promotion_name": self.name,
    "original_amount": amount,
    "discount_amount": 0.0,
    "discounted_amount": amount,
    "discount_type": self.discount_type,
    "discount_value": 0.0,
    "tier": None,
    }

    # Use the tier's discount value
    discount_value = tier.get("discount_value", 0.0)

    # Calculate discount based on type
    discount_amount = 0.0

    if self.discount_type == DiscountType.PERCENTAGE:
    # Percentage discount
    discount_amount = amount * (discount_value / 100.0)

    elif self.discount_type == DiscountType.FIXED_AMOUNT:
    # Fixed amount discount
    discount_amount = min(amount, discount_value)

    elif self.discount_type == DiscountType.FREE_UNITS:
    # Free units discount
    unit_price = amount / quantity if quantity > 0 else 0
    free_units = min(quantity, discount_value)
    discount_amount = unit_price * free_units

    elif self.discount_type == DiscountType.FREE_PRODUCT:
    # Free product discount
    # This is handled differently depending on the implementation
    # For now, we'll just use the discount_value as the product value
    discount_amount = discount_value

    # Apply maximum discount amount if specified
    if (
    self.max_discount_amount is not None
    and discount_amount > self.max_discount_amount
    ):
    discount_amount = self.max_discount_amount

    # Ensure discount doesn't exceed the original amount
    discount_amount = min(discount_amount, amount)

    # Calculate discounted amount
    discounted_amount = amount - discount_amount

    # Prepare discount info
    discount_info = {
    "promotion_id": self.id,
    "promotion_name": self.name,
    "original_amount": amount,
    "discount_amount": discount_amount,
    "discounted_amount": discounted_amount,
    "discount_type": self.discount_type,
    "discount_value": discount_value,
    "tier": tier,
    "loyalty_criteria": self.loyalty_criteria,
    "loyalty_value": self.get_customer_loyalty(customer_id).get(
    self.loyalty_criteria, 0
    ),
    }

    return discounted_amount, discount_info

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the loyalty promotion to a dictionary.

    Returns:
    Dictionary representation of the loyalty promotion
    """
    result = super().to_dict()
    result.update(
    {
    "loyalty_tiers": self.loyalty_tiers,
    "loyalty_criteria": self.loyalty_criteria,
    "reset_period": self.reset_period,
    "customer_loyalty": self.customer_loyalty,
    "last_reset": {k: v.isoformat() for k, v in self.last_reset.items()},
    }
    )
    return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoyaltyPromotion":
    """
    Create a loyalty promotion from a dictionary.

    Args:
    data: Dictionary with loyalty promotion data

    Returns:
    LoyaltyPromotion instance
    """
    # Convert date strings to datetime objects
    start_date = None
    if data.get("start_date"):
    start_date = datetime.fromisoformat(data["start_date"])

    end_date = None
    if data.get("end_date"):
    end_date = datetime.fromisoformat(data["end_date"])

    # Create the promotion
    promotion = cls(
    name=data["name"],
    description=data["description"],
    loyalty_tiers=data.get("loyalty_tiers", []),
    discount_type=data.get("discount_type", DiscountType.PERCENTAGE),
    start_date=start_date,
    end_date=end_date,
    max_uses=data.get("max_uses"),
    max_uses_per_customer=data.get("max_uses_per_customer"),
    min_purchase_amount=data.get("min_purchase_amount", 0.0),
    max_discount_amount=data.get("max_discount_amount"),
    applies_to_products=data.get("applies_to_products", []),
    applies_to_categories=data.get("applies_to_categories", []),
    applies_to_customers=data.get("applies_to_customers", []),
    excludes_products=data.get("excludes_products", []),
    excludes_categories=data.get("excludes_categories", []),
    excludes_customers=data.get("excludes_customers", []),
    stackable=data.get("stackable", False),
    metadata=data.get("metadata", {}),
    status=data.get("status", PromotionStatus.DRAFT),
    loyalty_criteria=data.get("loyalty_criteria", "purchase_count"),
    reset_period=data.get("reset_period"),
    )

    # Set additional attributes
    if "id" in data:
    promotion.id = data["id"]

    if "created_at" in data:
    promotion.created_at = datetime.fromisoformat(data["created_at"])

    if "updated_at" in data:
    promotion.updated_at = datetime.fromisoformat(data["updated_at"])

    if "usage_count" in data:
    promotion.usage_count = data["usage_count"]

    if "customer_usage" in data:
    promotion.customer_usage = data["customer_usage"]

    if "customer_loyalty" in data:
    promotion.customer_loyalty = data["customer_loyalty"]

    if "last_reset" in data:
    promotion.last_reset = {
    k: datetime.fromisoformat(v) for k, v in data["last_reset"].items()
    }

    return promotion


    # Example usage
    if __name__ == "__main__":
    # Create a time-limited promotion
    time_promotion = TimeLimitedPromotion(
    name="Summer Sale",
    description="20% off all products for the summer",
    discount_type=DiscountType.PERCENTAGE,
    discount_value=20.0,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=90),
    time_of_day_start="09:00",
    time_of_day_end="17:00",
    days_of_week=[1, 2, 3, 4, 5],  # Monday to Friday
    status=PromotionStatus.ACTIVE,
    )

    # Create a coupon promotion
    coupon_promotion = CouponPromotion(
    name="Welcome Discount",
    description="15% off your first purchase",
    code="WELCOME15",
    discount_type=DiscountType.PERCENTAGE,
    discount_value=15.0,
    max_uses_per_customer=1,
    status=PromotionStatus.ACTIVE,
    )

    # Create a referral promotion
    referral_promotion = ReferralPromotion(
    name="Refer a Friend",
    description="Get $10 off when a friend signs up, and they get 20% off their first purchase",
    referrer_discount_type=DiscountType.FIXED_AMOUNT,
    referrer_discount_value=10.0,
    referee_discount_type=DiscountType.PERCENTAGE,
    referee_discount_value=20.0,
    status=PromotionStatus.ACTIVE,
    )

    # Create a bundle promotion
    bundle_promotion = BundlePromotion(
    name="API Bundle",
    description="Buy 3 API products and get 25% off",
    bundle_items=[
    {"product_id": "api_product_1", "quantity": 1},
    {"product_id": "api_product_2", "quantity": 1},
    {"product_id": "api_product_3", "quantity": 1},
    ],
    discount_type=DiscountType.PERCENTAGE,
    discount_value=25.0,
    require_all_items=True,
    status=PromotionStatus.ACTIVE,
    )

    # Create a loyalty promotion
    loyalty_promotion = LoyaltyPromotion(
    name="Loyalty Rewards",
    description="Get increasing discounts based on your purchase history",
    loyalty_tiers=[
    {
    "min_value": 0,
    "max_value": 4,
    "discount_value": 5.0,
    },  # 5% off for 0-4 purchases
    {
    "min_value": 5,
    "max_value": 9,
    "discount_value": 10.0,
    },  # 10% off for 5-9 purchases
    {
    "min_value": 10,
    "max_value": None,
    "discount_value": 15.0,
    },  # 15% off for 10+ purchases
    ],
    discount_type=DiscountType.PERCENTAGE,
    loyalty_criteria="purchase_count",
    reset_period="yearly",
    status=PromotionStatus.ACTIVE,
    )

    # Update customer loyalty
    customer_id = "customer123"
    loyalty_promotion.update_customer_loyalty(
    customer_id=customer_id,
    purchase_count=7,  # This should put the customer in the second tier
    purchase_amount=500.0,
    account_age=180,
    )

    # Create a promotion manager
    manager = PromotionManager(allow_stacking=True)

    # Add the promotions
    manager.add_promotion(time_promotion)
    manager.add_promotion(coupon_promotion)
    manager.add_promotion(referral_promotion)
    manager.add_promotion(bundle_promotion)
    manager.add_promotion(loyalty_promotion)

    # Apply the loyalty promotion
    discounted_amount, discount_info = manager.apply_promotions(
    amount=100.0,
    customer_id=customer_id,
    promotion_ids=[loyalty_promotion.id],
    context={"customer_id": customer_id},
    )

    print(f"Customer loyalty: {loyalty_promotion.get_customer_loyalty(customer_id)}")
    print(f"Customer loyalty tier: {loyalty_promotion.get_loyalty_tier(customer_id)}")
    print("Original amount: $100.00")
    print(f"Discounted amount (loyalty): ${discounted_amount:.2f}")
    print(f"Discount info: {discount_info}")

    # Create a cart with bundle items
    cart_items = [
    {"product_id": "api_product_1", "quantity": 1, "price": 50.0},
    {"product_id": "api_product_2", "quantity": 2, "price": 75.0},
    {"product_id": "api_product_3", "quantity": 1, "price": 100.0},
    ]

    # Calculate the cart total
    cart_total = sum(item["price"] * item["quantity"] for item in cart_items)

    # Apply multiple promotions
    discounted_amount, discount_info = manager.apply_promotions(
    amount=cart_total,
    customer_id=customer_id,
    context={"customer_id": customer_id, "cart_items": cart_items},
    )

    print(f"\nCart total: ${cart_total:.2f}")
    print(f"Discounted amount (all promotions): ${discounted_amount:.2f}")
    print(f"Discount info: {discount_info}")