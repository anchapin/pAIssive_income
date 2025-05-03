"""
Subscription management for the pAIssive Income project.

This module provides classes for managing subscription plans, tiers, and user subscriptions.
It includes tools for subscription lifecycle management and payment processing.
"""


import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class FeatureWrapper

:
    """
    Wrapper class for feature dictionaries to provide attribute access.
    """

    def __init__(self, feature_dict: Dict[str, Any]):
        """
        Initialize a feature wrapper.

        Args:
            feature_dict: Dictionary containing feature data
        """
        self._feature = feature_dict

        # Copy common attributes directly to avoid recursion
        self.id = feature_dict.get("id")
        self.name = feature_dict.get("name")
        self.description = feature_dict.get("description")
        self.type = feature_dict.get("type")
        self.value_type = feature_dict.get("value_type")
        self.category = feature_dict.get("category")
        self.value = feature_dict.get("value", True)
        self.limit = feature_dict.get("limit")
        self.created_at = feature_dict.get("created_at")
        self.updated_at = feature_dict.get("updated_at")

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the feature dictionary.

        Args:
            name: Name of the attribute

        Returns:
            Value of the attribute
        """
        if name.startswith("_"):
            return super().__getattr__(name)

        if name in self._feature:
            return self._feature[name]
        raise AttributeError(f"'FeatureWrapper' object has no attribute '{name}'")

    def __getitem__(self, key: str) -> Any:
        """
        Get an item from the feature dictionary.

        Args:
            key: Key to get

        Returns:
            Value of the key
        """
        return self._feature[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an item in the feature dictionary.

        Args:
            key: Key to set
            value: Value to set
        """
        self._feature[key] = value

        # Update direct attribute if it exists
        if hasattr(self, key):
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an item from the feature dictionary with a default value.

        Args:
            key: Key to get
            default: Default value if key not found

        Returns:
            Value of the key or default
        """
        return self._feature.get(key, default)


class TierWrapper:
    """
    Wrapper class for tier dictionaries to provide attribute access.
    """

    def __init__(self, tier_dict: Dict[str, Any]):
        """
        Initialize a tier wrapper.

        Args:
            tier_dict: Dictionary containing tier data
        """
        self._tier = tier_dict

        # Copy common attributes directly to avoid recursion
        self.id = tier_dict.get("id")
        self.name = tier_dict.get("name")
        self.description = tier_dict.get("description")
        self.price_monthly = tier_dict.get("price_monthly")
        self.price_annual = tier_dict.get("price_annual")
        self.target_users = tier_dict.get("target_users")
        self.is_popular = tier_dict.get("is_popular")
        self.is_hidden = tier_dict.get("is_hidden")
        self.max_users = tier_dict.get("max_users")
        self.trial_days = tier_dict.get("trial_days")
        self.created_at = tier_dict.get("created_at")
        self.updated_at = tier_dict.get("updated_at")

        # Handle features separately to avoid recursion
        self.features = tier_dict.get("features", [])

        # Handle limits separately
        self.limits = tier_dict.get("limits", {})

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the tier dictionary.

        Args:
            name: Name of the attribute

        Returns:
            Value of the attribute
        """
        if name.startswith("_"):
            return super().__getattr__(name)

        if name in self._tier:
            return self._tier[name]
        raise AttributeError(f"'TierWrapper' object has no attribute '{name}'")

    def __getitem__(self, key: str) -> Any:
        """
        Get an item from the tier dictionary.

        Args:
            key: Key to get

        Returns:
            Value of the key
        """
        return self._tier[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an item in the tier dictionary.

        Args:
            key: Key to set
            value: Value to set
        """
        self._tier[key] = value

        # Update direct attribute if it exists
        if hasattr(self, key):
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an item from the tier dictionary with a default value.

        Args:
            key: Key to get
            default: Default value if key not found

        Returns:
            Value of the key or default
        """
        return self._tier.get(key, default)


class SubscriptionPlan:
    """
    Base class for subscription plans.

    A subscription plan defines the overall structure of a subscription offering,
    including tiers, features, and billing options.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        billing_cycles: Optional[List[str]] = None,
        features: Optional[List[Dict[str, Any]]] = None,
        tiers: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize a subscription plan.

        Args:
            name: Name of the subscription plan
            description: Description of the subscription plan
            billing_cycles: Available billing cycles (e.g., ["monthly", "annual"])
            features: List of features available in the plan
            tiers: List of subscription tiers
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.billing_cycles = billing_cycles or ["monthly", "annual"]
        self.features = features or []
        self.tiers = tiers or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_feature(
        self,
        name: str,
        description: str = "",
        type: str = "boolean",
        value_type: str = "string",
        category: str = "general",
    ) -> Dict[str, Any]:
        """
        Add a feature to the subscription plan.

        Args:
            name: Name of the feature
            description: Description of the feature
            type: Type of feature (boolean, quantity, access)
            value_type: Type of value (string, number, boolean)
            category: Category of the feature

        Returns:
            The created feature
        """
        feature = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "type": type,
            "value_type": value_type,
            "category": category,
            "created_at": datetime.now().isoformat(),
        }

        self.features.append(feature)
        self.updated_at = datetime.now().isoformat()

        return feature

    def get_feature(
        self, feature_id: str
    ) -> Optional[Union[Dict[str, Any], FeatureWrapper]]:
        """
        Get a feature by ID.

        Args:
            feature_id: ID of the feature

        Returns:
            The feature or None if not found
        """
        for feature in self.features:
            if isinstance(feature, FeatureWrapper):
                if feature.id == feature_id:
                    return feature
            elif feature["id"] == feature_id:
                return feature

        return None

    def update_feature(
        self,
        feature_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[str] = None,
        value_type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a feature.

        Args:
            feature_id: ID of the feature to update
            name: New name of the feature
            description: New description of the feature
            type: New type of feature
            value_type: New type of value
            category: New category of the feature

        Returns:
            The updated feature or None if not found
        """
        feature = self.get_feature(feature_id)

        if feature:
            if name is not None:
                feature["name"] = name

            if description is not None:
                feature["description"] = description

            if type is not None:
                feature["type"] = type

            if value_type is not None:
                feature["value_type"] = value_type

            if category is not None:
                feature["category"] = category

            feature["updated_at"] = datetime.now().isoformat()
            self.updated_at = datetime.now().isoformat()

            return feature

        return None

    def remove_feature(self, feature_id: str) -> bool:
        """
        Remove a feature from the subscription plan.

        Args:
            feature_id: ID of the feature to remove

        Returns:
            True if the feature was removed, False otherwise
        """
        for i, feature in enumerate(self.features):
            if feature["id"] == feature_id:
                self.features.pop(i)
                self.updated_at = datetime.now().isoformat()

                # Also remove the feature from all tiers
                for tier in self.tiers:
                    if "features" in tier:
                        tier["features"] = [
                            f for f in tier["features"] if f["feature_id"] != feature_id
                        ]

                return True

        return False

    def add_tier(
        self,
        name: str,
        description: str = "",
        price_monthly: float = 0.0,
        price_annual: Optional[float] = None,
        features: Optional[List[Dict[str, Any]]] = None,
        target_users: str = "",
        is_popular: bool = False,
        is_hidden: bool = False,
        max_users: Optional[int] = None,
        trial_days: int = 0,
    ) -> Dict[str, Any]:
        """
        Add a tier to the subscription plan.

        Args:
            name: Name of the tier
            description: Description of the tier
            price_monthly: Monthly price of the tier
            price_annual: Annual price of the tier (if None, calculated as monthly * 10)
            features: List of features included in the tier
            target_users: Description of target users for this tier
            is_popular: Whether this tier is marked as popular
            is_hidden: Whether this tier is hidden from public view
            max_users: Maximum number of users allowed in this tier
            trial_days: Number of trial days for this tier

        Returns:
            The created tier
        """
        # Calculate annual price if not provided
        if price_annual is None and price_monthly > 0:
            price_annual = price_monthly * 10  # 2 months free
        elif price_annual is None:
            price_annual = 0.0

        tier = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "price_monthly": price_monthly,
            "price_annual": price_annual,
            "features": features or [],
            "target_users": target_users,
            "is_popular": is_popular,
            "is_hidden": is_hidden,
            "max_users": max_users,
            "trial_days": trial_days,
            "created_at": datetime.now().isoformat(),
        }

        self.tiers.append(tier)
        self.updated_at = datetime.now().isoformat()

        return tier

    def get_tier(self, tier_id: str) -> Optional[Union[Dict[str, Any], TierWrapper]]:
        """
        Get a tier by ID.

        Args:
            tier_id: ID of the tier

        Returns:
            The tier or None if not found
        """
        for tier in self.tiers:
            if isinstance(tier, TierWrapper):
                if tier.id == tier_id:
                    return tier
            elif tier["id"] == tier_id:
                return tier

        return None

    def update_tier(
        self,
        tier_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price_monthly: Optional[float] = None,
        price_annual: Optional[float] = None,
        target_users: Optional[str] = None,
        is_popular: Optional[bool] = None,
        is_hidden: Optional[bool] = None,
        max_users: Optional[int] = None,
        trial_days: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a tier.

        Args:
            tier_id: ID of the tier to update
            name: New name of the tier
            description: New description of the tier
            price_monthly: New monthly price of the tier
            price_annual: New annual price of the tier
            target_users: New description of target users
            is_popular: New popular status
            is_hidden: New hidden status
            max_users: New maximum number of users
            trial_days: New number of trial days

        Returns:
            The updated tier or None if not found
        """
        tier = self.get_tier(tier_id)

        if tier:
            if name is not None:
                tier["name"] = name

            if description is not None:
                tier["description"] = description

            if price_monthly is not None:
                tier["price_monthly"] = price_monthly

                # Update annual price if monthly price changed and annual price not specified
                if price_annual is None and price_monthly > 0:
                    tier["price_annual"] = price_monthly * 10  # 2 months free

            if price_annual is not None:
                tier["price_annual"] = price_annual

            if target_users is not None:
                tier["target_users"] = target_users

            if is_popular is not None:
                tier["is_popular"] = is_popular

            if is_hidden is not None:
                tier["is_hidden"] = is_hidden

            if max_users is not None:
                tier["max_users"] = max_users

            if trial_days is not None:
                tier["trial_days"] = trial_days

            tier["updated_at"] = datetime.now().isoformat()
            self.updated_at = datetime.now().isoformat()

            return tier

        return None

    def remove_tier(self, tier_id: str) -> bool:
        """
        Remove a tier from the subscription plan.

        Args:
            tier_id: ID of the tier to remove

        Returns:
            True if the tier was removed, False otherwise
        """
        for i, tier in enumerate(self.tiers):
            if tier["id"] == tier_id:
                self.tiers.pop(i)
                self.updated_at = datetime.now().isoformat()
                return True

        return False

    def add_feature_to_tier(
        self,
        tier_id: str,
        feature_id: str,
        value: Any = True,
        limit: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Add a feature to a tier.

        Args:
            tier_id: ID of the tier
            feature_id: ID of the feature
            value: Value of the feature for this tier
            limit: Limit for quantity-based features

        Returns:
            The updated tier or None if not found
        """
        tier = self.get_tier(tier_id)
        feature = self.get_feature(feature_id)

        if tier and feature:
            # Check if feature already exists in tier
            for i, f in enumerate(tier["features"]):
                if f["feature_id"] == feature_id:
                    # Update existing feature
                    tier["features"][i]["value"] = value
                    if limit is not None:
                        tier["features"][i]["limit"] = limit

                    tier["updated_at"] = datetime.now().isoformat()
                    self.updated_at = datetime.now().isoformat()

                    return tier

            # Add new feature to tier
            tier_feature = {"feature_id": feature_id, "value": value}

            if limit is not None:
                tier_feature["limit"] = limit

            tier["features"].append(tier_feature)
            tier["updated_at"] = datetime.now().isoformat()
            self.updated_at = datetime.now().isoformat()

            return tier

        return None

    def remove_feature_from_tier(self, tier_id: str, feature_id: str) -> bool:
        """
        Remove a feature from a tier.

        Args:
            tier_id: ID of the tier
            feature_id: ID of the feature

        Returns:
            True if the feature was removed, False otherwise
        """
        tier = self.get_tier(tier_id)

        if tier:
            for i, feature in enumerate(tier["features"]):
                if feature["feature_id"] == feature_id:
                    tier["features"].pop(i)
                    tier["updated_at"] = datetime.now().isoformat()
                    self.updated_at = datetime.now().isoformat()
                    return True

        return False

    def get_tier_features(
        self, tier_id: str
    ) -> List[Union[Dict[str, Any], FeatureWrapper]]:
        """
        Get all features for a tier with their details.

        Args:
            tier_id: ID of the tier

        Returns:
            List of features with their details
        """
        tier = self.get_tier(tier_id)

        if not tier:
            return []

        result = []

        # Get the features list from the tier
        tier_features = []
        if isinstance(tier, dict):
            tier_features = tier.get("features", [])
        elif isinstance(tier, TierWrapper):
            tier_features = tier.features
        else:
            return []

        for tier_feature in tier_features:
            # Get the feature ID
            feature_id = None
            if isinstance(tier_feature, dict):
                feature_id = tier_feature.get("feature_id")
            elif hasattr(tier_feature, "feature_id"):
                feature_id = tier_feature.feature_id
            else:
                continue

            # Get the feature
            feature = self.get_feature(feature_id)

            if feature:
                # Get the value and limit
                value = True
                limit = None

                if isinstance(tier_feature, dict):
                    value = tier_feature.get("value", True)
                    limit = tier_feature.get("limit")
                elif hasattr(tier_feature, "value"):
                    value = getattr(tier_feature, "value", True)
                    limit = getattr(tier_feature, "limit", None)

                # Create a new feature wrapper or dictionary
                if isinstance(feature, dict):
                    # Create a copy of the feature
                    feature_copy = feature.copy()
                    feature_copy["value"] = value

                    if limit is not None:
                        feature_copy["limit"] = limit

                    # Wrap the feature in a FeatureWrapper
                    result.append(FeatureWrapper(feature_copy))
                elif isinstance(feature, FeatureWrapper):
                    # Create a new FeatureWrapper
                    feature_dict = {
                        "id": feature.id,
                        "name": feature.name,
                        "description": feature.description,
                        "type": feature.type,
                        "value_type": feature.value_type,
                        "category": feature.category,
                        "value": value,
                        "created_at": feature.created_at,
                        "updated_at": feature.updated_at,
                    }

                    if limit is not None:
                        feature_dict["limit"] = limit

                    result.append(FeatureWrapper(feature_dict))

        return result

    def compare_tiers(self, tier_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple tiers side by side.

        Args:
            tier_ids: List of tier IDs to compare

        Returns:
            Dictionary with comparison data
        """
        tiers = [
            self.get_tier(tier_id) for tier_id in tier_ids if self.get_tier(tier_id)
        ]

        if not tiers:
            return {"tiers": [], "features": []}

        # Get all features across the tiers
        all_feature_ids = set()
        for tier in tiers:
            for tier_feature in tier["features"]:
                all_feature_ids.add(tier_feature["feature_id"])

        # Get feature details
        features = []
        for feature_id in all_feature_ids:
            feature = self.get_feature(feature_id)
            if feature:
                features.append(feature)

        # Sort features by category
        features.sort(key=lambda f: (f["category"], f["name"]))

        # Create comparison data
        comparison = {
            "tiers": [
                {
                    "id": tier["id"],
                    "name": tier["name"],
                    "price_monthly": tier["price_monthly"],
                    "price_annual": tier["price_annual"],
                }
                for tier in tiers
            ],
            "features": [],
        }

        # Add feature comparison
        for feature in features:
            feature_comparison = {
                "id": feature["id"],
                "name": feature["name"],
                "description": feature["description"],
                "category": feature["category"],
                "type": feature["type"],
                "values": [],
            }

            for tier in tiers:
                # Find feature in tier
                tier_feature = next(
                    (f for f in tier["features"] if f["feature_id"] == feature["id"]),
                    None,
                )

                if tier_feature:
                    value = {"value": tier_feature.get("value", True)}

                    if "limit" in tier_feature:
                        value["limit"] = tier_feature["limit"]

                    feature_comparison["values"].append(value)
                else:
                    feature_comparison["values"].append({"value": False})

            comparison["features"].append(feature_comparison)

        return comparison

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the subscription plan to a dictionary.

        Returns:
            Dictionary representation of the subscription plan
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "billing_cycles": self.billing_cycles,
            "features": self.features,
            "tiers": self.tiers,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the subscription plan to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the subscription plan
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, file_path: str) -> None:
        """
        Save the subscription plan to a JSON file.

        Args:
            file_path: Path to save the file
        """
        with open(file_path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> "SubscriptionPlan":
        """
        Load a subscription plan from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            SubscriptionPlan instance
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        plan = cls(
            name=data["name"],
            description=data["description"],
            billing_cycles=data["billing_cycles"],
            features=data["features"],
            tiers=data["tiers"],
        )

        plan.id = data["id"]
        plan.created_at = data["created_at"]
        plan.updated_at = data["updated_at"]

        return plan

    def __str__(self) -> str:
        """String representation of the subscription plan."""
        return f"{self.name} ({len(self.tiers)} tiers, {len(self.features)} features)"

    def __repr__(self) -> str:
        """Detailed string representation of the subscription plan."""
        return f"SubscriptionPlan(id={self.id}, name={self.name}, tiers={len(self.tiers)}, features={len(self.features)})"


class SubscriptionTier:
    """
    Helper class for working with subscription tiers.

    This class provides a more object-oriented interface for working with tiers
    compared to the dictionary-based approach in SubscriptionPlan.
    """

    def __init__(self, plan: SubscriptionPlan, tier_id: str):
        """
        Initialize a subscription tier.

        Args:
            plan: Subscription plan that contains this tier
            tier_id: ID of the tier
        """
        self.plan = plan
        self.tier_id = tier_id
        self._tier_data = plan.get_tier(tier_id)

        if not self._tier_data:
            raise ValueError(f"Tier with ID {tier_id} not found in plan {plan.name}")

    @property
    def id(self) -> str:
        """Get the tier ID."""
        return self.tier_id

    @property
    def name(self) -> str:
        """Get the tier name."""
        return self._tier_data["name"]

    @name.setter
    def name(self, value: str) -> None:
        """Set the tier name."""
        self.plan.update_tier(self.tier_id, name=value)
        self._refresh()

    @property
    def description(self) -> str:
        """Get the tier description."""
        return self._tier_data["description"]

    @description.setter
    def description(self, value: str) -> None:
        """Set the tier description."""
        self.plan.update_tier(self.tier_id, description=value)
        self._refresh()

    @property
    def price_monthly(self) -> float:
        """Get the monthly price."""
        return self._tier_data["price_monthly"]

    @price_monthly.setter
    def price_monthly(self, value: float) -> None:
        """Set the monthly price."""
        self.plan.update_tier(self.tier_id, price_monthly=value)
        self._refresh()

    @property
    def price_annual(self) -> float:
        """Get the annual price."""
        return self._tier_data["price_annual"]

    @price_annual.setter
    def price_annual(self, value: float) -> None:
        """Set the annual price."""
        self.plan.update_tier(self.tier_id, price_annual=value)
        self._refresh()

    @property
    def is_free(self) -> bool:
        """Check if this is a free tier."""
        return self.price_monthly == 0 and self.price_annual == 0

    @property
    def features(self) -> List[Dict[str, Any]]:
        """Get the tier features with their details."""
        return self.plan.get_tier_features(self.tier_id)

    def add_feature(
        self, feature_id: str, value: Any = True, limit: Optional[int] = None
    ) -> bool:
        """
        Add a feature to this tier.

        Args:
            feature_id: ID of the feature
            value: Value of the feature for this tier
            limit: Limit for quantity-based features

        Returns:
            True if the feature was added, False otherwise
        """
        result = self.plan.add_feature_to_tier(self.tier_id, feature_id, value, limit)
        self._refresh()
        return result is not None

    def remove_feature(self, feature_id: str) -> bool:
        """
        Remove a feature from this tier.

        Args:
            feature_id: ID of the feature

        Returns:
            True if the feature was removed, False otherwise
        """
        result = self.plan.remove_feature_from_tier(self.tier_id, feature_id)
        self._refresh()
        return result

    def has_feature(self, feature_id: str) -> bool:
        """
        Check if this tier has a specific feature.

        Args:
            feature_id: ID of the feature

        Returns:
            True if the tier has the feature, False otherwise
        """
        for feature in self._tier_data["features"]:
            if feature["feature_id"] == feature_id:
                return True

        return False

    def get_feature_value(self, feature_id: str) -> Optional[Any]:
        """
        Get the value of a feature for this tier.

        Args:
            feature_id: ID of the feature

        Returns:
            Value of the feature or None if not found
        """
        for feature in self._tier_data["features"]:
            if feature["feature_id"] == feature_id:
                return feature.get("value", True)

        return None

    def get_feature_limit(self, feature_id: str) -> Optional[int]:
        """
        Get the limit of a feature for this tier.

        Args:
            feature_id: ID of the feature

        Returns:
            Limit of the feature or None if not found or no limit
        """
        for feature in self._tier_data["features"]:
            if feature["feature_id"] == feature_id:
                return feature.get("limit")

        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tier to a dictionary.

        Returns:
            Dictionary representation of the tier
        """
        return self._tier_data

    def _refresh(self) -> None:
        """Refresh the tier data from the plan."""
        self._tier_data = self.plan.get_tier(self.tier_id)

        if not self._tier_data:
            raise ValueError(
                f"Tier with ID {self.tier_id} no longer exists in plan {self.plan.name}"
            )


# Example usage
if __name__ == "__main__":
    # Create a subscription plan
    plan = SubscriptionPlan(
        name="AI Tool Subscription",
        description="Subscription plan for an AI-powered tool",
    )

    # Add features
    feature1 = plan.add_feature(
        name="Content Generation",
        description="Generate content using AI",
        type="quantity",
        category="core",
    )

    feature2 = plan.add_feature(
        name="API Access",
        description="Access to the API",
        type="boolean",
        category="integration",
    )

    feature3 = plan.add_feature(
        name="Team Members",
        description="Number of team members",
        type="quantity",
        category="team",
    )

    # Add tiers
    free_tier = plan.add_tier(
        name="Free",
        description="Basic features for individuals",
        price_monthly=0,
        target_users="Individuals trying out the service",
    )

    basic_tier = plan.add_tier(
        name="Basic",
        description="Essential features for individuals",
        price_monthly=9.99,
        target_users="Individual creators and small businesses",
    )

    pro_tier = plan.add_tier(
        name="Pro",
        description="Advanced features for professionals",
        price_monthly=19.99,
        is_popular=True,
        target_users="Professional content creators and marketing teams",
    )

    # Add features to tiers
    plan.add_feature_to_tier(free_tier["id"], feature1["id"], value=True, limit=10)
    plan.add_feature_to_tier(basic_tier["id"], feature1["id"], value=True, limit=100)
    plan.add_feature_to_tier(pro_tier["id"], feature1["id"], value=True, limit=1000)

    plan.add_feature_to_tier(basic_tier["id"], feature2["id"], value=True)
    plan.add_feature_to_tier(pro_tier["id"], feature2["id"], value=True)

    plan.add_feature_to_tier(basic_tier["id"], feature3["id"], value=True, limit=3)
    plan.add_feature_to_tier(pro_tier["id"], feature3["id"], value=True, limit=10)

    # Use the SubscriptionTier helper class
    pro_tier_obj = SubscriptionTier(plan, pro_tier["id"])
    print(f"Tier: {pro_tier_obj.name}")
    print(f"Monthly price: ${pro_tier_obj.price_monthly:.2f}")
    print(f"Annual price: ${pro_tier_obj.price_annual:.2f}")

    print("\nFeatures:")
    for feature in pro_tier_obj.features:
        limit_str = f" (Limit: {feature.get('limit')})" if "limit" in feature else ""
        print(f"- {feature['name']}: {feature['value']}{limit_str}")

    # Compare tiers
    comparison = plan.compare_tiers([free_tier["id"], basic_tier["id"], pro_tier["id"]])

    print("\nTier Comparison:")
    for i, tier in enumerate(comparison["tiers"]):
        print(f"{tier['name']}: ${tier['price_monthly']:.2f}/month")

    print("\nFeature Comparison:")
    for feature in comparison["features"]:
        print(f"{feature['name']}:")
        for i, value in enumerate(feature["values"]):
            tier_name = comparison["tiers"][i]["name"]
            limit_str = f" (Limit: {value.get('limit')})" if "limit" in value else ""
            print(f"  - {tier_name}: {value['value']}{limit_str}")