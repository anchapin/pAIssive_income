"""
Team configuration for the pAIssive Income AI agent team.
Defines the overall structure and collaboration patterns for the agent team.
"""

from typing import Dict, List, Optional, Any
import json
import os

from .agent_profiles.researcher import ResearchAgent
from .agent_profiles.developer import DeveloperAgent
from .agent_profiles.monetization import MonetizationAgent
from .agent_profiles.marketing import MarketingAgent
from .agent_profiles.feedback import FeedbackAgent


class AgentTeam:
    """
    A team of specialized AI agents that collaborate on developing and
    monetizing niche AI tools for passive income generation.
    """

    def __init__(self, project_name: str, config_path: Optional[str] = None):
        """
        Initialize the agent team with a project name and optional configuration.

        Args:
            project_name: Name of the niche AI tool project
            config_path: Optional path to a JSON configuration file
        """
        self.project_name = project_name
        self.config = self._load_config(config_path)

        # Initialize the specialized agents
        self.researcher = ResearchAgent(self)
        self.developer = DeveloperAgent(self)
        self.monetization = MonetizationAgent(self)
        self.marketing = MarketingAgent(self)
        self.feedback = FeedbackAgent(self)

        # Project state storage
        self.project_state = {
            "identified_niches": [],
            "selected_niche": None,
            "user_problems": [],
            "solution_design": None,
            "monetization_strategy": None,
            "marketing_plan": None,
            "feedback_data": [],
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a JSON file or use default configuration.

        Args:
            config_path: Path to a JSON configuration file

        Returns:
            Configuration dictionary
        """
        default_config = {
            "model_settings": {
                "researcher": {"model": "gpt-4", "temperature": 0.7},
                "developer": {"model": "gpt-4", "temperature": 0.2},
                "monetization": {"model": "gpt-4", "temperature": 0.5},
                "marketing": {"model": "gpt-4", "temperature": 0.8},
                "feedback": {"model": "gpt-4", "temperature": 0.3},
            },
            "workflow": {
                "auto_progression": False,
                "review_required": True,
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge user config with default config
                for key, value in user_config.items():
                    if key in default_config and isinstance(value, dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value

        return default_config

    def run_niche_analysis(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Run a complete niche analysis workflow using the researcher agent.

        Args:
            market_segments: List of market segments to analyze

        Returns:
            List of identified niche opportunities with scores
        """
        return self.researcher.analyze_market_segments(market_segments)

    def develop_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """
        Develop an AI solution for a selected niche using the developer agent.

        Args:
            niche: The selected niche object from the niche analysis

        Returns:
            Solution design specification
        """
        # Store the selected niche in the project state
        self.project_state["selected_niche"] = niche

        # For backward compatibility, also add to identified_niches if not already there
        if niche not in self.project_state["identified_niches"]:
            self.project_state["identified_niches"].append(niche)

        # Develop the solution
        solution = self.developer.design_solution(niche)

        # Store the solution in the project state
        self.project_state["solution_design"] = solution

        return solution

    def create_monetization_strategy(self, solution: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a monetization strategy for the developed solution.

        Args:
            solution: Optional solution object. If not provided, uses the solution from project state.

        Returns:
            Monetization strategy specification
        """
        # If solution is provided, use it; otherwise use the one from project state
        if solution:
            # Store the solution in the project state if it's not already there
            if not self.project_state["solution_design"]:
                self.project_state["solution_design"] = solution
        elif not self.project_state["solution_design"]:
            raise ValueError("Solution must be designed before creating monetization strategy")

        # Use the solution from the project state or the provided solution
        solution_to_use = solution if solution else self.project_state["solution_design"]

        # Create the monetization strategy
        strategy = self.monetization.create_strategy(solution_to_use)

        # Store the strategy in the project state
        self.project_state["monetization_strategy"] = strategy

        return strategy

    def create_marketing_plan(self, niche: Optional[Dict[str, Any]] = None,
                          solution: Optional[Dict[str, Any]] = None,
                          monetization: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a marketing plan for the developed solution.

        Args:
            niche: Optional niche object. If not provided, uses the niche from project state.
            solution: Optional solution object. If not provided, uses the solution from project state.
            monetization: Optional monetization strategy object. If not provided, uses the strategy from project state.

        Returns:
            Marketing plan specification
        """
        # Use provided objects or fall back to project state
        niche_to_use = niche if niche else self.project_state["selected_niche"]
        solution_to_use = solution if solution else self.project_state["solution_design"]
        monetization_to_use = monetization if monetization else self.project_state["monetization_strategy"]

        # Validate that we have all required objects
        if not niche_to_use:
            raise ValueError("Niche must be selected before creating marketing plan")
        if not solution_to_use:
            raise ValueError("Solution must be designed before creating marketing plan")
        if not monetization_to_use:
            raise ValueError("Monetization strategy must be created before marketing plan")

        # Create the marketing plan
        plan = self.marketing.create_plan(niche_to_use, solution_to_use, monetization_to_use)

        # Store the plan in the project state
        self.project_state["marketing_plan"] = plan

        return plan

    def process_feedback(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process user feedback and generate improvement recommendations.

        Args:
            feedback_data: List of user feedback items

        Returns:
            Analysis and recommendations based on feedback
        """
        self.project_state["feedback_data"].extend(feedback_data)
        return self.feedback.analyze_feedback(feedback_data)

    def export_project_plan(self, output_path: str) -> None:
        """
        Export the complete project plan to a JSON file.

        Args:
            output_path: Path to save the project plan
        """
        with open(output_path, 'w') as f:
            json.dump(self.project_state, f, indent=2)

    def __str__(self) -> str:
        """String representation of the agent team."""
        return f"AgentTeam(project_name={self.project_name}, agents=5)"
