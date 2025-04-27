"""
Team configuration for the pAIssive Income AI agent team.
Defines the overall structure and collaboration patterns for the agent team.
"""

from typing import Dict, List, Optional, Any, Type, TypeVar, cast
import json
import os
import logging
import uuid
from datetime import datetime

from interfaces.agent_interfaces import (
    IAgentTeam, IResearchAgent, IDeveloperAgent,
    IMonetizationAgent, IMarketingAgent, IFeedbackAgent
)
from .agent_profiles.researcher import ResearchAgent
from .agent_profiles.developer import DeveloperAgent
from .agent_profiles.monetization import MonetizationAgent
from .agent_profiles.marketing import MarketingAgent
from .agent_profiles.feedback import FeedbackAgent
from .errors import (
    AgentTeamError, AgentInitializationError, WorkflowError,
    ValidationError, handle_exception
)

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for agent interfaces
T = TypeVar('T')


class AgentTeam(IAgentTeam):
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

        Raises:
            ValidationError: If the project name is invalid
            AgentInitializationError: If an agent fails to initialize
        """
        try:
            # Validate project name
            if not project_name or not isinstance(project_name, str):
                raise ValidationError(
                    message="Project name must be a non-empty string",
                    field="project_name",
                    validation_errors=[{
                        "field": "project_name",
                        "value": project_name,
                        "error": "Must be a non-empty string"
                    }]
                )

            self._project_name = project_name
            self._id = str(uuid.uuid4())
            logger.info(f"Initializing agent team for project: {project_name}")

            # Load configuration
            try:
                self._config = self._load_config(config_path)
            except Exception as e:
                raise AgentTeamError(
                    message=f"Failed to load configuration: {e}",
                    code="config_load_error",
                    original_exception=e
                )

            # Initialize the specialized agents
            try:
                self.researcher = ResearchAgent(self)
                logger.debug(f"Initialized Research Agent for project: {project_name}")
            except Exception as e:
                raise AgentInitializationError(
                    message=f"Failed to initialize Research Agent: {e}",
                    agent_name="Research Agent",
                    original_exception=e
                )

            try:
                self.developer = DeveloperAgent(self)
                logger.debug(f"Initialized Developer Agent for project: {project_name}")
            except Exception as e:
                raise AgentInitializationError(
                    message=f"Failed to initialize Developer Agent: {e}",
                    agent_name="Developer Agent",
                    original_exception=e
                )

            try:
                self.monetization = MonetizationAgent(self)
                logger.debug(f"Initialized Monetization Agent for project: {project_name}")
            except Exception as e:
                raise AgentInitializationError(
                    message=f"Failed to initialize Monetization Agent: {e}",
                    agent_name="Monetization Agent",
                    original_exception=e
                )

            try:
                self.marketing = MarketingAgent(self)
                logger.debug(f"Initialized Marketing Agent for project: {project_name}")
            except Exception as e:
                raise AgentInitializationError(
                    message=f"Failed to initialize Marketing Agent: {e}",
                    agent_name="Marketing Agent",
                    original_exception=e
                )

            try:
                self.feedback = FeedbackAgent(self)
                logger.debug(f"Initialized Feedback Agent for project: {project_name}")
            except Exception as e:
                raise AgentInitializationError(
                    message=f"Failed to initialize Feedback Agent: {e}",
                    agent_name="Feedback Agent",
                    original_exception=e
                )

            # Project state storage
            self.project_state = {
                "id": self.id,
                "name": self.project_name,
                "identified_niches": [],
                "selected_niche": None,
                "user_problems": [],
                "solution_design": None,
                "monetization_strategy": None,
                "marketing_plan": None,
                "feedback_data": [],
                "created_at": str(datetime.now().isoformat()),
                "updated_at": str(datetime.now().isoformat())
            }

            # Agent registry for dependency injection
            self._agent_registry = {
                "researcher": self.researcher,
                "developer": self.developer,
                "monetization": self.monetization,
                "marketing": self.marketing,
                "feedback": self.feedback
            }

            logger.info(f"Successfully initialized agent team for project: {project_name}")

        except ValidationError:
            # Re-raise validation errors
            raise
        except AgentTeamError:
            # Re-raise agent team errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error = handle_exception(
                e,
                error_class=AgentTeamError,
                message=f"Failed to initialize agent team for project {project_name}",
                reraise=True,
                log_level=logging.ERROR
            )
            # This line won't be reached due to reraise=True

    @property
    def project_name(self) -> str:
        """Get the project name."""
        return self._project_name

    @property
    def id(self) -> str:
        """Get the team ID."""
        return self._id

    @property
    def config(self) -> Dict[str, Any]:
        """Get the team configuration."""
        return self._config

    def get_agent(self, agent_type: str) -> Any:
        """
        Get an agent by type.

        Args:
            agent_type: Type of agent to get

        Returns:
            Agent instance

        Raises:
            ValueError: If the agent type is invalid
        """
        if agent_type not in self._agent_registry:
            raise ValueError(f"Invalid agent type: {agent_type}. Valid types are: {', '.join(self._agent_registry.keys())}")

        return self._agent_registry[agent_type]

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a JSON file or use default configuration.

        Args:
            config_path: Path to a JSON configuration file

        Returns:
            Configuration dictionary

        Raises:
            ValidationError: If the configuration is invalid
            AgentTeamError: If there's an issue loading the configuration
        """
        try:
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

            if config_path:
                if not os.path.exists(config_path):
                    raise ValidationError(
                        message=f"Configuration file not found: {config_path}",
                        field="config_path",
                        validation_errors=[{
                            "field": "config_path",
                            "value": config_path,
                            "error": "File not found"
                        }]
                    )

                try:
                    with open(config_path, 'r') as f:
                        try:
                            user_config = json.load(f)
                        except json.JSONDecodeError as e:
                            raise ValidationError(
                                message=f"Invalid JSON in configuration file: {e}",
                                field="config_file_content",
                                original_exception=e
                            )

                        # Validate user config
                        if not isinstance(user_config, dict):
                            raise ValidationError(
                                message="Configuration must be a dictionary",
                                field="config_file_content",
                                validation_errors=[{
                                    "field": "config_file_content",
                                    "value": str(type(user_config)),
                                    "error": "Must be a dictionary"
                                }]
                            )

                        # Merge user config with default config
                        for key, value in user_config.items():
                            if key in default_config and isinstance(value, dict) and isinstance(default_config[key], dict):
                                default_config[key].update(value)
                            else:
                                default_config[key] = value

                except (IOError, OSError) as e:
                    raise AgentTeamError(
                        message=f"Failed to read configuration file: {e}",
                        code="config_file_error",
                        original_exception=e
                    )

            # Validate the final config
            required_sections = ["model_settings", "workflow"]
            missing_sections = [section for section in required_sections if section not in default_config]

            if missing_sections:
                raise ValidationError(
                    message=f"Configuration is missing required sections: {', '.join(missing_sections)}",
                    field="config",
                    validation_errors=[{
                        "field": section,
                        "error": "Required section is missing"
                    } for section in missing_sections]
                )

            # Validate model settings
            if "model_settings" in default_config:
                required_agents = ["researcher", "developer", "monetization", "marketing", "feedback"]
                missing_agents = [agent for agent in required_agents if agent not in default_config["model_settings"]]

                if missing_agents:
                    raise ValidationError(
                        message=f"Model settings are missing for agents: {', '.join(missing_agents)}",
                        field="model_settings",
                        validation_errors=[{
                            "field": f"model_settings.{agent}",
                            "error": "Required agent settings are missing"
                        } for agent in missing_agents]
                    )

            logger.info(f"Successfully loaded configuration{' from file: ' + config_path if config_path else ''}")
            return default_config

        except ValidationError:
            # Re-raise validation errors
            raise
        except AgentTeamError:
            # Re-raise agent team errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error = handle_exception(
                e,
                error_class=AgentTeamError,
                message=f"Failed to load configuration: {e}",
                reraise=True,
                log_level=logging.ERROR
            )
            return {}  # This line won't be reached due to reraise=True

    def run_niche_analysis(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Run a complete niche analysis workflow using the researcher agent.

        Args:
            market_segments: List of market segments to analyze

        Returns:
            List of identified niche opportunities with scores

        Raises:
            ValidationError: If the market segments are invalid
            ResearchAgentError: If there's an issue with the research agent
            WorkflowError: If there's an issue with the workflow
        """
        try:
            # Validate input
            if not market_segments:
                raise ValidationError(
                    message="Market segments list cannot be empty",
                    field="market_segments",
                    validation_errors=[{
                        "field": "market_segments",
                        "value": str(market_segments),
                        "error": "Cannot be empty"
                    }]
                )

            if not isinstance(market_segments, list):
                raise ValidationError(
                    message="Market segments must be a list",
                    field="market_segments",
                    validation_errors=[{
                        "field": "market_segments",
                        "value": str(type(market_segments)),
                        "error": "Must be a list"
                    }]
                )

            for i, segment in enumerate(market_segments):
                if not segment or not isinstance(segment, str):
                    raise ValidationError(
                        message=f"Market segment at index {i} must be a non-empty string",
                        field=f"market_segments[{i}]",
                        validation_errors=[{
                            "field": f"market_segments[{i}]",
                            "value": str(segment),
                            "error": "Must be a non-empty string"
                        }]
                    )

            logger.info(f"Running niche analysis for market segments: {', '.join(market_segments)}")

            try:
                # Run the analysis
                niches = self.researcher.analyze_market_segments(market_segments)

                # Store the results in the project state
                self.project_state["identified_niches"] = niches
                self.project_state["updated_at"] = str(datetime.now().isoformat())

                logger.info(f"Identified {len(niches)} niches across {len(market_segments)} market segments")
                return niches

            except Exception as e:
                raise WorkflowError(
                    message=f"Niche analysis workflow failed: {e}",
                    workflow_step="niche_analysis",
                    original_exception=e
                )

        except ValidationError:
            # Re-raise validation errors
            raise
        except (AgentTeamError, WorkflowError):
            # Re-raise agent team and workflow errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error = handle_exception(
                e,
                error_class=WorkflowError,
                message=f"Unexpected error in niche analysis workflow: {e}",
                details={"workflow_step": "niche_analysis"},
                reraise=True,
                log_level=logging.ERROR
            )
            return []  # This line won't be reached due to reraise=True

    def develop_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """
        Develop an AI solution for a selected niche using the developer agent.

        Args:
            niche: The selected niche object from the niche analysis

        Returns:
            Solution design specification

        Raises:
            ValidationError: If the niche is invalid
            DeveloperAgentError: If there's an issue with the developer agent
            WorkflowError: If there's an issue with the workflow
        """
        try:
            # Validate input
            if not niche or not isinstance(niche, dict):
                raise ValidationError(
                    message="Niche must be a non-empty dictionary",
                    field="niche",
                    validation_errors=[{
                        "field": "niche",
                        "value": str(type(niche)),
                        "error": "Must be a non-empty dictionary"
                    }]
                )

            # Check for required fields
            required_fields = ["id", "name", "market_segment", "opportunity_score"]
            missing_fields = [field for field in required_fields if field not in niche]

            if missing_fields:
                raise ValidationError(
                    message=f"Niche is missing required fields: {', '.join(missing_fields)}",
                    field="niche",
                    validation_errors=[{
                        "field": f"niche.{field}",
                        "error": "Required field is missing"
                    } for field in missing_fields]
                )

            logger.info(f"Developing solution for niche: {niche['name']}")

            try:
                # Store the selected niche in the project state
                self.project_state["selected_niche"] = niche

                # For backward compatibility, also add to identified_niches if not already there
                if niche not in self.project_state["identified_niches"]:
                    self.project_state["identified_niches"].append(niche)

                # Develop the solution
                solution = self.developer.design_solution(niche)

                # Store the solution in the project state
                self.project_state["solution_design"] = solution
                self.project_state["updated_at"] = str(datetime.now().isoformat())

                logger.info(f"Successfully developed solution: {solution.get('name', 'Unnamed solution')}")
                return solution

            except Exception as e:
                raise WorkflowError(
                    message=f"Solution development workflow failed: {e}",
                    workflow_step="develop_solution",
                    original_exception=e
                )

        except ValidationError:
            # Re-raise validation errors
            raise
        except (AgentTeamError, WorkflowError):
            # Re-raise agent team and workflow errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error = handle_exception(
                e,
                error_class=WorkflowError,
                message=f"Unexpected error in solution development workflow: {e}",
                details={"workflow_step": "develop_solution"},
                reraise=True,
                log_level=logging.ERROR
            )
            return {}  # This line won't be reached due to reraise=True

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
