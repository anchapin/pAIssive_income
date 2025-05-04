"""
"""
Team configuration for the pAIssive Income AI agent team.
Team configuration for the pAIssive Income AI agent team.
Defines the overall structure and collaboration patterns for the agent team.
Defines the overall structure and collaboration patterns for the agent team.
"""
"""


import json
import json
import logging
import logging
import os
import os
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar
from typing import Any, Dict, List, Optional, TypeVar


from interfaces.agent_interfaces import IAgentTeam
from interfaces.agent_interfaces import IAgentTeam


from .agent_profiles.developer import DeveloperAgent
from .agent_profiles.developer import DeveloperAgent
from .agent_profiles.feedback import FeedbackAgent
from .agent_profiles.feedback import FeedbackAgent
from .agent_profiles.marketing import MarketingAgent
from .agent_profiles.marketing import MarketingAgent
from .agent_profiles.monetization import MonetizationAgent
from .agent_profiles.monetization import MonetizationAgent
from .agent_profiles.researcher import ResearchAgent
from .agent_profiles.researcher import ResearchAgent
from .errors import (AgentInitializationError, AgentTeamError, ValidationError,
from .errors import (AgentInitializationError, AgentTeamError, ValidationError,
WorkflowError, handle_exception)
WorkflowError, handle_exception)
from .schemas import (FeedbackItemSchema, MarketingPlanSchema,
from .schemas import (FeedbackItemSchema, MarketingPlanSchema,
MonetizationStrategySchema, NicheSchema,
MonetizationStrategySchema, NicheSchema,
ProjectStateSchema, SolutionSchema, TeamConfigSchema)
ProjectStateSchema, SolutionSchema, TeamConfigSchema)


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Type variable for agent interfaces
# Type variable for agent interfaces
T = TypeVar("T")
T = TypeVar("T")




class AgentTeam(IAgentTeam):
    class AgentTeam(IAgentTeam):
    """
    """
    A team of specialized AI agents that collaborate on developing and
    A team of specialized AI agents that collaborate on developing and
    monetizing niche AI tools for passive income generation.
    monetizing niche AI tools for passive income generation.
    """
    """


    def __init__(self, project_name: str, config_path: Optional[str] = None):
    def __init__(self, project_name: str, config_path: Optional[str] = None):
    """
    """
    Initialize the agent team with a project name and optional configuration.
    Initialize the agent team with a project name and optional configuration.


    Args:
    Args:
    project_name: Name of the niche AI tool project
    project_name: Name of the niche AI tool project
    config_path: Optional path to a JSON configuration file
    config_path: Optional path to a JSON configuration file


    Raises:
    Raises:
    ValidationError: If the project name is invalid
    ValidationError: If the project name is invalid
    AgentInitializationError: If an agent fails to initialize
    AgentInitializationError: If an agent fails to initialize
    """
    """
    try:
    try:
    # Validate project name
    # Validate project name
    if not project_name or not isinstance(project_name, str):
    if not project_name or not isinstance(project_name, str):
    raise ValidationError(
    raise ValidationError(
    message="Project name must be a non-empty string",
    message="Project name must be a non-empty string",
    field="project_name",
    field="project_name",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "project_name",
    "field": "project_name",
    "value": project_name,
    "value": project_name,
    "error": "Must be a non-empty string",
    "error": "Must be a non-empty string",
    }
    }
    ],
    ],
    )
    )


    self._project_name = project_name
    self._project_name = project_name
    self._id = str(uuid.uuid4())
    self._id = str(uuid.uuid4())
    logger.info(f"Initializing agent team for project: {project_name}")
    logger.info(f"Initializing agent team for project: {project_name}")


    # Load configuration
    # Load configuration
    try:
    try:
    self._config = self._load_config(config_path)
    self._config = self._load_config(config_path)
except Exception as e:
except Exception as e:
    raise AgentTeamError(
    raise AgentTeamError(
    message=f"Failed to load configuration: {e}",
    message=f"Failed to load configuration: {e}",
    code="config_load_error",
    code="config_load_error",
    original_exception=e,
    original_exception=e,
    )
    )


    # Initialize the specialized agents
    # Initialize the specialized agents
    try:
    try:
    self.researcher = ResearchAgent(self)
    self.researcher = ResearchAgent(self)
    logger.debug(f"Initialized Research Agent for project: {project_name}")
    logger.debug(f"Initialized Research Agent for project: {project_name}")
except Exception as e:
except Exception as e:
    raise AgentInitializationError(
    raise AgentInitializationError(
    message=f"Failed to initialize Research Agent: {e}",
    message=f"Failed to initialize Research Agent: {e}",
    agent_name="Research Agent",
    agent_name="Research Agent",
    original_exception=e,
    original_exception=e,
    )
    )


    try:
    try:
    self.developer = DeveloperAgent(self)
    self.developer = DeveloperAgent(self)
    logger.debug(f"Initialized Developer Agent for project: {project_name}")
    logger.debug(f"Initialized Developer Agent for project: {project_name}")
except Exception as e:
except Exception as e:
    raise AgentInitializationError(
    raise AgentInitializationError(
    message=f"Failed to initialize Developer Agent: {e}",
    message=f"Failed to initialize Developer Agent: {e}",
    agent_name="Developer Agent",
    agent_name="Developer Agent",
    original_exception=e,
    original_exception=e,
    )
    )


    try:
    try:
    self.monetization = MonetizationAgent(self)
    self.monetization = MonetizationAgent(self)
    logger.debug(
    logger.debug(
    f"Initialized Monetization Agent for project: {project_name}"
    f"Initialized Monetization Agent for project: {project_name}"
    )
    )
except Exception as e:
except Exception as e:
    raise AgentInitializationError(
    raise AgentInitializationError(
    message=f"Failed to initialize Monetization Agent: {e}",
    message=f"Failed to initialize Monetization Agent: {e}",
    agent_name="Monetization Agent",
    agent_name="Monetization Agent",
    original_exception=e,
    original_exception=e,
    )
    )


    try:
    try:
    self.marketing = MarketingAgent(self)
    self.marketing = MarketingAgent(self)
    logger.debug(f"Initialized Marketing Agent for project: {project_name}")
    logger.debug(f"Initialized Marketing Agent for project: {project_name}")
except Exception as e:
except Exception as e:
    raise AgentInitializationError(
    raise AgentInitializationError(
    message=f"Failed to initialize Marketing Agent: {e}",
    message=f"Failed to initialize Marketing Agent: {e}",
    agent_name="Marketing Agent",
    agent_name="Marketing Agent",
    original_exception=e,
    original_exception=e,
    )
    )


    try:
    try:
    self.feedback = FeedbackAgent(self)
    self.feedback = FeedbackAgent(self)
    logger.debug(f"Initialized Feedback Agent for project: {project_name}")
    logger.debug(f"Initialized Feedback Agent for project: {project_name}")
except Exception as e:
except Exception as e:
    raise AgentInitializationError(
    raise AgentInitializationError(
    message=f"Failed to initialize Feedback Agent: {e}",
    message=f"Failed to initialize Feedback Agent: {e}",
    agent_name="Feedback Agent",
    agent_name="Feedback Agent",
    original_exception=e,
    original_exception=e,
    )
    )


    # Project state storage
    # Project state storage
    self.project_state = {
    self.project_state = {
    "id": self.id,
    "id": self.id,
    "name": self.project_name,
    "name": self.project_name,
    "identified_niches": [],
    "identified_niches": [],
    "selected_niche": None,
    "selected_niche": None,
    "user_problems": [],
    "user_problems": [],
    "solution_design": None,
    "solution_design": None,
    "monetization_strategy": None,
    "monetization_strategy": None,
    "marketing_plan": None,
    "marketing_plan": None,
    "feedback_data": [],
    "feedback_data": [],
    "created_at": str(datetime.now().isoformat()),
    "created_at": str(datetime.now().isoformat()),
    "updated_at": str(datetime.now().isoformat()),
    "updated_at": str(datetime.now().isoformat()),
    }
    }


    # Agent registry for dependency injection
    # Agent registry for dependency injection
    self._agent_registry = {
    self._agent_registry = {
    "researcher": self.researcher,
    "researcher": self.researcher,
    "developer": self.developer,
    "developer": self.developer,
    "monetization": self.monetization,
    "monetization": self.monetization,
    "marketing": self.marketing,
    "marketing": self.marketing,
    "feedback": self.feedback,
    "feedback": self.feedback,
    }
    }


    logger.info(
    logger.info(
    f"Successfully initialized agent team for project: {project_name}"
    f"Successfully initialized agent team for project: {project_name}"
    )
    )


except ValidationError:
except ValidationError:
    # Re-raise validation errors
    # Re-raise validation errors
    raise
    raise
except AgentTeamError:
except AgentTeamError:
    # Re-raise agent team errors
    # Re-raise agent team errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=AgentTeamError,
    error_class=AgentTeamError,
    message=f"Failed to initialize agent team for project {project_name}",
    message=f"Failed to initialize agent team for project {project_name}",
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    # This line won't be reached due to reraise=True
    # This line won't be reached due to reraise=True


    @property
    @property
    def project_name(self) -> str:
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
    """
    Get an agent by type.
    Get an agent by type.


    Args:
    Args:
    agent_type: Type of agent to get
    agent_type: Type of agent to get


    Returns:
    Returns:
    Agent instance
    Agent instance


    Raises:
    Raises:
    ValueError: If the agent type is invalid
    ValueError: If the agent type is invalid
    """
    """
    if agent_type not in self._agent_registry:
    if agent_type not in self._agent_registry:
    raise ValueError(
    raise ValueError(
    f"Invalid agent type: {agent_type}. Valid types are: {', '.join(self._agent_registry.keys())}"
    f"Invalid agent type: {agent_type}. Valid types are: {', '.join(self._agent_registry.keys())}"
    )
    )


    return self._agent_registry[agent_type]
    return self._agent_registry[agent_type]


    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
    """
    """
    Load configuration from a JSON file or use default configuration.
    Load configuration from a JSON file or use default configuration.


    Args:
    Args:
    config_path: Path to a JSON configuration file
    config_path: Path to a JSON configuration file


    Returns:
    Returns:
    Configuration dictionary
    Configuration dictionary


    Raises:
    Raises:
    ValidationError: If the configuration is invalid
    ValidationError: If the configuration is invalid
    AgentTeamError: If there's an issue loading the configuration
    AgentTeamError: If there's an issue loading the configuration
    """
    """
    try:
    try:
    default_config = {
    default_config = {
    "model_settings": {
    "model_settings": {
    "researcher": {"model": "gpt-4", "temperature": 0.7},
    "researcher": {"model": "gpt-4", "temperature": 0.7},
    "developer": {"model": "gpt-4", "temperature": 0.2},
    "developer": {"model": "gpt-4", "temperature": 0.2},
    "monetization": {"model": "gpt-4", "temperature": 0.5},
    "monetization": {"model": "gpt-4", "temperature": 0.5},
    "marketing": {"model": "gpt-4", "temperature": 0.8},
    "marketing": {"model": "gpt-4", "temperature": 0.8},
    "feedback": {"model": "gpt-4", "temperature": 0.3},
    "feedback": {"model": "gpt-4", "temperature": 0.3},
    },
    },
    "workflow": {
    "workflow": {
    "auto_progression": False,
    "auto_progression": False,
    "review_required": True,
    "review_required": True,
    },
    },
    }
    }


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    raise ValidationError(
    raise ValidationError(
    message=f"Configuration file not found: {config_path}",
    message=f"Configuration file not found: {config_path}",
    field="config_path",
    field="config_path",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "config_path",
    "field": "config_path",
    "value": config_path,
    "value": config_path,
    "error": "File not found",
    "error": "File not found",
    }
    }
    ],
    ],
    )
    )


    try:
    try:
    with open(config_path, "r") as f:
    with open(config_path, "r") as f:
    try:
    try:
    user_config = json.load(f)
    user_config = json.load(f)
except json.JSONDecodeError as e:
except json.JSONDecodeError as e:
    raise ValidationError(
    raise ValidationError(
    message=f"Invalid JSON in configuration file: {e}",
    message=f"Invalid JSON in configuration file: {e}",
    field="config_file_content",
    field="config_file_content",
    original_exception=e,
    original_exception=e,
    )
    )


    # Merge user config with default config
    # Merge user config with default config
    for key, value in user_config.items():
    for key, value in user_config.items():
    if (
    if (
    key in default_config
    key in default_config
    and isinstance(value, dict)
    and isinstance(value, dict)
    and isinstance(default_config[key], dict)
    and isinstance(default_config[key], dict)
    ):
    ):
    default_config[key].update(value)
    default_config[key].update(value)
    else:
    else:
    default_config[key] = value
    default_config[key] = value


except (IOError, OSError) as e:
except (IOError, OSError) as e:
    raise AgentTeamError(
    raise AgentTeamError(
    message=f"Failed to read configuration file: {e}",
    message=f"Failed to read configuration file: {e}",
    code="config_file_error",
    code="config_file_error",
    original_exception=e,
    original_exception=e,
    )
    )


    # Validate the config using Pydantic schema
    # Validate the config using Pydantic schema
    try:
    try:
    validated_config = TeamConfigSchema(**default_config).dict()
    validated_config = TeamConfigSchema(**default_config).dict()
    logger.info(
    logger.info(
    "Successfully validated configuration using Pydantic schema"
    "Successfully validated configuration using Pydantic schema"
    )
    )
    return validated_config
    return validated_config
except Exception as e:
except Exception as e:
    raise ValidationError(
    raise ValidationError(
    message=f"Invalid configuration: {e}",
    message=f"Invalid configuration: {e}",
    field="config",
    field="config",
    original_exception=e,
    original_exception=e,
    )
    )


except ValidationError:
except ValidationError:
    # Re-raise validation errors
    # Re-raise validation errors
    raise
    raise
except AgentTeamError:
except AgentTeamError:
    # Re-raise agent team errors
    # Re-raise agent team errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=AgentTeamError,
    error_class=AgentTeamError,
    message=f"Failed to load configuration: {e}",
    message=f"Failed to load configuration: {e}",
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    return {}  # This line won't be reached due to reraise=True
    return {}  # This line won't be reached due to reraise=True


    def run_niche_analysis(self, market_segments: List[str]) -> List[Dict[str, Any]]:
    def run_niche_analysis(self, market_segments: List[str]) -> List[Dict[str, Any]]:
    """
    """
    Run a complete niche analysis workflow using the researcher agent.
    Run a complete niche analysis workflow using the researcher agent.


    Algorithm description:
    Algorithm description:
    ---------------------
    ---------------------
    The algorithm follows these steps:
    The algorithm follows these steps:
    1. Validate the input market segments (non-empty list of strings)
    1. Validate the input market segments (non-empty list of strings)
    2. Invoke the researcher agent's analyze_market_segments method, which:
    2. Invoke the researcher agent's analyze_market_segments method, which:
    a. Breaks down each segment into potential niches
    a. Breaks down each segment into potential niches
    b. Evaluates each niche based on multiple factors (market size, growth, etc.)
    b. Evaluates each niche based on multiple factors (market size, growth, etc.)
    c. Ranks niches by opportunity score
    c. Ranks niches by opportunity score
    3. Store the identified niches in the project state
    3. Store the identified niches in the project state
    4. Return the list of identified niches
    4. Return the list of identified niches


    Performance considerations:
    Performance considerations:
    -------------------------
    -------------------------
    - Time complexity: O(s*n*f), where:
    - Time complexity: O(s*n*f), where:
    * s = number of market segments
    * s = number of market segments
    * n = average number of niches per segment
    * n = average number of niches per segment
    * f = number of factors evaluated per niche
    * f = number of factors evaluated per niche
    - This algorithm handles API rate limiting by batching requests when possible
    - This algorithm handles API rate limiting by batching requests when possible


    Args:
    Args:
    market_segments: List of market segments to analyze
    market_segments: List of market segments to analyze


    Returns:
    Returns:
    List of identified niche opportunities with scores
    List of identified niche opportunities with scores


    Raises:
    Raises:
    ValidationError: If the market segments are invalid
    ValidationError: If the market segments are invalid
    ResearchAgentError: If there's an issue with the research agent
    ResearchAgentError: If there's an issue with the research agent
    WorkflowError: If there's an issue with the workflow
    WorkflowError: If there's an issue with the workflow
    """
    """
    try:
    try:
    # Validate input
    # Validate input
    if not market_segments:
    if not market_segments:
    raise ValidationError(
    raise ValidationError(
    message="Market segments list cannot be empty",
    message="Market segments list cannot be empty",
    field="market_segments",
    field="market_segments",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "market_segments",
    "field": "market_segments",
    "value": str(market_segments),
    "value": str(market_segments),
    "error": "Cannot be empty",
    "error": "Cannot be empty",
    }
    }
    ],
    ],
    )
    )


    if not isinstance(market_segments, list):
    if not isinstance(market_segments, list):
    raise ValidationError(
    raise ValidationError(
    message="Market segments must be a list",
    message="Market segments must be a list",
    field="market_segments",
    field="market_segments",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "market_segments",
    "field": "market_segments",
    "value": str(type(market_segments)),
    "value": str(type(market_segments)),
    "error": "Must be a list",
    "error": "Must be a list",
    }
    }
    ],
    ],
    )
    )


    for i, segment in enumerate(market_segments):
    for i, segment in enumerate(market_segments):
    if not segment or not isinstance(segment, str):
    if not segment or not isinstance(segment, str):
    raise ValidationError(
    raise ValidationError(
    message=f"Market segment at index {i} must be a non-empty string",
    message=f"Market segment at index {i} must be a non-empty string",
    field=f"market_segments[{i}]",
    field=f"market_segments[{i}]",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": f"market_segments[{i}]",
    "field": f"market_segments[{i}]",
    "value": str(segment),
    "value": str(segment),
    "error": "Must be a non-empty string",
    "error": "Must be a non-empty string",
    }
    }
    ],
    ],
    )
    )


    logger.info(
    logger.info(
    f"Running niche analysis for market segments: {', '.join(market_segments)}"
    f"Running niche analysis for market segments: {', '.join(market_segments)}"
    )
    )


    try:
    try:
    # Run the analysis
    # Run the analysis
    niches = self.researcher.analyze_market_segments(market_segments)
    niches = self.researcher.analyze_market_segments(market_segments)


    # Store the results in the project state
    # Store the results in the project state
    self.project_state["identified_niches"] = niches
    self.project_state["identified_niches"] = niches
    self.project_state["updated_at"] = str(datetime.now().isoformat())
    self.project_state["updated_at"] = str(datetime.now().isoformat())


    logger.info(
    logger.info(
    f"Identified {len(niches)} niches across {len(market_segments)} market segments"
    f"Identified {len(niches)} niches across {len(market_segments)} market segments"
    )
    )
    return niches
    return niches


except Exception as e:
except Exception as e:
    raise WorkflowError(
    raise WorkflowError(
    message=f"Niche analysis workflow failed: {e}",
    message=f"Niche analysis workflow failed: {e}",
    workflow_step="niche_analysis",
    workflow_step="niche_analysis",
    original_exception=e,
    original_exception=e,
    )
    )


except ValidationError:
except ValidationError:
    # Re-raise validation errors
    # Re-raise validation errors
    raise
    raise
except (AgentTeamError, WorkflowError):
except (AgentTeamError, WorkflowError):
    # Re-raise agent team and workflow errors
    # Re-raise agent team and workflow errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=WorkflowError,
    error_class=WorkflowError,
    message=f"Unexpected error in niche analysis workflow: {e}",
    message=f"Unexpected error in niche analysis workflow: {e}",
    details={"workflow_step": "niche_analysis"},
    details={"workflow_step": "niche_analysis"},
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    return []  # This line won't be reached due to reraise=True
    return []  # This line won't be reached due to reraise=True


    def develop_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]:
    def develop_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Develop an AI solution for a selected niche using the developer agent.
    Develop an AI solution for a selected niche using the developer agent.


    Algorithm description:
    Algorithm description:
    ---------------------
    ---------------------
    The solution development algorithm follows these steps:
    The solution development algorithm follows these steps:
    1. Validate and normalize the input niche data using Pydantic schema
    1. Validate and normalize the input niche data using Pydantic schema
    2. Store the selected niche in the project state for workflow continuity
    2. Store the selected niche in the project state for workflow continuity
    3. Invoke the developer agent's design_solution method, which:
    3. Invoke the developer agent's design_solution method, which:
    a. Analyzes user problems in the niche
    a. Analyzes user problems in the niche
    b. Identifies AI capabilities needed to solve these problems
    b. Identifies AI capabilities needed to solve these problems
    c. Creates a solution architecture with component specifications
    c. Creates a solution architecture with component specifications
    d. Generates feature lists and technology stack recommendations
    d. Generates feature lists and technology stack recommendations
    4. Validate the resulting solution design with schema validation
    4. Validate the resulting solution design with schema validation
    5. Store the solution design in the project state
    5. Store the solution design in the project state
    6. Return the validated solution design
    6. Return the validated solution design


    Performance considerations:
    Performance considerations:
    -------------------------
    -------------------------
    - Time complexity: O(p*c), where:
    - Time complexity: O(p*c), where:
    * p = number of problems identified in the niche
    * p = number of problems identified in the niche
    * c = number of components needed for the solution
    * c = number of components needed for the solution
    - Memory complexity: O(f), where f is the number of features in the solution
    - Memory complexity: O(f), where f is the number of features in the solution


    Args:
    Args:
    niche: The selected niche object from the niche analysis
    niche: The selected niche object from the niche analysis


    Returns:
    Returns:
    Solution design specification
    Solution design specification


    Raises:
    Raises:
    ValidationError: If the niche is invalid
    ValidationError: If the niche is invalid
    DeveloperAgentError: If there's an issue with the developer agent
    DeveloperAgentError: If there's an issue with the developer agent
    WorkflowError: If there's an issue with the workflow
    WorkflowError: If there's an issue with the workflow
    """
    """
    try:
    try:
    # Validate input using Pydantic schema
    # Validate input using Pydantic schema
    try:
    try:
    validated_niche = NicheSchema(**niche).dict()
    validated_niche = NicheSchema(**niche).dict()
    logger.info("Successfully validated niche input using Pydantic schema")
    logger.info("Successfully validated niche input using Pydantic schema")
except Exception as e:
except Exception as e:
    raise ValidationError(
    raise ValidationError(
    message=f"Invalid niche data: {e}",
    message=f"Invalid niche data: {e}",
    field="niche",
    field="niche",
    original_exception=e,
    original_exception=e,
    )
    )


    logger.info(f"Developing solution for niche: {validated_niche['name']}")
    logger.info(f"Developing solution for niche: {validated_niche['name']}")


    try:
    try:
    # Store the selected niche in the project state
    # Store the selected niche in the project state
    self.project_state["selected_niche"] = validated_niche
    self.project_state["selected_niche"] = validated_niche


    # For backward compatibility, also add to identified_niches if not already there
    # For backward compatibility, also add to identified_niches if not already there
    if validated_niche not in self.project_state["identified_niches"]:
    if validated_niche not in self.project_state["identified_niches"]:
    self.project_state["identified_niches"].append(validated_niche)
    self.project_state["identified_niches"].append(validated_niche)


    # Develop the solution
    # Develop the solution
    solution = self.developer.design_solution(validated_niche)
    solution = self.developer.design_solution(validated_niche)


    # Validate solution using Pydantic schema
    # Validate solution using Pydantic schema
    try:
    try:
    validated_solution = SolutionSchema(**solution).dict()
    validated_solution = SolutionSchema(**solution).dict()
    logger.info(
    logger.info(
    "Successfully validated solution output using Pydantic schema"
    "Successfully validated solution output using Pydantic schema"
    )
    )
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Solution data does not fully conform to schema: {e}"
    f"Solution data does not fully conform to schema: {e}"
    )
    )
    # Continue with original solution data if validation fails
    # Continue with original solution data if validation fails
    validated_solution = solution
    validated_solution = solution


    # Store the solution in the project state
    # Store the solution in the project state
    self.project_state["solution_design"] = validated_solution
    self.project_state["solution_design"] = validated_solution
    self.project_state["updated_at"] = str(datetime.now().isoformat())
    self.project_state["updated_at"] = str(datetime.now().isoformat())


    logger.info(
    logger.info(
    f"Successfully developed solution: {validated_solution.get('name', 'Unnamed solution')}"
    f"Successfully developed solution: {validated_solution.get('name', 'Unnamed solution')}"
    )
    )
    return validated_solution
    return validated_solution


except Exception as e:
except Exception as e:
    raise WorkflowError(
    raise WorkflowError(
    message=f"Solution development workflow failed: {e}",
    message=f"Solution development workflow failed: {e}",
    workflow_step="develop_solution",
    workflow_step="develop_solution",
    original_exception=e,
    original_exception=e,
    )
    )


except ValidationError:
except ValidationError:
    # Re-raise validation errors
    # Re-raise validation errors
    raise
    raise
except (AgentTeamError, WorkflowError):
except (AgentTeamError, WorkflowError):
    # Re-raise agent team and workflow errors
    # Re-raise agent team and workflow errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=WorkflowError,
    error_class=WorkflowError,
    message=f"Unexpected error in solution development workflow: {e}",
    message=f"Unexpected error in solution development workflow: {e}",
    details={"workflow_step": "develop_solution"},
    details={"workflow_step": "develop_solution"},
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    return {}  # This line won't be reached due to reraise=True
    return {}  # This line won't be reached due to reraise=True


    def create_monetization_strategy(
    def create_monetization_strategy(
    self, solution: Optional[Dict[str, Any]] = None
    self, solution: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a monetization strategy for the developed solution.
    Create a monetization strategy for the developed solution.


    Algorithm description:
    Algorithm description:
    ---------------------
    ---------------------
    The monetization strategy algorithm operates as follows:
    The monetization strategy algorithm operates as follows:
    1. Validate the input solution or use the solution from project state
    1. Validate the input solution or use the solution from project state
    2. Store solution in project state if new and needed for workflow continuity
    2. Store solution in project state if new and needed for workflow continuity
    3. Invoke monetization agent's create_strategy method, which:
    3. Invoke monetization agent's create_strategy method, which:
    a. Analyzes the solution features and target market
    a. Analyzes the solution features and target market
    b. Evaluates multiple pricing models (subscription, one-time, freemium, etc.)
    b. Evaluates multiple pricing models (subscription, one-time, freemium, etc.)
    c. Calculates optimal price points based on market research
    c. Calculates optimal price points based on market research
    d. Generates revenue projections and cash flow estimates
    d. Generates revenue projections and cash flow estimates
    e. Recommends customer acquisition and retention strategies
    e. Recommends customer acquisition and retention strategies
    4. Validate the resulting strategy with schema validation
    4. Validate the resulting strategy with schema validation
    5. Store the monetization strategy in the project state
    5. Store the monetization strategy in the project state
    6. Return the validated monetization strategy
    6. Return the validated monetization strategy


    Performance considerations:
    Performance considerations:
    -------------------------
    -------------------------
    - Time complexity: O(m*p), where:
    - Time complexity: O(m*p), where:
    * m = number of monetization models evaluated
    * m = number of monetization models evaluated
    * p = number of price points analyzed per model
    * p = number of price points analyzed per model
    - The algorithm dynamically adjusts calculation precision based on input size
    - The algorithm dynamically adjusts calculation precision based on input size


    Args:
    Args:
    solution: Optional solution object. If not provided, uses the solution from project state.
    solution: Optional solution object. If not provided, uses the solution from project state.


    Returns:
    Returns:
    Monetization strategy specification
    Monetization strategy specification


    Raises:
    Raises:
    ValidationError: If the solution is invalid
    ValidationError: If the solution is invalid
    MonetizationAgentError: If there's an issue with the monetization agent
    MonetizationAgentError: If there's an issue with the monetization agent
    WorkflowError: If there's an issue with the workflow
    WorkflowError: If there's an issue with the workflow
    """
    """
    try:
    try:
    # If solution is provided, validate it using Pydantic schema
    # If solution is provided, validate it using Pydantic schema
    if solution:
    if solution:
    try:
    try:
    validated_solution = SolutionSchema(**solution).dict()
    validated_solution = SolutionSchema(**solution).dict()
    logger.info(
    logger.info(
    "Successfully validated solution input using Pydantic schema"
    "Successfully validated solution input using Pydantic schema"
    )
    )
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Solution data does not fully conform to schema: {e}"
    f"Solution data does not fully conform to schema: {e}"
    )
    )
    validated_solution = solution
    validated_solution = solution


    # Store the solution in the project state if it's not already there
    # Store the solution in the project state if it's not already there
    if not self.project_state["solution_design"]:
    if not self.project_state["solution_design"]:
    self.project_state["solution_design"] = validated_solution
    self.project_state["solution_design"] = validated_solution
    elif not self.project_state["solution_design"]:
    elif not self.project_state["solution_design"]:
    raise ValueError(
    raise ValueError(
    "Solution must be designed before creating monetization strategy"
    "Solution must be designed before creating monetization strategy"
    )
    )


    # Use the solution from the project state or the provided solution
    # Use the solution from the project state or the provided solution
    solution_to_use = (
    solution_to_use = (
    validated_solution
    validated_solution
    if solution
    if solution
    else self.project_state["solution_design"]
    else self.project_state["solution_design"]
    )
    )


    try:
    try:
    # Create the monetization strategy
    # Create the monetization strategy
    strategy = self.monetization.create_strategy(solution_to_use)
    strategy = self.monetization.create_strategy(solution_to_use)


    # Validate strategy using Pydantic schema
    # Validate strategy using Pydantic schema
    try:
    try:
    validated_strategy = MonetizationStrategySchema(**strategy).dict()
    validated_strategy = MonetizationStrategySchema(**strategy).dict()
    logger.info(
    logger.info(
    "Successfully validated monetization strategy using Pydantic schema"
    "Successfully validated monetization strategy using Pydantic schema"
    )
    )
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Monetization strategy does not fully conform to schema: {e}"
    f"Monetization strategy does not fully conform to schema: {e}"
    )
    )
    validated_strategy = strategy
    validated_strategy = strategy


    # Store the strategy in the project state
    # Store the strategy in the project state
    self.project_state["monetization_strategy"] = validated_strategy
    self.project_state["monetization_strategy"] = validated_strategy
    self.project_state["updated_at"] = str(datetime.now().isoformat())
    self.project_state["updated_at"] = str(datetime.now().isoformat())


    logger.info(
    logger.info(
    f"Successfully created monetization strategy for solution: {solution_to_use.get('name', 'Unnamed solution')}"
    f"Successfully created monetization strategy for solution: {solution_to_use.get('name', 'Unnamed solution')}"
    )
    )
    return validated_strategy
    return validated_strategy


except Exception as e:
except Exception as e:
    raise WorkflowError(
    raise WorkflowError(
    message=f"Monetization strategy creation workflow failed: {e}",
    message=f"Monetization strategy creation workflow failed: {e}",
    workflow_step="create_monetization_strategy",
    workflow_step="create_monetization_strategy",
    original_exception=e,
    original_exception=e,
    )
    )


except ValueError:
except ValueError:
    # Re-raise value errors
    # Re-raise value errors
    raise
    raise
except (AgentTeamError, WorkflowError):
except (AgentTeamError, WorkflowError):
    # Re-raise agent team and workflow errors
    # Re-raise agent team and workflow errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=WorkflowError,
    error_class=WorkflowError,
    message=f"Unexpected error in monetization strategy workflow: {e}",
    message=f"Unexpected error in monetization strategy workflow: {e}",
    details={"workflow_step": "create_monetization_strategy"},
    details={"workflow_step": "create_monetization_strategy"},
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    return {}  # This line won't be reached due to reraise=True
    return {}  # This line won't be reached due to reraise=True


    def create_marketing_plan(
    def create_marketing_plan(
    self,
    self,
    niche: Optional[Dict[str, Any]] = None,
    niche: Optional[Dict[str, Any]] = None,
    solution: Optional[Dict[str, Any]] = None,
    solution: Optional[Dict[str, Any]] = None,
    monetization: Optional[Dict[str, Any]] = None,
    monetization: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a marketing plan for the developed solution.
    Create a marketing plan for the developed solution.


    Algorithm description:
    Algorithm description:
    ---------------------
    ---------------------
    The marketing plan creation algorithm follows these steps:
    The marketing plan creation algorithm follows these steps:
    1. Validate and collect required inputs (niche, solution, monetization strategy)
    1. Validate and collect required inputs (niche, solution, monetization strategy)
    a. Use provided inputs or fall back to project state
    a. Use provided inputs or fall back to project state
    b. Validate each input with its respective schema
    b. Validate each input with its respective schema
    2. Invoke marketing agent's create_plan method, which:
    2. Invoke marketing agent's create_plan method, which:
    a. Analyzes target audience characteristics from the niche information
    a. Analyzes target audience characteristics from the niche information
    b. Examines unique selling propositions from solution features
    b. Examines unique selling propositions from solution features
    c. Considers pricing strategy from monetization information
    c. Considers pricing strategy from monetization information
    d. Identifies optimal marketing channels for the audience
    d. Identifies optimal marketing channels for the audience
    e. Generates content strategies tailored to the solution
    e. Generates content strategies tailored to the solution
    f. Creates measurement and optimization approaches
    f. Creates measurement and optimization approaches
    3. Validate the resulting marketing plan with schema validation
    3. Validate the resulting marketing plan with schema validation
    4. Store the marketing plan in the project state
    4. Store the marketing plan in the project state
    5. Return the validated marketing plan
    5. Return the validated marketing plan


    Performance considerations:
    Performance considerations:
    -------------------------
    -------------------------
    - Time complexity: O(c*a), where:
    - Time complexity: O(c*a), where:
    * c = number of marketing channels evaluated
    * c = number of marketing channels evaluated
    * a = number of audience segments analyzed
    * a = number of audience segments analyzed
    - The algorithm prioritizes high-ROI marketing channels based on audience analysis
    - The algorithm prioritizes high-ROI marketing channels based on audience analysis


    Args:
    Args:
    niche: Optional niche object. If not provided, uses the niche from project state.
    niche: Optional niche object. If not provided, uses the niche from project state.
    solution: Optional solution object. If not provided, uses the solution from project state.
    solution: Optional solution object. If not provided, uses the solution from project state.
    monetization: Optional monetization strategy object. If not provided, uses the strategy from project state.
    monetization: Optional monetization strategy object. If not provided, uses the strategy from project state.


    Returns:
    Returns:
    Marketing plan specification
    Marketing plan specification


    Raises:
    Raises:
    ValidationError: If any of the inputs are invalid
    ValidationError: If any of the inputs are invalid
    MarketingAgentError: If there's an issue with the marketing agent
    MarketingAgentError: If there's an issue with the marketing agent
    WorkflowError: If there's an issue with the workflow
    WorkflowError: If there's an issue with the workflow
    """
    """
    try:
    try:
    # Use provided objects or fall back to project state
    # Use provided objects or fall back to project state
    niche_to_use = niche if niche else self.project_state["selected_niche"]
    niche_to_use = niche if niche else self.project_state["selected_niche"]
    solution_to_use = (
    solution_to_use = (
    solution if solution else self.project_state["solution_design"]
    solution if solution else self.project_state["solution_design"]
    )
    )
    monetization_to_use = (
    monetization_to_use = (
    monetization
    monetization
    if monetization
    if monetization
    else self.project_state["monetization_strategy"]
    else self.project_state["monetization_strategy"]
    )
    )


    # Validate that we have all required objects
    # Validate that we have all required objects
    if not niche_to_use:
    if not niche_to_use:
    raise ValueError(
    raise ValueError(
    "Niche must be selected before creating marketing plan"
    "Niche must be selected before creating marketing plan"
    )
    )
    if not solution_to_use:
    if not solution_to_use:
    raise ValueError(
    raise ValueError(
    "Solution must be designed before creating marketing plan"
    "Solution must be designed before creating marketing plan"
    )
    )
    if not monetization_to_use:
    if not monetization_to_use:
    raise ValueError(
    raise ValueError(
    "Monetization strategy must be created before marketing plan"
    "Monetization strategy must be created before marketing plan"
    )
    )


    # Validate inputs using Pydantic schemas
    # Validate inputs using Pydantic schemas
    try:
    try:
    if niche:
    if niche:
    validated_niche = NicheSchema(**niche_to_use).dict()
    validated_niche = NicheSchema(**niche_to_use).dict()
    logger.info(
    logger.info(
    "Successfully validated niche input using Pydantic schema"
    "Successfully validated niche input using Pydantic schema"
    )
    )
    niche_to_use = validated_niche
    niche_to_use = validated_niche
except Exception as e:
except Exception as e:
    logger.warning(f"Niche data does not fully conform to schema: {e}")
    logger.warning(f"Niche data does not fully conform to schema: {e}")


    try:
    try:
    if solution:
    if solution:
    validated_solution = SolutionSchema(**solution_to_use).dict()
    validated_solution = SolutionSchema(**solution_to_use).dict()
    logger.info(
    logger.info(
    "Successfully validated solution input using Pydantic schema"
    "Successfully validated solution input using Pydantic schema"
    )
    )
    solution_to_use = validated_solution
    solution_to_use = validated_solution
except Exception as e:
except Exception as e:
    logger.warning(f"Solution data does not fully conform to schema: {e}")
    logger.warning(f"Solution data does not fully conform to schema: {e}")


    try:
    try:
    if monetization:
    if monetization:
    validated_monetization = MonetizationStrategySchema(
    validated_monetization = MonetizationStrategySchema(
    **monetization_to_use
    **monetization_to_use
    ).dict()
    ).dict()
    logger.info(
    logger.info(
    "Successfully validated monetization input using Pydantic schema"
    "Successfully validated monetization input using Pydantic schema"
    )
    )
    monetization_to_use = validated_monetization
    monetization_to_use = validated_monetization
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Monetization data does not fully conform to schema: {e}"
    f"Monetization data does not fully conform to schema: {e}"
    )
    )


    try:
    try:
    # Create the marketing plan
    # Create the marketing plan
    plan = self.marketing.create_plan(
    plan = self.marketing.create_plan(
    niche_to_use, solution_to_use, monetization_to_use
    niche_to_use, solution_to_use, monetization_to_use
    )
    )


    # Validate marketing plan using Pydantic schema
    # Validate marketing plan using Pydantic schema
    try:
    try:
    validated_plan = MarketingPlanSchema(**plan).dict()
    validated_plan = MarketingPlanSchema(**plan).dict()
    logger.info(
    logger.info(
    "Successfully validated marketing plan using Pydantic schema"
    "Successfully validated marketing plan using Pydantic schema"
    )
    )
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Marketing plan does not fully conform to schema: {e}"
    f"Marketing plan does not fully conform to schema: {e}"
    )
    )
    validated_plan = plan
    validated_plan = plan


    # Store the plan in the project state
    # Store the plan in the project state
    self.project_state["marketing_plan"] = validated_plan
    self.project_state["marketing_plan"] = validated_plan
    self.project_state["updated_at"] = str(datetime.now().isoformat())
    self.project_state["updated_at"] = str(datetime.now().isoformat())


    logger.info(
    logger.info(
    f"Successfully created marketing plan for solution: {solution_to_use.get('name', 'Unnamed solution')}"
    f"Successfully created marketing plan for solution: {solution_to_use.get('name', 'Unnamed solution')}"
    )
    )
    return validated_plan
    return validated_plan


except Exception as e:
except Exception as e:
    raise WorkflowError(
    raise WorkflowError(
    message=f"Marketing plan creation workflow failed: {e}",
    message=f"Marketing plan creation workflow failed: {e}",
    workflow_step="create_marketing_plan",
    workflow_step="create_marketing_plan",
    original_exception=e,
    original_exception=e,
    )
    )


except ValueError:
except ValueError:
    # Re-raise value errors
    # Re-raise value errors
    raise
    raise
except (AgentTeamError, WorkflowError):
except (AgentTeamError, WorkflowError):
    # Re-raise agent team and workflow errors
    # Re-raise agent team and workflow errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=WorkflowError,
    error_class=WorkflowError,
    message=f"Unexpected error in marketing plan workflow: {e}",
    message=f"Unexpected error in marketing plan workflow: {e}",
    details={"workflow_step": "create_marketing_plan"},
    details={"workflow_step": "create_marketing_plan"},
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    return {}  # This line won't be reached due to reraise=True
    return {}  # This line won't be reached due to reraise=True


    def process_feedback(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    def process_feedback(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    """
    Process user feedback and generate improvement recommendations.
    Process user feedback and generate improvement recommendations.


    Args:
    Args:
    feedback_data: List of user feedback items
    feedback_data: List of user feedback items


    Returns:
    Returns:
    Analysis and recommendations based on feedback
    Analysis and recommendations based on feedback


    Raises:
    Raises:
    ValidationError: If the feedback data is invalid
    ValidationError: If the feedback data is invalid
    FeedbackAgentError: If there's an issue with the feedback agent
    FeedbackAgentError: If there's an issue with the feedback agent
    WorkflowError: If there's an issue with the workflow
    WorkflowError: If there's an issue with the workflow
    """
    """
    try:
    try:
    # Validate feedback data using Pydantic schema
    # Validate feedback data using Pydantic schema
    validated_feedback_items = []
    validated_feedback_items = []
    for i, item in enumerate(feedback_data):
    for i, item in enumerate(feedback_data):
    try:
    try:
    validated_item = FeedbackItemSchema(**item).dict()
    validated_item = FeedbackItemSchema(**item).dict()
    validated_feedback_items.append(validated_item)
    validated_feedback_items.append(validated_item)
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Feedback item at index {i} does not conform to schema: {e}"
    f"Feedback item at index {i} does not conform to schema: {e}"
    )
    )
    validated_feedback_items.append(item)
    validated_feedback_items.append(item)


    # Store feedback in the project state
    # Store feedback in the project state
    self.project_state["feedback_data"].extend(validated_feedback_items)
    self.project_state["feedback_data"].extend(validated_feedback_items)
    self.project_state["updated_at"] = str(datetime.now().isoformat())
    self.project_state["updated_at"] = str(datetime.now().isoformat())


    # Process the feedback
    # Process the feedback
    analysis = self.feedback.analyze_feedback(validated_feedback_items)
    analysis = self.feedback.analyze_feedback(validated_feedback_items)


    logger.info(
    logger.info(
    f"Successfully processed {len(validated_feedback_items)} feedback items"
    f"Successfully processed {len(validated_feedback_items)} feedback items"
    )
    )
    return analysis
    return analysis


except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(
    handle_exception(
    e,
    e,
    error_class=WorkflowError,
    error_class=WorkflowError,
    message=f"Unexpected error in feedback processing workflow: {e}",
    message=f"Unexpected error in feedback processing workflow: {e}",
    details={"workflow_step": "process_feedback"},
    details={"workflow_step": "process_feedback"},
    reraise=True,
    reraise=True,
    log_level=logging.ERROR,
    log_level=logging.ERROR,
    )
    )
    return {}  # This line won't be reached due to reraise=True
    return {}  # This line won't be reached due to reraise=True


    def export_project_plan(self, output_path: str) -> None:
    def export_project_plan(self, output_path: str) -> None:
    """
    """
    Export the complete project plan to a JSON file.
    Export the complete project plan to a JSON file.


    Args:
    Args:
    output_path: Path to save the project plan
    output_path: Path to save the project plan


    Raises:
    Raises:
    IOError: If there's an issue writing to the file
    IOError: If there's an issue writing to the file
    """
    """
    try:
    try:
    # Validate project state using Pydantic schema
    # Validate project state using Pydantic schema
    try:
    try:
    validated_state = ProjectStateSchema(**self.project_state).dict()
    validated_state = ProjectStateSchema(**self.project_state).dict()
    logger.info(
    logger.info(
    "Successfully validated project state using Pydantic schema"
    "Successfully validated project state using Pydantic schema"
    )
    )
except Exception as e:
except Exception as e:
    logger.warning(f"Project state does not fully conform to schema: {e}")
    logger.warning(f"Project state does not fully conform to schema: {e}")
    validated_state = self.project_state
    validated_state = self.project_state


    with open(output_path, "w") as f:
    with open(output_path, "w") as f:
    json.dump(validated_state, f, indent=2)
    json.dump(validated_state, f, indent=2)


    logger.info(f"Successfully exported project plan to: {output_path}")
    logger.info(f"Successfully exported project plan to: {output_path}")


except (IOError, OSError) as e:
except (IOError, OSError) as e:
    logger.error(f"Failed to export project plan: {e}")
    logger.error(f"Failed to export project plan: {e}")
    raise
    raise


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the agent team."""
    return f"AgentTeam(project_name={self.project_name}, agents=5)"
