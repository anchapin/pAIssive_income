"""
"""
Integration with the agent team for the AI Models module.
Integration with the agent team for the AI Models module.


This module provides functions and classes for integrating the AI Models module
This module provides functions and classes for integrating the AI Models module
with the agent team, allowing agents to use local AI models for their tasks.
with the agent team, allowing agents to use local AI models for their tasks.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dependency_container import get_container
from dependency_container import get_container
from interfaces.model_interfaces import IModelInfo, IModelManager
from interfaces.model_interfaces import IModelInfo, IModelManager


# Import the fallback manager classes
# Import the fallback manager classes
from .fallbacks import FallbackManager, FallbackStrategy
from .fallbacks import FallbackManager, FallbackStrategy
from .model_manager import ModelManager
from .model_manager import ModelManager


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class AgentModelProvider:
    class AgentModelProvider:
    """
    """
    Provider for AI models used by agents.
    Provider for AI models used by agents.


    This class serves as a bridge between the Agent Team module and the AI Models module,
    This class serves as a bridge between the Agent Team module and the AI Models module,
    providing a way for different agent types (researcher, developer, etc.) to access
    providing a way for different agent types (researcher, developer, etc.) to access
    appropriate AI models for their specific tasks. It implements a sophisticated model
    appropriate AI models for their specific tasks. It implements a sophisticated model
    selection algorithm that considers both the agent type and task type when finding
    selection algorithm that considers both the agent type and task type when finding
    the most suitable model.
    the most suitable model.


    The provider maintains a mapping of agent-to-model assignments and can dynamically
    The provider maintains a mapping of agent-to-model assignments and can dynamically
    find models based on predefined preferences when no explicit assignment exists.
    find models based on predefined preferences when no explicit assignment exists.


    It also implements a robust fallback strategy to ensure that agents always have
    It also implements a robust fallback strategy to ensure that agents always have
    a model to use, even if their preferred models are not available.
    a model to use, even if their preferred models are not available.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_manager: Optional[IModelManager] = None,
    model_manager: Optional[IModelManager] = None,
    fallback_enabled: bool = True,
    fallback_enabled: bool = True,
    fallback_config: Optional[Dict] = None,
    fallback_config: Optional[Dict] = None,
    ):
    ):
    """
    """
    Initialize the agent model provider.
    Initialize the agent model provider.


    Args:
    Args:
    model_manager: Optional model manager instance
    model_manager: Optional model manager instance
    fallback_enabled: Whether fallback mechanisms should be enabled
    fallback_enabled: Whether fallback mechanisms should be enabled
    fallback_config: Optional configuration for fallback behavior
    fallback_config: Optional configuration for fallback behavior
    """
    """
    # Use dependency injection to get the model manager if not provided
    # Use dependency injection to get the model manager if not provided
    if model_manager is None:
    if model_manager is None:
    container = get_container()
    container = get_container()
    try:
    try:
    self.model_manager = container.resolve(IModelManager)
    self.model_manager = container.resolve(IModelManager)
except ValueError:
except ValueError:
    # If not registered in the container, create a new instance
    # If not registered in the container, create a new instance
    self.model_manager = ModelManager()
    self.model_manager = ModelManager()
    else:
    else:
    self.model_manager = model_manager
    self.model_manager = model_manager


    # Dictionary to store agent model assignments
    # Dictionary to store agent model assignments
    # Structure: {agent_type: {task_type: model_id}}
    # Structure: {agent_type: {task_type: model_id}}
    self.agent_models: Dict[str, Dict[str, Any]] = {}
    self.agent_models: Dict[str, Dict[str, Any]] = {}


    # Default fallback configuration if none provided
    # Default fallback configuration if none provided
    default_fallback_config = {
    default_fallback_config = {
    "max_attempts": 3,  # Maximum number of fallback attempts
    "max_attempts": 3,  # Maximum number of fallback attempts
    "default_model_id": None,  # Global fallback model ID
    "default_model_id": None,  # Global fallback model ID
    "logging_level": logging.INFO,  # Logging level for fallback events
    "logging_level": logging.INFO,  # Logging level for fallback events
    "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
    "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
    "fallback_preferences": {  # Fallback preferences for different agent types
    "fallback_preferences": {  # Fallback preferences for different agent types
    "researcher": ["huggingface", "llama", "general-purpose"],
    "researcher": ["huggingface", "llama", "general-purpose"],
    "developer": ["huggingface", "llama", "general-purpose"],
    "developer": ["huggingface", "llama", "general-purpose"],
    "monetization": ["huggingface", "general-purpose"],
    "monetization": ["huggingface", "general-purpose"],
    "marketing": ["huggingface", "general-purpose"],
    "marketing": ["huggingface", "general-purpose"],
    "default": ["huggingface", "general-purpose"],
    "default": ["huggingface", "general-purpose"],
    },
    },
    }
    }


    # Apply any custom fallback configuration
    # Apply any custom fallback configuration
    if fallback_config:
    if fallback_config:
    for key, value in fallback_config.items():
    for key, value in fallback_config.items():
    default_fallback_config[key] = value
    default_fallback_config[key] = value


    # Initialize the fallback manager
    # Initialize the fallback manager
    self.fallback_manager = FallbackManager(
    self.fallback_manager = FallbackManager(
    model_manager=self.model_manager,
    model_manager=self.model_manager,
    fallback_enabled=fallback_enabled,
    fallback_enabled=fallback_enabled,
    default_strategy=FallbackStrategy.SPECIFIED_LIST,
    default_strategy=FallbackStrategy.SPECIFIED_LIST,
    max_attempts=default_fallback_config["max_attempts"],
    max_attempts=default_fallback_config["max_attempts"],
    default_model_id=default_fallback_config["default_model_id"],
    default_model_id=default_fallback_config["default_model_id"],
    fallback_preferences=default_fallback_config["fallback_preferences"],
    fallback_preferences=default_fallback_config["fallback_preferences"],
    logging_level=default_fallback_config["logging_level"],
    logging_level=default_fallback_config["logging_level"],
    )
    )


    def get_model_for_agent(
    def get_model_for_agent(
    self, agent_type: str, task_type: Optional[str] = None
    self, agent_type: str, task_type: Optional[str] = None
    ) -> Any:
    ) -> Any:
    """
    """
    Get a model for a specific agent and task.
    Get a model for a specific agent and task.


    This method implements a multi-step model selection process:
    This method implements a multi-step model selection process:
    1. Check if there's an explicit assignment for this agent and task
    1. Check if there's an explicit assignment for this agent and task
    2. If not, find a suitable model based on agent and task preferences
    2. If not, find a suitable model based on agent and task preferences
    3. Load the selected model
    3. Load the selected model
    4. Record the assignment for future use
    4. Record the assignment for future use


    If fallback is enabled and initial model selection fails, the method will
    If fallback is enabled and initial model selection fails, the method will
    attempt to find alternative models based on the fallback configuration.
    attempt to find alternative models based on the fallback configuration.


    Args:
    Args:
    agent_type: Type of agent (researcher, developer, etc.)
    agent_type: Type of agent (researcher, developer, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)


    Returns:
    Returns:
    Model instance
    Model instance


    Raises:
    Raises:
    ValueError: If no suitable model is found after exhausting all fallbacks
    ValueError: If no suitable model is found after exhausting all fallbacks
    """
    """
    # Check if the agent already has a model assigned
    # Check if the agent already has a model assigned
    if agent_type in self.agent_models and (
    if agent_type in self.agent_models and (
    task_type is None or task_type in self.agent_models[agent_type]
    task_type is None or task_type in self.agent_models[agent_type]
    ):
    ):
    model_id = (
    model_id = (
    self.agent_models[agent_type].get(task_type)
    self.agent_models[agent_type].get(task_type)
    if task_type
    if task_type
    else list(self.agent_models[agent_type].values())[0]
    else list(self.agent_models[agent_type].values())[0]
    )
    )
    try:
    try:
    return self.model_manager.load_model(model_id)
    return self.model_manager.load_model(model_id)
except Exception as e:
except Exception as e:
    if not self.fallback_manager.fallback_enabled:
    if not self.fallback_manager.fallback_enabled:
    raise e
    raise e
    # Log the failure and continue to fallback mechanisms
    # Log the failure and continue to fallback mechanisms
    logger.warning(
    logger.warning(
    f"Failed to load assigned model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
    f"Failed to load assigned model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
    "Attempting fallback."
    "Attempting fallback."
    )
    )
    # Try to find a fallback model
    # Try to find a fallback model
    fallback_model_info, event = self.fallback_manager.find_fallback_model(
    fallback_model_info, event = self.fallback_manager.find_fallback_model(
    original_model_id=model_id,
    original_model_id=model_id,
    agent_type=agent_type,
    agent_type=agent_type,
    task_type=task_type,
    task_type=task_type,
    )
    )


    if fallback_model_info:
    if fallback_model_info:
    # Try to load the fallback model
    # Try to load the fallback model
    try:
    try:
    model = self.model_manager.load_model(fallback_model_info.id)
    model = self.model_manager.load_model(fallback_model_info.id)
    # Update the agent's model assignment to use the fallback model
    # Update the agent's model assignment to use the fallback model
    self.agent_models[agent_type][
    self.agent_models[agent_type][
    task_type or "default"
    task_type or "default"
    ] = fallback_model_info.id
    ] = fallback_model_info.id
    return model
    return model
except Exception as load_error:
except Exception as load_error:
    # Mark the fallback as unsuccessful
    # Mark the fallback as unsuccessful
    if event:
    if event:
    self.fallback_manager.track_fallback_event(
    self.fallback_manager.track_fallback_event(
    event, was_successful=False
    event, was_successful=False
    )
    )
    # Re-raise with additional context
    # Re-raise with additional context
    raise ValueError(
    raise ValueError(
    f"Failed to load fallback model {fallback_model_info.id}: {str(load_error)}"
    f"Failed to load fallback model {fallback_model_info.id}: {str(load_error)}"
    ) from load_error
    ) from load_error


    # If we don't have a model assignment, find a suitable model
    # If we don't have a model assignment, find a suitable model
    model_info = self._find_suitable_model(agent_type, task_type)
    model_info = self._find_suitable_model(agent_type, task_type)


    # If no suitable model found, try fallback
    # If no suitable model found, try fallback
    if not model_info and self.fallback_manager.fallback_enabled:
    if not model_info and self.fallback_manager.fallback_enabled:
    logger.info(
    logger.info(
    f"No suitable model found for agent {agent_type}, task {task_type}. Attempting fallback."
    f"No suitable model found for agent {agent_type}, task {task_type}. Attempting fallback."
    )
    )
    fallback_model_info, _ = self.fallback_manager.find_fallback_model(
    fallback_model_info, _ = self.fallback_manager.find_fallback_model(
    agent_type=agent_type, task_type=task_type
    agent_type=agent_type, task_type=task_type
    )
    )
    model_info = fallback_model_info
    model_info = fallback_model_info


    if not model_info:
    if not model_info:
    raise ValueError(
    raise ValueError(
    f"No suitable model found for agent type {agent_type} and task type {task_type} "
    f"No suitable model found for agent type {agent_type} and task type {task_type} "
    "after exhausting all fallback options."
    "after exhausting all fallback options."
    )
    )


    # Load the model
    # Load the model
    try:
    try:
    model = self.model_manager.load_model(model_info.id)
    model = self.model_manager.load_model(model_info.id)
except Exception as e:
except Exception as e:
    # If we can't load the model, try one last fallback to ANY_AVAILABLE strategy
    # If we can't load the model, try one last fallback to ANY_AVAILABLE strategy
    if self.fallback_manager.fallback_enabled:
    if self.fallback_manager.fallback_enabled:
    logger.warning(
    logger.warning(
    f"Failed to load model {model_info.id}. Trying last-resort fallback."
    f"Failed to load model {model_info.id}. Trying last-resort fallback."
    )
    )
    fallback_model_info, _ = self.fallback_manager.find_fallback_model(
    fallback_model_info, _ = self.fallback_manager.find_fallback_model(
    original_model_id=model_info.id,
    original_model_id=model_info.id,
    agent_type=agent_type,
    agent_type=agent_type,
    task_type=task_type,
    task_type=task_type,
    strategy_override=FallbackStrategy.ANY_AVAILABLE,
    strategy_override=FallbackStrategy.ANY_AVAILABLE,
    )
    )


    if fallback_model_info:
    if fallback_model_info:
    try:
    try:
    model = self.model_manager.load_model(fallback_model_info.id)
    model = self.model_manager.load_model(fallback_model_info.id)
    model_info = fallback_model_info
    model_info = fallback_model_info
except Exception as fallback_error:
except Exception as fallback_error:
    raise ValueError(
    raise ValueError(
    f"Failed to load model for agent {agent_type}, task {task_type} "
    f"Failed to load model for agent {agent_type}, task {task_type} "
    f"after exhausting all fallbacks: {str(fallback_error)}"
    f"after exhausting all fallbacks: {str(fallback_error)}"
    ) from fallback_error
    ) from fallback_error
    else:
    else:
    raise ValueError(
    raise ValueError(
    f"Failed to load model for agent {agent_type}, task {task_type}. "
    f"Failed to load model for agent {agent_type}, task {task_type}. "
    "No fallback models available."
    "No fallback models available."
    ) from e
    ) from e
    else:
    else:
    raise ValueError(
    raise ValueError(
    f"Failed to load model {model_info.id} for agent {agent_type}, task {task_type}: {str(e)}"
    f"Failed to load model {model_info.id} for agent {agent_type}, task {task_type}: {str(e)}"
    ) from e
    ) from e


    # Store the model assignment
    # Store the model assignment
    if agent_type not in self.agent_models:
    if agent_type not in self.agent_models:
    self.agent_models[agent_type] = {}
    self.agent_models[agent_type] = {}


    self.agent_models[agent_type][task_type or "default"] = model_info.id
    self.agent_models[agent_type][task_type or "default"] = model_info.id
    logger.info(
    logger.info(
    f"Assigned model {model_info.id} to agent {agent_type}, task {task_type or 'default'}"
    f"Assigned model {model_info.id} to agent {agent_type}, task {task_type or 'default'}"
    )
    )


    return model
    return model


    def _find_suitable_model(
    def _find_suitable_model(
    self, agent_type: str, task_type: Optional[str] = None
    self, agent_type: str, task_type: Optional[str] = None
    ) -> Optional[IModelInfo]:
    ) -> Optional[IModelInfo]:
    """
    """
    Find a suitable model for a specific agent and task.
    Find a suitable model for a specific agent and task.


    This algorithm implements a preference-based model selection strategy:
    This algorithm implements a preference-based model selection strategy:


    1. Define preference lists for both agent types and task types
    1. Define preference lists for both agent types and task types
    2. For the given agent_type and task_type, retrieve their specific preferences
    2. For the given agent_type and task_type, retrieve their specific preferences
    3. Find the intersection of preferences if both are provided (agent AND task preferences)
    3. Find the intersection of preferences if both are provided (agent AND task preferences)
    4. Try to find models matching the combined preferences in order of priority
    4. Try to find models matching the combined preferences in order of priority
    5. Fall back to any available model if no matches found
    5. Fall back to any available model if no matches found


    This approach ensures that each agent gets a model that is optimized for both
    This approach ensures that each agent gets a model that is optimized for both
    its general role (agent_type) and specific current task (task_type).
    its general role (agent_type) and specific current task (task_type).


    Args:
    Args:
    agent_type: Type of agent (researcher, developer, etc.)
    agent_type: Type of agent (researcher, developer, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)


    Returns:
    Returns:
    IModelInfo instance or None if no suitable model is found
    IModelInfo instance or None if no suitable model is found
    """
    """
    # Get all available models
    # Get all available models
    all_models = self.model_manager.get_all_models()
    all_models = self.model_manager.get_all_models()
    if not all_models:
    if not all_models:
    return None
    return None


    # Define model preferences for different agent types
    # Define model preferences for different agent types
    # This maps agent types to a prioritized list of model types they prefer
    # This maps agent types to a prioritized list of model types they prefer
    agent_preferences = {
    agent_preferences = {
    "researcher": ["huggingface", "llama"],
    "researcher": ["huggingface", "llama"],
    "developer": ["huggingface", "llama"],
    "developer": ["huggingface", "llama"],
    "monetization": ["huggingface", "llama"],
    "monetization": ["huggingface", "llama"],
    "marketing": ["huggingface", "llama"],
    "marketing": ["huggingface", "llama"],
    "feedback": ["huggingface", "llama"],
    "feedback": ["huggingface", "llama"],
    }
    }


    # Define model preferences for different task types
    # Define model preferences for different task types
    # This maps task types to a prioritized list of model types best suited for them
    # This maps task types to a prioritized list of model types best suited for them
    task_preferences = {
    task_preferences = {
    "text-generation": ["huggingface", "llama"],
    "text-generation": ["huggingface", "llama"],
    "embedding": ["embedding"],
    "embedding": ["embedding"],
    "classification": ["huggingface"],
    "classification": ["huggingface"],
    "summarization": ["huggingface", "llama"],
    "summarization": ["huggingface", "llama"],
    "translation": ["huggingface"],
    "translation": ["huggingface"],
    }
    }


    # Get preferences for the specified agent type
    # Get preferences for the specified agent type
    # Use default preferences if agent_type is not found in the mapping
    # Use default preferences if agent_type is not found in the mapping
    agent_prefs = agent_preferences.get(agent_type, ["huggingface", "llama"])
    agent_prefs = agent_preferences.get(agent_type, ["huggingface", "llama"])


    # Get preferences for the specified task type
    # Get preferences for the specified task type
    # Only consider task preferences if a task_type was provided
    # Only consider task preferences if a task_type was provided
    task_prefs = (
    task_prefs = (
    task_preferences.get(task_type, ["huggingface", "llama"])
    task_preferences.get(task_type, ["huggingface", "llama"])
    if task_type
    if task_type
    else []
    else []
    )
    )


    # Combine preferences
    # Combine preferences
    # If task_prefs is not empty, find the intersection (preferences that satisfy both)
    # If task_prefs is not empty, find the intersection (preferences that satisfy both)
    # Otherwise, just use the agent preferences
    # Otherwise, just use the agent preferences
    combined_prefs = (
    combined_prefs = (
    list(set(agent_prefs) & set(task_prefs)) if task_prefs else agent_prefs
    list(set(agent_prefs) & set(task_prefs)) if task_prefs else agent_prefs
    )
    )


    # Find a model that matches the preferences
    # Find a model that matches the preferences
    # Try each preferred model type in order until a match is found
    # Try each preferred model type in order until a match is found
    for model_type in combined_prefs:
    for model_type in combined_prefs:
    models = self.model_manager.get_models_by_type(model_type)
    models = self.model_manager.get_models_by_type(model_type)
    if models:
    if models:
    return models[0]  # Return the first model of the preferred type
    return models[0]  # Return the first model of the preferred type


    # If no model matches the preferences, return None and let the caller decide what to do
    # If no model matches the preferences, return None and let the caller decide what to do
    return None
    return None


    def assign_model_to_agent(
    def assign_model_to_agent(
    self, agent_type: str, model_id: str, task_type: Optional[str] = None
    self, agent_type: str, model_id: str, task_type: Optional[str] = None
    ) -> None:
    ) -> None:
    """
    """
    Assign a specific model to an agent.
    Assign a specific model to an agent.


    Args:
    Args:
    agent_type: Type of agent (researcher, developer, etc.)
    agent_type: Type of agent (researcher, developer, etc.)
    model_id: ID of the model to assign
    model_id: ID of the model to assign
    task_type: Optional type of task (text-generation, embedding, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)


    Raises:
    Raises:
    ValueError: If the model is not found
    ValueError: If the model is not found
    """
    """
    # Check if the model exists
    # Check if the model exists
    model_info = self.model_manager.get_model_info(model_id)
    model_info = self.model_manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ValueError(f"Model with ID {model_id} not found")
    raise ValueError(f"Model with ID {model_id} not found")


    # Store the model assignment
    # Store the model assignment
    if agent_type not in self.agent_models:
    if agent_type not in self.agent_models:
    self.agent_models[agent_type] = {}
    self.agent_models[agent_type] = {}


    self.agent_models[agent_type][task_type or "default"] = model_id
    self.agent_models[agent_type][task_type or "default"] = model_id
    logger.info(
    logger.info(
    f"Assigned model {model_id} to agent {agent_type}, task {task_type or 'default'}"
    f"Assigned model {model_id} to agent {agent_type}, task {task_type or 'default'}"
    )
    )


    def unassign_model_from_agent(
    def unassign_model_from_agent(
    self, agent_type: str, task_type: Optional[str] = None
    self, agent_type: str, task_type: Optional[str] = None
    ) -> bool:
    ) -> bool:
    """
    """
    Unassign a model from an agent.
    Unassign a model from an agent.


    Args:
    Args:
    agent_type: Type of agent (researcher, developer, etc.)
    agent_type: Type of agent (researcher, developer, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)


    Returns:
    Returns:
    True if the model was unassigned, False otherwise
    True if the model was unassigned, False otherwise
    """
    """
    if agent_type in self.agent_models:
    if agent_type in self.agent_models:
    if task_type:
    if task_type:
    if task_type in self.agent_models[agent_type]:
    if task_type in self.agent_models[agent_type]:
    del self.agent_models[agent_type][task_type]
    del self.agent_models[agent_type][task_type]
    logger.info(
    logger.info(
    f"Unassigned model from agent {agent_type}, task {task_type}"
    f"Unassigned model from agent {agent_type}, task {task_type}"
    )
    )
    return True
    return True
    else:
    else:
    del self.agent_models[agent_type]
    del self.agent_models[agent_type]
    logger.info(f"Unassigned all models from agent {agent_type}")
    logger.info(f"Unassigned all models from agent {agent_type}")
    return True
    return True


    return False
    return False


    def get_agent_model_assignments(self) -> Dict[str, Dict[str, str]]:
    def get_agent_model_assignments(self) -> Dict[str, Dict[str, str]]:
    """
    """
    Get all agent model assignments.
    Get all agent model assignments.


    Returns:
    Returns:
    Dictionary of agent model assignments
    Dictionary of agent model assignments
    """
    """
    return self.agent_models
    return self.agent_models


    def get_model_with_fallback(
    def get_model_with_fallback(
    self, agent_type: str, model_id: str, task_type: Optional[str] = None
    self, agent_type: str, model_id: str, task_type: Optional[str] = None
    ) -> Any:
    ) -> Any:
    """
    """
    Get a model with fallback support.
    Get a model with fallback support.


    This method attempts to load the specified model, and if that fails,
    This method attempts to load the specified model, and if that fails,
    it will try to find a fallback model based on the configured fallback strategy.
    it will try to find a fallback model based on the configured fallback strategy.


    Args:
    Args:
    agent_type: Type of agent (researcher, developer, etc.)
    agent_type: Type of agent (researcher, developer, etc.)
    model_id: ID of the model to load
    model_id: ID of the model to load
    task_type: Optional type of task (text-generation, embedding, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)


    Returns:
    Returns:
    Model instance
    Model instance


    Raises:
    Raises:
    ValueError: If no suitable model is found after exhausting all fallbacks
    ValueError: If no suitable model is found after exhausting all fallbacks
    """
    """
    try:
    try:
    # First try to load the specified model
    # First try to load the specified model
    return self.model_manager.load_model(model_id)
    return self.model_manager.load_model(model_id)
except Exception as e:
except Exception as e:
    if not self.fallback_manager.fallback_enabled:
    if not self.fallback_manager.fallback_enabled:
    raise e
    raise e


    # Log the failure and continue to fallback mechanisms
    # Log the failure and continue to fallback mechanisms
    logger.warning(
    logger.warning(
    f"Failed to load model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
    f"Failed to load model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
    "Attempting fallback."
    "Attempting fallback."
    )
    )


    # Try to find a fallback model
    # Try to find a fallback model
    fallback_model_info, event = self.fallback_manager.find_fallback_model(
    fallback_model_info, event = self.fallback_manager.find_fallback_model(
    original_model_id=model_id, agent_type=agent_type, task_type=task_type
    original_model_id=model_id, agent_type=agent_type, task_type=task_type
    )
    )


    if fallback_model_info:
    if fallback_model_info:
    # Try to load the fallback model
    # Try to load the fallback model
    try:
    try:
    model = self.model_manager.load_model(fallback_model_info.id)
    model = self.model_manager.load_model(fallback_model_info.id)
    # Update the agent's model assignment to use the fallback model
    # Update the agent's model assignment to use the fallback model
    if agent_type not in self.agent_models:
    if agent_type not in self.agent_models:
    self.agent_models[agent_type] = {}
    self.agent_models[agent_type] = {}
    self.agent_models[agent_type][
    self.agent_models[agent_type][
    task_type or "default"
    task_type or "default"
    ] = fallback_model_info.id
    ] = fallback_model_info.id
    return model
    return model
except Exception as load_error:
except Exception as load_error:
    # Mark the fallback as unsuccessful
    # Mark the fallback as unsuccessful
    if event:
    if event:
    self.fallback_manager.track_fallback_event(
    self.fallback_manager.track_fallback_event(
    event, was_successful=False
    event, was_successful=False
    )
    )
    # Re-raise with additional context
    # Re-raise with additional context
    raise ValueError(
    raise ValueError(
    f"Failed to load fallback model {fallback_model_info.id}: {str(load_error)}"
    f"Failed to load fallback model {fallback_model_info.id}: {str(load_error)}"
    ) from load_error
    ) from load_error


    # If no fallback model found, raise an error
    # If no fallback model found, raise an error
    raise ValueError(
    raise ValueError(
    f"No fallback model found for {model_id} after exhausting all options"
    f"No fallback model found for {model_id} after exhausting all options"
    )
    )


    def configure_fallback(
    def configure_fallback(
    self, fallback_enabled: bool = True, fallback_config: Optional[Dict] = None
    self, fallback_enabled: bool = True, fallback_config: Optional[Dict] = None
    ) -> None:
    ) -> None:
    """
    """
    Configure fallback behavior.
    Configure fallback behavior.


    Args:
    Args:
    fallback_enabled: Whether fallback mechanisms should be enabled
    fallback_enabled: Whether fallback mechanisms should be enabled
    fallback_config: Optional configuration for fallback behavior
    fallback_config: Optional configuration for fallback behavior
    """
    """
    # Default fallback configuration if none provided
    # Default fallback configuration if none provided
    default_fallback_config = {
    default_fallback_config = {
    "max_attempts": 3,  # Maximum number of fallback attempts
    "max_attempts": 3,  # Maximum number of fallback attempts
    "default_model_id": None,  # Global fallback model ID
    "default_model_id": None,  # Global fallback model ID
    "logging_level": logging.INFO,  # Logging level for fallback events
    "logging_level": logging.INFO,  # Logging level for fallback events
    "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
    "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
    "fallback_preferences": {  # Fallback preferences for different agent types
    "fallback_preferences": {  # Fallback preferences for different agent types
    "researcher": ["huggingface", "llama", "general-purpose"],
    "researcher": ["huggingface", "llama", "general-purpose"],
    "developer": ["huggingface", "llama", "general-purpose"],
    "developer": ["huggingface", "llama", "general-purpose"],
    "monetization": ["huggingface", "general-purpose"],
    "monetization": ["huggingface", "general-purpose"],
    "marketing": ["huggingface", "general-purpose"],
    "marketing": ["huggingface", "general-purpose"],
    "default": ["huggingface", "general-purpose"],
    "default": ["huggingface", "general-purpose"],
    },
    },
    }
    }


    # Apply any custom fallback configuration
    # Apply any custom fallback configuration
    if fallback_config:
    if fallback_config:
    for key, value in fallback_config.items():
    for key, value in fallback_config.items():
    default_fallback_config[key] = value
    default_fallback_config[key] = value


    # Update the fallback manager
    # Update the fallback manager
    self.fallback_manager.fallback_enabled = fallback_enabled
    self.fallback_manager.fallback_enabled = fallback_enabled
    self.fallback_manager.max_attempts = default_fallback_config["max_attempts"]
    self.fallback_manager.max_attempts = default_fallback_config["max_attempts"]
    self.fallback_manager.default_model_id = default_fallback_config[
    self.fallback_manager.default_model_id = default_fallback_config[
    "default_model_id"
    "default_model_id"
    ]
    ]
    self.fallback_manager.fallback_preferences = default_fallback_config[
    self.fallback_manager.fallback_preferences = default_fallback_config[
    "fallback_preferences"
    "fallback_preferences"
    ]
    ]
    self.fallback_manager.logging_level = default_fallback_config["logging_level"]
    self.fallback_manager.logging_level = default_fallback_config["logging_level"]


    logger.info(f"Updated fallback configuration. Enabled: {fallback_enabled}")
    logger.info(f"Updated fallback configuration. Enabled: {fallback_enabled}")


    def model_has_capability(self, model_id: str, capability: str) -> bool:
    def model_has_capability(self, model_id: str, capability: str) -> bool:
    """
    """
    Check if a model has a specific capability.
    Check if a model has a specific capability.


    Args:
    Args:
    model_id: ID of the model to check
    model_id: ID of the model to check
    capability: Capability to check for
    capability: Capability to check for


    Returns:
    Returns:
    True if the model has the capability, False otherwise
    True if the model has the capability, False otherwise
    """
    """
    model_info = self.model_manager.get_model_info(model_id)
    model_info = self.model_manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    return False
    return False


    return capability in model_info.capabilities
    return capability in model_info.capabilities


    def get_assigned_model_id(
    def get_assigned_model_id(
    self, agent_type: str, task_type: Optional[str] = None
    self, agent_type: str, task_type: Optional[str] = None
    ) -> Optional[str]:
    ) -> Optional[str]:
    """
    """
    Get the currently assigned model ID for an agent and task type.
    Get the currently assigned model ID for an agent and task type.


    Args:
    Args:
    agent_type: Type of agent (researcher, developer, etc.)
    agent_type: Type of agent (researcher, developer, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)
    task_type: Optional type of task (text-generation, embedding, etc.)


    Returns:
    Returns:
    Assigned model ID or None if no model is assigned
    Assigned model ID or None if no model is assigned
    """
    """
    if agent_type not in self.agent_models:
    if agent_type not in self.agent_models:
    return None
    return None


    return self.agent_models[agent_type].get(task_type or "default")
    return self.agent_models[agent_type].get(task_type or "default")




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a model manager
    # Create a model manager
    manager = ModelManager()
    manager = ModelManager()


    # Create an agent model provider
    # Create an agent model provider
    provider = AgentModelProvider(manager)
    provider = AgentModelProvider(manager)


    # Get a model for the researcher agent
    # Get a model for the researcher agent
    try:
    try:
    researcher_model = provider.get_model_for_agent("researcher", "text-generation")
    researcher_model = provider.get_model_for_agent("researcher", "text-generation")
    print(f"Got model for researcher agent: {researcher_model}")
    print(f"Got model for researcher agent: {researcher_model}")
except ValueError as e:
except ValueError as e:
    print(f"Error getting model for researcher agent: {e}")
    print(f"Error getting model for researcher agent: {e}")


    # Get a model for the developer agent
    # Get a model for the developer agent
    try:
    try:
    developer_model = provider.get_model_for_agent("developer")
    developer_model = provider.get_model_for_agent("developer")
    print(f"Got model for developer agent: {developer_model}")
    print(f"Got model for developer agent: {developer_model}")
except ValueError as e:
except ValueError as e:
    print(f"Error getting model for developer agent: {e}")
    print(f"Error getting model for developer agent: {e}")


    # Print agent model assignments
    # Print agent model assignments
    assignments = provider.get_agent_model_assignments()
    assignments = provider.get_agent_model_assignments()
    print("\nAgent Model Assignments:")
    print("\nAgent Model Assignments:")
    for agent_type, tasks in assignments.items():
    for agent_type, tasks in assignments.items():
    for task_type, model_id in tasks.items():
    for task_type, model_id in tasks.items():
    model_info = manager.get_model_info(model_id)
    model_info = manager.get_model_info(model_id)
    print(
    print(
    f"Agent: {agent_type}, Task: {task_type}, Model: {model_info.name if model_info else model_id}"
    f"Agent: {agent_type}, Task: {task_type}, Model: {model_info.name if model_info else model_id}"
    )
    )


    # Configure fallback behavior
    # Configure fallback behavior
    provider.configure_fallback(
    provider.configure_fallback(
    fallback_enabled=True,
    fallback_enabled=True,
    fallback_config={
    fallback_config={
    "max_attempts": 5,
    "max_attempts": 5,
    "logging_level": logging.DEBUG,
    "logging_level": logging.DEBUG,
    "use_general_purpose_fallback": True,
    "use_general_purpose_fallback": True,
    },
    },
    )
    )

