"""Marketing service for UI interactions."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from interfaces.agent_interfaces import IAgentTeam
from interfaces.marketing_interfaces import IMarketingService

from ..utils import format_datetime
from .base_service import BaseService

logger = logging.getLogger(__name__)


class MarketingService(BaseService, IMarketingService):
    """Service for managing marketing plans."""

    def __init__(self, agent_team: IAgentTeam, data_dir: str) -> None:
        """Initialize the service."""
        super().__init__(data_dir, "marketing")
        self.agent_team = agent_team
        self.plans_dir = "plans"

    def get_plans(self) -> List[Dict[str, Any]]:
        """Get all marketing plans."""
        stored_data = self.load_data()
        if stored_data is None:
            return []
        return self._ensure_list(stored_data)

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific marketing plan.

        Args:
            plan_id: ID of the plan to get

        Returns:
            Plan data if found, None otherwise
        """
        plans = self.load_data()
        if plans is None:
            return None

        for plan in self._ensure_list(plans):
            if plan.get("id") == plan_id:
                return plan
        return None

    def create_plan(
        self,
        niche: Dict[str, Any],
        solution: Dict[str, Any],
        monetization: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a new marketing plan.

        Args:
            niche: Niche details
            solution: Solution details
            monetization: Monetization strategy

        Returns:
            Created plan data

        Raises:
            ValueError: If inputs are invalid
        """
        plan = self.agent_team.create_marketing_plan(niche, solution, monetization)

        # Add metadata
        plan["id"] = self._generate_id()
        plan["created_at"] = datetime.now().isoformat()
        plan["updated_at"] = plan["created_at"]

        # Save to storage
        plans = self.load_data() or []
        plans = self._ensure_list(plans)
        plans.append(plan)
        self.save_data("plans", plans)

        return plan

    def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a marketing plan.

        Args:
            plan_id: ID of plan to update
            updates: Fields to update

        Returns:
            Updated plan data

        Raises:
            ValueError: If plan not found
        """
        plans = self.load_data()
        if plans is None:
            raise ValueError(f"Plan not found: {plan_id}")

        plans = self._ensure_list(plans)
        for i, plan in enumerate(plans):
            if plan.get("id") == plan_id:
                plan.update(updates)
                plan["updated_at"] = datetime.now().isoformat()
                plans[i] = plan
                self.save_data("plans", plans)
                return plan

        raise ValueError(f"Plan not found: {plan_id}")

    def delete_plan(self, plan_id: str) -> None:
        """
        Delete a marketing plan.

        Args:
            plan_id: ID of plan to delete

        Raises:
            ValueError: If plan not found
        """
        plans = self.load_data()
        if plans is None:
            raise ValueError(f"Plan not found: {plan_id}")

        plans = self._ensure_list(plans)
        for i, plan in enumerate(plans):
            if plan.get("id") == plan_id:
                plans.pop(i)
                self.save_data("plans", plans)
                return

        raise ValueError(f"Plan not found: {plan_id}")

    def get_social_media_calendar(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get social media calendar for a plan."""
        plan = self.get_plan(plan_id)
        if not plan:
            return []

        calendar = plan.get("social_media_calendar", [])
        for event in calendar:
            if "date" in event:
                event["formatted_date"] = format_datetime(event["date"])
        return calendar

    def get_content_calendar(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get content calendar for a plan."""
        plan = self.get_plan(plan_id)
        if not plan:
            return []

        calendar = plan.get("content_calendar", [])
        for event in calendar:
            if "date" in event:
                event["formatted_date"] = format_datetime(event["date"])
        return calendar

    def get_email_calendar(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get email campaign calendar for a plan."""
        plan = self.get_plan(plan_id)
        if not plan:
            return []

        calendar = plan.get("email_calendar", [])
        for event in calendar:
            if "date" in event:
                event["formatted_date"] = format_datetime(event["date"])
        return calendar

    @staticmethod
    def _ensure_list(data: Any) -> List[Dict[str, Any]]:
        """Ensure data is a list of dictionaries."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
