"""Team configuration and management module."""

import logging
from typing import Dict, List, Optional

from interfaces.agent_interfaces import (
    IAgentTeam,
    IDeveloperAgent,
    IFeedbackAgent,
    IMarketingAgent,
    IMonetizationAgent,
    IResearchAgent,
)
from interfaces.model_interfaces import IModelManager

from .agent_profiles import (
    DeveloperAgent,
    FeedbackAgent,
    MarketingAgent,
    MonetizationAgent,
    ResearchAgent,
)

logger = logging.getLogger(__name__)


class TeamConfig:
    """Configuration for an agent team."""

    def __init__(self, model_settings: Dict = None, workflow: Dict = None):
        """Initialize team configuration.

        Args:
            model_settings: Model settings for each agent
            workflow: Workflow settings
        """
        self.model_settings = model_settings or {
            "researcher": {"model": "gpt-4", "temperature": 0.7},
            "developer": {"model": "gpt-4", "temperature": 0.2},
            "monetization": {"model": "gpt-4", "temperature": 0.5},
            "marketing": {"model": "gpt-4", "temperature": 0.8},
            "feedback": {"model": "gpt-4", "temperature": 0.3},
        }
        self.workflow = workflow or {"auto_progression": False, "review_required": True}

    def __getitem__(self, key):
        """Make TeamConfig subscriptable.

        Args:
            key: The key to access

        Returns:
            The value for the key

        Raises:
            KeyError: If the key is not found
        """
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(f"Invalid key: {key}")


class AgentTeam(IAgentTeam):
    """Manages a team of AI agents working on niche analysis and solution development."""

    def __init__(self, model_manager: IModelManager, team_config: Optional[TeamConfig] = None):
        """Initialize agent team."""
        self.model_manager = model_manager
        self.project_state: Dict = {}

        # Load or create configuration
        self.config = team_config or TeamConfig()

        # Initialize agents
        self._researcher = ResearchAgent(self)
        self._developer = DeveloperAgent(self)
        self._monetization = MonetizationAgent(self)
        self._marketing = MarketingAgent(self)
        self._feedback = FeedbackAgent(self)

    @property
    def researcher(self) -> IResearchAgent:
        """Get the research agent."""
        return self._researcher

    @property
    def developer(self) -> IDeveloperAgent:
        """Get the developer agent."""
        return self._developer

    @property
    def monetization(self) -> IMonetizationAgent:
        """Get the monetization agent."""
        return self._monetization

    @property
    def marketing(self) -> IMarketingAgent:
        """Get the marketing agent."""
        return self._marketing

    @property
    def feedback(self) -> IFeedbackAgent:
        """Get the feedback agent."""
        return self._feedback

    def run_niche_analysis(self, market_segments: List[str]) -> List[Dict]:
        """Run niche analysis workflow."""
        try:
            # Analyze market segments using researcher agent
            niches = self.researcher.analyze_market_segments(market_segments)

            # Store results in project state
            self.project_state["identified_niches"] = niches

            return niches
        except Exception as e:
            logger.error(f"Niche analysis failed: {str(e)}")
            raise

    def develop_solution(self, niche: Dict) -> Dict:
        """Develop solution workflow."""
        try:
            # Store the selected niche
            self.project_state["selected_niche"] = niche

            # Design solution using developer agent
            solution = self.developer.design_solution(niche)

            # Store solution in project state
            self.project_state["solution"] = solution

            return solution
        except Exception as e:
            logger.error(f"Solution development failed: {str(e)}")
            raise

    def create_monetization_strategy(self, solution: Optional[Dict] = None) -> Dict:
        """Create monetization strategy workflow."""
        try:
            # Use stored solution if none provided
            if solution is None:
                solution = self.project_state.get("solution")
                if solution is None:
                    raise ValueError("No solution available for monetization")

            # Create strategy using monetization agent
            strategy = self.monetization.create_strategy(solution)

            # Store strategy in project state
            self.project_state["monetization_strategy"] = strategy

            return strategy
        except Exception as e:
            logger.error(f"Monetization strategy creation failed: {str(e)}")
            raise

    def create_marketing_plan(
        self,
        niche: Optional[Dict] = None,
        solution: Optional[Dict] = None,
        monetization: Optional[Dict] = None,
    ) -> Dict:
        """Create marketing plan workflow."""
        try:
            # Use stored data if not provided
            if niche is None:
                niche = self.project_state.get("selected_niche")
            if solution is None:
                solution = self.project_state.get("solution")
            if monetization is None:
                monetization = self.project_state.get("monetization_strategy")

            if not all([niche, solution, monetization]):
                raise ValueError("Missing required data for marketing plan")

            # Create plan using marketing agent
            plan = self.marketing.create_plan(niche, solution, monetization)

            # Store plan in project state
            self.project_state["marketing_plan"] = plan

            return plan
        except Exception as e:
            logger.error(f"Marketing plan creation failed: {str(e)}")
            raise

    def process_feedback(self, feedback: List[Dict]) -> Dict:
        """Process feedback workflow."""
        try:
            # Analyze feedback using feedback agent
            analysis = self.feedback.analyze_feedback(feedback)

            # Store feedback analysis in project state
            self.project_state["feedback_analysis"] = analysis

            return analysis
        except Exception as e:
            logger.error(f"Feedback processing failed: {str(e)}")
            raise
