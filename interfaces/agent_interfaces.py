"""Agent interfaces for the pAIssive Income system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol


class IAgentProfile(Protocol):
    """Interface for agent profiles."""

    def is_configured(self) -> bool:
        """Check if the agent is properly configured."""
        ...

    def configure(self, **kwargs: Any) -> None:
        """Configure the agent."""
        ...


class IResearchAgent(IAgentProfile):
    """Interface for the research agent."""

    @abstractmethod
    def analyze_market_segments(self, segments: List[str]) -> List[Dict[str, Any]]:
        """Analyze market segments and identify niche opportunities."""
        ...

    @abstractmethod
    def validate_niche(self, niche: Dict[str, Any]) -> bool:
        """Validate a niche opportunity."""
        ...

    @abstractmethod
    def get_market_data(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed market data for a niche."""
        ...


class IDeveloperAgent(IAgentProfile):
    """Interface for the developer agent."""

    @abstractmethod
    def design_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """Design an AI solution for a niche."""
        ...

    @abstractmethod
    def validate_design(self, design: Dict[str, Any]) -> bool:
        """Validate a solution design."""
        ...

    @abstractmethod
    def estimate_development_effort(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate development effort for a solution."""
        ...


class IMonetizationAgent(IAgentProfile):
    """Interface for the monetization agent."""

    @abstractmethod
    def create_strategy(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Create a monetization strategy."""
        ...

    @abstractmethod
    def validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate a monetization strategy."""
        ...

    @abstractmethod
    def project_revenue(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Project revenue for a monetization strategy."""
        ...


class IMarketingAgent(IAgentProfile):
    """Interface for the marketing agent."""

    @abstractmethod
    def create_plan(
        self,
        niche: Dict[str, Any],
        solution: Dict[str, Any],
        monetization: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a marketing plan."""
        ...

    @abstractmethod
    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate a marketing plan."""
        ...

    @abstractmethod
    def estimate_roi(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate ROI for a marketing plan."""
        ...


class IFeedbackAgent(IAgentProfile):
    """Interface for the feedback agent."""

    @abstractmethod
    def analyze_feedback(self, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user feedback."""
        ...

    @abstractmethod
    def validate_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Validate user feedback."""
        ...

    @abstractmethod
    def generate_recommendations(
        self, feedback_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate improvement recommendations."""
        ...


class IAgentTeam(Protocol):
    """Interface for the agent team."""

    @property
    def researcher(self) -> IResearchAgent:
        """Get the research agent."""
        ...

    @property
    def developer(self) -> IDeveloperAgent:
        """Get the developer agent."""
        ...

    @property
    def monetization(self) -> IMonetizationAgent:
        """Get the monetization agent."""
        ...

    @property
    def marketing(self) -> IMarketingAgent:
        """Get the marketing agent."""
        ...

    @property
    def feedback(self) -> IFeedbackAgent:
        """Get the feedback agent."""
        ...

    def run_niche_analysis(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """Run niche analysis workflow."""
        ...

    def develop_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """Develop solution workflow."""
        ...

    def create_monetization_strategy(
        self, solution: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create monetization strategy workflow."""
        ...

    def create_marketing_plan(
        self,
        niche: Optional[Dict[str, Any]] = None,
        solution: Optional[Dict[str, Any]] = None,
        monetization: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create marketing plan workflow."""
        ...

    def process_feedback(self, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process feedback workflow."""
        ...
