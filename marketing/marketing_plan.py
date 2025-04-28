"""
Marketing Plan module for the pAIssive Income project.

This module provides functionality for creating and managing marketing plans.
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class MarketingPlan:
    """Class for creating and managing marketing plans."""

    def __init__(self, name: str, description: str = ""):
        """Initialize a marketing plan.

        Args:
            name: The name of the marketing plan.
            description: A description of the marketing plan.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.channels = []
        self.budget = None
        self.tier_budget_allocations = {}
        self.content_calendar = {
            "content_types": [],
            "frequency": "weekly"
        }
        self.target_audience = ""
        self.metrics = []
        self.tactics = []

    def set_budget(self, total_amount: float, period: str = "monthly", allocation_strategy: str = "equal"):
        """Set the budget for the marketing plan.

        Args:
            total_amount: The total budget amount.
            period: The budget period (e.g., "monthly", "quarterly", "annual").
            allocation_strategy: The strategy for allocating the budget.
        """
        self.budget = {
            "amount": total_amount,
            "period": period,
            "allocation_strategy": allocation_strategy,
            "allocation": {}
        }
        self.updated_at = datetime.now().isoformat()

    def add_channel(self, name: str, description: str, budget_percentage: float = 0.0):
        """Add a marketing channel to the plan.

        Args:
            name: The name of the channel.
            description: A description of the channel.
            budget_percentage: The percentage of the budget allocated to this channel.
        """
        channel = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "budget_percentage": budget_percentage
        }
        self.channels.append(channel)
        
        # Update budget allocation if budget exists
        if self.budget:
            self.budget["allocation"][name] = budget_percentage
        
        self.updated_at = datetime.now().isoformat()
        return channel

    def add_tier_budget_allocation(self, tier_name: str, amount: float, percentage: Optional[float] = None):
        """Add a budget allocation for a specific tier.

        Args:
            tier_name: The name of the tier.
            amount: The budget amount allocated to this tier.
            percentage: The percentage of the total budget allocated to this tier.
        """
        self.tier_budget_allocations[tier_name] = {
            "amount": amount,
            "percentage": percentage if percentage is not None else (
                amount / self.budget["amount"] if self.budget else 0.0
            )
        }
        self.updated_at = datetime.now().isoformat()

    def add_content_type(self, content_type: str):
        """Add a content type to the content calendar.

        Args:
            content_type: The type of content to add.
        """
        if content_type not in self.content_calendar["content_types"]:
            self.content_calendar["content_types"].append(content_type)
        self.updated_at = datetime.now().isoformat()

    def set_content_frequency(self, frequency: str):
        """Set the frequency for the content calendar.

        Args:
            frequency: The frequency for content creation (e.g., "daily", "weekly", "monthly").
        """
        self.content_calendar["frequency"] = frequency
        self.updated_at = datetime.now().isoformat()

    def set_target_audience(self, target_audience: str):
        """Set the target audience for the marketing plan.

        Args:
            target_audience: A description of the target audience.
        """
        self.target_audience = target_audience
        self.updated_at = datetime.now().isoformat()

    def add_metric(self, name: str, description: str, target_value: float, unit: str):
        """Add a metric to track for the marketing plan.

        Args:
            name: The name of the metric.
            description: A description of the metric.
            target_value: The target value for the metric.
            unit: The unit of measurement for the metric.
        """
        metric = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "target_value": target_value,
            "current_value": 0.0,
            "unit": unit
        }
        self.metrics.append(metric)
        self.updated_at = datetime.now().isoformat()
        return metric

    def add_tactic(self, name: str, channel_name: str, description: str, expected_impact: float = 0.5):
        """Add a marketing tactic to the plan.

        Args:
            name: The name of the tactic.
            channel_name: The name of the channel this tactic belongs to.
            description: A description of the tactic.
            expected_impact: The expected impact of the tactic (0.0 to 1.0).
        """
        tactic = {
            "id": str(uuid.uuid4()),
            "name": name,
            "channel_name": channel_name,
            "description": description,
            "expected_impact": expected_impact
        }
        self.tactics.append(tactic)
        self.updated_at = datetime.now().isoformat()
        return tactic

    def to_dict(self) -> Dict[str, Any]:
        """Convert the marketing plan to a dictionary.

        Returns:
            A dictionary representation of the marketing plan.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "channels": self.channels,
            "budget": self.budget,
            "tier_budget_allocations": self.tier_budget_allocations,
            "content_calendar": self.content_calendar,
            "target_audience": self.target_audience,
            "metrics": self.metrics,
            "tactics": self.tactics
        }

    def calculate_channel_budget(self, channel_name: str) -> float:
        """Calculate the budget for a specific channel.

        Args:
            channel_name: The name of the channel.

        Returns:
            The budget amount for the channel.
        """
        if not self.budget:
            return 0.0
        
        for channel in self.channels:
            if channel["name"] == channel_name:
                return self.budget["amount"] * channel["budget_percentage"]
        
        return 0.0

    def calculate_total_expected_impact(self) -> float:
        """Calculate the total expected impact of all tactics.

        Returns:
            The total expected impact.
        """
        return sum(tactic["expected_impact"] for tactic in self.tactics)
