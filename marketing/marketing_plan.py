"""Marketing plan module."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MarketingPlan:
    """Class for creating and managing marketing plans."""

    def __init__(
        self,
        name: str,
        description: str,
        target_audience: Dict[str, Any],
        channels: List[Dict[str, Any]],
        budget: Dict[str, Any],
        timeline: Dict[str, Any],
    ) -> None:
        """
        Initialize a marketing plan.

        Args:
            name: Name of the plan
            description: Description of the plan
            target_audience: Target audience details
            channels: List of marketing channels
            budget: Budget details
            timeline: Timeline details
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.target_audience = target_audience
        self.channels = channels
        self.budget = budget
        self.timeline = timeline
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.campaigns = []
        self.metrics = []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the marketing plan to a dictionary.

        Returns:
            Dictionary representation of the marketing plan
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_audience": self.target_audience,
            "channels": self.channels,
            "budget": self.budget,
            "timeline": self.timeline,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "campaigns": self.campaigns,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketingPlan":
        """
        Create a marketing plan from a dictionary.

        Args:
            data: Dictionary representation of the marketing plan

        Returns:
            MarketingPlan instance
        """
        plan = cls(
            name=data["name"],
            description=data["description"],
            target_audience=data["target_audience"],
            channels=data["channels"],
            budget=data["budget"],
            timeline=data["timeline"],
        )
        plan.id = data.get("id", plan.id)
        plan.created_at = data.get("created_at", plan.created_at)
        plan.updated_at = data.get("updated_at", plan.updated_at)
        plan.campaigns = data.get("campaigns", [])
        plan.metrics = data.get("metrics", [])
        return plan

    def add_campaign(self, campaign: Dict[str, Any]) -> None:
        """
        Add a campaign to the marketing plan.

        Args:
            campaign: Campaign details
        """
        self.campaigns.append(campaign)
        self.updated_at = datetime.now().isoformat()

    def add_metric(self, metric: Dict[str, Any]) -> None:
        """
        Add a metric to the marketing plan.

        Args:
            metric: Metric details
        """
        self.metrics.append(metric)
        self.updated_at = datetime.now().isoformat()

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update the marketing plan.

        Args:
            updates: Fields to update
        """
        for key, value in updates.items():
            if hasattr(self, key) and key not in ["id", "created_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
