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
    
    def develop_solution(self, niche_id: str) -> Dict[str, Any]:
        """
        Develop an AI solution for a selected niche using the developer agent.

        Args:
            niche_id: ID of the selected niche from the niche analysis

        Returns:
            Solution design specification
        """
        # Set the selected niche
        selected_niche = next((n for n in self.project_state["identified_niches"] 
                              if n.get("id") == niche_id), None)
        if not selected_niche:
            raise ValueError(f"Niche with ID {niche_id} not found in identified niches")
        
        self.project_state["selected_niche"] = selected_niche
        
        # Develop the solution
        return self.developer.design_solution(selected_niche)
    
    def create_monetization_strategy(self) -> Dict[str, Any]:
        """
        Create a monetization strategy for the developed solution.

        Returns:
            Monetization strategy specification
        """
        if not self.project_state["solution_design"]:
            raise ValueError("Solution must be designed before creating monetization strategy")
        
        return self.monetization.create_strategy(
            self.project_state["selected_niche"],
            self.project_state["solution_design"]
        )
    
    def create_marketing_plan(self) -> Dict[str, Any]:
        """
        Create a marketing plan for the developed solution.

        Returns:
            Marketing plan specification
        """
        if not self.project_state["monetization_strategy"]:
            raise ValueError("Monetization strategy must be created before marketing plan")
        
        return self.marketing.create_plan(
            self.project_state["selected_niche"],
            self.project_state["solution_design"],
            self.project_state["monetization_strategy"]
        )
    
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
